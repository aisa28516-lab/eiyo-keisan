import json, re, collections, os
D = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(f'{D}/data/raw.json'))
# 重量変化率：成分表 第1章 表12（PDF 39〜63ページ）から取り出した値
RATES = json.load(open(f'{D}/data/rates.json'))
assert RATES['01088'] == 210 and RATES['06268'] == 70 and RATES['11287'] == 62 and RATES['10153'] == 73 and RATES['01039'] == 180, RATES.get('10153')
print('表12から読んだ重量変化率:', len(RATES))
COOK = {'ゆで','焼き','水煮','油いため','蒸し','電子レンジ調理','ソテー','素揚げ','天ぷら','フライ','から揚げ','とんかつ','目玉焼き','いり','ポーチドエッグ'}
BASE = {'生','乾'}

def num(v):
    if isinstance(v, (int, float)): return v
    s = str(v).strip().replace('†', '').strip('()')
    if s in ('Tr', '-', ''): return 0
    return float(s)

foods = []; toks = []
for r in rows:
    name = re.sub(r'\s+', ' ', r[2].replace('　', ' ')).strip()
    t = name.split(' ')
    toks.append(t)
    foods.append([r[1], name, num(r[3]), num(r[4]), num(r[5]), num(r[6]), num(r[7]), num(r[8]), -1, '', 0] + [num(x) for x in r[9:24]])

full = {tuple(t): i for i, t in enumerate(toks)}
by = collections.defaultdict(list)
for i, t in enumerate(toks):
    if len(t) > 1: by[tuple(t[:-1])].append(i)

groups = []
for pre, mem in by.items():
    cooked = [i for i in mem if toks[i][-1] in COOK]
    if not cooked: continue
    base = [i for i in mem if toks[i][-1] in BASE]
    label = None
    if base:
        # 生と乾の両方がある場合は、ゆで・水煮のエネルギー収支が1に近いほうを調理前とする
        def fit(c):
            rs = [foods[i][3] * RATES[foods[i][0]] / 100 / foods[c][3] for i in cooked if foods[i][0] in RATES and toks[i][-1] in ('ゆで', '水煮') and foods[c][3]]
            return abs(sum(rs) / len(rs) - 1) if rs else 0
        b = min(base, key=fit); label = toks[b][-1]
    elif pre in full and foods[full[pre]][8] == -1:
        b = full[pre]; label = 'そのまま'
    else:
        same = [i for i in mem if toks[i][-1] == pre[-1] or toks[i][-1] == '食パン']
        b = same[0] if len(same) == 1 else -1
        label = 'そのまま'
    m = ([b] if b >= 0 else []) + cooked
    if len(m) < 2: continue
    gi = len(groups)
    for i in m:
        foods[i][8] = gi
        foods[i][9] = label if i == b else toks[i][-1]
    groups.append({'b': b, 'm': m})

# 重量変化率を調理後食品に付ける。調理前食品との対応が疑わしいものは付けない
OIL = {'油いため','ソテー','フライ','から揚げ','天ぷら','素揚げ','とんかつ','目玉焼き','いり'}
dropped = []
for g in groups:
    if g['b'] < 0: continue
    b = foods[g['b']]
    for i in g['m']:
        f = foods[i]
        if i == g['b'] or f[0] not in RATES: continue
        ratio = f[3] * RATES[f[0]] / 100 / b[3] if b[3] else 1
        if (f[9] in OIL and ratio < 0.7) or (f[9] not in OIL and ratio > 2):
            dropped.append((f[0], f[1], RATES[f[0]], round(ratio, 2))); continue
        f[10] = RATES[f[0]]
print('重量変化率を付けた食品:', sum(1 for f in foods if f[10]), '／除外:', dropped)

for f in foods:
    for k in (2, 3, 4, 5, 6, 7, 10) + tuple(range(11, 26)):
        if float(f[k]).is_integer(): f[k] = int(f[k])

# 正誤表（2026-03-27）が反映済みであることの確認
chk = {f[0]: f for f in foods}
assert chk['11183'][3] == 241 and chk['11314'][3] == 238 and chk['11315'][3] == 283 and chk['11316'][3] == 254
assert chk['06372'][6] == 4.3 and chk['10470'][6] == 12.2 and '半固体状' in chk['17042'][1]
assert len(foods) == 2538 and all(len(f) == 26 for f in foods)
assert chk['01088'][11] == 1.5 and chk['01088'][12] == 29 and chk['01088'][15] == 34, chk['01088']

# ---- 呼び名の辞書 ----
# 1) 手作業で対応づけた日常語（aliases.txt、食品番号は成分表で確認）
# 2) 成分表の備考欄「別名」
# 3) 解説章の見出し「かな＜漢字＞」→ 漢字をかな表記に置き換える
idx = {f[0]: i for i, f in enumerate(foods)}
al = []
for ln in open(f'{D}/aliases.txt', encoding='utf-8'):
    ln = ln.strip()
    if not ln: continue
    words, ids = ln.rsplit(' ', 1)
    ids = ids.split(',')
    for x in ids: assert x in idx, (ln, x)
    for w in words.split('|'): al.append([w, [idx[x] for x in ids]])
n_manual = len(al)
bm = json.load(open(f'{D}/data/betsumei.json'))
seen = collections.OrderedDict()
for fid, ws in bm.items():
    for w in ws:
        parts = [re.sub(r'[（(].*?[）)]', '', w)] + re.findall(r'[（(](.*?)[）)]', w)
        for q in parts:
            q = q.strip(' 　。')
            if 1 < len(q) <= 14: seen.setdefault(q, []).append(idx[fid])
al += [[w, v] for w, v in seen.items()]
kj = {}
for kana, ks in json.load(open(f'{D}/data/kanji_heads.json')):
    for k in re.split(r'[、,]', ks):
        k = k.strip()
        if k and re.search(r'[一-龥]', k) and k != kana: kj.setdefault(k, kana)
kj = sorted(kj.items(), key=lambda x: -len(x[0]))
print('辞書: 手作業', n_manual, '語／別名', len(seen), '語／漢字表記', len(kj), '語')
# ---- 目安量 ----
# 容量→重さ：成分表の備考「100 mL：○ g」。個数など：省庁の公開資料に数値があるものだけ（SRC が出典）
dens = {idx[k]: v for k, v in json.load(open(f'{D}/data/density.json')).items() if k in idx}
SRC = ['文部科学省「日本食品標準成分表（八訂）増補2023年」備考欄の容量と重さの換算',
       '厚生労働省 標準的な健診・保健指導プログラム 学習教材「アルコール飲料の容量」',
       '農林水産省「食事バランスガイド」サービング数計算早見表',
       '厚生労働省 e-ヘルスネット「食事バランスガイド（基本編）」',
       '総務省統計局「小売物価統計調査」調査品目及び基本銘柄（平成18年12月現在）']
# (食品番号…, ラベル, g または ('ml', mL), 単位の語, 計量の時点 a=食べる状態/b=調理前/None, 皮などを含む, 使う食品番号, 出典)
PSPEC = [
 (['01088','01085','01086','01087','01089','01155','01154','01168'], '茶碗1杯（中盛り）', 150, ['茶碗','お茶碗','中盛り','杯','膳'], None, 0, None, 3),
 (['01088','01085','01086','01087','01089','01155','01154','01168'], '茶碗1杯（小盛り）', 100, ['小盛り'], None, 0, None, 3),
 (['01038','01039'], '1玉（ゆで、200〜250 gの中央）', 225, ['玉','食','袋'], 'a', 0, '01039', 4),
 (['01047','01048'], '1玉（生、110〜130 gの中央）', 120, ['玉','食'], 'b', 0, None, 4),
 (['12004','12005','12006','12021','12022','12023'], '1個（約50 g）', 50, ['個'], 'b', 0, None, 2),
 (['04032','04033','04097','04098','04099','04100'], '1丁', 300, ['丁'], None, 0, None, 2),
 (['04046'], '1パック', 50, ['パック','個'], None, 0, None, 4),
 (['13040'], 'スライス1枚', 18, ['スライス','枚'], None, 0, None, 4),
 (['07026','07027'], '1個（皮つき、100〜120 gの中央）', 110, ['個'], None, 1, None, 4),
 (['07148'], '1個（皮・芯つき、250〜385 gの中央）', 318, ['個'], None, 1, None, 4),
 (['13003','13005'], '瓶1本（200 mL）', ('ml', 200), ['瓶','びん','本'], None, 0, None, 4),
 (['13003','13005'], 'コップ1杯（200 mL）', ('ml', 200), ['コップ','杯'], None, 0, None, 2),
 (['16006','16007','16008','16009'], '缶1本（350 mL）', ('ml', 350), ['缶','本'], None, 0, None, 4),
 (['16006','16007','16008','16009'], '中ジョッキ（500 mL）', ('ml', 500), ['中ジョッキ','ジョッキ','杯'], None, 0, None, 1),
 (['16006','16007','16008','16009'], '大ジョッキ（800 mL）', ('ml', 800), ['大ジョッキ'], None, 0, None, 1),
 (['16006','16007','16008','16009'], 'グラス1杯（約350 mL）', ('ml', 350), ['グラス'], None, 0, None, 1),
 (['16006','16007','16008','16009'], '中びん1本（500 mL）', ('ml', 500), ['中びん','中瓶','びん','瓶'], None, 0, None, 1),
 (['16006','16007','16008','16009'], '大びん1本（633 mL）', ('ml', 633), ['大びん','大瓶'], None, 0, None, 1),
 (['16001','16002','16003','16004','16005'], '銚子1本・1合（180 mL）', ('ml', 180), ['銚子','とっくり','徳利','本'], None, 0, None, 1),
 (['16001','16002','16003','16004','16005'], 'おちょこ1杯（約30 mL）', ('ml', 30), ['おちょこ','お猪口','杯'], None, 0, None, 1),
 (['16010','16011','16012'], 'グラス1杯（約120 mL）', ('ml', 120), ['グラス','杯'], None, 0, None, 1),
 (['16010','16011','16012'], 'ボトル1本（750 mL）', ('ml', 750), ['ボトル','本'], None, 0, None, 1),
 (['16016','16017'], 'シングル（30 mL）', ('ml', 30), ['シングル','杯'], None, 0, None, 1),
 (['16016','16017'], 'ダブル（60 mL）', ('ml', 60), ['ダブル'], None, 0, None, 1),
 (['16014','16015','16022'], 'コップ1杯（120 mL）', ('ml', 120), ['コップ','杯'], None, 0, None, 1),
]
ports = {}
for ids_, label, amt, keys, t, w, v, src in PSPEC:
    for x in ids_:
        assert x in idx, x
        if isinstance(amt, tuple): assert idx[x] in dens, (x, label)
        ports.setdefault(idx[x], []).append([label, amt[1] if isinstance(amt, tuple) else amt, 1 if isinstance(amt, tuple) else 0, keys, t or '', w, idx[v] if v else -1, src])
print('目安量: 容量換算つき', len(dens), '食品／個数などの目安', len(ports), '食品')
data = json.dumps({'f': foods, 'g': groups, 'a': al, 'k': kj, 'd': dens, 'p': ports, 'src': SRC}, ensure_ascii=False, separators=(',', ':'))
assert '</' not in data
html = open(f'{D}/template.html', encoding='utf-8').read().replace('/*DATA*/null', data)
ROOT = os.path.dirname(D)                              # リポジトリの直下＝公開されるフォルダ
OUT = f'{D}/.out'; os.makedirs(OUT, exist_ok=True)     # 確認用の出力（リポジトリには入れない）
open(f'{OUT}/eiyo-keisan.html', 'w', encoding='utf-8').write(html)   # Claude のアーティファクト用
head = ('<!doctype html><html lang="ja"><head><meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        '<meta name="robots" content="noindex,nofollow">\n'
        '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">\n'
        '<meta name="apple-mobile-web-app-title" content="栄養価計算"><meta name="apple-mobile-web-app-status-bar-style" content="default">\n'
        '<link rel="apple-touch-icon" href="icon-180.png"><link rel="icon" href="icon-192.png"><link rel="manifest" href="manifest.webmanifest">\n'
        '<style>:root{color-scheme:light dark;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>\n')
open(f'{OUT}/local.html', 'w', encoding='utf-8').write(head + '</head><body>' + html + '</body></html>')   # 同期なしの確認用
open(f'{ROOT}/index.html', 'w', encoding='utf-8').write(head + '<script src="config.js"></script></head><body>' + html + '</body></html>')
# 同期ありの確認用（接続先はダミー。tests/sync.py が通信を偽の応答に差し替える）
os.makedirs(f'{OUT}/sitetest', exist_ok=True)
import shutil, hashlib
for f in ['index.html', 'manifest.webmanifest', 'sw.js', 'icon-180.png', 'icon-192.png']:
    shutil.copy(f'{ROOT}/{f}', f'{OUT}/sitetest/{f}')
open(f'{OUT}/sitetest/config.js', 'w').write('window.EIYO_CONFIG = { apiKey: "TESTKEY", projectId: "testproj" };\n')
ver = hashlib.sha1(html.encode()).hexdigest()[:10]
sw = open(f'{ROOT}/sw.js', encoding='utf-8').read()
open(f'{ROOT}/sw.js', 'w', encoding='utf-8').write(re.sub(r"const C = 'eiyo-[0-9a-f]+';", f"const C = 'eiyo-{ver}';", sw))
print(len(foods), 'foods', len(groups), 'groups', len(html) // 1024, 'KB', 'version', ver)
