const fs=require('fs'),assert=require('assert'),src=fs.readFileSync('docs/side-flow-worker.js','utf8');
const results=[];
for(const [nx,re,U,steps] of [[960,2000,.04,640],[1440,1000,.03,320],[480,100,.015,640]]){
 const geo=JSON.parse(fs.readFileSync('docs/w11-side-mask-'+nx+'.json'));let r;
 const self={postMessage:x=>r=x};new Function('self',src)(self);
 self.onmessage({data:{type:'init',geometry:geo,re,U}});
 for(let t=0;t<steps;t+=80){self.onmessage({data:{type:'advance',steps:Math.min(80,steps-t)}});assert.notEqual(r.type,'error',r.message);}
 assert(Math.abs(r.re-re)<1e-7);
 results.push({grid:[nx,geo.ny],Re:r.re,U:r.U,nu:r.nu,steps:r.ticks,maxMach:r.maxMach,maxDensityError:r.maxRhoError});
 console.log(results.at(-1));
}
fs.writeFileSync('outputs/W11_2D_FINE_GRID_RE1K/PARAMETER_SMOKE_CHECKS.json',JSON.stringify({results,claim:'Short stability checks only. Longer runs at every control combination are not verified.'},null,2));
