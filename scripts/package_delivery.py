"""Package portable files without Finder metadata, dependencies or build caches."""
from pathlib import Path
import zipfile
r=Path(__file__).resolve().parents[1];out=r/'output';ignored={'.git','node_modules','tmp','__pycache__','.venv'}
files=[p for p in r.rglob('*')if p.is_file()and p.name!='.DS_Store'and not p.name.startswith('._')and not any(a in ignored for a in p.relative_to(r).parts)and p.suffix not in ['.zip','.npz','.xml']and not p.name.endswith(('_catalog.json','_layer.json','_page.html'))]
p=out/'UCSB_MainCampus_Delivery.zip'
with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for f in sorted(files):z.write(f,f.relative_to(r))
with zipfile.ZipFile(p)as z:assert z.testzip()is None;assert all(n.isascii()for n in z.namelist());assert 'output/UCSB_Campus_Offline.html'in z.namelist()
print('Portable delivery:',len(files),'files,',p.stat().st_size,'bytes')
