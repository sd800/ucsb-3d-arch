/** Test architectural voids and courtyard grades in the actual exported CAD. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {BufferGeometry,Float32BufferAttribute,Mesh,MeshBasicMaterial,Raycaster,Vector3,DoubleSide,BoxGeometry} from 'three';
import {prepareBuildingRoofs} from './surface_rendering.js';
import {groundHeight} from './ground_height.js';
const root=new URL('../',import.meta.url),read=p=>JSON.parse(fs.readFileSync(new URL(p,root),'utf8'));
const records=read('output/viewer_records.json'),tower=records.find(r=>r.facility_id==='353'),media=records.find(r=>r.facility_id==='354');
const report=read('output/storke_architecture.json'),layers=read('output/layer_map.json'),bytes=fs.readFileSync(new URL('output/UCSB_MainCampus.3ds',root));
const groups={walls:[],bells:[],context:[],media:[]};
function chunks(a,z,meta){
 for(let at=a;at<z;){const tag=bytes.readUInt16LE(at),n=bytes.readUInt32LE(at+2),end=at+n;assert(n>=6&&end<=z);
  if(tag===0x4d4d||tag===0x3d3d)chunks(at+6,end);
  if(tag===0x4000){const zero=bytes.indexOf(0,at+6),name=bytes.toString('ascii',at+6,zero);chunks(zero+1,end,{name,...layers[name]});}
  if(tag===0x4100&&meta){
   const owned=meta.layer===tower.layer||meta.layer===media.layer;
   const context=meta.layer==='Environment'&&['Ground','StorkePaving','StorkeConcrete','StorkePale','StorkeWater'].includes(meta.material);
   if(owned||context){let v,f;
    for(let k=at+6;k<end;){const t=bytes.readUInt16LE(k),s=bytes.readUInt32LE(k+2);
     if(t===0x4110){const count=bytes.readUInt16LE(k+6);v=new Float32Array(count*3);for(let i=0;i<v.length;i++)v[i]=bytes.readFloatLE(k+8+i*4);}
     if(t===0x4120){const count=bytes.readUInt16LE(k+6);f=[];for(let i=0;i<count;i++)f.push(bytes.readUInt16LE(k+8+i*8),bytes.readUInt16LE(k+10+i*8),bytes.readUInt16LE(k+12+i*8));}
     k+=s;
    }
    if(context){const selected=[];for(let i=0;i<f.length;i+=3){const ids=f.slice(i,i+3),xs=ids.map(id=>v[id*3]),ys=ids.map(id=>v[id*3+1]);if(Math.max(...xs)>=-92&&Math.min(...xs)<=-35&&Math.max(...ys)>=-163&&Math.min(...ys)<=-78)selected.push(...ids);}f=selected;}
    if(f.length){const geometry=new BufferGeometry();geometry.setAttribute('position',new Float32BufferAttribute(v,3));geometry.setIndex(f);const mesh=new Mesh(geometry,new MeshBasicMaterial({name:meta.material,side:DoubleSide}));mesh.updateMatrixWorld(true);
     if(context)groups.context.push(mesh);else if(meta.layer===media.layer)groups.media.push(mesh);else if(meta.material==='StorkeConcrete')groups.walls.push(mesh);else if(meta.material==='BellMetal')groups.bells.push(mesh);
    }
   }
  }
  at=end;
 }
}
chunks(0,bytes.length);
assert(groups.walls.length&&groups.bells.length&&groups.media.length);
const center=new Vector3(...tower.center,tower.ground_m),checks=[];
const ray=(objects,point,direction,far)=>new Raycaster(point,direction.clone().normalize(),0,far).intersectObjects(objects,false);
function expectWall(normal,offset,z,hit,label){
 const n=new Vector3(...normal,0),t=new Vector3(-normal[1],normal[0],0),depth=Math.abs(normal[0])>.8?report.footprint_m[0]:report.footprint_m[1];
 const origin=center.clone().addScaledVector(n,depth/2+2).addScaledVector(t,offset);origin.z+=z;
 const hits=ray(groups.walls,origin,n.clone().negate(),2.55);
 assert.equal(hits.length>0,hit,label);checks.push(label);
}
const faces=report.belfry_openings.filter(x=>x.center_offset===0);
for(const face of faces){
 const openings=report.belfry_openings.filter(x=>x.face_normal.every((n,i)=>Math.abs(n-face.face_normal[i])<1e-9)).sort((a,b)=>a.center_offset-b.center_offset);
 expectWall(face.face_normal,0,28,true,'Closed middle shaft '+face.face_normal);
 expectWall(face.face_normal,0,1.5,false,'True base arch '+face.face_normal);
 for(const opening of openings){
  expectWall(opening.face_normal,opening.center_offset,report.belfry_sill_m+4.4,false,'Long belfry opening '+opening.center_offset+' '+opening.face_normal);
  expectWall(opening.face_normal,opening.center_offset,opening.spring_m+opening.width_m/2-.08,false,'Round arch crown void '+opening.center_offset+' '+opening.face_normal);
  expectWall(opening.face_normal,opening.center_offset+opening.width_m*.46,opening.spring_m+opening.width_m/2-.08,true,'Solid shoulder beside arch crown '+opening.center_offset+' '+opening.face_normal);
 }
 for(let i=0;i<2;i++)expectWall(face.face_normal,(openings[i].center_offset+openings[i+1].center_offset)/2,report.belfry_sill_m+4.4,true,'Concrete pier between slots '+i+' '+face.face_normal);
}
// Probe the actual sloping media frontage: each opening must stay void while
// the intervening concrete and both end piers support the roof walk.
const endA=new Vector3(-87.462550,-108.455953,0),endB=new Vector3(-40.534248,-109.816941,0),axis=endB.clone().sub(endA).normalize(),normal=new Vector3(axis.y,-axis.x,0),mid=endA.clone().add(endB).multiplyScalar(.5),length=endA.distanceTo(endB),bayCount=report.publications.south_arcade_bays,bay=length/bayCount;
for(let i=0;i<bayCount;i++){
 const at=mid.clone().addScaledVector(axis,-length/2+bay*(i+.5)).addScaledVector(normal,.8);at.z=report.plaza.lower_court_m+1;
 assert.equal(ray(groups.media,at,normal.clone().negate(),1.4).length,0,'Open media arcade bay '+i);checks.push('Open media arcade bay '+i);
}
for(let i=0;i<=bayCount;i++){
 const at=mid.clone().addScaledVector(axis,-length/2+bay*i+(i===0?.1:i===bayCount?-.1:0)).addScaledVector(normal,.8);at.z=report.plaza.lower_court_m+1;
 assert(ray(groups.media,at,normal.clone().negate(),1.4).length>0,'Supported media arcade pier '+i);checks.push('Supported media arcade pier '+i);
}
assert.equal(report.belfry_openings.length,12);assert.equal(report.bells,61);assert.equal(report.clock_faces,0);
assert(Math.abs(tower.peak_m-tower.ground_m-53.34)<.012,'Published height retained');
assert(Math.abs(media.ground_m-report.plaza.lower_court_m)<.001);
const floor=report.plaza.lower_court_m,upper=report.plaza.upper_walk_m;
for(const [x,y,height,name] of [[-44,-130,floor+.098,'Lower court'],[-65,-135,floor-.385,'Pool surface'],[-75.4,-92.9,upper,'Tower upper pad']]){
 const surfaces=groups.context.filter(m=>name==='Tower upper pad'?m.material.name==='Ground':true);
 const hits=ray(surfaces,new Vector3(x,y,80),new Vector3(0,0,-1),100);
 assert(hits.length,name+' has a closed supporting surface');assert(Math.abs(hits[0].point.z-height)<.02,`${name} is at its intended grade: ${hits[0].point.z} vs ${height}`);checks.push(name+' grade');
}
assert.equal(report.plaza.stair_pads.length,32);
for(const flight of [report.plaza.stair_pads.slice(0,16),report.plaza.stair_pads.slice(16)]){
 assert(Math.abs(flight.at(-1).height-upper)<1e-6,'Last stair meets upper landing');
 for(let i=0;i<flight.length;i++){assert(Math.abs(flight[i].height-(floor+(i+1)*2.7/16))<1e-6);const [a,b,c,d]=flight[i].bounds;const p=new Vector3((a+c)/2,(b+d)/2,80),hits=ray(groups.context,p,new Vector3(0,0,-1),100);assert(Math.abs(hits[0].point.z-flight[i].height)<.02,`Tread ${flight[i].code} at ${p.toArray()} is ${hits[0].point.z} (${hits[0].object.material.name}), expected ${flight[i].height}`);}
}
checks.push('Both flights meet lower/upper landings without terrain crossing');
const material=new MeshBasicMaterial({name:'StorkeConcrete'}),probe=new Mesh(new BoxGeometry(2,2,54),material);probe.position.z=30;
assert(prepareBuildingRoofs(probe,0,false,true).every(m=>!m.material.userData.campusRoof),'Concrete cap keeps the tower concrete color');
const html=fs.readFileSync(new URL('index.html',root),'utf8'),data=JSON.parse(html.match(/<script id="campus-data"[^>]*>(.*?)<\/script>/s)[1]);
assert(Math.abs(groundHeight(data,-44,-130)-floor)<.001);
const places=data.places.filter(p=>p.name==='Storke Plaza');assert.equal(places.length,1);assert.equal(new Set(data.places.map(p=>p.id)).size,data.places.length);assert(Math.abs(places[0].position[2]-floor-.7)<.015);
const result={published_height_m:53.34,real_belfry_slots:12,base_arches:4,bronze_bells:61,checks:checks.length,sunken_court_depth_m:2.7,stairs:32,passed:true};
fs.writeFileSync(new URL('output/storke_validation.json',root),JSON.stringify(result,null,2)+'\n');console.log(result);
