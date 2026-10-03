# チェーン店メニューの取り込み手順

数値は各社の公式ページ・PDFからだけ取る。手で書き写さない（WebFetch の要約は行がずれることを確認済みなので使わない）。

1. ブラウザ（Claude の内蔵ブラウザ）で公式の栄養成分ページか PDF を開く
2. ページ内で JavaScript を実行して表を取り出す
   - PDF：pdf.js（cdn.jsdelivr.net/npm/pdfjs-dist@4）で文字と座標を取り、`extract_pdf.js` の `__PARSE` で「メニュー名・サイズ・5つの数値」に組み立てる。
     メニュー名は結合セルの中央に置かれているので、座標から行のまとまりを決めている
   - HTML の表：`table.rows` をそのまま読む
3. 結果を `@@CHAIN <id>@@` 〜 `@@END@@` の形で返す（1行目に件数と各列の合計）
4. `python3 src/chains/pull.py <id> <店名> <分野> <出典URL> <資料の更新日>` で会話の記録から取り出して保存。件数と合計が一致しないと保存されない
5. `python3 src/build.py` → `python3 src/tests/chain.py` → コミットして push

列：メニュー名、サイズ、エネルギー(kcal)、たんぱく質(g)、脂質(g)、炭水化物(g)、食塩相当量(g)

## 道具
`tools/extract.mjs`（公開先からブラウザで import できる）。`load(url)` で PDF の文字と座標を読み、表の形に合わせて次のどれかで組み立てる。
- `flat`：1行に名前と数値が並ぶ表（松屋、モスバーガー）
- `center`：メニュー名が結合セルの中央にある表（すき家、なか卯）
- `grid`：罫線でメニューのセルを決める表（吉野家、はなまるうどん）
- `table`：HTML の表（マクドナルド）
どの方式でも、エネルギーの列にある数値の個数と、取り出した行数が一致することを確かめる。

## 収録済み（2026-10-03）
| 店 | 出典 | 資料の日付 | 備考 |
|---|---|---|---|
| すき家 | https://images.zensho.co.jp/materials/sukiya/allergen/nutrition.pdf | 2026年9月29日 | |
| 吉野家 | https://www.yoshinoya.com/pdf/allergy/ | 2026年10月1日 | サイズ欄が複数行にまたがる C&C のドリンクとブルーシールは、どの行にどのサイズが当たるか確定できないため除外 |
| 松屋 | https://www.matsuyafoods.co.jp/matsuya/pdf/260929_nutritional_matsuya.pdf | 2026年9月29日 | 数値が幅で書かれた2品（マミー、生ジョッキ缶）は除外 |
| なか卯 | https://images.zensho.co.jp/materials/nakau/allergen/nutrition.pdf | 2026年9月30日 | |
| マクドナルド | https://www.mcdonalds.co.jp/quality/allergy_Nutrition/nutrient/ | 2026年9月30日 | 同名で数値の違う行が2組あり「一覧の1つ目／2つ目」として両方収録 |
| モスバーガー | https://www.mos.jp/menu/pdf/nutrition.pdf | 2026年10月1日 | 同名で数値の違う行は「モスカフェ専用」「中京エリア」「一覧の2つ目」と区別 |
| ケンタッキー | https://www.kfc.co.jp/food_information （PDF は外部CDN） | 2026年9月11日 | |
| CoCo壱番屋 | https://www.ichibanya.co.jp/menu/pdf/nutrition.pdf | 2026年10月1日 | ＊の注記（ライス量など）をサイズ欄に入れている |
| はなまるうどん | https://www.hanamaruudon.com/assets/pdf/allergy.pdf | 2026年10月1日 | レギュラーメニュー（2〜5ページ）だけ。季節メニューと吉野家コラボ店メニューは未収録 |
| サブウェイ | https://subway.co.jp/documents/pdf/eiyo.pdf | 2026年9月30日 | 同じ名前がサンドイッチ・サラダ・トッピングにあるので、区分をサイズ欄に入れている |
| ミスタードーナツ | https://www.misterdonut.jp/m_menu/eiyou/eiyou.pdf | 2026年9月30日 | |
| 松のや | https://www.matsuyafoods.co.jp/matsunoya/pdf/261002_matsunoya_nutritional.pdf | 2026年10月2日 | 一般店舗版。数値が幅で書かれた1品（マミー）は除外 |
| デニーズ | https://www.dennys.jp/safety/pdf/nutritive_value_A.pdf | 2026年10月2日 | 通常店版。同名で数値の違う3品は区分をサイズ欄に |
| ジョイフル | https://www.joyfull.co.jp/cal_pdf/cal.pdf | 2026年9月29日 | 同名で数値の違う行（後半の一覧）は「一覧の2つ目」 |
| 天丼てんや | https://www.tenya.co.jp/pdf/allergen-shop.pdf | 2026年9月24日 | |

## これから（公式資料の場所は 2026-10-03 に調査。5項目そろった一覧があるもの）
- PDF：フレッシュネスバーガー https://www.freshnessburger.co.jp/pdf/seibun.pdf ／バーガーキング（入口ページで最新版を確認してから）
- PDF：ロイヤルホスト（入口 https://www.royalhost.jp/safety/product_infomation.html ）／びっくりドンキー（入口で最新版を確認）／ジョリーパスタ https://images.zensho.co.jp/materials/jolly-pasta/allergen/nutrition_facts.pdf
- PDF：かっぱ寿司 https://www.kappasushi.jp/master_data/pdf/info_element.pdf ／タリーズ https://www.tullys.co.jp/menu/pdf/food.pdf ・drink.pdf
- HTML の表：やよい軒（都道府県別 https://www.yayoiken.com/menu/allergy.html ）／ほっともっと（都道府県別）／リンガーハット https://www.ringerhut.jp/quality/allergy-nutrition_value/ ／ファミリーマート（カテゴリ別 https://www.family.co.jp/goods/safety.html ）
- ロッテリア：PDF の場所は分かったが、ブラウザからの取得が 403 で読めなかった

## 収録できない・保留
- 炭水化物の列がない（糖質と食物繊維）：大戸屋
- 一覧がなく商品ごとのページだけ：スターバックス、ドトール、幸楽苑、ココス、セブン-イレブン、ローソン
- 項目が足りない：日高屋（エネルギーと食塩だけ）、くら寿司・はま寿司・コメダ珈琲店（エネルギーだけ）
- 栄養成分の公開が見つからない：ガスト、バーミヤン、ジョナサン、サイゼリヤ、餃子の王将、かつや、スシロー
- 未確認：丸亀製麺、オリジン弁当
