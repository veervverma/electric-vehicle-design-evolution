import os,sys,re,csv,zipfile,shutil
sys.path.insert(0,'work')
import formula_ev_v5_all_front_flaps as v5
from advanced_sedan import write_stl,bounds
OUT='outputs/FORMULA_EV_V5_PRINT_PARTS'
if os.path.exists(OUT):shutil.rmtree(OUT)
os.makedirs(OUT)

def rot_x90(M):return [tuple((p[0],-p[2],p[1]) for p in tri) for tri in M]
def normalize(M):
 P=[p for tri in M for p in tri];lo=[min(p[i] for p in P) for i in range(3)]
 return [tuple((p[0]-lo[0],p[1]-lo[1],p[2]-lo[2]) for p in tri) for tri in M]
def clean(s):return re.sub(r'[^A-Za-z0-9]+','_',s).strip('_').lower()
def material(mat):return 'TPU_95A' if mat=='Tire' else 'PETG'
rows=[]
for idx,(name,M,tr,mat) in enumerate(v5.I,1):
 if any(k in name.lower() for k in ('tire','rim','rotor','center lock')):M=rot_x90(M)
 M=normalize(M);fn=f'{idx:02d}_{clean(name)}.stl';write_stl(f'{OUT}/{fn}',M,name)
 rows.append((idx,fn,name,material(mat),bounds(M)))
with open(f'{OUT}/PARTS_AND_MATERIALS.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['part_number','filename','part_name','recommended_material','size_mm']);w.writerows(rows)
open(f'{OUT}/READ_ME_FIRST.txt','w').write('''FORMULA EV V5 — 55 PRINTABLE STL PARTS\n\nThis folder contains every physical part instance required for one complete model. Four tires, four rims, four brake rotors and four center locks are already included as separate files. Wheel parts are oriented flat.\n\nMATERIALS\n- Print files containing “slick_tire” in TPU 95A.\n- Print all other files in PETG.\n- Optional: use 2 mm metal rods for wheel axles and active-wing hinge pins.\n\nSTARTING SETTINGS\n0.15-0.20 mm layers, 4 walls, 20-30% gyroid infill. Enable build-plate supports for suspension, wing structures, halo and linkages.\n\nIMPORTANT\nPrint in several batches. Do not independently rescale any part. Print and test one moving-wing flap and hinge area before committing to the full set. These meshes were derived from the final visual V5 design; very small details may require a 0.25 mm nozzle or local reinforcement in your slicer.\n\nUse PARTS_AND_MATERIALS.csv as the checklist.\n''')
zip_path='outputs/FORMULA_EV_V5_PRINT_PARTS_ALL.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for fn in sorted(os.listdir(OUT)):z.write(f'{OUT}/{fn}',f'FORMULA_EV_V5_PRINT_PARTS/{fn}')
print('folder',OUT,'stl files',sum(f.endswith('.stl') for f in os.listdir(OUT)),'zip',zip_path)
