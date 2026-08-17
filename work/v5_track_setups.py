import csv,os
OUT='outputs/v5_track_setups_spa_silverstone_monaco';rho=1.225;g=9.80665;unc=.25
setups={
'Spa-Francorchamps':dict(ClA=3.90,ClA_active=2.80,eff=.90,CdA=1.20,CdA_active=.88,ride='28 / 40',wing='L1 4°, L2 7°, L3 10°',rear='10° closed; 28° DRS opening',spring='Stiff heave; medium roll; extra compression margin at Eau Rouge',arb='Medium front / medium rear',camber='Front -3.0°, rear -2.0°',toe='Front 0.05° out; rear 0.10° in',gearing='Long final drive; 345 km/h target',brakes='Medium ducts; bias ~56.5% front',aero='Use active front flaps and rear DRS on all long designated straights',lap='1:41.263',pace='1:47.845',corners=[('La Source',25,'closed'),('Eau Rouge/Raidillon',78,'closed'),('Pouhon',70,'closed'),('Blanchimont',82,'closed'),('Kemmel straight',83.33,'active')]),
'Silverstone':dict(ClA=4.50,ClA_active=3.10,eff=.92,CdA=1.42,CdA_active=.98,ride='27 / 38',wing='L1 7°, L2 11°, L3 15°',rear='14° closed; 28° DRS opening',spring='Stiff heave and roll platform for rapid direction changes',arb='Medium-stiff front / medium rear',camber='Front -3.2°, rear -2.2°',toe='Front 0.08° out; rear 0.12° in',gearing='Medium-long final drive; 330 km/h target',brakes='Medium-small ducts; bias ~56.0% front',aero='High-load corner mode through Copse and Maggotts/Becketts; active aero on straights',lap='1:24.830',pace='1:29.496',corners=[('Village',30,'closed'),('Copse',75,'closed'),('Maggotts/Becketts',68,'closed'),('Stowe',65,'closed'),('Hangar straight',83.33,'active')]),
'Monaco':dict(ClA=5.00,ClA_active=5.00,eff=.88,CdA=1.75,CdA_active=1.75,ride='36 / 48',wing='L1 12°, L2 16°, L3 20°',rear='20° maximum-load setting; DRS disabled',spring='Soft springs and heave; compliant bump/kerb setup',arb='Soft front / soft-medium rear',camber='Front -3.5°, rear -2.5°',toe='Front 0.15° out; rear 0.18° in',gearing='Short final drive; 295 km/h target; aggressive low-speed regen',brakes='Large ducts; bias ~57.5% front',aero='Keep every flap closed in maximum-downforce position; prioritize stability and traction',lap='1:09.041',pace='1:14.565',corners=[('Fairmont hairpin',13.5,'closed'),('Casino Square',48,'closed'),('Tabac',52,'closed'),('Swimming Pool',55.6,'closed'),('Tunnel',72,'closed')])}
rows=[]
for track,s in setups.items():
 for corner,v,mode in s['corners']:
  cla=(s['ClA_active'] if mode=='active' else s['ClA'])*s['eff'];q=.5*rho*v*v;f=q*cla
  rows.append(dict(track=track,location=corner,aero_mode=mode,speed_m_s=v,speed_km_h=v*3.6,effective_ClA_m2=cla,dynamic_pressure_pa=q,downforce_n=f,downforce_kn=f/1000,downforce_kgf=f/g,low_estimate_kn=f*(1-unc)/1000,high_estimate_kn=f*(1+unc)/1000))
with open(OUT+'/V5_TRACK_SPECIFIC_DOWNFORCE.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
with open(OUT+'/V5_TRACK_SETUP_PARAMETERS.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['track','qualifying_prediction','race_pace_prediction','closed_ClA_m2','active_ClA_m2','ride_height_front_rear_mm','front_flaps','rear_wing','spring_platform','anti_roll_bars','camber','toe','gearing','brakes','aero_strategy'])
 for t,s in setups.items():w.writerow([t,s['lap'],s['pace'],s['ClA'],s['ClA_active'],s['ride'],s['wing'],s['rear'],s['spring'],s['arb'],s['camber'],s['toe'],s['gearing'],s['brakes'],s['aero']])
lines=['V5 FORMULA EV — SPA, SILVERSTONE AND MONACO SETUP STUDY','', 'All values are conceptual starting points for the V5 full-size interpretation. Downforce uncertainty is at least +/-25%.','']
for t,s in setups.items():
 lines += [t.upper(),f'Predicted qualifying / race pace: {s["lap"]} / {s["pace"]}',f'Ride height F/R: {s["ride"]} mm',f'Front flaps: {s["wing"]}',f'Rear wing: {s["rear"]}',f'Springs: {s["spring"]}',f'Anti-roll bars: {s["arb"]}',f'Alignment: {s["camber"]}; {s["toe"]}',f'Gearing: {s["gearing"]}',f'Brakes: {s["brakes"]}',f'Active-aero strategy: {s["aero"]}','Downforce points:']
 for r in [q for q in rows if q['track']==t]:lines.append(f'  {r["location"]:<22} {r["speed_m_s"]:>6.2f} m/s  {r["downforce_kn"]:>6.2f} kN ({r["downforce_kgf"]:.0f} kgf), range {r["low_estimate_kn"]:.2f}-{r["high_estimate_kn"]:.2f} kN')
 lines.append('')
lines += ['LIMITATIONS','Not CFD or a seven-post/driver-in-loop model. Tire compound, temperatures, damping curves, steering geometry, exact mass distribution, battery state, motor torque map, wind, wet weather and track evolution are not solved. The alignment and ride-height numbers are starting hypotheses, not safe real-car instructions.']
open(OUT+'/V5_THREE_TRACK_SETUP_REPORT.txt','w').write('\n'.join(lines))
print('\n'.join(lines))
