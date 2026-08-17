import os,sys,math,zipfile
sys.path.insert(0,'work')
from advanced_sedan import box,cyl,tube,beam,loft,translate,write_stl,bounds
OUT='outputs/formula_ev_prototype';os.makedirs(OUT,exist_ok=True)

def sidepod(s):
 # tapered sidepod shell, mirrored by y center
 y=s*31
 sec=[(-20,18,18,13),(0,22,22,15),(30,21,20,14),(58,12,15,11)]
 M=[]
 # Each loft section uses y width; build centered then shift to side.
 M=translate(loft(sec,n_y=12,bottom=7),0,y,0)
 # intake lip and cooling vanes
 M+=tube(-17,y,16,9,6,4,'x',32)
 for x in (8,17,26,35): M+=box(x,y+s*14,17,2,2,11)
 return M

def wing_element(cx,cz,length,width,thick=2.2):
 return box(cx,0,cz,length,width,thick)

# Carbon monocoque / survival cell.
tubsecs=[(-86,7,10,8),(-70,10,14,10),(-48,14,22,14),(-22,20,31,18),(12,21,34,19),(42,19,28,17),(66,15,20,14),(78,11,15,11)]
monocoque=loft(tubsecs,n_y=16,bottom=7)
# keel and impact structures
monocoque+=box(-56,0,6,72,12,5)+box(48,0,7,58,20,5)
for x in (-45,-10,25,58): monocoque+=box(x,0,9,3,34 if x>-30 else 22,6)
# nose camera pod
monocoque+=box(-58,0,20,18,6,4)
# cockpit rim beams
monocoque+=beam((-18,-19,28),(27,-18,29),1.6)+beam((-18,19,28),(27,18,29),1.6)

# Detachable nose and crash cone.
nosesecs=[(-103,3,8,7),(-94,5,9,7),(-82,8,12,8),(-68,11,15,10),(-57,13,17,11)]
nose=loft(nosesecs,n_y=12,bottom=6)
nose+=box(-58,0,9,5,18,6)
for y in (-7,7):nose+=cyl(-57,y,13,2.4,4,'x',20)

# Ground-effect floor with twin venturi tunnels and diffuser strakes.
floor=box(7,0,4.5,145,72,3)
for y in (-31,31):floor+=box(13,y,7,120,4,8)
for y in (-22,-10,10,22):floor+=box(63,y,8,35,1.8,10)
# floor edge fences
for s in (-1,1):floor+=box(8,s*37,8,138,2,10)

# Sidepods and radiator duct detailing.
sidepods=sidepod(-1)+sidepod(1)
for s in (-1,1):
 sidepods+=beam((-8,s*25,26),(48,s*23,21),1.5)
 sidepods+=box(44,s*31,13,30,10,4)

# Multi-element front wing and endplates.
front_wing=wing_element(-94,5,18,142,2.5)+wing_element(-88,9,16,130,2.0)+wing_element(-82,12,14,112,1.8)
for s in (-1,1):
 front_wing+=box(-91,s*72,13,30,3,21)
 front_wing+=beam((-96,s*58,7),(-76,s*48,15),1.3)
# center pylons
front_wing+=beam((-88,-5,7),(-72,-5,15),1.8)+beam((-88,5,7),(-72,5,15),1.8)

# Rear wing: beam element + flap + endplates + swan-neck pylons.
rear_wing=wing_element(83,48,25,115,3)+wing_element(77,57,18,108,2.5)
for s in (-1,1):rear_wing+=box(80,s*59,49,31,3,31)
for s in (-1,1):
 rear_wing+=beam((62,s*18,25),(80,s*24,46),2.3)+beam((72,s*18,25),(84,s*24,46),2.3)

# Halo protection structure.
halo=beam((-10,-17,34),(-10,-5,50),2.5)+beam((-10,17,34),(-10,5,50),2.5)
halo+=beam((-10,-5,50),(25,-5,45),2.5)+beam((-10,5,50),(25,5,45),2.5)
halo+=beam((25,-5,45),(29,0,34),2.5)+beam((25,5,45),(29,0,34),2.5)

# Cockpit seat, headrest, steering wheel and dash.
cockpit=box(4,0,13,48,24,4)+box(18,0,22,8,19,22)
cockpit+=box(-16,0,21,5,25,12)+cyl(-12,0,28,6,2.5,'x',32)+beam((-15,0,28),(-20,0,24),1.4)
for s in (-1,1):cockpit+=box(19,s*10,28,12,4,10)

# Formula pushrod suspension modules.
def suspension(front=True):
 M=[]; xc=0
 inner=18 if front else 16; outer=52
 for s in (-1,1):
  y=s*outer
  # double wishbones
  for z,r in ((11,1.7),(22,1.5)):
   M+=beam((-12,s*inner,z),(0,y,15),r)+beam((12,s*inner,z),(0,y,15),r)
  # upright and axle
  M+=beam((0,y,8),(0,y,25),2.0)+cyl(0,s*(outer+6),16,3.8,16,'y',36)
  # pushrod to central rocker
  M+=beam((0,y,20),(8,s*8,30),1.6)
  # toe link
  M+=beam((-6,s*inner,14),(0,y,14),1.3)
 # inboard dampers
 M+=beam((8,-8,30),(22,-4,20),2.1)+beam((8,8,30),(22,4,20),2.1)
 if front:M+=beam((-4,-52,14),(-4,52,14),1.3)+box(-4,0,14,8,12,4)
 return M
front_susp=suspension(True);rear_susp=suspension(False)

# Slick tire and detailed center-lock rim.
tire=tube(0,0,0,18,13.5,13,'y',64)
# shallow circumferential identification grooves
for yy in (-5,5):tire+=tube(0,yy,0,18.35,17.8,1.1,'y',64)
rim=tube(0,0,0,13.7,11.5,10,'y',56)+tube(0,0,0,6.2,3.9,10,'y',40)
for k in range(12):
 a=2*math.pi*k/12
 rim+=beam((5.5*math.cos(a),-4.2,5.5*math.sin(a)),(12.1*math.cos(a+.10),-4.2,12.1*math.sin(a+.10)),1.0,10)
rotor=tube(0,0,0,10.8,4.1,2,'y',48)
rotor+=box(8.5,0,0,4,4,9)
centerlock=cyl(0,0,0,5.8,3,'y',36)+cyl(0,2.2,0,3.4,4,'y',32)

# EV powertrain: flat battery and compact rear e-motor.
battery=box(10,0,0,96,30,4)
for x in (-30,-10,10,30):
 for y in (-8,8):battery+=box(x,y,4,16,12,6)
battery+=box(10,0,8,82,3,3)
motor=cyl(61,0,0,11,25,'x',48)+cyl(74,0,0,13,9,'x',48)+cyl(82,0,0,8,7,'x',40)
for x in (53,57,61,65,69):motor+=tube(x,0,0,12,11,1.4,'x',40)
for y in (-45,45):motor+=beam((82,0,0),(82,y,0),2.2,20)
inverter=box(38,0,0,28,24,9)
for x in (28,33,38,43,48):inverter+=box(x,0,5,1.2,21,1.5)

parts={'01_carbon_monocoque':monocoque,'02_detachable_nose':nose,'03_ground_effect_floor':floor,'04_sidepods_radiator_ducts':sidepods,'05_front_wing':front_wing,'06_rear_wing':rear_wing,'07_halo':halo,'08_cockpit_insert':cockpit,'09_front_pushrod_suspension':front_susp,'10_rear_pushrod_suspension':rear_susp,'11_slick_tire_x4':tire,'12_centerlock_rim_x4':rim,'13_brake_rotor_x4':rotor,'14_centerlock_nut_x4':centerlock,'15_battery_pack':battery,'16_motor_gearbox':motor,'17_inverter':inverter}
for n,M in parts.items():write_stl(f'{OUT}/{n}.stl',M,n);print(n,bounds(M),len(M))

# Assembled coordinates and materials.
materials=[('White Carbon','#F3F3F0FF'),('Black Carbon','#202328FF'),('Tire','#151515FF'),('Aluminum','#AEB4BAFF'),('Brake','#777D83FF'),('Red','#D32626FF'),('Battery','#2C74B3FF'),('HV Orange','#F47A00FF'),('Cockpit','#323A43FF')]
mi={n:i for i,(n,c) in enumerate(materials)}
I=[]
def add(n,M,t,mat):I.append((n,M,t,mat))
add('Carbon monocoque',monocoque,(0,0,0),'White Carbon');add('Nose cone',nose,(0,0,0),'White Carbon');add('Ground effect floor',floor,(0,0,0),'Black Carbon');add('Sidepods',sidepods,(0,0,0),'White Carbon');add('Front wing',front_wing,(0,0,0),'Black Carbon');add('Rear wing',rear_wing,(0,0,0),'Black Carbon');add('Halo',halo,(0,0,0),'Black Carbon');add('Cockpit',cockpit,(0,0,0),'Cockpit');add('Front suspension',front_susp,(-68,0,0),'Aluminum');add('Rear suspension',rear_susp,(67,0,0),'Aluminum');add('Battery',battery,(0,0,9),'Battery');add('Rear motor',motor,(0,0,17),'HV Orange');add('Inverter',inverter,(0,0,24),'Cockpit')
for x in (-68,67):
 for y in (-58,58):
  n=('Front' if x<0 else 'Rear')+(' left' if y<0 else ' right')
  add(n+' slick tire',tire,(x,y,16),'Tire');add(n+' rim',rim,(x,y,16),'Aluminum');add(n+' rotor',rotor,(x,y,16),'Brake');add(n+' center lock',centerlock,(x,y+(-8 if y<0 else 8),16),'Red')

# Combined viewing STL.
A=[]
for n,M,t,mat in I:A+=translate(M,*t)
write_stl(f'{OUT}/FORMULA_EV_COMPLETE_ASSEMBLED.stl',A,'FORMULA_EV_COMPLETE_ASSEMBLED')
print('ASSEMBLED',bounds(A),len(A))

# Correct color 3MF assembly.
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
matxml='<m:basematerials id="900">'+''.join(f'<m:base name="{n}" displaycolor="{c}"/>' for n,c in materials)+'</m:basematerials>'
objs=[];items=[]
for oid,(n,M,(x,y,z),mat) in enumerate(I,1):
 V,F=vf(M);vs=''.join(f'<vertex x="{a}" y="{b}" z="{c}"/>' for a,b,c in V);fs=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in F)
 objs.append(f'<object id="{oid}" name="{n}" type="model" pid="900" pindex="{mi[mat]}"><mesh><vertices>{vs}</vertices><triangles>{fs}</triangles></mesh></object>');items.append(f'<item objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 {x} {y} {z}"/>')
model='<?xml version="1.0"?><model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02" requiredextensions="m"><metadata name="Title">Formula EV Prototype</metadata><resources>'+matxml+''.join(objs)+'</resources><build>'+''.join(items)+'</build></model>'
rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="r" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>';ct='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
with zipfile.ZipFile(f'{OUT}/FORMULA_EV_ASSEMBLED_COLOR.3mf','w',zipfile.ZIP_DEFLATED) as z:z.writestr('[Content_Types].xml',ct);z.writestr('_rels/.rels',rels);z.writestr('3D/3dmodel.model',model)

open(f'{OUT}/PRINT_ASSEMBLY_GUIDE.txt','w').write('''FORMULA EV PROTOTYPE — PRINT AND ASSEMBLY GUIDE\n\nA completely new open-wheel electric formula-car study model. Overall assembled envelope: approximately 210 x 153 x 65 mm.\n\nPRINT MATERIALS\nPETG or PLA+ for body, wings, floor, suspension and rims. TPU 95A for slick tires. Transparent or colored PETG may be used for display accents.\n\nSETTINGS\n0.20 mm layer height, 4 walls, 20-25% gyroid infill. Use build-plate supports for wings, halo and suspension. Print the monocoque and floor separately.\n\nASSEMBLY\n1. Glue battery, motor and inverter to the floor/chassis before fitting the monocoque.\n2. Fit sidepods, cockpit and halo.\n3. Install front and rear suspension modules at x=-68 and x=67 mm.\n4. Assemble each wheel: rotor, rim, TPU tire and center-lock nut. Glue only the center-lock nut to the axle tip.\n5. Attach nose, front wing and rear wing last.\n\nThe assembled STL is intended for viewing and static printing. Use separate STLs for functional rotating wheels and clearer multi-material printing. This is an educational scale prototype, not a road-safe design.\n''')
with zipfile.ZipFile(f'{OUT}/FORMULA_EV_ASSEMBLED_COLOR.3mf') as z:assert z.testzip() is None
