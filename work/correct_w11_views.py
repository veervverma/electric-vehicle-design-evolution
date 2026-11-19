from pathlib import Path
import subprocess
r=Path.cwd(); out=r/'work/w11-correction/docs'
def head(p):return subprocess.check_output(['git','show','HEAD:'+p]).decode()
s=head('docs/lab-view-switch.js').replace("const isColored=view!=='3d';","const isColored=view==='colored';\n    if(!isColored)window.dispatchEvent(new CustomEvent('w11-source-view',{detail:view}));")
s=s.replace("underfloor:'Underfloor / diffuser · actual section of the repaired W11 shell at y = +0.45 m · 2D calculation, not validated 3D floor performance'","underfloor:'Original W11 GLB · underside inspection + legacy external flow paths · unverified visualization, not new CFD'").replace("cooling:'Cooling channels · hypothetical internal passages in the W11 top projection · calculated 2D flow, not Mercedes duct CAD or thermal analysis'","cooling:'Original W11 GLB · transparent sidepod inspection · internal ducts are not defined; no internal flow prediction'")
s += "\nwindow.addEventListener('w11-model-ready',()=>window.dispatchEvent(new CustomEvent('w11-source-view',{detail:new URLSearchParams(location.search).get('view')||'3d'})));\n"
(out/'lab-view-switch.js').write_text(s)
s=head('docs/wind-tunnel.html').replace('COOLING CHANNELS · CONCEPT','W11 SIDEPOD INSPECTION').replace('UNDERFLOOR / DIFFUSER','W11 FLOOR / DIFFUSER').replace('wind-tunnel.js?v=20261115-integrated','w11-source-view.js?v=20261118-source1').replace('lab-view-switch.js?v=20261118-passages','lab-view-switch.js?v=20261118-source1')
(out/'wind-tunnel.html').write_text(s)
s=head('docs/wind-tunnel.js')
s=s.replace("addCar(gltf); addFlow(flow); loading.hidden = true; setMode('drive');","addCar(gltf); addFlow(flow); loading.hidden = true; setMode('all'); window.dispatchEvent(new Event('w11-model-ready'));")
s += '''
// Source-model inspection only: no invented cooling duct geometry or paths.
let sourceInspection = '3d';
const sourceMaterials = new Map();
function sourceView(view) {
  sourceInspection=view;
  if(!car)return;
  resetDrivePose(); setAutoDrive(false);
  car.traverse(node=>{
    if(!node.isMesh)return;
    for(const m of (Array.isArray(node.material)?node.material:[node.material])){
      if(!sourceMaterials.has(m))sourceMaterials.set(m,{transparent:m.transparent,opacity:m.opacity,depthWrite:m.depthWrite});
      const original=sourceMaterials.get(m);
      m.transparent=view==='cooling'?true:original.transparent;
      m.opacity=view==='cooling'?.22:original.opacity;
      m.depthWrite=view==='cooling'?false:original.depthWrite;
      m.needsUpdate=true;
    }
  });
  if(view==='underfloor'){
    setMode('focus');
    cameraGoal={position:new THREE.Vector3(95,-105,155),target:new THREE.Vector3(0,7,0)};
    tunnelGroup.visible=false;
    document.querySelector('#status-detail').textContent='ORIGINAL W11 UNDERSIDE · legacy external flow · NOT validated CFD';
  }else if(view==='cooling'){
    setMode('inspect'); setCamera('iso'); tunnelGroup.visible=false;
    document.querySelector('#status-detail').textContent='ORIGINAL W11 SIDEPODS · transparent inspection ONLY · no defined internal ducts';
  }else{setMode('all');setCamera('iso');tunnelGroup.visible=document.querySelector('#tunnel').checked;}
}
window.addEventListener('w11-source-view',event=>sourceView(event.detail));
'''
(out/'w11-source-view.js').write_text(s)
# Remove misleading old passage selections, including standalone pages.
s=head('docs/side-flow.html');import re
s=re.sub(r'<option value="(?:underfloor|cooling)"[^>]*>.*?</option>','',s)
(out/'side-flow.html').write_text(s.replace('20261118-passages','20261118-source1'))
s=head('docs/side-flow.js').replace("if(!['exterior','underfloor','cooling'].includes(region))return;","if(region!=='exterior')return;").replace("if(['underfloor','cooling'].includes(initialRegion))$('#region').value=initialRegion;","// Retired surrogate passage masks: only exterior projection remains in 2D.")
(out/'side-flow.js').write_text(s)
for f in out.iterdir():
 if f.name!='wind-tunnel.html':(r/'docs'/f.name).write_text(f.read_text())
# Preserve unrelated working-tree HTML edits while updating its script links/labels.
p=r/'docs/wind-tunnel.html';s=p.read_text();s=re.sub(r'src="wind-tunnel.js\?[^\"]+"','src="w11-source-view.js?v=20261118-source1"',s);s=re.sub(r'src="lab-view-switch.js\?[^\"]+"','src="lab-view-switch.js?v=20261118-source1"',s);s=s.replace('COOLING CHANNELS · CONCEPT','W11 SIDEPOD INSPECTION').replace('UNDERFLOOR / DIFFUSER','W11 FLOOR / DIFFUSER');p.write_text(s)
