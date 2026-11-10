# 下書きPDFにヘッダー（タイトル・氏名・日付・押印欄）を追加するアプリ

ホームページの下書きPDFを入力すると、**1枚目の上部**に次を追加したPDFを出力します。

- タイトル（既定: 新規部活動記事）
- 記載者の氏名
- 提出日（令和表記。例: 令和8年11月10日）
- 押印欄（既定: 校長／教頭／事務長／教務／篠原）と区切り線

1枚目の内容は少し縮小してヘッダーの下に収めます（2枚目以降はそのまま）。

## 準備

```bash
pip install pypdf reportlab
```

日本語フォントはOS標準のものを自動で探してPDFに埋め込みます。見つからない場合は
`pdf_header.py` と同じ場所に `font.ttf`（日本語TrueTypeフォント）を置いてください。

## 使い方

ウィンドウ画面（ファイルを選んで氏名・日付を入力するだけ）:

```bash
python tools/pdf_header/pdf_header.py
```

コマンドライン:

```bash
python tools/pdf_header/pdf_header.py 下書き.pdf -n "高橋　利之" -d 2026-11-10
# 押印欄の変更・出力名の指定
python tools/pdf_header/pdf_header.py 下書き.pdf -o 提出用.pdf -t 新規部活動記事 -s 校長 教頭 事務長 教務 篠原
# 縮小せず上から重ねたい場合
python tools/pdf_header/pdf_header.py 下書き.pdf --no-shrink
```
