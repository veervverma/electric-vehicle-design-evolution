(() => {
  const colored=document.querySelector('#colored-flow-view');
  const three=document.querySelector('#three-flow-view');
  const frame=document.querySelector('#colored-flow-frame');
  const coloredButton=document.querySelector('#view-colored');
  const threeButton=document.querySelector('#view-three');
  let activeView='colored';
  const underButton=document.querySelector('#view-underfloor');
  const coolingButton=document.querySelector('#view-cooling');
  function choose(view,updateUrl=true) {
    if(!['colored','3d','underfloor','cooling'].includes(view))view='colored';
    activeView=view;
    const notes={
      colored:'Exterior flow · 2D side projection · reduced-Reynolds-number educational study',
      underfloor:'Original W11 GLB · underside inspection + legacy external flow paths · unverified visualization, not new CFD',
      cooling:'Original W11 GLB · transparent sidepod inspection · internal ducts are not defined; no internal flow prediction',
      '3d':'Original 3D W11 particle presentation'
    };
    const summary=document.querySelector('#flow-region-summary');if(summary)summary.textContent=notes[view];
    const isColored=view==='colored';
    if(!isColored)window.dispatchEvent(new CustomEvent('w11-source-view',{detail:view}));
    colored.hidden=!isColored;three.hidden=isColored;
    const runState=document.querySelector('.run-state');if(runState)runState.hidden=isColored;
    coloredButton.setAttribute('aria-pressed',String(view==='colored'));
    underButton.setAttribute('aria-pressed',String(view==='underfloor'));
    coolingButton.setAttribute('aria-pressed',String(view==='cooling'));
    threeButton.setAttribute('aria-pressed',String(view==='3d'));
    frame.contentWindow?.postMessage({type:'w11-flow-visibility',active:isColored},location.origin);
    if(isColored)frame.contentWindow?.postMessage({type:'w11-flow-region',region:view==='colored'?'exterior':view},location.origin);
    if(updateUrl){
      const url=new URL(location.href);url.searchParams.set('view',view);
      history.replaceState(null,'',url);
    }
    window.dispatchEvent(new Event('resize'));
  }
  window.addEventListener('message',event=>{
    if(event.source===frame.contentWindow&&event.origin===location.origin&&event.data?.type==='w11-region-changed'){
      const view=event.data.region==='exterior'?'colored':event.data.region;
      if(view!==activeView)choose(view);
      return;
    }
    if(event.source!==frame.contentWindow||event.origin!==location.origin||event.data?.type!=='w11-flow-height')return;
    const height=Number(event.data.height);
    if(Number.isFinite(height))frame.style.height=Math.max(720,Math.min(2400,height))+'px';
  });
  document.querySelector('a[href="#colored-flow-view"]')?.addEventListener('click',()=>choose('colored'));
  coloredButton.addEventListener('click',()=>choose('colored'));
  underButton.addEventListener('click',()=>choose('underfloor'));
  coolingButton.addEventListener('click',()=>choose('cooling'));
  threeButton.addEventListener('click',()=>choose('3d'));
  frame.addEventListener('load',()=>choose(activeView,false));
  choose(new URLSearchParams(location.search).get('view')||'colored',false);
})();

window.addEventListener('w11-model-ready',()=>window.dispatchEvent(new CustomEvent('w11-source-view',{detail:new URLSearchParams(location.search).get('view')||'3d'})));
