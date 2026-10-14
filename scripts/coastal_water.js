import {TextureLoader,LinearFilter,ClampToEdgeWrapping} from 'three';
/** Precomputed distances avoid expensive shoreline processing in the browser. */
export async function prepareCoastalWater(data){
 const load=async field=>{const texture=await new TextureLoader().loadAsync(field.image);texture.minFilter=texture.magFilter=LinearFilter;texture.wrapS=texture.wrapT=ClampToEdgeWrapping;texture.generateMipmaps=false;return {texture,bounds:field.bounds};};
 return {ocean:await load(data.coastField),lagoon:await load(data.lagoonField)};
}
/** Continuous, static shallows/deep-water/haze; no animated noise or alpha sorting. */
export function styleCoastalWater(material,fields){
 if(!['Ocean','Foam','Water'].includes(material.name))return;
 const lagoon=material.name==='Water',foam=material.name==='Foam',field=lagoon?fields.lagoon:fields.ocean;
 material.onBeforeCompile=function(shader){
  shader.uniforms.shoreField={value:field.texture};shader.uniforms.shoreBounds={value:field.bounds};
  shader.vertexShader='varying vec2 vSeaXY;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <worldpos_vertex>','#include <worldpos_vertex>\nvSeaXY=(modelMatrix*vec4(transformed,1.0)).xy;');
  shader.fragmentShader='varying vec2 vSeaXY;\nuniform sampler2D shoreField;\nuniform vec4 shoreBounds;\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <colorspace_fragment>',`#include <colorspace_fragment>
   vec2 fieldUV=clamp((vSeaXY-shoreBounds.xy)/shoreBounds.zw,0.0,1.0);
   vec2 encoded=texture2D(shoreField,fieldUV).rg;
   float shoreDistance=dot(encoded,vec2(65280.0,255.0))*0.1;
   ${lagoon?`
   vec3 seaColor=mix(vec3(.48,.63,.55),vec3(.30,.51,.53),smoothstep(0.0,45.0,shoreDistance));
   `:`
   vec3 seaColor=mix(vec3(.53,.73,.75),vec3(.30,.57,.67),smoothstep(0.0,110.0,shoreDistance));
   seaColor=mix(seaColor,vec3(.19,.43,.58),smoothstep(90.0,650.0,shoreDistance));
   float haze=max(smoothstep(220.0,1100.0,shoreDistance),smoothstep(2000.0,3300.0,length(vSeaXY-vec2(170.0,-350.0))));
   ${foam?'float wave=smoothstep(.30,.78,.5+.5*sin(vSeaXY.x*.045+sin(vSeaXY.y*.03)*2.0));seaColor=mix(seaColor,vec3(.89,.94,.91),wave*.55);':''}
   seaColor=mix(seaColor,vec3(.9137255,.9254902,.8901961),haze);
   `}
   gl_FragColor.rgb=seaColor;
  `);
 };
 material.customProgramCacheKey=()=> 'ucsb-shore-distance-v2-'+material.name;
}
