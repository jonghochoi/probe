const {chromium}=require('playwright');const fs=require('fs');
const L=[
 ['hub','요약','중심 주장 카드','2610.16308','glance','.g-hub'],
 ['narr','요약','이야기 + 조건 칸','2610.16308','glance','.g-narr'],
 ['acts','요약','근거 카드 넷','2610.16308','glance','.g-acts'],
 ['key','상세','핵심 상자 (key)','2610.16308','full','.callout.co-key'],
 ['warn','상세','주의 상자 (warn)','2610.16308','full','.callout.co-warn'],
 ['ten','상세','긴장 상자 (ten)','2610.16308','full','.callout.co-ten'],
 ['ctx','상세','맥락 상자 (ctx)','2610.16308','full','.callout.co-ctx'],
 ['win','상세','성과 상자 (win)','2606.15768','full','.callout.co-win'],
 ['quiz','상세','확인 문제 (펼친 상태)','2610.16308','full','.quiz','open'],
 ['term','상세','용어 풀이 (펼친 상태)','2610.16308','full','.tdef','term'],
 ['split','상세','나란히 카드','2610.16308','full','.split'],
 ['lineage','상세','계보','2610.16308','full','.lineage'],
 ['scale','상세','막대표','2610.16308','full','.article .scale'],
 ['parts','상세','부품 표','2610.16308','full','.parts'],
 ['flow','상세','흐름도','2412.10345','full','.flow'],
 ['table','상세','표','2610.16308','full','.article .table-wrap'],
 ['fold','상세','접은 상자 (펼친 상태)','2610.16308','full','details.fold','open'],
 ['code','상세','코드','2610.16308','full','.article .code'],
 ['rel','상세','같은 갈래의 다른 글','2610.16308','full','.related'],
];
(async()=>{const b=await chromium.launch();
for(const dark of [false,true]){
const p=await b.newPage({viewport:{width:1280,height:900},colorScheme:dark?'dark':'light'});
const meta=[];
for(const [k,tab,name,id,t,sel,act] of L){
 await p.goto(`http://localhost:8766/p/${id}/index.html${t==='full'?'#full':''}`);await p.waitForTimeout(250);
 await p.addStyleTag({url:'/assets/plcard.css'});
 await p.evaluate(([sel,act])=>{const e=document.querySelector(sel);if(!e)return;
   if(act==='open'){e.open=true;}
   if(act==='term'){const r=document.querySelector('.tref');r.click();}
   (act==='term'?document.querySelector('.tdef'):e).scrollIntoView({block:'center'});
   const st=document.createElement('style');st.textContent='.site-nav,.tabs-wrap,.actstrip,.mark-fab,.memo-fab,.read-prog{visibility:hidden!important}';document.head.appendChild(st);},[sel,act]);
 await p.waitForTimeout(1200);
 for(const v of ['now','a','b','c']){
  await p.evaluate(v=>{if(v==='now')document.documentElement.removeAttribute('data-pc');else document.documentElement.setAttribute('data-pc',v);},v);
  await p.waitForTimeout(120);
  const bb=await p.evaluate(sel=>{const e=document.querySelector(sel);const r=e.getBoundingClientRect();return {x:r.left+scrollX,y:r.top+scrollY,w:r.width,h:r.height}},act==='term'?'.tdef':sel);
  const pad=14;const clip={x:Math.max(0,bb.x-pad),y:Math.max(0,bb.y-pad),width:Math.min(1265,bb.w+2*pad),height:Math.min(1400,bb.h+2*pad)};
  await p.screenshot({path:`gal/img/${k}-${v}${dark?'-d':''}.png`,clip,fullPage:true});
 }
 meta.push({k,tab,name});
}
if(!dark) fs.writeFileSync('gal/meta.json',JSON.stringify(meta));
await p.close();}
await b.close();})();
