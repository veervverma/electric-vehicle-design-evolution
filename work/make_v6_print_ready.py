import os,struct,math,collections,zipfile,shutil,hashlib
from xml.sax.saxutils import escape

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.path.join(ROOT,'outputs/V6_CFD_REBUILD/V6_FULL_SCALE_CFD_SURFACES.stl')
OUT=os.path.join(ROOT,'outputs/V6_PRINT_READY_5_TO_8_INCH')
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)

# ---------- basic mesh I/O ----------
def read_stl(path):
    b=open(path,'rb').read()
    if len(b)<84: raise ValueError('Invalid STL')
    n=struct.unpack_from('<I',b,80)[0]
    if 84+50*n != len(b): raise ValueError('Expected binary STL')
    T=[]
    for i in range(n):
        o=84+50*i+12
        T.append(tuple(struct.unpack_from('<3f',b,o+12*j) for j in range(3)))
    return T

def normal(a,b,c):
    u=(b[0]-a[0],b[1]-a[1],b[2]-a[2]);v=(c[0]-a[0],c[1]-a[1],c[2]-a[2])
    q=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    L=math.sqrt(sum(x*x for x in q))
    return (0.0,0.0,0.0) if L==0 else tuple(x/L for x in q)

def write_stl(path,T,name):
    with open(path,'wb') as f:
        f.write(name.encode('ascii','ignore')[:80].ljust(80,b' '));f.write(struct.pack('<I',len(T)))
        for a,b,c in T:
            n=normal(a,b,c)
            f.write(struct.pack('<12fH',*n,*a,*b,*c,0))

def bounds(T):
    P=[p for t in T for p in t]
    lo=[min(p[i] for p in P) for i in range(3)];hi=[max(p[i] for p in P) for i in range(3)]
    return lo,hi,[hi[i]-lo[i] for i in range(3)]

# ---------- closed helper solids for hidden print reinforcement ----------
def box(cx,cy,cz,l,w,h):
    x0,x1=cx-l/2,cx+l/2;y0,y1=cy-w/2,cy+w/2;z0,z1=cz-h/2,cz+h/2
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return [(v[a],v[b],v[c]) for a,b,c in f]

def beam(a,b,r,n=16):
    ax,ay,az=a;bx,by,bz=b;dx,dy,dz=bx-ax,by-ay,bz-az;L=math.sqrt(dx*dx+dy*dy+dz*dz)
    ux,uy,uz=dx/L,dy/L,dz/L
    tx,ty,tz=(0,0,1) if abs(uz)<.9 else (0,1,0)
    vx,vy,vz=uy*tz-uz*ty,uz*tx-ux*tz,ux*ty-uy*tx;q=math.sqrt(vx*vx+vy*vy+vz*vz);vx,vy,vz=vx/q,vy/q,vz/q
    wx,wy,wz=uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx
    rings=[]
    for P in (a,b):
        rings.append([(P[0]+r*(vx*math.cos(2*math.pi*i/n)+wx*math.sin(2*math.pi*i/n)),P[1]+r*(vy*math.cos(2*math.pi*i/n)+wy*math.sin(2*math.pi*i/n)),P[2]+r*(vz*math.cos(2*math.pi*i/n)+wz*math.sin(2*math.pi*i/n))) for i in range(n)])
    M=[]
    for i in range(n):
        j=(i+1)%n;M += [(rings[0][i],rings[0][j],rings[1][j]),(rings[0][i],rings[1][j],rings[1][i])]
        # End caps use reversed edge directions relative to side wall.
        M += [(a,rings[0][j],rings[0][i]),(b,rings[1][i],rings[1][j])]
    return M

# ---------- cleanup and close open loops ----------
def clean_and_cap(T,tol=1e-4):
    # Remove collapsed and duplicate facets, while welding near-identical coordinates.
    vmap={};V=[];F=[];seen=set();removed_degenerate=removed_duplicate=0
    def vid(p):
        k=tuple(int(round(float(x)/tol)) for x in p)
        if k not in vmap:vmap[k]=len(V);V.append(tuple(float(x) for x in p))
        return vmap[k]
    for tri in T:
        ids=tuple(vid(p) for p in tri)
        a,b,c=(V[i] for i in ids)
        n=normal(a,b,c)
        if len(set(ids))<3 or n==(0.0,0.0,0.0):removed_degenerate+=1;continue
        key=tuple(sorted(ids))
        if key in seen:removed_duplicate+=1;continue
        seen.add(key);F.append(ids)
    ec=collections.Counter()
    for f in F:
        for e in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):ec[tuple(sorted(e))]+=1
    directed=[]
    for f in F:
        for e in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):
            if ec[tuple(sorted(e))]==1:directed.append(e)
    # Boundary rings from directed edges. The generated beam walls are consistently directed.
    unused=set(range(len(directed)));out=collections.defaultdict(list)
    for i,(u,v) in enumerate(directed):out[u].append(i)
    loops=[]
    while unused:
        ei=next(iter(unused));unused.remove(ei);u0,v=directed[ei];loop=[u0,v];cur=v
        guard=0
        while cur!=u0 and guard<len(directed)+2:
            guard+=1;cands=[q for q in out[cur] if q in unused]
            if not cands:break
            q=cands[0];unused.remove(q);_,nv=directed[q];loop.append(nv);cur=nv
        if len(loop)>=4 and loop[-1]==loop[0]:loops.append(loop[:-1])
    caps=0
    for loop in loops:
        pts=[V[i] for i in loop];cen=tuple(sum(p[k] for p in pts)/len(pts) for k in range(3));ci=len(V);V.append(cen)
        for i,u in enumerate(loop):
            v=loop[(i+1)%len(loop)]
            F.append((ci,v,u));caps+=1
    TT=[(V[a],V[b],V[c]) for a,b,c in F]
    return TT,{'removed_degenerate':removed_degenerate,'removed_duplicate':removed_duplicate,'boundary_loops_capped':len(loops),'cap_triangles':caps}

def audit(T,tol=1e-5):
    vmap={};V=[];F=[]
    def vid(p):
        k=tuple(int(round(float(x)/tol)) for x in p)
        if k not in vmap:vmap[k]=len(V);V.append(p)
        return vmap[k]
    ec=collections.Counter();deg=0
    for t in T:
        f=tuple(vid(p) for p in t);F.append(f)
        if len(set(f))<3 or normal(*t)==(0,0,0):deg+=1
        for e in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):ec[tuple(sorted(e))]+=1
    boundary=sum(n==1 for n in ec.values());multi=sum(n>2 for n in ec.values())
    # Number of edge-connected shells.
    owners=collections.defaultdict(list)
    for i,f in enumerate(F):
        for e in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):owners[tuple(sorted(e))].append(i)
    adj=[[] for _ in F]
    for fs in owners.values():
        for i in range(1,len(fs)):adj[fs[0]].append(fs[i]);adj[fs[i]].append(fs[0])
    seen=set();comps=0
    for i in range(len(F)):
        if i in seen:continue
        comps+=1;seen.add(i);st=[i]
        while st:
            q=st.pop()
            for j in adj[q]:
                if j not in seen:seen.add(j);st.append(j)
    return {'triangles':len(T),'vertices':len(V),'boundary_edges':boundary,'nonmanifold_edges':multi,'degenerate_triangles':deg,'closed_shells':comps}

def face_components(T,tol=1e-5):
    """Group triangles that share geometric edges; coincident CFD interfaces stay together."""
    d={};V=[];F=[];owners=collections.defaultdict(list)
    def vid(p):
        k=tuple(int(round(float(x)/tol)) for x in p)
        if k not in d:d[k]=len(V);V.append(p)
        return d[k]
    for fi,t in enumerate(T):
        f=tuple(vid(p) for p in t);F.append(f)
        for e in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):owners[tuple(sorted(e))].append(fi)
    adj=[[] for _ in F]
    for fs in owners.values():
        if len(fs)>1:
            a=fs[0]
            for b in fs[1:]:adj[a].append(b);adj[b].append(a)
    seen=set();groups=[]
    for i in range(len(F)):
        if i in seen:continue
        seen.add(i);st=[i];g=[]
        while st:
            q=st.pop();g.append(q)
            for j in adj[q]:
                if j not in seen:seen.add(j);st.append(j)
        groups.append(g)
    return groups

def solidify(T,pitch):
    """Winding-number voxel union followed by greedy watertight surface extraction."""
    lo,hi,sz=bounds(T);origin=[lo[i]-pitch for i in range(3)]
    dims=[int(math.ceil(sz[i]/pitch))+2 for i in range(3)];nx,ny,nz=dims
    occ=bytearray(nx*ny*nz)
    def oi(ix,iy,iz):return (ix*ny+iy)*nz+iz
    groups=face_components(T,tol=max(1e-5,pitch*1e-4))
    bad_winding=0;event_count=0
    # Scan each connected closed shell along X, then OR the shell volume into the union.
    for group in groups:
        events=collections.defaultdict(list)
        for fi in group:
            a,b,c=T[fi]
            ux,uy,uz=b[0]-a[0],b[1]-a[1],b[2]-a[2]
            vx,vy,vz=c[0]-a[0],c[1]-a[1],c[2]-a[2]
            nn=(uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx);nxx,nyy,nzz=nn
            if abs(nxx)<1e-12:continue
            ya,za=a[1],a[2];yb,zb=b[1],b[2];yc,zc=c[1],c[2]
            den=(yb-yc)*(za-zc)+(zc-zb)*(ya-yc)
            if abs(den)<1e-15:continue
            iy0=max(0,int(math.ceil((min(ya,yb,yc)-origin[1])/pitch-.5-1e-9)))
            iy1=min(ny-1,int(math.floor((max(ya,yb,yc)-origin[1])/pitch-.5+1e-9)))
            iz0=max(0,int(math.ceil((min(za,zb,zc)-origin[2])/pitch-.5-1e-9)))
            iz1=min(nz-1,int(math.floor((max(za,zb,zc)-origin[2])/pitch-.5+1e-9)))
            delta=1 if nxx>0 else -1
            for iy in range(iy0,iy1+1):
                y=origin[1]+(iy+.5)*pitch+pitch*1.0e-8
                for iz in range(iz0,iz1+1):
                    z=origin[2]+(iz+.5)*pitch+pitch*1.7e-8
                    w1=((yb-yc)*(z-zc)+(zc-zb)*(y-yc))/den
                    w2=((yc-ya)*(z-zc)+(za-zc)*(y-yc))/den
                    w3=1.0-w1-w2
                    if w1>=-1e-9 and w2>=-1e-9 and w3>=-1e-9:
                        x=a[0]-(nyy*(y-a[1])+nzz*(z-a[2]))/nxx
                        events[iy*nz+iz].append((x,delta));event_count+=1
        for line,ev in events.items():
            ev.sort();grouped=[]
            for x,dlt in ev:
                if grouped and abs(x-grouped[-1][0])<pitch*1e-6:grouped[-1][1]+=dlt
                else:grouped.append([x,dlt])
            winding=0;iy=line//nz;iz=line%nz
            for q in range(len(grouped)-1):
                winding+=grouped[q][1];left,right=grouped[q][0],grouped[q+1][0]
                if winding==0 or right-left<1e-10:continue
                i0=max(0,int(math.ceil((left-origin[0])/pitch-.5+1e-7)))
                i1=min(nx-1,int(math.floor((right-origin[0])/pitch-.5-1e-7)))
                if i0>i1:
                    i0=i1=max(0,min(nx-1,int(round(((left+right)/2-origin[0])/pitch-.5))))
                for ix in range(i0,i1+1):occ[oi(ix,iy,iz)]=1
            if grouped:
                winding+=grouped[-1][1]
                if winding!=0:bad_winding+=1
    def get(x,y,z):
        return 0 if x<0 or y<0 or z<0 or x>=nx or y>=ny or z>=nz else occ[oi(x,y,z)]

    # A raw voxel union can contain a checkerboard around a grid edge: two
    # solids then touch only along that edge and create a non-manifold mesh.
    # Fill the two opposing gaps in every such pattern.  This changes the
    # surface by at most a few pitch-sized cells but makes slicer topology
    # substantially more reliable.
    regularized=0
    for _pass in range(4):
        add=set()
        # x-directed grid edges
        for ix in range(nx):
            base=ix*ny*nz
            for iy in range(1,ny):
                row0=base+(iy-1)*nz;row1=base+iy*nz
                for iz in range(1,nz):
                    i0=row0+iz-1;i1=row1+iz-1;i2=row1+iz;i3=row0+iz
                    a0=occ[i0];a1=occ[i1];a2=occ[i2];a3=occ[i3]
                    if a0 and a2 and not a1 and not a3:add.update((i1,i3))
                    elif a1 and a3 and not a0 and not a2:add.update((i0,i2))
        # y-directed grid edges
        slab=ny*nz
        for iy in range(ny):
            yoff=iy*nz
            for ix in range(1,nx):
                b0=(ix-1)*slab+yoff;b1=ix*slab+yoff
                for iz in range(1,nz):
                    i0=b0+iz-1;i1=b1+iz-1;i2=b1+iz;i3=b0+iz
                    a0=occ[i0];a1=occ[i1];a2=occ[i2];a3=occ[i3]
                    if a0 and a2 and not a1 and not a3:add.update((i1,i3))
                    elif a1 and a3 and not a0 and not a2:add.update((i0,i2))
        # z-directed grid edges
        for iz in range(nz):
            for ix in range(1,nx):
                b0=(ix-1)*slab;b1=ix*slab
                for iy in range(1,ny):
                    i0=b0+(iy-1)*nz+iz;i1=b1+(iy-1)*nz+iz
                    i2=b1+iy*nz+iz;i3=b0+iy*nz+iz
                    a0=occ[i0];a1=occ[i1];a2=occ[i2];a3=occ[i3]
                    if a0 and a2 and not a1 and not a3:add.update((i1,i3))
                    elif a1 and a3 and not a0 and not a2:add.update((i0,i2))
        if not add:break
        for idx in add:occ[idx]=1
        regularized+=len(add)

    # Mesh every exposed voxel face.  Do not greedily merge rectangles here:
    # merged rectangles next to unmerged ones create T-junctions, which many
    # slicers quite correctly report as non-manifold geometry.
    tris=[]
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                if not get(ix,iy,iz):continue
                cell=[ix,iy,iz]
                for d_axis in range(3):
                    u=(d_axis+1)%3;v=(d_axis+2)%3
                    for sign in (-1,1):
                        nb=cell[:];nb[d_axis]+=sign
                        if get(*nb):continue
                        p=cell[:]
                        if sign>0:p[d_axis]+=1
                        du=[0,0,0];dv=[0,0,0];du[u]=1;dv[v]=1
                        vv=[]
                        for off in ((0,0),(1,0),(1,1),(0,1)):
                            g=[p[k]+off[0]*du[k]+off[1]*dv[k] for k in range(3)]
                            vv.append(tuple(origin[k]+g[k]*pitch for k in range(3)))
                        if sign>0:tris += [(vv[0],vv[1],vv[2]),(vv[0],vv[2],vv[3])]
                        else:tris += [(vv[0],vv[2],vv[1]),(vv[0],vv[3],vv[2])]
    filled=sum(occ)
    return tris,{'pitch_mm':pitch,'grid':dims,'filled_voxels':filled,'input_shell_groups':len(groups),'ray_events':event_count,'bad_winding_lines':bad_winding,'regularized_voxels':regularized}

# ---------- explicit-mm 3MF ----------
def write_3mf(path,T,title):
    d={};V=[];F=[]
    for tri in T:
        f=[]
        for p in tri:
            k=tuple(round(float(x),5) for x in p)
            if k not in d:d[k]=len(V);V.append(k)
            f.append(d[k])
        F.append(f)
    vs=''.join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x,y,z in V)
    fs=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in F)
    model=('<?xml version="1.0" encoding="UTF-8"?>'
           '<model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
           f'<metadata name="Title">{escape(title)}</metadata>'
           '<metadata name="Description">Repaired and reinforced V6 display-print model; units are millimeters.</metadata>'
           f'<resources><object id="1" name="{escape(title)}" type="model"><mesh><vertices>{vs}</vertices><triangles>{fs}</triangles></mesh></object></resources>'
           '<build><item objectid="1"/></build></model>')
    rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    ct='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',ct);z.writestr('_rels/.rels',rels);z.writestr('3D/3dmodel.model',model)
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise RuntimeError('3MF verification failed')

# Original CFD export plus closed hidden reinforcement needed for a one-piece display print.
T=read_stl(SRC)
rein=[]
# Join nose to monocoque and connect front-wing pylons down into the nose.
rein += box(-1900,0,260,180,280,150)
for s in (-1,1):rein += beam((-2100,s*140,480),(-2030,s*140,305),38,16)
# Attach active front flaps to the endplates (movement intentionally removed for this one-piece print).
for s in (-1,1):
    for x,z,span in [(-2490,300,840),(-2380,370,760),(-2280,440,650)]:
        outer=s*(span+80);rein += beam((x,outer,z),(x,s*985,z),26,16)
# Attach rear DRS flap to the rear-wing endplates.
for s in (-1,1):rein += beam((2240,s*845,1010),(2240,s*965,1010),30,16)
# Join plank/skids to the floor with a hidden center keel.
rein += box(50,0,81,3850,150,88)
# Small underfloor support posts retain the Venturi/diffuser study surfaces after printing.
for x,z0,z1 in [(-1200,88,126),(0,70,126),(900,92,126),(1500,164,225)]:
    for s in (-1,1):rein += box(x,s*410,(z0+z1)/2,55,55,z1-z0)
T.extend(rein)
T,repair=clean_and_cap(T)
base_audit=audit(T)
if base_audit['boundary_edges'] or base_audit['nonmanifold_edges'] or base_audit['degenerate_triangles']:
    print('DEBUG repair audit:',base_audit)
lo,hi,size=bounds(T)

reports=[]
for inches in (5.0,8.0):
    target=inches*25.4;scale=target/size[0]
    # Normalize all axes so slicers see a positive, bed-ready coordinate range with Z=0.
    S=[tuple(tuple((p[k]-lo[k])*scale for k in range(3)) for p in tri) for tri in T]
    _,_,smooth_dims=bounds(S);tag=str(inches).replace('.0','').replace('.','_')+'IN'
    smooth=os.path.join(OUT,f'V6_{tag}_SMOOTH_REPAIRED_MM.stl')
    write_stl(smooth,S,f'V6 {inches:g} IN SMOOTH REPAIRED MM')
    pitch=.30 if inches==5.0 else .40
    solid,solid_info=solidify(S,pitch)
    slo,_,_=bounds(solid)
    solid=[tuple(tuple(p[k]-slo[k] for k in range(3)) for p in tri) for tri in solid]
    _,_,solid_dims=bounds(solid)
    stl=os.path.join(OUT,f'V6_{tag}_PRINT_READY_SOLID_MM.stl');mf=os.path.join(OUT,f'V6_{tag}_PRINT_READY_SOLID_MM.3mf')
    write_stl(stl,solid,f'V6 {inches:g} IN PRINT READY SOLID MM')
    write_3mf(mf,solid,f'V6 {inches:g}-inch print-ready solid model')
    au=audit(solid,tol=1e-5)
    if au['boundary_edges'] or au['nonmanifold_edges'] or au['degenerate_triangles']:
        raise RuntimeError(f'Solidified {inches:g}-inch audit failed: {au}')
    reports.append((inches,scale,smooth_dims,solid_dims,au,solid_info,os.path.basename(stl),os.path.basename(mf),os.path.basename(smooth)))

with open(os.path.join(OUT,'READ_ME_FIRST.txt'),'w') as f:
    f.write('''V6 FORMULA EV — REPAIRED 5-INCH AND 8-INCH PRINT MODELS\n\nWHAT WAS WRONG WITH THE ORIGINAL\nThe source STL was a full-scale CFD-preparation export measuring about 5,450 mm long (over 17 feet). STL files do not store units, and the model also contained open beam ends, very thin CFD surfaces, separate active wing elements, and disconnected underfloor details. It was not intended to be sent directly to a slicer.\n\nFILES\n- V6_8IN_PRINT_READY_SOLID_MM.stl / .3mf: approximately 203 mm long. RECOMMENDED because its details and suspension are stronger.\n- V6_5IN_PRINT_READY_SOLID_MM.stl / .3mf: approximately 127 mm long. Fits smaller machines, but its wing and suspension details are more fragile.\n- V6_*_SMOOTH_REPAIRED_MM.stl: smoother reference alternatives. These retain intersecting CFD shells, so use the SOLID files for the most reliable slicing.\n\nIMPORT UNITS\nChoose MILLIMETERS if the slicer asks. The 3MF files explicitly declare millimeters and are the safest option. Do not import these as inches and do not apply the original full-scale dimensions.\n\nPRINTING RECOMMENDATION\nMaterial: PLA or PLA+ for the easiest detailed display print; PETG if greater impact resistance is needed. Start with a 0.4 mm nozzle, 0.16-0.20 mm layers, 3 walls, 15-20% gyroid infill, and automatic/tree supports. Print the 8-inch SOLID version when the build plate allows it. Orient it upright exactly as imported, with the wheels on the build plate. Use a brim around the wheels and front wing.\n\nDESIGN CHANGES FOR THE ONE-PIECE PRINT\nOpen mesh boundaries were capped. Degenerate facets were removed. Hidden structural connections were added between the nose and body, floor and plank, underfloor surfaces, front-wing flaps, and rear DRS flap. The active flaps therefore do not move in this one-piece display version. The recommended models were then solidified into manifold voxel-derived meshes to eliminate overlapping CFD surfaces.\n\nLIMITATION\nThis is a repaired display-print derivative of the V6 CFD study model, not a working RC car or structurally engineered vehicle. Solidification uses 0.30 mm cells for the 5-inch model and 0.40 mm cells for the 8-inch model, so tiny stair-step facets may be visible under extreme magnification. At 5 inches, very fine aerodynamic details may still be below the reliable capability of some FDM printers.\n''')

with open(os.path.join(OUT,'MESH_VALIDATION.txt'),'w') as f:
    f.write('V6 PRINT-READY MESH VALIDATION\n\n')
    f.write(f'Source full-scale length before scaling: {size[0]:.3f} mm\n')
    f.write(f'Repair operations: {repair}\n')
    f.write(f'Full-scale repaired audit: {base_audit}\n\n')
    for inches,scale,smooth_dims,solid_dims,au,solid_info,stl,mf,smooth in reports:
        f.write(f'{inches:g}-inch version\n  scale factor: {scale:.9f}\n  smooth dimensions: {smooth_dims[0]:.3f} x {smooth_dims[1]:.3f} x {smooth_dims[2]:.3f} mm\n  solid dimensions: {solid_dims[0]:.3f} x {solid_dims[1]:.3f} x {solid_dims[2]:.3f} mm\n  solidification: {solid_info}\n  solid audit: {au}\n  recommended files: {stl}, {mf}\n  smooth alternative: {smooth}\n\n')
    f.write('Acceptance for recommended SOLID files: zero boundary edges, zero non-manifold edges, and zero degenerate triangles.\n')

zip_path=os.path.join(ROOT,'outputs','V6_PRINT_READY_5_TO_8_INCH.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(OUT)):z.write(os.path.join(OUT,fn),os.path.join('V6_PRINT_READY_5_TO_8_INCH',fn))
with zipfile.ZipFile(zip_path) as z:
    if z.testzip() is not None:raise RuntimeError('ZIP verification failed')

print('source_dims',size)
print('repair',repair)
print('base_audit',base_audit)
for row in reports:print(row)
print('output',OUT)
print('zip',zip_path,os.path.getsize(zip_path))
