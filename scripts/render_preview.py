"""Render a lightweight metric massing preview from the exported footprints."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw
from shapely.geometry import shape
r=Path(__file__).resolve().parents[1];out=r/'output'
features=json.loads((out/'footprints_local_meters.geojson').read_text())['features'];s=json.loads((out/'model_summary.json').read_text())
back=np.array([-1.1,-1.2,1.3]);back/=np.linalg.norm(back);right=np.cross([0,0,1],back);right/=np.linalg.norm(right);up=np.cross(back,right)
W,H=2400,1850;center=np.array([*s['overview_center'],50]);scale=.94
im=Image.new('RGB',(W,H),'#e9ece3');d=ImageDraw.Draw(im)
def project(v):
 p=np.asarray(v)-center;return [(float(W/2+q@right*scale),float(H/2-q@up*scale)) for q in p]
order=[]
for f in features:
 b=f['properties'];g=shape(f['geometry']);parts=list(g.geoms) if hasattr(g,'geoms') else [g]
 for p in parts:
  z=b['ground_m'];h=b['height'];cc=list(p.exterior.coords);material='#d8ccb0'
  for aa,bb in zip(cc[:-1],cc[1:]):
   q=np.asarray([[*aa,z],[*bb,z],[*bb,z+h],[*aa,z+h]]);order.append((float(q.mean(axis=0)@back),project(q),material))
  top=np.array([[x,y,z+h] for x,y in cc]);order.append((float(top.mean(axis=0)@back),project(top),'#6d7a80'))
for _,p,c in sorted(order,key=lambda x:x[0]):d.polygon(p,fill=c)
im.save(out/'campus_aerial.png');print('Massing preview generated from exported metric footprints.')
