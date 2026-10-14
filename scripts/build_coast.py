"""Precompute a small signed shoreline distance texture; no browser geometry processing."""
from cad_core import ROOT,TF,OX,OY
import numpy as np,json,base64
from shapely.geometry import shape
from shapely.ops import transform
from shapely import distance,points
from PIL import Image
from coastal_geometry import mapped_shoreline

def pro(x,y,z=None):
 a,b=TF.transform(x,y);return np.asarray(a)-OX,np.asarray(b)-OY
fs=json.loads((ROOT/'sources/icm_30.geojson').read_text())['features'];ocean=transform(pro,shape(next(f['geometry']for f in fs if f['properties']['Name']=='Pacific Ocean')))
bounds=[-4400,-4700,4400,1500];w=h=384;x=np.linspace(bounds[0],bounds[2],w);y=np.linspace(bounds[3],bounds[1],h);xx,yy=np.meshgrid(x,y)
meters=np.clip(distance(points(xx.ravel(),yy.ravel()),mapped_shoreline(ocean)).reshape(h,w)*10,0,65535).astype('uint16');a=np.zeros((h,w,3),dtype='uint8');a[:,:,0]=meters//256;a[:,:,1]=meters%256
im=Image.fromarray(a);im.save(ROOT/'assets/coast-distance.png',optimize=True)
(ROOT/'output/coast_field.json').write_text(json.dumps({'bounds':[bounds[0],bounds[1],bounds[2]-bounds[0],bounds[3]-bounds[1]],'width':w,'height':h,'scale':.1,'encoding':'RG unsigned 16-bit decimeters; north at top PNG row','source':'Historical UCSB mapped land-facing shoreline, excluding three offshore dataset closure edges; visual depth colors, not bathymetry'}))
print('Shoreline texture:',(ROOT/'assets/coast-distance.png').stat().st_size,'bytes')

fs=json.loads((ROOT/'sources/osm_features.geojson').read_text())['features'];lagoon=transform(pro,shape(next(f['geometry']for f in fs if f['properties'].get('name')=='Campus Lagoon')))
bounds=[-410,-900,470,-150];w=h=192;x=np.linspace(bounds[0],bounds[2],w);y=np.linspace(bounds[3],bounds[1],h);xx,yy=np.meshgrid(x,y)
meters=np.clip(distance(points(xx.ravel(),yy.ravel()),lagoon.boundary).reshape(h,w)*10,0,65535).astype('uint16');a=np.zeros((h,w,3),dtype='uint8');a[:,:,0]=meters//256;a[:,:,1]=meters%256
Image.fromarray(a).save(ROOT/'assets/lagoon-distance.png',optimize=True)
(ROOT/'output/lagoon_field.json').write_text(json.dumps({'bounds':[bounds[0],bounds[1],bounds[2]-bounds[0],bounds[3]-bounds[1]],'width':w,'height':h,'scale':.1,'source':'Mapped lagoon perimeter; illustrative shore color, not bathymetry'}))
