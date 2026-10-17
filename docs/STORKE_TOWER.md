# Storke Tower and sunken plaza reconstruction

The earlier tower used exposed posts and an open stack of stair landings, and added clock disks. Owner photographs show a mostly closed concrete shaft and tall rounded belfry slots. The earlier surrounding model also treated Storke Publications as an above-ground block and Storke Plaza as ordinary grade, despite the public map explicitly tagging the court below grade.

## Rebuilt features

- Retained the official tower footprint and UCSB's published 175 ft (53.34 m) height.
- Closed the shaft with board-formed concrete walls and restrained pour joints.
- Subtracted four large round-arched base openings as real geometry, with a sheltered stair, core, supported railings and corner posts.
- Subtracted three long, narrow, round-headed belfry apertures per face. The twelve openings have wall thickness and deep reveals, separated by solid concrete piers. They are not painted lines or applied facade rods.
- Recessed the bronze bell shells and their racks inside the belfry; removed invented clock faces. The 61-bell count is published, while the arrangement and sizes are illustrative.
- Rebuilt the below-grade media frontage with an arcade aligned to the retained mapped south edge and a supported roof walk at the upper arrival level.
- Cut the real lower-court domain out of the ordinary ground stack, including its stair access. Added a continuous lower supporting slab, restrained paving, the western reflecting pool, connected west/south steps, benches, broad-crowned date palms and terrace railings.
- Shared the lower court and individual stair heights with camera/hover ground lookup. Kept the existing Explore camera direction and preserved the tower's concrete cap color in the web renderer.

## Evidence and limits

- [Owner photograph: tower, arcade and reflecting pool](https://conferences.ucsb.edu/summer-conferences/attendee-information)
- [Owner photograph: full shaft, base arch, stair and railing](https://yang.chem.ucsb.edu/contact)
- [UCSB: 175 ft tower and 61 bells](https://news.ucsb.edu/2014/014151/bells)
- [UCSB campus tower entry](https://www.campuscalendar.ucsb.edu/storke_tower)
- [Daily Nexus: firsthand carillon feature](https://dailynexus.com/interactives/storke-tower-carillon/)
- [Mapped plaza boundary and below-grade layer](https://www.openstreetmap.org/way/218817558)
- The retained building footprints come from the archived official UCSB 2026 GIS layer in `sources/ucsb_buildings.geojson`.

Secondary member widths, concrete joint intervals, internal bell mounts, pool tracing and the 2.70 m court drop are photo/map interpretations, not surveyed dimensions or verified interior plans. Source imagery is consulted, not redistributed in the repository. The native CAD geometry and the full-detail campus web derivative are regenerated together; regional LOD remains limited to neighboring areas.

## Focused checks

`npm run check:storke` reads the actual exported 3DS position and face chunks. It tests the closed middle shaft, twelve open belfry slots, rounded heads and solid shoulders, intermediate piers, four base arch voids, courtyard/pool datums, all 32 stair treads and their upper landings, and every arcade bay and supporting end pier. It also checks camera/hover grade data, the unique plaza hover entry and preservation of the concrete cap material. `npm run check:highlights` independently counts connected bronze bell shells. Native closed-solid validation, source/packet integrity and browser views complete the checks.
