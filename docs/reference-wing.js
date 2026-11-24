// Generic NACA 2412 teaching geometry. Not a W11 wing section.
export function buildWing(nx,angle=4,inverted=false){
 const ny=nx*3/10,dx=15/nx,c=3,m=.02,p=.4,t=.12,poly=[],upper=[],lower=[];
 const theta=-angle*Math.PI/180,cs=Math.cos(theta),sn=Math.sin(theta);
 const transform=(x,y)=>{const xx=c*(x-.25),zz=c*y*(inverted?-1:1);return [cs*xx-sn*zz,2.25+sn*xx+cs*zz];};
 for(let i=0;i<=160;i++){const x=(1-Math.cos(Math.PI*i/160))/2;const yt=5*t*(.2969*Math.sqrt(x)-.126*x-.3516*x*x+.2843*x*x*x-.1036*x*x*x*x);const yc=x<p?m/(p*p)*(2*p*x-x*x):m/((1-p)**2)*(1-2*p+2*p*x-x*x);const dy=x<p?2*m/(p*p)*(p-x):2*m/((1-p)**2)*(p-x),a=Math.atan(dy);upper.push(transform(x-yt*Math.sin(a),yc+yt*Math.cos(a)));lower.push(transform(x+yt*Math.sin(a),yc-yt*Math.cos(a)));}
 poly.push(...upper,...lower.reverse());
 const inside=(x,y)=>{let hit=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[i],b=poly[j];if(((a[1]>y)!==(b[1]>y))&&(x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]))hit=!hit;}return hit;};
 const ids=[];const xs=poly.map(p=>p[0]),ys=poly.map(p=>p[1]);const xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys);
 for(let y=Math.max(1,Math.floor(ymin/dx));y<=Math.min(ny-2,Math.ceil(ymax/dx));y++)for(let x=Math.floor((xmin+5)/dx);x<=Math.ceil((xmax+5)/dx);x++)if(inside(-5+(x+.5)*dx,(y+.5)*dx))ids.push(y*nx+x);
 return {nx,ny,xmin_m:-5,xmax_m:10,dx_m:dx,car_length_m:c,car_length_cells:c/dx,solid_indices:ids,region:'wing',title:'Generic NACA 2412 teaching section · NOT W11',view_m:{xmin:-3,xmax:7,zmin:.75,zmax:3.75},particle_band_m:[.76,3.74],seed_regions_m:[[-2.9,6.9,.8,3.7]],vector_box_m:[-1.5,5.5,1,3.5],axis_note:`GENERIC NACA 2412 · angle ${angle}° · ${inverted?'inverted camber':'upright camber'} · Re is chord-based · reduced-Re 2D, not a measured stall angle`,provenance:'Analytically generated NACA 2412 section, separate from the original W11 projections.',limitation:'Low-Re voxel mask, confined domain, impulsive startup. No validated stall angle or forces; changing angle resets the calculation. This is not a dynamic pitching-wing solution.',labels:[]};
}
