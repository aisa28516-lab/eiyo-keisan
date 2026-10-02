"""ブラウザで公式資料から取り出した表（@@CHAIN id@@ … @@END@@）を、会話の記録からそのまま取り出して保存する。
手で書き写さないための道具。件数と合計が、ブラウザ側で計算した値と一致することを確かめる。
使い方: python3 src/chains/pull.py <id> <店名> <分野> <出典URL> <資料の更新日> [取得日]"""
import sys, json, glob, os, datetime
cid, name, cat, src, upd = sys.argv[1:6]
got = sys.argv[6] if len(sys.argv) > 6 else datetime.date.today().isoformat()
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(os.path.dirname(HERE), 'data', 'chains')
log = max(glob.glob('/root/.claude/projects/-home-claude-eiyo-keisan/*.jsonl'), key=os.path.getmtime)
mark = f'@@CHAIN {cid}@@'
def walk(o):
    if isinstance(o, str):
        if mark in o and '@@END@@' in o: yield o
    elif isinstance(o, dict):
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)
best = None
for line in open(log, encoding='utf-8'):
    if mark not in line or '"tool_result"' not in line: continue
    try: d = json.loads(line)
    except Exception: continue
    for s in walk(d):
        best = s
assert best, 'not found'
if best.lstrip().startswith('"'):
    try: best = json.loads(best[best.index('"'):best.rindex('"') + 1])
    except Exception: pass
body = best[best.index(mark) + len(mark):best.index('@@END@@')].strip('\n')
head, *rows = body.split('\n')
meta = json.loads(head)
rows = [r.split('\t') for r in rows if r.strip()]
assert all(len(r) == 7 for r in rows), [r for r in rows if len(r) != 7][:3]
assert len(rows) == meta['n'], (len(rows), meta['n'])
sums = [round(sum(float(r[k]) for r in rows), 1) for k in range(2, 7)]
assert sums == meta['sums'], (sums, meta['sums'])
assert not meta.get('anom'), meta['anom']
os.makedirs(DATA, exist_ok=True)
open(f'{DATA}/{cid}.tsv', 'w', encoding='utf-8').write('\n'.join('\t'.join(r) for r in rows) + '\n')
ip = f'{DATA}/index.json'
idx = json.load(open(ip, encoding='utf-8')) if os.path.exists(ip) else []
idx = [x for x in idx if x['id'] != cid] + [{'id': cid, 'name': name, 'cat': cat, 'src': src, 'updated': upd, 'fetched': got}]
json.dump(idx, open(ip, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved', cid, len(rows), 'rows; sums', sums)
