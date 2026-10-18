# UC Santa Barbara highlight refinement

All 24 architectural highlights are individually reviewed in [the architectural form audit](HIGHLIGHT_ARCHITECTURE_AUDIT.md). That audit records source-specific reconstructions and the individual forms retained after review. The component table below documents joinery only; a frame count is not architectural verification. This remains a public-source exterior interpretation; opening positions and member dimensions are not a measured facade survey.

Shaped reveals follow the existing glass outlines, including pointed Gothic heads. Frames and transoms remain within each opening zone. Coping follows actual roof triangles, including concave plans, and stays supported on its roof finish. No automatic rooftop equipment boxes or arbitrary full-height facade rods are introduced. Repeated components retain separate material/feature ownership.

Campbell Hall separates the lecture-hall drum from lower wings and uses an alternating folded-plate roof plus tall plaza glazing, interpreted from the owner's exterior photograph. Kohn Hall separates its warm gate-facing tower and low wings; the courtyard concavity is retained from the map and receives a supported, partly open high awning and paving, using the public two-floor plan as a layout reference. Bioengineering uses three storeys in accordance with the department facilities description. Storke is rebuilt as a closed board-formed concrete shaft, with four actual base arch voids and three tall round-headed belfry apertures per face. Its 61 bronze bells sit behind the deep openings. The sunken plaza, reflecting pool, below-grade media arcade and two connected stair flights replace the former flat ground and above-grade media box. Overall tower height is published; secondary dimensions and court grades are photo/map interpretations. See [the focused architectural review](STORKE_TOWER.md). Harder Stadium adds guardrails supported on its upper modeled grandstand tread.

- [Campbell Hall plaza photograph — AAIT](https://aait.ucsb.edu/event-av-services/campbell-hall/gallery)
- [Kohn Hall architecture — KITP](https://www.kitp.ucsb.edu/news/new-kohn-hall)
- [Kohn Hall public plan — KITP](https://www.kitp.ucsb.edu/sites/default/files/kitp/maps/KITPemergencymap.png)
- [Bioengineering facilities — department](https://bioengineering.ucsb.edu/facilities)
- [Storke Tower — university](https://www.campuscalendar.ucsb.edu/storke_tower)

The campus keeps its existing full campus renderer. Regional LOD continues to apply only to Isla Vista and neighboring areas.

| Code | Highlight | Framed openings | Transoms | Roof coping (m) | Reference |
|---|---|---:|---:|---:|---|
| S001 | Henley Hall | 0 | 0 | 0.00 | [Reference](https://kierantimberlake.com/work/henley-hall-institute-for-energy-efficiency/) |
| S008 | Campbell Hall | 16 | 15 | 32.96 | [Reference](https://aait.ucsb.edu/event-av-services/campbell-hall/gallery) |
| S022 | Elings Hall (CNSI) | 0 | 0 | 0.00 | [Reference](https://www.mat.ucsb.edu/~g.legrady/academic/courses/09f200a/c/cnsi.html) |
| S030 | Kohn Hall | 110 | 0 | 0.00 | [Reference](https://www.kitp.ucsb.edu/news/new-kohn-hall) |
| S040 | UCSB Library | 657 | 342 | 849.44 | [Reference](https://www.library.ucsb.edu/visit/floor-plans-locations) |
| S042 | Harold Frank Hall | 0 | 0 | 0.00 | [Reference](https://sp.dfss.ucsb.edu/entrances/enter-bldg/hfh.html) |
| S053 | Bren Hall | 0 | 0 | 0.00 | [Reference](https://bren.ucsb.edu/about/bren-hall) |
| S054 | Bioengineering | 0 | 0 | 0.00 | [Reference](https://bioengineering.ucsb.edu/facilities) |
| S061 | Storke Tower | 1 | 0 | 0.00 | [Reference](https://www.campuscalendar.ucsb.edu/storke_tower) |
| S063 | Interactive Learning Pavilion | 235 | 0 | 368.25 | [Reference](https://lmnarchitects.com/project/classroom-building-university-of-california) |
| S065 | Marine Science Building | 0 | 0 | 0.00 | [Reference](https://msi.ucsb.edu/facilities-services/marine-science-research-building) |
| S066 | Music | 0 | 0 | 0.00 | [Reference](https://music.ucsb.edu/operations/facilities) |
| S076 | University Center (UCEN) | 296 | 182 | 846.46 | [Reference](https://www.ucen.ucsb.edu/meet/meetings-events/outdoor-spaces) |
| S078 | Robertson Gym | 204 | 167 | 1278.86 | [Reference](https://recreation.ucsb.edu/facilities) |
| S084 | Events Center | 116 | 116 | 282.04 | [Reference](https://ucsbgauchos.com/facilities) |
| S086 | Humanities and Social Sciences Building | 0 | 0 | 0.00 | [Reference](https://marcuse.faculty.history.ucsb.edu/projects/HSSBLocation.htm) |
| S088 | Student Resource Building | 0 | 0 | 0.00 | [Reference](https://srb.sa.ucsb.edu/about) |
| S091 | Arts | 0 | 0 | 0.00 | [Reference](https://arts.ucsb.edu/atrium/) |
| S095 | San Rafael Tower | 0 | 0 | 0.00 | [Reference](https://www.housing.ucsb.edu/housing-options/options-filter/san-rafael) |
| S125 | University House | 0 | 0 | 0.00 | [Reference](https://news.ucsb.edu/in-focus/uc-regents-approve-acquisition-campus-residential-property) |
| S130 | Benioff Ocean Science Laboratory | 0 | 0 | 0.00 | [Reference](https://news.ucsb.edu/2026/022864/ucsb-seeks-community-input-university-plans-sea-level-rise) |
| S151 | Harder Stadium | 0 | 0 | 0.00 | [Reference](https://ucsbgauchos.com/facilities/harder-stadium/1) |
| S166 | Recreation Center (Rec Cen) | 213 | 155 | 389.29 | [Reference](https://recreation.ucsb.edu/facilities) |
| S173 | Mosher Alumni House | 75 | 70 | 215.57 | [Reference](https://www.alumni.ucsb.edu/about/mosher-house) |

Joinery coverage is a component-presence check, not proof of agreement with real architecture. The true Storke openings, closed shaft, concrete piers, stair landings, courtyard levels and roof color are separately tested against the actual exported CAD by `scripts/check_storke.mjs`. Coverage and exported bell counts are checked by `scripts/check_highlights.py`. CAD import, compressed-byte integrity, existing navigation checks and concise representative near-view browser checks are used for validation.
