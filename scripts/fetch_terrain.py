"""Export meter-valued bare-earth USGS DEM to the model's projected CRS."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
import json,hashlib
from pyproj import Transformer
r=Path(__file__).resolve().parents[1];s=r/'sources'
service='https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer'
t=Transformer.from_crs(4326,32611,always_xy=True)
a,b=t.transform(-119.86,34.402);c,d=t.transform(-119.836,34.426)
p={'f':'json','bbox':','.join(map(str,[a,b,c,d])),'bboxSR':32611,'imageSR':32611,'size':'300,300','format':'tiff','pixelType':'F32','interpolation':'RSP_BilinearInterpolation','noDataInterpretation':'esriNoDataMatchAny','adjustAspectRatio':'false'}
u=service+'/exportImage?'+urlencode(p);raw=urlopen(u,timeout=90).read();j=json.loads(raw);assert 'href' in j,j
(s/'terrain_export_metadata.json').write_bytes(raw);data=urlopen(j['href'],timeout=90).read();(s/'terrain_dem.tif').write_bytes(data)
(s/'terrain_source.json').write_text(json.dumps({'service':service,'export_parameters':p,'raster_sha256':hashlib.sha256(data).hexdigest(),'height_datum':'USGS 3DEP service elevations in meters; no survey certification','local_z_zero_m':0},indent=2))
print('DEM',j['width'],j['height'],len(data),j['extent'])
