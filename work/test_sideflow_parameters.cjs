const fs=require('fs'),assert=require('assert'),source=fs.readFileSync('docs/side-flow-worker.js','utf8'),geo=JSON.parse(fs.readFileSync('docs/w11-side-mask.json','utf8'));
let result;const self={postMessage:r=>result=r};new Function('self',source)(self);
for(const [U,nu] of [[.06,.035],[.02,.12]]){
 self.onmessage({data:{type:'init',geometry:geo}});
 self.onmessage({data:{type:'parameters',U,nu}});
 for(let k=0;k<20;k++){self.onmessage({data:{type:'advance',steps:80}});assert.notEqual(result.type,'error',result.message);}
 assert(result.maxMach<.3);assert(result.maxRhoError<.15);
 console.log({U,nu,iterations:result.ticks,maxMach:result.maxMach,maxDensityError:result.maxRhoError});
}
