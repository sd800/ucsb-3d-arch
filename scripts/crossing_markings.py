"""Conservative source-driven crossing paint; no inferred parking/street zebra grid."""
import numpy as np
from shapely.geometry import LineString,Polygon

def crossing_markings(features,land,roadarea):
    widths={'primary':14,'secondary':12,'tertiary':9,'residential':6.8,'service':4.6,'unclassified':6.4,'living_street':5}
    streets=[f for f in features if f['properties'].get('highway')in widths and f['poly'].geom_type=='LineString']
    output=[];audit=[]
    for f in features:
        t=f['properties'];q=f['poly']
        if q.geom_type!='Point' or t.get('highway')!='crossing' or not land.contains(q):continue
        style=t.get('crossing:markings');row={'source_id':t.get('osm_id'),'crossing':t.get('crossing'),'markings':style,'painted':False}
        audit.append(row)
        if t.get('crossing')=='unmarked' or style not in ['zebra','ladder','ladder:skewed','zebra:double','lines']:
            row['reason']='Unmarked, non-paint surface treatment, or unspecified paint pattern';continue
        if not streets:row['reason']='No mapped street';continue
        fstreet=min(streets,key=lambda f:f['poly'].distance(q));street=fstreet['poly'];distance=street.distance(q);row['street_distance_m']=round(distance,3)
        # Shared street/crossing nodes are at the centre line. Footpath nodes and
        # markings in parking aisles must not be projected onto a distant road.
        if distance>1.2:row['reason']='Crossing point is not on a mapped vehicular street';continue
        at=street.project(q);a=street.interpolate(max(0,at-1));b=street.interpolate(min(street.length,at+1));u=np.array([b.x-a.x,b.y-a.y]);length=np.linalg.norm(u)
        if length<.05:row['reason']='Degenerate street tangent';continue
        u/=length;n=np.array([-u[1],u[0]]);c=np.array([q.x,q.y]);width=widths[fstreet['properties']['highway']]
        corridor=street.buffer(width/2,cap_style=2).intersection(roadarea)
        paint=[]
        if style=='lines':
            for side in [-1,1]:paint.append(LineString([c+u*side*1.5-n*width/2,c+u*side*1.5+n*width/2]).buffer(.09,cap_style=2).intersection(corridor))
        else:
            for off in np.arange(-width/2+.4,width/2,.8):
                center=c+n*off;paint.append(Polygon([center-u*1.5-n*.21,center+u*1.5-n*.21,center+u*1.5+n*.21,center-u*1.5+n*.21]).intersection(corridor))
        paint=[p for p in paint if not p.is_empty and p.area>.05]
        output.extend(paint);row.update(painted=bool(paint),style='two parallel crossing boundary lines' if style=='lines' else 'zebra',paint_area_m2=round(sum(p.area for p in paint),3))
    return output,{'source':'OSM snapshot; road widths remain approximate','crossings_in_scope':len(audit),'painted_crossings':sum(r['painted']for r in audit),'zebra_crossings':sum(r.get('style')=='zebra' and r['painted']for r in audit),'dense_parking_stripe_grid':False,'records':audit}
