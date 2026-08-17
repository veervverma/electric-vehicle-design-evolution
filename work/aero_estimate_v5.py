import csv,math,os
OUT='outputs/aero_estimate_v5'
rho=1.225;g=9.80665
# Effective coefficient-area assumptions for a full-size conceptual Formula car.
ClA_corner=4.60       # m^2, closed/high-downforce aero
ClA_straight=3.20     # m^2, synchronized active front + rear DRS
CdA_corner=1.55       # m^2
CdA_straight=1.05     # m^2
corner_eff=0.92       # yaw/roll/ride-height loss in a real corner
unc=0.25
scenarios=[('Hairpin',25.0,'corner'),('Slow corner',35.0,'corner'),('Medium corner',50.0,'corner'),('Fast corner',65.0,'corner'),('Very fast corner',75.0,'corner'),('300 km/h straight',300/3.6,'straight'),('300 km/h corner-equivalent',300/3.6,'corner')]
rows=[]
for name,v,mode in scenarios:
 q=.5*rho*v*v
 if mode=='corner':cla=ClA_corner*corner_eff;cda=CdA_corner
 else:cla=ClA_straight;cda=CdA_straight
 df=q*cla;drag=q*cda;power=drag*v
 rows.append(dict(scenario=name,speed_m_s=v,speed_km_h=v*3.6,mode=mode,dynamic_pressure_pa=q,downforce_n=df,downforce_kgf=df/g,downforce_low_n=df*(1-unc),downforce_high_n=df*(1+unc),drag_n=drag,aero_power_kw=power/1000))
with open(OUT+'/downforce_estimate.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)

# Force contribution estimates at 300 km/h.
v=300/3.6;q=.5*rho*v*v
contrib_corner=[('Underfloor + diffuser',.58),('Front wing',.18),('Rear wing',.17),('Body/other',.07)]
contrib_straight=[('Underfloor + diffuser',.78),('Front active wing',.08),('Rear DRS wing',.08),('Body/other',.06)]
with open(OUT+'/downforce_breakdown_300kph.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['mode','component','fraction','downforce_n'])
 for mode,total,cs in [('corner_closed',q*ClA_corner*corner_eff,contrib_corner),('straight_active',q*ClA_straight,contrib_straight)]:
  for n,fr in cs:w.writerow([mode,n,fr,total*fr])

# Lightweight SVG chart from actual calculated values.
W,H=1200,720;ml,mr,mt,mb=95,55,75,90;pw=W-ml-mr;ph=H-mt-mb
vs=[i for i in range(0,86,2)]
def force(v,mode):return .5*rho*v*v*(ClA_corner*corner_eff if mode=='corner' else ClA_straight)/1000
ymax=22
def pts(mode):return ' '.join(f'{ml+pw*v/85:.1f},{mt+ph*(1-force(v,mode)/ymax):.1f}' for v in vs)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="#f4f6f8"/><text x="{ml}" y="42" font-family="Arial" font-size="30" font-weight="bold" fill="#17212b">V5 Formula EV — Estimated Downforce vs Speed</text>']
for y in range(0,23,2):
 py=mt+ph*(1-y/ymax);svg.append(f'<line x1="{ml}" y1="{py}" x2="{W-mr}" y2="{py}" stroke="#d5dbe1"/><text x="{ml-15}" y="{py+6}" text-anchor="end" font-family="Arial" font-size="16" fill="#53606d">{y}</text>')
for x in range(0,86,10):
 px=ml+pw*x/85;svg.append(f'<line x1="{px}" y1="{mt}" x2="{px}" y2="{H-mb}" stroke="#e0e4e8"/><text x="{px}" y="{H-mb+28}" text-anchor="middle" font-family="Arial" font-size="16" fill="#53606d">{x}</text>')
svg += [f'<polyline points="{pts("corner")}" fill="none" stroke="#d42c2c" stroke-width="5"/>',f'<polyline points="{pts("straight")}" fill="none" stroke="#2474b5" stroke-width="5"/>',f'<text x="{ml+20}" y="{mt+28}" font-family="Arial" font-size="17" fill="#d42c2c">Closed aero / corner estimate</text>',f'<text x="{ml+20}" y="{mt+54}" font-family="Arial" font-size="17" fill="#2474b5">Active front + rear DRS / straight estimate</text>',f'<text x="{W/2}" y="{H-25}" text-anchor="middle" font-family="Arial" font-size="20" fill="#17212b">Speed (m/s)</text>',f'<text x="25" y="{H/2}" transform="rotate(-90 25 {H/2})" text-anchor="middle" font-family="Arial" font-size="20" fill="#17212b">Downforce (kN)</text>','</svg>']
open(OUT+'/downforce_chart.svg','w').write(''.join(svg))

straight=next(r for r in rows if r['scenario']=='300 km/h straight');corner=next(r for r in rows if r['scenario']=='300 km/h corner-equivalent')
report=f'''V5 FORMULA EV — FIRST-ORDER AERODYNAMIC ESTIMATE\n\nSCOPE\nFull-size conceptual interpretation of the V5 design. This is not CFD or wind-tunnel validation. It uses the aerodynamic force relation F = 0.5*rho*V^2*ClA.\n\nASSUMPTIONS\nAir density: {rho:.3f} kg/m^3 (standard sea-level day)\nClosed/high-downforce effective ClA: {ClA_corner:.2f} m^2\nCorner efficiency factor for yaw, roll and ride-height disturbance: {corner_eff:.2f}\nActive-front-wing + rear-DRS effective ClA: {ClA_straight:.2f} m^2\nCorner CdA: {CdA_corner:.2f} m^2\nStraight active-aero CdA: {CdA_straight:.2f} m^2\nUncertainty band: +/-{unc*100:.0f}%\n\n300 KM/H STRAIGHT\nSpeed: {straight['speed_m_s']:.2f} m/s\nDynamic pressure: {straight['dynamic_pressure_pa']:.0f} Pa\nEstimated downforce: {straight['downforce_n']/1000:.2f} kN ({straight['downforce_kgf']:.0f} kgf)\nPlausible range: {straight['downforce_low_n']/1000:.2f}-{straight['downforce_high_n']/1000:.2f} kN\nEstimated drag: {straight['drag_n']/1000:.2f} kN\nAerodynamic power required: {straight['aero_power_kw']:.0f} kW\n\n300 KM/H, CLOSED-AERO CORNER EQUIVALENT\nSpeed: {corner['speed_m_s']:.2f} m/s\nEstimated downforce: {corner['downforce_n']/1000:.2f} kN ({corner['downforce_kgf']:.0f} kgf)\nPlausible range: {corner['downforce_low_n']/1000:.2f}-{corner['downforce_high_n']/1000:.2f} kN\n\nLIMITATIONS\nThe GLB is a visual/printing mesh, not a CFD-ready watertight aerodynamic surface. The estimate does not solve pressure fields, turbulence, wheel rotation, moving ground, tire deformation, porpoising, crosswind, cooling flow or aeroelastic wing movement. Reliable figures require CFD with a moving ground and rotating wheels, followed by wind-tunnel or track correlation.\n'''
open(OUT+'/AERO_SIMULATION_REPORT.txt','w').write(report)
print(report)
