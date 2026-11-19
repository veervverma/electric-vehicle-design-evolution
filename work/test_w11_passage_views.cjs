const fs=require('fs'),assert=require('assert'),source=fs.readFileSync('docs/side-flow-worker.js','utf8');
const results=[];
for(const [region,nx,steps] of [['underfloor',480,960],['cooling',480,960],['underfloor',960,320],['cooling',960,320]]){
 const geo=JSON.parse(fs.readFileSync('docs/w11-'+region+'-mask-'+nx+'.json'));let r;
 const self={postMessage:x=>r=x};new Function('self',source)(self);
 self.onmessage({data:{type:'init',geometry:geo,re:1000,U:.03}});
 for(let i=0;i<steps;i+=80){self.onmessage({data:{type:'advance',steps:Math.min(80,steps-i)}});assert.notEqual(r.type,'error',r.message);}
 assert(Math.abs(r.re-1000)<1e-6);assert(geo.solid_indices.every(i=>r.ux[i]===0&&r.uy[i]===0));
 const solids=new Set(geo.solid_indices);let cells=0,sum=0;
 for(let i=0;i<r.ux.length;i++){
  const x=geo.xmin_m+(i%nx+.5)*geo.dx_m,z=(Math.floor(i/nx)+.5)*geo.dx_m;
  const inROI=x>0&&x<1&&(region==='underfloor'?(z>.03&&z<.12):(Math.abs(Math.abs(z-2.25)-.75)<.09));
  if(inROI&&!solids.has(i)){cells++;sum+=Math.hypot(r.ux[i],r.uy[i])/r.U;}
 }
 assert(cells>0);assert(Number.isFinite(sum/cells));assert(sum/cells>.001);
 const result={region,nx,ny:geo.ny,steps:r.ticks,re:r.re,maxMach:r.maxMach,maxDensityError:r.maxRhoError,passageSampleFluidCells:cells,passageMeanSpeedRatio:sum/cells,solidVelocityZero:true};
 results.push(result);console.log(result);
}
fs.writeFileSync('outputs/W11_CHASSIS_AIRFLOW_VIEWS/PASSAGE_CHECKS.json',JSON.stringify({results,claim:'Short finite-flow and solid-mask smoke checks, not settled passage flux, radiator validation or full-scale CFD.'},null,2));
