import os,sys,math,struct,json
sys.path.insert(0,'work')
import formula_ev as b
from advanced_sedan import box,cyl,tube,beam,loft,translate
OUT='outputs/formula_ev_v2_detailed';os.makedirs(OUT,exist_ok=True)

def merge(*ms):
 r=[]
 for m in ms:r+=m
 return r

# 1 Monocoque: access covers, camera pod, rollover structure, side-impact spars.
monocoque=list(b.monocoque)
for x in (-38,-20,0,20,40):monocoque+=box(x,0,8,1.5,34 if x>-25 else 22,2)
monocoque+=box(-42,0,23,14,7,5)+cyl(-42,0,27,3,5,'z',24)
for s in (-1,1):monocoque+=beam((-18,s*17,20),(38,s*16,19),1.5)

# 2 Nose: pylons, pitot tube, camera/sensor housings.
nose=list(b.nose)
nose+=beam((-104,0,10),(-112,0,10),1.1)+cyl(-112,0,10,1.8,3,'x',16)
for s in (-1,1):nose+=box(-78,s*8,14,7,4,3)+beam((-74,s*8,13),(-68,s*8,9),1.2)

# 3 Floor/diffuser: floor-edge devices, tunnel vanes and vortex generators.
floor=list(b.floor)
for s in (-1,1):
 for x in (-40,-20,0,20,40):floor+=beam((x,s*37,8),(x+8,s*41,11),1.0)
for y in (-28,-18,-8,8,18,28):floor+=box(64,y,10,34,1.5,12)
for s in (-1,1):floor+=box(48,s*35,13,45,2,14)

# 4 Sidepods: more pronounced undercut and radiator detail.
sidepods=list(b.sidepods)
for s in (-1,1):
 # sculptural lower and upper edge rails
 sidepods+=beam((-18,s*22,11),(52,s*17,13),2.0)
 sidepods+=beam((-18,s*40,25),(50,s*28,21),1.7)
 # radiator vane bank behind intake
 for x in (-9,-5,-1,3,7):sidepods+=box(x,s*31,18,1.2,27,13)
 # top cooling louvres
 for x in (20,27,34,41):sidepods+=box(x,s*28,26,4,10,1.3)

# 5 Front wing: four-element cascade, fences, endplate louvers, adjuster rods.
front=[]
for i,(x,z,w,l,t) in enumerate([(-98,5,146,22,2.8),(-92,9,137,19,2.2),(-86,13,124,17,1.9),(-80,17,104,14,1.6)]):
 front+=box(x,0,z,l,w,t)
 for s in (-1,1):front+=beam((x-l/2,s*(w/2-8),z),(x+l/2,s*(w/2-14),z+2),1.0)
for s in (-1,1):
 front+=box(-91,s*74,14,38,3,27)
 for z in (8,14,20):front+=box(-88,s*71,z,18,7,1.2)
 # wheel-wake control vanes
 for y in (50,57,64):front+=box(-83,s*y,15,18,1.5,15)
front+=beam((-93,-7,7),(-70,-7,16),2)+beam((-93,7,7),(-70,7,16),2)

# 6 Fixed rear wing support/mainplane and separate local-space DRS flap.
rear_fixed=[]
rear_fixed+=box(84,0,47,28,118,3.2) # main plane
for s in (-1,1):
 rear_fixed+=box(81,s*61,50,38,3,37)
 # endplate slots/strakes
 for z in (39,47,55,63):rear_fixed+=box(78,s*59,z,20,7,1.2)
 rear_fixed+=beam((61,s*18,24),(80,s*25,45),2.5)+beam((70,s*18,24),(87,s*25,45),2.5)
 # DRS actuator arms
 rear_fixed+=beam((82,s*18,49),(80,s*18,56),1.4)
rear_fixed+=box(77,0,51,8,18,8) # central actuator housing
# DRS flap local around hinge; animation rotates this node.
drs=box(0,0,0,18,108,2.4)
for s in (-1,1):drs+=cyl(-8,s*50,0,2.2,6,'y',20)
# actuator linkage is separate visible item
actuator=cyl(0,0,0,2.2,18,'z',24)+beam((0,0,-8),(7,0,-15),1.5)

# 7 Halo: fairing, top camera and mounting bosses.
halo=list(b.halo)
halo+=box(-8,0,50,14,7,4)+cyl(-8,0,54,2.5,4,'z',24)
for p in [(-10,-17,34),(-10,17,34),(29,0,34)]:halo+=cyl(*p,4,3,'z',24)

# 8 Cockpit: shell + seat, six-point harness, dash display, paddle wheel and pedals.
cockpit=list(b.cockpit)
# harness belts
for s in (-1,1):
 cockpit+=beam((18,s*6,30),(2,s*3,15),1.2)+beam((12,s*7,14),(-2,s*5,11),1.0)
# display and buttons
cockpit+=box(-18,0,29,2.5,17,8)
for y in (-6,-3,0,3,6):cockpit+=cyl(-20,y,29,0.8,1.2,'x',12)
# steering grips/paddles and pedals
cockpit+=beam((-12,-6,28),(-12,6,28),1.3)+box(-10,-7,28,5,1,7)+box(-10,7,28,5,1,7)
cockpit+=box(-34,-5,10,8,4,1.5)+box(-34,5,10,8,4,1.5)

# 9/10 Suspension: existing geometry + rockers, coils, anti-roll links, wheel tethers.
def enhance_susp(M,front=True):
 R=list(M)
 for s in (-1,1):
  R+=beam((8,s*8,30),(18,s*5,25),2.4) # rocker
  # visible inboard spring rings
  for q in range(6):R+=cyl(21+q*1.8,s*4,20-q*.4,2.8,0.9,'x',14)
  R+=beam((0,s*52,20),(12,s*18,28),0.8) # safety tether
 R+=beam((16,-10,23),(16,10,23),1.4) # anti-roll bar
 return R
front_susp=enhance_susp(b.front_susp,True);rear_susp=enhance_susp(b.rear_susp,False)

# 11-14 Wheel system enhanced with sidewall lettering blocks and wheel gun center nut.
tire=list(b.tire)
for k in range(8):
 a=2*math.pi*k/8;tire+=box(15.8*math.cos(a),-6.8,15.8*math.sin(a),3.2,1.2,1.4)
rim=list(b.rim)
for k in range(12):
 a=2*math.pi*k/12;rim+=cyl(8.5*math.cos(a),-5,8.5*math.sin(a),0.6,1.5,'y',12)
rotor=list(b.rotor)
for k in range(12):
 a=2*math.pi*k/12;rotor+=cyl(8*math.cos(a),-1.2,8*math.sin(a),0.55,2.4,'y',10)
centerlock=list(b.centerlock)+box(0,3,0,3,2,9)

# 15-17 Powertrain enhanced.
battery=list(b.battery)
for x in (-30,-10,10,30):
 for y in (-8,8):
  for r in (-5,0,5):battery+=box(x+r,y,7.4,1,10,1)
battery+=box(8,0,10,80,3,2.5)
motor=list(b.motor)
for s in (-1,1):motor+=beam((70,s*9,-10),(45,s*14,-12),2.0)
motor+=box(63,0,14,36,20,5)+cyl(45,0,14,3,5,'x',24)
inverter=list(b.inverter)
for y in (-8,-4,0,4,8):inverter+=box(38,y,6,22,1,2)
inverter+=cyl(26,-10,0,2.4,5,'y',20)+cyl(26,10,0,2.4,5,'y',20)

# 18 Cooling system / ducts, 19 telemetry antennas.
cooling=[]
for s in (-1,1):
 cooling+=box(4,s*31,19,28,3,18)
 for x in (-8,-3,2,7,12):cooling+=box(x,s*31,19,1,25,15)
telemetry=beam((-12,0,48),(-12,0,62),0.8)+beam((38,0,30),(38,0,42),0.7)+cyl(38,0,43,2,2,'z',16)

parts=[
('01_enhanced_monocoque',monocoque,'White Carbon'),('02_sensor_nose_cone',nose,'White Carbon'),('03_venturi_floor_diffuser',floor,'Black Carbon'),('04_sculpted_sidepods_radiators',sidepods,'White Carbon'),('05_four_element_front_wing',front,'Black Carbon'),('06_rear_wing_mainplane',rear_fixed,'Black Carbon'),('07_animated_drs_flap',drs,'White Carbon'),('08_drs_actuator',actuator,'Aluminum'),('09_enhanced_halo',halo,'Black Carbon'),('10_detailed_cockpit',cockpit,'Cockpit'),('11_front_pushrod_suspension',front_susp,'Aluminum'),('12_rear_pushrod_suspension',rear_susp,'Aluminum'),('13_slick_tire',tire,'Tire'),('14_centerlock_rim',rim,'Aluminum'),('15_drilled_brake_rotor',rotor,'Brake'),('16_centerlock_nut',centerlock,'Red'),('17_battery_pack_busbars',battery,'Battery'),('18_motor_gearbox_cooling',motor,'HV Orange'),('19_inverter_connectors',inverter,'Electronics'),('20_radiator_cooling_system',cooling,'Aluminum'),('21_telemetry_antennas',telemetry,'Red')]

materials={'White Carbon':(0.94,0.94,0.91,1),'Black Carbon':(0.025,0.032,0.045,1),'Tire':(0.008,0.008,0.008,1),'Aluminum':(0.62,0.67,0.72,1),'Brake':(0.28,0.31,0.34,1),'Red':(0.78,0.015,0.015,1),'Battery':(0.025,0.28,0.62,1),'HV Orange':(0.95,0.28,0.0,1),'Cockpit':(0.07,0.09,0.12,1),'Electronics':(0.22,0.27,0.32,1)}

# Complete assembly instances: name, mesh, translation, material.
I=[]
def add(n,M,t,mat):I.append((n,M,t,mat))
add('Enhanced monocoque',monocoque,(0,0,0),'White Carbon');add('Sensor nose cone',nose,(0,0,0),'White Carbon');add('Venturi floor and diffuser',floor,(0,0,0),'Black Carbon');add('Sculpted sidepods and radiator ducts',sidepods,(0,0,0),'White Carbon');add('Four-element front wing',front,(0,0,0),'Black Carbon');add('Rear wing mainplane',rear_fixed,(0,0,0),'Black Carbon');add('DRS flap animated',drs,(79,0,58),'White Carbon');add('DRS actuator',actuator,(77,0,51),'Aluminum');add('Enhanced halo',halo,(0,0,0),'Black Carbon');add('Detailed cockpit',cockpit,(0,0,0),'Cockpit');add('Front pushrod suspension',front_susp,(-68,0,0),'Aluminum');add('Rear pushrod suspension',rear_susp,(67,0,0),'Aluminum');add('Battery modules and busbars',battery,(0,0,9),'Battery');add('Motor gearbox and cooling',motor,(0,0,17),'HV Orange');add('Inverter and HV connectors',inverter,(0,0,24),'Electronics');add('Radiator cooling system',cooling,(0,0,0),'Aluminum');add('Telemetry antennas',telemetry,(0,0,0),'Red')
for x in (-68,67):
 for y in (-58,58):
  n=('Front' if x<0 else 'Rear')+(' left' if y<0 else ' right')
  add(n+' slick tire',tire,(x,y,16),'Tire');add(n+' detailed rim',rim,(x,y,16),'Aluminum');add(n+' drilled brake rotor',rotor,(x,y,16),'Brake');add(n+' center lock',centerlock,(x,y+(-8 if y<0 else 8),16),'Red')

# GLB exporter with optional DRS animation.
def indexed(M):
 d={};V=[];F=[]
 for tri in M:
  for p in tri:
   p=tuple(float(q) for q in p)
   if p not in d:d[p]=len(V);V.append(p)
   F.append(d[p])
 return V,F

def glb(path,instances,animate=False):
 binbuf=bytearray();views=[];acc=[];meshes=[];nodes=[]
 def align():
  while len(binbuf)%4:binbuf.append(0)
 def view(data,target=None):
  align();off=len(binbuf);binbuf.extend(data);q={'buffer':0,'byteOffset':off,'byteLength':len(data)}
  if target:q['target']=target
  views.append(q);return len(views)-1
 mats=[];mi={}
 for n,c in materials.items():mi[n]=len(mats);mats.append({'name':n,'pbrMetallicRoughness':{'baseColorFactor':list(c),'metallicFactor':.72 if n in ('Aluminum','Brake') else .04,'roughnessFactor':.24 if n in ('White Carbon','Aluminum') else .55},'doubleSided':True})
 drs_node=None
 for name,M,tr,mat in instances:
  V,F=indexed(M);pv=view(b''.join(struct.pack('<3f',*p) for p in V),34962);iv=view(b''.join(struct.pack('<I',i) for i in F),34963)
  mins=[min(p[k] for p in V) for k in range(3)];maxs=[max(p[k] for p in V) for k in range(3)]
  pa=len(acc);acc.append({'bufferView':pv,'componentType':5126,'count':len(V),'type':'VEC3','min':mins,'max':maxs});ia=len(acc);acc.append({'bufferView':iv,'componentType':5125,'count':len(F),'type':'SCALAR','min':[min(F)],'max':[max(F)]})
  meshes.append({'name':name,'primitives':[{'attributes':{'POSITION':pa},'indices':ia,'material':mi[mat]}]});nodes.append({'name':name,'mesh':len(meshes)-1,'translation':list(tr)})
  if 'DRS flap' in name:drs_node=len(nodes) # +1 after root
 root={'name':'FORMULA EV V2 ASSEMBLY','rotation':[-.7071068,0,0,.7071068],'children':list(range(1,len(nodes)+1))}
 doc={'asset':{'version':'2.0','generator':'Formula EV V2 detailed exporter'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[root]+nodes,'meshes':meshes,'materials':mats,'buffers':[{'byteLength':0}],'bufferViews':views,'accessors':acc}
 if animate and drs_node:
  times=[0.,1.5,3.0];ang=[0,math.radians(28),0];rots=[]
  for a in ang:rots.extend([0,math.sin(a/2),0,math.cos(a/2)])
  tv=view(struct.pack('<3f',*times));rv=view(struct.pack('<12f',*rots));ta=len(acc);acc.append({'bufferView':tv,'componentType':5126,'count':3,'type':'SCALAR','min':[0],'max':[3]});ra=len(acc);acc.append({'bufferView':rv,'componentType':5126,'count':3,'type':'VEC4'})
  doc['animations']=[{'name':'DRS OPEN CLOSE','samplers':[{'input':ta,'output':ra,'interpolation':'LINEAR'}],'channels':[{'sampler':0,'target':{'node':drs_node,'path':'rotation'}}]}]
 doc['buffers'][0]['byteLength']=len(binbuf);js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((4-len(js)%4)%4)
 while len(binbuf)%4:binbuf.append(0)
 bb=bytes(binbuf);total=12+8+len(js)+8+len(bb)
 with open(path,'wb') as o:o.write(struct.pack('<4sII',b'glTF',2,total));o.write(struct.pack('<I4s',len(js),b'JSON'));o.write(js);o.write(struct.pack('<I4s',len(bb),b'BIN\0'));o.write(bb)

# Complete animated car.
glb(f'{OUT}/FORMULA_EV_V2_COMPLETE_ANIMATED_DRS.glb',I,True)
# Individual major part/system GLBs at origin.
for n,M,mat in parts:glb(f'{OUT}/{n}.glb',[(n,M,(0,0,0),mat)],False)
open(f'{OUT}/VIEWER_GUIDE.txt','w').write('''FORMULA EV V2 GLB VIEWER GUIDE\n\nOpen FORMULA_EV_V2_COMPLETE_ANIMATED_DRS.glb in Blender for the best inspection. The model has separately named components. Select and hide body parts to inspect suspension, battery, motor and cooling systems.\n\nDRS ANIMATION\nIn Blender, switch to the Animation workspace and press Play. The rear flap opens to 28 degrees and closes over a 3-second loop. If a viewer does not support glTF animations, the flap remains visible as a separate selectable object.\n\nINDIVIDUAL FILES\nThe numbered GLBs contain each major system by itself, centered at the origin for easy rotation and inspection. Wheel component files are intended to be reused four times.\n''')
# Validate headers.
for fn in os.listdir(OUT):
 if fn.endswith('.glb'):
  data=open(OUT+'/'+fn,'rb').read(12);magic,ver,total=struct.unpack('<4sII',data);assert magic==b'glTF' and ver==2
print('complete instances',len(I),'individual files',len(parts))
