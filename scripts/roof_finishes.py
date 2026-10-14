"""Explicit nearby roof finishes and satellite-referenced photovoltaic patches.
No imagery is redistributed. Individual panel modules and roof rises are estimates.
"""
from cad_core import *

ROOF_PROFILE={330:'tile',292:'tile',309:'tile',297:'tile',316:'tile',224:'tile',355:'light',280:'pale'}
_layout=json.loads((ROOT/'sources/library_roof_reference.json').read_text())
_to_local=Transformer.from_crs(3857,32611,always_xy=True)

def array_mask(building_id,wing):
    selected=[];e=_layout['extent'];w,h=_layout['width'],_layout['height']
    for row in _layout['arrays']:
        if row['building_id']!=building_id or row['wing']!=wing:continue
        coords=[];dx,dy=row['offset_local_m']
        for x,y in row['pixels']:
            xx=e['xmin']+x/w*(e['xmax']-e['xmin']);yy=e['ymax']-y/h*(e['ymax']-e['ymin']);a,b=_to_local.transform(xx,yy);coords.append((a-OX+dx,b-OY+dy))
        selected.append(Polygon(coords))
    return unary_union(selected)

def solar_arrays(ms,mask,z):
    # Each source patch sets the array extent. A clipped regular module pattern
    # describes the visible solar panels, rather than covering an entire roof.
    panel_count=0
    for q in polygons(mask):
        a,b,c,d=q.bounds
        for x in np.arange(a+.6,c-.4,1.18):
            for y in np.arange(b+.92,d-.7,1.94):
                pane=box(x-.52,y-.85,x+.52,y+.85)
                if q.covers(pane):
                    ms['SolarLibrary'].append(extrusion(pane,z+.10,.11));panel_count+=1
    return panel_count

def flat_finish(ms,p,z,material,edge='RoofLibraryGray'):
    for q in polygons(p):
        for inset in polygons(q.buffer(-.12,join_style=2)):ms[material].append(extrusion(inset,z,.16))
        rim=q.buffer(-.10,join_style=2).difference(q.buffer(-.34,join_style=2))
        for inset in polygons(rim):ms[edge].append(extrusion(inset,z+.17,.20))

def nearby_roof(ms,p,z,building_id):
    style=ROOF_PROFILE.get(building_id)
    if not style:return False
    if style in ['light','pale']:
        flat_finish(ms,p,z,'RoofLibraryLight' if style=='light' else 'RoofPavilion')
        if building_id==355:solar_arrays(ms,array_mask(355,'main').intersection(p.buffer(-.9)),z+.16)
        return True
    # Local wing ranges avoid one huge ridge across a courtyard or T-shaped plan.
    cuts={
      330:[box(20,-40,54,36),box(54,-40,105,-12),box(74,-12,105,35)],
      292:[box(315,-60,352,15),box(352,-34,387,-8),box(387,-45,405,5)],
      309:[box(315,-160,340,-50),box(340,-130,410,-95)],
      297:[box(-25,-180,16,-80),box(16,-115,105,-80),box(65,-160,105,-115),box(16,-180,65,-143)]
    }.get(building_id,[p.envelope])
    used=Polygon()
    for cut in cuts:
        q=p.intersection(cut).difference(used);used=unary_union([used,q])
        for part in polygons(q):
            cc=np.asarray(part.minimum_rotated_rectangle.exterior.coords)[:4];ed=np.roll(cc,-1,axis=0)-cc;u=ed[np.argmax(np.linalg.norm(ed,axis=1))];u/=np.linalg.norm(u);v=np.array([-u[1],u[0]]);c=part.centroid
            loc=affinity.affine_transform(part,[u[0],u[1],v[0],v[1],-c.x*u[0]-c.y*u[1],-c.x*v[0]-c.y*v[1]])
            matrix=np.eye(4);matrix[:2,0]=u;matrix[:2,1]=v;matrix[:2,3]=[c.x,c.y]
            for m in pitched(loc,z,1.0):m.apply_transform(matrix);ms['RoofClay'].append(m)
    # Some auditorium and connector caps are flat, visible in the same image.
    for part in polygons(p.difference(used)):flat_finish(ms,part,z,'RoofLibraryWarm')
    return True
