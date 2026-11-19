from pathlib import Path
import numpy as np,json,hashlib
import trimesh
from matplotlib.path import Path as Polygon
from build_w11_2020_glbderived_cfd_v2 import glb_arrays,EXTERIOR_MATERIALS
root=Path(__file__).resolve().parents[1]
shellpath=root/'outputs/W11_CHASSIS_AIRFLOW_VIEWS/GEOMETRY/W11_SOURCE_SHELL_METRES_NOT_PRINT_SIZE.stl'
shell=trimesh.load(shellpath,force='mesh',process=True)
cut=shell.section(plane_origin=[0,.45,0],plane_normal=[0,1,0])
assert cut is not None
loops=[]
for a in cut.discrete:
 if np.linalg.norm(a[0]-a[-1])<1e-5 and len(a)>3:loops.append(a[:,[0,2]])
assert loops
source=root/'references/mercedec-f1-2020/mercedec-f1-2020.glb'
v,f=glb_arrays(source,EXTERIOR_MATERIALS)
top=np.column_stack((-v[:,1],v[:,0]+2.25))
for nx in [480,960,1440]:
 ny=nx*3//10;dx=15/nx
 X,Z=np.meshgrid(-5+(np.arange(nx)+.5)*dx,(np.arange(ny)+.5)*dx)
 flat=np.column_stack((X.ravel(),Z.ravel()))
 under=np.zeros(nx*ny,bool)
 for loop in loops:under^=Polygon(loop).contains_points(flat)
 under=under.reshape(ny,nx)
 cooling=np.zeros((ny,nx),np.uint8)
 for tri in top[f]:
  a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-12:continue
  lo=np.maximum(0,np.floor((tri.min(axis=0)-[-5,0])/dx-.5).astype(int));hi=np.minimum([nx-1,ny-1],np.ceil((tri.max(axis=0)-[-5,0])/dx-.5).astype(int))
  if np.any(hi<lo):continue
  xx,zz=X[lo[1]:hi[1]+1,lo[0]:hi[0]+1],Z[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
  w1=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(zz-c[1]))/den;w2=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(zz-c[1]))/den
  cooling[lo[1]:hi[1]+1,lo[0]:hi[0]+1]|=(w1>=-1e-7)&(w2>=-1e-7)&(w1+w2<=1+1e-7)
 # Explicitly hypothetical channels: smooth paired corridors in the sidepod region.
 # The source does not supply usable internal duct or radiator CAD.
 centre=.70+.07*np.sin((X+1.6)/4.9*np.pi)
 width=.14+.035*np.cos((X+.9)/3*np.pi)
 corridor=(X>-1.6)&(X<3.35)&(np.abs(np.abs(Z-2.25)-centre)<width)
 cooling[corridor]=0
 common=dict(nx=nx,ny=ny,xmin_m=-5,xmax_m=10,dx_m=dx,car_length_m=float(np.ptp(top[:,0])),car_length_cells=float(np.ptp(top[:,0])/dx),source_GLB_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
 specs=[
 ('underfloor',under,dict(
  title='Underfloor / diffuser · section y = +0.45 m',
  provenance='Plane section of repaired W11-derived 20 mm shell at lateral y=+0.45 m. This is not the full projected silhouette.',
  limitation='Reduced-Re 2D section. Sealed gaps in the repaired shell remain sealed. This does not recover full 3D floor flow or validated downforce.',
  view_m=dict(xmin=-3.2,xmax=5.2,zmin=0,zmax=1.05),particle_band_m=[.005,.55],
  seed_regions_m=[[-3,-1,.015,.25],[-.8,2.6,.015,.20],[2.7,4.9,.03,.65]],
  vector_box_m=[-2.4,4.7,.03,.50],
  labels=[dict(x=-1.9,z=.40,text='Floor entry'),dict(x=.3,z=.45,text='Solid floor above road gap'),dict(x=2.75,z=.65,text='Diffuser / exit')],
  axis_note='Longitudinal section; vertical scale enlarged for visibility. Air flows through fluid gaps, never through solid floor.',
  solver_surface_sha256=hashlib.sha256(shellpath.read_bytes()).hexdigest())),
 ('cooling',cooling.astype(bool),dict(
  title='Internal cooling · conceptual top-plan channels',
  provenance='Source-derived top projection with two explicitly hypothetical open sidepod channels carved into it.',
  limitation='Assumed duct layout, not Mercedes internal CAD. No radiator pressure-drop calibration, heat transfer, fan, wheel rotation or cooling-performance prediction.',
  view_m=dict(xmin=-3.2,xmax=5.2,zmin=.9,zmax=3.6),particle_band_m=[.92,3.58],
  seed_regions_m=[[-1.6,3.3,1.35,1.72],[-1.6,3.3,2.78,3.15]],
  vector_box_m=[-1.4,3.4,1.30,3.2],
  labels=[dict(x=-1.4,z=3.25,text='Assumed inlets'),dict(x=.3,z=2.25,text='Solid chassis / monocoque'),dict(x=2.7,z=3.3,text='Assumed cooling exits')],
  axis_note='Top plan: longitudinal x, lateral y shifted +2.25 m. Channels are conceptual. Radiator cores are not represented.'))]
 for name,mask,details in specs:
  result={**common,**details,'region':name,'solid_indices':np.flatnonzero(mask.ravel()).tolist()}
  for folder in ['docs','outputs/W11_CHASSIS_AIRFLOW_VIEWS']:
   (root/folder/f'w11-{name}-mask-{nx}.json').write_text(json.dumps(result,separators=(',',':')))
  print(name,nx,int(mask.sum()),flush=True)
