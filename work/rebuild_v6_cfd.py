import os,sys,math,struct,json,zipfile,shutil
sys.path.insert(0,'work')
from advanced_sedan import box,cyl,tube,beam,loft,translate,write_stl,bounds
OUT='outputs/V6_CFD_REBUILD';GEO=OUT+'/geometry';CASE=OUT+'/OpenFOAM_83ms';os.makedirs(GEO,exist_ok=True)

def wedge(x0,x1,y0,y1,z0,z1,t=8):
 v=[(x0,y0,z0),(x0,y1,z0),(x1,y1,z1),(x1,y0,z1),(x0,y0,z0+t),(x0,y1,z0+t),(x1,y1,z1+t),(x1,y0,z1+t)]
 f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
 return [(v[a],v[b],v[c]) for a,b,c in f]
def naca0012(chord,span,cx,cy,cz,angle_deg=0,n=34):
 # Closed NACA 0012 extrusion, span along Y.
 pts=[]
 for i in range(n+1):
  x=(1-math.cos(math.pi*i/n))/2;yt=5*.12*(.2969*math.sqrt(max(x,1e-9))-.126*x-.3516*x*x+.2843*x**3-.1015*x**4);pts.append((x,yt))
 profile=pts[::-1]+[(x,-y) for x,y in pts[1:-1]]
 a=math.radians(angle_deg);rings=[]
 for y in (cy-span/2,cy+span/2):
  r=[]
  for x,z in profile:
   X=(x-.5)*chord;Z=z*chord;r.append((cx+X*math.cos(a)+Z*math.sin(a),y,cz-X*math.sin(a)+Z*math.cos(a)))
  rings.append(r)
 M=[];N=len(profile)
 for i in range(N):
  j=(i+1)%N;M += [(rings[0][i],rings[0][j],rings[1][j]),(rings[0][i],rings[1][j],rings[1][i])]
 for ring,rev in ((rings[0],True),(rings[1],False)):
  c=(sum(p[0] for p in ring)/N,ring[0][1],sum(p[2] for p in ring)/N)
  for i in range(N):
   j=(i+1)%N;M += [(c,ring[j],ring[i])] if rev else [(c,ring[i],ring[j])]
 return M

# Full-scale coordinate system in millimetres: X forward->rear, Y lateral, Z up.
# Overall target: 5600 L x 2000 W x 1050 H; wheelbase 3600 mm.
body=loft([(-2400,150,300,240),(-1900,240,410,270),(-1100,390,700,350),(-350,500,900,440),(500,510,860,420),(1250,400,650,340),(1900,230,420,240)],n_y=24,bottom=170)
body+=box(-900,0,180,2800,480,70) # continuous survival-cell keel
nose=loft([(-2800,55,205,185),(-2550,90,235,195),(-2200,150,300,220),(-1900,225,390,270)],n_y=16,bottom=170)
# Sidepods: independent closed solids with clear undercut volume below.
sidepods=[]
for s in (-1,1):
 sidepods+=translate(loft([(-650,220,330,250),(-250,300,560,330),(450,330,620,360),(1100,270,520,315),(1650,130,340,245)],n_y=16,bottom=245),0,s*570,0)
 sidepods+=tube(-520,s*570,420,150,105,45,'x',44)
# Cockpit canopy/driver-head fairing, closed for CFD.
canopy=loft([(-650,210,160,90),(-300,250,430,170),(150,240,520,180),(600,180,280,120)],n_y=18,bottom=0)
canopy=translate(canopy,0,0,500)
# Halo tubes, separate wall patches.
halo=beam((-520,-260,650),(-470,-90,960),38)+beam((-520,260,650),(-470,90,960),38)+beam((-470,-90,960),(420,-80,880),38)+beam((-470,90,960),(420,80,880),38)+beam((420,-80,880),(500,0,650),38)+beam((420,80,880),(500,0,650),38)
# Floor body and external edge sealing rails.
floor=box(150,0,145,3900,1500,45)
for s in (-1,1):floor+=box(150,s*755,190,3800,28,110)
# Venturi ceiling surfaces: descending inlet, throat, progressive diffuser expansion.
venturi=[]
for s in (-1,1):
 y0,y1=(150,690) if s>0 else (-690,-150)
 venturi+=wedge(-1750,-950,y0,y1,150,70,12)+wedge(-950,650,y0,y1,70,76,12)+wedge(650,1250,y0,y1,76,140,12)+wedge(1250,1950,y0,y1,140,340,12)
 # Four inlet fences.
 ys=[180,330,500,660]
 for q,y in enumerate(ys):
  y*=s;venturi+=beam((-1700,y,100),(-1150,y+s*(35+q*18),175),16)
# Central plank and titanium skids.
plank=box(50,0,37,3850,260,18)
skids=[]
for x in (-1350,-450,450,1350):skids+=box(x,0,25,500,180,12)
# Diffuser strakes and floor-edge devices.
diffuser=[]
for y in (-650,-430,-210,210,430,650):diffuser+=wedge(700,2050,y-14,y+14,90,350,20)
for s in (-1,1):
 for x in (-900,-500,-100,300,700,1100):diffuser+=beam((x,s*755,205),(x+170,s*850,285),18)
# Front wing with fixed mainplane and six active flaps.
frontWing=naca0012(480,2000,-2600,0,230,3)
frontFlaps=[]
for s in (-1,1):
 for level,(x,z,chord,span,ang) in enumerate([(-2490,300,340,840,7),(-2380,370,300,760,11),(-2280,440,260,650,16)],1):frontFlaps+=naca0012(chord,span,x,s*(span/2+80),z,ang)
# Endplates and pylons.
frontWing+=box(-2500,-990,360,700,30,500)+box(-2500,990,360,700,30,500)+beam((-2600,-140,200),(-2100,-140,480),30)+beam((-2600,140,200),(-2100,140,480),30)
# Rear mainplane and DRS flap, true airfoil solids.
rearWing=naca0012(520,1900,2250,0,860,12)+box(2250,-970,820,700,30,500)+box(2250,970,820,700,30,500)
for s in (-1,1):rearWing+=beam((1750,s*260,430),(2250,s*310,790),38)
rearFlap=naca0012(360,1700,2240,0,1010,18)
# Solid rotating-wheel surfaces, each closed.
wheelR=360;wheelW=310;wheelX=(-1800,1800);wheelY=(-845,845)
wheels={}
for xi,x in enumerate(wheelX):
 for yi,y in enumerate(wheelY):wheels[f'wheel{"F" if xi==0 else "R"}{"L" if yi==0 else "R"}']=cyl(x,y,wheelR,wheelR,wheelW,'y',64)
# Suspension/tethers as separate closed beams.
suspension=[]
for x in wheelX:
 for s in (-1,1):
  y=s*690;oy=s*845
  for z in (270,520):suspension+=beam((x-220,y,z),(x,oy,360),24)+beam((x+220,y,z),(x,oy,360),24)
  suspension+=beam((x+120,s*420,680),(x,oy,450),20)+beam((x,oy,260),(x,oy,520),30)
# Cooling openings represented as closed ducts / lips.
cooling=[]
for s in (-1,1):cooling+=tube(-450,s*735,430,165,120,80,'x',44)+box(550,s*760,520,700,30,180)

surfaces={'body':body,'nose':nose,'sidepods':sidepods,'canopy':canopy,'halo':halo,'floor':floor,'venturi':venturi,'plank':plank,'skids':skids,'diffuser':diffuser,'frontWing':frontWing,'frontFlaps':frontFlaps,'rearWing':rearWing,'rearFlap':rearFlap,'suspension':suspension,'cooling':cooling,**wheels}
for n,M in surfaces.items():write_stl(f'{GEO}/{n}.stl',M,n)
# Combined visual surface STL.
combined=[]
for M in surfaces.values():combined+=M
write_stl(f'{OUT}/V6_FULL_SCALE_CFD_SURFACES.stl',combined,'V6_FULL_SCALE_CFD_SURFACES')

# GLB preview, converting mm to metres and preserving selectable systems.
colors={'body':(.92,.92,.89,1),'nose':(.92,.92,.89,1),'sidepods':(.92,.92,.89,1),'canopy':(.14,.20,.26,1),'halo':(.03,.04,.05,1),'floor':(.03,.04,.05,1),'venturi':(.12,.16,.20,1),'plank':(.55,.38,.20,1),'skids':(.55,.60,.65,1),'diffuser':(.05,.06,.08,1),'frontWing':(.04,.05,.06,1),'frontFlaps':(.90,.12,.08,1),'rearWing':(.04,.05,.06,1),'rearFlap':(.90,.12,.08,1),'suspension':(.58,.62,.66,1),'cooling':(.32,.38,.42,1),'wheelFL':(.02,.02,.02,1),'wheelFR':(.02,.02,.02,1),'wheelRL':(.02,.02,.02,1),'wheelRR':(.02,.02,.02,1)}
def indexed(M):
 d={};V=[];F=[]
 for tri in M:
  for p in tri:
   p=tuple(q/1000 for q in p)
   if p not in d:d[p]=len(V);V.append(p)
   F.append(d[p])
 return V,F
buf=bytearray();views=[];acc=[];meshes=[];nodes=[];mats=[]
def align():
 while len(buf)%4:buf.append(0)
def view(data,target):
 align();off=len(buf);buf.extend(data);views.append({'buffer':0,'byteOffset':off,'byteLength':len(data),'target':target});return len(views)-1
for n,M in surfaces.items():
 V,F=indexed(M);pv=view(b''.join(struct.pack('<3f',*p) for p in V),34962);iv=view(b''.join(struct.pack('<I',i) for i in F),34963);mn=[min(p[k] for p in V) for k in range(3)];mx=[max(p[k] for p in V) for k in range(3)];pa=len(acc);acc.append({'bufferView':pv,'componentType':5126,'count':len(V),'type':'VEC3','min':mn,'max':mx});ia=len(acc);acc.append({'bufferView':iv,'componentType':5125,'count':len(F),'type':'SCALAR','min':[min(F)],'max':[max(F)]});mats.append({'name':n,'pbrMetallicRoughness':{'baseColorFactor':list(colors[n]),'metallicFactor':.65 if n in ('skids','suspension') else .03,'roughnessFactor':.35},'doubleSided':True});meshes.append({'name':n,'primitives':[{'attributes':{'POSITION':pa},'indices':ia,'material':len(mats)-1}]});nodes.append({'name':n,'mesh':len(meshes)-1})
root={'name':'V6 FULL SCALE CFD REBUILD','rotation':[-.7071068,0,0,.7071068],'children':list(range(1,len(nodes)+1))};doc={'asset':{'version':'2.0','generator':'V6 CFD rebuild'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[root]+nodes,'meshes':meshes,'materials':mats,'buffers':[{'byteLength':len(buf)}],'bufferViews':views,'accessors':acc};js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((4-len(js)%4)%4)
while len(buf)%4:buf.append(0)
bb=bytes(buf);total=12+8+len(js)+8+len(bb)
with open(f'{OUT}/V6_FULL_SCALE_CFD_PREVIEW.glb','wb') as o:o.write(struct.pack('<4sII',b'glTF',2,total));o.write(struct.pack('<I4s',len(js),b'JSON'));o.write(js);o.write(struct.pack('<I4s',len(bb),b'BIN\0'));o.write(bb)

# OpenFOAM case template.
for d in ('0','constant','system'):os.makedirs(f'{CASE}/{d}',exist_ok=True)
def wr(rel,s):open(f'{CASE}/{rel}','w').write(s)
header=lambda cls,obj:f'''FoamFile\n{{\n version 2.0;\n format ascii;\n class {cls};\n object {obj};\n}}\n'''
wr('system/blockMeshDict',header('dictionary','blockMeshDict')+'''convertToMeters 1;\nvertices ((-15 -10 0)(25 -10 0)(25 10 0)(-15 10 0)(-15 -10 8)(25 -10 8)(25 10 8)(-15 10 8));\nblocks (hex (0 1 2 3 4 5 6 7) (200 100 50) simpleGrading (1 1 1));\nedges ();\nboundary (inlet {type patch;faces ((0 4 7 3));} outlet {type patch;faces ((1 2 6 5));} ground {type wall;faces ((0 3 2 1));} sides {type symmetryPlane;faces ((0 1 5 4)(3 7 6 2));} top {type symmetryPlane;faces ((4 5 6 7));});\nmergePatchPairs ();\n''')
geo='\n'.join(f' {n}.stl {{type triSurfaceMesh; name {n};}}' for n in surfaces)
refs='\n'.join(f' {n} {{level ({5 if n in ("venturi","diffuser","frontWing","frontFlaps","rearWing","rearFlap") else 4} {6 if n in ("venturi","diffuser") else 5}); patchInfo {{type wall;}}}}' for n in surfaces)
wr('system/snappyHexMeshDict',header('dictionary','snappyHexMeshDict')+f'''castellatedMesh true; snap true; addLayers true;\ngeometry\n{{\n{geo}\n carZone {{type searchableBox; min (-3 -1.5 0); max (3 1.5 1.5);}}\n}}\ncastellatedMeshControls\n{{maxLocalCells 4000000; maxGlobalCells 30000000; minRefinementCells 10; nCellsBetweenLevels 3; features (); refinementSurfaces {{{refs}}} refinementRegions {{carZone {{mode inside; levels ((1E15 3));}}}} resolveFeatureAngle 30; locationInMesh (-10 0 2); allowFreeStandingZoneFaces true;}}\nsnapControls {{nSmoothPatch 5; tolerance 2.0; nSolveIter 50; nRelaxIter 8; nFeatureSnapIter 15; implicitFeatureSnap true; explicitFeatureSnap false; multiRegionFeatureSnap false;}}\naddLayersControls {{relativeSizes true; layers {{"(body|nose|sidepods|floor|venturi|diffuser|frontWing|frontFlaps|rearWing|rearFlap)" {{nSurfaceLayers 5;}}}} expansionRatio 1.22; finalLayerThickness 0.35; minThickness 0.08; nGrow 0; featureAngle 55; nRelaxIter 5; nSmoothSurfaceNormals 3; nSmoothNormals 5; nSmoothThickness 10; maxFaceThicknessRatio 0.5; maxThicknessToMedialRatio 0.3; minMedianAxisAngle 90; nBufferCellsNoExtrude 0; nLayerIter 50;}}\nmeshQualityControls {{maxNonOrtho 65; maxBoundarySkewness 20; maxInternalSkewness 4; maxConcave 80; minVol 1e-15; minTetQuality 1e-12; minArea -1; minTwist 0.02; minDeterminant 0.001; minFaceWeight 0.02; minVolRatio 0.01; minTriangleTwist -1; nSmoothScale 4; errorReduction 0.75;}}\ndebug 0; mergeTolerance 1e-6;\n''')
wr('system/surfaceFeatureExtractDict',header('dictionary','surfaceFeatureExtractDict')+'\n'.join(f'{n}.stl {{extractionMethod extractFromSurface; extractFromSurfaceCoeffs {{includedAngle 150;}} writeObj yes;}}' for n in surfaces))
wr('system/controlDict',header('dictionary','controlDict')+'''application simpleFoam; startFrom startTime; startTime 0; stopAt endTime; endTime 3000; deltaT 1; writeControl timeStep; writeInterval 250; purgeWrite 0; writeFormat binary; writePrecision 8; writeCompression off; timeFormat general; timePrecision 6; runTimeModifiable true; functions {forces {type forceCoeffs; libs ("libforces.so"); patches (body nose sidepods canopy halo floor venturi plank skids diffuser frontWing frontFlaps rearWing rearFlap suspension cooling wheelFL wheelFR wheelRL wheelRR); rho rhoInf; rhoInf 1.225; liftDir (0 0 1); dragDir (1 0 0); pitchAxis (0 1 0); CofR (0 0 0.30); magUInf 83.333; lRef 5.60; Aref 1.60; writeControl timeStep; writeInterval 10;}}\n''')
wr('system/fvSchemes',header('dictionary','fvSchemes')+'''ddtSchemes {default steadyState;} gradSchemes {default cellLimited Gauss linear 1;} divSchemes {default none; div(phi,U) bounded Gauss linearUpwind grad(U); div(phi,k) bounded Gauss upwind; div(phi,omega) bounded Gauss upwind; div((nuEff*dev2(T(grad(U))))) Gauss linear;} laplacianSchemes {default Gauss linear limited 0.5;} interpolationSchemes {default linear;} snGradSchemes {default limited 0.5;} wallDist {method meshWave;}\n''')
wr('system/fvSolution',header('dictionary','fvSolution')+'''solvers {p {solver GAMG; tolerance 1e-7; relTol 0.02; smoother GaussSeidel;} U {solver smoothSolver; smoother symGaussSeidel; tolerance 1e-7; relTol 0.05;} "(k|omega)" {solver smoothSolver; smoother symGaussSeidel; tolerance 1e-7; relTol 0.05;}} SIMPLE {nNonOrthogonalCorrectors 1; consistent yes; residualControl {p 1e-5; U 1e-5; "(k|omega)" 1e-5;}} relaxationFactors {fields {p 0.3;} equations {U 0.7; k 0.7; omega 0.7;}}\n''')
wr('constant/transportProperties',header('dictionary','transportProperties')+'''transportModel Newtonian; nu [0 2 -1 0 0 0 0] 1.46e-5;\n''')
wr('constant/turbulenceProperties',header('dictionary','turbulenceProperties')+'''simulationType RAS; RAS {RASModel kOmegaSST; turbulence on; printCoeffs on;}\n''')
# Copy surfaces into case triSurface.
os.makedirs(f'{CASE}/constant/triSurface',exist_ok=True)
for n in surfaces:shutil.copy(f'{GEO}/{n}.stl',f'{CASE}/constant/triSurface/{n}.stl')
wall='(body|nose|sidepods|canopy|halo|floor|venturi|plank|skids|diffuser|frontWing|frontFlaps|rearWing|rearFlap|suspension|cooling)'
wr('0/U',header('volVectorField','U')+f'''dimensions [0 1 -1 0 0 0 0]; internalField uniform (83.333 0 0); boundaryField {{inlet {{type fixedValue; value uniform (83.333 0 0);}} outlet {{type zeroGradient;}} ground {{type fixedValue; value uniform (83.333 0 0);}} sides {{type symmetryPlane;}} top {{type symmetryPlane;}} "{wall}" {{type noSlip;}} wheelFL {{type rotatingWallVelocity; origin (-1.8 -0.845 0.36); axis (0 -1 0); omega 231.48; value uniform (0 0 0);}} wheelFR {{type rotatingWallVelocity; origin (-1.8 0.845 0.36); axis (0 -1 0); omega 231.48; value uniform (0 0 0);}} wheelRL {{type rotatingWallVelocity; origin (1.8 -0.845 0.36); axis (0 -1 0); omega 231.48; value uniform (0 0 0);}} wheelRR {{type rotatingWallVelocity; origin (1.8 0.845 0.36); axis (0 -1 0); omega 231.48; value uniform (0 0 0);}}}}\n''')
wr('0/p',header('volScalarField','p')+f'''dimensions [0 2 -2 0 0 0 0]; internalField uniform 0; boundaryField {{inlet {{type zeroGradient;}} outlet {{type fixedValue; value uniform 0;}} ground {{type zeroGradient;}} sides {{type symmetryPlane;}} top {{type symmetryPlane;}} "{wall}" {{type zeroGradient;}} "(wheelFL|wheelFR|wheelRL|wheelRR)" {{type zeroGradient;}}}}\n''')
wr('0/k',header('volScalarField','k')+f'''dimensions [0 2 -2 0 0 0 0]; internalField uniform 1.0417; boundaryField {{inlet {{type fixedValue; value uniform 1.0417;}} outlet {{type zeroGradient;}} ground {{type kqRWallFunction; value uniform 1.0417;}} sides {{type symmetryPlane;}} top {{type symmetryPlane;}} "{wall}" {{type kqRWallFunction; value uniform 1.0417;}} "(wheelFL|wheelFR|wheelRL|wheelRR)" {{type kqRWallFunction; value uniform 1.0417;}}}}\n''')
wr('0/omega',header('volScalarField','omega')+f'''dimensions [0 0 -1 0 0 0 0]; internalField uniform 12.4; boundaryField {{inlet {{type fixedValue; value uniform 12.4;}} outlet {{type zeroGradient;}} ground {{type omegaWallFunction; value uniform 12.4;}} sides {{type symmetryPlane;}} top {{type symmetryPlane;}} "{wall}" {{type omegaWallFunction; value uniform 12.4;}} "(wheelFL|wheelFR|wheelRL|wheelRR)" {{type omegaWallFunction; value uniform 12.4;}}}}\n''')
wr('0/nut',header('volScalarField','nut')+f'''dimensions [0 2 -1 0 0 0 0]; internalField uniform 0; boundaryField {{inlet {{type calculated; value uniform 0;}} outlet {{type calculated; value uniform 0;}} ground {{type nutkWallFunction; value uniform 0;}} sides {{type symmetryPlane;}} top {{type symmetryPlane;}} "{wall}" {{type nutkWallFunction; value uniform 0;}} "(wheelFL|wheelFR|wheelRL|wheelRR)" {{type nutkWallFunction; value uniform 0;}}}}\n''')
wr('Allrun','''#!/bin/sh\ncd "${0%/*}" || exit 1\n. ${WM_PROJECT_DIR:?}/bin/tools/RunFunctions\nrunApplication blockMesh\nrunApplication surfaceFeatureExtract\nrunApplication snappyHexMesh -overwrite\nrunApplication checkMesh\nrunApplication simpleFoam\n''');os.chmod(f'{CASE}/Allrun',0o755)
wr('README.txt','''V6 OPENFOAM CFD TEMPLATE\n\nRequires OpenFOAM with simpleFoam, blockMesh and snappyHexMesh. Geometry is in millimetres in geometry/, while the copied OpenFOAM surfaces are interpreted with the supplied full-scale dimensions. If your OpenFOAM build expects STL scaling, use surfaceTransformPoints -scale '(0.001 0.001 0.001)' on every triSurface file before meshing; verify with surfaceCheck.\n\nBaseline: 83.333 m/s, rho=1.225 kg/m3, nu=1.46e-5 m2/s, moving ground, wheel omega=231.48 rad/s, k-omega SST. Run ./Allrun.\n\nThis is a starting case. Inspect every patch name after snappyHexMesh, confirm units, achieve mesh independence, and monitor force convergence before trusting coefficients. 30 million maximum cells may require 64-128 GB RAM.\n''')
# Assumptions and dimensional spec.
open(f'{OUT}/V6_ASSUMPTIONS_AND_LIMITATIONS.txt','w').write('''V6 FULL-SCALE CFD REBUILD\n\nTarget envelope: 5.6 m length, 2.0 m width, approximately 1.05 m height. Wheelbase 3.6 m; track 1.69 m; tire radius 0.36 m; tire width 0.31 m. Ground clearance/plank region approximately 25-55 mm.\n\nThe model is rebuilt parametrically with closed component meshes and NACA 0012 wing sections. It is substantially cleaner than V5 GLB geometry, but it has not been boolean-unioned or run through surfaceCheck because OpenFOAM/meshing software is unavailable in this environment. Treat it as CFD preparation, not validated CFD geometry. Physical wind-tunnel and track testing remain external tasks.\n''')
# Zip case and deliverables.
with zipfile.ZipFile(f'{OUT}/V6_OPENFOAM_CFD_PACKAGE.zip','w',zipfile.ZIP_DEFLATED) as z:
 for root,ds,fs in os.walk(CASE):
  for fn in fs:z.write(os.path.join(root,fn),os.path.relpath(os.path.join(root,fn),OUT))
 for fn in ('V6_FULL_SCALE_CFD_PREVIEW.glb','V6_FULL_SCALE_CFD_SURFACES.stl','V6_ASSUMPTIONS_AND_LIMITATIONS.txt'):z.write(f'{OUT}/{fn}',fn)
print('surfaces',len(surfaces),'combined tris',len(combined),'case',CASE)
for n,M in surfaces.items():print(n,bounds(M),len(M))
