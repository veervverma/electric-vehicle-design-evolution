// D2Q9 two-relaxation-time (TRT) LBM. All solved quantities use lattice units.
// nu = U * L_cells / Re; Lambda=(tau_even-.5)*(tau_odd-.5)=3/16.
// No Reynolds-dependent swirl, body force, or artificial wake is added.
const CX=[0,1,0,-1,0,1,-1,-1,1],CY=[0,0,1,0,-1,1,1,-1,-1];
const W=[4/9,1/9,1/9,1/9,1/9,1/36,1/36,1/36,1/36],OP=[0,3,4,1,2,7,8,5,6],PAIRS=[1,2,5,6];
let epoch=0,nx,ny,n,solid,f,g,ticks=0,U=.03,nu,omegaEven,omegaOdd,carLength,targetRe=1000,flowTimes=0,meta;
function eq(q,r,u,v){const cu=CX[q]*u+CY[q]*v;return W[q]*r*(1+3*cu+4.5*cu*cu-1.5*(u*u+v*v));}
function relax(){
 nu=U*carLength/targetRe;
 const tau=.5+3*nu;
 omegaEven=1/tau;omegaOdd=1/(.5+(3/16)/(tau-.5));
}
function parameters(data){
 if(data.U!==undefined)U=Math.max(.015,Math.min(.04,Number(data.U)||.03));
 if(data.re!==undefined)targetRe=Math.max(100,Math.min(2000,Number(data.re)||1000));
 if(carLength)relax();
}
function init(data){
 meta=data;nx=data.nx;ny=data.ny;n=nx*ny;carLength=data.car_length_cells;
 solid=new Uint8Array(n);for(const i of data.solid_indices)solid[i]=1;
 relax();f=new Float32Array(n*9);g=new Float32Array(n*9);ticks=0;flowTimes=0;
 for(let i=0;i<n;i++)for(let q=0;q<9;q++)f[i*9+q]=eq(q,1,solid[i]?0:U,0);
}
function step(){
 for(let i=0;i<n;i++){
  if(solid[i])continue;
  const k=i*9;let r=0,u=0,v=0;
  for(let q=0;q<9;q++){const z=f[k+q];r+=z;u+=z*CX[q];v+=z*CY[q];}
  u/=r;v/=r;const common=1-1.5*(u*u+v*v);
  g[k]=f[k]-omegaEven*(f[k]-W[0]*r*common);
  for(let a=0;a<4;a++){
   const q=PAIRS[a],o=OP[q],cu=CX[q]*u+CY[q]*v;
   const e=.5*(f[k+q]+f[k+o])-W[q]*r*(common+4.5*cu*cu);
   const odd=.5*(f[k+q]-f[k+o])-W[q]*r*3*cu;
   g[k+q]=f[k+q]-omegaEven*e-omegaOdd*odd;
   g[k+o]=f[k+o]-omegaEven*e+omegaOdd*odd;
  }
 }
 for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
  const i=y*nx+x,k=i*9;if(solid[i])continue;
  if(x===0||y===0||y===ny-1){for(let q=0;q<9;q++)f[k+q]=eq(q,1,U,0);continue;}
  if(x===nx-1){for(let q=0;q<9;q++)f[k+q]=g[k-9+q];continue;}
  for(let q=0;q<9;q++){const j=(y-CY[q])*nx+x-CX[q];f[k+q]=solid[j]?g[k+OP[q]]:g[j*9+q];}
 }
 ticks++;flowTimes+=U/carLength;
}
function field(){
 const ux=new Float32Array(n),uy=new Float32Array(n),rho=new Float32Array(n);
 let maxSpeed=0,maxRhoError=0,mass=0,fluid=0,wakeSpeed=0,wakeReverse=0,wakeCells=0;
 const dx=meta.dx_m,xmin=meta.xmin_m;
 for(let i=0;i<n;i++){
  if(solid[i])continue;const k=i*9;let r=0,u=0,v=0;
  for(let q=0;q<9;q++){const z=f[k+q];r+=z;u+=z*CX[q];v+=z*CY[q];}
  u/=r;v/=r;ux[i]=u;uy[i]=v;rho[i]=r;mass+=r;fluid++;
  maxSpeed=Math.max(maxSpeed,Math.hypot(u,v));maxRhoError=Math.max(maxRhoError,Math.abs(r-1));
  const x=xmin+(i%nx+.5)*dx,z=(Math.floor(i/nx)+.5)*dx;
  if(x>3.1&&x<6&&z>.05&&z<1.2){wakeSpeed+=Math.hypot(u,v)/U;wakeReverse+=u<0?1:0;wakeCells++;}
 }
 return {ux,uy,rho,ticks,U,nu,re:U*carLength/nu,flowTimes,nx,ny,carLength,
  tauEven:1/omegaEven,tauOdd:1/omegaOdd,
  maxMach:maxSpeed*Math.sqrt(3),maxRhoError,meanDensity:mass/fluid,
  wake:{meanSpeedRatio:wakeCells?wakeSpeed/wakeCells:null,reverseFlowFraction:wakeCells?wakeReverse/wakeCells:null,cells:wakeCells}};
}
self.onmessage=({data})=>{
 try{
  if(data.type==='init'){epoch=data.epoch??0;parameters(data);init(data.geometry);}
  if(data.type==='parameters'){parameters(data);return;}
  const steps=Math.max(0,Math.min(80,data.steps??0));for(let k=0;k<steps;k++)step();
  const result=field();
  if(!Number.isFinite(result.maxMach)||!Number.isFinite(result.meanDensity)||result.maxMach>.3||result.maxRhoError>.15)throw Error('Numerical limits exceeded. Reset with a lower Re or choose a finer grid.');
  self.postMessage({type:'field',epoch,...result},[result.ux.buffer,result.uy.buffer,result.rho.buffer]);
 }catch(e){self.postMessage({type:'error',epoch,message:String(e.message||e)});}
};
