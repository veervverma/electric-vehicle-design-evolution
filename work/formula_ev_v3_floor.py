import os,sys,math,struct,json,zipfile
sys.path.insert(0,'work')
import formula_ev_v2_glb as v2
from advanced_sedan import box,cyl,tube,beam,translate
OUT='outputs/formula_ev_v3_2022_2025_floor';os.makedirs(OUT,exist_ok=True)

def wedge(x0,x1,y0,y1,z0,z1,t=1.4):
 # Closed thin sloped plate.
 v=[(x0,y0,z0),(x0,y1,z0),(x1,y1,z1),(x1,y0,z1),(x0,y0,z0+t),(x0,y1,z0+t),(x1,y1,z1+t),(x1,y0,z1+t)]
 f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
 return [(v[a],v[b],v[c]) for a,b,c in f]

def curved_rail(points,r=1.2):
 M=[]
 for a,b in zip(points[:-1],points[1:]):M+=beam(a,b,r,14)
 return M

# A: structural upper floor / floor-body planform.
upper_floor=box(4,0,7,142,72,3)
# tapered forward floor shoulders
upper_floor+=wedge(-70,-48,-25,-10,6,7,2)+wedge(-70,-48,10,25,6,7,2)
for s in (-1,1):upper_floor+=box(8,s*36.5,10,138,2.4,9)

# B/C: independent left and right Venturi tunnel lower surfaces.
def tunnel(s):
 y0,y1=(7,33) if s>0 else (-33,-7)
 M=[]
 # 2022-type inlet ramp down to throat.
 M+=wedge(-55,-32,y0,y1,6.0,2.2,1.4)
 # long 2023/24 narrow throat.
 M+=wedge(-32,30,y0,y1,2.2,2.5,1.4)
 # 2025-inspired progressive expansion into diffuser.
 M+=wedge(30,48,y0,y1,2.5,5.5,1.4)
 M+=wedge(48,68,y0,y1,5.5,12.5,1.4)
 M+=wedge(68,82,y0,y1,12.5,19.0,1.4)
 # inner tunnel roof rail and outer sealing rail.
 M+=curved_rail([(-55,s*abs(y0),7),(-32,s*abs(y0),3.5),(30,s*abs(y0),3.8),(68,s*abs(y0),14)],1.1)
 return M
left_tunnel=tunnel(-1);right_tunnel=tunnel(1)

# D/E: four front floor fences on each side; progressive curvature.
def fences(s):
 M=[]
 ys=[8,15,23,31]
 for i,y in enumerate(ys):
  y*=s
  pts=[(-56,y,7),(-47,y+s*(i*1.2),11),(-34,y+s*(3+i),8),(-25,y+s*(4+i),5)]
  M+=curved_rail(pts,1.25 if i==3 else 1.0)
  # fence vertical web approximated with ribs
  for q in range(4):
   t=q/3;x=-55+q*9;M+=beam((x,y,5),(x,y,12-i*.6),.75,10)
 return M
left_fences=fences(-1);right_fences=fences(1)

# F/G: floor-edge wings with 2022 curl, 2023 cut-in and 2025 vortex-generator row.
def edge_wing(s):
 M=[];y=s*38
 # raised front ramp and single curl.
 M+=curved_rail([(-48,y,8),(-38,y,13),(-26,y,9),(-10,y,12),(8,y,9),(30,y,10),(52,y,12)],1.7)
 # serrated vortex generators along edge.
 for i,x in enumerate((-18,-7,4,15,26,37,48)):
  M+=beam((x,y,9),(x+6,y+s*(4+(i%2)*2),14),1.0)
 # rear cut-in wing approaching tire gap.
 M+=wedge(44,70,s*34,s*42 if s>0 else s*42,10,15,1.5) if s>0 else wedge(44,70,s*42,s*34,10,15,1.5)
 return M
left_edge=edge_wing(-1);right_edge=edge_wing(1)

# H: central FIA-style plank and inspection holes/skid mounting features.
plank=box(2,0,0.7,132,13,2.4)
for x in (-45,-10,25,57):plank+=tube(x,0,-.6,3.2,1.8,2.5,'z',24)
# I: separate titanium skid set.
skids=[]
for x,l in [(-48,16),(-18,18),(15,18),(48,16)]:skids+=box(x,0,-.7,l,9,1.5)

# J: bib/tea-tray and stay.
bib=wedge(-70,-52,-16,16,4.5,6.5,2.0)+box(-63,0,8,22,3,8)

# K/L: left/right diffuser shells with a narrowed 2025-like boat tail.
def diffuser(s):
 y0,y1=(7,35) if s>0 else (-35,-7)
 M=wedge(34,82,y0,y1,3,20,1.5)
 # outer wall and rear tire-squirt fence
 M+=curved_rail([(34,s*35,5),(55,s*35,10),(82,s*34,22)],1.4)
 M+=wedge(58,81,s*31,s*38 if s>0 else s*38,11,20,1.5) if s>0 else wedge(58,81,s*38,s*31,11,20,1.5)
 return M
left_diff=diffuser(-1);right_diff=diffuser(1)
# M: diffuser strakes and boat-tail center keel.
strakes=[]
for y in (-31,-21,-11,11,21,31):strakes+=wedge(38,82,y-1,y+1,4,21,2)
boat_tail=wedge(35,82,-7,7,4,17,2)+curved_rail([(35,-7,6),(60,-5,11),(82,-3,19)],1.0)+curved_rail([(35,7,6),(60,5,11),(82,3,19)],1.0)

# N/O: rear-wheel wake fences and floor stays.
rear_wake=[]
for s in (-1,1):
 for x in (52,60,68):rear_wake+=beam((x,s*37,12),(x+5,s*42,18),1.0)
floor_stays=beam((20,-38,10),(20,-25,23),1.2)+beam((20,38,10),(20,25,23),1.2)+beam((55,-37,13),(55,-24,22),1.2)+beam((55,37,13),(55,24,22),1.2)

floor_parts=[
('22_upper_floor_body',upper_floor,'Black Carbon'),('23_left_venturi_tunnel',left_tunnel,'Underfloor'),('24_right_venturi_tunnel',right_tunnel,'Underfloor'),('25_left_inlet_fences_x4',left_fences,'Red'),('26_right_inlet_fences_x4',right_fences,'Red'),('27_left_floor_edge_wing',left_edge,'Black Carbon'),('28_right_floor_edge_wing',right_edge,'Black Carbon'),('29_central_plank',plank,'Plank'),('30_titanium_skid_set',skids,'Titanium'),('31_bib_tea_tray',bib,'Black Carbon'),('32_left_diffuser',left_diff,'Underfloor'),('33_right_diffuser',right_diff,'Underfloor'),('34_diffuser_strakes',strakes,'Black Carbon'),('35_boat_tail_keel',boat_tail,'Underfloor'),('36_rear_wake_fences',rear_wake,'Red'),('37_floor_stays',floor_stays,'Titanium')]

materials=dict(v2.materials)
materials.update({'Underfloor':(0.10,0.12,0.15,1),'Plank':(0.58,0.42,0.23,1),'Titanium':(0.42,0.46,0.50,1)})

# Whole-car instances: replace prior floor with detailed multi-part floor.
I=[]
for n,M,t,mat in v2.I:
 if n!='Venturi floor and diffuser':I.append((n,M,t,mat))
for n,M,mat in floor_parts:I.append((n,M,(0,0,0),mat))

# Reusable GLB exporter, preserving V2 DRS animation.
def indexed(M):
 d={};V=[];F=[]
 for tri in M:
  for p in tri:
   p=tuple(float(q) for q in p)
   if p not in d:d[p]=len(V);V.append(p)
   F.append(d[p])
 return V,F

def glb(path,instances,animate=False,explode=False):
 binbuf=bytearray();views=[];acc=[];meshes=[];nodes=[]
 def align():
  while len(binbuf)%4:binbuf.append(0)
 def view(data,target=None):
  align();off=len(binbuf);binbuf.extend(data);q={'buffer':0,'byteOffset':off,'byteLength':len(data)}
  if target:q['target']=target
  views.append(q);return len(views)-1
 mats=[];mi={}
 for n,c in materials.items():mi[n]=len(mats);mats.append({'name':n,'pbrMetallicRoughness':{'baseColorFactor':list(c),'metallicFactor':.8 if n in ('Aluminum','Brake','Titanium') else .03,'roughnessFactor':.23 if n in ('White Carbon','Aluminum','Titanium') else .58},'doubleSided':True})
 drs_node=None
 for name,M,tr,mat in instances:
  V,F=indexed(M);pv=view(b''.join(struct.pack('<3f',*p) for p in V),34962);iv=view(b''.join(struct.pack('<I',i) for i in F),34963)
  mins=[min(p[k] for p in V) for k in range(3)];maxs=[max(p[k] for p in V) for k in range(3)]
  pa=len(acc);acc.append({'bufferView':pv,'componentType':5126,'count':len(V),'type':'VEC3','min':mins,'max':maxs});ia=len(acc);acc.append({'bufferView':iv,'componentType':5125,'count':len(F),'type':'SCALAR','min':[min(F)],'max':[max(F)]})
  meshes.append({'name':name,'primitives':[{'attributes':{'POSITION':pa},'indices':ia,'material':mi[mat]}]})
  x,y,z=tr
  if explode:
   # Spread floor systems vertically and laterally for technical inspection.
   if 'upper_floor' in name:z+=28
   elif 'venturi' in name:z-=14
   elif 'fences' in name:z+=15
   elif 'edge_wing' in name:y+=-22 if 'left' in name else 22
   elif 'plank' in name:z-=27
   elif 'skid' in name:z-=37
   elif 'bib' in name:x-=18;z+=8
   elif 'diffuser' in name and 'strakes' not in name:z-=17
   elif 'strakes' in name:z-=30
   elif 'boat_tail' in name:z-=24
   elif 'wake' in name:y+=-18 if 'left' in name else 18
  nodes.append({'name':name,'mesh':len(meshes)-1,'translation':[x,y,z]})
  if 'DRS flap' in name:drs_node=len(nodes)
 root={'name':'FORMULA EV V3 2022-2025 FLOOR STUDY','rotation':[-.7071068,0,0,.7071068],'children':list(range(1,len(nodes)+1))}
 doc={'asset':{'version':'2.0','generator':'Formula EV V3 floor-study exporter'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[root]+nodes,'meshes':meshes,'materials':mats,'buffers':[{'byteLength':0}],'bufferViews':views,'accessors':acc}
 if animate and drs_node:
  times=[0.,1.5,3.];angles=[0,math.radians(28),0];rots=[]
  for a in angles:rots += [0,math.sin(a/2),0,math.cos(a/2)]
  tv=view(struct.pack('<3f',*times));rv=view(struct.pack('<12f',*rots));ta=len(acc);acc.append({'bufferView':tv,'componentType':5126,'count':3,'type':'SCALAR','min':[0],'max':[3]});ra=len(acc);acc.append({'bufferView':rv,'componentType':5126,'count':3,'type':'VEC4'});doc['animations']=[{'name':'DRS OPEN CLOSE','samplers':[{'input':ta,'output':ra,'interpolation':'LINEAR'}],'channels':[{'sampler':0,'target':{'node':drs_node,'path':'rotation'}}]}]
 doc['buffers'][0]['byteLength']=len(binbuf);js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((4-len(js)%4)%4)
 while len(binbuf)%4:binbuf.append(0)
 bb=bytes(binbuf);total=12+8+len(js)+8+len(bb)
 with open(path,'wb') as o:o.write(struct.pack('<4sII',b'glTF',2,total));o.write(struct.pack('<I4s',len(js),b'JSON'));o.write(js);o.write(struct.pack('<I4s',len(bb),b'BIN\0'));o.write(bb)

# Whole car, complete floor assembly, and exploded floor study.
glb(f'{OUT}/FORMULA_EV_V3_COMPLETE_2022_2025_FLOOR.glb',I,True)
floorI=[(n,M,(0,0,0),mat) for n,M,mat in floor_parts]
glb(f'{OUT}/FORMULA_EV_V3_COMPLETE_UNDERFLOOR.glb',floorI,False)
glb(f'{OUT}/FORMULA_EV_V3_EXPLODED_UNDERFLOOR.glb',floorI,False,True)
# Every V2 major component except obsolete floor, plus every V3 floor component.
all_individual=[p for p in v2.parts if p[0]!='03_venturi_floor_diffuser']+floor_parts
for n,M,mat in all_individual:glb(f'{OUT}/{n}.glb',[(n,M,(0,0,0),mat)])

open(f'{OUT}/FLOOR_DESIGN_NOTES.txt','w').write('''FORMULA EV V3 — 2022-2025 GROUND-EFFECT FLOOR STUDY\n\nThis is an original educational scale interpretation of publicly documented 2022-2025 Formula 1 ground-effect concepts, not a scan or exact copy of any team car.\n\nSYSTEMS MODELED\n- Twin Venturi inlets, descending ramps, narrow throats and progressive rear expansion\n- Four inlet fences per side\n- Raised floor-edge ramp and curl\n- Floor-edge vortex-generator row and rear cut-in wing\n- Central plank with inspection holes and separate titanium skid set\n- Bib/tea-tray element and floor stays\n- Left/right multi-stage diffuser shells\n- Six diffuser strakes and narrowed boat-tail center keel\n- Rear-wheel wake/tire-squirt fences\n\nFILES\nFORMULA_EV_V3_COMPLETE_2022_2025_FLOOR.glb: whole car with animated DRS.\nFORMULA_EV_V3_COMPLETE_UNDERFLOOR.glb: floor system only, assembled.\nFORMULA_EV_V3_EXPLODED_UNDERFLOOR.glb: floor elements separated for study.\nNumbered GLBs: every major car and floor component individually.\n''')
# Validate all GLB headers and package all files.
for fn in os.listdir(OUT):
 if fn.endswith('.glb'):
  magic,ver,total=struct.unpack('<4sII',open(OUT+'/'+fn,'rb').read(12));assert magic==b'glTF' and ver==2
with zipfile.ZipFile(f'{OUT}/FORMULA_EV_V3_ALL_GLB_FILES.zip','w',zipfile.ZIP_DEFLATED) as z:
 for fn in os.listdir(OUT):
  if fn.endswith('.glb') or fn.endswith('.txt'):z.write(OUT+'/'+fn,fn)
print('whole instances',len(I),'floor parts',len(floor_parts),'individual',len(all_individual))
