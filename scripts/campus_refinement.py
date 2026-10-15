"""Public-source exterior interpretations, tied to official 2026 footprint edges.
See docs/RESIDENTIAL_AND_NEIGHBORHOOD_SOURCES.md for photographed features,
source dates and the distinction between mapped plan geometry and estimated detail.
"""
from cad_core import *
from shapely import segmentize

TARGETS={293,312,313,314,318,327,323,324,284,276,279,283,299,343,345}
REFINEMENT_REFS={312:'https://www.housing.ucsb.edu/housing-options/options-filter/anacapa',293:'https://www.housing.ucsb.edu/housing-options/options-filter/santa-rosa',313:'https://www.housing.ucsb.edu/housing-options/options-filter/santa-cruz',318:'https://www.housing.ucsb.edu/housing-options/options-filter/san-miguel/san-miguel-hall-emergency-map',327:'https://www.housing.ucsb.edu/housing-options/options-filter/san-nicolas',314:'https://dining.ucsb.edu/dining-commons/de-la-guerra-dining-commons',324:'https://www.ucen.ucsb.edu/meet/meetings-events/outdoor-spaces',323:'https://mcc.sa.ucsb.edu/',284:'https://www.alumni.ucsb.edu/about/mosher-house',345:'https://ucsbgauchos.com/facilities/harder-stadium/1',343:'https://ucsbgauchos.com/facilities/harder-stadium/1',276:'https://ucsbgauchos.com/facilities',279:'https://recreation.ucsb.edu/facilities',283:'https://recreation.ucsb.edu/facilities',299:'https://recreation.ucsb.edu/facilities'}
NOTES={
312:('Four bent residential wings retain the official open courtyards. Deep low eaves, brick piers, paired windows, central glazed lobby and shaded entrance are interpreted from Housing exterior photos.','按官方轮廓保留四组转折翼楼及开敞庭院；依据住宿部门照片细化低檐、砖柱、成组窗、中央玻璃门厅及遮阴入口。'),
293:('The mapped zigzag low-rise wings remain separate from their landscaped courtyards. Shallow roofs, brick ends, recessed window bays and covered entries replace the generic pitched cap.','保留映射的折线低层翼楼与庭院，细化缓坡屋面、砖砌端墙、成组窗及有顶入口。'),
313:('Bent two-storey wings, deep overhangs, brick end walls, grouped windows and courtyard approaches follow the university footprint and exterior photographs.','按官方轮廓及外观照片表达转折的两层翼楼、深檐、砖砌端墙、成组窗及庭院入口。'),
318:('Two offset eight-storey residential towers are separated from the one-storey community core. Brick end walls, light window reveals, low connecting roofs, entrance and stage are modeled from Housing photos and the hall layout.','依据住宿部门照片及布局图区分两座错位的八层宿舍塔楼与单层公共空间，细化砖砌端墙、浅色窗框、低层连廊、入口和舞台。'),
327:('Two eight-storey bars and their low connecting community wing replace a full-footprint tower extrusion. Brick end walls and paired window bays retain the mapped outline.','区分两座八层条形塔楼与低层公共连廊，细化砖砌端墙及成组窗，保留映射轮廓。'),
314:('Separate dining hall, service volume and glazed entry pavilion; open courtyard, supported canopy, window mullions and roof edges use the current Campus Dining exterior photographs.','参照校园餐饮部门现有外观照片区分餐厅、后勤体块与玻璃入口亭，细化开敞庭院、有支撑的雨棚、窗梃和屋檐。'),
324:('Lagoon-facing lower rooms, set-back upper floor, glazed frontage, outdoor terraces and supported shade structures articulate the University Center. Patio and lawn connections follow mapped routes.','区分面向泻湖的下层空间、退台上层、玻璃立面、室外露台和有支撑的遮阴构架；露台及草坪衔接沿用映射路径。'),
323:('Theater and lower lounge/entry volumes are distinguished, with a clear glazed entrance and shallow roof overhangs. Auditorium interiors are not modeled.','区分剧场与较低的休息厅、入口体块，细化玻璃入口及浅檐；未建模室内观众厅。'),
284:('Three terraced levels, glazed meeting rooms, Whalen Plaza approach and an open circular Sky Terrace pergola replace the generic roof garden. Based on Alumni House photos; member dimensions approximate.','参照校友之家照片重建三层退台、玻璃会议空间、惠伦广场入口及开放式圆形屋顶露台花架，构件尺寸为近似。')}

def add(ms,g,z,h,mat):
    for p in polygons(g):ms[mat].append(extrusion(p,z,h))
def linebeam(ms,a,b,z,h,width=.14,mat='Frame'):
    add(ms,LineString([a,b]).buffer(width/2,cap_style=2),z,h,mat)
def pane(ms,a,b,z,h,normal,material='DarkGlass',frame='LightStone',mullions=True):
    a,b,n=np.array(a),np.array(b),np.array(normal);ln=np.linalg.norm(b-a)
    if ln<.25:return
    u=(b-a)/ln;c0=a+n*.07;c1=b+n*.07
    add(ms,Polygon([c0,c1,c1+n*.075,c0+n*.075]),z,h,material)
    for hh in [z-.06,z+h]:linebeam(ms,c0+n*.09,c1+n*.09,hh,.09,.12,frame)
    if mullions:
        for d in np.linspace(0,ln,max(2,int(ln/1.8)+1)):
            c=c0+u*d+n*.09;add(ms,Point(*c).buffer(.045,quad_segs=1),z,h,frame)

def exterior(ms,q,z,h,n,kind,parts):
    # Only exposed faces receive openings; avoid windows on party walls.
    for ring in [q.exterior,*q.interiors]:
        cc=np.array(ring.coords)
        for a,b in zip(cc[:-1],cc[1:]):
            ln=np.linalg.norm(b-a)
            if ln<2.4:continue
            u=(b-a)/ln;normal=np.array([u[1],-u[0]]);probe=Point(*((a+b)/2+normal*.25))
            blocked=max([hh for name,qq,hh,nn,mm in parts if name!=kind and qq.buffer(.1).covers(probe)],default=0)
            continuous=kind in ['entry','glazed-entry','lounge','lagoon-rooms','theater-entry','vista','garden']
            bay=3.4 if kind.startswith('tower')else 4.4 if continuous else 3.6
            count=max(1,int(ln/bay));step=ln/count;dh=h/n
            # Tower short ends are solid brick; long elevations have vertical
            # paired openings and light concrete piers, as photographed.
            if kind.startswith('tower') and ln<12:
                linebeam(ms,a+normal*.08,b+normal*.08,z+.2,h-.4,.17,'Brick');continue
            for k in range(n):
                if k*dh+.55<blocked-.1:continue
                for j in range(count):
                    c=a+u*((j+.5)*step);ww=step*(.86 if continuous else .60)
                    wh=min(dh-1.0,2.85);zz=z+k*dh+.67
                    pane(ms,c-u*ww/2,c+u*ww/2,zz,wh,normal,frame='WhitePanel'if kind.startswith('tower')else 'ConcreteBlock',mullions=continuous)
                    if kind.startswith('tower'):
                        for side in [-1,1]:
                            c1=c+u*(ww/2+.13)*side+normal*.13;linebeam(ms,c1-u*.11,c1+u*.11,z+k*dh+.12,dh-.16,.22,'LightStone')
                    elif not continuous:
                        linebeam(ms,c-u*(ww/2+.09)+normal*.18,c+u*(ww/2+.09)+normal*.18,zz-.09,.11,.28,'LightStone')
            if not kind.startswith('tower'):
                for k in range(1,n):
                    if k*dh>=blocked-.05:linebeam(ms,a+normal*.11,b+normal*.11,z+k*dh-.10,.17,.18,'Concrete')
            # Short masonry end faces give the low-rise residential wings their
            # photographed contrast, without adding free-standing fins.
            if kind=='residence' and ln<15:linebeam(ms,a+normal*.04,b+normal*.04,z+.08,h-.16,.12,'Brick')

def parts_for(id,p):
    parts=[];used=Polygon()
    def part(name,mask,h,n,mat):
        nonlocal used
        q=p.intersection(mask).difference(used).buffer(0)
        if q.area>.1:parts.append((name,q,h,n,mat));used=unary_union([used,q])
    if id in [293,312,313]:return [('residence',p,6.65,2,'ConcreteBlock')]
    if id==318:
        part('tower-west',box(14,-358,34,-312),25.0,8,'Brick')
        part('tower-east',box(59,-409,76,-370),25.0,8,'Brick')
        part('lounge',box(40,-355,58,-326),4.0,1,'ConcreteBlock')
        part('community',p,3.7,1,'ConcreteBlock')
    elif id==327:
        part('tower-west',box(91,-440,109,-399),25,8,'Brick')
        part('tower-east',box(117,-440,138,-400),25,8,'Brick')
        part('community',p,3.8,1,'ConcreteBlock')
    elif id==314:
        part('glazed-entry',box(214,-414,242,-387),8.8,2,'ConcreteBlock')
        part('dining',box(193,-451,265,-413),6.4,1,'ConcreteBlock')
        part('service',p,4.9,1,'ConcreteBlock')
    elif id==324:
        part('upper',box(-95,-222,54,-182),10.4,3,'Limestone')
        part('lagoon-rooms',p,6.5,2,'ConcreteBlock')
    elif id==323:
        part('theater',box(72,-218,102,-188),9.1,2,'Limestone')
        part('theater-entry',p,4.8,1,'ConcreteBlock')
    elif id==284:
        part('vista',box(185,419,217,449),11.6,3,'WhitePanel')
        part('garden',p,7.9,2,'ConcreteBlock')
    elif id in [276,279,283,299]:
        h={276:16.2,279:11.8,283:11.0,299:10.6}[id]
        core=p.buffer(-8,join_style=2).buffer(5,join_style=2).intersection(p)
        part('hall',core,h,2,'ConcreteBlock');part('entry',p,5.1,1,'ConcreteBlock')
    return parts

def refined_building(ms,id,p,z,code,lay,info):
    if id in [343,345]:
        # Field-facing bleachers follow the mapped narrow grandstand instead
        # of repeatedly extruding the whole L-shaped office/stand footprint.
        a,b,c,d=p.bounds
        stand=p.intersection(box(a+2,b+4,a+19,d-3)) if id==343 else p.buffer(-.25)
        used=Polygon();rows=17 if id==343 else 14
        sa,sb,sc,sd=stand.bounds;run=(sc-sa)/rows
        for k in range(rows):
            x0=sa+k*run
            q=stand.intersection(box(x0,sb,x0+run+.01,sd));top=.55+(rows-1-k if id==343 else k)*.41
            add(ms,q,z-.12,top+.12,'Seat')
            edge=q.intersection(box(x0,sb,x0+.10,sd));add(ms,edge,z+top,.08,'Purple')
        add(ms,p.difference(stand),z,3.2,'ConcreteBlock')
        for yy in np.arange(sb+5,sd-3,16):
            x=sa+.5 if id==343 else sc-.5
            ms['Frame'].append(cylinder((x,yy,z),(x,yy,z+8.0),.06,6))
        return 8.2,2,[{'name':'stepped-grandstand','area_m2':round(stand.area,2),'height_m':8.2,'storeys':2}]
    parts=parts_for(id,p);metadata=[]
    for index,(name,g,h,n,mat)in enumerate(parts):
        for q in polygons(g):
            native_extrude(q,z,h,code+'_Volume',lay,mat,info);push(code+'B'+f'{index:02d}'+f'{len(metadata):02d}',extrusion(q,z,h),mat,lay,native=False,info=info)
            exterior(ms,q,z,h,n,name,parts)
            metadata.append({'name':name,'area_m2':round(q.area,2),'height_m':h,'storeys':n})
            roofmat='RoofClay'if id in [293,312,313]else 'RoofLibraryWarm'if id in [314,324,323]else 'RoofLibraryGray'
            if id in [293,312,313]:
                # Very low hipped roof, subdivided by wing orientation. No
                # single high tent roof draped over the bent whole footprint.
                core=q.buffer(-2.0,join_style=2)
                add(ms,q.buffer(.75,join_style=2),z+h,.18,'RoofLibraryGray')
                add(ms,core,z+h+.18,.16,'RoofLibraryWarm')
                for ring in [q.exterior,*q.interiors]:
                    for aa,bb in zip(list(ring.coords)[:-1],list(ring.coords)[1:]):
                        aa,bb=np.array(aa),np.array(bb);v=bb-aa;ln=np.linalg.norm(v)
                        if ln<5:continue
                        u=v/ln;n0=np.array([u[1],-u[0]])
                        for dd in np.arange(1.8,ln-1,4.8):
                            cc=aa+u*dd+n0*.2;linebeam(ms,cc,cc+n0*.5,z+.1,h-.1,.32,'Brick')
            else:
                add(ms,q.buffer(-.08,join_style=2),z+h,.16,roofmat)
                # Parapet is a separate ring ABOVE the finish, never a duplicate
                # coplanar roof cap. It ends at adjoining taller volumes.
                edge=q.boundary.buffer(.11).difference(p.difference(q).buffer(.15));add(ms,edge,z+h+.16,.22,'Concrete')
    if id==314:
        # Photographed two-storey glass entrance tower north of the dining hall.
        pane(ms,(217,-389),(238,-389),z+.3,8.2,(0,1),'Glass','Frame')
        for y in [-414,-404,-394]:
            pane(ms,(241,y),(241,y+8),z+.4,7.6,(1,0),'Glass','Frame')
        canopy=box(217,-385,247,-381);add(ms,canopy,z+3.7,.20,'RoofLibraryGray')
        for x in [218,230,245]:ms['Frame'].append(cylinder((x,-382,z-.5),(x,-382,z+3.7),.12,8))
        for x in np.arange(218,246,2.3):linebeam(ms,(x,-385),(x,-381),z+3.9,.10,.10,'LightStone')
    elif id==324:
        # Supported southern terrace, railing and broad glass lagoon frontage.
        terrace=p.intersection(box(-94,-246,12,-225)).buffer(-.15)
        add(ms,terrace,z+6.5,.17,'Paving')
        for q in polygons(terrace):
            for a,b in zip(list(q.exterior.coords)[:-1],list(q.exterior.coords)[1:]):
                a,b=np.array(a),np.array(b);ln=np.linalg.norm(b-a)
                if ln<2 or p.buffer(-.2).contains(LineString([a,b]).centroid):continue
                for t in np.linspace(0,1,max(2,int(ln/2)+1)):
                    c=a+(b-a)*t;ms['Frame'].append(cylinder((*c,z+6.66),(*c,z+7.7),.04,5))
                ms['Frame'].append(cylinder((*a,z+7.7),(*b,z+7.7),.04,5))
        from shapely.ops import nearest_points
        for x in np.arange(-85,14,8):
            if not terrace.buffer(.15).contains(Point(x,-229)):continue
            a0=nearest_points(Point(x,-229),terrace)[1]
            b0=nearest_points(Point(x,-239),terrace)[1]
            if a0.distance(b0)<1.5:continue
            aa=np.array(a0.coords[0]);bb=np.array(b0.coords[0])
            linebeam(ms,aa,bb,z+9.4,.16,.20,'LightStone')
            for endpoint in [aa,bb]:
                ms['ConcreteBlock'].append(cylinder((*endpoint,z+6.67),(*endpoint,z+9.4),.095,8))
    elif id==284:
        # Open ring pergola: radial rafters, open sky and supported perimeter.
        c=np.array([201.,428.]);rr=8.0;floor=z+11.82
        disk=Point(*c).buffer(rr,quad_segs=32);add(ms,disk,floor-.20,.20,'Paving')
        ring=Point(*c).buffer(rr+.15,quad_segs=32).difference(Point(*c).buffer(rr-.20,quad_segs=32));add(ms,ring,floor+2.65,.22,'ConcreteBlock')
        for a0 in np.linspace(0,math.tau,28,endpoint=False):
            u=np.array([math.cos(a0),math.sin(a0)]);linebeam(ms,c+u*4.9,c+u*8.0,floor+2.66,.15,.11,'Boardwalk')
        inner=Point(*c).buffer(4.9,quad_segs=32).difference(Point(*c).buffer(4.68,quad_segs=32));add(ms,inner,floor+2.66,.20,'ConcreteBlock')
        for a0 in np.linspace(0,math.tau,8,endpoint=False):
            q=c+np.array([math.cos(a0),math.sin(a0)])*7.8;ms['Frame'].append(cylinder((*q,z+7.7),(*q,floor+2.65),.09,8))
        for a0 in np.linspace(0,math.tau,32,endpoint=False):
            q=c+np.array([math.cos(a0),math.sin(a0)])*7.8;ms['Frame'].append(cylinder((*q,floor),(*q,floor+1.0),.025,5))
        for q in polygons(Point(*c).buffer(7.8,quad_segs=32).boundary.buffer(.035)):ms['Frame'].append(extrusion(q,floor+1,.05))
    return max([h+.4 for _,_,h,_,_ in parts]+([14.7]if id==284 else [])),max(n for _,_,_,n,_ in parts),metadata

def refined_outdoors(eg,buildings,osm,ground,env,place,footprints,walkarea,bikearea):
    indexed={f['id']:f for f in buildings}
    def paved(q,mat='Paving'):
        env(q.difference(footprints).difference(bikearea),.38,.05,mat)
    def furniture(x,y,kind='seat'):
        z=float(ground(x,y));eg['Furniture'].append(boxmesh(x,y,z+.43,1.8,.55,.13))
        for dx in [-.62,.62]:eg['Furniture'].append(boxmesh(x+dx,y,z-.15,.12,.35,.64))
        if kind=='table':eg['Furniture'].append(boxmesh(x,y+.9,z+.75,1.6,.8,.09))
    # Patio outlines are constrained to existing hardscape; they do not turn
    # an entire source lawn into a guessed plaza.
    for id in [312,293,313,318,327,314,324,323,284,276,279,283,299]:
        f=indexed[id];p=f['poly'];paved(p.buffer(1.45,join_style=2).difference(p))
        # Direct entrance aprons meet the nearest mapped public path.
        route=unary_union([walkarea,bikearea]);from shapely.ops import nearest_points
        for q in polygons(p):
            pt,edge=nearest_points(q,route);line=LineString([pt,edge])
            if .2<line.length<12:paved(line.buffer(1.7,cap_style=2))
    # Existing patios beside the low-rise halls and tower common rooms.
    for id,rect in [(312,(413,-270,438,-257)),(313,(349,-388,370,-375)),(318,(35,-349,47,-338)),(327,(76,-453,91,-442)),(314,(212,-385,248,-375)),(284,(188,398,226,411)),(324,(-80,-260,-7,-241)),(323,(60,-247,100,-240))]:
        q=box(*rect).difference(footprints).difference(bikearea);paved(q)
        for pt in [q.representative_point()]if not q.is_empty else []:furniture(pt.x,pt.y,'table')
    # San Miguel's photographed low exterior stage. No animated mural texture.
    q=box(69,-371,91,-365).difference(footprints);z=float(ground(80,-368));add(eg,q,z-.5,.95,'ConcreteBlock')
    add(eg,box(72,-366,90,-365.6),z+.45,1.1,'Brick');place('San Miguel stage','圣米格尔宿舍室外舞台',q.buffer(1))
    # UCen permanent lagoon-side stage and continuous lower patio.
    q=Point(-32,-270).buffer(9,quad_segs=24).intersection(box(-45,-279,-19,-270));z=float(ground(-32,-271));add(eg,q,z-.7,1.0,'ConcreteBlock');place('UCen Lagoon Lawn','大学中心泻湖草坪',box(-90,-310,30,-255))
    # Eternal Flame: mapped node + photographed low curved memorial bridge,
    # sloping plaque, stone bed, burner and small static flame interpretation.
    flame=next(f['poly']for f in osm if f['properties'].get('name')=='Eternal Flame');x,y=flame.x,flame.y;z=float(ground(x,y));bed=Point(x,y).buffer(2.8,quad_segs=20);paved(bed,'StepStone')
    rng=np.random.default_rng(1968)
    for _ in range(22):
        dx,dy=rng.uniform(-1.6,1.6,2)
        if dx*dx+dy*dy>2.6:continue
        m=trimesh.creation.icosphere(subdivisions=0);m.apply_scale([.28,.22,.18]);m.apply_translation([x+dx,y+dy,z+.20]);eg['Bluff'].append(m)
    path=[]
    for t in np.linspace(-1,1,18):path.append([x+t*2.25,y+.40,z+.35+1.05*(1-t*t)])
    for a,b in zip(path[:-1],path[1:]):eg['ConcreteBlock'].append(cylinder(a,b,.18,6))
    for sign in [-1,1]:eg['ConcreteBlock'].append(boxmesh(x+sign*2.20,y+.4,z-.3,.40,.6,.93))
    plaque=boxmesh(x-1.55,y+.2,z+.68,.82,.65,.08);plaque.apply_transform(trimesh.transformations.rotation_matrix(.32,[1,0,0],point=[x-1.55,y+.2,z+.7]));eg['Slate'].append(plaque)
    eg['Corten'].append(cylinder((x,y,z+.25),(x,y,z+.65),.20,16));eg['Gold'].append(trimesh.creation.icosphere(subdivisions=1).apply_scale([.13,.13,.32]).apply_translation([x,y,z+.95]))
    place('Eternal Flame','永恒之火',bed)
    # Henley Gate's surveyed gantry line supplies orientation and span. Tapered
    # stone piers support a shallow arch; all base pads meet local terrain.
    gate=next(f['poly']for f in osm if f['properties'].get('name')=='Henley Gate');rc=np.array(gate.minimum_rotated_rectangle.exterior.coords)[:4];vv=np.roll(rc,-1,axis=0)-rc;u=vv[np.argmax(np.linalg.norm(vv,axis=1))];span=np.linalg.norm(u);u=u/span;c0=np.array(gate.centroid.coords[0]);a=c0-u*span/2;b=c0+u*span/2;n=np.array([-u[1],u[0]])
    for t in [0,1]:
        c=a+(b-a)*t;zz=float(ground(*c));q=Polygon([c-u*1.0-n*1.1,c+u*1.0-n*1.1,c+u*1.0+n*1.1,c-u*1.0+n*1.1]);add(eg,q,zz-1.5,8.6,'ConcreteBlock')
        for h in np.arange(.6,7,.65):add(eg,q.buffer(.035).difference(q),zz+h,.035,'StoneJoint')
    zbase=max(float(ground(*a)),float(ground(*b)))+6.65
    top=[]
    for t in np.linspace(0,1,42):
        c=a+(b-a)*t;top.append([*c,zbase+1.7*math.sin(math.pi*t)])
    for aa,bb in zip(top[:-1],top[1:]):eg['Corten'].append(cylinder(aa,bb,.34,6))
    # Small stepped roadside walls visually anchor the arch in its planted verge.
    for c,sign in [(a,-1),(b,1)]:
        zz=float(ground(*c));linebeam(eg,c,c+u*sign*7,zz-.4,1.5,.65,'ConcreteBlock')
    place('Henley Gate','亨利校门',gate.buffer(4))
