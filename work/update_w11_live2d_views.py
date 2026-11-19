from pathlib import Path
import subprocess
root=Path.cwd();out=root/'work/live2d-publish/docs'
def head(p):return subprocess.check_output(['git','show','HEAD:'+p]).decode()
s=head('docs/lab-view-switch.js').replace("const isColored=view==='colored';","const isColored=view!=='3d';").replace("if(!isColored)window.dispatchEvent(new CustomEvent('w11-source-view',{detail:view}));","if(!isColored)window.dispatchEvent(new CustomEvent('w11-source-view',{detail:'3d'}));")
s=s.replace('Original W11 GLB · underside inspection + legacy external flow paths · unverified visualization, not new CFD','LIVE 2D · original W11 side projection · lower-car tracer focus · NOT an internal floor section').replace('Original W11 GLB · transparent sidepod inspection · internal ducts are not defined; no internal flow prediction','LIVE 2D · original W11 top projection · EXTERIOR sidepod airflow only · internal cooling geometry unavailable')
(out/'lab-view-switch.js').write_text(s)
s=head('docs/side-flow.js').replace("if(region!=='exterior')return;","if(!['exterior','underfloor','cooling'].includes(region))return;").replace('// Retired surrogate passage masks: only exterior projection remains in 2D.',"if(['underfloor','cooling'].includes(initialRegion))$('#region').value=initialRegion;")
# New mask filenames prevent stale surrogate masks from being served from cache.
s=s.replace("'w11-'+$('#region').value+'-mask-'","'w11-'+$('#region').value+'-projection-'")
s=s.replace("geo.region?' Passage velocity arrows'","geo.region?' Region velocity arrows'")
(out/'side-flow.js').write_text(s)
s=head('docs/side-flow.html').replace('<option value="exterior">Exterior · side projection</option>','<option value="exterior">Exterior · side projection</option><option value="underfloor">Lower car · same side projection</option><option value="cooling">Sidepods · exterior top projection</option>').replace('20261118-source1','20261118-projection1').replace('beneath the floor or inside the assumed cooling channels','near the lower car or around the exterior sidepods')
(out/'side-flow.html').write_text(s)
s=head('docs/wind-tunnel.html').replace('W11 FLOOR / DIFFUSER','LIVE 2D · LOWER CAR').replace('W11 SIDEPOD INSPECTION','LIVE 2D · SIDEPODS').replace('lab-view-switch.js?v=20261118-source1','lab-view-switch.js?v=20261118-projection1').replace('side-flow.html?embed=1&amp;v=20261118-passages','side-flow.html?embed=1&amp;v=20261118-projection1')
(out/'wind-tunnel.html').write_text(s)
for p in out.iterdir():
 if p.name!='wind-tunnel.html':(root/'docs'/p.name).write_text(p.read_text())
# Preserve unrelated local edits.
p=root/'docs/wind-tunnel.html';s=p.read_text().replace('W11 FLOOR / DIFFUSER','LIVE 2D · LOWER CAR').replace('W11 SIDEPOD INSPECTION','LIVE 2D · SIDEPODS').replace('lab-view-switch.js?v=20261118-source1','lab-view-switch.js?v=20261118-projection1').replace('side-flow.html?embed=1&amp;v=20261118-passages','side-flow.html?embed=1&amp;v=20261118-projection1');p.write_text(s)
