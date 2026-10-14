# Model notes

- Snapshot: 13 October 2026, America/Chicago. UCSB Buildings2026 describes a DFSS extraction dated 3 February 2026.
- The selected scope is the coastal Main Campus, including its northern athletic facilities, southern residences, Manzanita Village, Campus Lagoon, Lagoon Island and Campus Point. Separate San Clemente / West / North Campus properties and Isla Vista buildings are excluded.
- Every included public building polygon has its own Rhino layer. Disconnected parts of one polygon share that layer. Environment contains land, water, streets, paths, outdoor facilities, planting, furniture and ocean context.
- UCSB public paths, lawn, parking, water and flora mapping is historical; it is not claimed to be a live vegetation census. Trees that conflict with the current mapped building outlines are filtered out. Plant sizes and shapes are approximate. Coastal shrubs are illustrative habitat clusters.
- Original geographic coordinates use WGS84. Metric geometry uses local offsets in UTM zone 11N (EPSG:32611). Z follows the sampled USGS DEM meter datum; building pads are flattened. Sea and lagoon levels are approximate display levels, not tidal or flood predictions.
- Storke Tower overall height follows UCSB's published 175 ft (53.34 m). GIS BLDGHEIGHT has no explicit unit in the public field definition; raw values remain in metadata, but are not used as certified heights. FLOORCOUNT may include subterranean levels. Other external heights, storeys, facade openings, member sizes and roof partitions are approximate.
- Refinements include the tower's open piers, bell chamber and clocks; the library's 8-, 4-, 3- and 2-storey sections; the pavilion's separated teaching volumes, open circulation and bridges; Henley shading fins; Bren courtyard, terraces and solar panels; tiled housing roofs, stepped stands, field lines, paving joints, mapped parking areas, palms and coast trails.
- The ocean extends well beyond the campus framing. A static outer haze blends the remote sea into the viewer background. Shoreline-distance color gradients and sparse surf accents are artistic cartography, not bathymetry or a hydrodynamic simulation. No water animation or camera-dependent noise is used.
- English is the initial language on all devices. Chinese can be selected manually and is remembered. Independent Chinese translations preserve the original meaning; English names remain visible in details. Landmark labels start unchecked. Building and outdoor hover names remain available.
- Original CAD bytes are losslessly coded for web transfer, decoded and parsed in one worker with transferable arrays. The original metric Rhino and 3DS exports remain available. No quantization or mesh simplification is applied during compression.
- This is an independent public-source exterior study, not official university BIM, a measured as-built survey or a navigation aid.

- Road edges are notched at walk/cycle connections. Public entrance and rack positions, contributed crossings and cycle-route dashes add local connections. Lagoons have closed shore banks, small illustrative reed clusters and a smooth shore-color field.
- In the Rhino export, native volume extrusions replace the corresponding body meshes; duplicate coplanar body shells are not stored. The original 3DS retains all bodies.

- Flora shapes distinguish palms, taller eucalyptus/corymbia and lower succulent / bird-of-paradise records. Taxonomic records do not establish measured plant heights.

- Ground is triangulated with building-footprint holes, then filled by flat grade pads at each building base. Closed below-grade support skirts bridge the simplified terrain; these are visualization supports, not surveyed foundations. The terrain scope includes complete boundary-building footprints. `check_ground_contact.mjs` compares exported ground triangles with contact points over every building.

- Road crossings are painted only when OSM explicitly identifies zebra/ladder or two-line markings and the point lies on a mapped vehicular street. Unmarked, surface-only and unspecified crossings do not create white bars. Parking-lot polygons do not imply surveyed stall locations, so row paths are interpreted separately from satellite imagery, with observed aisles and row orientations retained; individual bay sizes remain approximate. See `output/parking_validation.json`. The source-ID audit is in `output/crossing_validation.json`.
- Ground materials distinguish weathered concrete walks, asphalt/cycleways, warm plaza paving, sand, mapped lawn and native planting. OSM land-cover polygons supplement the campus lawn layer. Unclassified exposed ground uses a subdued dry-earth tone, not white paving or an assertion of surveyed planting. UCSB describes a mix of managed landscapes and native coastal habitats: https://ccber.ucsb.edu/restoration-area-campus-lagoon and https://www.sustainability.ucsb.edu/focus-areas/landscape-and-biotic-environment .
- Path endpoints can bridge a source gap of at most 2.2 m to a mapped road or another route, clipped clear of building footprints. Short graded transitions lower concrete/cycleway skins to the road surface; curbs are interrupted at connections. These are source cleanup and illustrative surface grades, not an accessibility survey. See `output/junction_validation.json`.

- Campus ground is clipped to the mapped university property and the full coastal point, with complete pads for all selected buildings. Neighboring airport land is not filled by an unclassified campus ground sheet.

- A continuous closed earth mass now extends from Campus Point, Lagoon Island and all other campus land to a flat underside below sea level. The browser draws its sides and underside separately from the map skins, so terrain extrusion-side filtering cannot leave a floating coastal sheet or obscure surface detail.

- Parking row paths, straight/angled arrangements, inactive former lots and Lot 50 solar carport strips were checked against Esri World Imagery. The vector reference and attribution are retained in `sources/parking_layouts.json`; satellite rasters are not bundled. Parking paint is clipped clear of current building footprints and mapped planting islands.

- Ocean and lagoon include closed display-depth volumes with a static downward color fade, so water does not disappear into a zero-thickness plane at an exact horizon view. Display depths are presentation geometry, not bathymetric measurements. The viewer filters internal soil patch walls and uses only actual land/water boundary faces for the visible earth perimeter.

- Mapped lawn islands override the enclosing parking parcel, while actual street corridors remain open. Back-to-back angled bays use parallel dividers rather than opposing chevrons.
