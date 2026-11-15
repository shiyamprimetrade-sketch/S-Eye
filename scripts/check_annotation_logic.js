// Trusted editor logic only: no browser, DOM renderer, network, or file URL load.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const input = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const cases = [];
for (const [viewport, source, preview] of [[1100,[500,300],[500,300]],[390,[500,300],[500,300]],[390,[1200,800],[800,533]]]) {
  const downloads=[]; const blobs=new Map(); const pendingLoads=[];
  const element=()=>({value:'',textContent:'',children:[],events:{},appendChild(o){this.children.push(o);if(this.value==='')this.value=o.value;},addEventListener(n,f){this.events[n]=f;}});
  const elements={image:element(),class:element(),status:element(),undo:element(),download:element()};
  const drawing={clearRect(){},drawImage(){},strokeRect(){},fillText(){}};
  const width=Math.min(preview[0],viewport-50),height=width*preview[1]/preview[0];
  const canvas={...element(),clientLeft:1,clientTop:1,width:0,height:0,getContext(){return drawing;},setPointerCapture(){},getBoundingClientRect(){return {left:24,top:300,width:width+2,height:height+2};}};
  elements.canvas=canvas;
  class Bitmap {constructor(){this.naturalWidth=preview[0];this.naturalHeight=preview[1];}set src(value){pendingLoads.push(()=>{if(this.onload)this.onload();});}}
  class LocalBlob {constructor(parts){this.parts=parts;}}
  const data=JSON.parse(JSON.stringify(input.initial));data.images[0].source_size=source;
  const sandbox={INITIAL:data,PREVIEWS:['data:fixture'],LABELS:input.labels,Image:Bitmap,Blob:LocalBlob,
    document:{getElementById(id){return elements[id];},createElement(name){if(name==='a')return {click(){downloads.push(blobs.get(this.href).parts.join(''));}};return element();}},
    URL:{createObjectURL(blob){const key='blob:'+blobs.size;blobs.set(key,blob);return key;},revokeObjectURL(){}},setTimeout(){},console};
  vm.createContext(sandbox);new vm.Script(input.script).runInContext(sandbox,{timeout:2000});
  canvas.events.pointerdown({clientX:30,clientY:310,pointerId:1});canvas.events.pointerup({clientX:100,clientY:370,pointerId:1});
  elements.download.events.click();assert.equal(JSON.parse(downloads.pop()).images[0].instances.length,0);
  pendingLoads.splice(0).forEach(load=>load());
  elements.class.value='quadrilateral';
  function point(x,y){return {clientX:25+x*width,clientY:301+y*height,pointerId:1};}
  canvas.events.pointerdown(point(.1,.2));canvas.events.pointermove(point(.6,.7));canvas.events.pointerup(point(.6,.7));
  elements.download.events.click();
  const draft=JSON.parse(downloads.pop());const box=draft.images[0].instances[0].box;
  const expected=[source[0]*.1,source[1]*.2,source[0]*.6,source[1]*.7];
  const error=Math.max(...box.map((v,i)=>Math.abs(v-expected[i])));
  assert(error<=.02);assert.equal(draft.template_unscored,true);assert.equal(draft.images[0].annotation_status,'draft');assert.equal(draft.images[0].instances[0].class,'quadrilateral');
  elements.undo.events.click();elements.download.events.click();const undone=JSON.parse(downloads.pop());assert.equal(undone.images[0].instances.length,0);
  cases.push({simulated_viewport_width:viewport,source_size:source,preview_size:preview,source_box:box,maximum_coordinate_error_pixels:error,downloaded_boxes:1,undo_boxes:0,drawing_ignored_before_preview_load:true,unscored:true});
}
console.log(JSON.stringify({format:'seye-editor-logic-verification-v1',cases,browser_rendering_verified:false,scope:'Node VM with test doubles for canvas/elements/Blob; no browser UI or horizontal-layout validation',passed:true}));
