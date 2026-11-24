from pathlib import Path
r=Path.cwd();out=r/'work/reference-physics-publish/docs'
s=(r/'docs/side-flow.js').read_text();s="import {buildWing} from './reference-wing.js?v=20261124';\n"+s
s=s.replace('let epoch=0;',"let epoch=0;\nconst wingDemo=new URLSearchParams(location.search).has('wing');\nlet wingAngle=4,wingInverted=false,pressureArrows=false,probe=null;")
s=s.replace("  const response=await fetch(","  const response=wingDemo?null:await fetch(")
s=s.replace("  if(!response.ok)throw Error('Selected W11 grid unavailable');\n  const loaded=await response.json();", "  if(response&&!response.ok)throw Error('Selected W11 grid unavailable');\n  const loaded=wingDemo?buildWing(Number($('#grid').value),wingAngle,wingInverted):await response.json();")
s=s.replace('  if(journey){\n   const top=', '  if(journey&&!wingDemo){\n   const top=')
s=s.replace('latest=null;ux=null;uy=null;rho=null;', 'probe=null;latest=null;ux=null;uy=null;rho=null;')
s=s.replace(" else if(name==='reset')reset();", " else if(name==='reset')reset();\n else if(name==='arrows')pressureArrows=Boolean(value);\n else if(name==='wing-angle'&&wingDemo){wingAngle=Number(value);loadGrid();}\n else if(name==='wing-inverted'&&wingDemo){wingInverted=Boolean(value);loadGrid();}")
marker=" // Resolve silhouette edges directly from the W11 mask."
addition=''' // Qualitative pressure-force direction from adjacent fluid samples, not integrated loads.
 if(pressureArrows){
  const jump=Math.max(2,Math.round(geo.nx/180));
  for(let y=2;y<geo.ny-2;y+=jump)for(let x=2;x<geo.nx-2;x+=jump){
   const i=y*geo.nx+x;if(mask[i])continue;
   const gx=mask[i+1]-mask[i-1],gy=mask[i+geo.nx]-mask[i-geo.nx];const norm=Math.hypot(gx,gy);if(!norm)continue;
   const cp=(rho[i]-1)/(.5*3*latest.U*latest.U);if(Math.abs(cp)<.08)continue;
   const ax=(x-viewX)*canvas.width/viewW,ay=(geo.ny-y-viewY)*canvas.height/viewH;
   if(ax<0||ax>canvas.width||ay<0||ay>canvas.height)continue;
   const len=Math.min(26,4+Math.abs(cp)*7),sgn=Math.sign(cp),bx=ax+sgn*gx/norm*len,by=ay-sgn*gy/norm*len,a=Math.atan2(by-ay,bx-ax);
   ctx.strokeStyle=cp>0?'#ff786b':'#70d8ff';ctx.lineWidth=1.8;ctx.beginPath();ctx.moveTo(ax,ay);ctx.lineTo(bx,by);ctx.lineTo(bx-5*Math.cos(a-.55),by-5*Math.sin(a-.55));ctx.moveTo(bx,by);ctx.lineTo(bx-5*Math.cos(a+.55),by-5*Math.sin(a+.55));ctx.stroke();
  }
 }
 if(probe){
  const x=Math.floor(probe[0]),y=Math.floor(probe[1]),i=y*geo.nx+x;
  if(i>geo.nx&&i<mask.length-geo.nx&&!mask[i]){
   const speed=Math.hypot(ux[i],uy[i])/latest.U,cp=(rho[i]-1)/(.5*3*latest.U*latest.U),ideal=1-speed*speed;
   const text='PROBE · |u|/U '+speed.toFixed(2)+' · Cp (solver) '+cp.toFixed(2)+' · 1−(|u|/U)² '+ideal.toFixed(2)+' (ideal comparison only)';
   $('#probe-readout').textContent=text;
   const xx=(probe[0]-viewX)*canvas.width/viewW,yy=(geo.ny-probe[1]-viewY)*canvas.height/viewH;ctx.strokeStyle='#9cffad';ctx.lineWidth=2;ctx.beginPath();ctx.arc(xx,yy,7,0,7);ctx.stroke();
  }
 }
'''
s=s.replace(marker,addition+marker)
s=s.replace("$('#field').onchange=drawHeat;",'''canvas.addEventListener('click',event=>{
 if(!geo||!ux)return;const rect=canvas.getBoundingClientRect();const x=FLOW_VIEW.x+(event.clientX-rect.left)/rect.width*FLOW_VIEW.width,y=geo.ny-(FLOW_VIEW.y+(event.clientY-rect.top)/rect.height*FLOW_VIEW.height);
 const i=Math.floor(y)*geo.nx+Math.floor(x);if(mask[i]){$('#probe-readout').textContent='Solid obstacle: click a fluid cell outside the car / wing.';probe=null;}else probe=[x,y];
});
$('#field').onchange=drawHeat;''')
(out/'side-flow.js').write_text(s)
s=(r/'docs/side-flow.html').read_text().replace('side-flow.js?v=20261118-journey1','side-flow.js?v=20261124-refs1')
s=s.replace('<p id="phase-note"', '<p id="probe-readout" class="axis-note">Click the fluid to probe local speed and pressure. Red arrows = positive-pressure push; blue = suction direction. Qualitative, not integrated forces.</p><p id="phase-note"')
(out/'side-flow.html').write_text(s)
for p in out.iterdir():(r/'docs'/p.name).write_text(p.read_text())
