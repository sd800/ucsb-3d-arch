import {TextureLoader,LinearFilter,ClampToEdgeWrapping} from 'three';
/** Precomputed distances avoid expensive shoreline processing in the browser. */
export async function prepareCoastalWater(data){
 const load=async field=>{const texture=await new TextureLoader().loadAsync(field.image);texture.minFilter=texture.magFilter=LinearFilter;texture.wrapS=texture.wrapT=ClampToEdgeWrapping;texture.generateMipmaps=false;return {texture,bounds:field.bounds};};
 return {ocean:await load(data.coastField),lagoon:await load(data.lagoonField)};
}
// Share the exact horizontal color and fade for the skin, top cap and side walls.
// A common radial fade also makes every outer domain wall meet the background.
const waterColorGLSL=/* glsl */`
vec3 waterTopColor(float shoreDistance,bool lagoon){
 if(lagoon)return mix(vec3(.48,.63,.55),vec3(.30,.51,.53),smoothstep(0.0,45.0,shoreDistance));
 vec3 color=mix(vec3(.53,.73,.75),vec3(.30,.57,.67),smoothstep(0.0,110.0,shoreDistance));
 return mix(color,vec3(.19,.43,.58),smoothstep(90.0,650.0,shoreDistance));
}
float oceanFade(float shoreDistance,vec2 xy){
 return max(smoothstep(220.0,1100.0,shoreDistance),smoothstep(2000.0,3300.0,length(xy-vec2(170.0,-350.0))));
}
vec3 waterBackground(){return vec3(.9137255,.9254902,.8901961);}
`;
/** Continuous, static shallows/deep-water/haze; no animated noise or alpha sorting. */
export function styleCoastalWater(material,fields){
 if(!['Ocean','Foam','Water'].includes(material.name))return;
 const lagoon=material.name==='Water',foam=material.name==='Foam',field=lagoon?fields.lagoon:fields.ocean;
 material.onBeforeCompile=function(shader){
  shader.uniforms.shoreField={value:field.texture};shader.uniforms.shoreBounds={value:field.bounds};
  shader.vertexShader='varying vec2 vSeaXY;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <worldpos_vertex>','#include <worldpos_vertex>\nvSeaXY=(modelMatrix*vec4(transformed,1.0)).xy;');
  shader.fragmentShader='varying vec2 vSeaXY;\nuniform sampler2D shoreField;\nuniform vec4 shoreBounds;\n'+waterColorGLSL+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <colorspace_fragment>',`#include <colorspace_fragment>
   vec2 fieldUV=clamp((vSeaXY-shoreBounds.xy)/shoreBounds.zw,0.0,1.0);
   vec2 encoded=texture2D(shoreField,fieldUV).rg;
   float shoreDistance=dot(encoded,vec2(65280.0,255.0))*0.1;
   vec3 seaColor=waterTopColor(shoreDistance,${lagoon?'true':'false'});
   ${foam?'float wave=smoothstep(.30,.78,.5+.5*sin(vSeaXY.x*.045+sin(vSeaXY.y*.03)*2.0));seaColor=mix(seaColor,vec3(.89,.94,.91),wave*.55);':''}
   ${lagoon?'':'seaColor=mix(seaColor,waterBackground(),oceanFade(shoreDistance,vSeaXY));'}
   gl_FragColor.rgb=seaColor;
  `);
 };
 material.customProgramCacheKey=()=> 'ucsb-shore-distance-v3-'+material.name;
}

/** Closed water depth joins the skin and fades downward at a level angle. */
export function styleWaterDepth(material,fields){
 const lagoon=material.name==='LagoonDepth',field=lagoon?fields.lagoon:fields.ocean;material.depthWrite=true;material.depthTest=true;
 material.onBeforeCompile=function(shader){
  shader.uniforms.depthShoreField={value:field.texture};shader.uniforms.depthShoreBounds={value:field.bounds};
  shader.vertexShader='varying vec3 vDepthWorld;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <worldpos_vertex>','#include <worldpos_vertex>\nvDepthWorld=(modelMatrix*vec4(transformed,1.0)).xyz;');
  shader.fragmentShader='varying vec3 vDepthWorld;\nuniform sampler2D depthShoreField;\nuniform vec4 depthShoreBounds;\n'+waterColorGLSL+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <colorspace_fragment>',`#include <colorspace_fragment>
   float depth=max(0.0,${lagoon?'.805':'.055'}-vDepthWorld.z);
   vec2 uv=clamp((vDepthWorld.xy-depthShoreBounds.xy)/depthShoreBounds.zw,0.0,1.0);
   vec2 encoded=texture2D(depthShoreField,uv).rg;
   float offshore=dot(encoded,vec2(65280.0,255.0))*.1;
   vec3 top=waterTopColor(offshore,${lagoon?'true':'false'});
   vec3 deep=${lagoon?'vec3(.15,.29,.29)':'vec3(.17,.31,.42)'};
   vec3 color=mix(top,deep,smoothstep(0.0,${lagoon?'5.0':'10.0'},depth));
   float edgeFade=${lagoon?'0.0':'oceanFade(offshore,vDepthWorld.xy)'};
   float downward=smoothstep(${lagoon?'6.0,10.5':'13.0,24.0'},depth);
   gl_FragColor.rgb=mix(color,waterBackground(),max(edgeFade,downward));
  `);
 };
 material.customProgramCacheKey=()=>lagoon?'lagoon-depth-v2':'ocean-depth-v2';material.needsUpdate=true;
}
