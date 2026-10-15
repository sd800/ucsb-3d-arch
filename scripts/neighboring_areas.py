"""Isla Vista context from retained OSM outlines and an expanded USGS DEM.
Neighbor buildings and outdoor context have independent layers. No private
interiors, invented towers, roof machines or exhaustive parking grids are added.
"""
from cad_core import *
from campus_refinement import pane,add,linebeam
from shapely import segmentize,points
from shapely.strtree import STRtree
from scipy.interpolate import RegularGridInterpolator
from PIL import Image

NAMES={'Isla Vista Theater':'伊斯拉维斯塔剧院','Pardall Center':'帕多尔中心','Embarcadero Hall':'恩巴卡德罗楼','St. Michael’s University Church':'圣米迦勒大学教堂','St. Mark’s University Parish':'圣马可大学堂区','Isla Vista Community Center':'伊斯拉维斯塔社区中心','Pardall Gardens':'帕多尔花园','Anisq’Oyo’ Park':'Anisq’Oyo’ 公园','Anisq\'Oyo\' Park':'Anisq’Oyo’ 公园','Little Acorn Park':'小橡果公园','People’s Park':'人民公园','Perfect Park':'Perfect 公园','Estero Park':'埃斯特罗公园','Sea Lookout Park':'海景公园','Window-to-the-Sea Park':'海之窗公园','Pelican Park':'鹈鹕公园','Trigo-Pasado Park':'特里戈—帕萨多公园','Del Playa Open Space':'德尔普拉亚开放空间'}

def build_neighbors(osm,campus_scope,campus_footprints,ocean,campus_ground):
    selection=box(-2850,-760,-490,720)
    extent=selection.difference(ocean).difference(campus_scope.buffer(.02)).buffer(0)
    candidates=[]
    for f in osm:
        t=f['properties'];p=f['poly']
        if not t.get('building') or p.geom_type not in ['Polygon','MultiPolygon']or p.area<15:continue
        if not selection.covers(p.representative_point())or p.intersection(campus_footprints).area>p.area*.01:continue
        if t.get('building')in ['roof','construction','demolished']or t.get('location')=='underground':continue
        candidates.append(f)
    accepted=[]
    for f in sorted(candidates,key=lambda f:-f['poly'].area):
        p=f['poly'];overlaps=[a['poly']for a in accepted if a['poly'].intersects(p)]
        if overlaps and p.intersection(unary_union(overlaps)).area>p.area*.12:continue
        if overlaps:p=p.difference(unary_union(overlaps).buffer(.03)).buffer(0)
        if p.area>15:accepted.append({**f,'poly':p})
    accepted.sort(key=lambda f:(-f['poly'].centroid.y,f['poly'].centroid.x))
    footprints=unary_union([f['poly']for f in accepted]);allfoot=unary_union([footprints,campus_footprints])
    # Include complete selected buildings at the scope edge; do not slice a
    # neighbor house into a floating fragment along the context selection box.
    extent=unary_union([extent,*[f['poly'].buffer(2)for f in accepted]]).difference(ocean).difference(campus_scope.buffer(.02)).buffer(0)
    ex=json.loads((ROOT/'sources/neighbor_terrain_metadata.json').read_text())['extent'];dem=np.asarray(Image.open(ROOT/'sources/neighbor_terrain_dem.tif'),dtype=float)
    xs=np.linspace(ex['xmin'],ex['xmax'],dem.shape[1],endpoint=False)+(ex['xmax']-ex['xmin'])/dem.shape[1]/2-OX
    ys=np.linspace(ex['ymin'],ex['ymax'],dem.shape[0],endpoint=False)+(ex['ymax']-ex['ymin'])/dem.shape[0]/2-OY
    interp=RegularGridInterpolator((ys,xs),dem[::-1],bounds_error=False,fill_value=None)
    def raw(x,y):
        x,y=np.broadcast_arrays(x,y);z=np.maximum(.18,interp(np.column_stack([y.ravel(),x.ravel()])).reshape(x.shape))
        # At the old scope edge blend only elevations (not coordinates), so the
        # public DEM snapshots meet without a step in roads and sidewalks.
        ds=np.array([campus_scope.distance(Point(xx,yy))for xx,yy in zip(x.ravel(),y.ravel())]).reshape(x.shape)
        blend=np.clip(ds/25,0,1)
        return z*blend+campus_ground(x,y)*(1-blend)
    pads=[];samples=[]
    for f in accepted:
        p=f['poly'];xy=np.vstack([np.asarray(q.exterior.coords)for q in polygons(segmentize(p,5))]);f['grade']=float(np.max(raw(xy[:,0],xy[:,1])))+.12
    tree=STRtree([f['poly'].buffer(.08)for f in accepted]);heights=np.array([f['grade']for f in accepted])
    def ground(x,y):
        x,y=np.broadcast_arrays(x,y);z=np.array(raw(x,y),copy=True);aa,bb=tree.query(points(x.ravel(),y.ravel()),predicate='within');z.ravel()[aa]=heights[bb];return z
    # Primary roads remain distinct from sidewalks; neither uses white fill.
    roadparts=[];walkparts=[];verges=[]
    widths={'primary':14,'secondary':11,'tertiary':9,'residential':7,'unclassified':7,'service':4,'living_street':5,'pedestrian':4.5}
    for f in osm:
        t=f['properties'];g=f['poly'];h=t.get('highway')
        if g.geom_type not in ['LineString','MultiLineString']or not g.intersects(extent)or t.get('tunnel')=='yes'or str(t.get('layer','0')).startswith('-'):continue
        if h in widths:
            try:w=min(18,max(2,float(t.get('width',widths[h]))))
            except ValueError:w=widths[h]
            roadparts.append(g.buffer(w/2,cap_style=2,join_style=2))
            if h!='service':walkparts.append(g.buffer(w/2+1.55,cap_style=2,join_style=2));verges.append(g.buffer(w/2+3.3,cap_style=2,join_style=2))
        elif h in ['path','footway','steps','cycleway']:walkparts.append(g.buffer(1.5 if h=='cycleway'else 1.05,cap_style=2,join_style=2))
    parking=unary_union([f['poly']for f in osm if f['properties'].get('amenity')=='parking'and f['poly'].geom_type in ['Polygon','MultiPolygon']and f['poly'].intersects(extent)])
    roads=unary_union([*roadparts,parking]).intersection(extent).difference(allfoot).buffer(0)
    walks=unary_union(walkparts).intersection(extent).difference(roads).difference(allfoot).buffer(0)
    greens=unary_union([f['poly']for f in osm if f['poly'].geom_type in ['Polygon','MultiPolygon']and(f['properties'].get('leisure')in ['park','garden','nature_reserve']or f['properties'].get('landuse')in ['grass','forest','meadow']or f['properties'].get('natural')in ['grassland','scrub','wood'])and f['poly'].intersects(extent)])
    residential=unary_union([f['poly'].buffer(3.8,join_style=2)for f in accepted if f['properties'].get('building')in ['house','detached','apartments','residential']])
    greens=unary_union([greens,residential]).intersection(extent).difference(roads.buffer(.25)).difference(walks).difference(allfoot).buffer(0)
    paved=unary_union([f['poly'].buffer(1.0,join_style=2)for f in accepted]).intersection(extent).difference(greens).difference(roads).difference(walks).difference(allfoot)
    msenv={m:[]for m in COLORS};context=[]
    layer('Neighboring_Environment','ContextGrass')
    def env(g,z,h,mat,drape=True):
        g=g.intersection(extent).buffer(0)
        for p in polygons(g):
            a,b,c,d=p.bounds
            for xx in np.arange(math.floor(a/90)*90,c,90):
                for yy in np.arange(math.floor(b/90)*90,d,90):
                    for q in polygons(p.intersection(box(xx,yy,xx+90,yy+90))):
                        if drape:q=segmentize(q,8)
                        m=extrusion(q,z,h)
                        if drape:m.vertices[:,2]+=ground(m.vertices[:,0],m.vertices[:,1])
                        msenv[mat].append(m)
    env(extent.difference(allfoot),-3,3,'ContextGround')
    env(roads,.10,.05,'ContextRoad');env(walks,.18,.045,'ContextWalk');env(greens,.14,.04,'ContextGrass');env(paved,.22,.04,'ContextPaving')
    beach=extent.intersection(ocean.buffer(11)).difference(allfoot).difference(roads).difference(walks);env(beach,.26,.04,'Sand')
    routes=unary_union([roads,walks])
    for feature in osm:
        tt=feature['properties'];gg=feature['poly']
        if gg.geom_type in ['Polygon','MultiPolygon']and tt.get('natural')=='water'and gg.intersects(extent):env(gg,.26,.04,'Water')
    for j,f in enumerate(accepted,1):
        p=f['poly'];t=f['properties'];c=p.centroid;z=f['grade'];code=f'N{j:04d}';kind=t.get('building');res=kind in ['house','apartments','residential','dormitory','detached']
        address=' '.join(filter(None,[t.get('addr:housenumber'),t.get('addr:street')]))
        name=t.get('name')or address or 'Isla Vista building '+t['osm_id'].split('/')[-1]
        try:n=max(1,min(8,int(float(t.get('building:levels','')))))
        except ValueError:n=2 if p.area<600 else 3 if res else 1
        try:h=max(3,min(32,float(t.get('height',''))))
        except ValueError:h=n*(3.05 if res else 3.65)+.45
        if name=='Isla Vista Theater':n=1;h=7.5
        pitch=t.get('roof:shape')in ['hipped','gabled','half-hipped']or kind in ['house','detached']and p.area<350
        rise=min(1.7,h*.19)if pitch else 0;body=h-rise-.18
        wall='ContextBrick'if t.get('building:material')=='brick'else 'ContextStucco'if res else 'ContextStone'
        roofmat='ContextTile'if t.get('roof:material')in ['roof_tiles','tile']or t.get('roof:colour')in ['red','#A52A2A']else 'ContextRoof'
        source='https://www.openstreetmap.org/'+t['osm_id'];lay=code+'_'+name.replace(':',' ').replace('/',' ');layer(lay,wall);ms={m:[]for m in COLORS}
        info={'NameEN':name,'Source':source,'Scope':'Campus neighboring areas','HeightStatus':'OSM tagged height or exterior estimate','Units':'meters'}
        for q in polygons(p):
            native_extrude(q,z,body,code+'_Volume',lay,wall,info);ms[wall].append(extrusion(q,z,body))
            support=extrusion(segmentize(q,5),z-1.5,1.51);bottom=support.vertices[:,2]<z-.7;support.vertices[bottom,2]=np.minimum(z-1,raw(support.vertices[bottom,0],support.vertices[bottom,1])-1.2);ms[wall].append(support)
            if pitch:ms[roofmat].extend(pitched(q.buffer(.25,join_style=2),z+body,rise))
            else:
                add(ms,q.buffer(-.07,join_style=2),z+body,.16,roofmat)
                if p.area>220:add(ms,q.boundary.buffer(.09),z+h,.20,roofmat)
            # Conservative detailed windows and low front porches; never a
            # full-height rod at every facade bay or a roof-machine template.
            for ring in [q.exterior,*q.interiors]:
                cc=np.asarray(ring.coords)
                for a,b in zip(cc[:-1],cc[1:]):
                    ln=np.linalg.norm(b-a)
                    if ln<3:continue
                    u=(b-a)/ln;normal=np.array([u[1],-u[0]]);count=min(16,max(1,int(ln/4.0)));step=ln/count
                    for k in range(n):
                        for ii in range(count):
                            center=a+u*(ii+.5)*step;ww=min(2.8,step*.62);wh=min(2.2,body/n-1.1)
                            if wh>.3:
                                c0=center+normal*.07;add(ms,Polygon([c0-u*ww/2,c0+u*ww/2,c0+u*ww/2+normal*.08,c0-u*ww/2+normal*.08]),z+k*body/n+.67,wh,'ContextGlass')
                    if res and ln>8:linebeam(ms,a+normal*.11,b+normal*.11,z+body-.22,.13,.22,roofmat)
            # A small approach meets the nearest street or mapped walk.
            from shapely.ops import nearest_points
            entry,end=nearest_points(q,routes);gap=entry.distance(end)
            if .25<gap<8:env(LineString([entry,end]).buffer(.7,cap_style=2).difference(allfoot),.24,.04,'ContextPaving')
        for k,(mat,meshes)in enumerate(ms.items()):
            if meshes:chunk_meshes(code+('D'if mat=='ContextGlass'else 'M')+f'{k:02d}',meshes,mat,lay,info)
        # Full level pad closes terrain below the complete building footprint.
        for q in polygons(p):
            m=extrusion(q,z-.18,.18);msenv['ContextGround'].append(m)
            pq=q.buffer(-.15)
            if pq.is_empty:pq=q
            if pq.geom_type!='Polygon':pq=max(pq.geoms,key=lambda a:a.area)
            for pt in [pq.representative_point()]+[pq.exterior.interpolate(pq.exterior.length*k/4)for k in range(4)]:samples.append({'code':code,'name':name,'position':[pt.x,pt.y,z]})
        record={'code':code,'facility_id':'neighbor-'+t['osm_id'],'neighbor':True,'name':name,'name_zh':NAMES.get(name,name if t.get('name')else ('伊斯拉维斯塔建筑 '+t['osm_id'].split('/')[-1]if not address else address)),'short':name,'short_zh':NAMES.get(name,name),'aliases_zh':['Isla Vista','伊斯拉维斯塔',address],'layer':lay,'zone':'neighbors','landmark':False,'height':round(h,3),'height_status':'estimated','levels':n,'area':round(p.area,2),'width':round(p.bounds[2]-p.bounds[0],2),'depth':round(p.bounds[3]-p.bounds[1],2),'center':[round(c.x,3),round(c.y,3)],'ground_m':round(z,3),'bottom_m':round(z,3),'peak_m':round(z+h+.2,3),'partition_en':'Mapped building outline, courtyard voids, grouped window bays, shallow eaves and a distinct roof finish. Unrecorded facade members and materials are approximate.','partition':'采用映射建筑轮廓，保留庭院孔洞，细化成组窗、浅檐和屋面；未记录的立面构件及材质为近似表达。','basis_en':'OSM tagged height or storeys where present; otherwise a conservative low-rise exterior estimate. Ground uses expanded USGS 3DEP sampling and a closed level building pad.','basis':'优先采用OpenStreetMap所记高度或层数；缺失时采用保守的低层建筑外部估算。地面依据扩展的USGS 3DEP采样，建筑下方采用闭合平整基座。','source':source,'footprint_source':source}
        context.append(record);pads.append({'code':code,'height':z,'bounds':p.bounds,'geometry':mapping(p)})
        if j%250==0:print('Neighbor buildings',j,flush=True)
    # Retain mapped trees. Parks and residential planting get restrained,
    # explicitly illustrative canopies with deterministic sizes on actual green.
    used=[];rng=np.random.default_rng(263064)
    treepoints=[f['poly']for f in osm if f['poly'].geom_type=='Point'and f['properties'].get('natural')=='tree'and extent.contains(f['poly'])]
    a,b,c,d=extent.bounds
    for _ in range(2300):
        pt=Point(rng.uniform(a,c),rng.uniform(b,d))
        if greens.contains(pt)and pt.distance(allfoot)>2.5 and pt.distance(roads)>1.5 and pt.distance(walks)>1:treepoints.append(pt)
    treeclear=allfoot.buffer(.8)
    for pt in treepoints:
        if treeclear.contains(pt)or any(pt.distance(other)<4.0 for other in used):continue
        used.append(pt);x,y=pt.x,pt.y;z=float(ground(x,y));hh=float(rng.uniform(4.5,8.5));r=float(rng.uniform(1.5,2.8))
        msenv['Trunk'].append(cylinder((x,y,z-.5),(x,y,z+hh*.7),.12,5));m=trimesh.creation.icosphere(subdivisions=1);m.apply_scale([r,r*.85,hh*.35]);m.apply_translation([x,y,z+hh*.72]);msenv['ContextLeaves'].append(m)
    for k,(mat,meshes)in enumerate(msenv.items()):
        if meshes:
            before=len(objects);chunk_meshes(f'NE{k:02d}',meshes,mat,'Neighboring_Environment',{'Source':'OSM; USGS 3DEP','Scope':'Campus neighboring areas','Approximation':'Unrecorded widths, heights, facade members, materials and supplementary planting approximate'})
            for obj in objects[before:]:layer_map[obj['name']]['category']='neighbor-environment'
    places=[]
    for f in osm:
        t=f['properties'];g=f['poly'];name=t.get('name','')
        if not name or not g.intersects(extent)or t.get('building')or g.geom_type not in ['Polygon','MultiPolygon']:continue
        if t.get('leisure')not in ['park','garden','nature_reserve']:continue
        q=g.intersection(extent)
        if q.area<15:continue
        c=q.representative_point();places.append({'id':'neighbor-place-'+t['osm_id'],'name':name,'name_zh':NAMES.get(name,name),'neighbor':True,'position':[c.x,c.y,float(ground(c.x,c.y))+.5],'hitArea':mapping(q),'label':False})
    report={'buildings':len(context),'bounds':list(extent.bounds),'area_m2':extent.area,'source':'OSM snapshot, expanded USGS 3DEP DEM','selection':'Mapped Isla Vista and adjacent coastal streets west of the main campus, including Pardall, the Embarcaderos, Del Playa and mapped parks. Clipping bounds are recorded here; this is not the entire Goleta municipality.','trees':len(used),'accuracy':'OSM outlines and tagged levels retained. Other low-rise heights, facade bays, materials, width estimates and supplementary planting approximate. No satellite survey or parcel measurement is claimed.'}
    (OUT/'neighboring_records.json').write_text(json.dumps(context,ensure_ascii=False,indent=2)+'\n');(OUT/'neighboring_report.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'neighboring_pads.json').write_text(json.dumps(pads,separators=(',',':')));(OUT/'neighboring_contact_samples.json').write_text(json.dumps(samples,separators=(',',':')));(OUT/'neighboring_places.json').write_text(json.dumps(places,ensure_ascii=False,separators=(',',':')))
    (OUT/'neighboring_footprints_local_meters.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':r,'geometry':mapping(f['poly'])}for r,f in zip(context,accepted)]},ensure_ascii=False,separators=(',',':')))
    with (OUT/'neighboring_building_dimensions_and_sources.csv').open('w',encoding='utf-8-sig',newline='')as fd:
        w=csv.DictWriter(fd,fieldnames=list(context[0]));w.writeheader();w.writerows(context)
    return context,report
