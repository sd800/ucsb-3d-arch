# Architectural references

## UCSB Library

- [Official floor plans](https://www.library.ucsb.edu/visit/floor-plans-locations): Ocean Side has four- and eight-storey wings; Mountain Side has two- and three-storey wings. The project uses the university footprint with individually mapped OSM building parts, rather than latitude bands.
- [First floor](https://www.library.ucsb.edu/ucsb-1st), [eighth floor](https://www.library.ucsb.edu/ucsb-8th): Paseo, western/eastern doors, Mountain entrance/courtyard and narrow tower plan. Floor-plan graphics were inspected, not redistributed.
- [Pfeiffer / Perkins Eastman](https://www.perkinseastman.com/projects/university-of-california-santa-barbara-library-addition-and-renewal/): built exterior photographs of the white portal, glass hall, new north wing, shallow roof overhang, recessed windows and public landscape.
- [University green features](https://www.library.ucsb.edu/about-library/green-features-new-library): reflective roof and paving.

The university outline is the outer XY limit; part boundaries are interpreted from current public map data and floor plans. Storeys are source-confirmed. Heights, opening modules, canopy members, courtyard furniture and steps are approximations, not as-built measurements. The entry approach meets the existing DEM; landscaping and bicycle routes retain source geometry.

## Roof finishes around the Library

`library_roof_reference.json` retains the exact public Esri World Imagery export extent and explicitly reviewed photovoltaic patch outlines. The image was viewed on 14 October 2026; its acquisition date is not asserted. Imagery is not redistributed. The Library tower is gray; the original two-storey roof combines a warm light membrane and clay-colored perimeter; the Ocean-side roof has tan perimeter surfacing, a lighter center and a small skylight. The north addition has light roofing with substantial dark photovoltaic patches. Library and Kerr panel modules are approximate, clipped to their inset roof outlines; the image's residual roof parallax is not treated as measured building displacement.

The same view resolves clay roof ranges on Girvetz, Webb, Noble, Music and Psychology, with flat connector/auditorium caps retained. Bioengineering is pale-roofed and does not receive the previous unsupported all-over solar grid. ILP retains a pale roof with lower display brightness. These are distinct material interpretations, not sampled survey-certified paint colors.

## ILP exterior circulation connections

[LMN’s project page](https://lmnarchitects.com/project/classroom-building-university-of-california) and the built exterior photographs `Interactive-Learning-Pavilion-10_Copyright-Patrick-Price-2000x1319.jpg` and `UCSB_ILP_17.jpg` show exterior stair flights with solid inclined support, continuous guards and landings connected to the curved terraces. The model now uses one top-of-slab datum at each upper level. Bridge end locations and a short landing link are registered to the mapped terrace polygons rather than disconnected fixed points. Rail panels open at the junctions. Stair member dimensions and detailed circulation positions remain approximate public-photo reconstructions. `output/ilp_connection_validation.json` records the modeled connections and checks.

The historical Pacific Ocean polygon contains three long offshore edges that close the GIS data extent. `scripts/coastal_geometry.py` separates that closure from the mapped land-facing shoreline. Only the latter controls offshore shading; extended open water is illustrative context outside the campus model, not a bathymetric reconstruction.
