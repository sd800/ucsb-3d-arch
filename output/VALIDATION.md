# Validation

## 26.10.18.5 — GLB / FBX / 3DM delivery

- Native GLB: 5865 mesh objects, 4912816 triangles. Khronos glTF Validator: no errors or warnings on the extension-free download.
- Every native FBX vertex and triangle index matches the corresponding GLB object; meter units, Z-up settings and face normals verified. UChicago also imports with the independent Three.js FBXLoader.
- Web GLB accessor bytes match the native GLB after lossless meshopt/gzip decoding. HTTP, local classic-script and standalone data integrity checks pass.
- Guide lists 3DM, FBX and GLB in order; every linked artifact exists and fits the hosting per-file limit. Oversized native files use lossless XZ archives.
- All 93 regional GLB assets pass index, feature-ID, overview directory, hash, local-script and unchanged mobile/desktop-budget checks.

Earlier verification entries below describe their historical model versions.

