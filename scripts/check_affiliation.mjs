/** Campus membership must survive hiding the independent surrounding context. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync}from'node:fs';
import{createHash}from'node:crypto';
const root=new URL('../',import.meta.url),read=file=>JSON.parse(readFileSync(new URL(file,root),'utf8'));
const data=JSON.parse(readFileSync(new URL('index.html',root),'utf8').match(/<script id="campus-data"[^>]*>(.*?)<\/script>/s)[1]);
const promoted=read('output/campus_extension_records.json'),audit=read('output/campus_affiliation_audit.json'),summary=read('output/model_summary.json');
assert.equal(promoted.length,audit.buildings.length);assert.equal(promoted.length,summary.campus_extension_buildings);
assert.equal(data.records.length,summary.buildings);assert.equal(data.neighbors.length,summary.neighbor_buildings);
assert.equal(new Set([...data.records,...data.neighbors].map(r=>r.code)).size,data.records.length+data.neighbors.length);
for(const name of ['Embarcadero Hall','Isla Vista Theater','Pardall Center']){
 const record=data.records.find(r=>r.name===name);assert.ok(record,'Verified facility is in Campus: '+name);assert.equal(Boolean(record.neighbor),false);assert.ok(record.campus_affiliation.source.startsWith('https://'));assert.ok(!data.neighbors.some(r=>r.code===record.code));
}
for(const name of ['Zeta Beta Tau','Santa Barbara Hillel'])assert.ok(data.neighbors.some(r=>r.name===name&&r.neighbor),'Independent student/community facility stays in neighboring areas: '+name);
for(const r of promoted){assert.ok(data.records.some(x=>x.code===r.code&&!x.neighbor));assert.ok(data.groundPads.some(p=>p.code===r.code));assert.ok(!data.neighborPads.some(p=>p.code===r.code));}
const grounds=Object.values(data.layers).filter(r=>r.category==='campus-environment');assert.ok(grounds.length);assert.ok(grounds.every(r=>r.layer==='Campus_Extensions_Environment'));
const result={release:readFileSync(new URL('VERSION',root),'utf8').trim(),campus_buildings:data.records.length,campus_extensions:promoted.length,neighbor_buildings:data.neighbors.length,retained_campus_ground_objects:grounds.length,positive_facilities:['Embarcadero Hall','Isla Vista Theater','Pardall Center'],independent_context_controls:['Zeta Beta Tau','Santa Barbara Hillel'],passed:true};
if(process.argv[2]){
 const before=JSON.parse(readFileSync(process.argv[2],'utf8')),b=readFileSync(new URL('output/UCSB_MainCampus.3ds',root)),after={};
 function walk(start,end){for(let p=start;p+6<=end;){const id=b.readUInt16LE(p),len=b.readUInt32LE(p+2);assert.ok(len>=6&&p+len<=end);if(id===0x4000){let stop=p+6;while(b[stop])stop++;const name=b.toString('ascii',p+6,stop);if(/^[SN]\d/.test(name))after[name]=createHash('sha256').update(b.subarray(p,p+len)).digest('hex');}else if(id===0x4d4d||id===0x3d3d)walk(p+6,p+len);p+=len;}}
 walk(0,b.length);assert.deepEqual(after,before,'Reclassification preserves every existing building object byte-for-byte');result.building_geometry={objects:Object.keys(after).length,all_unchanged:true};
}
writeFileSync(new URL('output/campus_classification_validation.json',root),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
