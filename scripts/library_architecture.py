"""Library exterior from university floor plans, mapped parts and Pfeiffer photos.
The university footprint controls the outer boundary. Member sizes are estimates.
"""
from cad_core import *
from shapely import segmentize

REFERENCE='https://www.perkinseastman.com/projects/university-of-california-santa-barbara-library-addition-and-renewal/'
PART_IDS={'way/221409865':('tower',32.5,8),'way/987524011':('addition',12.4,3),'way/221409859':('ocean',16.0,4)}

def library_parts(p,osm):
    result=[];used=Polygon()
    for osm_id,(name,h,n) in PART_IDS.items():
        f=next(f for f in osm if f['properties'].get('osm_id')==osm_id)
        q=f['poly'].buffer(.8,join_style=2).intersection(p).difference(used)
        result.append((name,q,h,n));used=unary_union([used,q])
    # The glass entrance hall is immediately north of the tower. The previous
    # latitude cuts doubled the tower depth and put this hall at the wrong end.
    paseo=p.intersection(Polygon([(145,9),(231,6.9),(231,23.2),(145,25.3)])).difference(used)
    result.append(('paseo',paseo,9.6,2));used=unary_union([used,paseo])
    result.append(('original',p.difference(used),8.6,2))
    return result

def skin(ms,p,z,h,n,kind,parts):
    # Use only exposed wall faces. A party wall does not receive a window grid.
    neighbors=[(q,hh)for name,q,hh,nn in parts if name!=kind]
    for q in polygons(p):
        for a,b in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
            ln=np.linalg.norm(b-a)
            if ln<2.2:continue
            u=(b-a)/ln;normal=np.array([u[1],-u[0]])
            mid=(a+b)/2;probe=Point(*(mid+normal*.3))
            blocked=max([hh for other,hh in neighbors if other.buffer(.15).contains(probe)],default=0)
            bay=2.85 if kind=='tower' else (5.6 if kind in ['addition','original'] else 3.3)
            count=max(1,int(ln/bay));step=ln/count
            for k in range(n):
                zz=k*h/n+.64;wh=min(h/n-1.05,2.7 if kind=='tower' else 3.25)
                if zz<blocked-.1:continue
                for j in range(count):
                    c=a+u*((j+.5)*step)+normal*.07
                    width=step*(.56 if kind=='tower' else .77)
                    if kind=='addition' and k==2:width=step-.19
                    pane=Polygon([c-u*width/2,c+u*width/2,c+u*width/2+normal*.08,c-u*width/2+normal*.08])
                    ms['DarkGlass'].append(extrusion(pane,z+zz,wh))
                    # Shallow white frames match the deep historic tower reveals;
                    # these end at the opening, never project above the roof.
                    for side in [-1,1]:
                        s=c+u*(width/2+.055)*side
                        strip=Polygon([s-u*.07,s+u*.07,s+u*.07+normal*.15,s-u*.07+normal*.15])
                        ms['WhitePanel'].append(extrusion(strip,z+zz-.08,wh+.16))
                    sill=LineString([c-u*(width/2+.12),c+u*(width/2+.12)]).buffer(.10,cap_style=2)
                    for a0 in polygons(sill):ms['Concrete'].append(extrusion(a0,z+zz-.10,.10))
            for k in range(1,n):
                if k*h/n<blocked-.1:continue
                band=LineString([a+normal*.10,b+normal*.10]).buffer(.09,cap_style=2)
                for a0 in polygons(band):ms['WhitePanel'].append(extrusion(a0,z+k*h/n-.10,.20))

def library_detail(ms,p,z,parts):
    for name,q,h,n in parts:
        for part in polygons(q):
            roof=part.buffer(-.12,join_style=2)
            for a in polygons(roof):ms['RoofPavilion'].append(extrusion(a,z+h,.16))
            # Lower roof edges are not wrapped across the adjoining taller wing.
            edge=part.boundary.buffer(.10,cap_style=2).difference(p.difference(part).buffer(.18))
            for a in polygons(edge):ms['WhitePanel'].append(extrusion(a,z+h+.16,.22))
        skin(ms,q,z,h,n,name,parts)
    # Full-height glass at the east and west Paseo ends and at the new Mountain
    # entry: doors and mullions, not repeated storeys on a solid wall.
    for x,y,width,height in [(153.25,15.1,9.8,9.3),(220.0,24.0,8.2,9.3),(179.0,97.0,10.0,11.9)]:
        if x==179.0:
            a=np.array([x-width/2,y]);b=np.array([x+width/2,y]);normal=np.array([0.,-1.])
        else:a=np.array([x,y-width/2]);b=np.array([x,y+width/2]);normal=np.array([-1. if x<180 else 1.,0.])
        u=(b-a)/np.linalg.norm(b-a)
        panel=Polygon([a,b,b+normal*.12,a+normal*.12]);ms['Glass'].append(extrusion(panel,z+.20,height-.2))
        for at in np.arange(0,width+.1,1.4):
            c=a+u*at+normal*.15;ms['Frame'].append(cylinder((*c,z+.2),(*c,z+height),.045,4))
        for hh in [2.7,4.5,height-.15]:ms['Frame'].append(cylinder((*(a+normal*.15),z+hh),(*(b+normal*.15),z+hh),.055,4))
    # White west-entry portal and a supported shallow steel canopy as photographed.
    for y in [9.8,20.5]:ms['WhitePanel'].append(boxmesh(155.5,y,z,4.8,.65,10.7))
    ms['RoofPavilion'].append(boxmesh(157.4,15.15,z+10.45,9.0,11.6,.30))
    ms['Metal'].append(boxmesh(151.7,15.15,z+4.05,5.3,10.5,.16))
    for y in [10.8,19.5]:ms['Frame'].append(cylinder((149.2,y,z+.1),(149.2,y,z+4.05),.085,8))
    # Roof overhang on the three-storey north addition is shallow, as built.
    addition=next(q for name,q,h,n in parts if name=='addition')
    for q in polygons(addition.buffer(.7,join_style=2)):ms['RoofPavilion'].append(extrusion(q,z+12.36,.22))

def library_landscape(eg,p,base,ground,walkarea,bikearea,footprints):
    # A continuous approach follows the photographed west entrance. The coarse
    # DEM supplies the walk grade; solid treads are fitted below the entry slab.
    approach=box(134.5,10.1,153.0,20.3).difference(footprints)
    for q in polygons(approach):
        m=extrusion(segmentize(q,2),0,.10);m.vertices[:,2]+=ground(m.vertices[:,0],m.vertices[:,1])+.18;eg['Walk'].append(m)
    for k in range(3):
        x=149.1+k*1.20;top=base+.20-(2-k)*.14
        q=box(x,10.15,x+1.22,20.2).difference(footprints)
        for a in polygons(q):
            m=extrusion(a,top-.65,.65);bottom=m.vertices[:,2]<top-.3;m.vertices[bottom,2]=np.minimum(m.vertices[bottom,2],ground(m.vertices[bottom,0],m.vertices[bottom,1])-.2);eg['Concrete'].append(m)
    # Narrow paving joints, lower planters and seats use the existing mapped
    # hardscape/planting perimeter; the bicycle route remains open to the south.
    for yy in [10.2,20.2]:
        for xx in [141.5,145.5]:
            zz=float(ground(xx,yy));eg['Concrete'].append(boxmesh(xx,yy,zz+.10,2.7,.45,.43))
    court=box(165,87,187,96).difference(footprints).difference(bikearea)
    for q in polygons(court):
        m=extrusion(segmentize(q,2),0,.08);m.vertices[:,2]+=ground(m.vertices[:,0],m.vertices[:,1])+.16;eg['Walk'].append(m)
    for xx in [170.5,178.0,184.5]:
        yy=91.2
        if not court.contains(Point(xx,yy)):continue
        zz=float(ground(xx,yy));eg['Concrete'].append(boxmesh(xx,yy,zz+.1,2.6,1.2,.43));eg['Garden'].append(boxmesh(xx,yy,zz+.54,2.35,.95,.09))
        for dx in [-.65,0,.65]:
            m=trimesh.creation.icosphere(subdivisions=1);m.apply_scale([.55,.40,.40]);m.apply_translation([xx+dx,yy,zz+.95]);eg['Sage'].append(m)
    return approach
