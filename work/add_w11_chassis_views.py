from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'docs/side-flow.html';s=p.read_text().replace('side-flow.js?v=20261118-fine','side-flow.js?v=20261118-passages')
s=s.replace('<aside><h2>Fine-grid flow controls</h2>', '''<aside><h2>Flow region and controls</h2>
 <label>Flow region<select id="region"><option value="exterior">Exterior · side projection</option><option value="underfloor">Underfloor / diffuser · section</option><option value="cooling">Cooling ducts · conceptual top plan</option></select></label>
 <p id="region-note" class="control-note"></p>''')
s=s.replace('<div class="legend">','<p id="axis-note" class="axis-note"></p>\n  <div class="legend">',1)
s=s.replace('Particles are restricted to the lower half: car and wake. The upper velocity color field is retained.', 'Exterior tracers focus on the lower half. Passage modes seed fluid regions beneath the floor or inside the assumed cooling channels.')
p.write_text(s)
p=root/'docs/side-flow.css';p.write_text(p.read_text()+'''
.axis-note{font-size:10px;color:#d4c2df;padding:8px 18px;margin:0;line-height:1.6}
#region-note{padding:9px;border-left:2px solid #ffcc64;background:#100e1880}
''')
p=root/'docs/side-flow.js';s=p.read_text()
a=s.index('function particleCeiling()');b=s.index('const stops=',a)
s=s[:a]+"""function particleBand(){
 return geo.particle_band_m?geo.particle_band_m.map(z=>z/geo.dx_m):[1,geo.ny-FLOW_VIEW.y-FLOW_VIEW.height/2];
}
function spawn(i){
 const regions=geo.seed_regions_m;
 const band=particleBand();
 for(let k=0;k<60;k++){
  if(regions){
   const r=regions[Math.floor(random()*regions.length)];
   px[i]=(r[0]-geo.xmin_m+random()*(r[1]-r[0]))/geo.dx_m;
   py[i]=(r[2]+random()*(r[3]-r[2]))/geo.dx_m;
  }else{px[i]=FLOW_VIEW.x+1+random()*(FLOW_VIEW.width-2);py[i]=band[0]+random()*(band[1]-band[0]);}
  if(!mask[Math.floor(py[i])*geo.nx+Math.floor(px[i])])break;
 }
 age[i]=Math.floor(random()*120);
}
""" +s[b:]
s=s.replace('let v=sample(px[i],py[i]);if(!v||py[i]>=particleCeiling()||age[i]++>210)', 'const band=particleBand();let v=sample(px[i],py[i]);if(!v||py[i]<band[0]||py[i]>=band[1]||age[i]++>210)')
s=s.replace('if(ny>=particleCeiling()||', 'if(ny<band[0]||ny>=band[1]||')
s=s.replace('ctx.save();ctx.beginPath();ctx.rect(0,canvas.height/2,canvas.width,canvas.height/2);ctx.clip();', "ctx.save();\n  if(!geo.region){ctx.beginPath();ctx.rect(0,canvas.height/2,canvas.width,canvas.height/2);ctx.clip();}")
old="""for(let y=stride;y<1.35/geo.dx_m;y+=stride)for(let x=Math.ceil((3.1-geo.xmin_m)/geo.dx_m);x<(6-geo.xmin_m)/geo.dx_m;x+=stride){"""
new="""const box=geo.vector_box_m||[3.1,6,.03,1.35];
  for(let y=Math.max(stride,Math.ceil(box[2]/geo.dx_m));y<box[3]/geo.dx_m;y+=stride)for(let x=Math.ceil((box[0]-geo.xmin_m)/geo.dx_m);x<(box[1]-geo.xmin_m)/geo.dx_m;x+=stride){"""
assert old in s;s=s.replace(old,new)
s=s.replace("ctx.fillText('FLOW →',18,24);", """ctx.fillText('FLOW →',18,24);
 if(geo.labels){
  ctx.font='14px system-ui';
  for(const label of geo.labels){
   const x=((label.x-geo.xmin_m)/geo.dx_m-viewX)*canvas.width/viewW;
   const y=(geo.ny-label.z/geo.dx_m-viewY)*canvas.height/viewH;
   const width=ctx.measureText(label.text).width;
   ctx.fillStyle='rgba(12,12,20,.86)';ctx.fillRect(x-5,y-16,width+10,23);
   ctx.fillStyle='#fff1cf';ctx.fillText(label.text,x,y);
  }
 }""")
s=s.replace("$('#grid').onchange=()=>loadGrid();", """$('#grid').onchange=()=>loadGrid();
function setRegion(region){
 if(!['exterior','underfloor','cooling'].includes(region))return;
 $('#region').value=region;loadGrid();
 if(parent!==window)parent.postMessage({type:'w11-region-changed',region},location.origin);
}
$('#region').onchange=()=>setRegion($('#region').value);
window.addEventListener('message',event=>{
 if(event.source!==parent||event.origin!==location.origin||event.data?.type!=='w11-flow-region')return;
 if(event.data.region!==$('#region').value)setRegion(event.data.region);
});""")
s=s.replace("fetch('w11-side-mask-'+$('#grid').value+'.json')", "fetch(($('#region').value==='exterior'?'w11-side-mask-':'w11-'+$('#region').value+'-mask-')+$('#grid').value+'.json')")
s=s.replace("const scale=geo.nx/480;Object.assign(FLOW_VIEW,{x:41.6*scale,y:50.88*scale,width:310.4*scale,height:93.12*scale});", """const scale=geo.nx/480;
  if(geo.view_m){
   const v=geo.view_m;Object.assign(FLOW_VIEW,{x:(v.xmin-geo.xmin_m)/geo.dx_m,y:geo.ny-v.zmax/geo.dx_m,width:(v.xmax-v.xmin)/geo.dx_m,height:(v.zmax-v.zmin)/geo.dx_m});
  }else Object.assign(FLOW_VIEW,{x:41.6*scale,y:50.88*scale,width:310.4*scale,height:93.12*scale});
  $('#region-note').textContent=geo.provenance?geo.provenance+' '+geo.limitation:'Exterior side projection: depth-separated parts overlap; this cannot show internal passages.';
  $('#axis-note').textContent=geo.axis_note||'Side projection · computed exterior flow · particles shown in the lower half.';
  $('#vectors').parentElement.lastChild.textContent=geo.region?' Passage velocity arrows':' Wake velocity arrows';""")
s=s.replace('await loadGrid();', """const initialRegion=new URLSearchParams(location.search).get('region');
if(['underfloor','cooling'].includes(initialRegion))$('#region').value=initialRegion;
await loadGrid();""")
p.write_text(s)
