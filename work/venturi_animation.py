import os,sys,math,struct,json
sys.path.insert(0,'work')
import formula_ev_v3_floor as v3
from advanced_sedan import box,cyl,beam
OUT='outputs/v5_wind_tunnel_and_track_sim';os.makedirs(OUT,exist_ok=True)
# Floor elements plus translucent context body.
materials={'Ghost Body':((.75,.82,.88,.16),'BLEND'),'Carbon':((.035,.045,.06,1),'OPAQUE'),'Underfloor':((.10,.12,.15,1),'OPAQUE'),'Plank':((.58,.42,.23,1),'OPAQUE'),'Titanium':((.48,.52,.56,1),'OPAQUE'),'Air Slow':((.15,.72,1,1),'OPAQUE'),'Air Fast':((1,.75,.08,1),'OPAQUE'),'Downforce':((.95,.06,.04,1),'OPAQUE'),'Tunnel Frame':((.55,.62,.68,.20),'BLEND')}
I=[]
I += [('Ghost monocoque',v3.v2.monocoque,(0,0,0),'Ghost Body'),('Ghost sidepods',v3.v2.sidepods,(0,0,0),'Ghost Body')]
matmap={'Black Carbon':'Carbon','Underfloor':'Underfloor','Red':'Air Fast','Plank':'Plank','Titanium':'Titanium'}
for n,M,mat in v3.floor_parts:I.append((n,M,(0,0,0),matmap.get(mat,'Carbon')))
# Wind tunnel frame edges.
frame=[]
for y in (-58,58):
 frame+=beam((-82,y,-12),(94,y,-12),.8)+beam((-82,y,42),(94,y,42),.8)+beam((-82,y,-12),(-82,y,42),.8)+beam((94,y,-12),(94,y,42),.8)
for x in (-82,94):frame+=beam((x,-58,-12),(x,58,-12),.8)+beam((x,-58,42),(x,58,42),.8)
I.append(('Wind tunnel boundary frame',frame,(0,0,0),'Tunnel Frame'))
# Downforce vector arrows distributed across tunnel throat/diffuser.
arrows=[]
for x in (-35,0,35,65):
 for y in (-22,22):
  arrows+=beam((x,y,30),(x,y,20),1.0)
  arrows+=beam((x,y,20),(x-3,y,24),1.0)+beam((x,y,20),(x+3,y,24),1.0)
I.append(('Downforce vectors',arrows,(0,0,0),'Downforce'))
# Particle geometry and cyclic paths through both Venturi tunnels.
particle=cyl(0,0,0,1.0,3.2,'x',12)
paths=[]
ys=(-27,-20,-13,13,20,27)
base=[(-78,0,8),(-55,0,7),(-32,0,3.5),(5,0,3.2),(32,0,4),(55,0,10),(78,0,19),(94,0,23)]
for j,y in enumerate(ys):
 for phase in range(3):
  path=[(x,y,z+(j%2)*.8) for x,_,z in base];paths.append((f'Airflow particle y{y} p{phase}',particle,path,phase,'Air Fast' if abs(y)<22 else 'Air Slow'))

def indexed(M):
 d={};V=[];F=[]
 for tri in M:
  for p in tri:
   p=tuple(float(q) for q in p)
   if p not in d:d[p]=len(V);V.append(p)
   F.append(d[p])
 return V,F
buf=bytearray();views=[];acc=[];meshes=[];nodes=[]
def align():
 while len(buf)%4:buf.append(0)
def view(data,target=None):
 align();off=len(buf);buf.extend(data);q={'buffer':0,'byteOffset':off,'byteLength':len(data)}
 if target:q['target']=target
 views.append(q);return len(views)-1
mats=[];mi={}
for n,(c,mode) in materials.items():
 mi[n]=len(mats);q={'name':n,'pbrMetallicRoughness':{'baseColorFactor':list(c),'metallicFactor':.05,'roughnessFactor':.45},'doubleSided':True}
 if mode=='BLEND':q['alphaMode']='BLEND'
 mats.append(q)
def addmesh(name,M,tr,mat):
 V,F=indexed(M);pv=view(b''.join(struct.pack('<3f',*p) for p in V),34962);iv=view(b''.join(struct.pack('<I',i) for i in F),34963)
 mins=[min(p[k] for p in V) for k in range(3)];maxs=[max(p[k] for p in V) for k in range(3)]
 pa=len(acc);acc.append({'bufferView':pv,'componentType':5126,'count':len(V),'type':'VEC3','min':mins,'max':maxs});ia=len(acc);acc.append({'bufferView':iv,'componentType':5125,'count':len(F),'type':'SCALAR','min':[min(F)],'max':[max(F)]})
 meshes.append({'name':name,'primitives':[{'attributes':{'POSITION':pa},'indices':ia,'material':mi[mat]}]});nodes.append({'name':name,'mesh':len(meshes)-1,'translation':list(tr)});return len(nodes)
for n,M,tr,mat in I:addmesh(n,M,tr,mat)
particle_nodes=[]
for n,M,path,phase,mat in paths:particle_nodes.append((addmesh(n,M,path[0],mat),path,phase))
root={'name':'V5 VENTURI WIND TUNNEL STUDY','rotation':[-.7071068,0,0,.7071068],'children':list(range(1,len(nodes)+1))}
doc={'asset':{'version':'2.0','generator':'V5 Venturi airflow visualizer'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[root]+nodes,'meshes':meshes,'materials':mats,'buffers':[{'byteLength':0}],'bufferViews':views,'accessors':acc}
# One synchronized particle animation; phase offsets show a continuous stream.
times=[i*.55 for i in range(9)];tv=view(struct.pack('<9f',*times));ta=len(acc);acc.append({'bufferView':tv,'componentType':5126,'count':9,'type':'SCALAR','min':[times[0]],'max':[times[-1]]})
samplers=[];channels=[]
for node,path,phase in particle_nodes:
 seq=[]
 for k in range(9):seq.extend(path[(k+phase)%len(path)])
 vv=view(struct.pack('<27f',*seq));aa=len(acc);acc.append({'bufferView':vv,'componentType':5126,'count':9,'type':'VEC3'});samplers.append({'input':ta,'output':aa,'interpolation':'LINEAR'});channels.append({'sampler':len(samplers)-1,'target':{'node':node,'path':'translation'}})
doc['animations']=[{'name':'VENTURI AIRFLOW LOOP','samplers':samplers,'channels':channels}]
doc['buffers'][0]['byteLength']=len(buf);js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((4-len(js)%4)%4)
while len(buf)%4:buf.append(0)
bb=bytes(buf);total=12+8+len(js)+8+len(bb)
path=OUT+'/V5_VENTURI_WIND_TUNNEL_ANIMATION.glb'
with open(path,'wb') as o:o.write(struct.pack('<4sII',b'glTF',2,total));o.write(struct.pack('<I4s',len(js),b'JSON'));o.write(js);o.write(struct.pack('<I4s',len(bb),b'BIN\0'));o.write(bb)
print(path,'nodes',len(nodes),'particles',len(paths),'channels',len(channels))
