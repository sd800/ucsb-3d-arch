"""Evidence-based display scope; geographic proximity does not define UCSB membership.
Official GIS matches and explicitly verified university facilities/housing only.
OSM building=university, a student tenant or a UCSB email alone are insufficient.
"""
from cad_core import *
from shapely.strtree import STRtree

HOUSING='https://tap.ucsb.edu/parking-permits/student/university-owned-apartments-epermits'
GIS='https://services1.arcgis.com/4TXrdeWh0RyCqPgB/ArcGIS/rest/services/Buildings2026/FeatureServer/0'
AREA_RULES={
 'way/560598080':('West Campus Apartments',HOUSING),
 'way/651062330':('West Campus Point Faculty Housing','https://www.housing.ucsb.edu/housing-options/options-filter/west-campus-point'),
 'way/38269376':('Santa Ynez Apartments',HOUSING),
 'way/38269385':('Storke Family Student Housing',HOUSING),
 'way/42751740':('San Clemente Apartments',HOUSING),
 'way/581720398':('San Joaquin North Villages',HOUSING),
 'way/581720399':('San Joaquin Tower Villages',HOUSING),
}
BUILDING_RULES={
 'way/38171414':('Embarcadero Hall','https://aait.ucsb.edu/event-av-services/embarcadero-hall'),
 'way/38171690':('Isla Vista Theater','https://aait.ucsb.edu/event-av-services/isla-vista-theaters'),
 'way/42754953':('Pardall Center','https://pardallcenter.as.ucsb.edu/about/history/'),
 'relation/7893890':('El Dorado Apartments',HOUSING),
 'relation/8082670':('Tropicana Villas','https://news.ucsb.edu/2015/015764/tropicana-be-integrated-university-student-housing'),
 'way/539936496':('Portola Dining Commons','https://dining.ucsb.edu/dining-commons/portola-dining-commons'),
 'way/49745346':("Orfalea Family Children's Center",'https://childrenscenter.sa.ucsb.edu/programs-curriculum/ofcc'),
 'way/49745343':("Orfalea Family Children's Center — 353",'https://childrenscenter.sa.ucsb.edu/programs-curriculum/ofcc'),
 'way/49745347':("Orfalea Family Children's Center — 354",'https://childrenscenter.sa.ucsb.edu/programs-curriculum/ofcc'),
 'way/49745354':("Orfalea Family Children's Center — 352",'https://childrenscenter.sa.ucsb.edu/programs-curriculum/ofcc'),
 'way/218666033':('West Campus Conference Center','https://conferences.ucsb.edu/accommodations/visitors/overview'),
}

def classify_campus(osm,accepted):
    def project(x,y,z=None):
        a,b=TF.transform(x,y);return np.asarray(a)-OX,np.asarray(b)-OY
    official=json.loads((ROOT/'sources/ucsb_buildings.geojson').read_text())['features']
    official_polys=[transform(project,shape(f['geometry']))for f in official];tree=STRtree(official_polys)
    areas=[(f['poly'],*AREA_RULES[f['properties']['osm_id']])for f in osm if f['properties'].get('osm_id')in AREA_RULES]
    kept=[];site_polys=[];audit=[]
    for f in accepted:
        p=f['poly'];id=f['properties']['osm_id'];rule=BUILDING_RULES.get(id);kind='verified-facility';official_id=None
        matches=[int(i)for i in tree.query(p)if p.intersection(official_polys[i]).area/p.area>=.65]
        if rule is None and matches:
            i=max(matches,key=lambda i:p.intersection(official_polys[i]).area);t=official[i]['properties'];official_id=int(t['OBJECTID']);rule=((t.get('LONGNAME')or f['properties'].get('name')or 'UCSB facility '+str(official_id)).strip(),GIS);kind='official-campus-footprint'
        if rule is None:
            for area,name,url in areas:
                if area.covers(p.representative_point())and p.intersection(area).area/p.area>.80:
                    rule=(name,url);kind='verified-university-housing';break
        f['campus_affiliation']=None if rule is None else {'site':rule[0],'source':rule[1],'basis':kind,'official_gis_id':official_id}
        if rule:
            kept.append(f);site_polys.append(p.buffer(10,join_style=2));audit.append({'osm_id':id,'original_name':f['properties'].get('name'),'site':rule[0],'source':rule[1],'basis':kind,'official_gis_id':official_id})
    # Whole mapped university housing grounds are retained, but only within the
    # existing modeled extent. These are display grounds, not legal parcel lines.
    for area,name,url in areas:
        if any(area.covers(f['poly'].representative_point())for f in kept):site_polys.append(area)
    # Preserve the campus parking/entrance apron where a verified campus lot
    # adjoins a retained facility. Do not absorb an entire public street block.
    official_parking=json.loads((ROOT/'sources/icm_2.geojson').read_text())['features'];campus_foot=unary_union([f['poly']for f in kept])
    for f in official_parking:
        if not f.get('geometry'):continue
        p=transform(project,shape(f['geometry']))
        if p.area<15000 and p.distance(campus_foot)<8:site_polys.append(p.buffer(.5))
    sites=unary_union(site_polys).buffer(0)
    (OUT/'campus_affiliation_audit.json').write_text(json.dumps({'rule':'Official UCSB building-footprint overlap, or a verified university facility/housing area. No inference from student occupancy, OSM building=university or email domain alone.','review_date':'2026-10-15','buildings':audit},ensure_ascii=False,indent=2)+'\n')
    return sites
