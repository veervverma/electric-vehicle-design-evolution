import os,sys,math,zipfile
from xml.sax.saxutils import escape
sys.path.insert(0,'work')
import formula_ev_v5_all_front_flaps as v5
OUT='outputs/formula_ev_v5_all_active_flaps'

def rot_x90(M):
 # (x,y,z)->(x,-z,y), making Y-axis wheel bores vertical Z-axis.
 return [tuple((p[0],-p[2],p[1]) for p in tri) for tri in M]
def move(M,dx,dy,dz):return [tuple((p[0]+dx,p[1]+dy,p[2]+dz) for p in tri) for tri in M]
def bb(M):
 P=[p for tri in M for p in tri];return ([min(p[i] for p in P) for i in range(3)],[max(p[i] for p in P) for i in range(3)])
def normalize(M):
 lo,hi=bb(M);return move(M,-lo[0],-lo[1],-lo[2]),(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2])
def vf(M):
 d={};V=[];F=[]
 for tri in M:
  ids=[]
  for p in tri:
   p=tuple(round(float(q),5) for q in p)
   if p not in d:d[p]=len(V);V.append(p)
   ids.append(d[p])
  F.append(ids)
 return V,F

# Use every actual assembly instance, including all four wheel-corner sets.
objects=[]
for idx,(name,M,tr,mat) in enumerate(v5.I,1):
 # Wheel components print flat instead of balancing on their edges.
 if any(k in name.lower() for k in ('tire','rim','rotor','center lock')):M=rot_x90(M)
 M,size=normalize(M)
 objects.append({'name':f'{idx:02d}_{name}','mesh':M,'size':size,'mat':mat})

# Pack objects on a large virtual layout. Users can auto-arrange them across printer plates.
SHEET_W=600.;GAP=8.;x=GAP;y=GAP;rowh=0
for o in sorted(objects,key=lambda q:max(q['size'][0],q['size'][1]),reverse=True):
 w,h,_=o['size']
 if x+w+GAP>SHEET_W:x=GAP;y+=rowh+GAP;rowh=0
 o['pos']=(x,y,0);x+=w+GAP;rowh=max(rowh,h)
layout_h=y+rowh+GAP

# Stable material labels for slicer display/filament planning.
colors={'White Carbon':('#F4F4F0FF','PETG White'),'Black Carbon':('#202328FF','PETG Black'),'Tire':('#151515FF','TPU 95A Black'),'Aluminum':('#AEB5BCFF','PETG Silver'),'Brake':('#747A80FF','PETG Gray'),'Red':('#D32626FF','PETG Red'),'Battery':('#3577B8FF','PETG Blue'),'HV Orange':('#F47A00FF','PETG Orange'),'Cockpit':('#323A43FF','PETG Black'),'Electronics':('#555E68FF','PETG Gray'),'Underfloor':('#292E35FF','PETG Black'),'Plank':('#8F6B3EFF','PETG Brown'),'Titanium':('#777F86FF','PETG Silver')}
# Add any material not explicitly listed.
for o in objects:
 if o['mat'] not in colors:colors[o['mat']]=('#B0B0B0FF','PETG')
matkeys=list(colors);mi={k:i for i,k in enumerate(matkeys)}

def build_model(use_color=True):
 resources=[]
 if use_color:
  resources.append('<m:basematerials id="900">'+''.join(f'<m:base name="{escape(colors[k][1])}" displaycolor="{colors[k][0]}"/>' for k in matkeys)+'</m:basematerials>')
 items=[]
 for oid,o in enumerate(objects,1):
  V,F=vf(o['mesh']);vs=''.join(f'<vertex x="{a}" y="{b}" z="{c}"/>' for a,b,c in V);fs=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in F)
  prop=f' pid="900" pindex="{mi[o["mat"]]}"' if use_color else ''
  resources.append(f'<object id="{oid}" name="{escape(o["name"])}" type="model"{prop}><mesh><vertices>{vs}</vertices><triangles>{fs}</triangles></mesh></object>')
  px,py,pz=o['pos'];items.append(f'<item objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 {px:.3f} {py:.3f} {pz:.3f}"/>')
 ns=' xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02" requiredextensions="m"' if use_color else ''
 return '<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"'+ns+'><metadata name="Title">Formula EV V5 Complete Print Kit</metadata><metadata name="Description">55 separately selectable parts; auto-arrange across multiple 220mm plates before slicing</metadata><resources>'+''.join(resources)+'</resources><build>'+''.join(items)+'</build></model>'

rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="r" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
ct='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
def save(path,color):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('[Content_Types].xml',ct);z.writestr('_rels/.rels',rels);z.writestr('3D/3dmodel.model',build_model(color))
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
save(f'{OUT}/FORMULA_EV_V5_COMPLETE_PRINT_KIT_55_PARTS.3mf',True)
save(f'{OUT}/FORMULA_EV_V5_COMPLETE_PRINT_KIT_COMPATIBILITY.3mf',False)
open(f'{OUT}/PRINT_KIT_README.txt','w').write(f'''FORMULA EV V5 — COMPLETE 55-PART PRINT KIT\n\nThe 3MF contains all 55 physical part instances as separately selectable objects. Repeated wheel parts are included four times. Wheel parts are already rotated flat.\n\nIMPORTANT: The complete layout occupies approximately {SHEET_W:.0f} x {layout_h:.0f} mm and therefore cannot print on one 220 x 220 mm plate. In Bambu Studio, OrcaSlicer or PrusaSlicer, use Auto Arrange and distribute the objects over multiple plates/batches. Do not scale parts independently.\n\nMATERIAL PLAN\nPETG: body, aero, suspension, rims, floor and mechanical components.\nTPU 95A: four slick tires only.\nOptional metal: 2 mm rods for reliable wing hinges and wheel axles.\n\nThe colored file carries display/material assignments. If your slicer rejects material extensions, use the compatibility file and assign filaments manually. The GLB was a presentation model; test-fit small joints before printing the whole kit.\n''')
print('parts',len(objects),'layout',SHEET_W,layout_h)
for f in ('FORMULA_EV_V5_COMPLETE_PRINT_KIT_55_PARTS.3mf','FORMULA_EV_V5_COMPLETE_PRINT_KIT_COMPATIBILITY.3mf'):
 print(f,os.path.getsize(OUT+'/'+f))
