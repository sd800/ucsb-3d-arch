"""Mapped UCSB playing surfaces with conservative, connected sports fittings."""
from cad_core import *
from campus_refinement import add

def athletics_details(eg,osm,ground,env,place,footprints,scope):
    # Named fields retain source extents; unmeasured posts/net spacings are
    # approximate equipment rather than claims of a surveyed facility layout.
    for f in osm:
        t=f['properties'];g=f['poly'];sport=t.get('sport','')
        if g.geom_type not in ['Polygon','MultiPolygon']or not g.intersects(scope):continue
        if not(t.get('leisure')in ['pitch','swimming_pool']or t.get('osm_id')=='relation/5298065'):continue
        # Do not fit new equipment to a clipped fragment of a remote facility.
        if g.intersection(scope).area<g.area*.995:continue
        for q in polygons(g.intersection(scope).difference(footprints)):
            c=np.array(q.centroid.coords[0]);rr=np.array(q.minimum_rotated_rectangle.exterior.coords)[:4];vectors=np.roll(rr,-1,axis=0)-rr;lengths=np.linalg.norm(vectors,axis=1);u=vectors[np.argmax(lengths)]/max(lengths);v=np.array([-u[1],u[0]]);L=max(lengths);W=min(lengths)
            def paint(geom,mat='Marking',z=.40):env(geom.intersection(q),z,.015,mat)
            def segment(a,b,width=.07):paint(LineString([a,b]).buffer(width,cap_style=2))
            if t.get('leisure')=='swimming_pool':
                # Pool rim follows the mapped outline and lane ropes lie just
                # above the water, rather than a large solid roof-like slab.
                env(q.boundary.buffer(.34).difference(q),.39,.08,'Concrete')
                if L>22 and W>12:
                    lanes=max(4,min(10,round(W/2.4)))
                    for j in range(1,lanes):
                        cc=c+v*(-W/2+j*W/lanes)
                        line=LineString([cc-u*(L/2-.6),cc+u*(L/2-.6)]).intersection(q)
                        paint(line.buffer(.065),'Purple',.405)
                    for sign in [-1,1]:
                        cc=c+u*sign*(L/2-.25);zz=float(ground(*cc))+.40
                        for d in [-.30,.30]:
                            p=cc+v*d;eg['Frame'].append(cylinder((*p,zz),(*p,zz+.9),.035,6))
                        eg['Frame'].append(cylinder((*(cc-v*.30),zz+.9),(*(cc+v*.30),zz+.9),.035,6))
                continue
            if t.get('osm_id')=='relation/5298065':
                # The mapped running track is a ring with its real infield hole.
                # Use parallel lane rings, all clipped inside that same surface.
                for lane in np.arange(.8,7.8,1.05):
                    inset=q.buffer(-lane)
                    if not inset.is_empty:paint(inset.boundary.buffer(.045))
                place('Edwin W. Pauley Track','埃德温·W.波利田径场',q)
            if t.get('leisure')!='pitch':continue
            if 'soccer'in sport:
                for sign in [-1,1]:
                    end=c+u*(L/2-.25)*sign;back=end-u*sign*16.5
                    segment(end-v*20.16,back-v*20.16);segment(back-v*20.16,back+v*20.16);segment(back+v*20.16,end+v*20.16)
                    # Goal net is an open back frame, with sparse horizontal cords
                    # instead of a translucent coplanar sheet that shimmers.
                    z=float(ground(*end))+.27
                    eg['Frame'].append(cylinder((*(end-v*3.66),z+2.44),(*(end+v*3.66),z+2.44),.055,6))
                    for side in [-1,1]:
                        p=end+v*3.66*side;b=p+u*sign*1.8
                        eg['Frame'].append(cylinder((*p,z-.45),(*p,z+2.44),.055,6));eg['Frame'].append(cylinder((*p,z+2.44),(*b,z+2.0),.035,5));eg['Frame'].append(cylinder((*b,z-.45),(*b,z+2.0),.035,5))
                    for h in [.5,1.,1.5,2.]:eg['Marking'].append(cylinder((*(end-v*3.66+u*sign*1.8),z+h),(*(end+v*3.66+u*sign*1.8),z+h),.015,4))
            if sport=='basketball':
                segment(c-v*W/2,c+v*W/2);paint(Point(*c).buffer(1.8,quad_segs=24).boundary.buffer(.06))
                for sign in [-1,1]:
                    end=c+u*(L/2-.2)*sign;back=end-u*sign*5.8
                    for aa,bb in [(end-v*2.45,back-v*2.45),(back-v*2.45,back+v*2.45),(back+v*2.45,end+v*2.45)]:segment(aa,bb)
                    p=end-u*sign*1.0;z=float(ground(*p))+.3;outside=end+u*sign*1.1
                    eg['Frame'].append(cylinder((*outside,z),(*outside,z+3.8),.085,6));eg['Frame'].append(cylinder((*outside,z+3.8),(*p,z+3.05),.065,6))
                    board=LineString([p-v*.9,p+v*.9]).buffer(.05,cap_style=2);add(eg,board,z+2.8,1.05,'WhitePanel')
                    rim=Point(*(p-u*sign*.35)).buffer(.23,quad_segs=12).boundary.buffer(.025);add(eg,rim,z+3.05,.035,'Tile')
            if sport in ['baseball','softball']:
                # Home plate is the acute, south-east vertex in the mapped
                # fan-shaped pitch; baseline axes run toward the outfield.
                xy=np.array(q.simplify(.5).exterior.coords)[:-1];home=xy[np.argmax(xy[:,0]-xy[:,1])];out=c-home
                if np.linalg.norm(out)<1:continue
                direction=out/np.linalg.norm(out);side=np.array([-direction[1],direction[0]]);dist=27.43 if sport=='baseball'else 18.29
                u0=(direction+side)/math.sqrt(2);v0=(direction-side)/math.sqrt(2);home=home+direction*2.5
                one=home+u0*dist;three=home+v0*dist;two=home+(u0+v0)*dist
                diamond=Polygon([home,one,two,three]);dirt=diamond.buffer(3.3).union(Point(*home).buffer(5.0,quad_segs=20))
                paint(dirt,'Track',.365)
                for p0,p1 in [(home,one),(one,two),(two,three),(three,home)]:segment(p0,p1,.06)
                for pp in [home,one,two,three]:paint(Point(*pp).buffer(.33,quad_segs=1),'Marking',.41)
                mound=home+direction*(18.44 if sport=='baseball'else 13.1);paint(Point(*mound).buffer(2.7,quad_segs=20),'Track',.38)
                # Mapped outfield boundary supports a sparse, shallow wire fence.
                edge=q.exterior
                for d0 in np.arange(0,edge.length,5):
                    pp=edge.interpolate(d0)
                    if pp.distance(Point(*home))<13:continue
                    z=float(ground(pp.x,pp.y));eg['Frame'].append(cylinder((pp.x,pp.y,z),(pp.x,pp.y,z+2.3),.045,5))
                place('Caesar Uyesaka Stadium'if sport=='baseball'else 'Campus softball field','凯撒·上坂棒球场'if sport=='baseball'else '校园垒球场',q)
            if sport in ['tennis','beachvolleyball','volleyball']:
                # Net posts extend below terrain; all attachments share the
                # same local grade so no separate equipment floats above a path.
                h=1.07 if sport=='tennis'else 2.43
                for sign in [-1,1]:
                    pp=c+v*sign*(W/2+.15);z=float(ground(*pp));eg['Frame'].append(cylinder((*pp,z-.3),(*pp,z+h),.045,6))
                z=float(ground(*c));eg['Frame'].append(cylinder((*(c-v*W/2),z+h-.05),(*(c+v*W/2),z+h-.05),.025,5))
                for dd in np.arange(-W/2,W/2,.65):
                    pp=c+v*dd;eg['Furniture'].append(cylinder((*pp,z+h-.08),(*pp,z+max(.2,h-.95)),.012,4))
