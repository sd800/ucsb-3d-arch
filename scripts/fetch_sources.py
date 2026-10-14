from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
import concurrent.futures,datetime,gzip,hashlib,json,sys
R=Path(__file__).resolve().parents[1];S=R/'sources'
bbox='-119.86,34.402,-119.836,34.426'
service='https://services1.arcgis.com/4TXrdeWh0RyCqPgB/ArcGIS/rest/services/Buildings2026/FeatureServer/0'
manifest=[];refresh='--refresh'in sys.argv
def save(name,url,compress=False):
 p=S/name
 if p.exists()and not refresh:raw=p.read_bytes()
 else:
  raw=urlopen(Request(url,headers={'User-Agent':'PublicCampusModel/1.0'}),timeout=90).read()
  if compress:raw=gzip.compress(raw,mtime=0)
  p.write_bytes(raw)
 manifest.append({'file':name,'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()});print(name,len(raw),flush=True)
 return raw
fields='OBJECTID,BUILDINGID,FACILITYKEY,SHORTNAME,LONGNAME,FLOORCOUNT,BLDGAREA,BLDGTYPE,BLDGHEIGHT,BuildingNumber,PF_Zone,Link,Notes'
q={'f':'geojson','where':'1=1','geometry':bbox,'geometryType':'esriGeometryEnvelope','inSR':4326,'outSR':4326,'outFields':fields,'returnGeometry':'true','resultRecordCount':2000}
jobs=[('ucsb_buildings.geojson',service+'/query?'+urlencode(q),False),('building_layer.json',service+'?f=pjson',False)]
for name,box in [('west','-119.86,34.402,-119.848,34.426'),('east','-119.848,34.402,-119.836,34.426')]:jobs.append(('osm_map_'+name+'.xml.gz','https://api.openstreetmap.org/api/0.6/map?bbox='+box,True))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(lambda job:save(*job),jobs))
(S/'retrieval_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
j=json.loads((S/'ucsb_buildings.geojson').read_text());print('buildings',len(j.get('features',[])),j.get('exceededTransferLimit'))
for f in j.get('features',[]):
 t=f['properties'];print(t.get('OBJECTID'),t.get('BUILDINGID'),t.get('LONGNAME'),t.get('FLOORCOUNT'),t.get('BLDGHEIGHT'))
