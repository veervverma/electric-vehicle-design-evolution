import os,sys,math,struct,zipfile
sys.path.insert(0,'work')
from advanced_sedan import box,cyl,tube,beam,translate,write_stl,bounds
sys.path.insert(0,'work')
# Import V2 parts (regenerates source output, harmless).
import advanced_sedan_v2 as v2
OUT='outputs/portfolio_ev_sedan_v3'; os.makedirs(OUT,exist_ok=True)

# Additional engineering components.
# 8-module skateboard battery pack with busbar spine and high-voltage connector.
battery=box(7,0,0,105,53,3)
for i,x in enumerate((-36,-12,12,36)):
 for y in (-13,13):
  battery+=box(x,y,4,20,21,6)
  # module cooling ribs
  for rx in (-7,-3,1,5): battery+=box(x+rx,y,7.5,1.2,18,1)
battery+=box(7,0,8,92,4,3)
battery+=cyl(-47,0,8,3.2,8,'x',24)

# Rear e-axle motor, reduction gearbox, differential and half shafts.
motor=cyl(55,0,0,10,24,'x',48)
motor+=cyl(67,0,0,7,7,'x',40)
motor+=cyl(74,0,0,12,10,'x',48) # gearbox
motor+=cyl(80,0,0,8,5,'x',40)
for y in (-30,30): motor+=beam((80,0,0),(80,y,0),2.3,20)
# motor cooling fins
for x in (47,51,55,59,63): motor+=tube(x,0,0,11,10,1.5,'x',40)
# mounting feet
motor+=box(62,-10,-11,34,4,5)+box(62,10,-11,34,4,5)

# Inverter, controller and orange HV cable routing.
electronics=box(19,0,0,30,28,8)
for x in (9,14,19,24,29): electronics+=box(x,0,4.8,1.2,24,1.5)
electronics+=box(-18,0,0,22,20,7)
electronics+=beam((-7,0,1),(4,0,1),2.0,16)+beam((34,0,1),(45,0,1),2.0,16)

# Charging port and low-voltage service box.
service=box(0,0,0,20,14,8)+cyl(0,-8,0,4,4,'y',28)

extra={'15_skateboard_battery_pack':battery,'16_rear_motor_gearbox':motor,'17_inverter_controller':electronics,'18_charging_service_unit':service}
for n,M in extra.items(): write_stl(f'{OUT}/{n}.stl',M,n); print(n,bounds(M),len(M))

# Copy/emit all V2 meshes into V3 output for one self-contained folder.
parts=dict(v2.parts); parts.update(extra)
for n,M in v2.parts.items(): write_stl(f'{OUT}/{n}.stl',M,n)

# Material definitions (portfolio visualization; white exterior with technical accents).
materials=[
 ('Pearl White','#F4F4F1FF'),('Graphite Glass','#263746FF'),('Interior Black','#17191CFF'),
 ('Machined Aluminum','#AEB5BCFF'),('Tire Rubber','#171717FF'),('Brake Steel','#858A8FFF'),
 ('Performance Red','#D32929FF'),('Front LED','#B9E8FFFF'),('Rear LED','#FF3131FF'),
 ('Battery Blue','#3577B8FF'),('HV Orange','#F57C00FF'),('Electronics Gray','#555E68FF')]
mat_index={n:i for i,(n,c) in enumerate(materials)}

# name, mesh, translation, material
I=[]
def add(name,M,tr,mat): I.append((name,M,tr,mat))
add('White aerodynamic monocoque',v2.body,(0,0,0),'Pearl White')
add('Graphite fastback glasshouse',v2.cabin,(0,0,30),'Graphite Glass')
add('White removable vented hood',v2.hood,(0,0,27),'Pearl White')
add('Four-seat interior',v2.interior,(0,0,29),'Interior Black')
add('Swan-neck rear wing',v2.wing,(73,0,50),'Pearl White')
add('Front steering suspension',v2.front_susp,(-65,0,23),'Machined Aluminum')
add('Rear suspension',v2.rear_susp,(65,0,23),'Machined Aluminum')
# wheel corner assemblies
for ix,x in enumerate((-65,65)):
 for iy,y in enumerate((-47,47)):
  n=f'{"front" if x<0 else "rear"}_{"left" if y<0 else "right"}'
  add(n+' TPU tire',v2.tire,(x,y,14),'Tire Rubber')
  add(n+' ten-spoke rim',v2.rim,(x,y,14),'Machined Aluminum')
  add(n+' brake rotor',v2.rotor,(x,y,14),'Brake Steel')
  add(n+' wheel retainer',v2.cap,(x,y+(-6 if y<0 else 6),14),'Performance Red')
add('Front LED light bar',v2.front_lights,(0,0,0),'Front LED')
add('Rear LED light bar',v2.rear_lights,(0,0,0),'Rear LED')
add('Left aero mirror',v2.mirror,(-5,-44,48),'Pearl White')
add('Right aero mirror',v2.mirror,(-5,44,48),'Pearl White')
# components arranged in actual chassis coordinates. Body hides them in normal view; exploded file reveals them.
add('Skateboard battery pack',battery,(0,0,11),'Battery Blue')
add('Rear motor and reduction gearbox',motor,(0,0,18),'HV Orange')
add('Inverter and vehicle controller',electronics,(0,0,24),'Electronics Gray')
add('Charging and service unit',service,(72,0,27),'HV Orange')

# 3MF builder with correct Materials extension and object transforms.
def vf(M):
 d={};V=[];F=[]
 for tri in M:
  ids=[]
  for p in tri:
   p=tuple(round(q,5) for q in p)
   if p not in d:d[p]=len(V);V.append(p)
   ids.append(d[p])
  F.append(ids)
 return V,F

def make3mf(path,instances,explode=False):
 matxml='<m:basematerials id="900">'+''.join(f'<m:base name="{n}" displaycolor="{c}"/>' for n,c in materials)+'</m:basematerials>'
 objs=[];items=[]
 for oid,(name,M,tr,mat) in enumerate(instances,1):
  V,F=vf(M); vs=''.join(f'<vertex x="{x}" y="{y}" z="{z}"/>' for x,y,z in V); fs=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in F)
  objs.append(f'<object id="{oid}" name="{name}" type="model" pid="900" pindex="{mat_index[mat]}"><mesh><vertices>{vs}</vertices><triangles>{fs}</triangles></mesh></object>')
  tx,ty,tz=tr
  if explode:
   # Lift exterior; spread wheels/suspension; drop powertrain in layers.
   if 'glasshouse' in name: tz+=55
   elif 'hood' in name: tx-=25; tz+=42
   elif 'interior' in name: tz+=25
   elif 'wing' in name: tx+=20; tz+=30
   elif 'Front steering' in name: tx-=20; tz-=28
   elif 'Rear suspension' in name: tx+=20; tz-=28
   elif 'tire' in name or 'rim' in name or 'rotor' in name or 'retainer' in name: ty += -28 if ty<0 else 28
   elif 'battery' in name: tz-=32
   elif 'motor' in name: tz-=12; tx+=20
   elif 'Inverter' in name: tz+=15
   elif 'Charging' in name: tx+=22; tz+=12
  items.append(f'<item objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 {tx} {ty} {tz}"/>')
 model='<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02" requiredextensions="m"><metadata name="Title">Portfolio EV Sedan V3</metadata><resources>'+matxml+''.join(objs)+'</resources><build>'+''.join(items)+'</build></model>'
 rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
 ct='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('[Content_Types].xml',ct);z.writestr('_rels/.rels',rels);z.writestr('3D/3dmodel.model',model)

make3mf(f'{OUT}/EV_SEDAN_V3_ASSEMBLED_SHOWCASE.3mf',I,False)
make3mf(f'{OUT}/EV_SEDAN_V3_EXPLODED_TECHNICAL.3mf',I,True)

# Actual-geometry SVG renderer. Painter-sort triangles after isometric projection.
def render_svg(path,instances,explode=False,title=''):
 tris=[]
 for name,M,tr,mat in instances:
  tx,ty,tz=tr
  if explode:
   if 'glasshouse' in name: tz+=55
   elif 'hood' in name: tx-=25;tz+=42
   elif 'interior' in name:tz+=25
   elif 'wing' in name:tx+=20;tz+=30
   elif 'Front steering' in name:tx-=20;tz-=28
   elif 'Rear suspension' in name:tx+=20;tz-=28
   elif any(k in name for k in ('tire','rim','rotor','retainer')):ty+=-28 if ty<0 else 28
   elif 'battery' in name:tz-=32
   elif 'motor' in name:tz-=12;tx+=20
   elif 'Inverter' in name:tz+=15
   elif 'Charging' in name:tx+=22;tz+=12
  color=dict(materials)[mat][:7]
  # View: rotate z -35 deg, tilt 24 deg. Keep at most 1 in 2 triangles for manageable SVG.
  for q,(a,b,c) in enumerate(M):
   if q%2: continue
   pts=[]; depths=[]
   for x,y,z in (a,b,c):
    x+=tx;y+=ty;z+=tz
    az=-0.68; X=x*math.cos(az)-y*math.sin(az); Y=x*math.sin(az)+y*math.cos(az)
    el=0.40; sy=Y*math.sin(el)-z*math.cos(el); dep=Y*math.cos(el)+z*math.sin(el)
    pts.append((X,sy));depths.append(dep)
   # face brightness from projected orientation
   area=(pts[1][0]-pts[0][0])*(pts[2][1]-pts[0][1])-(pts[1][1]-pts[0][1])*(pts[2][0]-pts[0][0])
   tris.append((sum(depths)/3,pts,color,0.95 if area<0 else 0.82))
 tris.sort(key=lambda q:q[0],reverse=True)
 allp=[p for _,ps,_,_ in tris for p in ps]; minx=min(x for x,y in allp);maxx=max(x for x,y in allp);miny=min(y for x,y in allp);maxy=max(y for x,y in allp)
 W,H=1600,1000; s=min(1450/(maxx-minx),830/(maxy-miny)); ox=(W-s*(minx+maxx))/2;oy=100+(H-150-s*(miny+maxy))/2
 out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="#eef1f4"/><text x="70" y="65" font-family="Arial" font-size="34" font-weight="bold" fill="#17212b">{title}</text><text x="70" y="98" font-family="Arial" font-size="18" fill="#53606d">Portfolio engineering model • assembled envelope 198 × 111 × 72 mm</text>']
 for _,ps,col,op in tris:
  q=' '.join(f'{ox+s*x:.1f},{oy+s*y:.1f}' for x,y in ps);out.append(f'<polygon points="{q}" fill="{col}" fill-opacity="{op}" stroke="#2b343d" stroke-opacity=".10" stroke-width=".35"/>')
 out.append('</svg>');open(path,'w').write(''.join(out))

render_svg(f'{OUT}/assembled_showcase.svg',I,False,'EV SEDAN V3 — ASSEMBLED SHOWCASE')
render_svg(f'{OUT}/exploded_technical.svg',I,True,'EV SEDAN V3 — EXPLODED TECHNICAL VIEW')

open(f'{OUT}/PORTFOLIO_NOTES.txt','w').write('''EV SEDAN V3 — COLLEGE PORTFOLIO NOTES\n\nDESIGN INTENT\nA printable electric performance sedan study combining industrial design, mechanical packaging and design-for-additive-manufacturing. The exterior is a low fastback with functional aero cues; the technical model includes a skateboard battery, rear e-axle motor and reduction gearbox, power electronics, suspension, steering rack, brakes and a four-seat interior.\n\nWHAT TO SHOW\n1. Open EV_SEDAN_V3_ASSEMBLED_SHOWCASE.3mf for the complete color-coded vehicle.\n2. Open EV_SEDAN_V3_EXPLODED_TECHNICAL.3mf to explain how systems fit together.\n3. Use assembled_showcase.svg and exploded_technical.svg as portfolio images.\n4. Photograph your printed prototype next to design sketches and failed/test parts.\n\nENGINEERING STORY\n- Packaging: flat battery pack low between axles; e-axle and inverter positioned near rear drive unit.\n- Dynamics: low center of gravity, wide track, double-wishbone-style arms and visible brake rotors.\n- Manufacturing: body split into printable modules; TPU tires and rigid PETG structural parts; alignment pegs and wheel retainers simplify assembly.\n- Iteration: evolved from a bare skateboard chassis to a sedan, then to a modular suspension model and finally a system-level portfolio prototype.\n\nIMPORTANT\nThis is an educational scale prototype, not a road-safe vehicle design. Validate tolerances and motor temperatures before powered testing.\n''')

for f in ('EV_SEDAN_V3_ASSEMBLED_SHOWCASE.3mf','EV_SEDAN_V3_EXPLODED_TECHNICAL.3mf'):
 with zipfile.ZipFile(f'{OUT}/{f}') as z: assert z.testzip() is None
print('created',OUT,'instances',len(I))
