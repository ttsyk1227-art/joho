# Python ゲームサンプル：どら焼きキャッチ

青いネコ型ロボットを左右に動かして、落ちてくるどら焼きを受け取るゲームです。
お邪魔アイテム（爆弾）・ハイスコア保存・効果音つき。

同じゲームを 2 種類の書き方で用意しています。

| ファイル | 使うもの | 遊べる場所 |
|---|---|---|
| [dorayaki_catch.py](dorayaki_catch.py) | tkinter（Python に最初から入っている） | パソコンの Python |
| [web/main.py](web/main.py) | pygame | パソコンの Python ＋ **ブラウザ** |

## 操作方法

- ← / → キー（または A / D）：左右に移動
- スペースキー：スタート・リスタート
- M キー：効果音のオン / オフ
- （pygame 版のみ）画面の左半分 / 右半分をタッチ：左右に移動、タッチでスタート

## tkinter 版をパソコンで遊ぶ

```
python dorayaki_catch.py
```

## pygame 版をパソコンで遊ぶ

```
pip install pygame
python web/main.py
```

## pygame 版をブラウザで遊ぶ（GitHub Pages で公開）

[pygbag](https://pypi.org/project/pygbag/) を使うと、pygame のプログラムをブラウザで動かせます。
このリポジトリでは GitHub Actions（[.github/workflows/deploy-game.yml](../.github/workflows/deploy-game.yml)）が
自動で変換・公開します。

### 最初に 1 回だけやること

1. GitHub のリポジトリページで **Settings → Pages** を開く
2. **Build and deployment → Source** を **GitHub Actions** にする
3. `games/web` の変更が main ブランチに入ると自動で公開される
   （すぐ公開したいときは **Actions → ブラウザ版ゲームを公開 → Run workflow**）

公開されると、次の URL で遊べます（生徒にはこの URL を配るだけで OK）。

**https://ttsyk1227-art.github.io/joho/dorayaki/**

- 最初の読み込みに少し時間がかかります（ブラウザの中に Python を読み込むため）。
- 音はブラウザのルールで、画面をクリック / タッチした後から鳴ります。
- ハイスコアはそのブラウザの中（localStorage）に保存されます。

### 公開する前に自分のパソコンで試す

```
pip install pygbag
pygbag web
```

と実行して、ブラウザで http://localhost:8000 を開きます。

## ブラウザで動かすためのポイント（pygame 版）

- メインループを `async def main()` にして、1 フレームごとに `await asyncio.sleep(0)` を入れる
  （ブラウザに処理を返さないと画面が固まる）
- ファイル名は `main.py`、画像・フォントなどは同じフォルダ（`web/assets`）に入れる
- ブラウザにはパソコンの日本語フォントが無いので、フォントを同梱する
  （`web/assets/font.otf`。ゲームで使う文字だけを取り出した Noto Sans CJK JP。
  文章を変えて漢字が「□」になったら [tools/make_font.py](tools/make_font.py) で作り直す）
- ハイスコアはファイルではなく、ブラウザの localStorage に保存する
