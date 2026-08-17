import math, struct, os, zipfile
from xml.sax.saxutils import escape
OUT='outputs/advanced_ev_sedan'
os.makedirs(OUT,exist_ok=True)

# Triangle mesh utilities, standard-library only.
def add_tri(M,a,b,c): M.append((a,b,c))
def box(cx,cy,cz,l,w,h):
 x0,x1=cx-l/2,cx+l/2; y0,y1=cy-w/2,cy+w/2; z0,z1=cz-h/2,cz+h/2
 v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
 f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
 return [(v[a],v[b],v[c]) for a,b,c in f]
def cyl(cx,cy,cz,r,l,axis='y',n=40):
 M=[]
 def p(t,s):
  a=2*math.pi*t/n
  if axis=='y': return (cx+r*math.cos(a),cy+s*l/2,cz+r*math.sin(a))
  if axis=='x': return (cx+s*l/2,cy+r*math.cos(a),cz+r*math.sin(a))
  return (cx+r*math.cos(a),cy+r*math.sin(a),cz+s*l/2)
 for i in range(n):
  j=(i+1)%n
  a,b,c,d=p(i,-1),p(j,-1),p(j,1),p(i,1)
  M += [(a,b,c),(a,c,d)]
  M += [((cx,cy-l/2,cz) if axis=='y' else (cx-l/2,cy,cz) if axis=='x' else (cx,cy,cz-l/2),b,a)]
  M += [((cx,cy+l/2,cz) if axis=='y' else (cx+l/2,cy,cz) if axis=='x' else (cx,cy,cz+l/2),d,c)]
 return M
def tube(cx,cy,cz,ro,ri,l,axis='y',n=40):
 M=[]
 def p(r,t,s):
  a=2*math.pi*t/n
  if axis=='y': return (cx+r*math.cos(a),cy+s*l/2,cz+r*math.sin(a))
  if axis=='x': return (cx+s*l/2,cy+r*math.cos(a),cz+r*math.sin(a))
  return (cx+r*math.cos(a),cy+r*math.sin(a),cz+s*l/2)
 for i in range(n):
  j=(i+1)%n
  for r,flip in ((ro,False),(ri,True)):
   a,b,c,d=p(r,i,-1),p(r,j,-1),p(r,j,1),p(r,i,1)
   M += [(a,c,b),(a,d,c)] if flip else [(a,b,c),(a,c,d)]
  for s in (-1,1):
   ao,bo=p(ro,i,s),p(ro,j,s); ai,bi=p(ri,i,s),p(ri,j,s)
   M += [(ao,bi,bo),(ao,ai,bi)] if s<0 else [(ao,bo,bi),(ao,bi,ai)]
 return M
def beam(a,b,r,n=16):
 # cylinder aligned to arbitrary vector
 ax,ay,az=a; bx,by,bz=b; dx,dy,dz=bx-ax,by-ay,bz-az; L=math.sqrt(dx*dx+dy*dy+dz*dz)
 ux,uy,uz=dx/L,dy/L,dz/L
 # perpendicular basis
 tx,ty,tz=(0,0,1) if abs(uz)<.9 else (0,1,0)
 vx,vy,vz=uy*tz-uz*ty,uz*tx-ux*tz,ux*ty-uy*tx; q=math.sqrt(vx*vx+vy*vy+vz*vz); vx,vy,vz=vx/q,vy/q,vz/q
 wx,wy,wz=uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx
 M=[]
 rings=[]
 for P in (a,b):
  ring=[]
  for i in range(n):
   t=2*math.pi*i/n; ring.append((P[0]+r*(vx*math.cos(t)+wx*math.sin(t)),P[1]+r*(vy*math.cos(t)+wy*math.sin(t)),P[2]+r*(vz*math.cos(t)+wz*math.sin(t))))
  rings.append(ring)
 for i in range(n):
  j=(i+1)%n; M += [(rings[0][i],rings[0][j],rings[1][j]),(rings[0][i],rings[1][j],rings[1][i])]
 return M
def loft(sections,n_y=14,bottom=8):
 # sections: (x, halfwidth, top center, top edge), closed solid
 M=[]; rings=[]
 for x,w,tc,te in sections:
  ring=[]
  # bottom left->right then curved top right->left
  ring.append((x,-w,bottom)); ring.append((x,w,bottom))
  for i in range(n_y+1):
   y=w-2*w*i/n_y; u=abs(y)/w; z=tc+(te-tc)*(u**1.75); ring.append((x,y,z))
  rings.append(ring)
 N=len(rings[0])
 for k in range(len(rings)-1):
  for i in range(N):
   j=(i+1)%N; M += [(rings[k][i],rings[k+1][i],rings[k+1][j]),(rings[k][i],rings[k+1][j],rings[k][j])]
 for ring,rev in ((rings[0],True),(rings[-1],False)):
  c=(ring[0][0],sum(p[1] for p in ring)/N,sum(p[2] for p in ring)/N)
  for i in range(N):
   j=(i+1)%N; M += [(c,ring[j],ring[i])] if rev else [(c,ring[i],ring[j])]
 return M
def translate(M,dx=0,dy=0,dz=0): return [((a[0]+dx,a[1]+dy,a[2]+dz),(b[0]+dx,b[1]+dy,b[2]+dz),(c[0]+dx,c[1]+dy,c[2]+dz)) for a,b,c in M]
def write_stl(path,M,name):
 with open(path,'wb') as f:
  f.write(name.encode()[:80].ljust(80,b' ')); f.write(struct.pack('<I',len(M)))
  for a,b,c in M:
   f.write(struct.pack('<12fH',0,0,0,*a,*b,*c,0))
def bounds(M):
 P=[p for t in M for p in t]; return tuple(round(max(p[i] for p in P)-min(p[i] for p in P),2) for i in range(3))

# LOWER BODY: long, low fastback silhouette with integrated splitter/skirts/diffuser.
secs=[(-96,23,16,12),(-91,34,19,13),(-78,43,24,17),(-58,45,27,20),(-20,46,29,21),(25,46,30,21),(57,44,28,20),(78,41,25,18),(91,32,20,14),(96,20,16,12)]
body=loft(secs,bottom=7)
body += box(-90,0,6,18,74,3)                 # front splitter
body += box(2,-45,10,140,3,6)+box(2,45,10,140,3,6) # side skirts
body += box(88,0,8,13,70,3)                  # diffuser deck
for y in (-24,0,24): body += box(88,y,10,15,2.2,7) # diffuser fins
# battery tray / structural spine visible underneath
body += box(5,0,8.5,105,55,3)
# cabin deck pegs
for x in (-24,28):
 for y in (-24,24): body += cyl(x,y,29.5,2.7,5,'z',24)
# motor cradle inside front bay (130 or N20 motor adapter space)
body += box(-55,0,18,42,3,8)
for y in (-17,17): body += box(-55,y,18,42,3,8)
# air intake / styling ribs
for y in (-17,0,17): body += box(-82,y,17,16,2,4)

# CABIN: fastback glasshouse, roof spine, window-frame-like rails, hood/trunk shoulders.
cabsecs=[(-45,30,4,2),(-34,35,20,8),(-18,37,30,14),(8,38,34,16),(31,35,28,12),(49,29,13,5),(57,24,4,2)]
cabin=loft(cabsecs,n_y=16,bottom=0)
# center roof scoop and A/C fin details
cabin += box(5,0,34.5,30,8,2)
for y in (-37,37): cabin += beam((-28,y,9),(31,y,12),1.4)
# alignment sleeves represented as reinforcing pads
for x in (-24,28):
 for y in (-24,24): cabin += tube(x,y,1.8,4.0,3.25,3.6,'z',24)

# REAR WING, separate for easier printing.
wing=box(0,0,0,35,78,3)
wing += box(-13,-31,-7,5,4,14)+box(-13,31,-7,5,4,14)
wing += box(10,-31,-7,5,4,14)+box(10,31,-7,5,4,14)
# subtle end plates
wing += box(0,-40,1,38,3,11)+box(0,40,1,38,3,11)

# AXLE/SUSPENSION MODULE: double wishbone look, spring beam, axle tube, hub carriers.
def axle_module():
 M=[]
 M += box(0,0,0,26,58,3) # mounting bridge; assembly z origin at bridge
 for s in (-1,1):
  y=s*34
  # upper/lower A-arm pairs
  M += beam((-9,s*22,-2),(0,y,-8),1.7)+beam((9,s*22,-2),(0,y,-8),1.7)
  M += beam((-10,s*22,-12),(0,y,-8),1.9)+beam((10,s*22,-12),(0,y,-8),1.9)
  # upright and shock
  M += beam((0,y,-13),(0,y,0),2.1)
  M += beam((7,s*22,-1),(0,y,-9),1.7)
  # hub axle
  M += cyl(0,s*40,-8,3.8,13,'y',32)
 # transverse flexible leaf beam
 M += box(0,0,-3,12,68,2.2)
 return M
axle=axle_module()

# WHEEL: directional rim, tread ribs, separate spinning part.
def wheel():
 M=tube(0,0,0,16.5,10.8,9,'y',48)
 M+=tube(0,0,0,10.8,4.3,7.5,'y',40)
 # five split spokes on outer face
 for k in range(5):
  a=2*math.pi*k/5
  M += beam((4.4*math.cos(a),-4.0,4.4*math.sin(a)),(10*math.cos(a+.18),-4.0,10*math.sin(a+.18)),1.4,12)
  M += beam((4.4*math.cos(a),-4.0,4.4*math.sin(a)),(10*math.cos(a-.18),-4.0,10*math.sin(a-.18)),1.4,12)
 # tread ribs
 for k in range(24):
  a=2*math.pi*k/24; M += box(16.1*math.cos(a),0,16.1*math.sin(a),2.6,10,1.2)
 return M
wheel=wheel()
# Snap caps retain wheels on axles.
cap=cyl(0,0,0,5.8,2.5,'y',32)+cyl(0,1.8,0,3.5,3.5,'y',28)

parts={'advanced_body':body,'fastback_cabin':cabin,'rear_wing':wing,'suspension_axle_module_x2':axle,'sport_wheel_x4':wheel,'wheel_retainer_cap_x4':cap}
for n,M in parts.items():
 write_stl(f'{OUT}/{n}.stl',M,n); print(n,bounds(M),len(M))

# Full visual/reference assembly STL (not recommended as the functional print).
assembly=list(body)+translate(cabin,0,0,29)
assembly+=translate(wing,72,0,48)
for x in (-65,65):
 assembly+=translate(axle,x,0,22)
 for y in (-46,46): assembly+=translate(wheel,x,y,14)
write_stl(f'{OUT}/advanced_sedan_assembled_reference.stl',assembly,'advanced_sedan_assembled_reference')
print('assembly',bounds(assembly),len(assembly))

# Write a slicer-friendly 3MF containing all print parts arranged on one 220x220 plate.
def verts_faces(M):
 d={}; V=[]; F=[]
 for tri in M:
  ids=[]
  for p in tri:
   key=tuple(round(q,5) for q in p)
   if key not in d: d[key]=len(V); V.append(key)
   ids.append(d[key])
  F.append(ids)
 return V,F
placements=[('body',body,(100,110,0)),('cabin',cabin,(100,40,0)),('wing',wing,(180,35,10)),('axle1',axle,(24,35,15)),('axle2',axle,(24,105,15))]
# Wheels and caps on separate side region, standing as modeled.
for i in range(4): placements.append((f'wheel{i+1}',wheel,(170+(i%2)*22,80+(i//2)*42,17)))
for i in range(4): placements.append((f'cap{i+1}',cap,(168+i*11,175,6)))
objects=[]
for oid,(name,M,tr) in enumerate(placements,1):
 V,F=verts_faces(M); vs=''.join(f'<vertex x="{x}" y="{y}" z="{z}"/>' for x,y,z in V); fs=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in F)
 objects.append(f'<object id="{oid}" name="{escape(name)}" type="model"><mesh><vertices>{vs}</vertices><triangles>{fs}</triangles></mesh></object>')
build=''.join(f'<item objectid="{i}" transform="1 0 0 0 1 0 0 0 1 {tr[0]} {tr[1]} {tr[2]}"/>' for i,(_,_,tr) in enumerate(placements,1))
model='<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><metadata name="Title">Advanced EV Sedan Printing Kit</metadata><resources>'+''.join(objects)+'</resources><build>'+build+'</build></model>'
rels='<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
ct='<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
with zipfile.ZipFile(f'{OUT}/advanced_ev_sedan_print_plate.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml',ct); z.writestr('_rels/.rels',rels); z.writestr('3D/3dmodel.model',model)

# README
open(f'{OUT}/PRINT_AND_ASSEMBLY.txt','w').write('''ADVANCED EV SEDAN PRINTING KIT\n\nPARTS\n1x advanced_body.stl\n1x fastback_cabin.stl\n1x rear_wing.stl\n2x suspension_axle_module_x2.stl\n4x sport_wheel_x4.stl\n4x wheel_retainer_cap_x4.stl\n\nRecommended material: PETG. Use TPU only for optional tires if you later separate the tire geometry.\nLayer height: 0.20 mm; walls: 4; infill: 20-25%; supports: build plate only for suspension modules and wing.\n\nASSEMBLY\n1. Glue cabin to the four deck pegs.\n2. Glue axle-module bridges into the underside mounting areas at x = +/-65 mm. Keep arms free.\n3. Slide wheels onto 7.6 mm diameter axle stubs; gently sand bores if needed.\n4. Glue retainer caps only to axle ends; do not glue wheels.\n5. Glue wing on the rear deck.\n6. Install a 130-size DC motor or N20 gearmotor in the front cradle; final drivetrain coupling depends on your motor/gearbox.\n\nOverall assembled envelope: about 192 x 101 x 59 mm. Fits a 220 x 220 x 250 mm printer.\nThe 3MF contains the entire kit as individually selectable objects.\n''')
