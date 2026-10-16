# Changelog

## 26.10.15.8 — 2026-10-15

- Place collapsed Explore immediately to the left of Guide in a right-aligned action group, retaining the 6 px spacing and matching button styles. Wrap the pair together when the toolbar row has insufficient room.
- Preserve keyboard focus, selected landmark and language state when moving the collapse control between the panel and toolbar. Use UChicago or UW for concise browser verification of shared interface changes.

## 26.10.15.7 — 2026-10-15

- Bring the collapsed Explore button closer to Guide with a consistent 6 px gap on desktop and mobile.

## 26.10.15.6 — 2026-10-15

- Match the collapsed Explore button to Guide, including size, typography, colors, border and hover/focus states.
- Keep Guide right-aligned in the wrapping map toolbar on phones; use available row space instead of forcing a separate line. Position Highlights below the actual toolbar height in both languages and at different viewport widths.

## 26.10.15.5 — 2026-10-15

- Add an accessible top-right collapse button to Architectural Highlights. Collapsing replaces the panel with a single Explore button (localized in Chinese); clicking that button restores the panel.
- Shrink the collapsed panel, adapt its toggle for mobile layouts and preserve the current landmark, camera view and collapse state during language changes.
- Rename the guide entry to Guide, open its dialog at the heading instead of automatically scrolling to a link on phones, and place Sources after the model downloads.

## 26.10.15.4 — 2026-10-15

- Add two-finger parallel vertical dragging to adjust pitch directly, without enabling Rotate. Keep single-finger pan, two-finger twist, pinch zoom and desktop controls available.
- Distinguish deliberate tilt from pinch/turn/pan intent for each contact pair. Keep the tilt anchor fixed, prevent accidental zoom or heading changes, and stop at plan and horizon limits without inversion or inertia.
- Handle cancellation and close-contact recovery without queued movement or jumps; update English and Chinese controls help.

## 26.10.15.3 — 2026-10-15

- Add two-finger twist rotation around the gesture midpoint while preserving touch pan, pinch zoom, single-finger rotation mode and desktop navigation.
- Batch the two contacts once per frame, require a small intentional twist, and reset gesture baselines when fingers change or a gesture is canceled. Keep pitch, ground pivots and immediate stopping stable.
- Correct pinch centers when page and viewport coordinates differ; update English and Chinese controls help and verify combined gestures at plan, oblique and horizontal angles.

## 26.10.15.2 — 2026-10-15

- Classify verified university facilities and housing as Campus regardless of their location in Isla Vista or beyond the main campus boundary, including Embarcadero Hall, Isla Vista Theater, Pardall Center and modeled university housing.
- Move 263 mapped structures into the campus directory, leaving 1,199 independent neighboring structures. Remove their neighboring-name prefix and retain individual visibility, search and stable object codes.
- Keep verified campus extension ground, entrances, university parking and planting visible when neighboring areas are disabled, using a separate closed environment layer.
- Include the modeled campus extensions in Campus/Plan overview framing while retaining the initial core view.
- Record official affiliation sources and preserve existing building mesh geometry.
- Restore the complete five-pitch west recreation soccer group and surrounding ground beside Arrowhead Village; remove the diagonal campus crop and keep them visible with neighboring areas disabled.
- Consolidate duplicate soccer goal frames, connect their crossbars and anchor the net posts into the playing surface; omit fittings on cropped fragments of remote facilities.

## 26.10.15.1 — 2026-10-15

- Rebuild Anacapa, Santa Cruz and Santa Rosa with their mapped bent wings, open courtyards, low eaves, masonry ends and grouped window bays.
- Separate San Miguel and San Nicolas into eight-storey tower bars and lower community wings; refine their entrances, reveals, roofs and surrounding patios.
- Rebuild De La Guerra's dining/entry volumes, glazed pavilion and supported canopy; refine UCEN's lagoon-facing rooms, terraces and shade structures, and distinguish the Multi-Cultural Center's theater and entrance volumes.
- Refine Mosher Alumni House with terraced levels, glazed meeting spaces, plaza approach and an open circular Sky Terrace pergola.
- Add the mapped Eternal Flame memorial and Henley Gate, with connected bases, commemorative features and outdoor hover names.
- Refine Harder grandstands, recreation buildings, mapped track lanes, courts, baseball/softball diamonds, swimming lanes and connected sports equipment.
- Add 1,462 individually layered Isla Vista buildings, mapped streets, sidewalks, parks, coastal land and an expanded terrain sample. Provide a default-on ⁺Campus neighboring areas group, prefixed names, building search and a campus-only toggle.
- Keep context windows lightweight, lossless worker decoding, separate closed terrain and level building pads; retain stable roofs, hidden initial landmark labels and English by default.
- Standardize the Chinese translation of Santa Barbara and the university name across the website, sharing metadata and exports.

## 26.10.14.6 — 2026-10-14

- Exclude the legacy thin Earth backing from the browser scene now that Ground provides a continuous physical shell, preventing duplicate coplanar cliff/underside faces at low angles. Keep the original Rhino/3DS data and the modeled coastal bluffs.

## 26.10.14.5 — 2026-10-14

- Extend shallow terrain-tile undersides to a shared display datum and softly fade their unlit earth sides downward, removing the exposed faceted wedges in downhill horizontal views. Preserve the original CAD elevations and files.
- Restore closed terrain sides and undersides in the web viewer, including locally leveled building pads, to prevent floating or see-through bases at horizontal and low angles.
- Add a terrain and water depth barrier after stable road/lawn painting so underground geometry is occluded without reintroducing flickering surface overlaps.
- Keep the original CAD geometry, camera bearings and full horizontal rotation; add a focused horizontal/low-angle occlusion regression.

## 26.10.14.4 — 2026-10-14

- Rename the English heading, page title, sharing metadata and offline viewer to UC Santa Barbara Campus 3D Model.
- Merge adjacent curved terrace edges before buffering, removing narrow disconnected deck fragments and wall intrusions at their joins.
- Connect ILP stair landings, terraces and both bridges using the actual mapped wing boundaries; move the disconnected eastern bridge onto the facing circulation edges.
- Align slab tops, stair arrivals and landings at each floor, removing the previous 22 cm level mismatch. Replace stacked stair blocks with closed treads and continuous inclined waist slabs.
- Union terrace, bridge and landing slabs per floor and lower the supporting first-storey cap to avoid coincident walking surfaces.
- Exclude artificial offshore dataset edges from shoreline distances, extend open sea beyond the source crop and share surface/side-wall fades to remove low-angle ocean bands and hard edges.
- Add connected stair guards and handrails, open rail gaps at bridge/landing junctions, and fit the ground landing below the local terrain. Retain a connected three-wing upper circulation surface and record its geometry checks.

## 26.10.14.3 — 2026-10-14

- Replace the Library’s shared near-white roof with separate gray tower, warm membrane, clay perimeter and tan Ocean-side finishes, including its small skylight and shallow tower inset.
- Restore satellite-visible photovoltaic patches on the Library’s Mountain/original wings and Kerr Hall, keeping panels clear of roof edges.
- Restore local clay roof ranges on Girvetz, Webb, Noble, Music and Psychology buildings; remove unsupported generic solar arrays on Bioengineering and retain its pale roof.
- Reduce the pavilion roof material brightness while preserving its observed pale finish, matte lighting and stable depth ordering.

## 26.10.14.2 — 2026-10-14

- Rebuild Interactive Learning Pavilion with four-storey teaching volumes, an open paseo, curved inner terraces, supported switchback stairs, shallow guard panels, narrow vertical glazing and a pale membrane roof.
- Rebuild UCSB Library from official floor plans and mapped wings, correcting the tower depth and Paseo position; add the white entry portal, north addition, individual facade systems, graded west approach and Mountain courtyard.
- Close the unmodeled coastal strip between the campus parcel and mapped waterline; grade the added sand to sea level and retain a closed underside with a narrow wet-sand transition.
- Remove unsupported full-building facade rods and bound retained screens to the eaves of their own building wings.
- Replace reconstructed parking rows where available with primary university CAD stripe geometry checked against satellite imagery; retain explicit satellite rows for other clearly visible lots. Exclude obsolete parking, garages, current buildings, planting and the construction parcel.

## 26.10.14.1 — 2026-10-14

- Replace dense parking stripes with satellite-referenced rows, straight/angled bay outlines, clear aisles and solar carports; stop turning unmarked crossings into zebras. Distinguish explicitly mapped zebra/ladder paint from two-line crossing boundaries.
- Replace pale fallback ground with muted dry-earth tones, supplement mapped vegetation coverage, trim neighboring airport land and obsolete parking areas, and distinguish concrete paths, cycleways, plazas, asphalt and sand.
- Close the coastal land and island undersides below sea level, preventing floating terrain sheets in horizontal views. Add closed ocean/lagoon depth with a static downward fade so water remains visible at a level angle.
- Close short mapped route endpoint gaps, grade pedestrian and cycleway connections into roads, and interrupt curbs at through routes.
- Stop reading device language; retain English by default and remembered manual language choices.

## 26.10.13.1 — 2026-10-13

- Add an independent metric exterior model of the UC Santa Barbara main campus, with individual building layers, a separate environment layer, bilingual names and public-source provenance.
- Refine landmark volumes, mapped entrances, road edges, cycle dashes, crossings, bicycle racks, plazas, housing roofs, stadium stands and court markings.
- Include full Campus Point, offshore rocks, beach and bluff transitions, lagoon banks, reeds, island habitat, coastal paths and palms, with continuous shallow-to-deep ocean color and a distant fade.
- Fit terrain around exact building pads, add closed below-grade supports and complete edge-building ground, preventing floating or buried bases in horizontal views.
- Add an English-default bilingual website, hidden initial landmark labels, grounded controls, loading progress, contextual hover, CAD downloads and view export.
- Deliver losslessly compressed web models decoded in a single browser worker, layered Rhino and original 3DS files. Configure SEO and the ucsb.arch.songming.org domain.
