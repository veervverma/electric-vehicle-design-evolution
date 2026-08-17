import os, sys, math, struct, zipfile
sys.path.insert(0,'work')
# Import mesh primitives. This also refreshes V1 outputs.
from advanced_sedan import box,cyl,tube,beam,loft,translate,write_stl,bounds
OUT='outputs/advanced_ev_sedan_v2'; os.makedirs(OUT,exist_ok=True)

def merge(*ms):
 r=[]
 for m in ms:r+=m
 return r

def ring_spokes(ro=13, hub=4.2, width=7.5, spokes=10):
 M=tube(0,0,0,ro,ro-2.2,width,'y',56)+tube(0,0,0,hub+2.2,hub,width,'y',40)
 for k in range(spokes):
  a=2*math.pi*k/spokes
  M+=beam(((hub+1.5)*math.cos(a),-width/2+0.6,(hub+1.5)*math.sin(a)),((ro-1.5)*math.cos(a+0.10),-width/2+0.6,(ro-1.5)*math.sin(a+0.10)),1.0,10)
 return M

# --- Main monocoque with stronger aerodynamic details ---
secs=[(-98,18,14,11),(-94,31,18,13),(-84,40,23,16),(-67,45,27,19),(-35,47,29,20),(5,47,30,21),(42,46,29,20),(70,43,26,18),(88,37,22,15),(97,22,16,11)]
body=loft(secs,n_y=18,bottom=7)
# splitter + canards + skirts + venturi floor
body+=box(-91,0,5.5,18,78,3)
for s in (-1,1):
 body+=box(-87,s*39,10,20,8,2)+beam((-92,s*38,8),(-76,s*45,13),1.2)
 body+=box(4,s*46.5,9.5,142,3,6)
body+=box(7,0,7.8,118,57,2.6)
# diffuser with six vertical channels
body+=box(87,0,8,18,72,2.5)
for y in (-30,-18,-6,6,18,30): body+=box(88,y,11,20,1.8,8)
# lower grille slats and side intake blades
for y in range(-24,25,8): body+=box(-91,y,15,8,2,5)
for s in (-1,1):
 for x in (-36,-28,-20): body+=box(x,s*44,18,5,2,8)
# battery/motor chassis tray, rails, crossmembers
body+=box(4,0,8.8,112,58,3)
for y in (-27,27): body+=box(4,y,12,120,3,7)
for x in (-48,-10,28,60): body+=box(x,0,12,3,55,7)
# front motor cradle sized for 130 motor body (~20x38)
body+=box(-57,0,17,44,3,8)
for y in (-13,13): body+=box(-57,y,17,44,3,8)
# four cabin locator pegs and interior locator pegs
for x in (-25,30):
 for y in (-25,25): body+=cyl(x,y,30,2.5,5,'z',28)
for x in (-22,25):
 for y in (-16,16): body+=cyl(x,y,29.5,1.8,4,'z',24)

# --- Fastback cabin shell ---
cabsecs=[(-46,29,3,1),(-36,34,17,7),(-20,37,29,13),(5,38,34,16),(28,36,30,13),(48,31,16,6),(58,23,3,1)]
cabin=loft(cabsecs,n_y=18,bottom=0)
# roof spine and camera/scoop pod
cabin+=box(5,0,34.5,34,7,2)+box(20,0,36,10,5,2)
# window-frame rails and B pillars
for s in (-1,1):
 cabin+=beam((-34,s*33,7),(-17,s*36,25),1.5)
 cabin+=beam((-17,s*36,25),(28,s*34,25),1.4)
 cabin+=beam((28,s*34,25),(47,s*29,8),1.5)
 cabin+=beam((4,s*36,7),(4,s*36,28),1.5)

# --- Removable hood with heat extraction vents ---
hoodsecs=[(-79,35,2.8,1),(-67,39,5,2),(-52,41,6,2),(-40,39,4,1)]
hood=loft(hoodsecs,n_y=12,bottom=0)
# NACA-style raised vent lips
for s in (-1,1):
 hood+=beam((-61,s*13,6),(-47,s*17,5),1.2)
 hood+=beam((-61,s*13,6),(-47,s*9,5),1.2)
# underside locating tabs
for x in (-67,-48):
 for y in (-25,25): hood+=box(x,y,-2,5,5,4)

# --- Interior tub: floor, four bucket seats, console, dash, steering wheel ---
interior=box(5,0,1.5,78,54,3)
# seat helper: base + back + side bolsters
for x in (-12,24):
 for y in (-14,14):
  interior+=box(x,y,5,15,11,5)+box(x+5,y,12,5,13,17)
  interior+=box(x,y-6,8,14,2,10)+box(x,y+6,8,14,2,10)
interior+=box(-8,0,6,54,6,9) # center console
interior+=box(-30,0,11,6,50,12) # dashboard
interior+=cyl(-26,-14,16,6,2.5,'x',32)+beam((-28,-14,16),(-32,-14,13),1.5)

# --- Rear wing with swan-neck mounts and DRS-like center slot ---
wing=box(0,-21,0,38,35,2.6)+box(0,21,0,38,35,2.6)
wing+=box(0,-40,2,42,3,12)+box(0,40,2,42,3,12)
for s in (-1,1):
 wing+=beam((-10,s*22,-10),(-2,s*18,0),2.0)+beam((12,s*22,-10),(4,s*18,0),2.0)

# --- Suspension module V2: wishbones, upright, coil-over look, steering/tie rod ---
def suspension(front=False):
 M=box(0,0,0,28,58,3)
 for s in (-1,1):
  y=s*35
  # paired upper/lower control arms
  for z,r in ((-3,1.7),(-13,2.0)):
   M+=beam((-11,s*23,z),(0,y,-9),r)+beam((11,s*23,z),(0,y,-9),r)
  M+=beam((0,y,-15),(0,y,1),2.2) # upright
  M+=beam((8,s*22,0),(0,y,-10),1.8) # damper
  # coil rings around damper shaft approximation
  for q in range(5):
   t=q/4; px=8*(1-t); py=s*(22+13*t); pz=-10*t
   M+=cyl(px,py,pz,2.8,1.0,'z',16)
  M+=cyl(0,s*41,-9,3.8,14,'y',36)
 if front:
  M+=beam((0,-35,-7),(0,35,-7),1.5) # tie rod
  M+=box(-4,0,-7,8,14,4) # rack housing
 M+=box(0,0,-4,12,70,2.2) # transverse flexure
 return M
front_susp=suspension(True); rear_susp=suspension(False)

# --- Three-piece wheel system: TPU tire, rigid rim, brake rotor/caliper ---
tire=tube(0,0,0,17.2,13.3,10.5,'y',64)
# tread blocks arranged as longitudinal ribs; attached to tire shell
for k in range(32):
 a=2*math.pi*k/32
 # short cylinders used as radial tread lugs
 tire+=cyl(16.7*math.cos(a),0,16.7*math.sin(a),1.6,11,'y',12)
rim=ring_spokes(13.5,4.15,8.2,10)
# outer rim lip
rim+=tube(0,-4.0,0,14.2,13.3,1.1,'y',56)
rotor=tube(0,0,0,10.2,4.2,1.8,'y',48)
# rotor drill pattern
for k in range(10):
 a=2*math.pi*k/10; rotor+=cyl(7.7*math.cos(a),-1.0,7.7*math.sin(a),0.8,2.2,'y',12)
rotor+=box(8,0,0,4,4,8) # visible caliper block
cap=cyl(0,0,0,5.8,2.5,'y',36)+cyl(0,1.7,0,3.45,3.4,'y',32)

# --- Detail inserts ---
front_lights=beam((-91,-30,21),(-91,30,21),1.8,24)
rear_lights=beam((88,-31,21),(88,31,21),1.8,24)
mirror=box(0,0,0,10,5,3)+beam((-4,0,-1),(-7,0,-5),1.2)

parts={
 '01_monocoque_body':body,'02_fastback_cabin':cabin,'03_removable_vented_hood':hood,
 '04_interior_tub':interior,'05_swan_neck_rear_wing':wing,
 '06_front_steering_suspension':front_susp,'07_rear_suspension':rear_susp,
 '08_tpu_tire_x4':tire,'09_sport_rim_x4':rim,'10_brake_rotor_x4':rotor,
 '11_wheel_cap_x4':cap,'12_front_light_insert':front_lights,'13_rear_light_insert':rear_lights,
 '14_mirror_x2':mirror}
for n,M in parts.items(): write_stl(f'{OUT}/{n}.stl',M,n); print(n,bounds(M),len(M))

# Assembled reference. Coordinates are aesthetic/reference, not a one-piece functional print.
A=list(body)
A+=translate(cabin,0,0,30)+translate(hood,0,0,27)+translate(interior,0,0,29)+translate(wing,73,0,50)
A+=translate(front_susp,-65,0,23)+translate(rear_susp,65,0,23)
for x in (-65,65):
 for y in (-47,47):
  A+=translate(tire,x,y,14)+translate(rim,x,y,14)+translate(rotor,x,y,14)+translate(cap,x,y+(-6 if y<0 else 6),14)
A+=front_lights+rear_lights+translate(mirror,-5,-44,48)+translate(mirror,-5,44,48)
write_stl(f'{OUT}/advanced_sedan_v2_assembled_reference.stl',A,'advanced_sedan_v2_assembled_reference')
print('ASSEMBLY',bounds(A),len(A))

# Build kit 3MF with individually named meshes at origin; slicer user arranges batches.
def vf(M):
 d={};V=[];F=[]
 for tri in M:
  ids=[]
  for p in tri:
   p=tuple(round(v,5) for v in p)
   if p not in d:d[p]=len(V);V.append(p)
   ids.append(d[p])
  F.append(ids)
 return V,F
instances=[]
for n,M in parts.items():
 count=4 if '_x4' in n else 2 if '_x2' in n else 1
 for i in range(count): instances.append((n.replace('_x4','').replace('_x2','')+(f'_{i+1}' if count>1 else ''),M))
objs=[]
for oid,(n,M) in enumerate(instances,1):
 V,F=vf(M); vs=''.join(f'<vertex x="{x}" y="{y}" z="{z}"/>' for x,y,z in V); fs=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in F)
 objs.append(f'<object id="{oid}" name="{n}" type="model"><mesh><vertices>{vs}</vertices><triangles>{fs}</triangles></mesh></object>')
build=''.join(f'<item objectid="{i}"/>' for i in range(1,len(instances)+1))
model='<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><metadata name="Title">Advanced EV Sedan V2 Kit</metadata><resources>'+''.join(objs)+'</resources><build>'+build+'</build></model>'
rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
ct='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
with zipfile.ZipFile(f'{OUT}/advanced_ev_sedan_v2_kit.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml',ct);z.writestr('_rels/.rels',rels);z.writestr('3D/3dmodel.model',model)

open(f'{OUT}/PRINT_GUIDE.txt','w').write('''ADVANCED EV SEDAN V2 — PRINT GUIDE\n\nFEATURES\nFastback aero body, removable vented hood, four-seat interior, dashboard and steering wheel, swan-neck wing, splitter, canards, skirts, diffuser, front steering rack, double-wishbone-style suspension, separate TPU tires, detailed ten-spoke rims, brake rotors/calipers, light inserts, mirrors, battery tray and 130-size motor cradle.\n\nRECOMMENDED MATERIALS\nRigid parts: PETG (preferred) or PLA+. Tires: TPU 95A. Light inserts: transparent PETG optional.\n\nSLICER STARTING POINT\n0.20 mm layers; 4 walls; 5 top/bottom layers; 20-25% gyroid infill. Use build-plate supports for suspension, mirrors and wing. Print the monocoque separately.\n\nQUANTITIES\n1 each: body, cabin, hood, interior, wing, front suspension, rear suspension, front light, rear light.\n4 each: tire, rim, brake rotor, wheel cap.\n2 mirrors.\nTotal final pieces: 29.\n\nASSEMBLY ORDER\n1. Install interior and glue cabin to body pegs.\n2. Fit removable hood; lightly sand tabs if tight.\n3. Glue suspension bridges under body at x +/-65 mm. Keep arms/flexure clear of glue.\n4. Insert brake rotor, rim and TPU tire onto each axle. Glue cap to axle tip only.\n5. Glue wing, mirrors and lights.\n6. Fit a 130 motor in the 44 x 26 mm front cradle. Motor-to-wheel gearing remains a custom drivetrain step.\n\nASSEMBLED ENVELOPE\nApprox. 195 x 105 x 70 mm; fits a 220 x 220 x 250 mm printer. Always print a small tolerance test before committing to the complete kit.\n''')
