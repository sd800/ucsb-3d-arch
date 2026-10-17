"""Storke Tower and sunken Communications Plaza, interpreted from owner photographs.

The 53.34 m peak and 61 bells are published. Secondary dimensions, board joints,
carillon mounts and courtyard grades are photo/map approximations, not a survey.
"""
from cad_core import *
from highlight_finish import bell_mesh

REFERENCES=[
 'https://yang.chem.ucsb.edu/contact',
 'https://conferences.ucsb.edu/summer-conferences/attendee-information',
 'https://news.ucsb.edu/2014/014151/bells',
 'https://www.campuscalendar.ucsb.edu/storke_tower',
 'https://dailynexus.com/interactives/storke-tower-carillon/',
]
REPORT={}

def add(ms,g,z,h,mat='StorkeConcrete'):
    for q in polygons(g):ms[mat].append(extrusion(q,z,h))

def arch_profile(width,spring,rise=None,sill=0):
    rise=width/2 if rise is None else rise
    pts=[(-width/2,sill),(width/2,sill),(width/2,spring)]
    pts += [(width/2*math.cos(a),spring+rise*math.sin(a))for a in np.linspace(0,math.pi,33)[1:]]
    return Polygon(pts)

def profile_mesh(profile,c,u,n,z,depth,thickness):
    for q in polygons(profile):
        m=extrusion(q,0,thickness);v=m.vertices.copy()
        m.vertices=np.column_stack((c[0]+v[:,0]*u[0]+(depth+v[:,2])*n[0],c[1]+v[:,0]*u[1]+(depth+v[:,2])*n[1],z+v[:,1]))
        trimesh.repair.fix_normals(m);assert m.is_watertight
        yield m

def local_frame(p):
    q=max(polygons(p),key=lambda q:q.area);cc=np.array(q.minimum_rotated_rectangle.exterior.coords)[:4]
    u=max([cc[1]-cc[0],cc[2]-cc[1]],key=lambda x:abs(x[0])/np.linalg.norm(x));u/=np.linalg.norm(u)
    if u[0]<0:u=-u
    v=np.array([-u[1],u[0]]);c=np.array(q.centroid.coords[0]);uv=(cc-c)@np.column_stack([u,v])
    return c,u,v,np.ptp(uv[:,0]),np.ptp(uv[:,1])

def build_storke(ms,p,z,h):
    c,u,v,w,d=local_frame(p);t=.48
    def rect(x,y,sx,sy,zz,hh,mat='StorkeConcrete'):
        center=c+u*x+v*y;q=Polygon([center+u*a+v*b for a,b in [(-sx/2,-sy/2),(sx/2,-sy/2),(sx/2,sy/2),(-sx/2,sy/2)]])
        add(ms,q,z+zz,hh,mat)
    base_top=7.4;belfry_sill=h-12.1;cap=.78;apertures=[]
    faces=[(u,v,d,w),(-u,-v,d,w),(v,-u,w,d),(-v,u,w,d)]
    # Walls, with true subtracted openings. The shaft is a closed concrete
    # enclosure, not a four-post staircase skeleton with invented clock faces.
    for normal,tangent,width,depth in faces:
        center=c+normal*depth/2;wall=box(-width/2,0,width/2,h)
        base_open=arch_profile(width*.66,2.65,width*.33,sill=-.04)
        wall=wall.difference(base_open)
        span=width*.86;bay=span/3;opening_width=bay*.61
        for offset in [-bay,0,bay]:
            opening=affinity.translate(arch_profile(opening_width,h-2.4,opening_width/2,sill=belfry_sill),offset,0)
            wall=wall.difference(opening)
            apertures.append({'face_normal':normal.tolist(),'center_offset':float(offset),'sill_m':belfry_sill,'spring_m':h-2.4,'width_m':opening_width})
        # Square-corner overlap is inside the wall thickness, so the exterior
        # profiles meet without a daylight crack or stacked coincident faces.
        ms['StorkeConcrete'].extend(profile_mesh(wall,center,tangent,normal,z,-t,t))
        # Board-formed grain and construction pours follow concrete only.
        for offset in np.arange(-width/2+.28,width/2-.12,.44):
            strip=box(offset-.010,0,offset+.010,h-.12).intersection(wall)
            ms['StorkeJoint'].extend(profile_mesh(strip,center,tangent,normal,z,.014,.012))
        for zz in [7.4,13.8,20.2,26.6,33.0,belfry_sill-.20,h-.78]:
            strip=box(-width/2,zz-.017,width/2,zz+.017).intersection(wall)
            ms['StorkeJoint'].extend(profile_mesh(strip,center,tangent,normal,z,.016,.014))
        # Narrow supported lip follows the base arch; no painted dark disk.
        surround=base_open.buffer(.065,join_style=2).difference(base_open).intersection(box(-width/2,0,width/2,base_top))
        ms['StorkePale'].extend(profile_mesh(surround,center,tangent,normal,z,.025,.055))
    rect(0,0,w-2*t,d-2*t,base_top-.28,.28)
    rect(0,0,w-2*t,d-2*t,h-cap,cap)
    # The lower core and visible entrance stair are sheltered by the arches.
    rect(-w*.12,0,1.65,2.3,-.45,7.55)
    rect(-w*.12,-1.18,.90,.04,.10,2.15,'DarkGlass')
    for k in range(14):
        rect(w*.24,-d*.34+k*.27,1.50,.28,-.04,.15*(k+1),'StorkeConcrete')
    # Railings follow the real lower stair; no rails continue up the facade.
    for side in [-1,1]:
        a=c+u*(w*.24+side*.70)-v*d*.34;b=a+v*3.51
        ms['Frame'].append(cylinder((*a,z+1.02),(*b,z+3.12),.035,6))
        for k in range(0,14,2):
            at=a+v*k*.27;ms['Frame'].append(cylinder((*at,z+k*.15),(*at,z+k*.15+1.02),.026,5))
    # The base has low metal railings, supported pickets and concrete corner
    # posts. These stay at the entrance level, rather than climbing the shaft.
    for normal,tangent,width,depth in faces:
        for side in [-1,1]:
            center=c+normal*(depth/2+.08)+tangent*(side*(width/4+.42))
            length=width/2-.84
            a=center-tangent*length/2;b=center+tangent*length/2
            for zz in [.24,1.13]:ms['Frame'].append(cylinder((*a,z+zz),(*b,z+zz),.028,6))
            for q in np.linspace(0,1,max(2,int(length/.20))):
                at=a+(b-a)*q;ms['Frame'].append(cylinder((*at,z+.24),(*at,z+1.13),.018,5))
    for x in [-w/2,w/2]:
        for y in [-d/2,d/2]:rect(x,y,.36,.36,-.03,1.44,'StorkePale')
    # Carillon racks sit behind the long arched openings. Bell positions and
    # sizes are interpreted; the owner, not the mesh count, documents 61 bells.
    bell_count=0
    for face,(normal,tangent,width,depth)in enumerate(faces):
        count=16 if face==0 else 15
        for row in range(4):
            zz=belfry_sill+.65+row*2.25
            count_row=min(4,count-row*4)
            if count_row<=0:continue
            line_center=c+normal*(depth/2-1.15)
            a=line_center-tangent*(width*.36);b=line_center+tangent*(width*.36)
            ms['Frame'].append(cylinder((*a,z+zz+1.65),(*b,z+zz+1.65),.075,8))
            for col in range(count_row):
                at=line_center+tangent*(col-(count_row-1)/2)*1.12
                radius=.58*(.70**row)*(1-col*.07);height=radius*1.95
                ms['BellMetal'].append(bell_mesh([*at,z+zz+1.48-height],radius,height,20));bell_count+=1
                ms['Frame'].append(cylinder((*at,z+zz+1.48),(*at,z+zz+1.65),.055,6))
        for side in [-1,1]:
            at=c+normal*(depth/2-1.15)+tangent*width*.36*side
            ms['Frame'].append(cylinder((*at,z+belfry_sill+.30),(*at,z+h-1.10),.085,8))
    assert bell_count==61
    REPORT.update({'height_m':h,'footprint_m':[round(w,3),round(d,3)],'solid_shaft_from_m':base_top,'belfry_sill_m':belfry_sill,'base_arches':4,'belfry_openings':apertures,'bells':bell_count,'clock_faces':0,'references':REFERENCES,'limits':'Published overall height and bell count; secondary widths, wall thickness, bell mounts, board joints and court grades are interpretations of public photographs and mapped plans.'})
    return [{'name':'closed-concrete-shaft','height_m':h,'base_arches':4,'belfry_arches':12,'bells':61}]

def context_geometry(publications,plaza):
    # The public map explicitly tags Storke Plaza layer=-1. Its boundary is
    # retained as the lower-court cut; photographs resolve arcade/steps/pond.
    outer=Polygon(max(polygons(publications),key=lambda q:q.area).exterior)
    stairs=unary_union([box(-75.1,-117.85,-66.9,-112.15),box(-55.05,-159.1,-44.95,-153.2)])
    return unary_union([outer,plaza,stairs]).buffer(.04,join_style=2)

def build_publications(ms,p,z,code,lay,info):
    depth=2.70
    # Separate subterranean rooms from the grade-level roof walk. South-facing
    # arcade bays open into the lower plaza instead of a generic four-metre box.
    # The mapped south edge slopes 1.36 m across the frontage. Put every
    # arch on that actual line so neither arcade piers nor its roof float.
    a=np.array([-87.462550,-108.455953]);b=np.array([-40.534248,-109.816941])
    u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]]);length=np.linalg.norm(b-a);c=(a+b)/2
    front=Polygon([a,b,b-n*4.45,a-n*4.45]).intersection(p);core=p.difference(front)
    for k,q in enumerate(polygons(core)):
        native_extrude(q,z-depth,depth-.12,code+'_LowerRooms',lay,'StorkeConcrete',info)
        push(code+'B'+f'{k:02d}',extrusion(q,z-depth,depth-.12),'StorkeConcrete',lay,native=False,info=info)
    add(ms,p,z-.12,.22,'StorkePale')
    profile=box(-length/2,z-depth,length/2,z-.12)
    bay_count=round(length/5.35);bay=length/bay_count
    offsets=np.linspace(-length/2+bay/2,length/2-bay/2,bay_count)
    for offset in offsets:
        hole=affinity.translate(arch_profile(4.75,z-depth+.20,2.00,sill=z-depth-.1),offset,0)
        profile=profile.difference(hole)
        # Recessed paired media-office doors behind each open arcade bay.
        at=c+u*offset-n*2.4
        def door_strip(x0,x1,dep,width):
            center=at+u*((x0+x1)/2)+n*dep
            return Polygon([center+u*x+n*y for x,y in [(-(x1-x0)/2,-width/2),((x1-x0)/2,-width/2),((x1-x0)/2,width/2),(-(x1-x0)/2,width/2)]])
        add(ms,door_strip(-1.45,1.45,0,.09),z-depth+.03,2.32,'DarkGlass')
        for dx in [-1.46,0,1.46]:add(ms,door_strip(dx-.035,dx+.035,.035,.13),z-depth+.03,2.32,'Frame')
    # Profile uses along-frontage X / absolute Z, the roof walk supplies its cap.
    ms['StorkeConcrete'].extend(profile_mesh(profile,c,u,n,0,-.55,.55))
    REPORT['publications']={'below_grade_m':depth,'south_arcade_bays':len(offsets),'roof_walk_at_grade':True,'source_footprint_voids_retained':True}
    return depth

def build_storke_landscape(eg,tower,publications,plaza,ground,place):
    z=tower['ground'];lower=z-2.70;cut=context_geometry(publications['poly'],plaza)
    floor=unary_union([plaza,Polygon(max(polygons(publications['poly']),key=lambda q:q.area).exterior)]).difference(publications['poly']).difference(tower['poly'])
    # Long pool on the western side of the lower plaza, traced approximately
    # from the reviewed aerial and confirmed by the owner's courtyard photo.
    pool=Polygon([(-70.3,-148.3),(-61.2,-148.55),(-60.45,-122.0),(-69.55,-121.75)]).intersection(plaza)
    # A physical lower ground slab supports both the court and the buried
    # rooms. The tower keeps its own upper-grade pad through the courtyard.
    add(eg,floor.union(publications['poly']).difference(pool),lower-.45,.45,'Ground')
    add(eg,tower['poly'],z-.20,.20,'Ground')
    add(eg,floor.difference(pool),lower+.018,.08,'StorkePaving')
    for xx in np.arange(-88,-39,3.5):
        add(eg,box(xx-.013,-160,xx+.013,-80).intersection(floor).difference(pool.buffer(.30)),lower+.108,.018,'StorkeJoint')
    for yy in np.arange(-158,-79,3.5):
        add(eg,box(-88,yy-.013,-39,yy+.013).intersection(floor).difference(pool.buffer(.30)),lower+.108,.018,'StorkeJoint')
    add(eg,pool,lower-.68,.25,'StorkeJoint');add(eg,pool.buffer(-.22),lower-.43,.045,'StorkeWater')
    coping=pool.buffer(.26,join_style=2).difference(pool.buffer(-.02,join_style=2));add(eg,coping,lower,.36,'StorkeConcrete')
    # Low perimeter retaining walls, with open access gaps occupied by stairs.
    west_gap=box(-77,-119,-65,-111);south_gap=box(-57,-161,-42,-153)
    wall=plaza.boundary.buffer(.24,join_style=2).difference(unary_union([west_gap,south_gap,box(-90,-111,-38,-105)]))
    add(eg,wall,lower-.12,2.90,'StorkeConcrete')
    stair_pads=[]
    def stair(a,b,width,count=16):
        a,b=np.array(a),np.array(b);u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]]);run=np.linalg.norm(b-a)/count
        # a is lower court and b meets the upper route. Tread tops share the
        # exact landing datums, with a single closed support per tread.
        for k in range(count):
            c=a+u*(k+.5)*run;q=Polygon([c-u*run*.505-n*width/2,c+u*run*.505-n*width/2,c+u*run*.505+n*width/2,c-u*run*.505+n*width/2]);top=lower+(k+1)/count*2.70
            add(eg,q,lower-.15,top-lower+.15,'StorkePale')
            stair_pads.append({'code':'STORKE_STEP_'+str(len(stair_pads)),'height':top,'bounds':list(q.bounds),'geometry':mapping(q)})
        for offset in [-width*.46,0,width*.46]:
            aa=a+n*offset;bb=b+n*offset;eg['Frame'].append(cylinder((*aa,lower+1),(*bb,z+1),.035,6))
            for t in np.linspace(0,1,5):
                at=aa+(bb-aa)*t;zz=lower+t*2.70;eg['Frame'].append(cylinder((*at,zz),(*at,zz+1),.028,5))
    stair((-67,-115),(-75,-115),5.6);stair((-50,-153.3),(-50,-159.0),10.0)
    # Terrace parapet/gates above the arcade and short benches along the
    # lower pool court. No new shrubs are scattered over mapped paths.
    for a,b in [((-83,-109.1),(-42,-110.3)),((-87,-89),(-87,-106))]:
        a,b=np.array(a),np.array(b)
        eg['Frame'].append(cylinder((*a,z+1),(*b,z+1),.035,6))
        for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/.35))):
            at=a+(b-a)*t;eg['Frame'].append(cylinder((*at,z+.15),(*at,z+1),.020,5))
    for x,y in [(-55,-125),(-53,-137),(-48,-147)]:
        add(eg,box(x-1,y-.35,x+1,y+.35),lower+.44,.13,'Boardwalk')
        for dx in [-.7,.7]:add(eg,box(x+dx-.08,y-.24,x+dx+.08,y+.24),lower,.44,'StorkeConcrete')
    # The courtyard photograph shows broad date-palm crowns with thick trunks,
    # unlike the slender fan-palm silhouettes elsewhere on campus.
    for k,(x,y)in enumerate([(-55,-118),(-51,-133),(-48,-147)]):
        rng=np.random.default_rng(3530+k);h=[9.5,10.2,8.8][k];root=lower+.12
        eg['Trunk'].append(cylinder((x,y,root-.15),(x,y,root+h),.40,12))
        for zz in np.arange(root+.3,root+h-.6,.4):
            eg['Trunk'].append(cylinder((x,y,zz),(x,y,zz+.09),.44,12))
        for leaf in range(26):
            angle=leaf*math.tau/26+rng.uniform(-.10,.10);u=np.array([math.cos(angle),math.sin(angle)]);n=np.array([-u[1],u[0]])
            radius=rng.uniform(4.2,5.1);droop=rng.uniform(1.3,2.5)
            for j in range(6):
                t0=j/6;t1=(j+1)/6;a=np.array([x,y])+u*radius*t0;b=np.array([x,y])+u*radius*t1
                w=.10+1.0*math.sin(t0*math.pi)**.6
                za=root+h+1.6*math.sin(t0*math.pi)-droop*t0;zb=root+h+1.6*math.sin(t1*math.pi)-droop*t1
                vv=np.array([[*(a-n*w/2),za],[*(a+n*w/2),za],[*b,zb],[*(a-n*w/2),za-.045],[*(a+n*w/2),za-.045],[*b,zb-.045]])
                ff=np.array([[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]])
                m=trimesh.Trimesh(vertices=vv,faces=ff,process=True);trimesh.repair.fix_normals(m);assert m.is_watertight;eg['Leaves'].append(m)
        add(eg,Point(x,y).buffer(.88,quad_segs=16),lower+.085,.055,'StorkeSoil')
        add(eg,Point(x,y).buffer(1.02,quad_segs=16).difference(Point(x,y).buffer(.88,quad_segs=16)),lower+.08,.12,'StorkeConcrete')
    # Two narrow cypress silhouettes flank the tower's upper arrival.
    for k,(x,y)in enumerate([(-82,-98),(-82,-87)]):
        zz=float(ground(x,y));eg['Trunk'].append(cylinder((x,y,zz-.2),(x,y,zz+5),.13,7));m=trimesh.creation.icosphere(subdivisions=2);m.apply_scale([.85,.85,4.3]);m.apply_translation([x,y,zz+5.4]);eg['Leaves'].append(m)
    place('Storke Plaza','斯托克广场',plaza,lower+.7,source='https://www.openstreetmap.org/way/218817558')
    REPORT['plaza']={'mapped_source':'https://www.openstreetmap.org/way/218817558','mapped_layer':-1,'lower_court_m':lower,'upper_walk_m':z,'pool_area_m2':round(pool.area,2),'two_connected_stair_flights':True,'estimated_court_palms':3,'palm_form':'Thick-trunked date palms with broad arching crowns, photo interpreted','retained_mapped_extent':mapping(plaza),'ground_cut':mapping(cut),'lower_floor':mapping(floor),'stair_pads':stair_pads}
    (OUT/'storke_architecture.json').write_text(json.dumps(REPORT,indent=2)+'\n')
    return cut
