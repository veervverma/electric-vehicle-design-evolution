#!/usr/bin/env python3
"""Build the reproducible W11 2020 reference-based half-car SU2 CFD mesh.

This is a deliberately defeatured, full-scale aerodynamic surrogate derived
from the printable/reference model.  It preserves the 2020 flat/stepped floor,
central plank, short diffuser, exposed wheels, inverted wings, sidepod/body
volumes and half-car symmetry.  It does not claim to be proprietary Mercedes
CAD.  Gmsh 4.15+ is required.

Usage:
  python work/build_w11_2020_su2_case.py [output.su2] [body_mesh_size_m]
"""

import gmsh, math, os, sys

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT=os.path.join(ROOT,'outputs/W11_2020_AERO_CFD_VALIDATION_300KPH/CFD_SU2_CASE/w11_coarse.su2')
out=os.path.abspath(sys.argv[1]) if len(sys.argv)>1 else DEFAULT
lc=float(sys.argv[2]) if len(sys.argv)>2 else 0.24
os.makedirs(os.path.dirname(out),exist_ok=True)
gmsh.initialize()
gmsh.option.setNumber('General.Terminal',1)
gmsh.model.add('w11_half_domain')
occ=gmsh.model.occ

domain=occ.addBox(-10.0,0.0,0.0,25.0,5.0,5.0)
sol=[]
def ellipsoid(cx,cy,cz,rx,ry,rz):
    t=occ.addSphere(cx,cy,cz,1.0)
    occ.dilate([(3,t)],cx,cy,cz,rx,ry,rz)
    sol.append((3,t)); return t
def box(x,y,z,dx,dy,dz):
    t=occ.addBox(x,y,z,dx,dy,dz);sol.append((3,t));return t
def cyl(x,y,z,dx,dy,dz,r):
    t=occ.addCylinder(x,y,z,dx,dy,dz,r);sol.append((3,t));return t
def ramp(x0,x1,y0,y1,z0a,z0b,thick):
    wires=[]
    for x,z0 in [(x0,z0a),(x1,z0b)]:
        p=[occ.addPoint(x,y0,z0),occ.addPoint(x,y1,z0),occ.addPoint(x,y1,z0+thick),occ.addPoint(x,y0,z0+thick)]
        e=[occ.addLine(p[i],p[(i+1)%4]) for i in range(4)]
        wires.append(occ.addWire(e))
    made=occ.addThruSections(wires,makeSolid=True,makeRuled=True)
    for dt in made:
        if dt[0]==3: sol.append(dt)
    return made
def foil(cx,cz,chord,span,camber=-0.08,thickness=0.10,angle_deg=0,n=22):
    pts=[]
    upper=[];lower=[]
    pcam=0.4
    for i in range(n+1):
        u=(1-math.cos(math.pi*i/n))/2
        yt=5*thickness*(0.2969*math.sqrt(max(u,1e-12))-0.1260*u-0.3516*u*u+0.2843*u**3-0.1036*u**4)
        if u<pcam:
            yc=camber/(pcam*pcam)*(2*pcam*u-u*u);dy=2*camber/(pcam*pcam)*(pcam-u)
        else:
            yc=camber/((1-pcam)**2)*((1-2*pcam)+2*pcam*u-u*u);dy=2*camber/((1-pcam)**2)*(pcam-u)
        th=math.atan(dy)
        upper.append((u-yt*math.sin(th),yc+yt*math.cos(th)))
        lower.append((u+yt*math.sin(th),yc-yt*math.cos(th)))
    profile=upper+list(reversed(lower[1:-1]))
    a=math.radians(angle_deg);tags=[]
    for u,z in profile:
        xx=(u-0.5)*chord;zz=z*chord
        x=cx+xx*math.cos(a)+zz*math.sin(a)
        zz2=cz-xx*math.sin(a)+zz*math.cos(a)
        tags.append(occ.addPoint(x,0.0,zz2))
    edges=[occ.addLine(tags[i],tags[(i+1)%len(tags)]) for i in range(len(tags))]
    wire=occ.addWire(edges);face=occ.addPlaneSurface([wire])
    made=occ.extrude([(2,face)],0,span,0)
    for dt in made:
        if dt[0]==3:sol.append(dt)
    return made

# 2020-era flat/stepped floor and central plank.
box(-1.62,0.0,0.055,3.15,0.96,0.055)
box(-1.60,0.0,0.035,3.05,0.155,0.025)
# Short 2020-style diffuser ramp, not a 2022 twin Venturi tunnel.
t=occ.addBox(1.20,0.0,0.055,0.82,0.86,0.055)
occ.rotate([(3,t)],1.20,0.0,0.055,0,1,0,math.radians(-13.0));sol.append((3,t))
# Main survival cell, nose, engine cover, and one half-sidepod.
ellipsoid(-0.35,0.0,0.48,1.35,0.39,0.43)
ellipsoid(-1.55,0.0,0.31,0.90,0.18,0.16)
ellipsoid(0.65,0.0,0.68,1.18,0.23,0.48)
ellipsoid(0.25,0.53,0.38,1.12,0.50,0.29)
# Halo/cockpit headrest envelope.
ellipsoid(-0.12,0.0,0.88,0.42,0.31,0.34)
# Inverted-camber front and rear wing elements.
for x,z,chord,span,camber,ang in [(-2.33,0.13,0.52,1.0,-0.12,-15),(-2.12,0.20,0.38,0.96,-0.14,-20),(-1.94,0.27,0.29,0.88,-0.16,-25),
                                  (1.78,1.03,0.42,0.78,-0.18,-25),(1.94,1.17,0.34,0.75,-0.20,-30)]:
    foil(x,z,chord,span,camber,0.10,ang)
# Endplates.
box(-2.38,0.94,0.09,0.62,0.035,0.28)
box(1.69,0.745,0.87,0.46,0.035,0.52)
# Wheels and suspension on modeled half.
for x,r,w in [(-1.55,0.36,0.305),(1.53,0.37,0.405)]:
    cyl(x,0.73,r+0.008,0,w,0,r)
# Bargeboards and rear tyre vanes represented as thin solids.
for x,z in [(-1.12,0.16),(-1.02,0.21),(-0.92,0.26),(-0.82,0.31),(1.08,0.14),(1.18,0.18),(1.28,0.22)]:
    box(x,0.72,z,0.035,0.22,0.30 if x<0 else 0.20)

occ.synchronize()
current=[(3,domain)]
for i,tool in enumerate(sol):
    cut,_=occ.cut(current,[tool],removeObject=True,removeTool=True)
    vols_i=[dt for dt in cut if dt[0]==3]
    if not vols_i:
        raise RuntimeError(f'cut {i} removed fluid domain')
    current=[max(vols_i,key=lambda dt: occ.getMass(*dt))]
occ.synchronize()
print('sequential cuts',len(sol),'fluid',current,occ.getMass(*current[0]))
cut=current
occ.synchronize()
vols=[t for d,t in cut if d==3]
if not vols: raise RuntimeError('no fluid volume')
gmsh.model.addPhysicalGroup(3,vols,1)
gmsh.model.setPhysicalName(3,1,'fluid')

surfs=[]
for v in vols:
    surfs += [t for d,t in gmsh.model.getBoundary([(3,v)],oriented=False,recursive=False) if d==2]
surfs=sorted(set(surfs))
groups={'inlet':[],'outlet':[],'ground':[],'symmetry':[],'farfield':[],'car':[]}
tol=1e-5
for s in surfs:
    xmin,ymin,zmin,xmax,ymax,zmax=gmsh.model.getBoundingBox(2,s)
    if abs(xmin+10)<tol and abs(xmax+10)<tol: groups['inlet'].append(s)
    elif abs(xmin-15)<tol and abs(xmax-15)<tol: groups['outlet'].append(s)
    elif abs(zmin)<tol and abs(zmax)<tol: groups['ground'].append(s)
    elif abs(ymin)<tol and abs(ymax)<tol: groups['symmetry'].append(s)
    elif abs(ymin-5)<tol and abs(ymax-5)<tol or abs(zmin-5)<tol and abs(zmax-5)<tol: groups['farfield'].append(s)
    else: groups['car'].append(s)
for i,(name,tags) in enumerate(groups.items(),10):
    if not tags: print('WARN empty',name);continue
    gmsh.model.addPhysicalGroup(2,tags,i);gmsh.model.setPhysicalName(2,i,name)
print('groups',{k:len(v) for k,v in groups.items()})

# Local refinement around all car surfaces and a ground/near wake box.
dist=gmsh.model.mesh.field.add('Distance')
gmsh.model.mesh.field.setNumbers(dist,'SurfacesList',groups['car'])
gmsh.model.mesh.field.setNumber(dist,'Sampling',100)
th=gmsh.model.mesh.field.add('Threshold')
gmsh.model.mesh.field.setNumber(th,'InField',dist)
gmsh.model.mesh.field.setNumber(th,'SizeMin',lc)
gmsh.model.mesh.field.setNumber(th,'SizeMax',0.9)
gmsh.model.mesh.field.setNumber(th,'DistMin',0.25)
gmsh.model.mesh.field.setNumber(th,'DistMax',2.2)
boxf=gmsh.model.mesh.field.add('Box')
for n,val in [('VIn',min(0.32,lc*1.6)),('VOut',0.9),('XMin',-3.2),('XMax',6.0),('YMin',0.0),('YMax',2.0),('ZMin',0.0),('ZMax',1.8)]:gmsh.model.mesh.field.setNumber(boxf,n,val)
under=max(0.010,lc/10.0)
underf=gmsh.model.mesh.field.add('Box')
for n,val in [('VIn',under),('VOut',0.9),('XMin',-1.85),('XMax',2.35),('YMin',0.0),('YMax',1.15),('ZMin',0.0),('ZMax',0.22)]:gmsh.model.mesh.field.setNumber(underf,n,val)
mn=gmsh.model.mesh.field.add('Min');gmsh.model.mesh.field.setNumbers(mn,'FieldsList',[th,boxf,underf]);gmsh.model.mesh.field.setAsBackgroundMesh(mn)
gmsh.option.setNumber('Mesh.MeshSizeMin',under)
gmsh.option.setNumber('Mesh.MeshSizeMax',0.9)
gmsh.option.setNumber('Mesh.Algorithm3D',1)
gmsh.option.setNumber('Mesh.Optimize',1)
gmsh.option.setNumber('Mesh.SaveAll',0)
gmsh.model.mesh.generate(3)
gmsh.write(out)
gmsh.write(out.rsplit('.',1)[0]+'.msh')
types,etags,enodes=gmsh.model.mesh.getElements(3)
element_count=sum(len(x) for x in etags)
node_tags,_,_=gmsh.model.mesh.getNodes()
meta={
    'model':'W11 2020 reference-based half-car aerodynamic surrogate',
    'solver_target':'SU2 8.5 INC_RANS SST V2003m',
    'units':'metres',
    'freestream_m_s':83.333333,
    'body_mesh_size_m':lc,
    'underfloor_mesh_size_m':under,
    'node_count':len(node_tags),
    'tetrahedron_count':element_count,
    'domain_m':{'x':[-10.0,15.0],'y':[0.0,5.0],'z':[0.0,5.0]},
    'limitations':['de-featured public-information surrogate','half-car symmetry','no cooling flow','wheel rotation not solved','no proprietary Mercedes geometry']
}
import json
with open(out.rsplit('.',1)[0]+'_mesh_metadata.json','w') as f:
    json.dump(meta,f,indent=2)
print('3d elements',element_count,'types',types,'out',out)
gmsh.finalize()
