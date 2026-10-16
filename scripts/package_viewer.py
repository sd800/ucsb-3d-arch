"""Build the crawlable root viewer and self-contained offline edition."""
from pathlib import Path
from html import escape
from datetime import datetime
from zoneinfo import ZoneInfo
import json,base64,hashlib,gzip
import numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[1];out=r/'output';assets=r/'assets'
config=json.loads((r/'config/site.config.json').read_text());summary=json.loads((out/'model_summary.json').read_text());records=json.loads((out/'viewer_records.json').read_text());site=config['url']
meta=json.loads((r/'sources/terrain_export_metadata.json').read_text());e=meta['extent'];dem=np.asarray(Image.open(r/'sources/terrain_dem.tif'));ox,oy=summary['origin_utm']
xs=np.linspace(e['xmin'],e['xmax'],dem.shape[1],endpoint=False)+(e['xmax']-e['xmin'])/dem.shape[1]/2-ox;ys=np.linspace(e['ymin'],e['ymax'],dem.shape[0],endpoint=False)+(e['ymax']-e['ymin'])/dem.shape[0]/2-oy
xi=list(range(0,len(xs),3));yi=list(range(0,len(ys),3));xi.append(len(xs)-1);yi.append(len(ys)-1)
grid={'x':[round(float(xs[i]),2) for i in xi],'y':[round(float(ys[i]),2) for i in yi],'heights':np.round(dem[::-1][np.ix_(yi,xi)],2).tolist()}
model=(out/'UCSB_MainCampus.3ds').read_bytes();from web_model_package import web_payload
web,compressed=web_payload(r,model)
encoded=base64.b64encode(compressed).decode();preview=base64.b64encode((out/'campus_aerial.png').read_bytes()).decode()
preview_width,preview_height=Image.open(out/'campus_aerial.png').size
order=[b['facility_id'] for b in records if b['landmark']]
from curation import LANDMARKS
order=[id for id in LANDMARKS if id in order]
b=summary['bounds'];data={**web,'landBoundary':json.loads((out/'land_boundary.json').read_text()),'groundPads':[{'code':f['properties']['code'],'height':f['properties']['ground_m'],'bounds':[min(x for ring in ([f['geometry']['coordinates']]if f['geometry']['type']=='Polygon'else f['geometry']['coordinates'])for points in ring for x,y in points),min(y for ring in ([f['geometry']['coordinates']]if f['geometry']['type']=='Polygon'else f['geometry']['coordinates'])for points in ring for x,y in points),max(x for ring in ([f['geometry']['coordinates']]if f['geometry']['type']=='Polygon'else f['geometry']['coordinates'])for points in ring for x,y in points),max(y for ring in ([f['geometry']['coordinates']]if f['geometry']['type']=='Polygon'else f['geometry']['coordinates'])for points in ring for x,y in points)],'geometry':f['geometry']}for f in json.loads((out/'footprints_local_meters.geojson').read_text())['features']],'coastField':{**json.loads((out/'coast_field.json').read_text()),'image':'data:image/png;base64,'+base64.b64encode((assets/'coast-distance.png').read_bytes()).decode()},'lagoonField':{**json.loads((out/'lagoon_field.json').read_text()),'image':'data:image/png;base64,'+base64.b64encode((assets/'lagoon-distance.png').read_bytes()).decode()},'overviewCenter':summary['overview_center'],'groundGrid':grid,'modelByteLength':len(model),'modelTransferBytes':len(compressed),'modelGlobal':'__UCSB_MODEL_BASE64__','downloadUrl':'output/UCSB_MainCampus.3ds','compression':'gzip','offlineModelScript':'assets/model-local.js','layers':json.loads((out/'layer_map.json').read_text()),'palette':json.loads((out/'palette.json').read_text()),'records':records,'preview':'output/campus_aerial.png','seo':{'en':{k:config[k] for k in ['title','description','imageAlt']},'zh':config['zh']},'landmarkOrder':order,'districtBounds':{**summary['district_bounds'],'core':[-500,-600,760,460],'south':[-550,-1130,600,-240],'north':[-710,390,500,1130],'overview':[-720,-1150,1070,1150]},'siteCenter':[(b[0]+b[2])/2,(b[1]+b[3])/2],'places':json.loads((out/'places.json').read_text())}
# Expanded context terrain is resampled once at build time; client lookup stays
# a small bilinear grid, with exact level pads for all selectable buildings.
from scipy.interpolate import RegularGridInterpolator
nm=json.loads((r/'sources/neighbor_terrain_metadata.json').read_text())['extent'];nd=np.asarray(Image.open(r/'sources/neighbor_terrain_dem.tif'),dtype=float)
nx=np.linspace(nm['xmin'],nm['xmax'],nd.shape[1],endpoint=False)+(nm['xmax']-nm['xmin'])/nd.shape[1]/2-ox
ny=np.linspace(nm['ymin'],nm['ymax'],nd.shape[0],endpoint=False)+(nm['ymax']-nm['ymin'])/nd.shape[0]/2-oy
xx=nx[::3];yy=ny[::3];gz=np.maximum(.18,nd[::-1][::3,::3]);gx,gy=np.meshgrid(xx,yy)
original=RegularGridInterpolator((ys,xs),dem[::-1],bounds_error=False,fill_value=None)
inside=(gx>=xs[0])&(gx<=xs[-1])&(gy>=ys[0])&(gy<=ys[-1]);gz[inside]=original(np.column_stack([gy[inside],gx[inside]]))
data['neighborGrid']={'x':np.round(xx,2).tolist(),'y':np.round(yy,2).tolist(),'heights':np.round(gz,2).tolist()}
data['neighbors']=json.loads((out/'neighboring_records.json').read_text());data['neighborBounds']=summary['neighbor_bounds'];data['neighborPads']=json.loads((out/'neighboring_pads.json').read_text());data['places']+=json.loads((out/'neighboring_places.json').read_text())
data['districtBounds']['overview']=summary.get('campus_display_bounds',data['districtBounds']['overview'])
data['regions']=json.loads((assets/'stream/manifest.json').read_text());data['campusModel']=data['regions']['campusModel'];assert data['regions']['sourceSha256']==hashlib.sha256(model).hexdigest()
# Keep the original full-campus CAD download separate from browsing derivatives.
archive=gzip.compress(model,compresslevel=6,mtime=0);(out/'UCSB_MainCampus.3ds.gz').write_bytes(archive);data['downloadArchiveUrl']='output/UCSB_MainCampus.3ds.gz'
date=datetime.now(ZoneInfo('America/Chicago')).date().isoformat()
schema={'@context':'https://schema.org','@graph':[{'@type':'WebSite','@id':site+'#website','url':site,'name':'UC Santa Barbara Campus 3D Model','inLanguage':['en','zh-CN'],'sameAs':config['repository'],'image':site+'assets/brand/ucsb-map.png'},{'@type':'WebPage','@id':site+'#webpage','url':site,'name':config['title'],'description':config['description'],'inLanguage':['en','zh-CN'],'isPartOf':{'@id':site+'#website'},'mainEntity':{'@id':site+'#model'},'dateModified':date,'primaryImageOfPage':{'@type':'ImageObject','url':site+'output/campus_aerial.png','width':preview_width,'height':preview_height}},{'@type':'3DModel','@id':site+'#model','name':'University of California, Santa Barbara exterior campus model','description':f"Independent public-source exterior model with {len(records)} building layers, {len(data['neighbors'])} neighboring building layers, separate campus/context environment layers, historical public flora positions and sampled USGS terrain. Exterior heights and geometry are approximate, not a measured as-built survey.",'contentUrl':site+'output/UCSB_MainCampus.3ds','encodingFormat':'application/x-3ds','contentSize':str(len(model))+' bytes','sha256':hashlib.sha256(model).hexdigest(),'thumbnailUrl':site+'output/campus_aerial.png','contentLocation':{'@type':'Place','name':'University of California, Santa Barbara campus','address':{'@type':'PostalAddress','addressLocality':'Santa Barbara','addressRegion':'CA','addressCountry':'US'}},'isBasedOn':['https://map.ucsb.edu/','https://www.dfss.ucsb.edu/design-construction-services/maps','https://www.openstreetmap.org/','https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer']}]}
def jsjson(v):return json.dumps(v,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')
template=(r/'scripts/viewer.template.html').read_text();bundle=(r/'tmp/viewer.bundle.js').read_text()
rows=''.join(f'<div class="row"><span class="building-name" data-building-name="{escape(b["code"])}">{escape(b["name"])}</span><span class="building-meta">{escape(b["name_zh"])} · {b["code"]}</span></div>' for b in records)
for token,value in {'__SITE_URL__':site,'__SEO_TITLE__':escape(config['title'],quote=True),'__SEO_DESCRIPTION__':escape(config['description'],quote=True),'__IMAGE_ALT__':escape(config['imageAlt'],quote=True),'__STRUCTURED_DATA__':jsjson(schema),'__INITIAL_BUILDINGS__':rows,'__INITIAL_COUNT__':str(len(records)),'__PREVIEW_WIDTH__':str(preview_width),'__PREVIEW_HEIGHT__':str(preview_height)}.items():template=template.replace(token,value)
license=((r/'docs/THIRD_PARTY_NOTICES.md').read_text()+'\n'+(assets/'fonts/OFL.txt').read_text()).replace('--','- -');template=template.replace('</head>','<!--\n'+license+'\n-->\n</head>')
def edition(payload,font,preview,icons,logo,script,robots,rhino):
    html=template
    for token,value in {'__CAMPUS_DATA__':jsjson(payload),'__TITLE_FONT_URL__':font,'__PREVIEW_IMAGE__':preview,'__FAVICON__':icons['32'],'__FAVICON_16__':icons['16'],'__APPLE_ICON__':icons['apple'],'__LOGO__':logo,'__VIEWER_SCRIPT__':script,'__ROBOTS__':robots,'__RHINO_URL__':rhino}.items():html=html.replace(token,value)
    assert not any(t in html for t in ['__CAMPUS_DATA__','__TITLE_FONT_URL__','__PREVIEW_IMAGE__','__FAVICON__','__APPLE_ICON__','__LOGO__','__VIEWER_SCRIPT__','__ROBOTS__','__RHINO_URL__']);return html
(assets/'viewer.bundle.js').write_text(bundle);(assets/'model-local.js').write_text('window.__UCSB_MODEL_BASE64__='+json.dumps(encoded)+';\n')
html=edition(data,'assets/fonts/Manrope.ttf','output/campus_aerial.png',{'32':'assets/favicon-32.png','16':'assets/favicon-16.png','apple':'assets/apple-touch-icon.png'},'assets/brand/ucsb-map-192.png','<script defer src="assets/viewer.bundle.js?v='+hashlib.sha256(bundle.encode()).hexdigest()[:12]+'"></script>','index, follow, max-image-preview:large','output/UCSB_MainCampus_Layered.3dm');(r/'index.html').write_text(html)
def png(path):return 'data:image/png;base64,'+base64.b64encode((assets/path).read_bytes()).decode()
inline_regions={a['id']:base64.b64encode((r/a['url']).read_bytes()).decode()for a in [data['regions']['base'],*data['regions']['tiles']]}
core_encoded=base64.b64encode((r/data['campusModel']['modelUrl']).read_bytes()).decode()
offline=edition({**data,'inlineRegions':inline_regions,'campusModel':{**data['campusModel'],'model':core_encoded},'downloadArchiveUrl':'UCSB_MainCampus.3ds.gz','preview':'data:image/png;base64,'+preview},'data:font/ttf;base64,'+base64.b64encode((assets/'fonts/Manrope.ttf').read_bytes()).decode(),'data:image/png;base64,'+preview,{'32':png('favicon-32.png'),'16':png('favicon-16.png'),'apple':png('apple-touch-icon.png')},png('brand/ucsb-map-192.png'),'<script>'+bundle.replace('</script',r'<\/script')+'</script>','noindex, follow','UCSB_MainCampus_Layered.3dm');(out/'UCSB_Campus_Offline.html').write_text(offline)
(r/'CNAME').write_text(config['domain']+'\n');(r/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+site+'sitemap.xml\n');(r/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+site+'</loc><lastmod>'+date+'</lastmod></url></urlset>\n')
print('Viewer:',len(html.encode()),'bytes; offline:',len(offline.encode()),'bytes; buildings:',len(records))
