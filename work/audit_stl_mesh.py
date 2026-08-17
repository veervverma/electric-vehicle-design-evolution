import struct,sys,glob,os,math,collections

def read(path):
 b=open(path,'rb').read(); n=struct.unpack_from('<I',b,80)[0]
 if 84+50*n != len(b): raise ValueError('not binary STL')
 tris=[]
 for i in range(n):
  off=84+i*50+12
  tris.append(tuple(struct.unpack_from('<3f',b,off+12*j) for j in range(3)))
 return tris

def audit(path,tol=1e-5):
 T=read(path); d={}; V=[]; F=[]; deg=0
 def vid(p):
  q=tuple(round(x/tol) for x in p)
  if q not in d:d[q]=len(V);V.append(p)
  return d[q]
 E=collections.Counter()
 for t in T:
  f=[vid(p) for p in t]
  a,b,c=t
  ux,uy,uz=(b[i]-a[i] for i in range(3)); vx,vy,vz=(c[i]-a[i] for i in range(3))
  cx=uy*vz-uz*vy;cy=uz*vx-ux*vz;cz=ux*vy-uy*vx
  if cx*cx+cy*cy+cz*cz < tol*tol:deg+=1
  F.append(f)
  for u,v in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])): E[tuple(sorted((u,v)))]+=1
 bad=sum(1 for x in E.values() if x!=2); boundary=sum(1 for x in E.values() if x==1); multi=sum(1 for x in E.values() if x>2)
 # face adjacency via shared edge
 adj=[[] for _ in F]; owners={}
 for fi,f in enumerate(F):
  for u,v in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):
   e=tuple(sorted((u,v)))
   if e in owners:
    for fj in owners[e]:adj[fi].append(fj);adj[fj].append(fi)
    owners[e].append(fi)
   else:owners[e]=[fi]
 seen=set(); comps=0
 for i in range(len(F)):
  if i in seen:continue
  comps+=1;st=[i];seen.add(i)
  while st:
   q=st.pop()
   for j in adj[q]:
    if j not in seen:seen.add(j);st.append(j)
 P=[p for t in T for p in t]; lo=[min(p[i] for p in P) for i in range(3)];hi=[max(p[i] for p in P) for i in range(3)]
 return len(T),len(V),bad,boundary,multi,deg,comps,[hi[i]-lo[i] for i in range(3)]

for p in sys.argv[1:] or glob.glob('outputs/V6_CFD_REBUILD/geometry/*.stl'):
 print(os.path.basename(p),audit(p))
