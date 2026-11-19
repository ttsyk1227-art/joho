# joho
## 教材

- [Google Colab で Python を学ぶための手引き](colab-python-guide.md)（[印刷用 PDF](colab-python-guide.pdf)）
- [練習用ノートブック 第1回](notebooks/python_practice_01.ipynb)

## Google Classroom 用 授業教材（全10回）

「基本事項 → 例題 → 課題 → 提出」の流れで段階的に学ぶ教材です。

- [授業ガイド（教員用）](classroom/README.md)
- [生徒配布用ノートブック](classroom/lessons/)

## フローチャート学習ツール

[フローチャート・トレーサー](tools/flowchart/index.html)（[ブラウザで開く](https://ttsyk1227-art.github.io/joho/flowchart/)）

フローチャートを 1 ステップずつ実行し、いま実行している記号・対応する Python の行・変数の値を同時に確かめられる教材です。
「Python段階学習 授業計画」（全12回）の **例題と課題** を、回ごとに選んで動かせます（第8回は参考例題のみ。ほかに補充として線形探索・バブルソート）。

- 入力値やリストの中身を変えて、通る道筋の違いを比べられます。関数の呼び出しや `break` の動きも追えます
- 値や分岐を先に予想してから進める「予想モード」つき
- **課題は Python を表示しません**（フローチャートを読んで自分で書く練習用）。解説のときは、アドレスの最後に `?teacher=1` を付けて開くと課題でも Python が表示されます
  - ⚠️ これは「うっかり見えない」ようにするだけの仕組みです。フローチャート自体が解答の手順を示しており、ページのソースを見れば Python も読めます。課題を公開したくない場合は、`index.html` の `LESSONS` から課題を外してください
- `index.html` 1 ファイルだけで動くので、ダウンロードして開くこともできます

### A4 プリント（左にフローチャート、右にプログラムを書く欄）

- ツールの「🖨 プリント」ボタンから、A4 縦のプリントを作って印刷できます。範囲（このプログラム／この回／全部の課題 など）と、右の欄（書きこみ用の空欄／プログラムつき）を選べます
- 右の欄は行番号つきの罫線で、字下げの目安になる点線が入ります。実行例（入力と表示）も載せられます
- 図が長くて字が小さくなるとき（縮小率 0.8 未満）は、自動で2枚に分けます。図は結合子（○A）でつながり、右の欄の行番号は2枚目に続きます（印刷画面のチェックで、分けないこともできます）
- 印刷の設定は、用紙 A4・縦、倍率 100％（「ページに合わせる」はオフ）にしてください
- 全36本（2枚に分けた2本を含めて38ページ。空欄・実行例つき）をまとめた PDF：[prints_student.pdf](tools/flowchart/prints_student.pdf)（[ブラウザで開く](https://ttsyk1227-art.github.io/joho/flowchart/prints_student.pdf)）
- 課題をプログラムつきで印刷できるのは、`?teacher=1` を付けて開いたときだけです（解答例は生徒用 PDF に入れていません）

## Python 作品ギャラリー（Colab でできることの紹介）

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ttsyk1227-art/joho/blob/main/showcase/python_showcase.ipynb)

音楽・フラクタル・シミュレーション・データ分析・Web API・機械学習・画像処理・3D グラフなど、
Python と Colab で作れる 11 の作品例です → [showcase/python_showcase.ipynb](showcase/python_showcase.ipynb)

## Python ゲームサンプル

- [どら焼きキャッチゲーム](games/README.md)：青いネコ型ロボットを ← → キーで動かし、落ちてくるどら焼きを受け取るゲーム。お邪魔アイテム（爆弾）・ハイスコア保存・効果音つき
  - [tkinter 版](games/dorayaki_catch.py)（パソコンの Python で実行）
  - [pygame 版](games/web/main.py)（パソコン・**ブラウザ**で実行。[ブラウザで遊ぶ](https://ttsyk1227-art.github.io/joho/dorayaki/)）

## 下書きPDFにヘッダーを追加するアプリ

ホームページの下書きPDFの1枚目上部に、タイトル・氏名・提出日・押印欄を追加します。

- [ブラウザで使う](https://ttsyk1227-art.github.io/joho/pdf-header/)（インストール不要）
- [Python版・説明](tools/pdf_header/README.md)
