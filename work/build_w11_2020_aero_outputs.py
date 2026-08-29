#!/usr/bin/env python3
"""Create W11 airflow presentation, equation estimates, and CFD plots/reports."""

import csv, json, math, os, struct, sys, statistics

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'outputs/W11_2020_AERO_CFD_VALIDATION_300KPH')
FIG=os.path.join(OUT,'FIGURES')
BASE=os.path.join(ROOT,'outputs/W11_2020_RESEARCH_REBUILD_STATIC_8IN/W11_2020_PRINTABLE_ASSEMBLED_REFERENCE.stl')
os.makedirs(FIG,exist_ok=True)

RHO=1.225
CL_A_NOM=4.20
CD_A_NOM=1.25
UNC_CL=0.30
UNC_CD=0.25

def read_stl(path):
    data=open(path,'rb').read();n=struct.unpack_from('<I',data,80)[0];m=[];off=84
    for _ in range(n):
        vals=struct.unpack_from('<12fH',data,off);off+=50
        m.append((tuple(vals[3:6]),tuple(vals[6:9]),tuple(vals[9:12])))
    return m

def box(cx,cy,cz,l,w,h):
    x0,x1=cx-l/2,cx+l/2;y0,y1=cy-w/2,cy+w/2;z0,z1=cz-h/2,cz+h/2
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return [(v[a],v[b],v[c]) for a,b,c in f]

def cyl(cx,cy,cz,r,length,axis='x',n=12):
    out=[]
    def p(i,s):
        a=2*math.pi*i/n
        if axis=='x':return (cx+s*length/2,cy+r*math.cos(a),cz+r*math.sin(a))
        if axis=='y':return (cx+r*math.cos(a),cy+s*length/2,cz+r*math.sin(a))
        return (cx+r*math.cos(a),cy+r*math.sin(a),cz+s*length/2)
    c0=(cx-length/2,cy,cz) if axis=='x' else (cx,cy-length/2,cz) if axis=='y' else (cx,cy,cz-length/2)
    c1=(cx+length/2,cy,cz) if axis=='x' else (cx,cy+length/2,cz) if axis=='y' else (cx,cy,cz+length/2)
    for i in range(n):
        j=(i+1)%n;a,b,c,d=p(i,-1),p(j,-1),p(j,1),p(i,1)
        out += [(a,b,c),(a,c,d),(c0,b,a),(c1,d,c)]
    return out

def beam(a,b,r,n=10):
    ax,ay,az=a;bx,by,bz=b;dx,dy,dz=bx-ax,by-ay,bz-az;L=math.sqrt(dx*dx+dy*dy+dz*dz)
    if L<1e-9:return []
    ux,uy,uz=dx/L,dy/L,dz/L;tx,ty,tz=(0,0,1) if abs(uz)<.9 else (0,1,0)
    vx,vy,vz=uy*tz-uz*ty,uz*tx-ux*tz,ux*ty-uy*tx;q=math.sqrt(vx*vx+vy*vy+vz*vz);vx,vy,vz=vx/q,vy/q,vz/q
    wx,wy,wz=uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx;rings=[]
    for p0 in (a,b):
        rings.append([(p0[0]+r*(vx*math.cos(2*math.pi*i/n)+wx*math.sin(2*math.pi*i/n)),p0[1]+r*(vy*math.cos(2*math.pi*i/n)+wy*math.sin(2*math.pi*i/n)),p0[2]+r*(vz*math.cos(2*math.pi*i/n)+wz*math.sin(2*math.pi*i/n))) for i in range(n)])
    out=[]
    for i in range(n):
        j=(i+1)%n;out += [(rings[0][i],rings[0][j],rings[1][j]),(rings[0][i],rings[1][j],rings[1][i]),(a,rings[0][j],rings[0][i]),(b,rings[1][i],rings[1][j])]
    return out

def indexed(mesh):
    d={};v=[];f=[]
    for tri in mesh:
        for p in tri:
            p=tuple(float(x) for x in p)
            if p not in d:d[p]=len(v);v.append(p)
            f.append(d[p])
    return v,f

def build_glb():
    materials={
        'White body':((0.88,0.90,0.92,1),'OPAQUE'),'Ground':((0.09,0.11,0.14,.42),'BLEND'),
        'Tunnel':((0.55,0.65,0.72,.25),'BLEND'),'Slow air':((0.10,0.55,1.0,1),'OPAQUE'),
        'Fast air':((1.0,0.66,0.05,1),'OPAQUE'),'Wake':((0.72,0.18,0.95,1),'OPAQUE'),
        'Force':((0.96,0.05,0.04,1),'OPAQUE')}
    items=[('W11 2020 reference-based car',read_stl(BASE),(0,0,0),'White body'),('Moving-ground plane',box(8,0,-2.0,245,115,0.7),(0,0,0),'Ground')]
    frame=[]
    for y in (-57,57):
        frame+=beam((-120,y,-2),(130,y,-2),.45)+beam((-120,y,55),(130,y,55),.45)+beam((-120,y,-2),(-120,y,55),.45)+beam((130,y,-2),(130,y,55),.45)
    items.append(('Wind-tunnel frame',frame,(0,0,0),'Tunnel'))
    arrows=[]
    for x,z in [(-75,25),(-25,33),(25,30),(72,30),(96,44)]:
        for y in (-22,22):
            arrows+=beam((x,y,z),(x,y,z-10),.75)+beam((x,y,z-10),(x-3,y,z-6),.75)+beam((x,y,z-10),(x+3,y,z-6),.75)
    items.append(('Downforce direction indicators',arrows,(0,0,0),'Force'))
    particle=cyl(0,0,0,.72,2.5,'x',10);paths=[]
    # Presentation paths only: whole-car upper flow, side flow, flat-floor gap and diffuser exit.
    templates=[]
    for y in (-30,-18,0,18,30):templates.append(([(-120,y,20),(-90,y,20),(-60,y,30),(-20,y,45),(25,y,42),(65,y,35),(100,y,45),(130,y,43)],'Slow air'))
    for y in (-20,-10,0,10,20):templates.append(([(-120,y,.0),(-90,y,.2),(-60,y,.35),(-25,y,.40),(20,y,.45),(55,y,.8),(82,y,5.5),(105,y,12),(130,y,14)],'Fast air'))
    for y in (-32,32):templates.append(([(-120,y,12),(-80,y,10),(-35,y,8),(10,y,9),(55,y,13),(95,y,20),(130,y,24)],'Wake'))
    for j,(path,mat) in enumerate(templates):
        for phase in range(3):paths.append((f'Airflow particle {j+1}-{phase+1}',particle,path,phase,mat))
    buf=bytearray();views=[];acc=[];meshes=[];nodes=[]
    def align():
        while len(buf)%4:buf.append(0)
    def view(data,target=None):
        align();off=len(buf);buf.extend(data);q={'buffer':0,'byteOffset':off,'byteLength':len(data)}
        if target:q['target']=target
        views.append(q);return len(views)-1
    mats=[];mi={}
    for name,(c,mode) in materials.items():
        mi[name]=len(mats);q={'name':name,'pbrMetallicRoughness':{'baseColorFactor':list(c),'metallicFactor':.08,'roughnessFactor':.48},'doubleSided':True}
        if mode=='BLEND':q['alphaMode']='BLEND'
        mats.append(q)
    def addmesh(name,mesh,tr,mat):
        v,f=indexed(mesh);pv=view(b''.join(struct.pack('<3f',*p) for p in v),34962);iv=view(b''.join(struct.pack('<I',i) for i in f),34963)
        mins=[min(p[k] for p in v) for k in range(3)];maxs=[max(p[k] for p in v) for k in range(3)]
        pa=len(acc);acc.append({'bufferView':pv,'componentType':5126,'count':len(v),'type':'VEC3','min':mins,'max':maxs});ia=len(acc);acc.append({'bufferView':iv,'componentType':5125,'count':len(f),'type':'SCALAR','min':[min(f)],'max':[max(f)]})
        meshes.append({'name':name,'primitives':[{'attributes':{'POSITION':pa},'indices':ia,'material':mi[mat]}]});nodes.append({'name':name,'mesh':len(meshes)-1,'translation':list(tr)});return len(nodes)
    for q in items:addmesh(*q)
    moving=[]
    for name,mesh,path,phase,mat in paths:moving.append((addmesh(name,mesh,path[0],mat),path,phase))
    root={'name':'W11 2020 AERODYNAMIC PRESENTATION - NOT SOLVER STREAMLINES','children':list(range(1,len(nodes)+1))}
    doc={'asset':{'version':'2.0','generator':'W11 2020 aero presentation'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[root]+nodes,'meshes':meshes,'materials':mats,'buffers':[{'byteLength':0}],'bufferViews':views,'accessors':acc}
    times=[i*.42 for i in range(10)];tv=view(struct.pack('<10f',*times));ta=len(acc);acc.append({'bufferView':tv,'componentType':5126,'count':10,'type':'SCALAR','min':[times[0]],'max':[times[-1]]});samplers=[];channels=[]
    for node,path,phase in moving:
        seq=[]
        for k in range(10):seq.extend(path[(k+phase)%len(path)])
        vv=view(struct.pack('<30f',*seq));aa=len(acc);acc.append({'bufferView':vv,'componentType':5126,'count':10,'type':'VEC3'});samplers.append({'input':ta,'output':aa,'interpolation':'LINEAR'});channels.append({'sampler':len(samplers)-1,'target':{'node':node,'path':'translation'}})
    doc['animations']=[{'name':'ILLUSTRATIVE WHOLE-CAR AIRFLOW LOOP','samplers':samplers,'channels':channels}];doc['buffers'][0]['byteLength']=len(buf)
    js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((4-len(js)%4)%4)
    while len(buf)%4:buf.append(0)
    bb=bytes(buf);total=12+8+len(js)+8+len(bb);path=os.path.join(OUT,'W11_2020_WHOLE_CAR_AIRFLOW_PRESENTATION.glb')
    with open(path,'wb') as o:o.write(struct.pack('<4sII',b'glTF',2,total));o.write(struct.pack('<I4s',len(js),b'JSON'));o.write(js);o.write(struct.pack('<I4s',len(bb),b'BIN\0'));o.write(bb)
    return path,len(moving)

def equation_outputs():
    rows=[]
    for kmh in (90,126,180,234,270,300):
        v=kmh/3.6;q=.5*RHO*v*v;df=q*CL_A_NOM;drag=q*CD_A_NOM
        rows.append({'speed_km_h':kmh,'speed_m_s':v,'dynamic_pressure_pa':q,'nominal_ClA_m2':CL_A_NOM,'downforce_n':df,'downforce_low_n':df*(1-UNC_CL),'downforce_high_n':df*(1+UNC_CL),'nominal_CdA_m2':CD_A_NOM,'drag_n':drag,'aero_power_kw':drag*v/1000})
    path=os.path.join(OUT,'W11_EQUATION_BASED_AERO_ESTIMATE.csv')
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    return rows

def read_history(path,n=20):
    if not os.path.exists(path):return None
    r=list(csv.reader(open(path)));h=[x.strip(' \"') for x in r[0]];d=[[float(x) for x in row] for row in r[1:] if row]
    tail=d[-min(n,len(d)):];ci=h.index('CL');di=h.index('CD');ri=h.index('rms[P]')
    return {'file':os.path.basename(path),'iterations':len(d),'window':len(tail),'CL_mean_half':statistics.mean(x[ci] for x in tail),'CL_stdev_half':statistics.pstdev(x[ci] for x in tail),'CD_mean_half':statistics.mean(x[di] for x in tail),'CD_stdev_half':statistics.pstdev(x[di] for x in tail),'final_rms_pressure_log10':d[-1][ri]}

def plots(restart_csv,histories):
    try:
        import numpy as np
        import matplotlib;matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.tri as mtri
    except Exception as e:
        print('Plot dependencies unavailable:',e);return []
    made=[]
    # Equation chart.
    eq=list(csv.DictReader(open(os.path.join(OUT,'W11_EQUATION_BASED_AERO_ESTIMATE.csv'))));x=np.array([float(r['speed_km_h']) for r in eq]);y=np.array([float(r['downforce_n'])/1000 for r in eq]);lo=np.array([float(r['downforce_low_n'])/1000 for r in eq]);hi=np.array([float(r['downforce_high_n'])/1000 for r in eq])
    fig,ax=plt.subplots(figsize=(9,5.2));ax.fill_between(x,lo,hi,color='#8bc5ff',alpha=.42,label='Assumption band ±30%');ax.plot(x,y,'o-',color='#0767b2',lw=2.5,label='Nominal equation estimate');ax.set(xlabel='Speed (km/h)',ylabel='Downforce (kN)',title='W11 2020 reference study — equation-based downforce estimate');ax.grid(alpha=.25);ax.legend();fig.tight_layout();p=os.path.join(FIG,'EQUATION_DOWNFORCE_VS_SPEED.png');fig.savefig(p,dpi=180);plt.close(fig);made.append(p)
    # Convergence histories.
    fig,axs=plt.subplots(2,1,figsize=(9,7),sharex=False)
    for hp in histories:
        if not os.path.exists(hp):continue
        rr=list(csv.reader(open(hp)));hh=[a.strip(' \"') for a in rr[0]];dd=np.array([[float(a) for a in row] for row in rr[1:] if row]);label=os.path.basename(hp).replace('history_','').replace('.csv','')
        axs[0].plot(dd[:,hh.index('Inner_Iter')],dd[:,hh.index('CL')],label=label);axs[1].plot(dd[:,hh.index('Inner_Iter')],dd[:,hh.index('CD')],label=label)
    axs[0].set(ylabel='Half-model CL',title='SU2 force-coefficient histories');axs[1].set(xlabel='Pseudo-time iteration',ylabel='Half-model CD');
    for ax in axs:ax.grid(alpha=.25);ax.legend(fontsize=8)
    fig.tight_layout();p=os.path.join(FIG,'CFD_FORCE_CONVERGENCE.png');fig.savefig(p,dpi=180);plt.close(fig);made.append(p)
    # Moving-ground cases on their own scale so the force stabilization and
    # coarse/medium spread remain legible despite the stationary-run transients.
    fig,axs=plt.subplots(2,1,figsize=(9,7),sharex=False)
    plotted=False
    for hp in histories:
        if 'moving_ground' not in os.path.basename(hp) or not os.path.exists(hp):continue
        rr=list(csv.reader(open(hp)));hh=[a.strip(' "') for a in rr[0]];dd=np.array([[float(a) for a in row] for row in rr[1:] if row]);label=os.path.basename(hp).replace('history_','').replace('.csv','')
        axs[0].plot(dd[:,hh.index('Inner_Iter')],dd[:,hh.index('CL')],label=label);axs[1].plot(dd[:,hh.index('Inner_Iter')],dd[:,hh.index('CD')],label=label);plotted=True
    if plotted:
        axs[0].set(ylabel='Half-model CL',title='SU2 moving-ground force convergence');axs[1].set(xlabel='Pseudo-time iteration',ylabel='Half-model CD')
        for ax in axs:ax.grid(alpha=.25);ax.legend(fontsize=9)
        fig.tight_layout();p=os.path.join(FIG,'CFD_MOVING_GROUND_CONVERGENCE.png');fig.savefig(p,dpi=180);made.append(p)
    plt.close(fig)
    # Solved side-plane contours from the ASCII restart.
    if restart_csv and os.path.exists(restart_csv):
        pts=[]
        with open(restart_csv) as f:
            for r in csv.DictReader(f):
                if abs(float(r['y']))<1e-8:
                    ux=float(r['Velocity_x']);uy=float(r['Velocity_y']);uz=float(r['Velocity_z']);pts.append((float(r['x']),float(r['z']),math.sqrt(ux*ux+uy*uy+uz*uz),2*float(r['Pressure'])))
        a=np.array(pts)
        if len(a)>20:
            tri=mtri.Triangulation(a[:,0],a[:,1]);mask=[]
            for t in tri.triangles:
                xx=a[t,0];zz=a[t,1];mask.append((xx.max()-xx.min()>1.2) or (zz.max()-zz.min()>0.8))
            tri.set_mask(mask)
            for col,cmap,title,name,vmin,vmax in [(2,'turbo','Velocity magnitude / freestream','CFD_SIDEPLANE_VELOCITY.png',0,1.5),(3,'coolwarm','Pressure coefficient Cp','CFD_SIDEPLANE_PRESSURE.png',-1.5,1.5)]:
                fig,ax=plt.subplots(figsize=(11,4.2));q=ax.tricontourf(tri,a[:,col],levels=50,cmap=cmap,vmin=vmin,vmax=vmax);ax.set(xlim=(-3.2,5.5),ylim=(0,2.0),xlabel='x (m)',ylabel='z (m)',title='Solved SU2 symmetry-plane '+title);fig.colorbar(q,ax=ax,label=title);fig.tight_layout();p=os.path.join(FIG,name);fig.savefig(p,dpi=190);plt.close(fig);made.append(p)
    return made

glb,channels=build_glb();eq=equation_outputs()
histdir=os.path.join(OUT,'CFD_RESULTS')
histories=[os.path.join(histdir,x) for x in ('history_coarse_stationary.csv','history_medium_stationary.csv','history_coarse_moving_ground.csv','history_medium_moving_ground.csv')]
summaries=[x for x in (read_history(p) for p in histories) if x]
restart=os.path.join(histdir,'restart_coarse_moving_ground.csv')
made=plots(restart,histories)
summary={'airflow_glb':os.path.basename(glb),'animation_channels':channels,'equation_nominal':{'ClA_m2':CL_A_NOM,'CdA_m2':CD_A_NOM,'uncertainty_downforce':UNC_CL,'uncertainty_drag':UNC_CD},'cfd_history_summaries':summaries,'figures':[os.path.relpath(p,OUT) for p in made]}
json.dump(summary,open(os.path.join(OUT,'AERO_RUN_SUMMARY.json'),'w'),indent=2)
print(json.dumps(summary,indent=2))
