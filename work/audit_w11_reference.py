import struct,json,collections,math
P='references/mercedec-f1-2020/mercedec-f1-2020.glb'
b=open(P,'rb').read(); jl=struct.unpack_from('<I',b,12)[0]; d=json.loads(b[20:20+jl]); bo=20+jl; bl,bt=struct.unpack_from('<I4s',b,bo); data=b[bo+8:bo+8+bl]
cs={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)}; nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def acc(i):
 a=d['accessors'][i]; v=d['bufferViews'][a['bufferView']]; fmt,s=cs[a['componentType']]; n=nc[a['type']]; stride=v.get('byteStride',s*n); off=v.get('byteOffset',0)+a.get('byteOffset',0); return [struct.unpack_from('<'+fmt*n,data,off+k*stride) for k in range(a['count'])]
def audit(tris,tol=1e-5):
 dm={}; edges=collections.Counter(); deg=0
 def vid(p):
  k=tuple(round(q/tol) for q in p)
  if k not in dm:dm[k]=len(dm)
  return dm[k]
 for t in tris:
  f=tuple(vid(p) for p in t)
  if len(set(f))<3:deg+=1
  for e in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):edges[tuple(sorted(e))]+=1
 return len(dm),sum(v==1 for v in edges.values()),sum(v>2 for v in edges.values()),deg
sets={'all':set(range(43)),'no_wheels':set(range(43))-set(range(10,20)),'main_body':{0,1,2,3,4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,28,30,31,32}}
for sn,sel in sets.items():
 T=[]
 for pr in d['meshes'][0]['primitives']:
  if pr['material'] not in sel:continue
  V=acc(pr['attributes']['POSITION']); I=acc(pr['indices']); I=[q[0] for q in I]
  for j in range(0,len(I),3):T.append((V[I[j]],V[I[j+1]],V[I[j+2]]))
 print(sn,'tris',len(T),'audit',audit(T))
