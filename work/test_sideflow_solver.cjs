const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync('docs/side-flow-worker.js','utf8'),geo=JSON.parse(fs.readFileSync('docs/w11-side-mask.json','utf8'));
let result;const context={self:{postMessage:v=>result=v}};
new Function('self',source)(context.self);
const send=data=>{context.self.onmessage({data});assert.notEqual(result.type,'error',result.message);return result;};
send({type:'init',geometry:{...geo,solid_indices:[]},steps:80});
assert(Math.abs(result.meanDensity-1)<1e-5);assert(Math.abs(result.ux[geo.nx*40+30]-.045)<1e-5);
console.log('Uniform empty-domain preservation: passed');
send({type:'init',geometry:geo,steps:0});
for(let k=0;k<40;k++){send({type:'advance',steps:80});if(k%10===9)console.log('W11',result.ticks,'Ma',result.maxMach,'max density error',result.maxRhoError);}
assert(result.maxMach<.3);assert(result.maxRhoError<.15);
const solid=new Set(geo.solid_indices);
assert(geo.solid_indices.every(i=>result.ux[i]===0&&result.uy[i]===0));
const peak=Math.max(...result.ux);
assert(peak>.045*1.02);
const report={uniform_field_preservation:true,solid_velocity_zero:true,steps:result.ticks,Re:result.re,maxMach:result.maxMach,maxDensityError:result.maxRhoError,peakSpeedX:peak,claim:'Numerical smoke tests only; no grid-convergence or physical validation'};
fs.writeFileSync('outputs/W11_2D_SIDE_FLOW/SOLVER_SMOKE_TEST.json',JSON.stringify(report,null,2));
console.log(report);
