# UC Santa Barbara Campus 3D Model

An independent, bilingual exterior study of the **University of California, Santa Barbara coastal Main Campus**, including the academic core, arts buildings, athletics, residences, Campus Lagoon, Lagoon Island, Campus Point, beaches and adjacent Pacific Ocean.

**Open `index.html` directly**, keeping `assets` and `output` beside it. No server or internet connection is required for local viewing. English is the initial language on every device; a manual Chinese choice is remembered. Landmark labels start hidden. Hover names remain available.

## Deliverables

| File | Contents |
| --- | --- |
| `index.html` | Root website, supporting HTTP and double-click viewing |
| `output/UCSB_MainCampus.3ds` | Metric exterior meshes; 1 unit = 1 meter |
| `output/UCSB_MainCampus_Layered.3dm` | Rhino v7, native building solids, one layer per mapped structure and one Environment layer |
| `output/UCSB_Campus_Offline.html` | Generated self-contained offline edition, included in the local delivery ZIP |
| `output/building_dimensions_and_sources.csv` | Bilingual building directory, mapped extents, height certainty and source notes |
| `output/layer_map.json` | Mapping of 3DS object names to building/environment layers |
| `scripts/apply_layers_rhino.py` | Restore layers after importing 3DS into Rhino |
| `output/campus_aerial.png` | Rendered preview and social-sharing image |
| `output/usage_guide.md` | Chinese usage instructions |

The model contains **175 building layers plus one Environment layer** and 24 architectural highlights. Separate mapped structures remain separate; disconnected pieces of a single polygon share their building layer. Excluded peripheral facilities are documented in `output/excluded_records.json`.

Refinements include Storke Tower's open frame, belfry and clocks; the library's stepped wings and tower; the Interactive Learning Pavilion's separate volumes and bridges; Henley shading fins; Bren courtyard, terraces and solar arrays; housing roof forms; stadium seating and field markings. Campus outdoor work includes mapped entrances, paths and cycle routes, route dashes, road edges, explicitly mapped crossing paint, parking areas, bicycle racks, plazas, paving joints, lawns and a historical flora inventory with distinct palms.

The coastal setting includes the full point, offshore rock islets, terrain down to the sea, beaches, coastal trails and boardwalks. Lagoon banks, wetland-margin reeds, restoration vegetation and island paths are integrated with residences and academic spaces. Coastal shrubs and member sizes are illustrative. The ocean extends beyond the campus framing: continuous shoreline-distance shading transitions from shallows to deeper blue and distant haze. Static surf accents avoid motion. Ocean colors are visual cartography, **not bathymetry**.

## Interaction

Left-drag pans; right-drag rotates; the wheel zooms at the pointer. On touch screens one finger pans, two fingers pan or pinch; Rotate enables one-finger rotation. Arrow keys pan and +/− zoom when the map has keyboard focus. Controls keep a grounded pivot and stop without inertia. Campus, core, arts/west, lagoon/coast, athletics and Plan presets frame different areas. Reset restores the core view. No Level toolbar option is shown.

Select, hide, isolate or locate individual buildings. Search either language, the model code or official building number. Outdoor hover names work independently of the hidden-by-default persistent labels. The viewer includes percentage loading, metric scale, elevation slicing, shadow/detail toggles, original CAD downloads and PNG export. WebGL 2 and browser Compression Streams are needed for interactive viewing; a preview and crawlable directory remain available otherwise.

## Sources and accuracy

- **UCSB public Buildings2026 GIS** identifies a DFSS extraction on 3 February 2026. Building outlines and names provide plan geometry. Historical campus-map layers provide walks, cycle routes, water, lawns, parking, entrances, racks and flora positions. Vegetation records are not a live census. [University maps](https://www.dfss.ucsb.edu/design-construction-services/maps).
- **OpenStreetMap contributors**, ODbL 1.0, provide supplemental shore, road, trail, outdoor-space and crossing geometry. [Attribution and license](https://www.openstreetmap.org/copyright).
- **USGS 3DEP** provides sampled bare-earth elevations, approximately 8 m per sample. Building pads are locally flattened. [Terrain service](https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer).
- **Storke Tower uses UCSB's published 175 ft (53.34 m) overall height.** Other heights, storeys, roof partitions, windows, structural members, vegetation sizes and unrecorded widths are approximate. The public BLDGHEIGHT field does not declare its unit: raw values remain in the directory, without silently treating them as certified metric heights. FLOORCOUNT may include basements.
- Coordinates use **EPSG:32611**, local meter offsets from WGS84 −119.8476, 34.4135. Z follows the DEM's meter datum. Sea/lagoon display levels are approximate; the model is not a tidal or flood forecast.
- This independent exterior study is **not official university BIM or a measured as-built survey**. Original English names remain available beside independent Chinese translations.

See `docs/PROJECT_NOTES.md`, `docs/THIRD_PARTY_NOTICES.md` and `sources/source_index.json`. Reference photographs and drawings are not redistributed.

## Web transfer and offline viewing

The website loads a lossless meshoptimizer + gzip stream, decoded and parsed in one worker with transferable typed arrays. No quantization or simplification is used in compression. `output/web_model_report.json` records transfer size and SHA-256 integrity. Original 3DS bytes are exactly recoverable; the CAD files remain downloadable. Shore-distance fields are precomputed at build time and supplied as small local textures, so clients do not calculate coastal geometry. See `docs/COMPRESSION.md`.

## Rebuild

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
npm ci
python3 scripts/prepare_sources.py
python3 scripts/build_coast.py
python3 scripts/build_campus.py
python3 scripts/render_preview.py
npm run build
npm run check:3ds
npm run check:ground
python3 scripts/validate_rhino.py
npm run check:compression
npm run check:interaction
npm run check:viewport
npm run check:hover
npm run check:locale
npm run check:seo
npm run check:release
python3 scripts/package_delivery.py
```

Source snapshots are retained, so rebuilding requires no live map access. Fetch scripts are provided for explicit future refreshes. `render_preview.py` supplies a fallback footprint preview; a PNG exported from the actual viewer is used for the delivered campus preview. Re-run packaging after replacing that image.

## Website and releases

Domain: **https://ucsb.arch.songming.org/**. Repository: **https://github.com/sd800/ucsb-3d-arch**. Canonical, Open Graph/Twitter, bilingual building content, structured 3DModel data, sitemap, robots and CNAME are included. Publishing and DNS must point the domain to the static host; a CNAME file alone does not configure the domain provider.

Work on `main`. `VERSION` records `YY.M.D.NUM`, with America/Chicago dates; every commit message is `Release YY.M.D.NUM`. The English changelog records user-facing changes. `.DS_Store` is ignored at every depth and retained locally. Filenames are English. Non-root implementation and provenance files are grouped under `scripts`, `config`, `docs`, `assets`, `sources` and `output`.

## Library and teaching-pavilion refinement

UCSB Library uses individual two-, three-, four- and eight-storey wings from current mapped part outlines and university floor plans, with a corrected narrow tower, glazed Paseo, entry portal and graded west approach. The Mountain courtyard and surrounding paths meet the existing landscape. See `sources/ARCHITECTURE_REFERENCES.md` and `output/library_detail.png`.

Interactive Learning Pavilion has curved inner terraces, an open paseo, connecting bridges, supported switchback stairs and narrow vertical glazing instead of unsupported full-height rods. See `output/interactive_learning_pavilion_detail.png`. These are public-source exterior reconstructions, with approximate component heights and member dimensions.

Where available, primary university CAD stripe geometry replaces interpreted parking rows, after comparison with satellite imagery and exclusion of garages, current buildings, planting and obsolete parking. Added coastal sand joins the campus parcel to the mapped waterline, with continuous grade and a closed underside.

Library roof finishes are differentiated by wing, with satellite-visible photovoltaic patches on the original/Mountain wings and Kerr Hall. Nearby clay roof ranges and pale membrane roofs retain their individual materials. See `sources/library_roof_reference.json` for the reviewed image extent and approximate array outlines.

ILP stairs, landings, terraces and both bridges form one connected upper circulation surface at each level. Treads meet the shared slab-top datum, supported by closed inclined waist slabs; rails leave the connecting routes open. Connection and level checks are recorded in `output/ilp_connection_validation.json`.

Offshore context uses only land-facing shoreline distances, excluding artificial water-map crop edges. The sea surface and closed depth volume share a continuous fade, including low-angle views. See `output/ocean_low_angle.png` and `output/ocean_continuity_validation.json`.
