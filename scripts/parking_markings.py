"""Satellite-referenced parking rows; no automatic array across a lot envelope."""
import math
import numpy as np
from shapely.geometry import LineString,Polygon,Point

def parking_markings(lots,land,footprints,roadarea,layout,clear):
    paint=[];audit=[];by_id={f['properties']['OBJECTID']:f for f in lots}
    for row in layout['rows']:
        source=by_id.get(row['lot_objectid'])
        if not source:continue
        lot=source['poly'].intersection(land).difference(footprints.buffer(.4)).difference(clear).intersection(roadarea)
        if lot.is_empty:continue
        path=LineString(row['path']);count=0;depth=row['depth_m'];spacing=row['spacing_m'];shift=depth/math.tan(math.radians(row['angle_deg']))
        for at in np.arange(.6,path.length-spacing,spacing):
            a=path.interpolate(at);b=path.interpolate(at+spacing);u=np.array([b.x-a.x,b.y-a.y]);ln=np.linalg.norm(u)
            if ln<.5:continue
            u/=ln;n=np.array([-u[1],u[0]])
            for sign in row['sides']:
                back1=np.array([a.x,a.y]);back2=np.array([b.x,b.y]);forward=(n*depth+u*shift)*sign;front1=back1+forward;front2=back2+forward
                bay=Polygon([back1,back2,front2,front1])
                if bay.intersection(lot).area<bay.area*.87:continue
                # A fine continuous back edge and individual dividers, no broad white fills.
                for pts in [[front1,back1,back2],[back2,front2]]:
                    stroke=LineString(pts).buffer(.045,cap_style=2,join_style=2).intersection(lot)
                    if not stroke.is_empty:paint.append(stroke)
                count+=1
        audit.append({'source_objectid':row['lot_objectid'],'row_path':row['path'],'angle_deg':row['angle_deg'],'outlined_bays':count})
    return paint,{'source':'sources/parking_layouts.json','row_paths':len(audit),'line_width_m':.09,'outlined_bays':sum(x['outlined_bays']for x in audit),'rows':audit,'automatic_envelope_grid':False}
