# Web model transport

The browser downloads `assets/campus-model.bin`, a gzip stream of losslessly encoded 3DS vertex and index sequences. Meshoptimizer is used without quantization, reordering or geometry simplification. Non-geometry chunks, material groups and flags are retained. Exact original CAD bytes are recoverable and checked by SHA-256.

One worker inflates bounded blocks, restores CAD and parses geometry. Compressed input and typed geometry arrays are transferred rather than copied between threads. Scene preparation yields to the browser. The fallback parser cooperatively yields between objects. Loading reports download, unpack, parse and scene progress. Offline editions use the identical compressed bytes.

`output/web_model_report.json` records original and transferred sizes and integrity hashes. Run `npm run check:compression` for geometry and original-byte integrity. Downloadable Rhino and 3DS remain unchanged.
