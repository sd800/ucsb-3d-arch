"""Original navy/gold coastal-campus icon; not an official university signature."""
from pathlib import Path
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[1];a=r/'assets';(a/'brand').mkdir(exist_ok=True)
navy='#003660';gold='#febc11';pale='#f4ebcb'
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><title>UCSB campus model: tower, palm and Pacific coast</title><rect width="512" height="512" rx="78" fill="{navy}"/><path d="M129 303V99H153V303M205 303V99H229V303M129 101H229M129 155H229M129 194H229" fill="none" stroke="{gold}" stroke-width="15"/><circle cx="179" cy="222" r="24" fill="{pale}"/><path d="M179 208V223L190 231M348 300C352 242 351 197 345 161M345 164Q310 104 270 151M345 164Q349 101 394 126M345 164Q402 143 424 186M345 164Q309 139 291 191M345 164Q372 185 387 214" fill="none" stroke="{gold}" stroke-width="13" stroke-linecap="round"/><path d="M88 330Q172 311 256 340T424 330M88 373Q172 354 256 383T424 373M110 416Q183 399 256 425T402 416" fill="none" stroke="{pale}" stroke-width="14" stroke-linecap="round"/></svg>'''
(a/'brand/ucsb-map.svg').write_text(svg+'\n');im=Image.new('RGBA',(2048,2048));d=ImageDraw.Draw(im);sc=4
box=lambda v:tuple(int(x*sc)for x in v)
def line(p,color,width=14):d.line([(int(x*sc),int(y*sc))for x,y in p],fill=color,width=width*sc,joint='curve')
d.rounded_rectangle((0,0,2047,2047),radius=78*sc,fill=navy)
for p in [[(129,303),(129,99)],[(153,303),(153,99)],[(205,303),(205,99)],[(229,303),(229,99)],[(129,101),(229,101)],[(129,155),(229,155)],[(129,194),(229,194)]]:line(p,gold,12)
d.ellipse(box((155,198,203,246)),fill=pale);line([(179,208),(179,223),(190,231)],navy,5)
for p in [[(348,300),(351,230),(345,164)],[(345,164),(325,130),(298,129),(270,151)],[(345,164),(355,124),(375,117),(394,126)],[(345,164),(384,152),(408,166),(424,186)],[(345,164),(315,158),(291,191)],[(345,164),(370,183),(387,214)]]:line(p,gold,12)
import math
for y,x0,x1 in [(330,88,424),(373,88,424),(416,110,402)]:line([(x,y-13*math.sin((x-x0)/(x1-x0)*math.tau))for x in range(x0,x1+1)],pale,13)
for size,file in [(1024,'brand/ucsb-map.png'),(192,'brand/ucsb-map-192.png'),(180,'apple-touch-icon.png'),(32,'favicon-32.png'),(16,'favicon-16.png')]:im.resize((size,size),Image.Resampling.LANCZOS).save(a/file)
im.resize((256,256),Image.Resampling.LANCZOS).save(r/'favicon.ico',sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
(a/'brand/README.md').write_text('Original independent project icon: Storke-inspired tower, palm and Pacific waves in UCSB-inspired navy and gold. Not the university seal or an official signature. SVG source is editable.\n')
