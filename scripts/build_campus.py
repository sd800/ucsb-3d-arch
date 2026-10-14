"""Metric coastal main-campus exterior study, from public snapshots, not an as-built BIM."""
from cad_core import *
from campus_detail import *
from ilp_architecture import DECK,pavilion_parts,pavilion_detail,pavilion_facade
from library_architecture import library_parts,library_detail,library_landscape
from roof_finishes import nearby_roof,ROOF_PROFILE
from curation import *
from coastal_geometry import open_sea_domain
from scipy.interpolate import RegularGridInterpolator
from shapely import segmentize,points,distance,contains
from shapely.strtree import STRtree
from shapely.ops import nearest_points
from PIL import Image
import re

def project(x,y,z=None):
    a,b=TF.transform(x,y);return np.asarray(a)-OX,np.asarray(b)-OY
def features(file):
    result=[]
    for f in json.loads((ROOT/'sources'/file).read_text())['features']:
        if not f.get('geometry'):continue
        q=transform(project,shape(f['geometry']))
        if q.geom_type in ['Polygon','MultiPolygon'] and not q.is_valid:q=q.buffer(0)
        if not q.is_empty:result.append({'properties':f['properties'],'poly':q})
    return result
osm=features('osm_features.geojson');raw=features('ucsb_buildings.geojson');mapped_entries=features('icm_11.geojson')
# The coastal Main Campus; Isla Vista and the separate San Clemente complex are outside scope.
scope=Polygon([(-570,-1130),(700,-1130),(1080,200),(850,540),(480,1150),(-560,1150),(-700,650),(-550,350),(-550,-600)])
waterfs=features('icm_30.geojson');ocean=next(f['poly'] for f in waterfs if f['properties'].get('Name')=='Pacific Ocean')
lagoon=next(f['poly'] for f in osm if f['properties'].get('name')=='Campus Lagoon' and f['poly'].geom_type=='Polygon')
land=scope.difference(ocean).difference(lagoon).buffer(0)
# Open sea is modeled far beyond the campus framing. Its outer color fades in the viewer.
sea_context=open_sea_domain(ocean).intersection(Point(170,-350).buffer(4200,quad_segs=64));shallow=ocean.intersection(land.buffer(65));midsea=ocean.intersection(land.buffer(420)).difference(shallow)
excluded=[];buildings=[]
for f in raw:
    t=f['properties'];id=int(t['OBJECTID']);p=f['poly'];c=p.centroid
    if id in [65,95,210,211,237,278,285,496,499,500,501,502,503,504,505,506,507,508,509,510,511,512,513,543,547,548,549,550,551,555,556,557] or not scope.intersects(c) or p.area<8:
        excluded.append({'id':id,'name':t.get('LONGNAME'),'reason':'Outside coastal main-campus scope or duplicate utility point'});continue
    name=CORRECT.get(id,(t.get('LONGNAME') or t.get('SHORTNAME') or t.get('BUILDINGID') or 'Campus Facility '+str(id)).strip())
    zone='north' if c.y>400 else ('south' if c.y<-240 else ('west' if c.x<-140 else 'central'))
    buildings.append({**f,'id':id,'name':name,'name_zh':chinese(id,name),'zone':zone})
buildings.sort(key=lambda f:(['central','west','south','north'].index(f['zone']),-f['poly'].centroid.y,f['poly'].centroid.x))
footprints=unary_union([f['poly'] for f in buildings])
campus_property=next(f['poly']for f in osm if f['properties'].get('osm_id')=='relation/12409275')
# Keep mapped campus land and the complete coastal point, without filling the
# neighboring airport area with a large unclassified ground sheet.
model_extent=scope
scope=unary_union([scope.intersection(campus_property.buffer(8)),scope.intersection(box(-700,-1130,700,-500)),footprints.buffer(5)]).buffer(0)
# The campus parcel ends at the bluff, while the historical water polygon starts
# at the beach. Keeping only the parcel left an unmodeled white coastal strip.
# Complete that land context up to the source waterline without filling airport
# parcels or extending the offshore surface across actual land.
parcel_extent=scope
coastal_completion=model_extent.buffer(30).intersection(ocean.buffer(45)).difference(ocean).difference(scope).buffer(0)
scope=unary_union([scope,coastal_completion]).buffer(0)
land=scope.difference(ocean).difference(lagoon).buffer(0);meta=json.loads((ROOT/'sources/terrain_export_metadata.json').read_text());ex=meta['extent'];dem=np.asarray(Image.open(ROOT/'sources/terrain_dem.tif'),dtype=float)
assert np.isfinite(dem).all() and dem.min()>-100 and dem.max()<200
xs=np.linspace(ex['xmin'],ex['xmax'],dem.shape[1],endpoint=False)+(ex['xmax']-ex['xmin'])/dem.shape[1]/2-OX
ys=np.linspace(ex['ymin'],ex['ymax'],dem.shape[0],endpoint=False)+(ex['ymax']-ex['ymin'])/dem.shape[0]/2-OY
interpolate=RegularGridInterpolator((ys,xs),dem[::-1],bounds_error=False,fill_value=None)
def raw_ground(x,y):
    x,y=np.broadcast_arrays(x,y);z=np.maximum(.18,interpolate(np.column_stack([y.ravel(),x.ravel()])).reshape(x.shape))
    pts=points(x.ravel(),y.ravel());mask=contains(coastal_completion,pts)
    if np.any(mask):
        wet=distance(pts[mask],ocean);inland=distance(pts[mask],parcel_extent)
        blend=wet/np.maximum(.01,wet+inland)
        z.ravel()[mask]=.18+(z.ravel()[mask]-.18)*blend
    return z
for f in buildings:
    c=f['poly'].representative_point();f['ground']=float(raw_ground(c.x,c.y))
pad_tree=STRtree([f['poly'].buffer(.25) for f in buildings]);pad_z=np.array([f['ground'] for f in buildings])
def ground(x,y):
    x,y=np.broadcast_arrays(x,y);z=np.asarray(raw_ground(x,y));aa,bb=pad_tree.query(points(x.ravel(),y.ravel()),predicate='within');z.ravel()[aa]=pad_z[bb];return z
print('Preparing',len(buildings),'building layers',flush=True)
for j,f in enumerate(buildings,1):
    id,p,t=f['id'],f['poly'],f['properties'];code=f'S{j:03d}';lay=code+'_'+f['name'];base=f['ground'];a,b,c,d=p.bounds;x,y=p.centroid.coords[0]
    levels=LEVELS.get(id,int(t.get('FLOORCOUNT') or (1 if p.area<500 else 2)))
    if id in PITCHED:levels=int(t.get('FLOORCOUNT') or levels)
    levels=max(1,min(levels,8));height=HEIGHTS.get(id,max(3.5,levels*(3.2 if 'Residence' in f['name'] else 3.7)+.6))
    # Unspecified-unit GIS heights are retained in metadata, but are not silently converted to metric.
    tile=id in PITCHED or id in {293,312,313,314,307,328,351,332};mat='Limestone'
    if id in {218,277}:mat='Concrete'
    if id in {280,284,227}:mat='WhitePanel'
    if id in {276,279,283,299}:mat='Concrete'
    if 'Greenhouse' in f['name']:mat='Glass'
    layer(lay,mat);ms={m:[] for m in COLORS};info={'FacilityID':id,'NameEN':f['name'],'NameZH':f['name_zh'],'FootprintSource':GIS,'HeightStatus':'Published overall height' if id==353 else 'Estimated exterior','Units':'meters'}
    partitions=[];body_index=0
    # Closed below-grade support is separate from the measured above-ground envelope.
    # Its lower perimeter follows the DEM and overlaps the terrain, avoiding open bases.
    for q in polygons(segmentize(p,5)):
        support=extrusion(q,base-1.5,1.51);bottom=support.vertices[:,2]<base-.7
        support.vertices[bottom,2]=np.minimum(base-.2,raw_ground(support.vertices[bottom,0],support.vertices[bottom,1])-1.5)
        ms['Foundation'].append(support)

    if id==353:storke(ms,p,base,height)
    elif id==291:
        parts=library_parts(p,osm);levels=8;height=32.88
        for name,volume,hh,n in parts:
            material='Glass' if name=='paseo' else ('WhitePanel' if name in ['addition','original'] else 'ConcreteBlock')
            for q in polygons(volume):
                native_extrude(q,base,hh,code+'_Volume',lay,material,info);push(code+'B'+f'{body_index:02d}',extrusion(q,base,hh),material,lay,native=False,info=info);body_index+=1
                partitions.append({'name':name,'area_m2':round(q.area,2),'height_m':hh,'storeys':n})
        library_detail(ms,p,base,parts)
    elif id==277:
        height=18.18;levels=4
        for q,hh,n,balcony in pavilion_parts(p):
            volumes=[(q,0,hh,n)] if balcony is None else [(q,0,4.4-DECK,1),(q.difference(balcony[1]),4.4-DECK,hh-4.4+DECK,3)]
            for volume,z0,h0,n0 in volumes:
                for part in polygons(volume):
                    native_extrude(part,base+z0,h0,code+'_Volume',lay,'WhitePanel',info);push(code+'B'+f'{body_index:02d}',extrusion(part,base+z0,h0),'WhitePanel',lay,native=False,info=info);body_index+=1
                    pavilion_facade(ms,part,base+z0,h0,n0)
            partitions.append({'area_m2':round(q.area,2),'height_m':hh,'storeys':n})
        pavilion_detail(ms,p,base,ground)
    elif id in {343,345}:
        # Each mapped stand is its own layer. Stepped seating follows the real long axis.
        for q in polygons(p):
            ah,bh,ch,dh=q.bounds
            rows=18 if id==343 else 14
            for n in range(rows):
                strip=q.intersection(box(ah+(ch-ah)*n/rows,bh,ch,dh)) if id==345 else q.intersection(box(ah,bh,ch-(ch-ah)*n/rows,dh))
                for pp in polygons(strip):ms['Seat'].append(extrusion(pp,base+n*.46,.48))
            for yy in np.arange(bh+5,dh-3,20):ms['Concrete'].append(boxmesh((ah+ch)/2,yy,base,1.0,1.0,5.2))
    else:
        for volume,hh,n in split_volumes(id,p,height,levels):
            if volume.is_empty:continue
            if tile:hh=max(3.3,hh-1.6)
            for q in polygons(volume):
                native_extrude(q,base,hh,code+'_Volume',lay,mat,info);push(code+'B'+f'{body_index:02d}',extrusion(q,base,hh),mat,lay,native=False,info=info);body_index+=1;partitions.append({'area_m2':round(q.area,2),'height_m':hh,'storeys':n})
                facade(ms,q,base,hh,n,continuous=id in {218,280,284,227,291},spacing=3.6 if id in {218,277,288,291} else 4.2)
                if not nearby_roof(ms,q,base+hh,id):roof(ms,q,base+hh,tile)
                bands(ms,q,base,hh,max(1,n),mat='LightStone' if mat!='Limestone' else 'Concrete')
        # Screens follow each wing's eaves. Unverified whole-building rods are omitted.
        if id in {218,288}:
            for volume,hh,n in split_volumes(id,p,height,levels):
                if volume.area>150:fins(ms,volume,base,hh,spacing=2.0 if id==218 else 5.4,mat='Tile' if id==218 else 'LightStone',depth=.30)
        # Public mapped entrances provide actual door positions; member sizes are approximate.
        entry_points=[e['poly']for e in mapped_entries if e['poly'].geom_type=='Point'and e['poly'].distance(p.boundary)<1.8]
        if not entry_points and id in {218,277,288,282,284,280,213,324,291}:entrance(ms,p,base)
        for door in entry_points:
            q=min(polygons(p),key=lambda q:q.boundary.distance(door));edge=q.exterior;at=edge.project(door);pa=edge.interpolate(max(0,at-.4));pb=edge.interpolate(min(edge.length,at+.4));u=np.array([pb.x-pa.x,pb.y-pa.y]);ln=np.linalg.norm(u)
            if ln<.05:continue
            u/=ln;n=np.array([u[1],-u[0]]);c0=np.array([door.x,door.y])+n*.10;pp=Polygon([c0-u*.75,c0+u*.75,c0+u*.75+n*.1,c0-u*.75+n*.1]);ms['DarkGlass'].append(extrusion(pp,base+.06,2.6))


        if id==303:
            center=p.centroid;m=trimesh.creation.cone(radius=21.3,height=1.6,sections=64);m.apply_translation([center.x,center.y,base+height+.24]);ms['Metal'].append(m)
        if id in {288,274,283}:
            q=p.buffer(-4);aa,bb,cc,dd=q.bounds
            for xx in np.arange(aa+2,cc-2,5):
                for yy in np.arange(bb+2,dd-2,5):
                    panel=box(xx-1.8,yy-1,xx+1.8,yy+1)
                    if q.contains(panel):
                        ms['Solar'].append(extrusion(panel,base+height+.65,.12))
                        for dx in [-1.5,1.5]:
                            for dy in [-.75,.75]:ms['Frame'].append(cylinder((xx+dx,yy+dy,base+height+.2),(xx+dx,yy+dy,base+height+.66),.045,5))
        if id==284:
            q=p.buffer(-2)
            for pp in polygons(q):ms['Garden'].append(extrusion(pp,base+height+.6,.15))
        if id in {276,279,299}:
            for xx in np.arange(a+5,c-3,8):
                q=box(xx-.12,b+4,xx+.12,d-4).intersection(p.buffer(-1))
                for pp in polygons(q):ms['Metal'].append(extrusion(pp,base+height+.27,.22))
    for q in polygons(p):
        for ring in [q.exterior,*q.interiors]:model.Objects.AddCurve(rh.PolylineCurve([rh.Point3d(xx,yy,base)for xx,yy in ring.coords]),attr(code+'_Footprint',lay,mat,info))
    # Body and roof groups remain visible when small facade details are switched off.
    for k,(mm,parts) in enumerate(ms.items()):
        if parts:chunk_meshes(code+('D' if mm in ['Glass','DarkGlass','Frame','Solar'] else 'M')+f'{k:02d}',parts,mm,lay,info)
    if ROOF_PROFILE.get(id)=='tile':height=max(height,max((m.bounds[1,2]-base for pp in ms.values()for m in pp),default=height))
    en,zh=DETAIL_NOTES.get(id,('Mapped wings and courtyard voids with repeated facade bays, entrance and roof edges. Members, heights and floor divisions are approximate.','保留映射的翼楼和庭院，表达立面开窗、入口与屋顶边缘；构件、高度及楼层划分为近似。'))
    r={'code':code,'facility_id':str(id),'official_number':t.get('BuildingNumber'),'name':f['name'],'name_zh':f['name_zh'],'official_name':t.get('LONGNAME'),'short':SHORT.get(str(id),f['name']),'short_zh':'校园图书馆' if id==291 else f['name_zh'],'aliases_zh':[str(t.get('BuildingNumber') or ''),t.get('SHORTNAME') or ''],'layer':lay,'zone':f['zone'],'landmark':str(id)in LANDMARKS,'height':round(height,3),'height_status':'published' if id==353 else 'estimated','levels':0 if id==353 else levels,'area':round(p.area,2),'width':round(c-a,2),'depth':round(d-b,2),'center':[round(x,3),round(y,3)],'ground_m':round(base,3),'bottom_m':round(base,3),'peak_m':round(max((m.bounds[1,2]for pp in ms.values()for m in pp),default=base+height),3),'basis_en':'Overall height 175 ft (53.34 m), published by UCSB.' if id==353 else 'Official 2026 footprint. Exterior storeys and heights are approximate public-source interpretations, not measurements. GIS FLOORCOUNT may include basements; the unspecified-unit BLDGHEIGHT field is retained without treating it as certified height.','basis':'总高采用UCSB官方公布的175英尺（53.34米）。' if id==353 else '采用2026年学校公开轮廓；外部层数和高度为公开资料基础上的近似表达，未经实测。GIS层数可能包含地下层，未注明单位的高度字段保留备查，不作为实测高度。','partition_en':en,'partition':zh,'volume_parts':partitions,'source':REFS.get(str(id),GIS),'footprint_source':GIS,'architecture_reference':REFS.get(str(id)),'gis_height_raw':t.get('BLDGHEIGHT'),'gis_floorcount_raw':t.get('FLOORCOUNT'),'construction_status':'Mapped in 2026 public layer'}
    records.append(r);f['record']=r
    if j%40==0:print('Buildings',j,flush=True)
print('Buildings complete',flush=True)
# Mapped outdoor surface stack: all visible regions are disjoint per material.
COLORS.update({})
eg={k:[] for k in COLORS};places=[]
def env(g,z,hh,mat,drape=True,clip=True):
    if clip:g=g.intersection(scope)
    g=g.buffer(0)
    for q in polygons(g):
        aa,bb,cc,dd=q.bounds
        size=70 if drape else 800
        for gx in np.arange(math.floor(aa/size)*size,cc,size):
            for gy in np.arange(math.floor(bb/size)*size,dd,size):
                for pp in polygons(q.intersection(box(gx,gy,gx+size,gy+size))):
                    if drape:pp=segmentize(pp,10)
                    m=extrusion(pp,z,hh)
                    if drape:
                        m.vertices[:,2]+=ground(m.vertices[:,0],m.vertices[:,1])
                        if mat in ['Walk','Cycleway']:
                            # A short graded transition meets the road surface exactly.
                            ramp=np.clip(1-distance(points(m.vertices[:,0],m.vertices[:,1]),roadarea)/1.8,0,1)
                            m.vertices[:,2]-=max(0,z+hh-.11)*ramp
                    eg[mat].append(m)
def unionfile(file):return unary_union([f['poly']for f in features(file)]).buffer(0)
roads=[];walks=[];bikes=[]
for f in osm:
    t=f['properties'];g=f['poly'];h=t.get('highway')
    if g.geom_type not in ['LineString','MultiLineString'] or t.get('tunnel')=='yes' or t.get('layer')=='-1':continue
    if h in ['primary','secondary','tertiary','residential','service','unclassified','living_street']:roads.append(g.buffer({'primary':7,'secondary':6,'tertiary':4.5,'residential':3.4,'service':2.3,'unclassified':3.2,'living_street':2.5}[h],cap_style=2,join_style=2))
    if h in ['footway','path','steps','pedestrian']:walks.append(g.buffer(1.3 if h!='path' else .95,cap_style=2,join_style=2))
    if h=='cycleway':bikes.append(g.buffer(2.0,cap_style=2,join_style=2))
parking_layout=json.loads((ROOT/'sources/parking_layouts.json').read_text());parking_fs=features('icm_2.geojson')
retired_parking=unary_union([f['poly']for f in parking_fs if f['properties']['OBJECTID']in parking_layout['retired_parking_objectids']])
active_parking=unary_union([f['poly']for f in parking_fs if f['properties']['OBJECTID']not in parking_layout['retired_parking_objectids']])
roadarea=unary_union([*roads,unionfile('icm_20.geojson'),unionfile('icm_21.geojson'),active_parking]).difference(retired_parking).intersection(land).difference(footprints).buffer(0)
# Mapped planting islands remain planted within the larger parking parcel.
parking_islands=unionfile('icm_22.geojson').intersection(active_parking).difference(footprints).difference(unary_union(roads))
roadarea=roadarea.difference(parking_islands).buffer(0)
walkarea=unary_union([*walks,unionfile('icm_18.geojson')]).intersection(land).difference(footprints).difference(roadarea).buffer(0)
for f in features('icm_5.geojson'):bikes.append(f['poly'].buffer(1.8,cap_style=2,join_style=2))
bikearea=unary_union(bikes).intersection(land).difference(footprints).difference(roadarea).buffer(0)
# Close only short mapped path endpoints that almost meet another route/road.
# No route is drawn across a lawn simply to connect unrelated nearby paths.
joins={'walk':[],'bike':[]};junction_audit=[]
join_targets={'bike':unary_union([roadarea,walkarea]),'walk':unary_union([roadarea,bikearea])}
for f in osm:
    g=f['poly'];h=f['properties'].get('highway')
    if g.geom_type!='LineString' or h not in ['footway','path','steps','pedestrian','cycleway']:continue
    if f['properties'].get('tunnel')=='yes' or f['properties'].get('layer')=='-1':continue
    kind='bike'if h=='cycleway'else 'walk';own=bikearea if kind=='bike'else walkarea
    for xy in [g.coords[0],g.coords[-1]]:
        pt=Point(*xy)
        if not land.contains(pt) or footprints.buffer(.5).contains(pt):continue
        target=join_targets[kind]
        gap=pt.distance(target)
        if .08<gap<=2.2:
            end=nearest_points(pt,target)[1];line=LineString([pt,end]);patch=line.buffer(1.7 if kind=='bike'else 1.25,cap_style=2).intersection(land).difference(footprints.buffer(.2)).difference(roadarea)
            if patch.area>.1:
                joins[kind].append(patch);junction_audit.append({'source_id':f['properties'].get('osm_id'),'kind':kind,'gap_m':round(gap,3)})
walkarea=unary_union([walkarea,*joins['walk']]).difference(roadarea).difference(footprints)
bikearea=unary_union([bikearea,*joins['bike']]).difference(roadarea).difference(footprints)
(OUT/'junction_validation.json').write_text(json.dumps({'max_join_distance_m':2.2,'joins':junction_audit,'road_walk_grade_transition_m':1.8,'note':'Small closure of source route endpoint gaps only; no inferred cross-campus routes.'},indent=2)+'\n')
lawns=unionfile('icm_22.geojson').intersection(land).difference(footprints).difference(roadarea).difference(walkarea).difference(bikearea).buffer(0)
beaches=unary_union([f['poly']for f in osm if f['properties'].get('natural')=='beach' and f['poly'].geom_type in ['Polygon','MultiPolygon']]).intersection(land)
beaches=unary_union([beaches,coastal_completion,land.intersection(ocean.buffer(10))]).difference(footprints).buffer(0)
# Cut actual footprint holes before triangulation. Evaluating the pad height only
# at sparse terrain vertices allowed triangles to pass below a flat building base.
env(land.difference(footprints),-2.5,2.5,'Ground')
for f in buildings:env(f['poly'],f['ground']-.18,.18,'Ground',False)
# Public land-cover polygons supplement the historical campus lawn inventory.
cover=[]
for f in osm:
    t=f['properties'];q=f['poly']
    if q.geom_type not in ['Polygon','MultiPolygon'] or t.get('building'):continue
    mat='Grass' if t.get('landuse') in ['grass','meadow','village_green'] or t.get('natural')=='grassland' else ('Garden' if t.get('natural') in ['scrub','wood'] or t.get('landuse')=='forest' or t.get('leisure')=='garden' else None)
    if mat:
        q=q.intersection(land).difference(footprints).difference(roadarea).difference(walkarea).difference(bikearea).difference(beaches).difference(lawns)
        if not q.is_empty:env(q,.09,.04,mat);cover.append(q)
(OUT/'surface_validation.json').write_text(json.dumps({'land_m2':land.area,'mapped_lawn_m2':lawns.area,'roads_and_parking_m2':roadarea.area,'walks_m2':walkarea.area,'cycleways_m2':bikearea.area,'supplementary_mapped_cover_m2':unary_union(cover).area,'fallback':'Muted dry-earth material for unclassified land; not an assertion of parcel-level land cover.','parking_stall_grid_generated':False,'parking_layout_source':'Satellite-interpreted row paths; sources/parking_layouts.json'},indent=2)+'\n')
env(lawns,.11,.05,'Grass');env(roadarea,.06,.05,'Road');env(walkarea.difference(bikearea),.13,.05,'Walk');env(bikearea,.11,.035,'Cycleway');env(beaches,.13,.05,'Sand')
wet_sand=beaches.intersection(ocean.buffer(2.3)).difference(footprints)
env(wet_sand,.19,.018,'WetSand')
(OUT/'shore_join_validation.json').write_text(json.dumps({'completed_coastal_land_m2':round(coastal_completion.area,2),'shore_source':ICM,'coastal_context_width_m':45,'grade':'Continuous blend between the existing parcel DEM and a 0.18 m waterline toe','closed_land_mass':True},indent=2)+'\n')
# A continuous closed earth mass, including the island and Campus Point. The
# cartographic surface renderer deliberately removes generic extrusion sides;
# the land therefore needs its own physical underside, not just a narrow coast ribbon.
# Reuse the exact top triangulation of the final grade skin. A separately
# triangulated coarse soil cap can protrude through roads on curved terrain.
for source in eg['Ground']:
    m=source.copy();up=np.unique(source.faces[source.face_normals[:,2]>.1].ravel())
    m.vertices[:,2]=-3;m.vertices[up,2]=source.vertices[up,2]-.04;eg['Earth'].append(m)
land_rings=[]
for q in polygons(land):land_rings.extend([list(q.exterior.coords),*[list(r.coords)for r in q.interiors]])
(OUT/'land_boundary.json').write_text(json.dumps(land_rings,separators=(',',':')))
# Close the real coastline down to sea level so low views do not reveal floating land.
cliff=land.intersection(ocean.buffer(2.0)).difference(footprints)
for q in polygons(cliff):
    for part in polygons(segmentize(q,8)):
        m=extrusion(part,-.45,1.0);top=m.vertices[:,2]>.1;m.vertices[top,2]=ground(m.vertices[top,0],m.vertices[top,1])+.035;eg['Bluff'].append(m)
# Mapped offshore rock islets around the point, with low irregular tops.
for f in osm:
    t=f['properties'];q=f['poly']
    if t.get('natural')=='coastline' and q.geom_type in ['Polygon','MultiPolygon'] and q.area<4000 and q.intersects(box(180,-1130,400,-900)):
        for part in polygons(q):
            m=extrusion(part,-.3,1.9);top=m.vertices[:,2]>.8;m.vertices[top,2]+=np.sin(m.vertices[top,0]*.13)*.35+np.cos(m.vertices[top,1]*.16)*.3;eg['Bluff'].append(m)
for q in polygons(sea_context):eg['OceanDepth'].append(extrusion(q,-24,24.055))
for q in polygons(lagoon):eg['LagoonDepth'].append(extrusion(q,-10,10.805))
env(sea_context,.02,.035,'Ocean',False,False);env(lagoon,.78,.025,'Water',False)
# Alongshore ribbons stay outside the mapped land. They follow the coastline.
for distance,width,zz in [(3,.8,.16),(11,.5,.17),(23,.4,.18)]:
    ribbon=land.buffer(distance+width/2).difference(land.buffer(distance-width/2)).intersection(ocean).intersection(scope.buffer(60));env(ribbon,zz,.02,'Foam',False,False)

def place(name,zh,g,z=None,source=MAP):
    g=g.intersection(scope).buffer(0)
    if g.is_empty or g.area<2:return
    c=g.representative_point();places.append({'id':'P'+str(len(places)),'name':name,'name_zh':zh,'position':[round(c.x,2),round(c.y,2),round(float(raw_ground(c.x,c.y))+.7 if z is None else z,2)],'hitArea':mapping(set_precision(g.simplify(.1),.01)),'source':source})
place('Campus Lagoon','校园泻湖',lagoon,1.1)
place('Pacific Ocean','太平洋近岸海域',ocean.intersection(scope.buffer(180)),.4)
place('Campus Point','校园岬角',land.intersection(box(200,-1130,500,-570)))
island=land.intersection(lagoon.convex_hull).intersection(box(-290,-830,180,-290));place('Lagoon Island','泻湖岛',island)
# Habitat planting and low coastal scrub; no invented lawns blanket the headland.
habitat=unary_union([land.intersection(lagoon.buffer(35)),island,land.intersection(box(-550,-1130,500,-560))]).difference(footprints.buffer(4)).difference(walkarea).difference(bikearea).difference(lawns).difference(beaches)
env(habitat,.13,.035,'Garden')
# Lagoon banks close the ground surface into the water rather than leaving a floating edge.
bank=land.intersection(lagoon.buffer(2.4)).difference(footprints)
for q in polygons(segmentize(bank,7)):
    m=extrusion(q,.62,1.0);top=m.vertices[:,2]>1;m.vertices[top,2]=np.maximum(.87,ground(m.vertices[top,0],m.vertices[top,1])+.04);eg['Bank'].append(m)
# Small reed clusters follow the mapped shore, outside the water and walks.
rng_reed=np.random.default_rng(219)
for d0 in np.arange(0,lagoon.exterior.length,9):
    q=lagoon.exterior.interpolate(d0);c0=np.array([q.x,q.y]);pa=lagoon.exterior.interpolate(max(0,d0-.5));pb=lagoon.exterior.interpolate(min(lagoon.exterior.length,d0+.5));vec=np.array([pb.x-pa.x,pb.y-pa.y]);ln=np.linalg.norm(vec)
    if ln<.01:continue
    n=np.array([-vec[1],vec[0]])/ln
    for sign in [-1,1]:
        c1=c0+n*sign*2.8;q1=Point(*c1)
        if not habitat.contains(q1)or q1.distance(walkarea)<1:continue
        for j in range(4):
            xx,yy=c1+rng_reed.uniform(-.7,.7,2);zz=float(ground(xx,yy));hh=rng_reed.uniform(.7,1.4);eg['DryGrass'].append(cylinder((xx,yy,zz),(xx+.12,yy,zz+hh),.035,4))

for f in osm:
    t=f['properties'];g=f['poly'];name=t.get('name','')
    if g.geom_type not in ['Polygon','MultiPolygon'] or t.get('building') or not g.intersects(scope):continue
    zh={'Storke Plaza':'斯托克广场','Library Plaza':'图书馆广场','Chemistry Lawn':'化学楼草坪','Noble Hall Courtyard':'诺布尔楼庭院','UCSB Rain Garden':'校园雨水花园','The Learning Garden':'学习花园','Manzanita Village Habitat Garden':'曼萨尼塔村生境花园','Marie Rogers Lowry Museum Plaza':'玛丽·罗杰斯·洛里博物馆广场','Harder Stadium':'哈德体育场','Caesar Uyesaka Stadium':'凯撒·上坂棒球场'}.get(name)
    if zh:place(name,zh,g)
    if t.get('leisure') in ['pitch','track']:
        mat='Track' if t.get('leisure')=='track' else ('Court' if t.get('sport') in ['tennis','basketball'] else 'Grass')
        env(g.difference(footprints),.23,.04,mat)
        # Mapped perimeter and centre line, clipped within actual field dimensions.
        if t.get('leisure')=='pitch':
            edge=g.boundary.buffer(.10).intersection(g);env(edge,.31,.02,'Marking')
            rect=g.minimum_rotated_rectangle;cc=np.asarray(rect.exterior.coords)[:4];u=cc[1]-cc[0];v=cc[2]-cc[1]
            if np.linalg.norm(u)<np.linalg.norm(v):u,v=v,u
            u/=np.linalg.norm(u);v/=np.linalg.norm(v);c0=np.array(g.centroid.coords[0]);r0=min(np.linalg.norm(cc[1]-cc[0]),np.linalg.norm(cc[2]-cc[1]))
            if t.get('sport')=='tennis':
                length=max(np.linalg.norm(cc[1]-cc[0]),np.linalg.norm(cc[2]-cc[1]));halfwidth=r0/2
                for dd0 in [-6.4,0,6.4]:env(LineString([c0+u*dd0-v*halfwidth,c0+u*dd0+v*halfwidth]).buffer(.055).intersection(g),.33,.015,'Marking')
                env(LineString([c0-u*6.4,c0+u*6.4]).buffer(.055).intersection(g),.33,.015,'Marking')
                for sign in [-1,1]:
                    end=c0+v*(halfwidth+.25)*sign;zz=float(ground(*end));eg['Furniture'].append(cylinder((*end,zz),(*end,zz+1.07),.045,5))
                zz=float(ground(*c0));eg['Frame'].append(cylinder((*(c0-v*halfwidth),zz+.95),(*(c0+v*halfwidth),zz+.95),.025,4))
            if t.get('sport') in ['soccer','football']:
                env(LineString([c0-v*r0/2,c0+v*r0/2]).buffer(.10).intersection(g),.32,.02,'Marking');env(Point(*c0).buffer(9.15,quad_segs=24).boundary.buffer(.10).intersection(g),.32,.02,'Marking')
                for sign in [-1,1]:
                    ends=[p0@u for p0 in np.asarray(g.exterior.coords)];end=max(ends)if sign>0 else min(ends);goal=c0+u*(end-c0@u-sign*.5)
                    for offset in [-3.66,3.66]:
                        a0=goal+v*offset;eg['Furniture'].append(cylinder((*a0,float(ground(*a0))),(*a0,float(ground(*a0))+2.44),.06,6))
                    eg['Furniture'].append(cylinder((*(goal-v*3.66),float(ground(*goal))+2.44),(*(goal+v*3.66),float(ground(*goal))+2.44),.06,6))
    if t.get('leisure')=='garden':env(g.difference(footprints).difference(walkarea),.15,.04,'Garden')
    if t.get('leisure')=='swimming_pool':env(g,.32,.04,'PoolWater');place(name or 'Campus swimming pool','校园泳池',g)
    if name in ['Storke Plaza','Library Plaza','Marie Rogers Lowry Museum Plaza']:
        env(g.difference(footprints),.26,.06,'Paving')
        # Separate paving joints are visible close up, with no coplanar skins.
        aa,bb,cc,dd=g.bounds
        for xx in np.arange(aa,cc,4):env(box(xx-.025,bb,xx+.025,dd).intersection(g).difference(footprints),.325,.012,'StoneJoint')
        for yy in np.arange(bb,dd,4):env(box(aa,yy-.025,cc,yy+.025).intersection(g).difference(footprints),.325,.012,'StoneJoint')
# Road edges remain open at pedestrian and bicycle connections.
curb=roadarea.boundary.buffer(.16).intersection(land).difference(footprints).difference(walkarea.buffer(.4)).difference(bikearea.buffer(.5))
env(curb,.11,.07,'Concrete')
# Centre dashes follow public cycle routes and stop at the road crossings.
for f in features('icm_5.geojson'):
    g=f['poly']
    for line in list(g.geoms)if g.geom_type=='MultiLineString'else [g]:
        if line.geom_type!='LineString':continue
        for dd0 in np.arange(2,line.length-2,14):
            a0=line.interpolate(dd0);b0=line.interpolate(min(dd0+2,line.length));env(LineString([a0,b0]).buffer(.055).intersection(bikearea),.27,.018,'Marking')
# Only explicitly mapped paint is drawn. Unmarked path intersections are not zebras.
from crossing_markings import crossing_markings
crossings,crossing_audit=crossing_markings(osm,land,roadarea)
for geometry in crossings:env(geometry,.14,.025,'Marking')
(OUT/'crossing_validation.json').write_text(json.dumps(crossing_audit,indent=2)+'\n')
# Bicycle racks occupy their public mapped footprints; the U-shaped bars are approximate.
for f in features('icm_7.geojson'):
    q=f['poly'].intersection(land).difference(footprints)
    if q.is_empty:continue
    for part in polygons(q):
        rect=part.minimum_rotated_rectangle;cc=np.asarray(rect.exterior.coords)[:4];vec=cc[1]-cc[0]
        if np.linalg.norm(vec)<np.linalg.norm(cc[2]-cc[1]):vec=cc[2]-cc[1]
        u=vec/np.linalg.norm(vec);v=np.array([-u[1],u[0]]);c0=np.array(part.centroid.coords[0])
        for off in np.arange(-max(1,math.sqrt(part.area))*.35,max(1,math.sqrt(part.area))*.35,.9):
            c1=c0+u*off
            if not part.contains(Point(*c1)):continue
            zz=float(ground(*c1))
            for side in [-1,1]:
                a0=c1+v*.3*side;eg['Furniture'].append(cylinder((*a0,zz),(*a0,zz+.75),.035,5))
            eg['Furniture'].append(cylinder((*(c1-v*.3),zz+.75),(*(c1+v*.3),zz+.75),.035,5))

# Furniture uses mapped OSM positions, with a few clearly illustrative plaza benches.
for f in osm:
    t=f['properties'];q=f['poly']
    if q.geom_type=='Point'and t.get('amenity')=='bench'and land.contains(q)and not footprints.buffer(.6).contains(q):
        z=float(ground(q.x,q.y));eg['Furniture'] += [boxmesh(q.x,q.y,z+.45,1.8,.5,.12),boxmesh(q.x,q.y+.22,z+.5,1.8,.08,.5)]
        for dx in [-.6,.6]:
            for dy in [-.16,.16]:eg['Furniture'].append(cylinder((q.x+dx,q.y+dy,z-.3),(q.x+dx,q.y+dy,z+.5),.045,5))
# Parking uses fine bay outlines aligned with lot edges, with a clear central aisle.
from parking_markings import parking_markings
parking_clear=unary_union([lawns,unionfile('icm_23.geojson')])
cad_paint=json.loads((ROOT/'sources/parking_paint.geojson').read_text());cad_lots={int(id)for f in cad_paint['features']for id in f['properties']['lot_ids']}
parking_paint,parking_audit=parking_markings([f for f in parking_fs if f['properties']['OBJECTID']not in cad_lots],land,footprints,roadarea,parking_layout,parking_clear)
for q in parking_paint:env(q,.14,.014,'Marking')
paint_clear=land.intersection(roadarea).difference(footprints.buffer(.4)).difference(parking_clear.buffer(.1))
paint_count=0
for feature in cad_paint['features']:
    line=shape(feature['geometry'])
    if line.length<.20:continue
    q=line.buffer(.045,cap_style=2,join_style=2).intersection(paint_clear)
    if not q.is_empty:env(q,.14,.014,'Marking');paint_count+=1
parking_audit.update({'native_cad_paint_features':paint_count,'native_cad_lots':sorted(cad_lots),'paint_geometry_source':cad_paint['source'],'paint_width_m':.09,'satellite_referenced_fallback_rows_only_for_lots_without_cad':True})
(OUT/'parking_validation.json').write_text(json.dumps(parking_audit,indent=2)+'\n')
# Satellite-observed solar carports use dark panels and open column supports.
for canopy in parking_layout['solar_carports']:
    g=Polygon(canopy['outline']).intersection(land).difference(footprints.buffer(.2))
    for q in polygons(g):
        a,b,c,d=q.bounds;zz=float(raw_ground(q.centroid.x,q.centroid.y))+canopy['eaves_m']
        panel=extrusion(q,zz,.14);panel.vertices[:,2]+=canopy['rise_m']*(panel.vertices[:,1]-b)/max(d-b,1);eg['Solar'].append(panel)
        for xx in np.arange(a+2,c-1,9):
            for yy in [b+1.8,d-1.8]:
                if q.contains(Point(xx,yy)):eg['Frame'].append(cylinder((xx,yy,float(ground(xx,yy))-.2),(xx,yy,zz+.2),.12,6))
        for xx in np.arange(a+1,c,2):
            joint=LineString([(xx,b),(xx,d)]).buffer(.012).intersection(q)
            for part in polygons(joint):eg['Frame'].append(extrusion(part,zz+.145,.012))

# Library entrances and the Mountain courtyard are modeled with the corrected
# building parts; all other public routes retain their mapped plan geometry.
library=next(f for f in buildings if f['id']==291)
library_approach=library_landscape(eg,library['poly'],library['ground'],ground,walkarea,bikearea,footprints)
# Existing mapped trees: public flora inventory is historical, not a live census.
clear=unary_union([footprints.buffer(.7),library_approach.buffer(.5)]);trees=palmtree=0;used=[]
for f in features('icm_14.geojson'):
    q=f['poly'];t=f['properties']
    if q.geom_type!='Point' or not land.contains(q)or clear.contains(q)or lagoon.contains(q):continue
    x,y=q.x,q.y;z=float(ground(x,y));rng=np.random.default_rng(int(t['OBJECTID']));species=((t.get('genus')or'')+' '+(t.get('species')or'')+' '+(t.get('common_nam')or'')).lower()
    if any(a in species for a in ['agave','aloe','opuntia','yucca','furcraea','dasylirion','strelitzia','cordyline']):
        # Succulents and bird-of-paradise records are low plants, not full-size trees.
        h=rng.uniform(1.0,2.6)
        for k in range(7):
            ang=k*math.tau/7;u=np.array([math.cos(ang),math.sin(ang)]);c0=np.array([x,y])+u*h*.35
            m=trimesh.creation.icosphere(subdivisions=0);m.apply_scale([.22,.38,h*.55]);m.apply_transform(trimesh.transformations.rotation_matrix(ang,[0,0,1]));m.apply_translation([*c0,z+h*.55]);eg['Sage'].append(m)
    elif any(a in species for a in ['phoenix','washingtonia','syagrus','palm','butia','jubaea','chamaerops','howea','brahea','trachycarpus']):palms(eg,x,y,z,rng);palmtree+=1;trees+=1
    else:
        tall=any(a in species for a in ['eucalyptus','corymbia']);h=rng.uniform(10,17)if tall else rng.uniform(6,12);r=rng.uniform(2.2,4.0);eg['Trunk'].append(cylinder((x,y,z-1.5),(x,y,z+h*.7),.16,6))
        lobes=[(-.8,0,.58),(.9,.3,.78)]if tall else [(0,0,.68)]
        for dx,dy,zz in lobes:
            m=trimesh.creation.icosphere(subdivisions=1);m.apply_scale([r*.8 if tall else r,r*.72 if tall else r*.9,h*.24 if tall else h*.38]);m.apply_translation([x+dx,y+dy,z+h*zz]);eg['Leaves'].append(m)
            if tall:eg['Trunk'].append(cylinder((x,y,z+h*.48),(x+dx,y+dy,z+h*zz),.09,5))
        trees+=1
# Coastal vegetation clusters are illustrative, deterministic and kept off trails.
rng=np.random.default_rng(611);scrub=habitat.difference(walkarea.buffer(1.5)).difference(bikearea.buffer(1.5)).difference(footprints.buffer(4));shrubs=0
for _ in range(3200):
    x=rng.uniform(-550,600);y=rng.uniform(-1130,-250);q=Point(x,y)
    if not scrub.contains(q):continue
    h=rng.uniform(.4,1.3);m=trimesh.creation.icosphere(subdivisions=0);m.apply_scale([h,h,h*.7]);m.apply_translation([x,y,float(ground(x,y))+h*.5]);eg[['Leaves','Sage','DryGrass'][int(rng.integers(0,3))]].append(m);shrubs+=1
# Campus Point boardwalk: mapped route, raised deck slats and unobtrusive rails.
boardwalks=[]
for f in osm:
    t=f['properties'];g=f['poly']
    if g.geom_type=='LineString'and t.get('highway') in ['path','footway','steps']and g.centroid.y<-600 and g.centroid.x>180:
        boardwalks.append(g)
        env(g.buffer(.9,cap_style=2).intersection(land),.3,.12,'Boardwalk')
        for dist in np.arange(0,g.length,1.2):
            a=g.interpolate(dist);b=g.interpolate(min(g.length,dist+.4));vec=np.array([b.x-a.x,b.y-a.y]);ln=np.linalg.norm(vec)
            if ln<.01:continue
            n=np.array([-vec[1],vec[0]])/ln;zz=float(ground(a.x,a.y))+.44
            eg['Furniture'].append(cylinder((a.x-n[0]*.85,a.y-n[1]*.85,zz),(a.x+n[0]*.85,a.y+n[1]*.85,zz),.022,4))
if boardwalks:place('Campus Point coastal trails','校园岬角滨海步道',unary_union(boardwalks).buffer(2.2).intersection(land))
place('Campus beaches','校园沙滩',beaches)
for k,(mat,parts) in enumerate(eg.items()):
    if parts:chunk_meshes(f'E{k:02d}',parts,mat,'Environment',{'Source':ICM+'; OSM; USGS 3DEP','Approximation':'Vegetation shapes, facade detail, street widths and ocean surface styling are illustrative','Units':'meters'})
print('Landscape:',trees,'mapped trees,',palmtree,'palms,',shrubs,'illustrative coastal shrubs',flush=True)
zone_shapes={z:unary_union([f['poly']for f in buildings if f['zone']==z]).envelope.buffer(20)for z in ['central','west','south','north']}
for name,g in [('Campus',scope),*zone_shapes.items()]:
    aa,bb,cc,dd=g.bounds;xx=(aa+cc)/2;yy=(bb+dd)/2;size=max(cc-aa,dd-bb)*.7;v=rh.ViewInfo();v.Name=name;v.Viewport.SetCameraLocation(rh.Point3d(xx-1200,yy-1700,1700));v.Viewport.SetCameraDirection(rh.Vector3d(1200,1700,-1600));v.Viewport.SetCameraUp(rh.Vector3d(0,0,1));v.Viewport.TargetPoint=rh.Point3d(xx,yy,12);v.Viewport.ChangeToParallelProjection(True);v.Viewport.SetFrustum(-size,size,-size,size,1,40000);model.NamedViews.Add(v)
model.Strings['ModelNotes']='Independent UCSB coastal Main Campus exterior study. Official 2026 footprints, historical public outdoor mapping, OSM shore and paths, USGS terrain. Storke height published; remaining heights and details approximate. One layer per mapped structure; all outdoor and sea geometry on Environment. Not official BIM or a measured survey.'
assert model.Write(str(OUT/'UCSB_MainCampus_Layered.3dm'),7)
def chunk(tag,data=b''):return struct.pack('<HI',tag,len(data)+6)+data
def zs(s):return s.encode('ascii')+b'\0'
def rgb(c):return chunk(0x0011,bytes(c))
mb=b''
for name,co in COLORS.items():mb+=chunk(0xAFFF,chunk(0xA000,zs(name))+chunk(0xA010,rgb(tuple(int(v*.5)for v in co)))+chunk(0xA020,rgb(co))+chunk(0xA030,rgb((10,10,10))))
ob=b''
for o in objects:
    m=o['mesh'];v=np.asarray(m.vertices,dtype='<f4');ff=np.column_stack((m.faces,np.full(len(m.faces),7))).astype('<u2');fc0=struct.pack('<H',len(ff))+ff.tobytes()+chunk(0x4130,zs(o['mat'])+struct.pack('<H',len(ff))+np.arange(len(ff),dtype='<u2').tobytes())+chunk(0x4150,np.zeros(len(ff),dtype='<u4').tobytes());ob+=chunk(0x4000,zs(o['name'])+chunk(0x4100,chunk(0x4110,struct.pack('<H',len(v))+v.tobytes())+chunk(0x4120,fc0)))
(OUT/'UCSB_MainCampus.3ds').write_bytes(chunk(0x4D4D,chunk(0x0002,struct.pack('<I',3))+chunk(0x3D3D,chunk(0x3D3E,struct.pack('<I',3))+chunk(0x0100,struct.pack('<f',1))+mb+ob)))
for name,data in [('layer_map',layer_map),('palette',COLORS),('buildings',records),('viewer_records',records),('places',places)]:
    (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2))
with (OUT/'building_dimensions_and_sources.csv').open('w',encoding='utf-8-sig',newline='')as fd:
    w=csv.DictWriter(fd,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
(OUT/'footprints_local_meters.geojson').write_text(json.dumps({'type':'FeatureCollection','coordinate_system':{'epsg':32611,'origin_easting':OX,'origin_northing':OY,'origin_wgs84':[LON,LAT],'unit':'m','note':'Local projected meters, not RFC7946 lon/lat'},'features':[{'type':'Feature','properties':f['record'],'geometry':mapping(f['poly'])}for f in buildings]},ensure_ascii=False,separators=(',',':')))
samples=[]
for f in buildings:
    for part in polygons(f['poly']):
        q=part.buffer(-.15)
        if q.is_empty:q=part
        if q.geom_type!='Polygon':q=max(q.geoms,key=lambda p:p.area)
        probes=[q.representative_point()]+[q.exterior.interpolate(q.exterior.length*k/6)for k in range(6)]
        for pt in probes:samples.append({'code':f['record']['code'],'name':f['name'],'position':[pt.x,pt.y,f['record']['ground_m']]})
(OUT/'ground_contact_samples.json').write_text(json.dumps(samples,separators=(',',':')))
av=[];af=[];co=[];offset=0
for m,mat in meshdata:av.append(m.vertices);af.append(m.faces+offset);co.extend([COLORS[mat]]*len(m.faces));offset+=len(m.vertices)
np.savez_compressed(OUT/'preview_mesh_data.npz',vertices=np.vstack(av),faces=np.vstack(af),colors=np.asarray(co,dtype=np.uint8))
summary={'buildings':len(records),'layers':len(model.Layers),'environment_layer':'Environment','native_closed_solids':sum(isinstance(o.Geometry,rh.Extrusion)for o in model.Objects),'objects_3ds':len(objects),'vertices':offset,'triangles':sum(len(m.faces)for m,_ in meshdata),'trees':trees,'mapped_flora_positions':sum(1 for f in features('icm_14.geojson')if f['poly'].geom_type=='Point'and land.contains(f['poly'])and not clear.contains(f['poly'])and not lagoon.contains(f['poly'])),'palms':palmtree,'coastal_shrubs':shrubs,'landmarks':sum(r['landmark']for r in records),'unit':'meters','crs':'EPSG:32611 local offsets','origin_wgs84':[LON,LAT],'origin_utm':[OX,OY],'local_z_zero_m':0,'bounds':scope.bounds,'district_bounds':{z:list(g.bounds)for z,g in zone_shapes.items()},'overview_center':[130,-90],'terrain':'USGS 3DEP F32 bare-earth DEM, about 8m sampling; segmented landscape, locally flattened building pads','terrain_source':'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer','sectors':{z:sum(r['zone']==z for r in records)for z in zone_shapes},'accuracy':'Official 2026 building outlines, historical public landscape and flora positions, OSM and USGS DEM. Storke overall height published; remaining heights, components, vegetation sizes, wave styling and width estimates approximate.'}
(OUT/'model_summary.json').write_text(json.dumps(summary,indent=2));(OUT/'excluded_records.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2));print(json.dumps(summary,indent=2),flush=True)
