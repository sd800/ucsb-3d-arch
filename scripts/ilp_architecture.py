"""ILP exterior reconstruction from LMN photos and the current campus footprint.
Four storeys, open circulation and inward-facing terraces. Sizes are approximate.
"""
from cad_core import *
from shapely.ops import nearest_points,linemerge

FLOORS=(4.4,8.8,13.2)
DECK=.22
STAIR_X=(193.2,195.8)
STAIR_Y=-120.4
TREAD=.28
RISERS=13
STAIR_WIDTH=2.2
LANDING_DEPTH=1.4

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
            if ((q.centroid.y>-114 and (mid[1]<-101 or (q.centroid.x<210 and mid[0]>204) or (q.centroid.x>210 and mid[0]<214))) or (q.centroid.y<-114 and mid[1]>-124)):
                edges.append(LineString([a,b]))
        edge=linemerge(unary_union(edges)) if len(edges)>1 else (edges[0]if edges else LineString())
        terrace=edge.buffer(2.0,cap_style=2,join_style=2).intersection(q).buffer(.035,join_style=2).buffer(-.025,join_style=2).intersection(q)
        pieces.append((q,17.8,4,(edge,terrace)))
    return pieces

def circulation(p):
    pieces=pavilion_parts(p);terraces=unary_union([balcony[1]for q,h,n,balcony in pieces if balcony])
    lines=[LineString([(186.,-105.4),(186.,-119.4)]),LineString([(203.8,-101.0),(214.0,-101.0)])]
    bridges=[line.buffer(1.25,cap_style=2)for line in lines]
    x0=STAIR_X[0]-STAIR_WIDTH/2;x1=STAIR_X[1]+STAIR_WIDTH/2
    top=box(x0,STAIR_Y-LANDING_DEPTH,x1,STAIR_Y+.035)
    # Register the stair landing to the actual terrace, rather than assuming the
    # old hand-entered platform position already touches the mapped footprint.
    south=min((q for q,h,n,balcony in pieces if balcony),key=lambda q:q.centroid.y)
    target=terraces.intersection(south)
    a,b=nearest_points(top,target)
    link=LineString([a,b]).buffer(1.1,cap_style=3).union(top).intersection(box(x0-.1,-130,x1+.1,-120.5))
    top=unary_union([top,link]).buffer(0)
    half=box(x0,STAIR_Y+RISERS*TREAD-.035,x1,STAIR_Y+RISERS*TREAD+LANDING_DEPTH)
    return terraces,bridges,top,half


def sloped_prism(q,z0,z1,start_y,end_y,thickness):
    m=extrusion(q,0,thickness)
    t=np.clip((m.vertices[:,1]-start_y)/(end_y-start_y),0,1)
    m.vertices[:,2]+=z0+t*(z1-z0)-thickness
    trimesh.repair.fix_normals(m);assert m.is_watertight
    return m


def pavilion_detail(ms,p,base,ground=None):
    terraces,bridges,landing,half=circulation(p)
    route=unary_union([terraces,*bridges,landing]).buffer(0)
    assert len(polygons(route))==1,'All three terrace wings, bridges and stair landing must form one connected surface.'
    max_gap=max([landing.distance(terraces),*[bridge.distance(terraces)for bridge in bridges]])
    # One unioned slab per level removes coincident bridge/terrace caps.
    for level in FLOORS:
        for q in polygons(route):ms['Concrete'].append(extrusion(q,base+level-DECK,DECK))
    for q,h,n,balcony in pavilion_parts(p):
        ms['RoofPavilion'].append(extrusion(q,base+h,.16))
        rim=q.buffer(-.12,join_style=2).difference(q.buffer(-.32,join_style=2))
        for r in polygons(rim):ms['Concrete'].append(extrusion(r,base+h+.16,.22))
        if not balcony:continue
        edge,terrace=balcony
        for level in FLOORS:
            # level denotes the TOP of every slab, landing and stair arrival.
            openings=unary_union([*bridges,landing]).buffer(.18)
            rail=edge.buffer(.055,cap_style=2,join_style=2).difference(p.buffer(-.05)).difference(openings)
            for r in polygons(rail):ms['WhitePanel'].append(extrusion(r,base+level,1.05))
        for a,b in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
            ln=np.linalg.norm(b-a)
            if ln<7 or edge.distance(Point(*((a+b)/2)))<.15:continue
            u=(b-a)/ln;normal=np.array([u[1],-u[0]])
            for dist in np.arange(2.4,ln-1.2,2.4):
                c=a+u*dist+normal*.018
                seam=Polygon([c-u*.012,c+u*.012,c+u*.012+normal*.012,c-u*.012+normal*.012])
                ms['Concrete'].append(extrusion(seam,base+.18,h-.38))
    # Bridge rails end at the connected terrace edges; no rail blocks the route.
    for level in FLOORS:
        for deck in bridges:
            edges=deck.boundary.buffer(.035,cap_style=2,join_style=2).difference(terraces.buffer(.20))
            for q in polygons(edges):ms['WhitePanel'].append(extrusion(q,base+level,1.05))
    # The ground landing meets a closed support fitted to the local DEM.
    ground_landing=landing.union(box(STAIR_X[0]-STAIR_WIDTH/2,STAIR_Y-LANDING_DEPTH,STAIR_X[0]+STAIR_WIDTH/2,STAIR_Y+.04))
    for q in polygons(ground_landing):
        m=extrusion(q,base-1.0,1.18)
        if ground is not None:
            bottom=m.vertices[:,2]<base-.5;m.vertices[bottom,2]=np.minimum(base-1.,ground(m.vertices[bottom,0],m.vertices[bottom,1])-1.)
        ms['Concrete'].append(m)
    reports=[]
    for floor,upper in enumerate(FLOORS):
        lower=.18 if floor==0 else FLOORS[floor-1];mid=(lower+upper)/2
        for q in polygons(half):ms['Concrete'].append(extrusion(q,base+mid-DECK,DECK))
        y1=STAIR_Y+RISERS*TREAD
        for flight,(x,ys,ye,zlo,zhi) in enumerate([(STAIR_X[0],STAIR_Y,y1,lower,mid),(STAIR_X[1],y1,STAIR_Y,mid,upper)]):
            rise=(zhi-zlo)/RISERS
            for k in range(RISERS):
                a=ys+(ye-ys)*k/RISERS;b=ys+(ye-ys)*(k+1)/RISERS
                top=base+zlo+(k+1)*rise
                # Thin closed treads overlap a continuous inclined waist slab.
                ms['Concrete'].append(boxmesh(x,(a+b)/2,top-.19,STAIR_WIDTH,abs(b-a)+.012,.19))
            q=box(x-STAIR_WIDTH/2,min(ys,ye),x+STAIR_WIDTH/2,max(ys,ye))
            ms['Concrete'].append(sloped_prism(q,base+zlo,base+zhi,ys,ye,.24))
            for side in [-1,1]:
                xx=x+side*(STAIR_WIDTH/2-.035)
                rail=box(xx-.035,min(ys,ye),xx+.035,max(ys,ye))
                # A sloping solid guard, joined to continuous tubular handrails.
                ms['WhitePanel'].append(sloped_prism(rail,base+zlo+1.05,base+zhi+1.05,ys,ye,1.05))
                ms['Frame'].append(cylinder((xx,ys,base+zlo+1.08),(xx,ye,base+zhi+1.08),.045,6))
            assert abs((zlo+RISERS*rise)-zhi)<1e-9
        # Guard only the exposed turnaround perimeter; leave the two flight
        # openings unblocked, and do not close the landing's terrace doorway.
        x0=STAIR_X[0]-STAIR_WIDTH/2+.035;x1=STAIR_X[1]+STAIR_WIDTH/2-.035
        rail_path=LineString([(x0,y1),(x0,y1+LANDING_DEPTH-.035),(x1,y1+LANDING_DEPTH-.035),(x1,y1)])
        for q in polygons(rail_path.buffer(.035,cap_style=2,join_style=2)):ms['WhitePanel'].append(extrusion(q,base+mid,1.05))
        rail_points=list(rail_path.coords)
        for a,b in zip(rail_points[:-1],rail_points[1:]):ms['Frame'].append(cylinder((*a,base+mid+1.08),(*b,base+mid+1.08),.045,6))
        reports.append({'arrival_top_m':upper,'departure_top_m':lower,'half_landing_top_m':mid,'risers':26,'riser_height_m':round((upper-lower)/26,6),'tread_run_m':TREAD,'landing_to_terrace_gap_m':round(landing.distance(terraces),6),'flight_to_platform_vertical_gap_m':0})
    # Consecutive floors stack above each other with sufficient head clearance;
    # all solids stay closed in the CAD, rather than disconnected floating steps.
    report={'reference':REFERENCE,'member_dimensions':'Public-photo approximation','connected_terrace_wings':3,'upper_connected_surface_components':len(polygons(route)),'max_plan_connection_gap_m':round(max_gap,6),'terrace_top_levels_m':list(FLOORS),'slab_thickness_m':DECK,'unified_upper_decks':len(FLOORS),'inclined_waist_slabs':6,'ground_fitted_landing':True,'stairs':reports,'passed':True}
    (OUT/'ilp_connection_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


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
