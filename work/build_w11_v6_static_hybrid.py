#!/usr/bin/env python3
"""Build an 8-inch static W11/V6 hybrid display and desktop-print package.

The supplied Mercedes 2020 GLB remains the high-detail exterior reference in the
assembled visual files.  New geometry is deliberately printable: a reinforced
upper body approximation, twin-Venturi floor, structural EV chassis, energy
store, rear motor/inverter, static suspension and rolling wheel hardware.

Only the Python standard library is used so the build is reproducible here.
"""

import collections
import hashlib
import json
import math
import os
import shutil
import struct
import zipfile
from xml.sax.saxutils import escape


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCE = os.path.join(ROOT, "references/mercedec-f1-2020/mercedec-f1-2020.glb")
OUT = os.path.join(ROOT, "outputs/W11_V6_HYBRID_STATIC_8IN")
STL_DIR = os.path.join(OUT, "STL_PRINT_PARTS")
GLB_DIR = os.path.join(OUT, "GLB_INDIVIDUAL_PARTS")

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(STL_DIR)
os.makedirs(GLB_DIR)


# ---------------------------------------------------------------------------
# Closed triangle primitives. Coordinates are millimetres; X is longitudinal
# (front negative), Y lateral, Z up.
# ---------------------------------------------------------------------------

def box(cx, cy, cz, length, width, height):
    x0, x1 = cx - length / 2, cx + length / 2
    y0, y1 = cy - width / 2, cy + width / 2
    z0, z1 = cz - height / 2, cz + height / 2
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
         (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f = [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
         (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return [(v[a], v[b], v[c]) for a,b,c in f]


def cyl(cx, cy, cz, radius, length, axis="y", n=40):
    m = []
    def p(i, side):
        a = 2 * math.pi * i / n
        if axis == "y": return (cx + radius*math.cos(a), cy + side*length/2, cz + radius*math.sin(a))
        if axis == "x": return (cx + side*length/2, cy + radius*math.cos(a), cz + radius*math.sin(a))
        return (cx + radius*math.cos(a), cy + radius*math.sin(a), cz + side*length/2)
    c0 = (cx,cy-length/2,cz) if axis == "y" else (cx-length/2,cy,cz) if axis == "x" else (cx,cy,cz-length/2)
    c1 = (cx,cy+length/2,cz) if axis == "y" else (cx+length/2,cy,cz) if axis == "x" else (cx,cy,cz+length/2)
    for i in range(n):
        j = (i + 1) % n
        a,b,c,d = p(i,-1),p(j,-1),p(j,1),p(i,1)
        m += [(a,b,c),(a,c,d),(c0,b,a),(c1,d,c)]
    return m


def tube(cx, cy, cz, outer, inner, length, axis="y", n=48):
    m = []
    def p(r, i, side):
        a = 2 * math.pi * i / n
        if axis == "y": return (cx+r*math.cos(a), cy+side*length/2, cz+r*math.sin(a))
        if axis == "x": return (cx+side*length/2, cy+r*math.cos(a), cz+r*math.sin(a))
        return (cx+r*math.cos(a), cy+r*math.sin(a), cz+side*length/2)
    for i in range(n):
        j = (i + 1) % n
        for r, inward in ((outer,False),(inner,True)):
            a,b,c,d = p(r,i,-1),p(r,j,-1),p(r,j,1),p(r,i,1)
            m += [(a,c,b),(a,d,c)] if inward else [(a,b,c),(a,c,d)]
        for side in (-1,1):
            ao,bo,ai,bi = p(outer,i,side),p(outer,j,side),p(inner,i,side),p(inner,j,side)
            m += [(ao,bi,bo),(ao,ai,bi)] if side < 0 else [(ao,bo,bi),(ao,bi,ai)]
    return m


def beam(a, b, radius, n=16):
    ax,ay,az = a; bx,by,bz = b
    dx,dy,dz = bx-ax,by-ay,bz-az
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    if length <= 1e-12:
        return []
    ux,uy,uz = dx/length,dy/length,dz/length
    tx,ty,tz = (0,0,1) if abs(uz) < .9 else (0,1,0)
    vx,vy,vz = uy*tz-uz*ty, uz*tx-ux*tz, ux*ty-uy*tx
    q = math.sqrt(vx*vx + vy*vy + vz*vz); vx,vy,vz = vx/q,vy/q,vz/q
    wx,wy,wz = uy*vz-uz*vy, uz*vx-ux*vz, ux*vy-uy*vx
    rings = []
    for p0 in (a,b):
        ring = []
        for i in range(n):
            t = 2*math.pi*i/n
            ring.append((p0[0]+radius*(vx*math.cos(t)+wx*math.sin(t)),
                         p0[1]+radius*(vy*math.cos(t)+wy*math.sin(t)),
                         p0[2]+radius*(vz*math.cos(t)+wz*math.sin(t))))
        rings.append(ring)
    m = []
    for i in range(n):
        j = (i + 1) % n
        m += [(rings[0][i],rings[0][j],rings[1][j]),
              (rings[0][i],rings[1][j],rings[1][i]),
              (a,rings[0][j],rings[0][i]),
              (b,rings[1][i],rings[1][j])]
    return m


def loft(sections, n_y=16, bottom=5.0):
    """Closed loft. sections are (x, half_width, top_center, top_edge)."""
    rings = []
    for x,w,tc,te in sections:
        ring = [(x,-w,bottom),(x,w,bottom)]
        for i in range(n_y + 1):
            y = w - 2*w*i/n_y
            u = abs(y)/max(w,1e-9)
            z = tc + (te-tc)*(u**1.65)
            ring.append((x,y,z))
        rings.append(ring)
    n = len(rings[0]); m = []
    for k in range(len(rings)-1):
        for i in range(n):
            j = (i+1)%n
            m += [(rings[k][i],rings[k+1][i],rings[k+1][j]),
                  (rings[k][i],rings[k+1][j],rings[k][j])]
    for ring, rev in ((rings[0],True),(rings[-1],False)):
        c = (ring[0][0],sum(p[1] for p in ring)/n,sum(p[2] for p in ring)/n)
        for i in range(n):
            j = (i+1)%n
            m += [(c,ring[j],ring[i])] if rev else [(c,ring[i],ring[j])]
    return m


def translate(mesh, dx=0, dy=0, dz=0):
    return [tuple((p[0]+dx,p[1]+dy,p[2]+dz) for p in tri) for tri in mesh]


def rotate_z(mesh, angle_deg):
    a = math.radians(angle_deg); ca,sa = math.cos(a),math.sin(a)
    return [tuple((p[0]*ca-p[1]*sa,p[0]*sa+p[1]*ca,p[2]) for p in tri) for tri in mesh]


def planform_plate(sections, z0, z1):
    """Closed symmetric floor plate from (x, half-width) planform stations."""
    outline = [(x,-w) for x,w in sections] + [(x,w) for x,w in reversed(sections)]
    n = len(outline); bottom=[(x,y,z0) for x,y in outline]; top=[(x,y,z1) for x,y in outline]
    cb = (sum(x for x,y in outline)/n,sum(y for x,y in outline)/n,z0)
    ct = (cb[0],cb[1],z1); m=[]
    for i in range(n):
        j=(i+1)%n
        m += [(bottom[i],bottom[j],top[j]),(bottom[i],top[j],top[i]),
              (cb,bottom[j],bottom[i]),(ct,top[i],top[j])]
    return m


def ramp_slab(x0,x1,y0,y1,z0,z1,thickness=1.2):
    v=[(x0,y0,z0),(x0,y1,z0),(x1,y1,z1),(x1,y0,z1),
       (x0,y0,z0+thickness),(x0,y1,z0+thickness),(x1,y1,z1+thickness),(x1,y0,z1+thickness)]
    f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
       (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return [(v[a],v[b],v[c]) for a,b,c in f]


def naca0012(chord, span, cx, cy, cz, angle_deg=0, n=24):
    pts=[]
    for i in range(n+1):
        x=(1-math.cos(math.pi*i/n))/2
        yt=5*.12*(.2969*math.sqrt(max(x,1e-9))-.126*x-.3516*x*x+.2843*x**3-.1015*x**4)
        pts.append((x,yt))
    profile=pts[::-1]+[(x,-z) for x,z in pts[1:-1]]
    a=math.radians(angle_deg); rings=[]
    for y in (cy-span/2,cy+span/2):
        ring=[]
        for x,z in profile:
            xx=(x-.5)*chord; zz=z*chord
            ring.append((cx+xx*math.cos(a)+zz*math.sin(a),y,
                         cz-xx*math.sin(a)+zz*math.cos(a)))
        rings.append(ring)
    m=[]; nn=len(profile)
    for i in range(nn):
        j=(i+1)%nn
        m += [(rings[0][i],rings[0][j],rings[1][j]),(rings[0][i],rings[1][j],rings[1][i])]
    for ring,rev in ((rings[0],True),(rings[1],False)):
        c=(sum(p[0] for p in ring)/nn,ring[0][1],sum(p[2] for p in ring)/nn)
        for i in range(nn):
            j=(i+1)%nn
            m += [(c,ring[j],ring[i])] if rev else [(c,ring[i],ring[j])]
    return m


def bounds(mesh):
    pts=[p for t in mesh for p in t]
    lo=[min(p[i] for p in pts) for i in range(3)]
    hi=[max(p[i] for p in pts) for i in range(3)]
    return lo,hi,[hi[i]-lo[i] for i in range(3)]


def normal(a,b,c):
    u=(b[0]-a[0],b[1]-a[1],b[2]-a[2]); v=(c[0]-a[0],c[1]-a[1],c[2]-a[2])
    q=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    ll=math.sqrt(sum(x*x for x in q))
    return (0.,0.,0.) if ll < 1e-14 else tuple(x/ll for x in q)


def write_stl(path, mesh, title):
    with open(path,"wb") as f:
        f.write(title.encode("ascii","ignore")[:80].ljust(80,b" "))
        f.write(struct.pack("<I",len(mesh)))
        for a,b,c in mesh:
            f.write(struct.pack("<12fH",*normal(a,b,c),*a,*b,*c,0))


def audit(mesh, tol=1e-5):
    vmap={}; edges=collections.Counter(); deg=0
    def vid(p):
        key=tuple(int(round(float(x)/tol)) for x in p)
        if key not in vmap: vmap[key]=len(vmap)
        return vmap[key]
    for tri in mesh:
        ids=tuple(vid(p) for p in tri)
        if len(set(ids))<3 or normal(*tri)==(0.,0.,0.): deg+=1
        for e in ((ids[0],ids[1]),(ids[1],ids[2]),(ids[2],ids[0])):
            edges[tuple(sorted(e))]+=1
    return {"triangles":len(mesh),"vertices":len(vmap),
            "boundary_edges":sum(v==1 for v in edges.values()),
            "nonmanifold_edges":sum(v>2 for v in edges.values()),
            "degenerate_triangles":deg}


# ---------------------------------------------------------------------------
# Printable systems, all dimensioned for the 203.2 mm overall envelope.
# ---------------------------------------------------------------------------

# Reinforced upper body approximation: W11-like narrow nose, monocoque cover,
# deep sidepods, airbox/engine cover, floor-edge shoulders and static details.
upper_body = loft([
    (-74,4.2,9.5,7.5),(-62,6.5,12.5,9.0),(-47,9.5,19.5,13.0),
    (-31,13.0,27.0,16.5),(-12,14.5,33.0,18.0),(10,13.8,34.5,18.0),
    (31,12.8,31.0,17.0),(52,11.0,27.0,15.0),(70,7.0,20.0,12.0),(79,3.8,13.5,9.0)
], n_y=18, bottom=5.6)
upper_body += box(-56,0,13.2,28,5.0,4.0)  # nose strength spine
for s in (-1,1):
    side = loft([(-34,5.5,16.0,12.0),(-22,8.5,21.0,13.5),(0,9.0,24.0,14.0),
                 (27,8.2,21.0,13.0),(52,5.0,16.0,11.0),(67,2.5,11.0,8.0)],
                n_y=12,bottom=5.2)
    upper_body += translate(side,0,s*17.0,0)
    upper_body += tube(-25,s*23.0,15.5,4.0,2.0,3.0,"x",28)
    for x in (16,23,30,37):
        upper_body += box(x,s*23.5,21.5,3.8,1.2,5.5)
upper_body += loft([(-8,4.0,29.0,25.0),(3,5.5,38.0,28.0),(17,5.0,37.0,27.0),
                    (42,3.0,31.0,23.0),(66,1.2,22.0,17.0)],n_y=10,bottom=18.0)
upper_body += box(39,0,28.0,45,1.4,13.0)  # shark fin

# Removable nose/crash box gives a cleaner split and protects the wing.
nose = loft([(-91,2.2,7.0,5.8),(-84,3.0,8.0,6.2),(-75,4.5,10.0,7.5),
             (-66,6.2,13.0,9.0),(-58,7.2,15.0,10.0)],n_y=12,bottom=4.7)
nose += box(-58,0,8.0,4.0,12.0,5.5)
for y in (-4.1,4.1): nose += cyl(-57.5,y,11.0,1.15,3.4,"x",20)

# Cockpit insert and static halo. Static means no active wing linkages/animation.
cockpit = box(-4,0,15.5,31,17,3.0)+box(8,0,23.0,7.0,15.0,14.0)
cockpit += box(-18,0,23.0,3.0,18.0,9.0)+cyl(-13.5,0,27.0,4.2,2.0,"x",28)
cockpit += beam((-15,-5,27),(-15,5,27),1.0,14)
halo = beam((-17,-11.5,28),(-12,-4.2,39.0),1.5,18)+beam((-17,11.5,28),(-12,4.2,39.0),1.5,18)
halo += beam((-12,-4.2,39),(19,-4.2,35.0),1.5,18)+beam((-12,4.2,39),(19,4.2,35.0),1.5,18)
halo += beam((19,-4.2,35),(23,0,27.5),1.5,18)+beam((19,4.2,35),(23,0,27.5),1.5,18)
halo += box(-8,0,40.0,8.0,5.0,2.2)

# Static multi-element wings, thick enough for typical 0.4 mm FDM nozzles.
front_wing = naca0012(11.0,72.0,-96.0,0,5.2,3.0,26)
front_wing += naca0012(9.0,65.0,-91.0,0,8.5,8.0,24)
front_wing += naca0012(7.0,55.0,-86.5,0,11.5,13.0,22)
for s in (-1,1):
    front_wing += box(-93.0,s*35.4,10.0,19.0,1.5,15.0)
    front_wing += beam((-96,s*4.5,6.0),(-75,s*4.5,12.0),1.0,14)
# Align the extreme leading edge to X=-101.6 mm.
front_wing = translate(front_wing,.9,0,0)

rear_wing = naca0012(13.0,55.0,94.0,0,32.5,10.0,26)
rear_wing += naca0012(9.0,51.0,98.0,0,37.0,18.0,24)
for s in (-1,1):
    rear_wing += box(96.0,s*27.8,33.0,20.0,1.6,16.0)
    rear_wing += beam((73,s*8.0,19.0),(94,s*10.0,31.0),1.3,16)
# Align the extreme trailing edge to X=+101.6 mm. Together with the front wing
# this fixes the assembled printable envelope at exactly 203.2 mm / 8.00 in.
rear_wing = translate(rear_wing,-4.4,0,0)

# V6-derived twin Venturi architecture, scaled and strengthened for printing.
floor_base = planform_plate([(-73,17),(-59,23),(-36,26),(35,26),(63,24),(87,16)],3.5,4.9)
floor_edges=[]
for s in (-1,1):
    floor_edges += beam((-58,s*24.0,5.0),(57,s*25.5,6.0),1.1,14)
    floor_edges += beam((57,s*25.5,6.0),(86,s*17.0,10.0),1.1,14)
left_tunnel=[]; right_tunnel=[]
for s,target in ((-1,left_tunnel),(1,right_tunnel)):
    y0,y1=(-22,-6) if s<0 else (6,22)
    target += ramp_slab(-64,-34,y0,y1,5.2,2.2,1.2)
    target += ramp_slab(-34,35,y0,y1,2.2,2.5,1.2)
    target += ramp_slab(35,63,y0,y1,2.5,5.7,1.2)
    target += ramp_slab(63,88,y0,y1,5.7,10.5,1.2)
    # Inlet and tunnel fences, integrated and static.
    for yy in (7.5,12.5,17.5,21.5):
        y=s*yy
        target += beam((-63,y,3.1),(-38,y+s*1.5,5.3),0.75,12)
diffuser=[]
for y in (-21,-14,-7,7,14,21):
    diffuser += ramp_slab(45,89,y-.55,y+.55,3.5,13.0,1.1)
for s in (-1,1):
    for x in (48,58,68,78): diffuser += beam((x,s*25.0,5.8),(x+8,s*28.5,8.5),0.7,12)
plank = box(7,0,2.6,148,7.0,1.3)
for x in (-47,-10,27,64): plank += box(x,0,1.65,13,5.2,.6)
venturi_floor = floor_base + floor_edges + left_tunnel + right_tunnel + diffuser + plank

# Open structural chassis: lower keel, side-impact rails, bulkheads and hoops.
chassis=[]
chassis += box(2,0,7.2,129,9.0,3.0)
for s in (-1,1):
    chassis += beam((-51,s*8.0,9.0),(55,s*11.5,10.0),1.35,16)
    chassis += beam((-35,s*10.0,18.0),(44,s*11.0,18.5),1.2,16)
    chassis += beam((-51,s*8.0,9.0),(-35,s*10.0,18.0),1.2,16)
    chassis += beam((55,s*11.5,10.0),(44,s*11.0,18.5),1.2,16)
for x,w,h in ((-51,18,14),(-32,24,20),(-5,25,22),(23,24,21),(50,20,16)):
    chassis += box(x,0,9.0,2.0,w,3.0)
    chassis += beam((x,-w/2,9.0),(x,-w/2+2.0,h),1.0,14)
    chassis += beam((x,w/2,9.0),(x,w/2-2.0,h),1.0,14)
    chassis += beam((x,-w/2+2.0,h),(x,w/2-2.0,h),1.0,14)
chassis += box(-64,0,8.5,23,8.0,6.0)+box(67,0,9.0,29,16,6.0)
for x in (-30,0,30): chassis += box(x,0,8.0,2.0,26,3.0)

# EV energy store and rear drive systems.
battery = box(1,0,7.0,75,21,3.8)
for x in (-27,-9,9,27):
    for y in (-6.5,6.5): battery += box(x,y,10.0,15,6.5,2.0)
battery += box(1,0,11.7,67,2.0,1.5)
rear_motor = cyl(58,0,13.0,6.7,17.0,"x",40)+cyl(67.5,0,13.0,8.0,5.0,"x",40)
for x in (52.5,55.5,58.5,61.5,64.5): rear_motor += tube(x,0,13.0,7.3,6.6,.8,"x",30)
rear_motor += box(73,0,13.0,6.0,14.0,12.0)
inverter = box(42,0,18.0,21,15,6.0)
for x in (35,39,43,47,51): inverter += box(x,0,21.5,1.0,13,1.0)
for y in (-5.5,5.5): inverter += cyl(31.5,y,18.0,1.5,3.0,"x",18)


def suspension_module(front=True):
    m=[]; outer=27.3; inner=12.5
    for s in (-1,1):
        y=s*outer
        for z,r in ((9.0,1.05),(18.5,.95)):
            m += beam((-7,s*inner,z),(0,y,13.5),r,14)
            m += beam((7,s*inner,z),(0,y,13.5),r,14)
        m += beam((0,y,7.0),(0,y,20.5),1.25,16)
        m += beam((0,y,18.0),(7,s*7.0,25.0),.95,14)
        m += beam((-4,s*inner,12.0),(0,y,12.0),.8,12)
        if front:
            m += beam((-5,s*inner,15.0),(0,y,15.5),.75,12)
    m += box(0,0,7.0,17,27,2.2)
    m += beam((7,-7,25),(17,-3.5,18),1.15,14)+beam((7,7,25),(17,3.5,18),1.15,14)
    if front:
        m += beam((-3,-27.3,14.2),(-3,27.3,14.2),.65,12)
        m += box(-3,0,14.2,7.0,8.0,2.0)
    else:
        for s in (-1,1): m += cyl(0,s*25.0,13.5,3.4,3.0,"y",24)
    return m


front_susp = suspension_module(True)
rear_susp = suspension_module(False)


def wheel():
    m=tube(0,0,0,12.8,9.1,10.6,"y",56)
    m+=tube(0,0,0,9.1,1.25,7.6,"y",44)
    for k in range(10):
        a=2*math.pi*k/10
        m += beam((2.0*math.cos(a),-3.6,2.0*math.sin(a)),
                  (8.1*math.cos(a+.11),-3.6,8.1*math.sin(a+.11)),.55,10)
    for yy in (-4.7,4.7): m += tube(0,yy,0,12.95,12.45,.55,"y",48)
    return m


wheel_mesh = wheel()
axle_pin = cyl(0,0,0,1.0,11.5,"y",28)
wheel_cap = cyl(0,0,0,2.2,1.4,"y",28)+cyl(0,.9,0,.92,2.0,"y",24)


# Part list: file stem, display name, geometry at its own assembly origin,
# assembly translation, material, print quantity.
PARTS = [
    ("01_reinforced_upper_body", "Reinforced upper body", upper_body, (0,0,0), "White body", 1),
    ("02_removable_nose_crashbox", "Removable nose and crash box", nose, (0,0,0), "White body", 1),
    ("03_cockpit_insert", "Cockpit insert", cockpit, (0,0,0), "Cockpit", 1),
    ("04_static_halo", "Static halo", halo, (0,0,0), "Black carbon", 1),
    ("05_static_front_wing", "Static multi-element front wing", front_wing, (0,0,0), "Black carbon", 1),
    ("06_static_rear_wing", "Static rear wing", rear_wing, (0,0,0), "Black carbon", 1),
    ("07_twin_venturi_floor", "Twin Venturi floor and diffuser", venturi_floor, (0,0,0), "Black carbon", 1),
    ("08_structural_ev_chassis", "Structural EV chassis", chassis, (0,0,0), "Aluminum", 1),
    ("09_low_energy_store", "Low energy store", battery, (0,0,0), "Battery", 1),
    ("10_rear_motor_gearbox", "Rear motor and gearbox", rear_motor, (0,0,0), "HV orange", 1),
    ("11_inverter_controller", "Inverter and controller", inverter, (0,0,0), "Electronics", 1),
    ("12_front_static_suspension", "Front static suspension and steering rack", front_susp, (-53.6,0,0), "Aluminum", 1),
    ("13_rear_static_suspension", "Rear static suspension", rear_susp, (76.2,0,0), "Aluminum", 1),
    ("14_rolling_wheel_x4", "Rolling wheel", wheel_mesh, (0,0,0), "Tire", 4),
    ("15_axle_pin_x4", "Axle pin", axle_pin, (0,0,0), "Aluminum", 4),
    ("16_wheel_retainer_x4", "Wheel retainer", wheel_cap, (0,0,0), "Accent", 4),
]

ASSEMBLY_INSTANCES=[]
for stem,name,mesh,tr,mat,qty in PARTS:
    if stem == "14_rolling_wheel_x4":
        for x in (-53.6,76.2):
            for y in (-30.5,30.5): ASSEMBLY_INSTANCES.append((name,mesh,(x,y,14.0),mat))
    elif stem == "15_axle_pin_x4":
        for x in (-53.6,76.2):
            for y in (-28.7,28.7): ASSEMBLY_INSTANCES.append((name,mesh,(x,y,14.0),mat))
    elif stem == "16_wheel_retainer_x4":
        for x in (-53.6,76.2):
            for y in (-36.1,36.1): ASSEMBLY_INSTANCES.append((name,mesh,(x,y,14.0),mat))
    else:
        ASSEMBLY_INSTANCES.append((name,mesh,tr,mat))


# Visual underfloor components remain individually selectable in the reference GLB.
SYSTEM_INSTANCES = [
    ("V6 floor base",floor_base,(0,0,0),"Black carbon"),
    ("Left Venturi tunnel",left_tunnel,(0,0,0),"Tunnel blue"),
    ("Right Venturi tunnel",right_tunnel,(0,0,0),"Tunnel blue"),
    ("Floor edge sealing structures",floor_edges,(0,0,0),"Black carbon"),
    ("Progressive diffuser and strakes",diffuser,(0,0,0),"Tunnel blue"),
    ("Central plank and skid blocks",plank,(0,0,0),"Plank"),
    ("Structural EV chassis",chassis,(0,0,0),"Aluminum"),
    ("Low energy store",battery,(0,0,0),"Battery"),
    ("Rear motor and gearbox",rear_motor,(0,0,0),"HV orange"),
    ("Inverter controller",inverter,(0,0,0),"Electronics"),
    ("Front static suspension",front_susp,(-53.6,0,0),"Aluminum"),
    ("Rear static suspension",rear_susp,(76.2,0,0),"Aluminum"),
]


COLORS = {
    "White body": (0.96,0.97,0.98,1.0),
    "Black carbon": (0.025,0.035,0.050,1.0),
    "Tunnel blue": (0.04,0.32,0.52,1.0),
    "Plank": (0.56,0.37,0.18,1.0),
    "Aluminum": (0.62,0.68,0.74,1.0),
    "Battery": (0.04,0.24,0.64,1.0),
    "HV orange": (0.96,0.26,0.02,1.0),
    "Electronics": (0.20,0.25,0.31,1.0),
    "Cockpit": (0.05,0.07,0.10,1.0),
    "Tire": (0.012,0.012,0.015,1.0),
    "Accent": (0.80,0.04,0.04,1.0),
}


# ---------------------------------------------------------------------------
# GLB writers. Procedural coordinates convert to glTF Y-up world coordinates.
# ---------------------------------------------------------------------------

def indexed(mesh, transform=(0,0,0)):
    tx,ty,tz=transform; d={}; verts=[]; inds=[]
    for tri in mesh:
        for p in tri:
            # Print X/Y/Z -> glTF world X/Y/Z = lateral/up/front, metres.
            q=((p[1]+ty)/1000.0,(p[2]+tz)/1000.0,-(p[0]+tx)/1000.0)
            key=tuple(round(x,9) for x in q)
            if key not in d: d[key]=len(verts); verts.append(q)
            inds.append(d[key])
    return verts,inds


def _append_instances(doc, binbuf, instances, generator_note=""):
    doc.setdefault("bufferViews",[]); doc.setdefault("accessors",[])
    doc.setdefault("meshes",[]); doc.setdefault("materials",[]); doc.setdefault("nodes",[])
    def align():
        while len(binbuf)%4: binbuf.append(0)
    def view(data,target):
        align(); off=len(binbuf); binbuf.extend(data)
        doc["bufferViews"].append({"buffer":0,"byteOffset":off,"byteLength":len(data),"target":target})
        return len(doc["bufferViews"])-1
    mi={m.get("name"):i for i,m in enumerate(doc["materials"])}
    for mat,color in COLORS.items():
        if mat in mi: continue
        mi[mat]=len(doc["materials"])
        metallic=.72 if mat=="Aluminum" else .08
        rough=.26 if mat in ("White body","Aluminum") else .48
        doc["materials"].append({"name":mat,"pbrMetallicRoughness":{
            "baseColorFactor":list(color),"metallicFactor":metallic,"roughnessFactor":rough},
            "doubleSided":True})
    added=[]
    for name,mesh,tr,mat in instances:
        verts,inds=indexed(mesh,tr)
        pv=view(b"".join(struct.pack("<3f",*p) for p in verts),34962)
        iv=view(b"".join(struct.pack("<I",i) for i in inds),34963)
        mn=[min(p[k] for p in verts) for k in range(3)]; mx=[max(p[k] for p in verts) for k in range(3)]
        pa=len(doc["accessors"]); doc["accessors"].append({"bufferView":pv,"componentType":5126,
            "count":len(verts),"type":"VEC3","min":mn,"max":mx})
        ia=len(doc["accessors"]); doc["accessors"].append({"bufferView":iv,"componentType":5125,
            "count":len(inds),"type":"SCALAR","min":[min(inds)],"max":[max(inds)]})
        mesh_id=len(doc["meshes"]); doc["meshes"].append({"name":name,"primitives":[{
            "attributes":{"POSITION":pa},"indices":ia,"material":mi[mat]}]})
        node_id=len(doc["nodes"]); doc["nodes"].append({"name":name,"mesh":mesh_id})
        added.append(node_id)
    doc["asset"]["generator"]=(doc["asset"].get("generator","")+"; "+generator_note).strip("; ")
    return added


def write_glb(path, instances, title):
    doc={"asset":{"version":"2.0","generator":"W11 V6 static printable hybrid"},
         "scene":0,"scenes":[{"name":title,"nodes":[]}],"nodes":[],"meshes":[],"materials":[],
         "buffers":[{"byteLength":0}],"bufferViews":[],"accessors":[],
         "extras":{"units":"metres","printDesignUnits":"millimetres","overallTargetLength_mm":203.2,
                   "configuration":"static"}}
    binbuf=bytearray(); ids=_append_instances(doc,binbuf,instances,title); doc["scenes"][0]["nodes"]=ids
    _finish_glb(path,doc,binbuf)


def _read_glb(path):
    raw=open(path,"rb").read(); magic,ver,total=struct.unpack_from("<4sII",raw,0)
    if magic!=b"glTF" or ver!=2: raise ValueError("Expected GLB 2.0")
    jl,jt=struct.unpack_from("<I4s",raw,12); doc=json.loads(raw[20:20+jl])
    off=20+jl; bl,bt=struct.unpack_from("<I4s",raw,off)
    return doc,bytearray(raw[off+8:off+8+bl])


def _finish_glb(path,doc,binbuf):
    while len(binbuf)%4: binbuf.append(0)
    doc["buffers"][0]["byteLength"]=len(binbuf)
    js=json.dumps(doc,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    js += b" "*((4-len(js)%4)%4); bb=bytes(binbuf)
    total=12+8+len(js)+8+len(bb)
    with open(path,"wb") as f:
        f.write(struct.pack("<4sII",b"glTF",2,total)); f.write(struct.pack("<I4s",len(js),b"JSON")); f.write(js)
        f.write(struct.pack("<I4s",len(bb),b"BIN\0")); f.write(bb)


def write_augmented_reference(path, additions, exploded=False):
    doc,binbuf=_read_glb(REFERENCE)
    # Original is 5.699470996 m long. Scale to 203.2 mm and center longitudinally.
    scale=.2032/5.699470996
    original_scene_nodes=list(doc["scenes"][doc.get("scene",0)]["nodes"])
    for node_id in original_scene_nodes:
        node=doc["nodes"][node_id]
        node["scale"]=[scale,scale,scale]
        tr=list(node.get("translation",[0,0,0])); tr[2]+=0.004705
        if exploded: tr[1]+=0.052
        node["translation"]=tr
        node["name"]="Mercedes W11 exterior reference" if not exploded else "Mercedes W11 exterior reference - lifted"
    if exploded:
        expanded=[]
        for name,mesh,tr,mat in additions:
            dx,dy,dz=tr
            if "floor" in name.lower() or "tunnel" in name.lower() or "diffuser" in name.lower() or "plank" in name.lower(): dz-=13
            elif "battery" in name.lower(): dy-=32
            elif "motor" in name.lower() or "inverter" in name.lower(): dy+=30
            expanded.append((name,mesh,(dx,dy,dz),mat))
        additions=expanded
    ids=_append_instances(doc,binbuf,additions,"8-inch static V6 floor and EV chassis integration")
    doc["scenes"][doc.get("scene",0)]["nodes"].extend(ids)
    doc["extras"]={"project":"W11 V6 static 8-inch hybrid","referenceScale":scale,
                   "configuration":"static","note":"Exterior reference plus printable V6-derived systems"}
    _finish_glb(path,doc,binbuf)


# ---------------------------------------------------------------------------
# 3MF writer and a compact single-bed layout.
# ---------------------------------------------------------------------------

def mesh_for_bed(mesh, rotated=False):
    m=rotate_z(mesh,90) if rotated else list(mesh)
    lo,hi,sz=bounds(m)
    return translate(m,-lo[0],-lo[1],-lo[2]),sz


def maxrect_pack(entries, bed=220.0, edge=3.0, gap=2.2):
    """Small best-short-side-fit packer. entries: (label, mesh, material)."""
    free=[(edge,edge,bed-2*edge,bed-2*edge)]; placed=[]
    items=[]
    for label,mesh,mat in entries:
        _,_,sz=bounds(mesh); items.append((max(sz[0],sz[1]),sz[0]*sz[1],label,mesh,mat,sz))
    items.sort(reverse=True)
    for _,__,label,mesh,mat,sz in items:
        best=None
        for fi,(fx,fy,fw,fh) in enumerate(free):
            for rot,(w,h) in enumerate(((sz[0]+gap,sz[1]+gap),(sz[1]+gap,sz[0]+gap))):
                if w<=fw+1e-9 and h<=fh+1e-9:
                    score=(min(fw-w,fh-h),max(fw-w,fh-h),fi,rot)
                    if best is None or score<best[0]: best=(score,fx,fy,w,h)
        if best is None: return None
        (_,_,fi,rot),x,y,w,h=best; fx,fy,fw,fh=free.pop(fi)
        placed.append((label,mesh,mat,x+gap/2,y+gap/2,bool(rot)))
        # Guillotine split along the longer leftover dimension.
        rw,rh=fw-w,fh-h
        if rw>rh:
            if rw>0: free.append((fx+w,fy,rw,fh))
            if rh>0: free.append((fx,fy+h,w,rh))
        else:
            if rh>0: free.append((fx,fy+h,fw,rh))
            if rw>0: free.append((fx+w,fy,rw,h))
        # Drop contained free rectangles.
        clean=[]
        for i,r in enumerate(free):
            if not any(i!=j and r[0]>=q[0] and r[1]>=q[1] and r[0]+r[2]<=q[0]+q[2] and r[1]+r[3]<=q[1]+q[3]
                       for j,q in enumerate(free)): clean.append(r)
        free=clean
    return placed


def vf(mesh):
    d={};v=[];f=[]
    for tri in mesh:
        ids=[]
        for p in tri:
            key=tuple(round(float(x),5) for x in p)
            if key not in d: d[key]=len(v);v.append(key)
            ids.append(d[key])
        f.append(ids)
    return v,f


def write_3mf(path, placed, title):
    mats=list(COLORS); mi={n:i for i,n in enumerate(mats)}
    matxml='<m:basematerials id="900">'+''.join(
        f'<m:base name="{escape(n)}" displaycolor="#{int(COLORS[n][0]*255):02X}{int(COLORS[n][1]*255):02X}{int(COLORS[n][2]*255):02X}FF"/>'
        for n in mats)+'</m:basematerials>'
    objects=[];build=[]
    for oid,(name,mesh,mat,x,y,rot) in enumerate(placed,1):
        mm,sz=mesh_for_bed(mesh,rot); mm=translate(mm,x,y,0)
        v,f=vf(mm)
        vs=''.join(f'<vertex x="{a:.5f}" y="{b:.5f}" z="{c:.5f}"/>' for a,b,c in v)
        fs=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in f)
        objects.append(f'<object id="{oid}" name="{escape(name)}" type="model" pid="900" pindex="{mi[mat]}"><mesh><vertices>{vs}</vertices><triangles>{fs}</triangles></mesh></object>')
        build.append(f'<item objectid="{oid}"/>')
    model=('<?xml version="1.0" encoding="UTF-8"?>'
           '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
           'xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02" requiredextensions="m">'
           f'<metadata name="Title">{escape(title)}</metadata><metadata name="Description">Static 8-inch W11/V6 hybrid print kit; all dimensions are millimetres.</metadata>'
           '<resources>'+matxml+''.join(objects)+'</resources><build>'+''.join(build)+'</build></model>')
    rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    ct='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",ct);z.writestr("_rels/.rels",rels);z.writestr("3D/3dmodel.model",model)
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None: raise RuntimeError("3MF verification failed")


# ---------------------------------------------------------------------------
# Deliverables.
# ---------------------------------------------------------------------------

validation=[]
for stem,name,mesh,tr,mat,qty in PARTS:
    stl=os.path.join(STL_DIR,stem+".stl"); write_stl(stl,mesh,name)
    write_glb(os.path.join(GLB_DIR,stem+".glb"),[(name,mesh,(0,0,0),mat)],name)
    au=audit(mesh); lo,hi,sz=bounds(mesh)
    validation.append((stem,name,qty,sz,au,os.path.getsize(stl)))
    if au["boundary_edges"] or au["degenerate_triangles"]:
        raise RuntimeError(f"Open or degenerate geometry in {stem}: {au}")

# Fully procedural print assemblies.
write_glb(os.path.join(OUT,"W11_V6_PRINTABLE_ASSEMBLED.glb"),ASSEMBLY_INSTANCES,"W11 V6 printable assembled")
exploded=[]
for i,(name,mesh,tr,mat) in enumerate(ASSEMBLY_INSTANCES):
    x,y,z=tr
    if "body" in name.lower(): z+=42
    elif "nose" in name.lower(): x-=22;z+=20
    elif "wing" in name.lower(): z+=22
    elif "floor" in name.lower(): z-=10
    elif "battery" in name.lower(): y-=35
    elif "motor" in name.lower() or "inverter" in name.lower(): y+=34
    elif "wheel" in name.lower() or "retainer" in name.lower(): y += (-18 if y<0 else 18)
    exploded.append((name,mesh,(x,y,z),mat))
write_glb(os.path.join(OUT,"W11_V6_PRINTABLE_EXPLODED.glb"),exploded,"W11 V6 printable exploded")
write_glb(os.path.join(OUT,"W11_V6_CHASSIS_ONLY.glb"),[
    ("Structural EV chassis",chassis,(0,0,0),"Aluminum"),("Low energy store",battery,(0,0,0),"Battery"),
    ("Rear motor and gearbox",rear_motor,(0,0,0),"HV orange"),("Inverter controller",inverter,(0,0,0),"Electronics"),
    ("Front suspension",front_susp,(-53.6,0,0),"Aluminum"),("Rear suspension",rear_susp,(76.2,0,0),"Aluminum")],"W11 V6 chassis only")
write_glb(os.path.join(OUT,"W11_V6_VENTURI_FLOOR_ONLY.glb"),SYSTEM_INSTANCES[:6],"W11 V6 Venturi floor only")

# High-detail supplied exterior reference with integrated systems.
write_augmented_reference(os.path.join(OUT,"W11_REFERENCE_V6_SYSTEMS_ASSEMBLED.glb"),SYSTEM_INSTANCES,False)
write_augmented_reference(os.path.join(OUT,"W11_REFERENCE_V6_SYSTEMS_EXPLODED.glb"),SYSTEM_INSTANCES,True)

# Reference assembled STL of printable geometry (not the preferred one-piece print).
assembled=[]
for name,mesh,tr,mat in ASSEMBLY_INSTANCES: assembled += translate(mesh,*tr)
write_stl(os.path.join(OUT,"W11_V6_PRINTABLE_ASSEMBLED_REFERENCE.stl"),assembled,"W11 V6 PRINTABLE ASSEMBLED REFERENCE")

# Physical print list and compact 220 x 220 layout.
physical=[]
for stem,name,mesh,tr,mat,qty in PARTS:
    for i in range(qty): physical.append((f"{name} {i+1}" if qty>1 else name,mesh,mat))
packed=maxrect_pack(physical)
if packed is None:
    raise RuntimeError("All parts did not fit the 220 x 220 mm plate")
write_3mf(os.path.join(OUT,"W11_V6_ALL_PRINT_PARTS_220MM_PLATE.3mf"),packed,"W11 V6 static 8-inch complete print kit")

# Human-readable documentation.
source_sha=hashlib.sha256(open(REFERENCE,"rb").read()).hexdigest()
readme=f"""# W11 / V6 STATIC 8-INCH HYBRID

This package combines the supplied high-detail 2020 Mercedes-style exterior reference with a newly built, printable V6-derived twin-Venturi floor and a complete educational EV chassis. The design is **static**: there are no DRS or active-front-wing animations. The four printed wheels can rotate on separate axle pins.

## Start here

- `W11_REFERENCE_V6_SYSTEMS_ASSEMBLED.glb` — best high-detail exterior view with named floor/chassis systems.
- `W11_REFERENCE_V6_SYSTEMS_EXPLODED.glb` — exterior lifted so the chassis and floor are easy to inspect.
- `W11_V6_PRINTABLE_ASSEMBLED.glb` — exact procedural geometry represented by the printable files.
- `W11_V6_PRINTABLE_EXPLODED.glb` — exact print parts separated for inspection.
- `W11_V6_ALL_PRINT_PARTS_220MM_PLATE.3mf` — all {sum(p[5] for p in PARTS)} physical parts arranged on one 220 x 220 mm plate; units are explicitly millimetres.
- `STL_PRINT_PARTS/` — one STL per unique part, with x4 quantities in filenames.
- `GLB_INDIVIDUAL_PARTS/` — each printable part as an individually viewable GLB.

## Finished size

Nominal overall length: **203.2 mm / 8.00 in**. Approximate assembled envelope: {bounds(assembled)[2][0]:.2f} x {bounds(assembled)[2][1]:.2f} x {bounds(assembled)[2][2]:.2f} mm. STL files do not store units, so choose **millimetres** when importing. The 3MF declares millimetres directly.

## Recommended material and settings

- Best simple choice: **PLA+** for all rigid parts.
- Optional upgrade: **PETG** for axle pins, retainers and suspension; **TPU 95A** for the four wheels.
- 0.4 mm nozzle; 0.16-0.20 mm layers; 3-4 walls; 18-25% gyroid infill.
- Use tree/build-plate supports for the body, halo, wings and suspension.
- Print the floor with its broad upper face on the bed so the Venturi channels face upward; rotate after slicing only if your support preview is cleaner.

## Assembly order

1. Fit the low energy store, motor and inverter into the structural chassis.
2. Attach the chassis to the upper face of the twin-Venturi floor. Keep the floor removable if you want the tunnels visible.
3. Attach front and rear suspension at the marked axle stations, approximately X=-53.6 mm and X=+76.2 mm.
4. Glue axle pins into the uprights. Slide on wheels; glue retainers only to the pin tips. Leave about 0.25-0.35 mm lateral play.
5. Fit cockpit insert and halo to the upper body, then attach the removable nose.
6. Place the upper body over the chassis. Attach the static front and rear wings last.

## What is and is not copied

The supplied GLB is retained as the detailed visual exterior in the two `W11_REFERENCE...` files. It is a rendering mesh rather than watertight CAD. The printable body is therefore a strengthened, simplified derivative matched to the reference silhouette; it is not a direct raw conversion of the fragile source mesh. The V6 tunnel/plank/diffuser architecture is newly rebuilt for this 8-inch model and is not validated CFD or structural engineering.

## Reference credit

Original Sketchfab model: `mercedec f1 2020` by Kevin Love SketchFab / Tyler_Kevin, licensed CC BY 4.0: https://sketchfab.com/3d-models/mercedec-f1-2020-0d97207d829441ba95952598f84e8d63

Source GLB SHA-256: `{source_sha}`
"""
open(os.path.join(OUT,"README.md"),"w").write(readme)

with open(os.path.join(OUT,"PARTS_MANIFEST.csv"),"w") as f:
    f.write("file,part,quantity,length_mm,width_mm,height_mm,material\n")
    for stem,name,mesh,tr,mat,qty in PARTS:
        sz=bounds(mesh)[2]
        f.write(f"STL_PRINT_PARTS/{stem}.stl,{name},{qty},{sz[0]:.3f},{sz[1]:.3f},{sz[2]:.3f},{mat}\n")

with open(os.path.join(OUT,"MESH_VALIDATION.txt"),"w") as f:
    f.write("W11 V6 STATIC 8-INCH PRINT MESH VALIDATION\n\n")
    f.write("Acceptance for unique STL parts: zero boundary edges and zero degenerate triangles.\n")
    f.write("Multiple closed shells and deliberate intersections are retained where slicers should union reinforced features.\n\n")
    for stem,name,qty,sz,au,size in validation:
        f.write(f"{stem} | qty {qty} | {sz[0]:.3f} x {sz[1]:.3f} x {sz[2]:.3f} mm | {au} | {size} bytes\n")
    f.write(f"\nAssembled printable envelope: {bounds(assembled)[2]} mm\n")
    f.write(f"Packed 3MF objects: {len(packed)} on 220 x 220 mm bed\n")

license_text="""REFERENCE MODEL ATTRIBUTION\n\nTitle: mercedec f1 2020\nCreator: Kevin Love SketchFab / Tyler_Kevin\nSource: https://sketchfab.com/3d-models/mercedec-f1-2020-0d97207d829441ba95952598f84e8d63\nLicense: Creative Commons Attribution 4.0 International (CC BY 4.0)\nLicense URL: https://creativecommons.org/licenses/by/4.0/\n\nThe original visual asset is included only inside the W11_REFERENCE... GLB derivatives. Newly generated printable engineering-study geometry is separately identified in this package.\n"""
open(os.path.join(OUT,"REFERENCE_LICENSE_AND_ATTRIBUTION.txt"),"w").write(license_text)

# Lightweight visual guide that opens in any browser without a 3D engine.
svg='''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="820" viewBox="0 0 1400 820">
<rect width="1400" height="820" fill="#eef2f5"/><style>.t{font:700 28px Arial;fill:#15202b}.s{font:18px Arial;fill:#334}.l{stroke:#18384f;stroke-width:3;fill:none}.b{fill:#f9fbfc;stroke:#273845;stroke-width:3}.c{fill:#09131c;stroke:#1c4058;stroke-width:2}.u{fill:#087aa5;opacity:.8;stroke:#034c68;stroke-width:2}.m{fill:#f37021;stroke:#8b3510;stroke-width:2}.a{fill:#aab5bf;stroke:#4b5964;stroke-width:2}</style>
<text x="50" y="55" class="t">W11 / V6 STATIC 8-INCH HYBRID</text><text x="50" y="88" class="s">High-detail reference exterior + printable Venturi floor + complete EV chassis</text>
<g transform="translate(90,155)"><text x="0" y="-25" class="t">ASSEMBLED SIDE</text><path class="b" d="M40 170 L145 145 L245 90 L470 72 L665 105 L820 142 L1000 157 L1055 175 L1000 192 L230 197 L80 188 Z"/><path class="c" d="M490 73 L560 18 L650 50 L694 112 L610 120 Z"/><rect x="140" y="186" width="790" height="18" rx="8" class="u"/><circle cx="285" cy="205" r="65" class="c"/><circle cx="850" cy="205" r="65" class="c"/><path class="l" d="M150 125 L55 112 M150 135 L55 155 M930 120 L1030 70 M935 130 L1030 115"/><text x="415" y="240" class="s">203.2 mm overall</text></g>
<g transform="translate(90,505)"><text x="0" y="-25" class="t">EXPLODED SYSTEMS</text><path class="b" d="M70 30 L230 0 L720 0 L920 35 L750 65 L200 65 Z"/><path class="a" d="M170 112 L265 82 L700 82 L820 112 L730 145 L235 145 Z"/><rect x="290" y="101" width="300" height="32" rx="8" fill="#164eb5"/><rect x="645" y="98" width="90" height="40" rx="10" class="m"/><path class="u" d="M120 192 L235 160 L760 160 L890 195 L760 235 L230 235 Z"/><path class="l" d="M285 180 L360 212 L430 180 L510 212 L585 180 M620 180 L690 222 L760 180"/><text x="955" y="55" class="s">removable upper body</text><text x="955" y="130" class="s">structural chassis + EV systems</text><text x="955" y="210" class="s">twin Venturi floor + diffuser</text></g></svg>'''
open(os.path.join(OUT,"DESIGN_OVERVIEW.svg"),"w").write(svg)

# Zip the complete folder for one-click download/sharing.
zip_path=os.path.join(ROOT,"outputs","W11_V6_HYBRID_STATIC_8IN_COMPLETE.zip")
# Store the large texture-rich reference GLBs without recompression. This is a
# little larger, but avoids platform-specific deflate failures on already-
# compressed embedded PNG data and makes the share archive more robust.
with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_STORED) as z:
    for root,dirs,files in os.walk(OUT):
        for fn in sorted(files):
            p=os.path.join(root,fn); z.write(p,os.path.join(os.path.basename(OUT),os.path.relpath(p,OUT)))
with zipfile.ZipFile(zip_path) as z:
    if z.testzip() is not None: raise RuntimeError("ZIP verification failed")

# Final GLB/header validation.
for root,dirs,files in os.walk(OUT):
    for fn in files:
        p=os.path.join(root,fn)
        if fn.endswith(".glb"):
            head=open(p,"rb").read(12); magic,ver,total=struct.unpack("<4sII",head)
            if magic!=b"glTF" or ver!=2 or total!=os.path.getsize(p): raise RuntimeError(f"Bad GLB: {p}")

print("output",OUT)
print("zip",zip_path,os.path.getsize(zip_path))
print("parts",sum(p[5] for p in PARTS),"unique",len(PARTS),"packed",len(packed))
print("assembled_mm",bounds(assembled)[2])
for row in validation: print(row[0],row[2],row[3],row[4])
