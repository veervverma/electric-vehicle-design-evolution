from pathlib import Path
import struct

ROOT=Path('/Users/vivek.verma/Documents/Codex/2026-07-30/electric-car-chassis-design')
HTML=Path('/Users/vivek.verma/.codex/visualizations/2026/07/30/019fb44c-9d93-7d50-a84d-6521e6f25fa1/v5-v6-full-car-wind-tunnel.html')
GEOM=ROOT/'outputs/V6_CFD_REBUILD/geometry'

# Exact full-model bounds from the attached combined V6 STL.
xmin,xmax=-2850.0,2600.0
zmin,zmax=0.0,1072.20874
left,right,ground=70.0,820.0,270.0
scale=(right-left)/(xmax-xmin)

def read_triangles(path):
    data=path.read_bytes()
    n=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*n:
        raise ValueError(f'Unexpected STL layout: {path}')
    out=[]
    for i in range(n):
        vals=struct.unpack_from('<12fH',data,84+i*50)
        v=vals[3:12]
        pts=[]
        ys=[]
        for j in range(0,9,3):
            x,y,z=v[j:j+3]
            px=left+(x-xmin)*scale
            py=ground-(z-zmin)*scale
            pts.append((px,py)); ys.append(y)
        area=abs((pts[1][0]-pts[0][0])*(pts[2][1]-pts[0][1])-(pts[2][0]-pts[0][0])*(pts[1][1]-pts[0][1]))*.5
        if area>=0.02:
            out.append((sum(ys)/3,pts))
    out.sort(key=lambda item:item[0])
    return out

groups=[
 ('mesh-floor',['floor','venturi','plank','skids','diffuser']),
 ('mesh-body',['body','nose','sidepods','canopy','halo','cooling']),
 ('mesh-suspension',['suspension']),
 ('mesh-wheels',['wheelFL','wheelFR','wheelRL','wheelRR']),
 ('mesh-aero',['frontWing','frontFlaps','rearWing','rearFlap']),
]
parts=['<g class="v6-car v6-actual-mesh" data-source="V6_FULL_SCALE_CFD_SURFACES.stl">']
tri_count=0
for cls,names in groups:
    parts.append(f'<g class="{cls}">')
    for name in names:
        tris=read_triangles(GEOM/f'{name}.stl')
        tri_count+=len(tris)
        parts.append(f'<g data-component="{name}">')
        for _,pts in tris:
            coords=' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
            parts.append(f'<polygon points="{coords}"></polygon>')
        parts.append('</g>')
    parts.append('</g>')
# Actual wheel centers from the V6 full-scale model: front x=-1.8m, rear x=+1.8m, z=0.36m.
def mapx(x): return left+(x-xmin)*scale
def mapz(z): return ground-z*scale
fx,rx=mapx(-1800),mapx(1800); wy=mapz(360); rr=360*scale
parts.append(f'''<g class="actual-wheel-details">
  <g class="wheel-overlay front-wheel"><circle class="actual-rim" cx="{fx:.1f}" cy="{wy:.1f}" r="{rr*.52:.1f}"></circle><g class="spokes"><path d="M{fx:.1f} {wy-rr*.42:.1f} V{wy+rr*.42:.1f} M{fx-rr*.42:.1f} {wy:.1f} H{fx+rr*.42:.1f} M{fx-rr*.30:.1f} {wy-rr*.30:.1f} L{fx+rr*.30:.1f} {wy+rr*.30:.1f} M{fx+rr*.30:.1f} {wy-rr*.30:.1f} L{fx-rr*.30:.1f} {wy+rr*.30:.1f}"></path></g></g>
  <g class="wheel-overlay rear-wheel"><circle class="actual-rim" cx="{rx:.1f}" cy="{wy:.1f}" r="{rr*.52:.1f}"></circle><g class="spokes"><path d="M{rx:.1f} {wy-rr*.42:.1f} V{wy+rr*.42:.1f} M{rx-rr*.42:.1f} {wy:.1f} H{rx+rr*.42:.1f} M{rx-rr*.30:.1f} {wy-rr*.30:.1f} L{rx+rr*.30:.1f} {wy+rr*.30:.1f} M{rx+rr*.30:.1f} {wy-rr*.30:.1f} L{rx-rr*.30:.1f} {wy+rr*.30:.1f}"></path></g></g>
</g>''')
parts.append('<text class="actual-source-label" x="445" y="118">ACTUAL V6 STL SIDE PROJECTION</text>')
parts.append('</g>')
replacement='\n'.join(parts)+'\n          '

s=HTML.read_text()
start=s.index('<g class="v6-car">')
end=s.index('<g class="load-arrows v6-load"',start)
s=s[:start]+replacement+s[end:]
s=s.replace('Longer throat, progressive diffuser and cleaner wake recovery','Actual side profile projected from the attached V6 STL')
s=s.replace('Air particles travel over the multi-element front wing, wheels, streamlined body, rear wing and stronger Venturi floor.', 'The exact side projection of the attached V6 STL is shown with airflow over its front wing, wheels, body, rear wing and Venturi floor.')
s=s.replace('Conceptual moving-ground wind-tunnel visualization.', 'The V6 side silhouette is projected directly from V6_FULL_SCALE_CFD_SURFACES.stl; the V5 remains its fixed reference visualization. Conceptual moving-ground wind-tunnel visualization.')
css='''
#full-car-wind-tunnel .v6-actual-mesh polygon { vector-effect: non-scaling-stroke; }
#full-car-wind-tunnel .v6-actual-mesh .mesh-floor polygon { fill: color-mix(in srgb, var(--viz-series-2) 32%, var(--muted)); stroke: var(--viz-series-2); stroke-width: 0.18; }
#full-car-wind-tunnel .v6-actual-mesh .mesh-body polygon { fill: var(--muted); stroke: color-mix(in srgb, var(--muted-foreground) 55%, transparent); stroke-width: 0.16; }
#full-car-wind-tunnel .v6-actual-mesh .mesh-suspension polygon { fill: color-mix(in srgb, var(--muted-foreground) 70%, var(--card)); stroke: var(--muted-foreground); stroke-width: 0.20; }
#full-car-wind-tunnel .v6-actual-mesh .mesh-wheels polygon { fill: color-mix(in srgb, var(--foreground) 72%, var(--card)); stroke: var(--foreground); stroke-width: 0.18; }
#full-car-wind-tunnel .v6-actual-mesh .mesh-aero polygon { fill: color-mix(in srgb, var(--viz-series-2) 46%, var(--muted)); stroke: var(--viz-series-2); stroke-width: 0.24; }
#full-car-wind-tunnel .v6-actual-mesh .actual-rim { fill: var(--card); stroke: var(--viz-series-2); stroke-width: 2; }
#full-car-wind-tunnel .v6-actual-mesh .spokes path { fill: none; stroke: var(--viz-series-2); stroke-width: 1.7; }
#full-car-wind-tunnel .v6-actual-mesh .actual-source-label { fill: var(--muted-foreground); font-size: 10px; text-anchor: middle; letter-spacing: 0.08em; }
'''
s=s.replace('</style>',css+'</style>')
# Fix wheel animation centers to the projected coordinates now embedded from the STL.
s=s.replace("if (v6Front) v6Front.setAttribute('transform', `rotate(${wheelAngle.toFixed(1)} 263 216)`);",f"if (v6Front) v6Front.setAttribute('transform', `rotate(${{wheelAngle.toFixed(1)}} {fx:.1f} {wy:.1f})`);")
s=s.replace("if (v6Rear) v6Rear.setAttribute('transform', `rotate(${wheelAngle.toFixed(1)} 699 216)`);",f"if (v6Rear) v6Rear.setAttribute('transform', `rotate(${{wheelAngle.toFixed(1)}} {rx:.1f} {wy:.1f})`);")
HTML.write_text(s)
print('embedded projected triangles',tri_count)
print('scale px/mm',scale,'front center',fx,wy,'rear center',rx,wy)
print('html bytes',HTML.stat().st_size)
