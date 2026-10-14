# Model notes

- Snapshot: 13 October 2026, America/Chicago. UCSB Buildings2026 describes a DFSS extraction dated 3 February 2026.
- The selected scope is the coastal Main Campus, including its northern athletic facilities, southern residences, Manzanita Village, Campus Lagoon, Lagoon Island and Campus Point. Separate San Clemente / West / North Campus properties and Isla Vista buildings are excluded.
- Every included public building polygon has its own Rhino layer. Disconnected parts of one polygon share that layer. Environment contains land, water, streets, paths, outdoor facilities, planting, furniture and ocean context.
- UCSB public paths, lawn, parking, water and flora mapping is historical; it is not claimed to be a live vegetation census. Trees that conflict with the current mapped building outlines are filtered out. Plant sizes and shapes are approximate. Coastal shrubs are illustrative habitat clusters.
- Original geographic coordinates use WGS84. Metric geometry uses local offsets in UTM zone 11N (EPSG:32611). Z follows the sampled USGS DEM meter datum; building pads are flattened. Sea and lagoon levels are approximate display levels, not tidal or flood predictions.
- Storke Tower overall height follows UCSB's published 175 ft (53.34 m). GIS BLDGHEIGHT has no explicit unit in the public field definition; raw values remain in metadata, but are not used as certified heights. FLOORCOUNT may include subterranean levels. Other external heights, storeys, facade openings, member sizes and roof partitions are approximate.
- Refinements include the tower's open piers, bell chamber and clocks; the library's 8-, 4-, 3- and 2-storey sections; the pavilion's separated teaching volumes, open circulation and bridges; Henley shading fins; Bren courtyard, terraces and solar panels; tiled housing roofs, stepped stands, field lines, paving joints, parking bays, palms and coast trails.
- The ocean extends well beyond the campus framing. A static outer haze blends the remote sea into the viewer background. Shoreline-distance color gradients and sparse surf accents are artistic cartography, not bathymetry or a hydrodynamic simulation. No water animation or camera-dependent noise is used.
- English is the initial language on all devices. Chinese can be selected manually and is remembered. Independent Chinese translations preserve the original meaning; English names remain visible in details. Landmark labels start unchecked. Building and outdoor hover names remain available.
- Original CAD bytes are losslessly coded for web transfer, decoded and parsed in one worker with transferable arrays. The original metric Rhino and 3DS exports remain available. No quantization or mesh simplification is applied during compression.
- This is an independent public-source exterior study, not official university BIM, a measured as-built survey or a navigation aid.

- Road edges are notched at walk/cycle connections. Public entrance and rack positions, contributed crossings and cycle-route dashes add local connections. Lagoons have closed shore banks, small illustrative reed clusters and a smooth shore-color field.
- In the Rhino export, native volume extrusions replace the corresponding body meshes; duplicate coplanar body shells are not stored. The original 3DS retains all bodies.

- Flora shapes distinguish palms, taller eucalyptus/corymbia and lower succulent / bird-of-paradise records. Taxonomic records do not establish measured plant heights.

- Ground is triangulated with building-footprint holes, then filled by flat grade pads at each building base. Closed below-grade support skirts bridge the simplified terrain; these are visualization supports, not surveyed foundations. The terrain scope includes complete boundary-building footprints. `check_ground_contact.mjs` compares exported ground triangles with 1,505 points over every building.
