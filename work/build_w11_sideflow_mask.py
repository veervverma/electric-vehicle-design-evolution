from pathlib import Path
import numpy as np,json,hashlib
from build_w11_2020_glbderived_cfd_v2 import glb_arrays,EXTERIOR_MATERIALS
root=Path(__file__).resolve().parents[1]
source=root/'references/mercedec-f1-2020/mercedec-f1-2020.glb'
v,f=glb_arrays(source,EXTERIOR_MATERIALS)
nx,ny=480,144
xmin,xmax=-5.,10.
dx=(xmax-xmin)/nx
# Side projection from supplied source triangles, not invented primitives.
p=np.column_stack((-v[:,1],-v[:,2]))
mask=np.zeros((ny,nx),np.uint8)
for tri in p[f]:
 a,b,c=tri
 den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
 if abs(den)<1e-12:continue
 lo=np.maximum(0,np.floor((tri.min(axis=0)-[xmin,0])/dx-.5).astype(int))
 hi=np.minimum([nx-1,ny-1],np.ceil((tri.max(axis=0)-[xmin,0])/dx-.5).astype(int))
 if np.any(hi<lo):continue
 xx,yy=np.meshgrid(xmin+(np.arange(lo[0],hi[0]+1)+.5)*dx,(np.arange(lo[1],hi[1]+1)+.5)*dx)
 w1=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
 w2=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
 inside=(w1>=-1e-7)&(w2>=-1e-7)&(w1+w2<=1+1e-7)
 mask[lo[1]:hi[1]+1,lo[0]:hi[0]+1]|=inside
ids=np.flatnonzero(mask.ravel())
data=dict(nx=nx,ny=ny,xmin_m=xmin,xmax_m=xmax,dx_m=dx,solid_indices=ids.tolist(),source='Supplied Mercedes W11 GLB exterior side projection',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),car_length_cells=float(np.ptp(p[:,0])/dx),geometry_note='Union of all exterior triangles in side projection. This merges depth-separated components and closes projected passages. It is a 2D obstacle, not a physical centre-plane section or full 3D car.')
for folder in ['docs','work/sideflow-publish/docs','outputs/W11_2D_SIDE_FLOW']:
 (root/folder/'w11-side-mask.json').write_text(json.dumps(data,separators=(',',':')))
print('solid cells',len(ids),'car length cells',data['car_length_cells'])
