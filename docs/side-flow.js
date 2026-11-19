const $=s=>document.querySelector(s),canvas=$('#flow'),ctx=canvas.getContext('2d',{alpha:false});
const heat=document.createElement('canvas'),hctx=heat.getContext('2d');
const trails=document.createElement('canvas'),tctx=trails.getContext('2d');
const worker=new Worker('side-flow-worker.js?v=20261118-trt');
let epoch=0;
if(new URLSearchParams(location.search).has('embed')){
 const sendHeight=()=>parent.postMessage({type:'w11-flow-height',height:Math.ceil(document.body.scrollHeight)},location.origin);
 new ResizeObserver(sendHeight).observe(document.body);
}
let embedActive=true,loadingGrid=false,gridRequest=0;
let geo,ux,uy,rho,image,mask,latest,running=true,busy=false,failed=false,last=performance.now(),seed=12345;
const FLOW_VIEW={x:41.6,y:50.88,width:310.4,height:93.12};
const MAX_PARTICLES=18000,px=new Float32Array(MAX_PARTICLES),py=new Float32Array(MAX_PARTICLES),age=new Uint16Array(MAX_PARTICLES);
function random(){seed=(Math.imul(seed,1664525)+1013904223)|0;return (seed>>>0)/4294967296;}
function particleCeiling(){return geo.ny-FLOW_VIEW.y-FLOW_VIEW.height/2;}
function spawn(i){
 // Seed only the visible car/wake band; upper-half markers are intentionally omitted.
 for(let k=0;k<40;k++){
  px[i]=FLOW_VIEW.x+1+random()*(FLOW_VIEW.width-2);
  py[i]=1+random()*(particleCeiling()-2);
  if(!mask[Math.floor(py[i])*geo.nx+Math.floor(px[i])])break;
 }
 age[i]=Math.floor(random()*120);
}
const stops=[[38,16,68],[122,35,124],[216,79,97],[255,178,62],[255,255,176]];
const palette=Array.from({length:256},(_,i)=>{const t=i/255*4,j=Math.min(3,Math.floor(t)),f=t-j;return stops[j].map((v,k)=>Math.round(v*(1-f)+stops[j+1][k]*f));});
function diverging(t){t=Math.max(-1,Math.min(1,t));const white=[239,227,224],end=t<0?[42,91,203]:[225,57,82];return white.map((v,k)=>Math.round(v+(end[k]-v)*Math.abs(t)));}
function drawHeat(){
 if(!ux)return;const nx=geo.nx,ny=geo.ny,mode=$('#field').value;
 for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
  const i=y*nx+x,j=((ny-1-y)*nx+x)*4;
  let c;
  if(mask[i])c=[22,23,32];
  else if(mode==='speed')c=palette[Math.min(255,Math.round(Math.hypot(ux[i],uy[i])/latest.U/1.5*255))];
  else if(mode==='streamwise')c=diverging(ux[i]/latest.U);
  else if(mode==='pressure')c=diverging((rho[i]-1)/(.5*latest.U*latest.U*3));
  else {
   const left=i-(x>0?1:0),right=i+(x<nx-1?1:0),bottom=i-(y>0?nx:0),top=i+(y<ny-1?nx:0);
   c=diverging(((uy[right]-uy[left])-(ux[top]-ux[bottom]))/Math.max(.005,latest.U*.7));
  }
  image.data[j]=c[0];image.data[j+1]=c[1];image.data[j+2]=c[2];image.data[j+3]=255;
 }
 hctx.putImageData(image,0,0);
 $('#legend-label').textContent=mode==='speed'?'SPEED / INLET SPEED':mode==='pressure'?'RELATIVE PRESSURE · QUALITATIVE':mode==='streamwise'?'STREAMWISE VELOCITY / INLET · BLUE = REVERSE':'VORTICITY · COUNTER-ROTATING REGIONS';
 $('.legend i').style.background=mode==='speed'?'linear-gradient(90deg,#261044,#7a237c,#d84f61,#ffb23e,#ffffb0)':'linear-gradient(90deg,#2a5bcb,#efe3e0,#e13952)';
 const labels=$('.legend').querySelectorAll('span');
 labels[1].textContent=mode==='speed'?'0':'−';labels[2].textContent=mode==='speed'?'0.75':'0';labels[3].textContent=mode==='speed'?'1.5+':'+';
}
function request(){if(busy||!running||failed||loadingGrid||!geo||document.hidden||!embedActive)return;busy=true;worker.postMessage({type:'advance',steps:Number($('#rate').value)});}
worker.onmessage=({data})=>{
 if(data.epoch!==epoch)return;
 busy=false;
 if(data.type==='error'){failed=true;$('#state').textContent=data.message;return;}
 latest=data;ux=data.ux;uy=data.uy;rho=data.rho;
 $('#iteration').textContent=data.ticks.toLocaleString();$('#re').textContent=data.re.toFixed(0);
 $('#grid-readout').textContent=data.nx+' × '+data.ny;
 $('#viscosity-readout').textContent=data.nu.toFixed(5)+' lu²/step';
 $('#flow-times').textContent=data.flowTimes.toFixed(2);
 updatePhysicalReference();
 $('#mach').textContent=data.maxMach.toFixed(3);$('#rho').textContent=(data.maxRhoError*100).toFixed(2)+'%';
 $('#state').textContent=(data.flowTimes<3?'Developing wake':'Live 2D wake')+' · '+data.flowTimes.toFixed(2)+' car-length flow times';
 drawHeat();request();
};
window.addEventListener('message',event=>{
 if(event.source!==parent||event.origin!==location.origin||event.data?.type!=='w11-flow-visibility')return;
 embedActive=Boolean(event.data.active);if(embedActive)request();
});
document.addEventListener('visibilitychange',()=>{if(!document.hidden)request();});
worker.onerror=e=>{failed=true;$('#state').textContent='Solver unavailable: '+e.message;};
function sample(x,y){
 const a=Math.floor(x),b=Math.floor(y);if(a<1||a>=geo.nx-2||b<1||b>=geo.ny-2)return null;
 const i=b*geo.nx+a;if(mask[i])return null;
 const fx=x-a,fy=y-b,ids=[i,i+1,i+geo.nx,i+geo.nx+1],w=[(1-fx)*(1-fy),fx*(1-fy),(1-fx)*fy,fx*fy];let u=0,v=0;
 // Stop at solid-adjacent samples rather than interpolating across the car.
 if(ids.some(j=>mask[j]))return null;
 for(let k=0;k<4;k++){u+=ux[ids[k]]*w[k];v+=uy[ids[k]]*w[k];}return [u,v];
}
function animate(now){
 requestAnimationFrame(animate);const dt=Math.min(.04,(now-last)/1000);last=now;if(!geo||!ux||!embedActive)return;
 if(running){
  const fade=.025+(1-Number($('#trail').value)/100)*.25;
  tctx.globalCompositeOperation='destination-out';tctx.fillStyle='rgba(0,0,0,'+fade+')';tctx.fillRect(0,0,trails.width,trails.height);tctx.globalCompositeOperation='source-over';
  if($('#particles').checked){
   const count=Math.round(MAX_PARTICLES*Number($('#density').value)/100),sx=trails.width/geo.nx,sy=trails.height/geo.ny;
   tctx.strokeStyle='rgba(255,253,235,.68)';tctx.lineWidth=1;tctx.beginPath();
   for(let i=0;i<count;i++){
    let v=sample(px[i],py[i]);if(!v||py[i]>=particleCeiling()||age[i]++>210){spawn(i);continue;}
    const step=dt*340*(geo.nx/480),x=px[i],y=py[i],nx=x+v[0]*step,ny=y+v[1]*step;
    // Check the entire short segment before drawing it.
    if(ny>=particleCeiling()||!sample((x+nx)*.5,(y+ny)*.5)||!sample(nx,ny)){spawn(i);continue;}
    px[i]=nx;py[i]=ny;tctx.moveTo(x*sx,(geo.ny-y)*sy);tctx.lineTo(nx*sx,(geo.ny-ny)*sy);
   }
   tctx.stroke();
  }else tctx.clearRect(0,0,trails.width,trails.height);
 }
 const {x:viewX,y:viewY,width:viewW,height:viewH}=FLOW_VIEW;
 ctx.imageSmoothingEnabled=true;ctx.drawImage(heat,viewX,viewY,viewW,viewH,0,0,canvas.width,canvas.height);
 if($('#particles').checked){
  // Clip historical trails as well: no stale upper-half dots after advection.
  ctx.save();ctx.beginPath();ctx.rect(0,canvas.height/2,canvas.width,canvas.height/2);ctx.clip();
  ctx.drawImage(trails,viewX*trails.width/geo.nx,viewY*trails.height/geo.ny,viewW*trails.width/geo.nx,viewH*trails.height/geo.ny,0,0,canvas.width,canvas.height);ctx.restore();
 }
 // Wake arrows are sampled from the solved velocity, including any reverse flow.
 if($('#vectors').checked){
  const stride=Math.max(8,Math.round(geo.nx/48));
  ctx.strokeStyle='rgba(240,252,255,.8)';ctx.lineWidth=1.1;
  const map=(x,y)=>[(x-viewX)*canvas.width/viewW,(geo.ny-y-viewY)*canvas.height/viewH];
  for(let y=stride;y<1.35/geo.dx_m;y+=stride)for(let x=Math.ceil((3.1-geo.xmin_m)/geo.dx_m);x<(6-geo.xmin_m)/geo.dx_m;x+=stride){
   const v=sample(x,y);if(!v)continue;
   const a=map(x,y),b=map(x+v[0]/latest.U*stride*.65,y+v[1]/latest.U*stride*.65);
   const angle=Math.atan2(b[1]-a[1],b[0]-a[0]);if(Math.hypot(b[0]-a[0],b[1]-a[1])<2)continue;
   ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);
   ctx.moveTo(b[0]-5*Math.cos(angle-.5),b[1]-5*Math.sin(angle-.5));ctx.lineTo(...b);
   ctx.lineTo(b[0]-5*Math.cos(angle+.5),b[1]-5*Math.sin(angle+.5));ctx.stroke();
  }
 }
 // Resolve silhouette edges directly from the W11 mask.
 ctx.fillStyle='#9094a3';
 for(const i of geo.solid_indices){const x=i%geo.nx,y=Math.floor(i/geo.nx);if(!mask[i+geo.nx]||!mask[i-geo.nx]||!mask[i-1]||!mask[i+1])ctx.fillRect((x-viewX)*canvas.width/viewW,(geo.ny-1-y-viewY)*canvas.height/viewH,canvas.width/viewW,1);}
 ctx.fillStyle='#17131d';ctx.fillRect(0,canvas.height-3,canvas.width,3);
 ctx.fillStyle='rgba(255,255,255,.8)';ctx.font='12px monospace';ctx.fillText('FLOW →',18,24);
}
function reset(){failed=false;tctx.clearRect(0,0,trails.width,trails.height);for(let i=0;i<MAX_PARTICLES;i++)spawn(i);busy=true;worker.postMessage({type:'init',epoch:++epoch,geometry:geo,re:Number($('#target-re').value),U:Number($('#speed').value)/1000,steps:0});}
$('#pause').onclick=()=>{running=!running;$('#pause').textContent=running?'Pause':'Resume';if(running)request();};
$('#reset').onclick=reset;
function updatePhysicalReference(){
 if(!geo)return;
 const length=geo.car_length_m||geo.car_length_cells*geo.dx_m;
 const physicalRe=(Number($('#physical-speed').value)/3.6)*length/(1.7894e-5/1.225);
 $('#physical-re').textContent=(physicalRe/1e6).toFixed(1)+' million';
 $('#re-gap').textContent='Full-scale target is '+Math.round(physicalRe/(latest?.re||Number($('#target-re').value))).toLocaleString()+'× the simulated Re. Similarity is not matched.';
}
for(const name of ['density','trail','speed','target-re','rate']){
 $('#'+name).oninput=()=>{
  const value=Number($('#'+name).value);
  $('#'+name+'-out').textContent=(name==='density'||name==='trail')?value+'%':name==='speed'?(value/1000).toFixed(3)+' lu/step':value.toLocaleString();
  if(name==='speed'||name==='target-re')worker.postMessage({type:'parameters',U:Number($('#speed').value)/1000,re:Number($('#target-re').value)});
  if(name==='density'||name==='trail')tctx.clearRect(0,0,trails.width,trails.height);
 };
}
$('#physical-speed').oninput=updatePhysicalReference;
$('#grid').onchange=()=>loadGrid();
async function loadGrid(){
 const ticket=++gridRequest;loadingGrid=true;$('#state').textContent='Loading fine W11 geometry…';
 try{
  const response=await fetch('w11-side-mask-'+$('#grid').value+'.json');
  if(!response.ok)throw Error('Selected W11 grid unavailable');
  const loaded=await response.json();if(ticket!==gridRequest)return;
  geo=loaded;mask=new Uint8Array(geo.nx*geo.ny);geo.solid_indices.forEach(i=>mask[i]=1);
  const scale=geo.nx/480;Object.assign(FLOW_VIEW,{x:41.6*scale,y:50.88*scale,width:310.4*scale,height:93.12*scale});
  heat.width=geo.nx;heat.height=geo.ny;image=hctx.createImageData(geo.nx,geo.ny);
  canvas.width=1920;canvas.height=576;trails.width=1920;trails.height=576;
  latest=null;ux=null;uy=null;rho=null;loadingGrid=false;updatePhysicalReference();reset();
 }catch(e){loadingGrid=false;failed=true;$('#state').textContent=e.message;}
}
$('#field').onchange=drawHeat;
await loadGrid();
requestAnimationFrame(animate);
