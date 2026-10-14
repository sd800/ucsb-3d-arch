"""Separate the mapped shoreline from the water dataset's offshore closure."""
import numpy as np
from shapely.geometry import LineString,Polygon

def mapped_shoreline(ocean):
    xy=np.asarray(ocean.exterior.coords)[:-1]
    lengths=np.linalg.norm(np.roll(xy,-1,axis=0)-xy,axis=1)
    closure=np.flatnonzero(lengths>2000)
    # This reviewed public source closes the offshore rectangle with three long
    # segments. They are data extent limits, not beaches or depth contours.
    assert len(closure)==3 and np.all(np.diff(closure)==1)
    start=(int(closure[-1])+1)%len(xy)
    return LineString([xy[(start+i)%len(xy)]for i in range(len(xy)-len(closure)+1)])

def open_sea_domain(ocean):
    coast=list(mapped_shoreline(ocean).coords)
    west,east=coast[0],coast[-1]
    # Continue the context well beyond the viewer's fully faded 4.2 km domain;
    # retain the source shoreline wherever it is available.
    domain=Polygon([*coast,(east[0]+10000,east[1]),(east[0]+10000,-12000),(west[0]-10000,-12000),(west[0]-10000,west[1])])
    assert domain.is_valid and domain.covers(ocean)
    return domain
