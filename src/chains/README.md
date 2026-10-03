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

## 収録済み（2026-10-03、26店・7,055品）
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
| かっぱ寿司 | https://www.kappasushi.jp/master_data/pdf/info_element.pdf | 2026年10月1日 | 1食あたり（2貫商品を1貫で頼んだら半分）。数値が幅や「-」で書かれた酒類など11品は除外。同名で数値の違う行は区分（夏季節定番・テイクアウトなど）をサイズ欄に |
| タリーズコーヒー | https://www.tullys.co.jp/menu/allergy/ （ページが読み込む公式API api.tullys.co.jp/api/calories/food・drink） | 2026年9月25日 | サイズ欄は「HOT/ICED・S/T/G・ミルクの種類」 |
| フレッシュネスバーガー | https://www.freshnessburger.co.jp/pdf/seibun.pdf | フード2026年10月1日／ドリンク8月26日 | 日本語のページだけ（英語ページは同じ内容）。炭水化物は糖質＋食物繊維の合計の列 |
| ジョリーパスタ | https://images.zensho.co.jp/materials/jolly-pasta/allergen/nutrition_facts.pdf | 2026年10月5日（資料の記載どおり） | 同名で数値の違う行はカテゴリーをサイズ欄に |
| ロイヤルホスト | https://www.royalhost.jp/safety/images/defaultl_allergen_list_260917.pdf （入口 https://www.royalhost.jp/safety/product_infomation.html ） | 2026年9月17日 | 通常店版。名前も数値も同じ行（複数のメニュー表に載っている品）は1つにまとめた。備考欄の※（「①〜④の合計」「メイン料理のみ」など）は取り込んでいない。丸数字で始まる行はセットの内訳。数値が欠けたベビーフード2品は除外 |
| びっくりドンキー | https://www.bikkuri-donkey.com/control-panel/uploads/2026/08/2026_0826_nutrition.pdf （入口 https://www.bikkuri-donkey.com/producing/ ） | 定番2026年4月8日／季節8月26日ほか | S・M・L は結合セルの中央にあるので、座標から行のまとまりを決めた（13行ずつ・8行ずつで一致を確認）。「〃」は直前の行の名前で置き換え。＋で書かれた追加分は「追加分」。テイクアウト・宅配の表はサイズ欄に明記 |
| バーガーキング | https://www.burgerking.co.jp/images/org/pdf/2026/09/30/e9bf563b-8edc-43e9-b15b-ec52bbe275da.pdf （メニュー詳細の「カロリー・アレルゲン情報」ボタンの行き先） | 2026年10月2日 | サイズ欄は製品重量 |
| リンガーハット | https://www.ringerhut.jp/quality/allergy-nutrition_value/ | 2026年9月17日 | HTML の表（列の順は エネルギー・食塩・たんぱく質・脂質・炭水化物）。名前も数値も同じ2行は1つに |
| やよい軒 | https://www.yayoiken.com/menu_list/info/13 | 2026年8月1日 | 東京都版。ごはんの種類をサイズ欄に。数値が空欄の2行は除外 |
| ほっともっと | https://www.hottomotto.com/menu_list/info/13 | 2026年10月1日 | 東京都版。ごはんの量をサイズ欄に |
| ファミリーマート | https://www.family.co.jp/goods/safety.html （カテゴリ別13ページ） | 記載なし（2026-10-03 取得） | 対象地域が全国でない品は地域をサイズ欄に。数値が空欄・「未満」の2品は除外。商品の入れ替わりが早いので古くなりやすい |


## 取り込めなかった店
- ロッテリア：公式の栄養成分 PDF（https://images.zensho.co.jp/materials/lotteria/allergen/nutrition.pdf 、検索結果の表示では更新日 2026.3.18）は、ブラウザで開いたページからの読み込みが 403 で拒否される。回避はしていない

## 収録できない・保留
- 炭水化物の列がない（糖質と食物繊維）：大戸屋
- 一覧がなく商品ごとのページだけ：スターバックス、ドトール、幸楽苑、ココス、セブン-イレブン、ローソン
- 項目が足りない：日高屋（エネルギーと食塩だけ）、くら寿司・はま寿司・コメダ珈琲店（エネルギーだけ）
- 栄養成分の公開が見つからない：ガスト、バーミヤン、ジョナサン、サイゼリヤ、餃子の王将、かつや、スシロー
- 未確認：丸亀製麺、オリジン弁当
