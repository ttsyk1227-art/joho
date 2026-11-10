#!/usr/bin/env python3
"""ホームページ下書きPDFの1枚目の上部に「タイトル・氏名・日付・押印欄」を追加するアプリ。

使い方
  ウィンドウ画面:   python pdf_header.py
  コマンドライン:   python pdf_header.py 下書き.pdf -n "高橋　利之"
                    python pdf_header.py 下書き.pdf -o 提出用.pdf -t 新規部活動記事 \
                        -n "高橋　利之" -d 2026-11-10 -s 校長 教頭 事務長 教務 篠原

必要なもの: pip install pypdf reportlab
日本語フォント: Windows/Mac/Linux の標準フォントを自動で探してPDFに埋め込みます。
見つからない場合は、このファイルと同じ場所に font.ttf という名前でフォントを置いてください。
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# PDFに埋め込む日本語フォント（見つかった最初のもの）。ここに .ttf/.ttc を置いても良い。
FONT_CANDIDATES = [
    Path(__file__).with_name("font.ttf"),
    "C:/Windows/Fonts/BIZ-UDGothicR.ttc", "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/msgothic.ttc", "C:/Windows/Fonts/YuGothR.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
]


def _register_font() -> str:
    for cand in FONT_CANDIDATES:
        if Path(cand).is_file():
            try:
                pdfmetrics.registerFont(TTFont("JP", str(cand), subfontIndex=0))
                return "JP"
            except Exception:  # noqa: BLE001 - 読めないフォントは飛ばす
                continue
    # 見つからない場合は内蔵CIDフォント（埋め込まれないので表示環境に依存する）
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
    return "HeiseiKakuGo-W5"


FONT = _register_font()

DEFAULT_TITLE = "新規部活動記事"
DEFAULT_STAMPS = ["校長", "教頭", "事務長", "教務", "篠原"]
HEADER_HEIGHT = 105  # pt。ヘッダー帯の高さ（1枚目の上部に確保する）
MARGIN_X = 30  # pt。左右の余白


def to_reiwa(d: dt.date) -> str:
    """日付を「令和8年11月10日」の形式にする（令和=2019年5月1日〜）。"""
    if d >= dt.date(2019, 5, 1):
        y = d.year - 2018
        return f"令和{'元' if y == 1 else y}年{d.month}月{d.day}日"
    return f"{d.year}年{d.month}月{d.day}日"


def _header_pdf(width: float, height: float, title: str, name: str,
                date_text: str, stamps: list[str], label: str) -> PdfReader:
    """ヘッダー部分だけを描いた、元ページと同じ大きさの透明ページを作る。"""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    top = height  # 用紙の上端

    # 左: タイトル / 記載者 / 日付
    c.setFont(FONT, 14)
    c.drawString(MARGIN_X, top - 36, title)
    c.setFont(FONT, 10.5)
    c.drawString(MARGIN_X, top - 62, f"{label}　{name}" if name else label)
    c.drawString(MARGIN_X, top - 85, date_text)

    # 右: 押印欄（見出し行＋押印スペース）
    n = max(len(stamps), 1)
    box_w = min(60.0, (width * 0.5 - MARGIN_X) / n)  # 1欄の幅
    box_right = width - MARGIN_X
    box_left = box_right - box_w * n
    box_top = top - 21
    head_h, body_h = 14.0, 62.0
    c.setLineWidth(0.8)
    c.rect(box_left, box_top - head_h - body_h, box_w * n, head_h + body_h)
    c.line(box_left, box_top - head_h, box_right, box_top - head_h)
    for i in range(1, n):
        x = box_left + box_w * i
        c.line(x, box_top, x, box_top - head_h - body_h)
    for i, s in enumerate(stamps):
        size = 8.5
        while pdfmetrics.stringWidth(s, FONT, size) > box_w - 4 and size > 5:
            size -= 0.5  # 長い名称は欄に収まるまで縮める
        c.setFont(FONT, size)
        c.drawCentredString(box_left + box_w * (i + 0.5), box_top - head_h + 4, s)

    # 下: 区切り線
    c.setLineWidth(0.8)
    y = top - HEADER_HEIGHT + 6
    c.line(MARGIN_X, y, width - MARGIN_X, y)

    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf)


def add_header(src: str | Path, dst: str | Path, *, title: str = DEFAULT_TITLE,
               name: str = "", date: dt.date | None = None,
               stamps: list[str] | None = None, label: str = "記載者",
               shrink: bool = True) -> int:
    """src の1枚目にヘッダーを追加して dst に保存する。ページ数を返す。

    shrink=True : 1枚目の内容を縮小してヘッダーの下に収める（既定。文字や写真に重ならない）
    shrink=False: 縮小せず、そのまま上から重ねる（元の上余白が十分ある場合向け）
    """
    reader = PdfReader(str(src))
    if reader.is_encrypted:
        reader.decrypt("")
    writer = PdfWriter()
    date_text = to_reiwa(date or dt.date.today())
    stamps = DEFAULT_STAMPS if stamps is None else stamps

    for i, page in enumerate(reader.pages):
        if i == 0:
            w, h = float(page.mediabox.width), float(page.mediabox.height)
            if shrink:
                s = (h - HEADER_HEIGHT) / h
                # 縮小して、ヘッダーの下に左右中央で配置する
                tr = Transformation().scale(s, s).translate((w - w * s) / 2, 0)
                page.add_transformation(tr)
                page.cropbox = page.mediabox  # 変形後も表示範囲は用紙全体
            hdr = _header_pdf(w, h, title, name, date_text, stamps, label)
            page.merge_page(hdr.pages[0])
        writer.add_page(page)

    writer.add_metadata({"/Title": title})
    with open(dst, "wb") as f:
        writer.write(f)
    return len(reader.pages)


def default_output(src: Path) -> Path:
    return src.with_name(src.stem + "_提出用.pdf")


# ---------------------------------------------------------------- GUI
def run_gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("下書きPDFにヘッダーを追加")
    root.resizable(False, False)
    pad = {"padx": 8, "pady": 4}

    v_src = tk.StringVar()
    v_title = tk.StringVar(value=DEFAULT_TITLE)
    v_name = tk.StringVar()
    v_date = tk.StringVar(value=dt.date.today().isoformat())
    v_stamps = tk.StringVar(value="、".join(DEFAULT_STAMPS))
    v_shrink = tk.BooleanVar(value=True)

    frm = ttk.Frame(root, padding=10)
    frm.grid()
    rows = [("下書きPDF", v_src), ("タイトル", v_title), ("記載者の氏名", v_name),
            ("提出日 (YYYY-MM-DD)", v_date), ("押印欄（、で区切る）", v_stamps)]
    for r, (text, var) in enumerate(rows):
        ttk.Label(frm, text=text).grid(row=r, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=var, width=44).grid(row=r, column=1, **pad)

    def browse() -> None:
        p = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if p:
            v_src.set(p)

    ttk.Button(frm, text="選択…", command=browse).grid(row=0, column=2, **pad)
    ttk.Checkbutton(frm, text="1枚目を縮小してヘッダーの下に収める",
                    variable=v_shrink).grid(row=5, column=1, sticky="w", **pad)

    def run() -> None:
        src = Path(v_src.get())
        if not src.is_file():
            messagebox.showerror("エラー", "下書きPDFを選んでください。")
            return
        try:
            d = dt.date.fromisoformat(v_date.get().strip())
        except ValueError:
            messagebox.showerror("エラー", "提出日は 2026-11-10 の形式で入力してください。")
            return
        dst = filedialog.asksaveasfilename(
            defaultextension=".pdf", initialfile=default_output(src).name,
            initialdir=str(src.parent), filetypes=[("PDF", "*.pdf")])
        if not dst:
            return
        stamps = [s.strip() for s in v_stamps.get().replace(",", "、").split("、") if s.strip()]
        try:
            add_header(src, dst, title=v_title.get(), name=v_name.get(), date=d,
                       stamps=stamps, shrink=v_shrink.get())
        except Exception as e:  # noqa: BLE001 - 画面にそのまま表示する
            messagebox.showerror("エラー", f"変換に失敗しました:\n{e}")
            return
        messagebox.showinfo("完了", f"保存しました:\n{dst}")

    ttk.Button(frm, text="ヘッダーを追加して保存", command=run).grid(
        row=6, column=0, columnspan=3, pady=10)
    root.mainloop()


# ---------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input", nargs="?", help="下書きPDF（省略するとウィンドウ画面が開く）")
    ap.add_argument("-o", "--output", help="出力PDF（既定: 元の名前_提出用.pdf）")
    ap.add_argument("-t", "--title", default=DEFAULT_TITLE)
    ap.add_argument("-n", "--name", default="", help="記載者の氏名")
    ap.add_argument("-d", "--date", type=dt.date.fromisoformat, default=None,
                    help="提出日 YYYY-MM-DD（既定: 今日）")
    ap.add_argument("-s", "--stamps", nargs="+", default=None, metavar="役職",
                    help=f"押印欄の見出し（既定: {' '.join(DEFAULT_STAMPS)}）")
    ap.add_argument("--no-shrink", action="store_true", help="1枚目を縮小せず上から重ねる")
    a = ap.parse_args(argv)

    if not a.input:
        run_gui()
        return 0
    src = Path(a.input)
    dst = Path(a.output) if a.output else default_output(src)
    n = add_header(src, dst, title=a.title, name=a.name, date=a.date,
                   stamps=a.stamps, shrink=not a.no_shrink)
    print(f"保存しました: {dst}（{n}ページ）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
