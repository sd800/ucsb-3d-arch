from cad_core import *
from coastal_geometry import mapped_shoreline,open_sea_domain
from PIL import Image
fs=json.loads((ROOT/'sources/icm_30.geojson').read_text())['features']
def pro(x,y,z=None):
 a,b=TF.transform(x,y);return np.asarray(a)-OX,np.asarray(b)-OY
ocean=transform(pro,shape(next(f['geometry']for f in fs if f['properties']['Name']=='Pacific Ocean')))
shore=mapped_shoreline(ocean);context=open_sea_domain(ocean).intersection(Point(170,-350).buffer(4200,quad_segs=64))
transects=[]
for x in [0,500,1000]:
 ds=[shore.distance(Point(x,y))for y in range(-1200,-4501,-100)]
 assert min(np.diff(ds))>0,'Offshore distance must never reverse at the old crop edge'
 assert all(context.covers(Point(x,y))for y in range(-1200,-4401,-100)if Point(x,y).distance(Point(170,-350))<4199)
 transects.append({'x_m':x,'samples':len(ds),'minimum_increase_m':round(float(min(np.diff(ds))),3),'old_crop_distance_m':round(ocean.boundary.distance(Point(x,-3200)),2),'true_shore_distance_m':round(shore.distance(Point(x,-3200)),2)})
# Pixel decoding must continue to grow across the old offshore crop, with no
# synthetic second nearshore band caused by the rectangular dataset boundary.
a=np.asarray(Image.open(ROOT/'assets/coast-distance.png'),dtype=float);meta=json.loads((OUT/'coast_field.json').read_text());x0,y0,w,h=meta['bounds']
errs=[]
for x in [0,500,1000]:
 for y in range(-1200,-4401,-100):
  col=round((x-x0)/w*(a.shape[1]-1));row=round((1-(y-y0)/h)*(a.shape[0]-1))
  decoded=(a[row,col,0]*256+a[row,col,1])*.1;errs.append(abs(decoded-shore.distance(Point(x,y))))
assert max(errs)<30
report={'mapped_shoreline_length_m':round(shore.length,3),'excluded_offshore_closure_edges':3,'context_radius_m':4200,'surface_and_depth_top_m':.055,'fully_faded_radius_m':3300,'transects':transects,'texture_max_distance_error_m':round(max(errs),3),'passed':True}
(OUT/'ocean_continuity_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
