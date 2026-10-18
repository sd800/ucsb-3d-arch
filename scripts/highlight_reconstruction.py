"""Individual exterior reconstructions for the remaining Main Campus highlights.

Official 2026 plan edges are retained. Wing heights, bay spacing and small members
are exterior-photo estimates, not measured construction documents. Source-specific
forms live here; shared window joinery is deliberately not a completion criterion.
"""
from cad_core import *
from campus_refinement import add,linebeam,pane
from roof_finishes import flat_finish,nearby_roof

REFS={
280:'https://bioengineering.ucsb.edu/facilities',
218:'https://kierantimberlake.com/work/henley-hall-institute-for-energy-efficiency/',
227:'https://www.mat.ucsb.edu/~g.legrady/academic/courses/09f200a/c/cnsi.html',
321:'https://sp.dfss.ucsb.edu/entrances/enter-bldg/hfh.html',
288:'https://bren.ucsb.edu/about/bren-hall',
287:'https://msi.ucsb.edu/facilities-services/marine-science-research-building',
297:'https://music.ucsb.edu/operations/facilities',
282:'https://marcuse.faculty.history.ucsb.edu/projects/HSSBLocation.htm',
213:'https://srb.sa.ucsb.edu/about',
300:'https://arts.ucsb.edu/atrium/',
350:'https://www.housing.ucsb.edu/housing-options/options-filter/san-rafael',
308:'https://news.ucsb.edu/in-focus/uc-regents-approve-acquisition-campus-residential-property',
320:'https://news.ucsb.edu/2026/022864/ucsb-seeks-community-input-university-plans-sea-level-rise'}
FEATURES={
280:['three-storey concrete research wings','punched windows with deep square reveals','three-storey glazed entrance atrium','set-back clerestory strip','attached south window-zone shades'],
218:['western laboratory bar','eastern three-storey oval open-air atrium','connected galleries and stair flights','north curtain glazing','south terracotta solar screen and projecting eaves'],
227:['three-storey main laboratory bar','separate low northern ancillary volumes','glazed northern lobby','inclined end feature wall','closely spaced attached facade members; no unrealized display'],
321:['five-storey classroom/research bar','lower courtyard/service wing','recessed southern glazed lobby','deep horizontal concrete shades','paired grouped windows and exposed concrete frame'],
288:['open triangular courtyard','separate office and laboratory wings','set-back upper office level','courtyard balconies and supported shade canopy','limited roof-mounted photovoltaic rows'],
287:['three wings around open courtyard','four above-ground floors; basement excluded','second-level courtyard patio','sawtooth exterior bays','continuous concrete floor bands and shaded glazing'],
297:['separate performance halls and teaching wings','two open courtyards','low clay roofs by individual wing','shaded courtyard circulation','Music Bowl stepped seating and stage'],
282:['six-storey northern office tower','four-storey west wing and curved east wing','curved-head end pavilions','real open ground-floor arcade','red diamond frieze and supported rooftop trellis'],
213:['three-storey office and student-service wings','glazed central circulation/clerestory','low curved east meeting pavilion','supported entrance canopy','west-facing ventilation screen'],
300:['separate north and south arts wings','high-bay studio and two-storey classroom masses','open sculpture courtyards','glazed gallery fronts','roof monitors and shaded circulation'],
350:['seven-storey courtyard tower','recessed paired residential bays','deep concrete vertical piers','solid horizontal slab bands','lower glazed arrival and entrance canopy'],
308:['low mapped residential wings','individual low-pitched clay roofs','deep garden eaves','courtyard veranda with grounded columns','glazed garden doors and chimney'],
320:['low west laboratory bar and taller east coastal block','clay hipped roofs','continuous shaded sea-facing glazing','white concrete floor bands','recessed entrance and supported balcony']}
NOTES={i:('; '.join(fs)+'. Exterior member dimensions and unmeasured heights are approximate.','按公开建筑外观资料分体重建；构件尺寸与未公布标高为近似。')for i,fs in FEATURES.items()}

def edges(q):
    for pp in polygons(q):
        for ring in [pp.exterior,*pp.interiors]:
            cs=np.asarray(ring.coords)
            for a,b in zip(cs[:-1],cs[1:]):
                v=b-a;ln=np.linalg.norm(v)
                if ln>.4:
                    u=v/ln;yield a,b,u,np.array([u[1],-u[0]]),ln

def rails(ms,g,z):
    for a,b,u,n,ln in edges(g):
        if ln<1:continue
        ms['Frame'].append(cylinder((*a,z+1.03),(*b,z+1.03),.035,5))
        for dd in np.linspace(0,ln,max(2,int(ln/2)+1)):
            c=a+u*dd;ms['Frame'].append(cylinder((*c,z),(*c,z+1.03),.028,5))

def flights(ms,start,end,z,rise,width,steps):
    a,b=np.array(start),np.array(end);v=b-a;ln=np.linalg.norm(v);u=v/ln;n=np.array([-u[1],u[0]])
    for k in range(steps):
        c0=a+v*k/steps;c1=a+v*(k+1)/steps
        add(ms,Polygon([c0-n*width/2,c0+n*width/2,c1+n*width/2,c1-n*width/2]),z-.10,(k+1)*rise/steps+.10,'Concrete')
    for side in [-1,1]:
        aa=a+n*width*.46*side;bb=b+n*width*.46*side
        ms['Frame'].append(cylinder((*aa,z+1.0),(*bb,z+rise+1),.035,5))
        for t in [0,.5,1]:
            c=aa+(bb-aa)*t;ms['Frame'].append(cylinder((*c,z+rise*t),(*c,z+rise*t+1),.028,5))

def pitched_wing(ms,g,z,rise,material='RoofClay'):
    for q in polygons(g):
        cc=np.asarray(q.minimum_rotated_rectangle.exterior.coords)[:4];ee=np.roll(cc,-1,axis=0)-cc;u=ee[np.argmax(np.linalg.norm(ee,axis=1))];u/=np.linalg.norm(u);v=np.array([-u[1],u[0]]);o=np.array(q.centroid.coords[0])
        local=affinity.affine_transform(q,[*u,*v,-o@u,-o@v]);m=np.eye(4);m[:2,0]=u;m[:2,1]=v;m[:2,3]=o
        for mesh in pitched(local,z,rise):mesh.apply_transform(m);ms[material].append(mesh)

def build_reconstruction(id,p,z,ms,code,lay,info):
    if id not in REFS:return None
    parts=[];occupied=Polygon()
    def body(name,g,h,n,mat='ConcreteBlock',offset=0):
        for q in polygons(g):
            if id==282 and offset==0 and name=='curved-east-wing':
                # The courtyard-facing lower edge is an open arcade. Upper
                # floors bridge the recess; masonry piers remain grounded.
                recess=q.intersection(box(-255,-2,-230,44))
                if not recess.is_empty:
                    for low in polygons(q.difference(recess)):
                        native_extrude(low,z,3.4,code+'_ArcadeBase',lay,mat,info);push(code+'AR'+str(len(parts)).zfill(2)+str(len(ms[mat])),extrusion(low,z,3.4),mat,lay,native=False,info=info)
                    add(ms,recess,z+3.25,.18,'Concrete')
                    for yy in np.arange(1,42,5.6):
                        xx=-231.3
                        if recess.covers(Point(xx,yy)):ms['Concrete'].append(boxmesh(xx,yy,z,.42,.42,3.25))
                    native_extrude(q,z+3.4,h-3.4,code+'_ArcadeUpper',lay,mat,info);push(code+'RU'+str(len(parts)),extrusion(q,z+3.4,h-3.4),mat,lay,native=False,info=info)
                    parts.append({'name':name,'poly':q,'height_m':h,'storeys':n,'offset_m':0,'area_m2':round(q.area,2)})
                    continue
            native_extrude(q,z+offset,h,code+'_'+name,lay,mat,info)
            push(code+'R'+str(len(parts)).zfill(2),extrusion(q,z+offset,h),mat,lay,native=False,info=info)
            parts.append({'name':name,'poly':q,'height_m':h+offset,'storeys':n,'offset_m':offset,'area_m2':round(q.area,2)})
    def cut(name,mask,h,n,mat='ConcreteBlock'):
        nonlocal occupied
        g=p.intersection(mask).difference(occupied);occupied=unary_union([occupied,g]);body(name,g,h,n,mat);return g
    def finish(g,h,mat='RoofLibraryWarm'):flat_finish(ms,g,z+h,mat)
    def skin(part,style='punched',spacing=3.7,piers=False,shade=False):
        q,h,n,off=part['poly'],part['height_m'],part['storeys'],part['offset_m'];dh=(h-off)/n
        for a,b,u,v,ln in edges(q):
            if ln<2:continue
            probe=Point(*((a+b)/2+v*.25));blocked=max([r['height_m']for r in parts if r is not part and r['poly'].buffer(.05).covers(probe)],default=0)
            count=max(1,int(ln/spacing));step=ln/count
            for k in range(n):
                zz=off+k*dh
                if zz+.5<blocked:continue
                for j in range(count):
                    c=a+u*((j+.5)*step);w=step*(.86 if style=='glass'else .57);wh=dh-(.7 if style=='glass'else 1.25)
                    # Keep the arcade void clear: the upper glazing rhythm
                    # cannot continue as detached ground-floor window panels.
                    if id==282 and part['name']=='curved-east-wing' and k==0 and box(-255,-2,-230,44).covers(Point(*(c-v*.1))):continue
                    pane(ms,c-u*w/2,c+u*w/2,z+zz+.45,wh,v,'DarkGlass','Frame',style=='glass')
                # Slabs project slightly; their outer edge never shares a plane
                # with either the windows or the roof skin.
                if k>0 or shade:linebeam(ms,a+v*.16,b+v*.16,z+zz,.20,.48 if shade else .21,'Concrete')
            if piers:
                for dd in np.linspace(0,ln,count+1):
                    c=a+u*dd+v*.17;linebeam(ms,c-v*.10,c+v*.42,z+max(off,blocked),h-max(off,blocked),.27,'Concrete')
    a,b,c,d=p.bounds
    if id==218:
        court=affinity.scale(Point(304.0,386.5).buffer(1,quad_segs=40),6.5,4.2)
        west=p.intersection(box(a-1,b-1,291.0,d+1));east=p.difference(west)
        body('laboratory-west',west,14.5,3,'Concrete')
        body('atrium-office-ring',east.difference(court),13.6,3,'Concrete')
        add(ms,court,z,.13,'Paving')
        finish(west,14.5,'RoofLibraryGray');finish(east.difference(court),13.6,'RoofLibraryGray')
        for part in parts:skin(part,'glass'if part['name'].startswith('atrium')else 'punched',4.1)
        # Open circular galleries, connected to the office ring at every floor.
        for level in [4.5,9.0]:
            gallery=court.difference(court.buffer(-1.30));add(ms,gallery,z+level-.18,.18,'Concrete');rails(ms,court.buffer(-1.30),z+level)
        for k in range(2):flights(ms,(300,383),(300,389.8),z+k*4.5,4.5,1.5,24)
        # Solar screen is confined to the south-facing office elevation.
        for aa,bb,u,v,ln in edges(east):
            if v[1]>-.65 or ln<8:continue
            for dd in np.arange(.6,ln-.2,1.45):
                cc=aa+u*dd+v*.5;linebeam(ms,cc-v*.42,cc+v*.45,z+.35,13.25,.13,'Tile')
            linebeam(ms,aa+v*.75,bb+v*.75,z+13.65,.20,1.9,'Tile')
            for lev in [4.5,9]:linebeam(ms,aa+v*.45,bb+v*.45,z+lev,.20,1.1,'Tile')
    elif id==280:
        cut('south-office-wing',box(a-1,b-1,c+1,b+20),12.9,3,'ConcreteBlock')
        cut('northern-laboratory-wing',p,13.4,3,'ConcreteBlock')
        for part in parts:skin(part,'punched',4.0);finish(part['poly'],part['height_m'],'RoofPavilion')
        # Clear atrium glazing is local to the entrance hinge, not every face.
        for aa,bb,u,v,ln in edges(p):
            if ln<12:continue
            if v[1]<-.65:
                for zz in [4.0,8.4,12.8]:linebeam(ms,aa+v*.45,bb+v*.45,z+zz,.12,1.0,'Metal')
        hinge=np.array([a+18,b+20]);q=p.boundary.interpolate(p.boundary.project(Point(*hinge)));cc=np.array(q.coords[0])
        # Use the nearest long facade at the actual inner plan hinge.
        candidates=[e for e in edges(p)if e[4]>12];aa,bb,u,v,ln=min(candidates,key=lambda e:LineString([e[0],e[1]]).distance(Point(*hinge)))
        mid=aa+u*min(ln-4,max(4,LineString([aa,bb]).project(Point(*hinge))))
        pane(ms,mid-u*3.4,mid+u*3.4,z+.25,12.5,v,'Glass','Frame')
        for part in list(parts):
            q=part['poly'].buffer(-1.1,join_style=2);strip=q.intersection(box(a+2,d-5,c-2,d-1))
            body('set-back-clerestory',strip,1.2,1,'Glass',part['height_m']+.38)
            finish(strip,part['height_m']+1.58,'RoofLibraryGray')
    elif id==227:
        main=p.intersection(box(a-1,b-1,c+1,245));annex=p.difference(main)
        lobby=main.intersection(box(a-1,201,699,240));body('north-glazed-lobby',lobby,13.2,3,'Concrete')
        body('laboratory',main.difference(lobby),13.6,3,'WhitePanel');body('low-ancillary',annex,3.7,1,'ConcreteBlock')
        for part in parts:skin(part,'glass'if 'lobby'in part['name']else 'punched',3.9);finish(part['poly'],part['height_m'],'RoofLibraryGray')
        for aa,bb,u,v,ln in edges(main):
            if ln<18:continue
            # Narrow members attach to slab edges and stop at the parapet.
            for dd in np.arange(.7,ln-.4,2.8):
                cc=aa+u*dd+v*.22;linebeam(ms,cc-v*.16,cc+v*.28,z+.1,13.4,.13,'LightStone')
        # The north end's angled feature wall is a solid architectural wall,
        # not the video display shown only in the unrealized concept drawing.
        end=main.intersection(box(680,231,722,235));wall=extrusion(end,z+.05,13.8);wall.vertices[:,0]+=(wall.vertices[:,2]-z)*.055;ms['ConcreteBlock'].append(wall)
        pane(ms,(674.4,205),(674.4,230),z+.2,8.3,(-1,0),'Glass','Frame')
    elif id==321:
        high=cut('five-storey-north-bar',box(539,10,c+1,33),18.4,5,'Concrete')
        south=cut('courtyard-south-wing',box(a-1,b-1,601,10),11.2,3,'Concrete')
        cut('east-stair-wing',p,14.8,4,'Concrete')
        for part in parts:skin(part,'punched',3.9,True,True);finish(part['poly'],part['height_m'],'RoofLibraryGray')
        pane(ms,(550,b-.06),(569,b-.06),z+.1,3.7,(0,-1),'Glass','Concrete')
        add(ms,box(548,b-1.7,570,b+.2),z+3.9,.22,'Concrete')
        for x0 in [548.4,560,569.6]:ms['Concrete'].append(boxmesh(x0,b-.9,z,.28,.28,3.9))
    elif id==288:
        cut('western-laboratory',box(a-1,b-1,507,d+1),15.7,4,'ConcreteBlock')
        cut('northern-office',box(507,-29,c+1,d+1),14.7,4,'Limestone')
        cut('ocean-office',p,11.6,3,'Limestone')
        for part in parts:skin(part,'glass'if 'office'in part['name']else 'punched',4.4,False,True);finish(part['poly'],part['height_m'],'RoofLibraryWarm')
        courts=[Polygon(r)for q in polygons(p)for r in q.interiors]
        for court in courts:
            add(ms,court,z,.13,'Paving')
            for aa,bb,u,v,ln in edges(court):
                if ln<8:continue
                # Supported shade ledge over the courtyard circulation.
                strip=LineString([aa,bb]).buffer(1.1,cap_style=2).difference(p.buffer(-.1));add(ms,strip,z+3.5,.16,'Concrete')
                for dd in np.arange(1,ln-1,5.5):
                    cc=aa+u*dd;ms['Concrete'].append(cylinder((*cc,z),(*cc,z+3.5),.13,8))
        lab=parts[0]['poly'];mask=lab.buffer(-3)
        for yy in np.arange(b+6,d-4,4.8):
            for xx in [489.5,494.5,499.5]:
                patch=box(xx-1.8,yy-.85,xx+1.8,yy+.85)
                if mask.covers(patch):add(ms,patch,z+16.15,.12,'SolarLibrary')
    elif id==287:
        cut('west-laboratory-wing',box(a-1,b-1,484,d+1),15.0,4,'ConcreteBlock')
        cut('north-office-wing',box(484,-104,c+1,d+1),14.5,4,'ConcreteBlock')
        cut('curved-ocean-wing',p,14.5,4,'ConcreteBlock')
        for part in parts:skin(part,'glass'if 'ocean'in part['name']else 'punched',3.7,False,True);finish(part['poly'],part['height_m'],'RoofLibraryWarm')
        for q in polygons(p):
            for ring in q.interiors:
                court=Polygon(ring);add(ms,court,z,.14,'Paving');ledge=court.intersection(box(484,-129,502,-122));add(ms,ledge,z+3.62,.20,'Paving');rails(ms,ledge,z+3.82)
                for xx in [485,491,498]:ms['Concrete'].append(cylinder((xx,-125,z),(xx,-125,z+3.62),.13,8))
    elif id==297:
        cut('Lotte-Lehmann-performance-hall',box(-20,-157,15,-120),10.2,2,'ConcreteBlock')
        cut('Karl-Geiringer-hall',box(15,-171,57,-144),9.0,2,'ConcreteBlock')
        cut('north-teaching-wing',box(-20,-115,100,-84),10.6,3,'Limestone')
        cut('courtyard-studios',p,7.1,2,'Limestone')
        for part in parts:
            skin(part,'punched',3.8);nearby_roof(ms,part['poly'],z+part['height_m'],297)
        for q in polygons(p):
            for ring in q.interiors:
                court=Polygon(ring);add(ms,court,z,.14,'Paving')
                # Arcade paths remain outside the open central court.
                arcade=court.difference(court.buffer(-1.5));add(ms,arcade,z+3.12,.18,'RoofLibraryWarm')
                for aa,bb,u,v,ln in edges(court):
                    for dd in np.arange(1,ln-1,4.6):
                        cc=aa+u*dd;ms['LightStone'].append(cylinder((*cc,z),(*cc,z+3.12),.14,8))
        bowl=Point(39,-123)
        for k in range(5):
            outer=bowl.buffer(8+k*1.1,quad_segs=28);inner=bowl.buffer(7.4+k*1.1,quad_segs=28);q=outer.difference(inner).intersection(box(18,-130,63,-113)).difference(p)
            add(ms,q,z,.20+k*.22,'ConcreteBlock')
        add(ms,box(33,-129,45,-126).difference(p),z,.34,'Paving')
    elif id==282:
        cut('six-storey-northern-tower',box(a-1,48,c+1,d+1),22.3,6,'WhitePanel')
        cut('four-storey-west-wing',box(a-1,b-1,-257,48),14.8,4,'WhitePanel')
        cut('curved-east-wing',p,14.8,4,'WhitePanel')
        # Ground-level arcade is genuinely open along the court-facing edge.
        for part in parts:
            q=part['poly'];h=part['height_m'];skin(part,'punched',4.4)
            finish(q,h,'RoofLibraryWarm')
            for aa,bb,u,v,ln in edges(q):
                if ln<18:continue
                for dd in np.arange(1.2,ln-.8,4.4):
                    cc=aa+u*dd+v*.25
                    # Photographed red diamond frieze beneath the top trellis.
                    mark=boxmesh(*cc,z+h-2.25,.47,.12,.47);angle=math.atan2(u[1],u[0]);mark.apply_transform(trimesh.transformations.rotation_matrix(math.pi/4,[v[0],v[1],0],point=[*cc,z+h-2.0]));ms['Tile'].append(mark)
                    linebeam(ms,cc-v*.3,cc+v*1.35,z+h+.42,.18,.18,'Concrete')
                linebeam(ms,aa+v*1.25,bb+v*1.25,z+h+.42,.16,.20,'Concrete')
        for center in [(-310,-29.0),(-218,-24.8)]:
            # Thin vertical convex-head end walls, matching the photographed
            # elevator pavilion silhouette rather than cylinders on the roof.
            xs=np.linspace(-4.4,4.4,25);profile=Polygon([(-4.4,0),(4.4,0),*[(xx,1.8+1.15*math.sqrt(max(0,1-(xx/4.4)**2)))for xx in xs[::-1]]])
            for pp in polygons(profile):
                mm=extrusion(pp,0,.35);vv=mm.vertices.copy();mm.vertices=np.column_stack([center[0]+vv[:,0],center[1]-.18+vv[:,2],z+14.65+vv[:,1]]);trimesh.repair.fix_normals(mm);ms['WhitePanel'].append(mm)
            pane(ms,(center[0]-.50,center[1]-.2),(center[0]+.50,center[1]-.2),z+9.9,5.3,(0,-1),'DarkGlass','Frame')
        pane(ms,(-320,-29),(-300,-29),z+.2,3.2,(0,-1),'DarkGlass','Concrete')
    elif id==213:
        cut('curved-meeting-pavilion',box(-446,-74,c+1,d+1),5.6,1,'Concrete')
        cut('central-glazed-circulation',box(-463,b-1,-453,d+1),12.8,3,'Concrete')
        cut('west-student-services',p,11.8,3,'ConcreteBlock')
        for part in parts:skin(part,'glass'if any(x in part['name']for x in ['glazed','curved'])else 'punched',3.8);finish(part['poly'],part['height_m'],'RoofLibraryGray')
        # Taller clerestory lies over the circulation, not every office roof.
        lantern=box(-462,-84,-454,-65).intersection(p);body('clerestory',lantern,1.8,1,'Glass',12.8);finish(lantern,14.6,'RoofLibraryGray')
        canopy=box(-465,-93,-450,-87);add(ms,canopy,z+3.65,.23,'Concrete')
        for x0 in [-464,-451]:ms['Concrete'].append(cylinder((x0,-92,z),(x0,-92,z+3.65),.14,8))
        for yy in np.arange(-86,-57,1.3):linebeam(ms,(-498,yy),(-497.5,yy),z+1.0,9.8,.10,'Boardwalk')
    elif id==300:
        cut('north-classroom-and-gallery',box(a-1,-124,c+1,d+1),8.2,2,'ConcreteBlock')
        cut('south-high-bay-studios',p,6.6,1,'ConcreteBlock')
        for part in parts:skin(part,'punched',4.2);finish(part['poly'],part['height_m'],'RoofLibraryGray')
        for xx,yy in [(-182,-94),(-149,-151)]:
            monitor=box(xx-8,yy-2,xx+8,yy+2).intersection(p.buffer(-1));body('studio-roof-monitor',monitor,1.3,1,'Glass',8.57 if yy>-125 else 6.97);finish(monitor,10.0 if yy>-125 else 8.4,'RoofLibraryGray')
        pane(ms,(-162,-135),(-125,-135),z+.3,3.6,(0,1),'Glass','Frame')
        for yy in [-105,-173]:
            q=box(-177,yy-1.5,-118,yy+.1).intersection(p.buffer(1.2));add(ms,q,z+3.4,.18,'Concrete')
            for xx in np.arange(-173,-120,5.8):
                if p.buffer(1.2).covers(Point(xx,yy)):ms['Concrete'].append(cylinder((xx,yy,z),(xx,yy,z+3.4),.12,8))
    elif id==350:
        body('seven-storey-tower',p,22.5,7,'ConcreteBlock')
        for part in parts:skin(part,'punched',3.55,True,True);finish(part['poly'],part['height_m'],'RoofLibraryGray')
        for aa,bb,u,v,ln in edges(p):
            if ln<5:continue
            # Recessed panels below pairs of lights; floor-height concrete fins
            # are integrated with the continuous slabs rather than loose poles.
            for dd in np.arange(1.8,ln-1,3.55):
                cc=aa+u*dd+v*.12
                for k in range(7):linebeam(ms,cc-u*.73,cc+u*.73,z+k*22.5/7+.2,.65,.13,'RoofLibraryWarm')
        pane(ms,(-504,-227),(-486,-227),z+.15,2.9,(0,1),'Glass','Frame')
        add(ms,box(-504,-228,-486,-223.5),z+3.1,.20,'Concrete')
        for xx in [-503.5,-486.5]:ms['Concrete'].append(cylinder((xx,-224,z),(xx,-224,z+3.1),.13,8))
    elif id==308:
        body('garden-residence',p,3.2,1,'Limestone')
        for part in parts:skin(part,'glass',4.7)
        wings=[box(a-1,b-1,309.5,d+1),box(316.4,b-1,c+1,d+1),box(309.5,-515.6,316.4,-505.5)]
        used=Polygon()
        for mask in wings:
            q=p.intersection(mask).difference(used);used=unary_union([used,q]);pitched_wing(ms,q.buffer(.55,join_style=2),z+3.2,1.15)
        veranda=box(309.3,-506,316.7,-501.8);add(ms,veranda,z+3.05,.16,'RoofClay')
        for xx in [310,316]:ms['LightStone'].append(cylinder((xx,-502,z),(xx,-502,z+3.05),.14,8))
        add(ms,box(320,-515,321.2,-513.4),z+3.2,1.7,'ConcreteBlock')
    elif id==320:
        cut('three-storey-eastern-coastal-block',box(388,b-1,c+1,d+1),9.7,3,'WhitePanel')
        cut('two-storey-west-laboratory',p,6.8,2,'WhitePanel')
        for part in parts:skin(part,'glass',4.6,False,True);pitched_wing(ms,part['poly'].buffer(.5,join_style=2),z+part['height_m'],.9)
        # White concrete balcony rim and its real supports face the shore.
        ledge=box(389,-655.5,411,-651.7).intersection(p.buffer(.65));add(ms,ledge,z+6.45,.22,'Concrete');rails(ms,ledge,z+6.67)
        for xx in [391,400,409]:ms['WhitePanel'].append(cylinder((xx,-654,z),(xx,-654,z+6.45),.14,8))
    highest=max(m.bounds[1,2]-z for group in ms.values()for m in group)
    for r in parts:r.pop('poly')
    return float(highest),max(r['storeys']for r in parts),parts
