"""Fetch paginated public campus outdoor mapping, retaining snapshots by default."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
import json,datetime,hashlib,concurrent.futures,sys
r=Path(__file__).resolve().parents[1];s=r/'sources';refresh='--refresh'in sys.argv
base='https://services1.arcgis.com/4TXrdeWh0RyCqPgB/ArcGIS/rest/services/ucsb_icm.gdb/FeatureServer/'
ids=[2,5,7,11,14,18,20,21,22,23,24,25,30]
def fetch(id):
 p=s/f'icm_{id}.geojson';fs=[];url=base+str(id)+'/query'
 if p.exists()and not refresh:fs=json.loads(p.read_text())['features']
 else:
  for offset in range(0,30000,1000):
   q={'f':'geojson','where':'1=1','outFields':'*','outSR':4326,'returnGeometry':'true','resultOffset':offset,'resultRecordCount':1000}
   d=json.load(urlopen(url+'?'+urlencode(q),timeout=75));assert not d.get('error'),d
   batch=d.get('features',[])
   for f in batch:f['properties']={k:v for k,v in f['properties'].items()if not any(w in k.lower()for w in ['creat','edit','user','editor','photo','email'])}
   fs+=batch
   if len(batch)<1000:break
  p.write_text(json.dumps({'type':'FeatureCollection','features':fs},separators=(',',':')))
 raw=p.read_bytes();return {'file':p.name,'url':base+str(id),'features':len(fs),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'retained_snapshot':not refresh,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
rs=list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(fetch,ids));(s/'landscape_manifest.json').write_text(json.dumps(rs,indent=2)+'\n')
for r in rs:print(r['file'],r['features'])
