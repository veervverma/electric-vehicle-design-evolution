from pathlib import Path
import subprocess
r=Path.cwd();out=r/'work/flow-journey-publish/docs'
s=(r/'docs/side-flow.js').read_text()
s=s.replace('const MAX_PARTICLES=18000',"const journey=new URLSearchParams(location.search).has('journey');\nconst MAX_PARTICLES=journey?36000:18000")
s=s.replace("  geo=loaded;canvas.setAttribute",'''  geo=loaded;
  if(journey){
   const top=$('#region').value==='cooling';
   geo={...geo,view_m:{xmin:-3.7,xmax:6.3,zmin:top?.75:0,zmax:top?3.75:3},
    particle_band_m:top?[.76,3.74]:[.005,1.35],
    seed_regions_m:top?[[-3.6,-2.7,.85,3.65],[-2.7,3.1,1,3.5],[3.1,6.1,.85,3.65]]:[[-3.6,-2.7,.01,1.3],[-2.7,3.1,.01,.32],[3.1,6.1,.01,1.3]],
    vector_box_m:top?[-3.1,5.5,1,3.5]:[-3.1,5.5,.03,1.3],
    axis_note:top?'TOP PROJECTION · external tyre / sidepod / floor-edge flow · no internal ducts':'SIDE PROJECTION · front wing / tyres / lower-car / diffuser wake · projected floor gaps may be blocked',
    labels:top?[{x:-2.8,z:3.55,text:'FRONT WING'},{x:-1.9,z:1.02,text:'FRONT TYRES'},{x:.2,z:3.48,text:'SIDEPODS / FLOOR EDGES'},{x:3.4,z:3.4,text:'REAR WAKE'}]:[{x:-2.9,z:1.2,text:'FRONT WING + TYRES'},{x:-.5,z:1.55,text:'CHASSIS / SIDEPOD REGION'},{x:.3,z:.22,text:'PROJECTED FLOOR'},{x:3.25,z:1.2,text:'DIFFUSER / REAR WAKE'}]};
  }
  canvas.setAttribute''')
s=s.replace("const initialRegion=new URLSearchParams(location.search).get('region');",'''window.addEventListener('message',event=>{
 if(event.source!==parent||event.origin!==location.origin||event.data?.type!=='w11-journey-control')return;
 const {name,value}=event.data;
 if(['density','trail','rate','speed','target-re'].includes(name)){const el=$('#'+name);el.value=String(value);el.oninput();}
 else if(name==='grid'){$('#grid').value=String(value);loadGrid();}
 else if(name==='field'){$('#field').value=value;drawHeat();}
 else if(name==='running'){running=Boolean(value);$('#pause').textContent=running?'Pause':'Resume';if(running)request();}
 else if(name==='reset')reset();
});
if(journey){$('#density').value=100;$('#density-out').textContent='100%';$('#trail').value=80;$('#trail-out').textContent='80%';$('#grid').value='480';}
const initialRegion=new URLSearchParams(location.search).get('region');''')
(out/'side-flow.js').write_text(s)
s=(r/'docs/side-flow.html').read_text().replace('side-flow.js?v=20261118-projection1','side-flow.js?v=20261118-journey1')
s=s.replace('</head>','''<style>html.journey main{padding:0}html.journey .studio{display:block;min-height:0;border:0;border-radius:0}html.journey aside,html.journey .equations,html.journey .legend{display:none}html.journey .scene{padding:0}html.journey .axis-note{margin:8px 15px;font-size:11px}html.journey .stats{padding:8px 15px;gap:10px}html.journey #phase-note{font-size:10px}</style></head>''')
s=s.replace("<script>if(new URLSearchParams(location.search).has('embed'))", "<script>if(new URLSearchParams(location.search).has('journey'))document.documentElement.classList.add('journey');if(new URLSearchParams(location.search).has('embed'))")
(out/'side-flow.html').write_text(s)
for p in out.iterdir():(r/'docs'/p.name).write_text(p.read_text())
