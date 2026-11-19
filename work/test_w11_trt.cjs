const fs=require('fs'),assert=require('assert');
const source=fs.readFileSync('docs/side-flow-worker.js','utf8');
const output='outputs/W11_2D_FINE_GRID_RE1K';
function context(){let result;const self={postMessage:r=>result=r};new Function('self',source)(self);return data=>{self.onmessage({data});assert.notEqual(result.type,'error',result.message);return result;};}
const mode=process.argv[2]||'coarse',nx={coarse:480,fine:960,ultra:1440}[mode],geo=JSON.parse(fs.readFileSync('docs/w11-side-mask-'+nx+'.json'));
const run=context();let r=run({type:'init',geometry:{...geo,solid_indices:[]},re:1000,steps:80});
assert(Math.abs(r.meanDensity-1)<1e-5);assert(Math.abs(r.ux[nx*40+30]-.03)<1e-5);
r=run({type:'init',geometry:geo,re:1000});
const steps=Math.ceil(geo.car_length_cells/.03),history=[];
for(let done=0;done<steps;){
 const batch=Math.min(80,steps-done);r=run({type:'advance',steps:batch});done+=batch;
 if(done%800===0)console.log(mode,done,r.maxMach.toFixed(4),r.maxRhoError.toFixed(4));
 history.push({steps:r.ticks,flowTimes:r.flowTimes,wake:r.wake,maxMach:r.maxMach,maxRhoError:r.maxRhoError});
}
assert(Math.abs(r.re-1000)<1e-8);assert(r.maxMach<.2);assert(r.maxRhoError<.1);
assert(geo.solid_indices.every(i=>r.ux[i]===0&&r.uy[i]===0));
fs.writeFileSync(output+'/CHECK_'+mode+'.json',JSON.stringify({grid:[nx,geo.ny],targetRe:1000,re:r.re,steps:r.ticks,flowTimes:r.flowTimes,nu:r.nu,tauEven:r.tauEven,tauOdd:r.tauOdd,maxMach:r.maxMach,maxRhoError:r.maxRhoError,wake:r.wake,history,uniformFieldCheck:true,solidZeroCheck:true,claim:'One flow-through-time transient sensitivity check. Not convergence or physical validation.'},null,2));
console.log('PASS',mode,r.re,r.flowTimes,r.wake);
