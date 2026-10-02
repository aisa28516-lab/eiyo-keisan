// チェーン店の栄養成分表を公式PDF・ページから取り出すための道具（ブラウザのページ内で import して使う）
// 使い方: const X=await import('https://aisa28516-lab.github.io/eiyo-keisan/tools/extract.mjs'); await X.load(url)
const CDN='https://cdn.jsdelivr.net/npm/pdfjs-dist@4/';
let pdfjs,doc;
export const num=s=>String(s).replace(/,/g,'');
export const isNum=s=>/^-?\d+(\.\d+)?$/.test(num(s));
export async function load(url){
  pdfjs=pdfjs||await import(CDN+'build/pdf.min.mjs');pdfjs.GlobalWorkerOptions.workerSrc=CDN+'build/pdf.worker.min.mjs';
  const r=await fetch(url||location.href);if(!r.ok)throw new Error('fetch '+r.status);
  doc=await pdfjs.getDocument({data:await r.arrayBuffer(),cMapUrl:CDN+'cmaps/',cMapPacked:true}).promise;
  const items=[];for(let p=1;p<=doc.numPages;p++){const pg=await doc.getPage(p);const tc=await pg.getTextContent();tc.items.forEach(it=>{if(it.str.trim())items.push({p,x:Math.round(it.transform[4]),y:Math.round(it.transform[5]*10)/10,s:it.str.trim()})})}
  window.__IT=items;return{pages:doc.numPages,items:items.length,perPage:Array.from({length:doc.numPages},(_,k)=>items.filter(i=>i.p===k+1).length)};
}
// ページの文字を行ごとに見る（確認用）
export function rows(p,a=0,b=40,f){const R={};window.__IT.filter(i=>i.p===p&&(!f||f(i))).forEach(i=>{const k=Object.keys(R).find(k=>Math.abs(k-i.y)<1.5)||i.y;(R[k]=R[k]||[]).push(i)});
  return Object.keys(R).sort((x,y)=>y-x).slice(a,b).map(y=>y+': '+R[y].sort((x,z)=>x.x-z.x).map(i=>i.x+'='+i.s).join(' | ')).join('\n')}
// 罫線（横線）を取り出す
export async function lines(pn){const pg=await doc.getPage(pn);const ol=await pg.getOperatorList();const O=pdfjs.OPS;let m=[1,0,0,1,0,0];const st=[];
  const mul=(a,b)=>[a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5]];
  const ap=(x,y)=>[m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]];const segs=[];
  for(let i=0;i<ol.fnArray.length;i++){const f=ol.fnArray[i],a=ol.argsArray[i];
    if(f===O.save)st.push(m.slice());else if(f===O.restore)m=st.pop()||m;else if(f===O.transform)m=mul(m,a);
    else if(f===O.constructPath){const ops=a[0],c=a[1];let k=0,cx=0,cy=0;for(const op of ops){
      if(op===O.moveTo){cx=c[k++];cy=c[k++]}else if(op===O.lineTo){const x=c[k++],y=c[k++];const p1=ap(cx,cy),p2=ap(x,y);segs.push([p1[0],p1[1],p2[0],p2[1]]);cx=x;cy=y}
      else if(op===O.rectangle){const x=c[k++],y=c[k++],w=c[k++],h=c[k++];const p1=ap(x,y),p2=ap(x+w,y+h);segs.push([p1[0],p1[1],p2[0],p1[1]],[p1[0],p2[1],p2[0],p2[1]],[p1[0],p1[1],p1[0],p2[1]],[p2[0],p1[1],p2[0],p2[1]])}
      else if(op===O.curveTo)k+=6;else if(op===O.curveTo2||op===O.curveTo3)k+=4}}}
  return segs.map(s=>s.map(v=>Math.round(v*10)/10))}
const bounds=(segs,x0,x1)=>{const ys=segs.filter(q=>Math.abs(q[1]-q[3])<1&&Math.min(q[0],q[2])<x1-15&&Math.max(q[0],q[2])>x0+15).map(q=>q[1]).sort((a,b)=>b-a);const bs=[];ys.forEach(y=>{if(!bs.length||bs[bs.length-1]-y>4)bs.push(y)});return bs};
function finish(ID,L,extra){const sum=k=>Math.round(L.reduce((a,l)=>a+(+l.split('\t')[k]),0)*10)/10;const dup={};L.forEach(l=>{const k=l.split('\t').slice(0,2).join('|');dup[k]=(dup[k]||0)+1});
  window.__OUT=L;const meta={n:L.length,anom:[],sums:[2,3,4,5,6].map(sum)};window.__O='@@CHAIN '+ID+'@@\n'+JSON.stringify(meta)+'\n'+L.join('\n')+'\n@@END@@';
  return JSON.stringify(Object.assign({n:L.length,dups:Object.keys(dup).filter(k=>dup[k]>1)},extra))}
// __OUT を手直ししたあとで出力を作り直す
export function emit(ID,L){return finish(ID,L,{})}
// 方式A：メニュー名が結合セルの中央にある表（座標だけで組み立てる）。o={lx,sx,nx:[from,to],pages,tol,rt,skip}
export function center(ID,o){const TOL=o.tol||3.5,RT=o.rt||2,NC=5;const out=[],anom=[],merged=[];const items=window.__IT;const pages=o.pages||[...new Set(items.map(i=>i.p))];
  for(const p of pages){const its=items.filter(i=>i.p===p&&!(o.skip&&o.skip.test(i.s)));
    const M={};its.filter(i=>i.x>=o.nx[0]&&i.x<o.nx[1]&&isNum(i.s)).forEach(i=>{const k=Object.keys(M).find(k=>Math.abs(k-i.y)<RT)||i.y;(M[k]=M[k]||[]).push(i)});
    const rs=Object.keys(M).map(k=>({y:+k,n:M[k].sort((a,b)=>a.x-b.x).map(i=>num(i.s))})).sort((a,b)=>b.y-a.y);if(!rs.length)continue;
    rs.forEach(r=>{r.size=its.filter(i=>i.x>=o.sx[0]&&i.x<o.sx[1]&&Math.abs(i.y-r.y)<TOL&&!/サイズ/.test(i.s)).sort((a,b)=>a.x-b.x).map(i=>i.s).join('');if(r.n.length!==NC)anom.push('p'+p+' cols '+r.y+' '+r.n.join(','))});
    const raw=its.filter(i=>i.x>=o.lx[0]&&i.x<o.lx[1]&&!isNum(i.s)&&!/^(メニュー|カテゴリー|商品名)$/.test(i.s)&&i.y<rs[0].y+TOL*3).sort((a,b)=>b.y-a.y||a.x-b.x);
    const labels=[];raw.forEach(i=>{const L=labels[labels.length-1];if(L&&Math.abs(L.y-i.y)<RT)L.parts.push(i);else labels.push({y:i.y,parts:[i]})});
    labels.forEach(L=>L.s=L.parts.sort((a,b)=>a.x-b.x).map(i=>i.s).join(' '));
    let ri=0,li=0;
    while(li<labels.length&&ri<rs.length){let ok=false;
      for(let m=1;m<=3&&li+m<=labels.length&&!ok;m++){const ls=labels.slice(li,li+m),cy=ls.reduce((a,b)=>a+b.y,0)/m,exp=2*cy-rs[ri].y;
        const ei=rs.findIndex((r,k)=>k>=ri&&Math.abs(r.y-exp)<TOL);if(ei<0)continue;
        const nl=labels[li+m];if(nl&&(ei+1>=rs.length||nl.y>rs[ei+1].y+TOL))continue;if(!nl&&ei!==rs.length-1)continue;
        const name=ls.map(l=>l.s).join('');if(m>1)merged.push(name);for(let k=ri;k<=ei;k++)out.push([name,rs[k].size,...rs[k].n].join('\t'));ri=ei+1;li+=m;ok=true}
      if(!ok){anom.push('p'+p+' label '+labels[li].s+' y'+labels[li].y+' row y'+rs[ri].y);li++}}
    if(ri<rs.length)anom.push('p'+p+' unassigned rows '+(rs.length-ri)+' from y'+rs[ri].y);if(li<labels.length)anom.push('p'+p+' unused labels '+labels.slice(li).map(l=>l.s).join(','))}
  return finish(ID,out,{anom,merged})}
// 方式B：罫線でメニューのセルを決める表。o={mx:[メニュー列],sx:[サイズ列],nx:[数値列],pages,tol,cols:[使う数値列の番号5つ]}
export async function grid(ID,o){const out=[],anom=[];const TOL=o.tol||9;
  for(const p of o.pages){const segs=await lines(p);const its=window.__IT.filter(i=>i.p===p);
    const bs=bounds(segs,o.mx[0],o.mx[1]),sb=o.sx?bounds(segs,o.sx[0],o.sx[1]):[];
    const M={};its.filter(i=>i.x>=o.nx[0]&&i.x<o.nx[1]&&isNum(i.s)).forEach(i=>{const k=Object.keys(M).find(k=>Math.abs(k-i.y)<(o.rt||5))||i.y;(M[k]=M[k]||[]).push(i)});
    const rs=Object.keys(M).map(k=>({y:+k,n:M[k].sort((a,b)=>a.x-b.x).map(i=>num(i.s))})).sort((a,b)=>b.y-a.y);
    rs.forEach(r=>{const bi=sb.findIndex((y,k)=>k<sb.length-1&&r.y<y&&r.y>=sb[k+1]);r.size=bi<0?'':its.filter(i=>i.x>=o.sx[0]&&i.x<o.sx[1]&&i.y<sb[bi]-2&&i.y>sb[bi+1]-2&&!/^※|含まず/.test(i.s)).sort((a,b)=>b.y-a.y||a.x-b.x).map(i=>i.s).join('');
      if(o.cols){if(r.n.length<=Math.max(...o.cols))anom.push('p'+p+' cols y'+r.y+' '+r.n.join(','));r.n=o.cols.map(c=>r.n[c])}else if(r.n.length!==5)anom.push('p'+p+' cols y'+r.y+' '+r.n.join(','))});
    const cells=[];for(let b=0;b<bs.length-1;b++){const top=bs[b],bot=bs[b+1];const cr=rs.filter(r=>r.y<top&&r.y>=bot);if(!cr.length)continue;
      const lab=its.filter(i=>i.x>=o.mx[0]&&i.x<o.mx[1]&&i.y<top-2&&i.y>bot-2&&!isNum(i.s)&&i.s.length>1).sort((a,b)=>b.y-a.y||a.x-b.x);let name=lab.map(i=>i.s).join('');const ci=name.search(/[※]/);if(ci>0)name=name.slice(0,ci);
      cells.push({rs:cr,name,ly:lab.length?lab[0].y:null})}
    let U=[],last=null;
    for(let k=0;k<cells.length;k++){const c=cells[k];if(!c.name){U.push(c);continue}
      if(/^[（(]/.test(c.name)&&last&&!U.length){last.name+=c.name;last.cs.push(c);continue}
      const firstY=(U.length?U[0]:c).rs[0].y,exp=2*c.ly-firstY;const g=U.concat([c]);U=[];
      while(k+1<cells.length&&!cells[k+1].name&&cells[k+1].rs[0].y>=exp-TOL)g.push(cells[++k]);
      const lastY=g[g.length-1].rs[g[g.length-1].rs.length-1].y;if(g.length>1&&Math.abs(lastY-exp)>TOL)anom.push('p'+p+' center '+c.name+' last '+lastY+' exp '+Math.round(exp));
      last={name:c.name,cs:g};out.push(last)}
    if(U.length)anom.push('p'+p+' leftover noname '+U.length)}
  const L=[];out.forEach(g=>g.cs.forEach(c=>c.rs.forEach(r=>L.push([g.name,r.size,...r.n].join('\t')))));
  return finish(ID,L,{anom})}
// HTMLの表：cols=[名前,kcal,たんぱく質,脂質,炭水化物,食塩] の列番号。size＝サイズ列の番号（なければ null）
export function table(ID,tables,cols,size){const L=[],anom=[];
  tables.forEach(t=>[...t.rows].forEach((r,k)=>{const c=[...r.cells].map(x=>x.innerText.trim().replace(/\s+/g,' '));if(c.length<=Math.max(...cols))return;const v=cols.slice(1).map(i=>num(c[i]));
    if(!v.every(isNum)){if(v.some(isNum))anom.push(c.join('|').slice(0,80));return}L.push([c[cols[0]],size==null?'':c[size],...v].join('\t'))}));
  return finish(ID,L,{anom})}
// 方式C：1行に名前と数値が並ぶ表。o={lx:[名前列],sx:[サイズ列],nx:[数値列],pages,cols,rt}
export function flat(ID,o){const L=[],anom=[];const pages=o.pages||[...new Set(window.__IT.map(i=>i.p))];
  for(const p of pages){const R={};window.__IT.filter(i=>i.p===p).forEach(i=>{const k=Object.keys(R).find(k=>Math.abs(k-i.y)<(o.rt||2))||i.y;(R[k]=R[k]||[]).push(i)});
    Object.keys(R).sort((a,b)=>b-a).forEach(y=>{const r=R[y].sort((a,b)=>a.x-b.x);const nm=r.filter(i=>i.x>=o.lx[0]&&i.x<o.lx[1]).map(i=>i.s).join('');const sz=o.sx?r.filter(i=>i.x>=o.sx[0]&&i.x<o.sx[1]).map(i=>i.s).join(''):'';
      const ns=r.filter(i=>i.x>=o.nx[0]&&i.x<o.nx[1]&&isNum(i.s)).map(i=>num(i.s));const v=o.cols?o.cols.map(c=>ns[c]):ns;
      if(nm&&v.length===5&&v.every(x=>x!=null)&&ns.length>=(o.min||5))L.push([nm,sz,...v].join('\t'));else if(ns.length>=3||(nm&&ns.length))anom.push('p'+p+' y'+y+' '+nm+' ['+ns.join(',')+']')})}
  return finish(ID,L,{anom})}
