"""
ブラウザ版（games/web）で使う日本語フォントを作るスクリプト

日本語フォントは丸ごとだと十数 MB あってブラウザでの読み込みが遅くなるため、
ゲームで使う文字（＋ひらがな・カタカナ・英数字）だけを取り出した小さなフォントを作る。

ゲームの文章を変えて、新しい漢字が「□」になってしまったときに実行する。

準備:
    pip install fonttools
    Noto Sans CJK JP の Bold フォントを用意する
      （Ubuntu なら sudo apt install fonts-noto-cjk で
        /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc に入る。
        または https://github.com/notofonts/noto-cjk から入手）

実行（リポジトリのいちばん上のフォルダで）:
    python games/tools/make_font.py /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc
"""

import os
import sys

from fontTools import subset
from fontTools.ttLib import TTCollection, TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(HERE, "..", "web", "main.py")
OUT = os.path.join(HERE, "..", "web", "assets", "font.otf")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = sys.argv[1]

    # 使う文字：英数字・記号、ひらがな、カタカナ、全角記号 ＋ main.py に出てくる文字すべて
    chars = set(chr(c) for c in range(0x20, 0x7F))
    chars |= set(chr(c) for c in range(0x3000, 0x3100))   # 句読点・ひらがな・カタカナ
    chars |= set(chr(c) for c in range(0xFF01, 0xFF5F))   # 全角英数字・記号
    with open(GAME, encoding="utf-8") as f:
        chars |= set(f.read())
    chars = {c for c in chars if c.isprintable()}

    if src.lower().endswith(".ttc"):
        # .ttc はいくつものフォントが入っているので「JP」のものを選ぶ
        coll = TTCollection(src)
        font = next(f for f in coll if "CJK JP" in f["name"].getDebugName(4))
    else:
        font = TTFont(src)

    options = subset.Options()
    options.layout_features = ["*"]
    sub = subset.Subsetter(options)
    sub.populate(text="".join(chars))
    sub.subset(font)
    font.save(OUT)
    print(f"{OUT} を作りました（{len(chars)} 文字, {os.path.getsize(OUT) // 1024} KB）")


if __name__ == "__main__":
    main()
