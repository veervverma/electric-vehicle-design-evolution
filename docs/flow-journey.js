(()=>{const frames=[document.querySelector('#side'),document.querySelector('#top')];let running=true;
const send=(name,value)=>frames.forEach(f=>f.contentWindow?.postMessage({type:'w11-journey-control',name,value},location.origin));
for(const name of ['density','trail','field','grid'])document.querySelector('#'+name).addEventListener(name==='field'||name==='grid'?'change':'input',e=>{send(name,e.target.value);if(name==='density')document.querySelector('#density-out').textContent=e.target.value+'% · '+Math.round(72000*e.target.value/100).toLocaleString()+' tracers';});
document.querySelector('#pause').onclick=e=>{running=!running;send('running',running);e.target.textContent=running?'Pause both':'Resume both';};document.querySelector('#reset').onclick=()=>send('reset');
for(const f of frames)f.addEventListener('load',()=>{for(const n of ['density','trail','field','grid'])send(n,document.querySelector('#'+n).value);send('running',running);});
window.addEventListener('message',e=>{if(e.origin!==location.origin||e.data?.type!=='w11-flow-height')return;const f=frames.find(f=>f.contentWindow===e.source);if(f){const h=Number(e.data.height);if(Number.isFinite(h))f.style.height=Math.max(320,Math.min(850,h))+'px';}});
})();
