"""Distinct exterior volumes, coastal vegetation and architectural detailing."""
from cad_core import *

def roof(ms,p,z,tile=False):
    for q in polygons(p):
        if tile:
            cc=np.asarray(q.minimum_rotated_rectangle.exterior.coords)[:4];ed=np.roll(cc,-1,axis=0)-cc;u=ed[np.argmax(np.linalg.norm(ed,axis=1))];u/=np.linalg.norm(u);v=np.array([-u[1],u[0]]);c=q.centroid
            loc=affinity.affine_transform(q,[u[0],u[1],v[0],v[1],-c.x*u[0]-c.y*u[1],-c.x*v[0]-c.y*v[1]])
            tf=np.eye(4);tf[:2,0]=u;tf[:2,1]=v;tf[:2,3]=[c.x,c.y]
            for m in pitched(loc,z,1.6):m.apply_transform(tf);ms['Tile'].append(m)
        else:
            ms['Metal'].append(extrusion(q,z,.22))
            rim=q.buffer(-.12,join_style=2).difference(q.buffer(-.42,join_style=2))
            for r in polygons(rim):ms['LightStone'].append(extrusion(r,z+.23,.35))

def bands(ms,p,z,h,n,mat='LightStone'):
    for zz in [z+k*h/n for k in range(1,n)]:
        for q in polygons(p.buffer(.12,join_style=2).difference(p.buffer(-.08,join_style=2))):ms[mat].append(extrusion(q,zz,.18))

def entrance(ms,p,z):
    edges=[]
    for q in polygons(p):
        for a,b in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
            length=np.linalg.norm(b-a)
            if length>9:edges.append((length,a,b))
    if not edges:return
    _,a,b=max(edges,key=lambda v:v[0]);u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]]);c=(a+b)/2
    q=Polygon([c-u*3+n*.1,c+u*3+n*.1,c+u*3+n*2.6,c-u*3+n*2.6]);ms['Metal'].append(extrusion(q,z+3.0,.16))
    for off in [-2,0,2]:
        c0=c+u*off+n*.12;q=Polygon([c0-u*.65,c0+u*.65,c0+u*.65+n*.09,c0-u*.65+n*.09]);ms['DarkGlass'].append(extrusion(q,z+.1,2.6))

def fins(ms,p,z,h,spacing=2.1,mat='Tile',depth=.65):
    for q in polygons(p):
        for a,b in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
            vec=b-a;length=np.linalg.norm(vec)
            if length<10:continue
            u=vec/length;n=np.array([u[1],-u[0]])
            for along in np.arange(1,length-1,spacing):
                c=a+u*along+n*.15;pp=Polygon([c-u*.065,c+u*.065,c+u*.065+n*depth,c-u*.065+n*depth]);ms[mat].append(extrusion(pp,z+.6,h-.9))

def storke(ms,p,z,h):
    q=max(polygons(p),key=lambda q:q.area);cc=np.asarray(q.minimum_rotated_rectangle.exterior.coords)[:4];c=q.centroid;u=cc[1]-cc[0];u/=np.linalg.norm(u);v=np.array([-u[1],u[0]])
    def rect(x,y,sx,sy,zz,hh,mat='Concrete'):
        center=np.array([c.x,c.y])+u*x+v*y;pp=Polygon([center+u*a+v*b for a,b in [(-sx/2,-sy/2),(sx/2,-sy/2),(sx/2,sy/2),(-sx/2,sy/2)]]);ms[mat].append(extrusion(pp,z+zz,hh))
    for x,y in [(-2.8,-2.7),(-2.8,2.7),(2.8,-2.7),(2.8,2.7)]:rect(x,y,1.05,1.15,0,h)
    rect(-1.6,0,1.65,4.6,0,h-8)
    for zz in np.arange(3.6,h-8,3.8):rect(.7,0,3.2,4.8,zz,.17)
    for zz in [h-10.5,h-6.5,h-1.4]:rect(0,0,6.8,6.6,zz,.48)
    for k in range(8):
        zz=h-9+k*.85;rect(0,0,5.5,.13,zz,.16,'Frame')
    for x in [-1.6,0,1.6]:
        for y in [-1.5,0,1.5]:
            center=np.array([c.x,c.y])+u*x+v*y;bell=trimesh.creation.cone(radius=.42,height=.65,sections=10);bell.apply_transform(trimesh.transformations.rotation_matrix(math.pi,[1,0,0]));bell.apply_translation([*center,z+h-7.0]);ms['Gold'].append(bell)
    # Four clock discs in vertical planes, with clear radial hour markers.
    for normal in [u,-u,v,-v]:
        tangent=np.array([-normal[1],normal[0]]);center=np.array([c.x,c.y])+normal*3.53;cz=z+h-12
        ms['LightStone'].append(cylinder((*center,cz),(*(center+normal*.13),cz),1.02,24))
        for ang in np.arange(0,2*math.pi,math.pi/6):
            a=center+normal*.15+tangent*(.75*math.sin(ang));b=center+normal*.15+tangent*(.88*math.sin(ang));ms['Frame'].append(cylinder((*a,cz+.75*math.cos(ang)),(*b,cz+.88*math.cos(ang)),.035,4))
        for ang,length in [(0,.62),(math.pi/3,.45)]:
            b=center+normal*.18+tangent*(length*math.sin(ang));ms['Frame'].append(cylinder((*(center+normal*.18),cz),(*b,cz+length*math.cos(ang)),.045,5))

def split_volumes(id,p,h,levels):
    if id==277:return [(q,4.0 if q.area<150 else (21.0 if q.centroid.x>210 else 17.5),1 if q.area<150 else 4) for q in polygons(p)]
    if id in {317,329,326,294,337,336}:
        a,b,c,d=p.bounds;axis=(c-a)>(d-b);cut=box(a,b,c,b+(d-b)*.36) if axis else box(a,b,a+(c-a)*.36,d)
        return [(p.intersection(cut),h,levels),(p.difference(cut),max(7.2,h*.55),max(2,round(levels*.55)))]
    return [(p,h,levels)]

def pavilion_bridges(ms,z):
    for level in [1,2,3]:
        zz=z+level*4.7
        for start,end in [((192,-122),(194,-110)),((201,-101),(215,-101))]:
            q=LineString([start,end]).buffer(1.35,cap_style=2);ms['Concrete'].append(extrusion(q,zz,.24))
            for side in [-1,1]:
                a=np.array(start);b=np.array(end);u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])*1.23*side
                ms['Frame'].append(cylinder((*(a+n),zz+1.2),(*(b+n),zz+1.2),.055,5))
                for t in np.arange(0,np.linalg.norm(b-a),1.4):
                    c=a+u*t+n;ms['Frame'].append(cylinder((*c,zz+.25),(*c,zz+1.2),.035,4))
    for k in range(26):ms['Concrete'].append(boxmesh(206.5,-120+k*.3,z+k*.18,2.5,.31,.18))

def palms(eg,x,y,z,rng):
    h=rng.uniform(10,16);lean=np.array([rng.uniform(-.7,.7),rng.uniform(-.7,.7)]);top=np.array([x,y])+lean
    eg['Trunk'].append(cylinder((x,y,z-1.5),(*top,z+h),.18,7))
    crown=trimesh.creation.icosphere(subdivisions=1);crown.apply_scale([1.05,1.05,.65]);crown.apply_translation([*top,z+h-.15]);eg['Leaves'].append(crown)
    for k in range(9):
        ang=k*math.tau/9+rng.uniform(-.15,.15);u=np.array([math.cos(ang),math.sin(ang)]);v=np.array([-u[1],u[0]]);rr=rng.uniform(2.8,4.0)
        # Four closed tapered leaflets describe an arching feathered frond.
        for j in range(4):
            t0=j/4;t1=(j+1)/4;a=top+u*rr*t0;b=top+u*rr*t1;w=.95*(1-t0)+.12
            za=z+h+math.sin(t0*math.pi)*.7-t0*1.3;zb=z+h+math.sin(t1*math.pi)*.7-t1*1.3
            vv=np.array([[*(a-v*w/2),za],[*(a+v*w/2),za],[*b,zb],[*(a-v*w/2),za-.045],[*(a+v*w/2),za-.045],[*b,zb-.045]])
            ff=np.array([[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]])
            m=trimesh.Trimesh(vertices=vv,faces=ff,process=True);trimesh.repair.fix_normals(m);eg['Leaves'].append(m)
