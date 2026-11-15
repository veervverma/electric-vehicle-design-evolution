// D2Q9 BGK lattice-Boltzmann solver. Lattice units; low-Mach educational flow.
const CX=[0,1,0,-1,0,1,-1,-1,1],CY=[0,0,1,0,-1,1,1,-1,-1];
const W=[4/9,1/9,1/9,1/9,1/9,1/36,1/36,1/36,1/36],OP=[0,3,4,1,2,7,8,5,6];
let epoch=0;
let nx,ny,n,solid,f,g,ticks=0,U=.045,nu=.045,omega,carLength;
function eq(q,r,u,v){const cu=CX[q]*u+CY[q]*v;return W[q]*r*(1+3*cu+4.5*cu*cu-1.5*(u*u+v*v));}
function init(data){
 nx=data.nx;ny=data.ny;n=nx*ny;carLength=data.car_length_cells;
 solid=new Uint8Array(n);for(const i of data.solid_indices)solid[i]=1;
 omega=1/(.5+3*nu);f=new Float32Array(n*9);g=new Float32Array(n*9);ticks=0;
 for(let i=0;i<n;i++)for(let q=0;q<9;q++)f[i*9+q]=eq(q,1,solid[i]?0:U,0);
}
function step(){
 // Relax distributions toward the local Maxwellian expansion.
 for(let i=0;i<n;i++){
  if(solid[i])continue;const k=i*9;let r=0,u=0,v=0;
  for(let q=0;q<9;q++){const z=f[k+q];r+=z;u+=z*CX[q];v+=z*CY[q];}
  u/=r;v/=r;
  for(let q=0;q<9;q++)g[k+q]=f[k+q]+omega*(eq(q,r,u,v)-f[k+q]);
 }
 // Pull streaming; halfway bounce-back on the stationary projected car.
 for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
  const i=y*nx+x,k=i*9;if(solid[i])continue;
  if(x===0||y===0||y===ny-1){for(let q=0;q<9;q++)f[k+q]=eq(q,1,U,0);continue;}
  if(x===nx-1){for(let q=0;q<9;q++)f[k+q]=g[k-9+q];continue;}
  for(let q=0;q<9;q++){
   const j=(y-CY[q])*nx+x-CX[q];
   f[k+q]=solid[j]?g[k+OP[q]]:g[j*9+q];
  }
 }
 ticks++;
}
function field(){
 const ux=new Float32Array(n),uy=new Float32Array(n),rho=new Float32Array(n);
 let maxSpeed=0,maxRhoError=0,mass=0,fluid=0;
 for(let i=0;i<n;i++){
  if(solid[i])continue;const k=i*9;let r=0,u=0,v=0;
  for(let q=0;q<9;q++){const z=f[k+q];r+=z;u+=z*CX[q];v+=z*CY[q];}
  u/=r;v/=r;ux[i]=u;uy[i]=v;rho[i]=r;mass+=r;fluid++;
  maxSpeed=Math.max(maxSpeed,Math.hypot(u,v));maxRhoError=Math.max(maxRhoError,Math.abs(r-1));
 }
 return {ux,uy,rho,ticks,U,nu,re:U*carLength/nu,maxMach:maxSpeed*Math.sqrt(3),maxRhoError,meanDensity:mass/fluid};
}
self.onmessage=({data})=>{
 try {
  if(data.type==='init'){epoch=data.epoch??0;init(data.geometry);}
  if(data.type==='parameters'){
   U=Math.max(.02,Math.min(.06,Number(data.U)||.045));
   nu=Math.max(.035,Math.min(.12,Number(data.nu)||.045));omega=1/(.5+3*nu);
   return;
  }
  const steps=Math.max(0,Math.min(80,data.steps??0));
  for(let k=0;k<steps;k++)step();
  const result=field();
  if(!Number.isFinite(result.maxMach)||result.maxMach>.6||result.maxRhoError>.3)throw Error('Flow became unstable. Reset or reduce inlet speed / increase viscosity.');
  self.postMessage({type:'field',epoch,...result},[result.ux.buffer,result.uy.buffer,result.rho.buffer]);
 }catch(e){self.postMessage({type:'error',message:String(e.message||e)});}
};
