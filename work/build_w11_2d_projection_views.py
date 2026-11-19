from pathlib import Path
import json,hashlib
import numpy as np
from build_w11_2020_glbderived_cfd_v2 import glb_arrays,EXTERIOR_MATERIALS
root=Path(__file__).resolve().parents[1]
source=root/'references/mercedec-f1-2020/mercedec-f1-2020.glb'
v,f=glb_arrays(source,EXTERIOR_MATERIALS)
p=np.column_stack((-v[:,1],v[:,0]+2.25))
out=root/'outputs/W11_LIVE_2D_PROJECTION_VIEWS';out.mkdir(exist_ok=True)
for nx in [480,960,1440]:
 side=json.loads((root/f'docs/w11-side-mask-{nx}.json').read_text());ny=side['ny'];dx=side['dx_m']
 top=np.zeros((ny,nx),np.uint8)
 for tri in p[f]:
  a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-12:continue
  lo=np.maximum(0,np.floor((tri.min(axis=0)-[-5,0])/dx-.5).astype(int));hi=np.minimum([nx-1,ny-1],np.ceil((tri.max(axis=0)-[-5,0])/dx-.5).astype(int))
  if np.any(hi<lo):continue
  xx,zz=np.meshgrid(-5+(np.arange(lo[0],hi[0]+1)+.5)*dx,(np.arange(lo[1],hi[1]+1)+.5)*dx)
  w1=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(zz-c[1]))/den;w2=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(zz-c[1]))/den
  top[lo[1]:hi[1]+1,lo[0]:hi[0]+1]|=(w1>=-1e-7)&(w2>=-1e-7)&(w1+w2<=1+1e-7)
 common={k:side[k] for k in ['nx','ny','xmin_m','xmax_m','dx_m','car_length_cells']};common['source_GLB_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
 under={**side,'region':'underfloor','title':'W11 lower-car airflow · original side projection','provenance':'IDENTICAL W11 solid mask and live solver as Colored CFD · Live 2D. This mode changes tracer focus, not car geometry.','limitation':'Exterior side projection only: depth-separated parts overlap. Projected blockage may close the floor gap. This is NOT a physical underfloor section or downforce prediction.','view_m':{'xmin':-3.7,'xmax':6.3,'zmin':0,'zmax':3},'particle_band_m':[.01,.65],'seed_regions_m':[[-3.6,5.9,.01,.65]],'vector_box_m':[-3,5,.02,.65],'axis_note':'Original W11 side projection · equal x/z display scale · lower-car tracer focus.','labels':[]}
 cooling={**common,'region':'cooling','solid_indices':np.flatnonzero(top.ravel()).tolist(),'title':'W11 sidepod exterior airflow · top projection','provenance':'Unmodified top projection of the supplied W11 exterior triangles. No duct corridors carved or invented. Same live 2D TRT solver.','limitation':'EXTERNAL flow around projected sidepods only. Internal duct/radiator geometry is absent; no cooling channel or thermal performance is calculated. The solver bottom wall is a 2D domain boundary, not a road in this top view.','view_m':{'xmin':-3.7,'xmax':6.3,'zmin':.75,'zmax':3.75},'particle_band_m':[.76,3.74],'seed_regions_m':[[-3.6,5.9,.8,3.7]],'vector_box_m':[-2.7,4.8,1,3.5],'axis_note':'Original W11 top projection · equal longitudinal/lateral scale · exterior sidepod flow, NOT internal cooling.','labels':[]}
 for name,data in [('underfloor',under),('cooling',cooling)]:
  for folder in [root/'docs',out]:(folder/f'w11-{name}-projection-{nx}.json').write_text(json.dumps(data,separators=(',',':')))
  print(name,nx,len(data['solid_indices']),flush=True)
 assert under['solid_indices']==side['solid_indices']
