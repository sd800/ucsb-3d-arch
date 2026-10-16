"""Distinct highlight forms, interpreted from cited owner/project references."""
from cad_core import *
from campus_detail import roof,bands,facade
from highlight_finish import bell_mesh
REFS={332:'https://www.kitp.ucsb.edu/news/new-kohn-hall',280:'https://bioengineering.ucsb.edu/facilities',303:'https://aait.ucsb.edu/event-av-services/campbell-hall/gallery'}
NOTES={332:('Enclosed mapped courtyard, low tile-roofed wings, warm orange flat-topped entrance tower and supported, partly open courtyard awning. Local member dimensions are approximate.','保留映射内庭与低层瓦屋顶翼楼，区分暖橙色平顶入口塔，细化有支撑且局部开敞的庭院遮阳架；构件尺寸为近似。'),280:('Three-storey glass, metal and concrete research wings, with framed glazing, a taller glazed atrium and restrained south-side shading. Three above-ground storeys follow the department facilities reference.','依据院系设施资料采用地上三层，细化玻璃、金属及混凝土研究翼楼、窗框、挑高中庭与南侧遮阳。'),303:('Circular lecture-hall drum and low entrance/service wings are separated. The folded-plate roof has connected alternating radial ridges; glazed lobby bays and roof edges replace a generic full-footprint cap.','区分圆形讲堂与较低入口及配套翼楼；折板屋顶具有连续交替的径向屋脊，细化玻璃门厅、屋檐，替换通用全轮廓顶盖。')}

def build_highlight(id,p,z,ms,code,lay,info):
    if id not in REFS:return None
    metadata=[]
    def body(g,h,n,mat,windows=True):
        for q in polygons(g):
            native_extrude(q,z,h,code+'_HighlightVolume',lay,mat,info);push(code+'HB'+f'{len(metadata):02d}',extrusion(q,z,h),mat,lay,native=False,info=info);
            if windows:facade(ms,q,z,h,n,continuous=id==280,spacing=3.7)
            metadata.append({'name':mat,'area_m2':round(q.area,2),'height_m':h,'storeys':n})
    a,b,c,d=p.bounds
    if id==332:
        # The eastern gate-facing projection is a separate flat-topped tower;
        # courtyard voids remain part of the authoritative plan geometry.
        tower=p.intersection(Point(687.5,85.8).buffer(5.3,quad_segs=24));wings=p.difference(tower)
        body(wings,7.1,2,'KohnWall');roof(ms,wings,z+7.1,True)
        body(tower,11.4,2,'KohnStucco')
        for q in polygons(tower):ms['RoofLibraryWarm'].append(extrusion(q,z+11.4,.16))
        # The authoritative outline has a narrow opening at the courtyard,
        # so it is a concavity rather than an interior polygon ring. The KITP
        # public evacuation plan identifies the same central courtyard.
        courts=[Polygon(ring)for q in polygons(p)for ring in q.interiors]
        courts += [q for q in polygons(p.convex_hull.difference(p))if q.buffer(.5).covers(Point(644,84))]
        for space in courts:
            # Erode the narrow mapped opening, then retain only the courtyard
            # itself; small exterior slivers never become awning segments.
            pieces=[q for q in polygons(space.buffer(-.55))if q.covers(Point(644,84))]
            if not pieces:continue
            court=max(pieces,key=lambda q:q.area)
            if court.area<40:continue
            for part in polygons(court.buffer(.4).intersection(space)):ms['Paving'].append(extrusion(part,z+.02,.12))
            aa,bb,cc,dd=court.bounds
            for y in np.linspace(bb+.9,dd-.9,3):
                strip=LineString([(aa+.4,y),(cc-.4,y)]).buffer(.10,cap_style=2).intersection(court)
                for part in polygons(strip):ms['Frame'].append(extrusion(part,z+8.85,.16))
                span=LineString([(aa+.4,y),(cc-.4,y)]).intersection(court)
                for segment in ([span]if span.geom_type=='LineString'else getattr(span,'geoms',[])):
                    if segment.length<2:continue
                    for endpoint in [segment.interpolate(.35),segment.interpolate(max(.35,segment.length-.35))]:
                        x0,y0=endpoint.coords[0];ms['KohnStucco'].append(boxmesh(x0,y0,z+.14,.45,.45,1.1));ms['Frame'].append(boxmesh(x0,y0,z+1.24,.16,.16,7.61))
            for x in np.arange(aa+.8,cc-.5,2.8):
                panel=box(x,bb+.6,x+1.3,dd-.6).intersection(court)
                for part in polygons(panel):ms['RoofLibraryLight'].append(extrusion(part,z+9.01,.07))
        return 11.56,2,metadata
    if id==280:
        body(p,13.4,3,'ConcreteBlock');roof(ms,p,z+13.4)
        # Shading members remain attached to their own window/floor zone.
        for q in polygons(p):
            for aa,bb in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
                v=bb-aa;ln=np.linalg.norm(v)
                if ln<10:continue
                u=v/ln;n=np.array([u[1],-u[0]])
                if n[1]>-.5:continue
                for k in range(3):
                    cc=(aa+bb)/2+n*.24;strip=Polygon([aa+n*.12,bb+n*.12,bb+n*.70,aa+n*.70]);ms['Metal'].append(extrusion(strip,z+k*13.4/3+3.5,.12))
        return 13.98,3,metadata
    # Least-squares circle through 37 mapped exterior arc vertices. Keeping
    # the true drum radius avoids creating a spurious low ring around it.
    center=Point(222.75047957,300.79980025);radius=22.7262386161;disc=center.buffer(radius+.20,quad_segs=96).intersection(p);annex=p.difference(disc)
    assert disc.area>p.area*.90
    body(disc,8.55,1,'ConcreteBlock',False);body(annex,4.7,1,'ConcreteBlock');roof(ms,annex,z+4.7)
    # Owner's plaza photograph shows a zigzag folded-plate eave, not a
    # rotationally smooth cone. Match each ridge to the perimeter fold.
    count=32;vertices=[[center.x,center.y,z+10.15],[center.x,center.y,z+9.97]]
    for lower in [False,True]:
        for k in range(count):
            angle=k*math.tau/count;zz=z+8.55+(.95 if k%2==0 else 0)-(.18 if lower else 0)
            vertices.append([center.x+(radius+.35)*math.cos(angle),center.y+(radius+.35)*math.sin(angle),zz])
    faces=[]
    for k in range(count):
        a=2+k;b=2+(k+1)%count;c=a+count;d=b+count;faces.extend([[0,a,b],[1,d,c],[a,c,d],[a,d,b]])
        if k%2==0:ms['Metal'].append(cylinder((center.x,center.y,z+10.19),tuple(np.asarray(vertices[a])+[0,0,.04]),.045,5))
    folded=trimesh.Trimesh(vertices,faces,process=True);trimesh.repair.fix_normals(folded);assert folded.is_watertight;ms['RoofLibraryGray'].append(folded)
    from campus_refinement import pane
    def underside(x,y):
        angle=math.atan2(y-center.y,x-center.x)%math.tau;k=int(angle/math.tau*count);a=np.asarray(vertices[2+k]);b=np.asarray(vertices[2+(k+1)%count]);c=np.array([center.x,center.y]);weights=np.linalg.solve(np.column_stack([a[:2]-c,b[:2]-c]),np.array([x,y])-c);return z+10.15+weights[0]*(a[2]-z-10.15)+weights[1]*(b[2]-z-10.15)-.18
    for angle in np.linspace(-math.pi*.84,-math.pi*.16,15):
        normal=np.array([math.cos(angle),math.sin(angle)]);u=np.array([-normal[1],normal[0]]);c0=np.array([center.x,center.y])+normal*(radius+.04)
        pane(ms,c0-u*1.24,c0+u*1.24,z+.35,5.9,normal,'Glass','Frame')
        cc=c0+u*1.38+normal*.12;ms['ConcreteBlock'].append(boxmesh(*cc,z,.27,.27,underside(*cc)-z))
    return 10.22,1,metadata
