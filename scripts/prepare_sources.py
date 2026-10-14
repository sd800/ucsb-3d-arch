"""Normalize the two public OSM map extracts without modifying source positions."""
from pathlib import Path
import json,xml.etree.ElementTree as ET,gzip
from shapely.geometry import Point,LineString,Polygon,box,mapping
from shapely.ops import polygonize,unary_union
r=Path(__file__).resolve().parents[1];s=r/'sources';nodes={};node_elements={};ways={};relations={}
inputs=list(s.glob('osm_map_*.xml')) or list(s.glob('osm_map_*.xml.gz'))
for p in inputs:
    raw=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
    root=ET.fromstring(raw)
    for n in root.findall('node'):
        nodes[n.attrib['id']]=(float(n.attrib['lon']),float(n.attrib['lat']));node_elements[n.attrib['id']]=n
    for w in root.findall('way'):ways[w.attrib['id']]=w
    for rel in root.findall('relation'):relations[rel.attrib['id']]=rel
    if p.suffix!='.gz':(s/(p.name+'.gz')).write_bytes(gzip.compress(raw,mtime=0))
area=box(-119.86,34.402,-119.836,34.426);features=[];geoms={}
def tags(e):return {t.attrib['k']:t.attrib['v'] for t in e.findall('tag')}
def relevant(t):return bool(set(t)&{'building','building:part','highway','landuse','leisure','natural','water','man_made'}) or t.get('amenity') in {'fountain','parking','university'}
for id,w in ways.items():
    t=tags(w);ids=[n.attrib['ref'] for n in w.findall('nd')]
    if not all(i in nodes for i in ids) or len(ids)<2:continue
    cc=[nodes[i] for i in ids];closed=ids[0]==ids[-1] and len(ids)>3
    line=LineString(cc);geoms[id]=line
    if not relevant(t):continue
    g=Polygon(cc).buffer(0) if closed and ('building' in t or 'building:part' in t or t.get('area')=='yes' or set(t)&{'landuse','leisure','natural','water'} or t.get('amenity') in {'university','fountain','parking'}) else line
    if g.is_empty or not g.intersects(area):continue
    features.append({'type':'Feature','properties':{'osm_id':'way/'+id,**t},'geometry':mapping(g)})
for id,e in relations.items():
    t=tags(e)
    if t.get('type')!='multipolygon' or not relevant(t):continue
    outer=[geoms[m.attrib['ref']] for m in e.findall('member') if m.attrib['type']=='way' and m.attrib.get('role','outer') in ['','outer'] and m.attrib['ref'] in geoms]
    inner=[geoms[m.attrib['ref']] for m in e.findall('member') if m.attrib['type']=='way' and m.attrib.get('role')=='inner' and m.attrib['ref'] in geoms]
    if not outer:continue
    g=unary_union(list(polygonize(unary_union(outer)))).difference(unary_union(list(polygonize(unary_union(inner)))))
    if g.is_empty or not g.intersects(area):continue
    features.append({'type':'Feature','properties':{'osm_id':'relation/'+id,**t},'geometry':mapping(g)})
for id,n in node_elements.items():
    t=tags(n)
    if t.get('highway')=='crossing' or t.get('natural')=='tree' or t.get('amenity') in ['bench','fountain'] or t.get('tourism')=='artwork':
        features.append({'type':'Feature','properties':{'osm_id':'node/'+id,**t},'geometry':mapping(Point(nodes[id]))})
(s/'osm_features.geojson').write_text(json.dumps({'type':'FeatureCollection','source':'© OpenStreetMap contributors, ODbL 1.0; API snapshot 2026-10-13','features':features},ensure_ascii=False,separators=(',',':')))
print('Normalized',len(features),'features')
