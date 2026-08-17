import os,sys,math,struct,json,zipfile
sys.path.insert(0,'work')
import formula_ev_v4_active_front as v4
from advanced_sedan import box,cyl,beam
OUT='outputs/formula_ev_v5_all_active_flaps';os.makedirs(OUT,exist_ok=True)

# Fixed load-bearing mainplane, pylons, fences and endplates.
mainplane=box(-98,0,5,22,146,2.8)
for s in (-1,1):
 mainplane+=box(-91,s*74,14,38,3,27)
 mainplane+=beam((-98-11,s*65,5),(-98+11,s*59,7),1.1)
 for z in (8,14,20):mainplane+=box(-88,s*71,z,18,7,1.2)
 for y in (50,57,64):mainplane+=box(-83,s*y,15,18,1.5,15)
mainplane+=beam((-93,-7,7),(-70,-7,16),2)+beam((-93,7,7),(-70,7,16),2)

# Local flap mesh; level 1 is widest/lowest, level 3 narrowest/highest.
def flap(side,level):
 specs={1:(18,61,1.9),2:(16,55,1.7),3:(14,47,1.5)}
 chord,span,t=specs[level];cy=side*(span/2+3)
 M=box(0,cy,0,chord,span,t)
 # three hinge barrels and torsion/stiffener beam
 for yy in (side*3,side*(span/2+3),side*(span+3)):M+=cyl(-chord/2+1,yy,0,1.8,4.5,'y',20)
 M+=beam((-chord/2+3,side*3,1),(-chord/2+3,side*(span+3),1),.9)
 # actuator horn and load sensor boss
 M+=beam((-2,side*8,0),(4,side*8,-5-level),1.1)
 M+=cyl(0,side*(span*.72),1.2,1.4,2,'z',16)
 return M
flaps={(s,l):flap(s,l) for s in (-1,1) for l in (1,2,3)}
# Central hydraulic/electric actuator and six linkage rods.
actuator=box(0,0,0,14,18,9)+cyl(0,0,6,3.2,8,'z',28)
for s in (-1,1):
 for level,(x,z) in enumerate([(-92,9),(-86,13),(-80,17)],1):
  actuator+=beam((2,s*(3+level*2),0),(x+82,s*(8+level*2),z-18),1.05)

materials=dict(v4.materials)
# Remove V4 front system and insert V5 seven-piece active wing.
remove_names={'Three-element front-wing base','Left active front-wing flap','Right active front-wing flap','Front active-aero actuator'}
I=[q for q in v4.I if q[0] not in remove_names]
I.append(('Fixed front-wing mainplane',mainplane,(0,0,0),'Black Carbon'))
positions={1:(-92,9),2:(-86,13),3:(-80,17)}
for s in (-1,1):
 for level in (1,2,3):
  x,z=positions[level];I.append((f'{"Left" if s<0 else "Right"} active flap level {level}',flaps[(s,level)],(x,0,z),'White Carbon'))
I.append(('Six-channel front-wing actuator',actuator,(-82,0,18),'Aluminum'))

# Updated list of every individual system/part.
remove_files={'05_three_element_front_wing_base','38_left_active_front_flap','39_right_active_front_flap','40_front_active_aero_actuator'}
individual=[q for q in v4.individual if q[0] not in remove_files]
individual.append(('05_fixed_front_wing_mainplane',mainplane,'Black Carbon'))
num=38
for s in (-1,1):
 for level in (1,2,3):
  individual.append((f'{num:02d}_{"left" if s<0 else "right"}_active_flap_level_{level}',flaps[(s,level)],'White Carbon'));num+=1
individual.append(('44_six_channel_front_wing_actuator',actuator,'Aluminum'))

# GLB exporter with rear DRS and six front-flap animation channels.
def indexed(M):
 d={};V=[];F=[]
 for tri in M:
  for p in tri:
   p=tuple(float(q) for q in p)
   if p not in d:d[p]=len(V);V.append(p)
   F.append(d[p])
 return V,F

def glb(path,instances,animate=False):
 buf=bytearray();views=[];acc=[];meshes=[];nodes=[]
 def align():
  while len(buf)%4:buf.append(0)
 def view(data,target=None):
  align();off=len(buf);buf.extend(data);q={'buffer':0,'byteOffset':off,'byteLength':len(data)}
  if target:q['target']=target
  views.append(q);return len(views)-1
 mats=[];mi={}
 for n,c in materials.items():
  mi[n]=len(mats);mats.append({'name':n,'pbrMetallicRoughness':{'baseColorFactor':list(c),'metallicFactor':.8 if n in ('Aluminum','Brake','Titanium') else .03,'roughnessFactor':.23 if n in ('White Carbon','Aluminum','Titanium') else .58},'doubleSided':True})
 targets={'front':[]}
 for name,M,tr,mat in instances:
  V,F=indexed(M);pv=view(b''.join(struct.pack('<3f',*p) for p in V),34962);iv=view(b''.join(struct.pack('<I',i) for i in F),34963)
  mins=[min(p[k] for p in V) for k in range(3)];maxs=[max(p[k] for p in V) for k in range(3)]
  pa=len(acc);acc.append({'bufferView':pv,'componentType':5126,'count':len(V),'type':'VEC3','min':mins,'max':maxs});ia=len(acc);acc.append({'bufferView':iv,'componentType':5125,'count':len(F),'type':'SCALAR','min':[min(F)],'max':[max(F)]})
  meshes.append({'name':name,'primitives':[{'attributes':{'POSITION':pa},'indices':ia,'material':mi[mat]}]});nodes.append({'name':name,'mesh':len(meshes)-1,'translation':list(tr)});idx=len(nodes)
  if 'DRS flap' in name:targets['rear']=idx
  if 'active flap level' in name:
   level=int(name[-1]);targets['front'].append((idx,level))
 root={'name':'FORMULA EV V5 ALL ACTIVE FRONT FLAPS','rotation':[-.7071068,0,0,.7071068],'children':list(range(1,len(nodes)+1))}
 doc={'asset':{'version':'2.0','generator':'Formula EV V5 all-flap exporter'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[root]+nodes,'meshes':meshes,'materials':mats,'buffers':[{'byteLength':0}],'bufferViews':views,'accessors':acc}
 if animate:
  times=[0.,1.5,3.];tv=view(struct.pack('<3f',*times));ta=len(acc);acc.append({'bufferView':tv,'componentType':5126,'count':3,'type':'SCALAR','min':[0],'max':[3]});animations=[]
  if 'rear' in targets:
   ro=[]
   for a in (0,math.radians(28),0):ro += [0,math.sin(a/2),0,math.cos(a/2)]
   rv=view(struct.pack('<12f',*ro));ra=len(acc);acc.append({'bufferView':rv,'componentType':5126,'count':3,'type':'VEC4'});animations.append({'name':'REAR DRS OPEN CLOSE','samplers':[{'input':ta,'output':ra,'interpolation':'LINEAR'}],'channels':[{'sampler':0,'target':{'node':targets['rear'],'path':'rotation'}}]})
  # Each flap level has progressive motion: 7, 11, 16 degrees.
  samplers=[];channels=[]
  angles={1:-7,2:-11,3:-16}
  for idx,level in targets['front']:
   vals=[]
   for a in (0,math.radians(angles[level]),0):vals += [0,math.sin(a/2),0,math.cos(a/2)]
   vv=view(struct.pack('<12f',*vals));aa=len(acc);acc.append({'bufferView':vv,'componentType':5126,'count':3,'type':'VEC4'});samplers.append({'input':ta,'output':aa,'interpolation':'LINEAR'});channels.append({'sampler':len(samplers)-1,'target':{'node':idx,'path':'rotation'}})
  animations.append({'name':'ALL SIX FRONT FLAPS OPEN CLOSE','samplers':samplers,'channels':channels});doc['animations']=animations
 doc['buffers'][0]['byteLength']=len(buf);js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((4-len(js)%4)%4)
 while len(buf)%4:buf.append(0)
 bb=bytes(buf);total=12+8+len(js)+8+len(bb)
 with open(path,'wb') as o:o.write(struct.pack('<4sII',b'glTF',2,total));o.write(struct.pack('<I4s',len(js),b'JSON'));o.write(js);o.write(struct.pack('<I4s',len(bb),b'BIN\0'));o.write(bb)

# Whole car, active front system, and every individual GLB.
glb(f'{OUT}/FORMULA_EV_V5_COMPLETE_ALL_ACTIVE_FLAPS.glb',I,True)
frontI=[('Fixed front-wing mainplane',mainplane,(0,0,0),'Black Carbon')]
for s in (-1,1):
 for level in (1,2,3):
  x,z=positions[level];frontI.append((f'{"Left" if s<0 else "Right"} active flap level {level}',flaps[(s,level)],(x,0,z),'White Carbon'))
frontI.append(('Six-channel front-wing actuator',actuator,(-82,0,18),'Aluminum'))
glb(f'{OUT}/FORMULA_EV_V5_COMPLETE_ACTIVE_FRONT_WING.glb',frontI,True)
for n,M,mat in individual:glb(f'{OUT}/{n}.glb',[(n,M,(0,0,0),mat)])
open(f'{OUT}/ANIMATION_GUIDE.txt','w').write('''FORMULA EV V5 — ALL FRONT FLAPS ACTIVE\n\nThe front wing now contains one fixed structural mainplane and six moving flaps: three left and three right.\n\nAnimation ALL SIX FRONT FLAPS OPEN CLOSE:\n- Level 1 flaps rotate 7 degrees.\n- Level 2 flaps rotate 11 degrees.\n- Level 3 flaps rotate 16 degrees.\n\nThe rear DRS remains a separate 28-degree animation. In Blender, import the complete GLB, open the Animation workspace, choose an action and press Play.\n\nThis is an educational active-aero concept, not a regulation-compliant 2022-2025 Formula 1 system.\n''')
for fn in os.listdir(OUT):
 if fn.endswith('.glb'):
  m,v,t=struct.unpack('<4sII',open(OUT+'/'+fn,'rb').read(12));assert m==b'glTF' and v==2
with zipfile.ZipFile(f'{OUT}/FORMULA_EV_V5_ALL_GLB_FILES.zip','w',zipfile.ZIP_DEFLATED) as z:
 for fn in os.listdir(OUT):
  if fn.endswith('.glb') or fn.endswith('.txt'):z.write(OUT+'/'+fn,fn)
print('whole instances',len(I),'individual',len(individual),'moving front flaps',6)
