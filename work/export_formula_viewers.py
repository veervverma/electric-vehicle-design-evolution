import sys,os,math,struct,json
sys.path.insert(0,'work')
import formula_ev as f
OUT='outputs/formula_ev_prototype'
colors={'White Carbon':(0.90,0.90,0.87,1),'Black Carbon':(0.035,0.045,0.06,1),'Tire':(0.012,0.012,0.012,1),'Aluminum':(0.55,0.60,0.65,1),'Brake':(0.30,0.33,0.36,1),'Red':(0.75,0.02,0.02,1),'Battery':(0.03,0.30,0.65,1),'HV Orange':(0.95,0.28,0.0,1),'Cockpit':(0.08,0.11,0.15,1)}

def indexed(M):
 d={};V=[];F=[]
 for tri in M:
  ids=[]
  for p in tri:
   p=tuple(float(q) for q in p)
   if p not in d:d[p]=len(V);V.append(p)
   ids.append(d[p])
  F.extend(ids)
 return V,F

# GLB 2.0 with individually named nodes and PBR materials.
binbuf=bytearray(); views=[]; accessors=[]; meshes=[]; nodes=[]
def align4():
 while len(binbuf)%4:binbuf.append(0)
def add_view(data,target):
 align4();off=len(binbuf);binbuf.extend(data);views.append({'buffer':0,'byteOffset':off,'byteLength':len(data),'target':target});return len(views)-1
mats=[];midx={}
for name,c in colors.items():
 midx[name]=len(mats);mats.append({'name':name,'pbrMetallicRoughness':{'baseColorFactor':list(c),'metallicFactor':0.65 if name in ('Aluminum','Brake') else 0.05,'roughnessFactor':0.25 if name in ('White Carbon','Aluminum') else 0.58},'doubleSided':True})
for name,M,tr,mat in f.I:
 V,F=indexed(M)
 pos=b''.join(struct.pack('<3f',*p) for p in V);ind=b''.join(struct.pack('<I',i) for i in F)
 pv=add_view(pos,34962);iv=add_view(ind,34963)
 mins=[min(p[k] for p in V) for k in range(3)];maxs=[max(p[k] for p in V) for k in range(3)]
 pa=len(accessors);accessors.append({'bufferView':pv,'componentType':5126,'count':len(V),'type':'VEC3','min':mins,'max':maxs})
 ia=len(accessors);accessors.append({'bufferView':iv,'componentType':5125,'count':len(F),'type':'SCALAR','min':[min(F)],'max':[max(F)]})
 meshes.append({'name':name,'primitives':[{'attributes':{'POSITION':pa},'indices':ia,'material':midx[mat]}]})
 nodes.append({'name':name,'mesh':len(meshes)-1,'translation':list(tr)})
# Root converts model Z-up to glTF Y-up.
root={'name':'FORMULA EV ASSEMBLY','rotation':[-0.7071068,0,0,0.7071068],'children':list(range(1,len(nodes)+1))}
gltf={'asset':{'version':'2.0','generator':'Formula EV portfolio exporter'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[root]+nodes,'meshes':meshes,'materials':mats,'buffers':[{'byteLength':len(binbuf)}],'bufferViews':views,'accessors':accessors}
js=json.dumps(gltf,separators=(',',':')).encode();js+=b' ' *((4-len(js)%4)%4);align4();bb=bytes(binbuf);bb+=b'\0'*((4-len(bb)%4)%4)
total=12+8+len(js)+8+len(bb)
with open(OUT+'/FORMULA_EV_DETAILED_VIEWER.glb','wb') as o:
 o.write(struct.pack('<4sII',b'glTF',2,total));o.write(struct.pack('<I4s',len(js),b'JSON'));o.write(js);o.write(struct.pack('<I4s',len(bb),b'BIN\0'));o.write(bb)

# OBJ + MTL fallback for Blender, MeshLab and FreeCAD.
with open(OUT+'/FORMULA_EV_DETAILED_VIEWER.mtl','w') as m:
 for name,c in colors.items():
  m.write(f'newmtl {name.replace(" ","_")}\nKd {c[0]} {c[1]} {c[2]}\nKs 0.35 0.35 0.35\nNs 80\n\n')
with open(OUT+'/FORMULA_EV_DETAILED_VIEWER.obj','w') as o:
 o.write('mtllib FORMULA_EV_DETAILED_VIEWER.mtl\n')
 base=1
 for name,M,(tx,ty,tz),mat in f.I:
  V,F=indexed(M);o.write(f'o {name.replace(" ","_")}\nusemtl {mat.replace(" ","_")}\n')
  for x,y,z in V:o.write(f'v {x+tx:.5f} {y+ty:.5f} {z+tz:.5f}\n')
  for i in range(0,len(F),3):o.write(f'f {base+F[i]} {base+F[i+1]} {base+F[i+2]}\n')
  base+=len(V)
print('GLB',os.path.getsize(OUT+'/FORMULA_EV_DETAILED_VIEWER.glb'))
print('OBJ',os.path.getsize(OUT+'/FORMULA_EV_DETAILED_VIEWER.obj'))
