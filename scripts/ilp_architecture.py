"""ILP exterior reconstruction from LMN photos and the current campus footprint.
Four storeys, open circulation and inward-facing terraces. Sizes are approximate.
"""
from cad_core import *

REFERENCE='https://lmnarchitects.com/project/classroom-building-university-of-california'

def pavilion_parts(p):
    pieces=[]
    for q in polygons(p):
        if q.area<150:pieces.append((q,4.0,1,None));continue
        # The two curving sides face the open east/west paseo. Satellite/LMN
        # photographs show balconies here, not free-standing facade fins.
        edges=[]
        for a,b in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
            mid=(a+b)/2
            if (q.centroid.y>-114 and mid[1]<-101) or (q.centroid.y<-114 and mid[1]>-124):
                edges.append(LineString([a,b]))
        edge=unary_union(edges) if edges else LineString()
        terrace=edge.buffer(2.0,cap_style=2,join_style=2).intersection(q)
        pieces.append((q,17.8,4,(edge,terrace)))
    return pieces

def pavilion_detail(ms,p,base):
    for q,h,n,balcony in pavilion_parts(p):
        # A thin continuous membrane and low parapet, with no roof rods.
        ms['RoofPavilion'].append(extrusion(q,base+h,.16))
        rim=q.buffer(-.12,join_style=2).difference(q.buffer(-.32,join_style=2))
        for r in polygons(rim):ms['Concrete'].append(extrusion(r,base+h+.16,.22))
        if not balcony:continue
        edge,terrace=balcony
        for z in [4.4,8.8,13.2]:
            for r in polygons(terrace):ms['Concrete'].append(extrusion(r,base+z,.22))
            # Opaque, thin perforated-metal guard panels follow the mapped curve.
            rail=edge.buffer(.055,cap_style=2,join_style=2).difference(p.buffer(-.05))
            for r in polygons(rail):ms['Metal'].append(extrusion(r,base+z+.24,1.03))
        # Shallow panel seams at the outward faces, clipped to each local wing.
        for a,b in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
            ln=np.linalg.norm(b-a)
            if ln<7 or edge.distance(Point(*((a+b)/2)))<.15:continue
            u=(b-a)/ln;normal=np.array([u[1],-u[0]])
            for s in np.arange(2.4,ln-1.2,2.4):
                c=a+u*s+normal*.018
                seam=Polygon([c-u*.012,c+u*.012,c+u*.012+normal*.012,c-u*.012+normal*.012])
                ms['Concrete'].append(extrusion(seam,base+.18,h-.38))
    # Three upper bridges between the two mapped masses, with closed decks and
    # shallow guard panels. The corridor remains open at ground level.
    for z in [4.4,8.8,13.2]:
        for start,end in [((188.0,-107.0),(188.0,-118.0)),((206.3,-109.0),(213.2,-109.0))]:
            deck=LineString([start,end]).buffer(1.25,cap_style=2)
            for r in polygons(deck):ms['Concrete'].append(extrusion(r,base+z,.22))
            a=np.array(start);b=np.array(end);u=(b-a)/np.linalg.norm(b-a);normal=np.array([-u[1],u[0]])
            for side in [-1,1]:
                rail=LineString([a+normal*1.20*side,b+normal*1.20*side]).buffer(.035,cap_style=2)
                for r in polygons(rail):ms['Metal'].append(extrusion(r,base+z+.24,1.03))
    # A supported two-flight stair for each level; no single floating ladder.
    for floor in range(3):
        z=floor*4.4
        for flight in range(2):
            for k in range(13):
                y=-118.0+k*.28 if flight==0 else -114.64-k*.28
                x=198.4 if flight==0 else 201.4
                ms['Concrete'].append(boxmesh(x,y,base+z+flight*2.2,2.4,.29,(k+1)*2.2/13))
        ms['Concrete'].append(boxmesh(199.9,-114.5,base+z+2.2-.22,5.4,1.35,.22))
        ms['Concrete'].append(boxmesh(199.9,-118.35,base+z+4.4-.22,5.4,1.35,.22))
    return {'reference':REFERENCE,'storeys':4,'roof_fins':False,'terrace_levels_m':[4.4,8.8,13.2],'member_dimensions':'Public-photo approximation'}


def pavilion_facade(ms,p,z,h,levels):
    for q in polygons(p):
        for a,b in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
            ln=np.linalg.norm(b-a)
            if ln<4:continue
            u=(b-a)/ln;normal=np.array([u[1],-u[0]])
            for dist in np.arange(2.0,ln-1.2,4.5):
                c=a+u*dist+normal*.065
                for floor in range(levels):
                    zz=z+floor*h/levels+.72;wh=min(3.25,h/levels-1.0)
                    # Narrow vertical openings like the concrete panel elevations.
                    pane=Polygon([c-u*.48,c+u*.48,c+u*.48+normal*.07,c-u*.48+normal*.07]);ms['DarkGlass'].append(extrusion(pane,zz,wh))
                    divider=Polygon([c-u*.025,c+u*.025,c+u*.025+normal*.10,c-u*.025+normal*.10]);ms['Frame'].append(extrusion(divider,zz,wh))
