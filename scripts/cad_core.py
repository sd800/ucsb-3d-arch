"""UCSB exterior campus model: public GIS, USGS terrain, explicit height certainty."""
import pathlib, json, math, csv, struct, xml.etree.ElementTree as ET
import numpy as np
import trimesh
import rhino3dm as rh
from shapely.geometry import Polygon, MultiPolygon, Point, LineString, box, shape, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union, transform
from shapely import affinity, set_precision, constrained_delaunay_triangles
from pyproj import Transformer

ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
TF=Transformer.from_crs(4326,32611,always_xy=True)
LON,LAT=-119.8476,34.4135;OX,OY=TF.transform(LON,LAT)
COLORS={
 'ContextGround':(155,155,130),'ContextRoad':(88,91,92),'ContextWalk':(181,177,160),'ContextPaving':(176,166,143),'ContextGrass':(126,148,104),'ContextLeaves':(82,117,80),'ContextStucco':(197,186,158),'ContextStone':(183,180,160),'ContextBrick':(147,109,85),'ContextRoof':(132,137,128),'ContextTile':(151,111,83),'ContextGlass':(103,139,147),
 'WetSand':(177,157,113),
 'RoofLibraryGray':(123,130,126),'RoofLibraryWarm':(172,164,142),'RoofLibraryLight':(180,178,162),
 'RoofClay':(151,106,83),'RoofBallast':(149,135,120),'RoofGlass':(93,124,133),'SolarLibrary':(46,52,55),
 'RoofPavilion':(184,188,184),'ConcreteBlock':(178,170,156),
 'Earth':(166,150,113),'OceanDepth':(72,127,151),'LagoonDepth':(67,108,103),
 'Cycleway':(124,137,131),'Ocean':(76,139,165),'CoastalWater':(84,149,170),'ShallowWater':(97,158,174),'Foundation':(196,188,166),'Bank':(137,145,108),'Sage':(135,153,107),'DryGrass':(175,164,115),'Bluff':(185,166,129),'Boardwalk':(155,135,101),'Limestone':(216,204,176),'LightStone':(233,222,196),'Brick':(144,86,67),
 'Slate':(71,75,79),'Tile':(161,84,53),'Concrete':(197,198,193),'WhitePanel':(225,226,219),
 'Metal':(113,124,128),'Glass':(113,157,174),'DarkGlass':(59,83,91),'Frame':(64,65,64),
 'Ground':(155,157,127),'Road':(81,86,89),'Paving':(178,165,140),'Walk':(183,180,161),
 'Grass':(116,149,96),'Garden':(93,127,83),'Water':(86,142,146),'Track':(159,83,62),
 'Court':(89,132,122),'Marking':(232,228,207),'Leaves':(67,116,75),'Trunk':(119,95,68),
 'Furniture':(72,78,72),'Solar':(50,73,88),'Purple':(0,54,96),'Gold':(254,188,17),'Blossom':(225,172,185),'Sand':(201,182,138),'Seat':(197,199,194),'BrickPath':(166,120,94),'BrickPale':(150,78,56),'BrickWarm':(143,69,50),'BrickBand':(119,60,48),'StepStone':(182,175,157),'StoneEdge':(191,186,171),'StoneJoint':(141,143,136),'Corten':(117,63,43),'Spray':(194,221,225),'PoolWater':(65,123,145),'Foam':(228,239,235),'Ripple':(114,166,180),'BlossomPale':(237,198,208),
}
model=rh.File3dm();model.ApplicationName='University of California, Santa Barbara Public-source Exterior Model'
model.Settings.ModelUnitSystem=rh.UnitSystem.Meters;model.Settings.ModelAbsoluteTolerance=.01
model.Settings.ModelAngleToleranceDegrees=1
anchor=model.Settings.EarthAnchorPoint;anchor.Name='Santa Barbara campus local origin / WGS84'
anchor.EarthBasepointLatitude=LAT;anchor.EarthBasepointLongitude=LON
anchor.ModelBasePoint=rh.Point3d(0,0,0);anchor.ModelNorth=rh.Vector3d(0,1,0);anchor.ModelEast=rh.Vector3d(1,0,0)
model.Settings.EarthAnchorPoint=anchor
mats={};layers={};objects=[];meshdata=[];layer_map={};records=[];native_count=0
for name,c in COLORS.items():
    m=rh.Material();m.Name=name;m.DiffuseColor=(*c,255);m.Shine=0
    if name=='Glass':m.Transparency=.12
    mats[name]=model.Materials.Add(m)
def layer(name,mat):
    r=rh.Layer();r.Name=name;r.Color=(*COLORS[mat],255);layers[name]=model.Layers.Add(r);return layers[name]
layer('Environment','Grass')
def polygons(g):
    if g.is_empty:return []
    if isinstance(g,Polygon):
        g=set_precision(g.buffer(0),.005).simplify(.002,preserve_topology=True).buffer(0)
        if not isinstance(g,Polygon):return polygons(g)
        g=Polygon(g.exterior,[ring for ring in g.interiors if Polygon(ring).area>.04])
        return [orient(g,1)] if g.area>.025 else []
    if hasattr(g,'geoms'):return [p for a in g.geoms for p in polygons(a)]
    return []
def attr(name,lay,mat,info=None):
    a=rh.ObjectAttributes();a.Name=name;a.LayerIndex=layers[lay];a.MaterialIndex=mats[mat]
    a.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;a.ColorSource=rh.ObjectColorSource.ColorFromObject;a.ObjectColor=(*COLORS[mat],255)
    for k,v in (info or {}).items():a.SetUserString(k,str(v))
    return a
def rhmesh(m):
    r=rh.Mesh()
    for v in m.vertices:r.Vertices.Add(*map(float,v))
    for f in m.faces:r.Faces.AddFace(*map(int,f))
    r.Normals.ComputeNormals();r.Compact();assert r.IsValid
    return r
def extrusion(p,z,h):
    triangles=constrained_delaunay_triangles(p)
    vertices=[];faces=[];index={}
    for tri in triangles.geoms:
        face=[]
        for xy in list(tri.exterior.coords)[:3]:
            if xy not in index:index[xy]=len(vertices);vertices.append(xy)
            face.append(index[xy])
        faces.append(face)
    m=trimesh.creation.extrude_triangulation(np.asarray(vertices),np.asarray(faces),float(h));m.apply_translation([0,0,z])
    m.merge_vertices(digits_vertex=7);m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m,multibody=True)
    if not (m.is_watertight and m.is_winding_consistent):
        # Public GIS overlays may contain near-coincident edges. Try an
        # independent triangulator, then small topology regularization of touching boundaries.
        for delta in [0,.003,-.003,.008,-.008,.015,-.015,.03,-.03]:
            q=p if not delta else p.buffer(delta,join_style=2).buffer(-delta,join_style=2)
            parts=[trimesh.creation.extrude_polygon(a,float(h),engine='earcut') for a in polygons(q)]
            if not parts:continue
            candidate=trimesh.util.concatenate(parts);candidate.apply_translation([0,0,z]);trimesh.repair.fix_normals(candidate,multibody=True)
            if candidate.is_watertight and candidate.is_winding_consistent:
                m=candidate;break
    if not (m.is_watertight and m.is_winding_consistent):
        # Valid GIS polygons with point-touching holes extrude to a
        # non-manifold shell. Closed triangular cells preserve their volume.
        cells=[]
        for tri in constrained_delaunay_triangles(p).geoms:
            if tri.area<1e-10:continue
            coords=np.asarray(tri.exterior.coords)[:3]
            cell=trimesh.creation.extrude_triangulation(coords,np.array([[0,1,2]]),float(h));cell.apply_translation([0,0,z]);cells.append(cell)
        m=trimesh.util.concatenate(cells);trimesh.repair.fix_normals(m,multibody=True)
    assert m.is_watertight and m.is_winding_consistent,(p.bounds,h)
    return m
def boxmesh(x,y,z,sx,sy,sz):
    m=trimesh.creation.box(extents=(sx,sy,sz));m.apply_translation((x,y,z+sz/2));return m
def cylinder(a,b,r=.1,sections=8):
    return trimesh.creation.cylinder(radius=r,segment=np.asarray([a,b]),sections=sections)
def native_extrude(p,z,h,name,lay,mat,info):
    global native_count
    c=rh.PolylineCurve([rh.Point3d(float(x),float(y),float(z)) for x,y in p.exterior.coords]);e=rh.Extrusion.Create(c,float(h),True)
    for ring in p.interiors:e.AddInnerProfile(rh.PolylineCurve([rh.Point3d(float(x),float(y),float(z)) for x,y in ring.coords]))
    assert e.IsValid and e.IsSolid
    model.Objects.AddExtrusion(e,attr(name,lay,mat,info));native_count+=1
def push(name,m,mat,lay,native=True,info=None):
    assert len(m.vertices)<65536 and len(m.faces)<65536
    assert m.is_watertight and np.isfinite(m.vertices).all(),name
    objects.append({'name':name,'mesh':m,'mat':mat});meshdata.append((m,mat))
    layer_map[name]={'layer':lay,'category':'environment' if lay=='Environment' else 'building','material':mat}
    if native:model.Objects.AddMesh(rhmesh(m),attr(name,lay,mat,info))
def chunk_meshes(prefix,ms,mat,lay,info=None):
    part=[];nv=nf=0;idx=0
    def flush():
        nonlocal idx
        if part:push(prefix+f'{idx:02d}',trimesh.util.concatenate(part),mat,lay,info=info);idx+=1
    for m in ms:
        if nv+len(m.vertices)>58000 or nf+len(m.faces)>58000:flush();part=[];nv=nf=0
        part.append(m);nv+=len(m.vertices);nf+=len(m.faces)
    flush()
def pitched(p,z,rise,axis=None):
    # Split on the ridge before triangulation, so each half is exactly planar.
    a,b,c,d=p.bounds;axis=axis or ('y' if d-b>c-a else 'x')
    mid=(a+c)/2 if axis=='y' else (b+d)/2;half=(c-a)/2 if axis=='y' else (d-b)/2
    cuts=[box(a-1,b-1,mid,d+1),box(mid,b-1,c+1,d+1)] if axis=='y' else [box(a-1,b-1,c+1,mid),box(a-1,mid,c+1,d+1)]
    ms=[]
    for cut in cuts:
        for q in polygons(p.intersection(cut)):
            m=extrusion(q,z,.12);h=rise*np.maximum(.001,1-abs(m.vertices[:,0 if axis=='y' else 1]-mid)/max(half,.1))
            top=m.vertices[:,2]>z+.06;m.vertices[top,2]+=h[top];ms.append(m)
    return ms
def facade(ms,p,z,h,levels,gothic=False,continuous=False,spacing=3.7):
    # Windows are illustrative repeated bays, not measured facade openings.
    for ring in [p.exterior]+list(p.interiors):
        cc=np.asarray(ring.coords)
        for a,b in zip(cc[:-1],cc[1:]):
            v=b-a;length=np.linalg.norm(v)
            if length<3.7:continue
            u=v/length;n=np.array([u[1],-u[0]])
            for k in range(max(1,int(levels))):
                zz=z+(k+.23)*h/max(1,levels);wh=min(h/max(1,levels)*.56,2.8)
                if zz+wh>z+h-.25:continue
                nwin=max(1,int(length/spacing));ww=min(spacing*.48,2.0)
                if continuous:ww=length/nwin-.16
                for j in range(nwin):
                    c=a+u*((j+.5)*length/nwin)+n*.07
                    pts=[(-ww/2,0),(ww/2,0),(ww/2,wh*.73),(ww*.28,wh*.92),(0,wh),(-ww*.28,wh*.92),(-ww/2,wh*.73)] if gothic else [(-ww/2,0),(ww/2,0),(ww/2,wh),(-ww/2,wh)]
                    wm=trimesh.creation.extrude_polygon(Polygon(pts),.08,engine='earcut')
                    # local window plane X/Z; thickness points away from wall.
                    vv=wm.vertices.copy();wm.vertices=np.column_stack((c[0]+vv[:,0]*u[0]+vv[:,2]*n[0],c[1]+vv[:,0]*u[1]+vv[:,2]*n[1],zz+vv[:,1]))
                    trimesh.repair.fix_normals(wm);ms['DarkGlass' if gothic else 'Glass'].append(wm)
                    # slender mullion and stone sill
                    for off in [0]:
                        aa=(c[0]+off*u[0]+n[0]*.11,c[1]+off*u[1]+n[1]*.11,zz)
                        bb=(aa[0],aa[1],zz+wh);ms['LightStone' if gothic else 'Frame'].append(cylinder(aa,bb,.045,4))
def crenellations(ms,p,top,corner_height=2.0):
    a,b,c,d=p.bounds
    for x,y in [(a+.45,b+.45),(a+.45,d-.45),(c-.45,b+.45),(c-.45,d-.45)]:
        ms['LightStone'].append(boxmesh(x,y,top,1.0,1.0,corner_height))
    for aa,bb in zip(np.asarray(p.exterior.coords)[:-1],np.asarray(p.exterior.coords)[1:]):
        v=bb-aa;length=np.linalg.norm(v)
        for t in np.arange(1.2,length-1,2.3):
            q=aa+v*t/length;ms['Limestone'].append(boxmesh(*q,top,.8,.8,.8))
