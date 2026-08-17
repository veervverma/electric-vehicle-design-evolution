import os,sys,math,struct,json,zipfile
sys.path.insert(0,'work')
import formula_ev_v3_floor as v3
from advanced_sedan import box,cyl,beam
OUT='outputs/formula_ev_v4_dual_active_aero';os.makedirs(OUT,exist_ok=True)

# Fixed front-wing structure: three full-span elements, endplates, fences and pylons.
front_fixed=[]
for x,z,w,l,t in [(-98,5,146,22,2.8),(-92,9,137,19,2.2),(-86,13,124,17,1.9)]:
 front_fixed+=box(x,0,z,l,w,t)
 for s in (-1,1):front_fixed+=beam((x-l/2,s*(w/2-8),z),(x+l/2,s*(w/2-14),z+2),1.0)
for s in (-1,1):
 front_fixed+=box(-91,s*74,14,38,3,27)
 for z in (8,14,20):front_fixed+=box(-88,s*71,z,18,7,1.2)
 for y in (50,57,64):front_fixed+=box(-83,s*y,15,18,1.5,15)
front_fixed+=beam((-93,-7,7),(-70,-7,16),2)+beam((-93,7,7),(-70,7,16),2)
# Central active-aero actuator housing and sensor pod.
front_actuator=box(0,0,0,13,18,8)+cyl(0,0,5,3,7,'z',28)
front_actuator+=beam((0,-7,0),(7,-27,0),1.4)+beam((0,7,0),(7,27,0),1.4)
# Left/right upper flaps in local hinge coordinates. Each is individually selectable.
def active_flap(s):
 M=box(0,s*27,0,15,50,1.8)
 # hinge barrels and spanwise stiffener
 for y in (s*5,s*26,s*49):M+=cyl(-7,y,0,2.0,5,'y',22)
 M+=beam((-5,s*5,1),(-5,s*49,1),1.0)
 # actuator horn
 M+=beam((-4,s*9,0),(3,s*9,-6),1.2)
 return M
left_flap=active_flap(-1);right_flap=active_flap(1)

# Materials inherited from V3.
materials=dict(v3.materials)

# Replace V3 fixed front wing instance with V4 fixed and active components.
I=[]
for n,M,t,mat in v3.I:
 if n!='Four-element front wing':I.append((n,M,t,mat))
I += [
 ('Three-element front-wing base',front_fixed,(0,0,0),'Black Carbon'),
 ('Left active front-wing flap',left_flap,(-80,0,17),'White Carbon'),
 ('Right active front-wing flap',right_flap,(-80,0,17),'White Carbon'),
 ('Front active-aero actuator',front_actuator,(-82,0,18),'Aluminum')]

# Updated individual parts: replace old front wing and add each active-aero part.
individual=[]
for n,M,mat in v3.all_individual:
 if n!='05_four_element_front_wing':individual.append((n,M,mat))
individual += [
 ('05_three_element_front_wing_base',front_fixed,'Black Carbon'),
 ('38_left_active_front_flap',left_flap,'White Carbon'),
 ('39_right_active_front_flap',right_flap,'White Carbon'),
 ('40_front_active_aero_actuator',front_actuator,'Aluminum')]

# GLB exporter with two animation tracks: rear DRS and front active aero.
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
 for n,c in materials.items():
  mi[n]=len(mats);mats.append({'name':n,'pbrMetallicRoughness':{'baseColorFactor':list(c),'metallicFactor':.8 if n in ('Aluminum','Brake','Titanium') else .03,'roughnessFactor':.23 if n in ('White Carbon','Aluminum','Titanium') else .58},'doubleSided':True})
 targets={}
 for name,M,tr,mat in instances:
  V,F=indexed(M);pv=view(b''.join(struct.pack('<3f',*p) for p in V),34962);iv=view(b''.join(struct.pack('<I',i) for i in F),34963)
  mins=[min(p[k] for p in V) for k in range(3)];maxs=[max(p[k] for p in V) for k in range(3)]
  pa=len(acc);acc.append({'bufferView':pv,'componentType':5126,'count':len(V),'type':'VEC3','min':mins,'max':maxs});ia=len(acc);acc.append({'bufferView':iv,'componentType':5125,'count':len(F),'type':'SCALAR','min':[min(F)],'max':[max(F)]})
  meshes.append({'name':name,'primitives':[{'attributes':{'POSITION':pa},'indices':ia,'material':mi[mat]}]});nodes.append({'name':name,'mesh':len(meshes)-1,'translation':list(tr)})
  idx=len(nodes)
  if 'DRS flap' in name:targets['rear']=idx
  if 'Left active front-wing' in name:targets['front_l']=idx
  if 'Right active front-wing' in name:targets['front_r']=idx
 root={'name':'FORMULA EV V4 DUAL ACTIVE AERO','rotation':[-.7071068,0,0,.7071068],'children':list(range(1,len(nodes)+1))}
 doc={'asset':{'version':'2.0','generator':'Formula EV V4 dual active aero exporter'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[root]+nodes,'meshes':meshes,'materials':mats,'buffers':[{'byteLength':0}],'bufferViews':views,'accessors':acc}
 if animate:
  times=[0.,1.5,3.0];tv=view(struct.pack('<3f',*times));ta=len(acc);acc.append({'bufferView':tv,'componentType':5126,'count':3,'type':'SCALAR','min':[0],'max':[3]})
  animations=[]
  # Rear DRS: +28 degrees around local Y.
  if 'rear' in targets:
   ro=[]
   for a in (0,math.radians(28),0):ro += [0,math.sin(a/2),0,math.cos(a/2)]
   rv=view(struct.pack('<12f',*ro));ra=len(acc);acc.append({'bufferView':rv,'componentType':5126,'count':3,'type':'VEC4'})
   animations.append({'name':'REAR DRS OPEN CLOSE','samplers':[{'input':ta,'output':ra,'interpolation':'LINEAR'}],'channels':[{'sampler':0,'target':{'node':targets['rear'],'path':'rotation'}}]})
  # Front active aero: both flaps reduce incidence by 14 degrees.
  fro=[]
  for a in (0,math.radians(-14),0):fro += [0,math.sin(a/2),0,math.cos(a/2)]
  fv=view(struct.pack('<12f',*fro));fa=len(acc);acc.append({'bufferView':fv,'componentType':5126,'count':3,'type':'VEC4'})
  chans=[]
  for key in ('front_l','front_r'):
   if key in targets:chans.append({'sampler':0,'target':{'node':targets[key],'path':'rotation'}})
  animations.append({'name':'FRONT ACTIVE AERO LOW DRAG','samplers':[{'input':ta,'output':fa,'interpolation':'LINEAR'}],'channels':chans})
  doc['animations']=animations
 doc['buffers'][0]['byteLength']=len(binbuf);js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((4-len(js)%4)%4)
 while len(binbuf)%4:binbuf.append(0)
 bb=bytes(binbuf);total=12+8+len(js)+8+len(bb)
 with open(path,'wb') as o:o.write(struct.pack('<4sII',b'glTF',2,total));o.write(struct.pack('<I4s',len(js),b'JSON'));o.write(js);o.write(struct.pack('<I4s',len(bb),b'BIN\0'));o.write(bb)

# Complete dual-active-aero car and individual GLBs.
glb(f'{OUT}/FORMULA_EV_V4_COMPLETE_DUAL_ACTIVE_AERO.glb',I,True)
for n,M,mat in individual:glb(f'{OUT}/{n}.glb',[(n,M,(0,0,0),mat)],False)
# Dedicated assembled front active-aero system file, with animation.
frontI=[('Three-element front-wing base',front_fixed,(0,0,0),'Black Carbon'),('Left active front-wing flap',left_flap,(-80,0,17),'White Carbon'),('Right active front-wing flap',right_flap,(-80,0,17),'White Carbon'),('Front active-aero actuator',front_actuator,(-82,0,18),'Aluminum')]
glb(f'{OUT}/FORMULA_EV_V4_FRONT_ACTIVE_AERO_SYSTEM.glb',frontI,True)

open(f'{OUT}/ACTIVE_AERO_GUIDE.txt','w').write('''FORMULA EV V4 — DUAL ACTIVE AERO\n\nThe complete GLB contains two independent glTF animations:\n1. REAR DRS OPEN CLOSE: rear flap rotates +28 degrees.\n2. FRONT ACTIVE AERO LOW DRAG: left and right front flaps rotate -14 degrees together.\n\nIn Blender, import the GLB, open the Animation workspace, select an animation/action and press Play. Some basic GLB viewers display the components but do not play multiple animation tracks.\n\nThe front active-aero design is an educational concept. Current 2022-2025 Formula 1 regulations do not use this exact active front-wing arrangement.\n\nAll major car, underfloor and active-aero systems are provided as individual numbered GLBs.\n''')
# Validate and zip.
for fn in os.listdir(OUT):
 if fn.endswith('.glb'):
  magic,ver,total=struct.unpack('<4sII',open(OUT+'/'+fn,'rb').read(12));assert magic==b'glTF' and ver==2
with zipfile.ZipFile(f'{OUT}/FORMULA_EV_V4_ALL_GLB_FILES.zip','w',zipfile.ZIP_DEFLATED) as z:
 for fn in os.listdir(OUT):
  if fn.endswith('.glb') or fn.endswith('.txt'):z.write(OUT+'/'+fn,fn)
print('whole instances',len(I),'individual',len(individual))
