(() => {
  const colored=document.querySelector('#colored-flow-view');
  const three=document.querySelector('#three-flow-view');
  const frame=document.querySelector('#colored-flow-frame');
  const coloredButton=document.querySelector('#view-colored');
  const threeButton=document.querySelector('#view-three');
  function choose(view,updateUrl=true) {
    const isColored=view!=='3d';
    colored.hidden=!isColored;three.hidden=isColored;
    const runState=document.querySelector('.run-state');if(runState)runState.hidden=isColored;
    coloredButton.setAttribute('aria-pressed',String(isColored));
    threeButton.setAttribute('aria-pressed',String(!isColored));
    frame.contentWindow?.postMessage({type:'w11-flow-visibility',active:isColored},location.origin);
    if(updateUrl){
      const url=new URL(location.href);url.searchParams.set('view',isColored?'colored':'3d');
      history.replaceState(null,'',url);
    }
    window.dispatchEvent(new Event('resize'));
  }
  window.addEventListener('message',event=>{
    if(event.source!==frame.contentWindow||event.origin!==location.origin||event.data?.type!=='w11-flow-height')return;
    const height=Number(event.data.height);
    if(Number.isFinite(height))frame.style.height=Math.max(720,Math.min(2400,height))+'px';
  });
  document.querySelector('a[href="#colored-flow-view"]')?.addEventListener('click',()=>choose('colored'));
  coloredButton.addEventListener('click',()=>choose('colored'));
  threeButton.addEventListener('click',()=>choose('3d'));
  frame.addEventListener('load',()=>choose(three.hidden?'colored':'3d',false));
  choose(new URLSearchParams(location.search).get('view')||'colored',false);
})();
