# プラグイン配布サイト

HTML / CSS / JS だけの静的サイトです。サーバー側の処理はないので、GitHub Pages・Netlify・Cloudflare Pages
など、ファイルを置くだけのホスティングでそのまま公開できます。`site` フォルダの中身をアップロードしてください。

## 構成

| パス | 内容 |
| --- | --- |
| `index.html` | 一覧ページ（検索・カテゴリで絞り込み） |
| `plugin.html?id=…` | 詳細ページ（1 つのページがデータから全プラグインを表示） |
| `data/plugins.json` | **ここだけ編集する**。サイト名・説明文・プラグイン一覧 |
| `data/plugins.js` | `plugins.json` から自動生成（ページが読み込む。直接編集しない） |
| `images/<id>/` | 自動生成のカバー画像（16:9）とサンプル画像 |
| `downloads/<id>-<version>.zip` | 自動生成のダウンロード |
| `tools/build_site.py` | 画像・zip・`plugins.js` を作る |
| `tools/install_mac.command` / `install_windows.bat` | zip に入れるインストーラー（zip 内の Fusion フォルダを Fusion のユーザーフォルダへコピー） |
| `tools/licenses/` | zip の THIRD_PARTY_NOTICES.txt に入れるライセンス全文 |

## プラグインを追加する

1. `data/plugins.json` の `plugins` に 1 件追加する（既存の項目をコピーして書き換えるのが早い）
   - `id`: URL とファイル名に使う英小文字（例 `telopanim`）
   - `name` / `version` / `updated` / `category` / `tags` / `summary` / `description` / `features` / `usage` / `requirements`
   - `files`: zip に入れるファイル。`src` は site フォルダから見たパス、`dst` は zip 内の置き場所
     （Fusion のユーザーフォルダと同じ形: `Fusion/Fuses/…`、`Fusion/Templates/Edit/Effects/…` など）
   - `images.cover`: カバーの元画像。`crop: [左, 上, 右, 下]` で切り抜き、`fit: true` で全体を背景色の上に収める
   - `images.gallery`: サンプル画像と説明（`caption`）
   - `credits`: 外部の手法・コードのクレジット。ライセンス全文が必要なものは `license_file` に `tools/licenses/…` を指定
   - `changelog`: 更新履歴（新しい順）
2. サイトを作り直す（Pillow が必要）

   ```bash
   ../teloppreset/.venv/bin/python tools/build_site.py
   ```

3. 一覧に出ないカテゴリを使った場合も、カテゴリの絞り込みボタンは自動で増える

## 更新するとき

- `version` を上げ、`updated` と `changelog` を書き足して `build_site.py` を実行する
- zip のファイル名にバージョンが入るので、古いリンクが新しい版に化けることはない（古い zip は残る。不要なら `downloads/` から消す）

## 説明を書くときの注意

- ほかの会社の製品名は書かない（例: 「有名編集ソフトのような」）
- 参考にした手法・コードはクレジットを入れる。ライセンス表記が必要なものは zip にも全文を入れる
- 参考画像の作品名・商標はプリセット名やサンプルに使わない
- フッターの商標表記（DaVinci Resolve / Fusion は Blackmagic Design の商標）は消さない

## ローカルで確認する

```bash
python3 -m http.server 8765 --directory site
```

`http://localhost:8765` を開く。`index.html` を直接ダブルクリックしても表示できる。
