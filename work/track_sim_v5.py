import csv,os,math
OUT='outputs/v5_wind_tunnel_and_track_sim';os.makedirs(OUT,exist_ok=True)
# 2026 FIA calendar amended 26 March 2026: 22 venues.
# Average qualifying speeds are reduced-order circuit-profile assumptions for V5, not measured laps.
tracks=[
('Australia','Melbourne',5.278,'mixed',251,0.058),('China','Shanghai',5.451,'mixed',218,0.070),('Japan','Suzuka',5.807,'high-downforce',239,0.060),('Miami','Miami',5.412,'street-mixed',225,0.065),('Canada','Montreal',4.361,'low-drag',220,0.060),('Monaco','Monaco',3.337,'maximum-downforce',174,0.080),('Barcelona-Catalunya','Barcelona',4.657,'high-downforce',235,0.060),('Austria','Spielberg',4.318,'power',246,0.060),('Great Britain','Silverstone',5.891,'high-speed',250,0.055),('Belgium','Spa-Francorchamps',7.004,'high-speed',249,0.065),('Hungary','Hungaroring',4.381,'maximum-downforce',210,0.070),('Netherlands','Zandvoort',4.259,'high-downforce',221,0.070),('Italy','Monza',5.793,'minimum-drag',265,0.050),('Madrid','Madring',5.416,'street-mixed',212,0.070),('Azerbaijan','Baku',6.003,'street-low-drag',216,0.065),('Singapore','Marina Bay',4.940,'street-high-downforce',199,0.080),('United States','Austin',5.513,'mixed',218,0.065),('Mexico','Mexico City',4.304,'altitude-mixed',204,0.070),('Brazil','Interlagos',4.309,'mixed',228,0.070),('Las Vegas','Las Vegas Strip',6.201,'minimum-drag',243,0.060),('Qatar','Lusail',5.419,'high-speed',243,0.065),('Abu Dhabi','Yas Marina',5.281,'mixed',232,0.060)]
def fmt(s):
 m=int(s//60);return f'{m}:{s-60*m:06.3f}'
rows=[]
for i,(gp,circuit,L,kind,vavg,delta) in enumerate(tracks,1):
 q=3600*L/vavg;race_fast=q*1.025;pace=q*(1+delta)
 uncq=5.0 if gp=='Madrid' else max(1.8,q*.025);uncp=max(3.0,pace*.04)
 rows.append({'round':i,'grand_prix':gp,'circuit':circuit,'length_km':L,'track_type':kind,'assumed_qual_avg_speed_km_h':vavg,'assumed_qual_avg_speed_m_s':vavg/3.6,'predicted_qualifying_seconds':q,'predicted_qualifying_lap':fmt(q),'predicted_race_fastest_seconds':race_fast,'predicted_race_fastest_lap':fmt(race_fast),'predicted_green_flag_race_pace_seconds':pace,'predicted_green_flag_race_pace':fmt(pace),'qualifying_uncertainty_seconds':uncq,'race_pace_uncertainty_seconds':uncp})
with open(OUT+'/V5_2026_TRACK_SIMULATION.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
# Text report.
lines=['V5 FORMULA EV — 2026 CALENDAR REDUCED-ORDER LAP SIMULATION','', 'These are conceptual predictions, not actual CFD/vehicle-dynamics results. “Fastest lap” is the predicted low-fuel qualifying lap; race fastest is a late-race low-fuel estimate; race pace is a representative dry green-flag lap with fuel and tire allowance.','',f'{"Rnd":>3}  {"Venue":<22} {"Qualifying":>11} {"Race fastest":>13} {"Race pace":>11}']
for r in rows:lines.append(f'{r["round"]:>3}  {r["circuit"]:<22} {r["predicted_qualifying_lap"]:>11} {r["predicted_race_fastest_lap"]:>13} {r["predicted_green_flag_race_pace"]:>11}')
lines += ['','MODEL LIMITATIONS','The model uses track length, circuit category and assumed average speed calibrated to modern formula-car pace. It does not solve a racing line, braking zones, tire temperatures, battery state, motor torque curve, gear ratios, elevation, weather, traffic, safety cars or strategy. Typical uncertainty is about +/-2.5% for qualifying and +/-4% for race pace; Madrid is less certain because it is new. An electric car sustaining these laps also requires an energy-storage and thermal model that is not yet defined.']
open(OUT+'/V5_2026_TRACK_SIMULATION_REPORT.txt','w').write('\n'.join(lines))
# SVG bar chart for qualifying and race pace.
W,H=1500,1050;left=270;top=75;rowh=40;scale=8.3
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="#f4f6f8"/><text x="55" y="42" font-family="Arial" font-size="28" font-weight="bold" fill="#17212b">V5 Formula EV — Predicted 2026 Lap Times</text>']
for i,r in enumerate(rows):
 y=top+i*rowh;svg.append(f'<text x="{left-12}" y="{y+19}" text-anchor="end" font-family="Arial" font-size="15" fill="#27313b">{r["circuit"]}</text>');qw=r['predicted_qualifying_seconds']*scale;pw=r['predicted_green_flag_race_pace_seconds']*scale;svg.append(f'<rect x="{left}" y="{y+2}" width="{pw:.1f}" height="26" fill="#a9c7dd"/><rect x="{left}" y="{y+6}" width="{qw:.1f}" height="18" fill="#2574a9"/><text x="{left+pw+8}" y="{y+20}" font-family="Arial" font-size="14" fill="#27313b">Q {r["predicted_qualifying_lap"]} • race {r["predicted_green_flag_race_pace"]}</text>')
svg.append('</svg>');open(OUT+'/V5_2026_LAP_TIME_CHART.svg','w').write(''.join(svg))
print('\n'.join(lines))
