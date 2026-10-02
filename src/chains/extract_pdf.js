// 1) PDF を開いたタブで実行：文字と座標を window.__IT に入れる
const r=await fetch(location.href);
const pdfjs=await import('https://cdn.jsdelivr.net/npm/pdfjs-dist@4/build/pdf.min.mjs');pdfjs.GlobalWorkerOptions.workerSrc='https://cdn.jsdelivr.net/npm/pdfjs-dist@4/build/pdf.worker.min.mjs';
const doc=await pdfjs.getDocument({data:await r.arrayBuffer(),cMapUrl:'https://cdn.jsdelivr.net/npm/pdfjs-dist@4/cmaps/',cMapPacked:true}).promise;
const items=[];for(let p=1;p<=doc.numPages;p++){const pg=await doc.getPage(p);const tc=await pg.getTextContent();tc.items.forEach(it=>{if(it.str.trim())items.push({p,x:Math.round(it.transform[4]),y:Math.round(it.transform[5]*10)/10,s:it.str.trim()})})}
window.__IT=items;

// 2) 表に組み立てる。opt：lx＝メニュー名の列のx範囲、sx＝サイズの列のx範囲、nx＝数値の列の始まり、nc＝数値の列数
window.__PARSE=function(ID,items,opt){opt=opt||{};const LX=opt.lx||[95,205],SX=opt.sx||[205,280],NX=opt.nx||280,NC=opt.nc||5;const isNum=s=>/^-?\d+(\.\d+)?$/.test(s);
const out=[],anom=[];const np=Math.max(...items.map(i=>i.p));
for(let p=1;p<=np;p++){const its=items.filter(i=>i.p===p);
 const rowsM={};its.filter(i=>i.x>=NX&&isNum(i.s)).forEach(i=>{const k=Object.keys(rowsM).find(k=>Math.abs(k-i.y)<2)||i.y;(rowsM[k]=rowsM[k]||[]).push(i)});
 const rows=Object.keys(rowsM).map(k=>({y:+k,n:rowsM[k].sort((a,b)=>a.x-b.x).map(i=>i.s)})).sort((a,b)=>b.y-a.y);if(!rows.length)continue;
 rows.forEach(r=>{const sz=its.filter(i=>i.x>=SX[0]&&i.x<SX[1]&&Math.abs(i.y-r.y)<3&&!/サイズ/.test(i.s));r.size=sz.map(i=>i.s).join('');if(r.n.length!==NC)anom.push('p'+p+' cols '+r.y+' '+r.n.join(','))});
 const raw=its.filter(i=>i.x>=LX[0]&&i.x<LX[1]&&!isNum(i.s)&&!/^(メニュー|カテゴリー)$/.test(i.s)&&i.y<rows[0].y+8).sort((a,b)=>b.y-a.y||a.x-b.x);
 const labels=[];raw.forEach(i=>{const L=labels[labels.length-1];if(L&&Math.abs(L.y-i.y)<2){L.parts.push(i)}else labels.push({y:i.y,parts:[i]})});
 labels.forEach(L=>L.s=L.parts.sort((a,b)=>a.x-b.x).map(i=>i.s).join(' '));
 let ri=0,li=0;
 while(li<labels.length&&ri<rows.length){let ok=false;
  for(let m=1;m<=3&&li+m<=labels.length&&!ok;m++){const ls=labels.slice(li,li+m),cy=ls.reduce((a,b)=>a+b.y,0)/m,exp=2*cy-rows[ri].y;
   const ei=rows.findIndex((r,k)=>k>=ri&&Math.abs(r.y-exp)<3.5);if(ei<0)continue;
   const nl=labels[li+m];if(nl&&(ei+1>=rows.length||nl.y>rows[ei+1].y+3.5))continue;if(!nl&&ei!==rows.length-1)continue;
   const name=ls.map(l=>l.s).join('');if(m>1)anom.push('merged '+name);for(let k=ri;k<=ei;k++)out.push([name,rows[k].size,...rows[k].n].join('\t'));ri=ei+1;li+=m;ok=true}
  if(!ok){anom.push('p'+p+' label '+labels[li].s+' y'+labels[li].y+' row y'+rows[ri].y);li++}}
 if(ri<rows.length)anom.push('p'+p+' unassigned rows '+(rows.length-ri));if(li<labels.length)anom.push('p'+p+' unused labels '+labels.slice(li).map(l=>l.s).join(','));
}
const sum=k=>Math.round(out.reduce((a,l)=>a+(+l.split('\t')[k]),0)*10)/10;const merged=anom.filter(a=>a.startsWith('merged '));const bad=anom.filter(a=>!a.startsWith('merged '));
const meta={n:out.length,anom:bad,sums:[2,3,4,5,6].map(sum)};window.__O='@@CHAIN '+ID+'@@\n'+JSON.stringify(meta)+'\n'+out.join('\n')+'\n@@END@@';return JSON.stringify({meta,merged})};
// 3) window.__PARSE('<id>',window.__IT) で異常がないことを見てから、window.__O を返す
