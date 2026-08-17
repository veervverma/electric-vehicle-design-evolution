import sys,os
sys.path.insert(0,'work')
import portfolio_v3 as p
from advanced_sedan import translate,write_stl,bounds
out='outputs/portfolio_ev_sedan_v3'
assembled=[]
for name,M,(x,y,z),mat in p.I:
    assembled += translate(M,x,y,z)
write_stl(out+'/EV_SEDAN_V3_COMPLETE_ASSEMBLED.stl',assembled,'EV_SEDAN_V3_COMPLETE_ASSEMBLED')
print('assembled:',bounds(assembled),'triangles:',len(assembled))

# Also provide an exploded STL for technical viewing.
exploded=[]
for name,M,(tx,ty,tz),mat in p.I:
    if 'glasshouse' in name: tz+=55
    elif 'hood' in name: tx-=25; tz+=42
    elif 'interior' in name: tz+=25
    elif 'wing' in name: tx+=20; tz+=30
    elif 'Front steering' in name: tx-=20; tz-=28
    elif 'Rear suspension' in name: tx+=20; tz-=28
    elif any(k in name for k in ('tire','rim','rotor','retainer')): ty += -28 if ty<0 else 28
    elif 'battery' in name: tz-=32
    elif 'motor' in name: tz-=12; tx+=20
    elif 'Inverter' in name: tz+=15
    elif 'Charging' in name: tx+=22; tz+=12
    exploded += translate(M,tx,ty,tz)
write_stl(out+'/EV_SEDAN_V3_EXPLODED_REFERENCE.stl',exploded,'EV_SEDAN_V3_EXPLODED_REFERENCE')
print('exploded:',bounds(exploded),'triangles:',len(exploded))
