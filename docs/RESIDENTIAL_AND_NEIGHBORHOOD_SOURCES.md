# Residential, public-space and Isla Vista refinements

Reviewed 14 October 2026. The official 2026 campus footprint remains the plan boundary. Exterior photos and university layout maps guide volume divisions, surface character and architectural features. Heights other than Storke Tower and unrecorded component sizes are estimates. This is an exterior study, not an as-built survey.

## Residence halls and dining

- [Anacapa — Campus Housing](https://www.housing.ucsb.edu/housing-options/options-filter/anacapa) and its [hall layout](https://www.housing.ucsb.edu/housing-options/options-filter/anacapa/anacapa-hall-emergency-map): four bent wings, open lawns/courts, low roofs, masonry ends, entrance and patio character. Preserve the official plan voids; do not infer enclosed courtyards where the footprint is open.
- [Santa Cruz — Campus Housing](https://www.housing.ucsb.edu/housing-options/options-filter/santa-cruz): photographed two-storey wings, deep overhangs, pale wall panels and darker masonry ends. [Santa Rosa](https://www.housing.ucsb.edu/housing-options/options-filter/santa-rosa) retains its separate mapped zigzag geometry.
- [San Miguel](https://www.housing.ucsb.edu/housing-options/options-filter/san-miguel) and [official hall layout](https://www.housing.ucsb.edu/housing-options/options-filter/san-miguel/san-miguel-hall-emergency-map): eight-storey residential towers, lower community core, entrance, lounge patio and exterior stage. Separate the offset tower bars rather than extruding the entire footprint to eight storeys. Photograph gallery includes the 2026 stage. Mural artwork is not copied into textures.
- [San Nicolas — Campus Housing](https://www.housing.ucsb.edu/housing-options/options-filter/san-nicolas): distinguish residential tower bars and low connecting space, with lagoon-side outdoor connections. Window spacing, pier widths and envelope heights are estimated.
- [De La Guerra — Campus Dining](https://dining.ucsb.edu/dining-commons/de-la-guerra-dining-commons): current exterior gallery guides the glass entrance pavilion, low dining volume, roof overhang, supported entrance canopy and planted court. This replaces the shared generic pitched roof. The [UC Physical Design Framework](https://regents.universityofcalifornia.edu/regmeet/sept10/gb7attach2.pdf), page 32, provides an additional entrance reference.

## UCEN, MCC and Mosher

- [University Center outdoor spaces](https://www.ucen.ucsb.edu/meet/meetings-events/outdoor-spaces) and [spaces gallery](https://www.ucen.ucsb.edu/meet/meetings-events/spaces): lagoon-facing lower meeting rooms, slope to the permanent stage, patios, Friendship Court and Lagoon Plaza. The model expresses terrace steps, glazing and supported shade structures within the university footprint. Terrace member dimensions are interpretations, not recorded construction dimensions.
- [Multi-Cultural Center](https://mcc.sa.ucsb.edu/): the mapped theater and lower entrance/lounge are represented as distinct volumes, with a glazed approach. Theater interiors and a surveyed seating plan are not included.
- [Mosher Alumni House — UCSB Alumni](https://www.alumni.ucsb.edu/about/mosher-house): Garden, Plaza and Vista levels and the open Sky Terrace inform the stepped exterior and circular pergola. The pergola retains an open central sky view and supported perimeter, replacing the previous generic planted roof. Whalen Plaza and meeting-room glazing follow the photographed exterior character. The footprint controls position; elevations and member sizes are estimated.

## Memorial, gateway and athletics

- [Walk With Us — UCSB Current](https://news.ucsb.edu/2016/016268/walk-us): five university event photos show Eternal Flame's curved concrete memorial, plaque and stone bed. Its location uses OSM node 12860268876 near Buchanan Hall, between Buchanan and the Library. The small static flame is a visual interpretation; it does not assert that the real burner is operating. The university [TGIF project list](https://www.sustainability.ucsb.edu/tgif/projects) records a revitalization proposal.
- [Visit UCSB](https://www.ucsb.edu/about/visit), [university giving report](https://giving.ucsb.edu/sites/default/files/documents/annual-reports/private-giving-06-07.pdf) and [university entrance photograph](https://news.ucsb.edu/2023/020880/safer-217): Henley Gate's curved metal arch, stone piers and low approach walls. Mapped gantry way 667086101 supplies orientation/span. Pier, arch and stone-course dimensions remain approximate.
- [UCSB Recreation facilities](https://recreation.ucsb.edu/facilities) and [Harder Stadium](https://ucsbgauchos.com/facilities/harder-stadium/1): mapped sports surfaces, stands and recreation-building footprints form the basis. Field-facing stepped grandstands, lower entrance wings, track lanes, pool rims/lane ropes, court fittings, baseball/softball diamonds and sparse open nets provide readable exterior detail. Standard equipment dimensions and line widths are approximations. No surveyed court or track certification is claimed.

## Isla Vista context

- Source extracts: `osm_map_iv_west.xml.gz` and `osm_map_iv_east.xml.gz`, retained unchanged. Normalization combines these with the earlier campus extracts and deduplicates source IDs. [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0.
- The modeled surrounding area extends west from the campus through western Isla Vista, including Pardall, the Embarcaderos, Del Playa and mapped parks. It contains 1,462 separate building records; it does not cover all Goleta or the remote UCSB North/West Campus properties.
- Footprint holes and tagged building levels/heights are retained. Unrecorded heights use conservative low-rise estimates. Facade bays, shallow roof details, material choices, narrow entrance approaches and supplementary vegetation are approximate. No generic rooftop machinery is added.
- Streets, pedestrian routes, mapped parking polygons, park boundaries, ponds and coast are derived from source geometry. Road-width estimates and short facade approaches are illustrative. Unverified neighborhood parking-stall grids and zebra crossings are omitted. Existing campus parking paint retains its earlier CAD/satellite source audit.
- [Isla Vista Recreation and Park District — Anisq’Oyo’ Park](https://ivparks.org/isla-vista-district-parks/central-downtown-parks/anisqoyo-park/) confirms the park/pond/amphitheater context. Indigenous park names are retained rather than inventing literal Chinese translations. Supplementary plant locations do not claim a tree survey.
- `neighbor_terrain_dem.tif` supplies expanded [USGS 3DEP](https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer) elevations. Terrain meets the earlier campus scope with a narrow grade blend; flat building pads and closed support skirts prevent floating bases. Geometry uses EPSG:32611 local meters, matching the campus export.
- `neighboring_source_manifest.json` records download URLs and hashes. `refinement_photo_index.json` retains university photo URLs/captions; third-party reference images themselves are not redistributed.

## Display and naming

The default-on **⁺Campus neighboring areas** checkbox controls the complete context, including buildings, land, routes and planting. Its name frames the surrounding district. Search omits the pinned group and finds individual neighboring records; their displayed and hover names receive a ⁺ prefix. Campus counters retain their campus-only meaning.

Initial language remains English on every device; manual Chinese remains available. Santa Barbara is consistently 圣巴巴拉 and the university is 加州大学圣巴巴拉分校. Landmark labels remain hidden initially, while hover labels remain available.
