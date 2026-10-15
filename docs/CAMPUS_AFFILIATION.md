# Campus affiliation and neighboring-area display

Reviewed 15 October 2026. **Campus membership is separate from location.** A university facility can stand within the Isla Vista street grid. The neighboring-area checkbox must not hide verified university facilities or leave their buildings without ground.

## Verified facilities

- [Embarcadero Hall — UCSB Academic Affairs IT](https://aait.ucsb.edu/event-av-services/embarcadero-hall): university teaching, offices and events at 935 Embarcadero del Norte. [UCSB Current](https://news.ucsb.edu/2004/011799/ucsb-introduces-iv-live) explicitly describes it as a university-owned building. The retained 2026 university footprint layer also includes it.
- [Isla Vista Theaters — UCSB Academic Affairs IT](https://aait.ucsb.edu/event-av-services/isla-vista-theaters): university teaching and event facilities at 960 Embarcadero del Norte.
- [Pardall Center — Associated Students](https://pardallcenter.as.ucsb.edu/about/history/): the university's Associated Students resource center, also present in the official facility footprint layer.
- [University-owned apartment permits — UCSB Transportation & Parking Services](https://tap.ucsb.edu/parking-permits/student/university-owned-apartments-epermits): identifies El Dorado, San Clemente, San Joaquin, Santa Ynez, Sierra Madre, Westgate, Storke Family and West Campus housing. Only structures already present in this model are reclassified; no new remote buildings are added.
- [West Campus Point — Campus Housing](https://www.housing.ucsb.edu/housing-options/options-filter/west-campus-point): faculty condominiums on university ground leases. They are included as campus housing; this does **not** assert that the university owns every individual condominium.
- [Tropicana portfolio — UCSB Current](https://news.ucsb.edu/2015/015764/tropicana-be-integrated-university-student-housing): identifies Tropicana Gardens, Del Norte and Villas as the university-acquired housing portfolio. Independent management does not make these ordinary neighboring private residences in this display.
- [Orfalea Family Children's Center — UCSB](https://childrenscenter.sa.ucsb.edu/programs-curriculum/ofcc): the university's West Campus childcare facility.
- [Portola Dining Commons — UCSB](https://dining.ucsb.edu/dining-commons/portola-dining-commons) and [West Campus visitor accommodation](https://conferences.ucsb.edu/accommodations/visitors/overview) support the associated dining and campus accommodation facilities.
- Other matches use the retained [UCSB Buildings2026 layer](https://services1.arcgis.com/4TXrdeWh0RyCqPgB/ArcGIS/rest/services/Buildings2026/FeatureServer/0), with at least 65% footprint overlap. The audit retains the matching source ID where this is the inclusion basis. Shared campus/community facilities in that official layer are included as campus facilities, without making a legal ownership claim.

## Rules and outputs

`scripts/campus_affiliation.py` applies the verified facility list, explicit university-housing area list and official footprint overlap. An OSM `building=university` tag, a UCSB email address, a student tenant, or the word “university” in an independent organization's name is insufficient. Private shops, churches, fraternities, student co-ops and unrelated apartments remain neighboring areas unless independently verified.

The result moves **263 mapped structures** from the surrounding context into Campus: **438 campus structures** and **1,199 neighboring structures**, with the existing total of 1,637 mapped building layers unchanged. These are model structure/layer counts, not certified counts of occupied buildings or housing units. Campus membership and its primary-source URL are recorded in `output/campus_affiliation_audit.json` and `output/campus_extension_records.json`.

Campus members appear in the normal building list, count toward campus visibility, and have no ⁺ name prefix. Their building meshes and object codes remain stable. Campus and Plan overview framing includes the modeled extensions; the initial core view is retained.

`Campus_Extensions_Environment` keeps the verified sites' closed ground, level building pads, entrances, adjoining mapped campus lots, paths and planting visible when `⁺Campus neighboring areas` is unchecked. Public mapped housing envelopes and modest display aprons supply readable ground context. They are visualization boundaries, **not cadastral parcels or a property-title survey**. Ground and terrain are divided into separately closed pieces at these boundaries, preserving low-angle occlusion.

`Environment` remains the original core-campus landscape and ocean, while `Neighboring_Environment` contains the independently switchable non-campus context. All three remain controllable with the overall Landscape switch.
