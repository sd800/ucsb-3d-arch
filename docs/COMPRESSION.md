# Web model delivery

Initial browsing transfers the unchanged campus geometry in a **14.46 MB** lossless stream plus a **3.23 MB** lightweight neighboring-area overview. Regional LOD applies only to Isla Vista and campus neighboring areas. Campus buildings, lagoon, coastline and ocean retain the existing full campus renderer.

Nearby context packets load within bounded geometry budgets and are released when no longer needed. The campus-only stream restores original campus object bytes exactly; neighboring overview geometry is a simplified visual derivative. The complete lossless CAD web stream is 21.63 MB for the current 103.80 MB 3DS. Full CAD downloads remain separate, including the adjacent `.3ds.gz` archive for the standalone edition. See `docs/REGIONAL_RENDERING.md`, `output/streaming_model_report.json` and `output/web_model_report.json` for scope, limits, exact sizes and digests.

HTTP uses binary assets. Local double-click editions load classic-script assets; standalone HTML embeds its compressed browsing data. Parsing/decompression is cooperative or worker-based where appropriate. Geometry, framebuffers and browser storage remain additional memory costs.
