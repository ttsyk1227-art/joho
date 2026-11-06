"""
どら焼きキャッチゲーム（tkinter 版）

青いネコ型ロボットを左右に動かして、上から落ちてくるどら焼きを受け取ろう！

操作方法:
    ← / → キー（または A / D キー） : 左右に移動
    スペースキー                    : ゲームオーバー後にリスタート

ルール:
    - どら焼きをキャッチすると 1 点
    - どら焼きを落とすと ミス 1 回
    - お邪魔アイテム（爆弾）をキャッチしてしまうと ミス 1 回（爆弾は落としても OK）
    - ミスが 3 回になるとゲームオーバー
    - 点数が上がるほど落ちるスピードが速くなり、爆弾も増える
    - ハイスコアはファイル（highscore.txt）に保存され、次に遊ぶときも残る

実行方法（パソコンで）:
    python dorayaki_catch.py

※ tkinter は Python に最初から入っているので追加インストールは不要です。
※ Google Colab では画面（ウィンドウ）を表示できないため、パソコンの Python で実行してください。
"""

import os
import random
import tkinter as tk

# ---------------- 設定 ----------------
WIDTH = 480          # 画面の幅
HEIGHT = 640         # 画面の高さ
FPS_MS = 16          # 1 フレームの時間（ミリ秒）約 60fps
PLAYER_SPEED = 7     # キャラクターの移動速度
PLAYER_Y = HEIGHT - 90   # キャラクターの中心の y 座標
MAX_MISS = 3         # 何回ミスしたらゲームオーバーか

# ハイスコアを保存するファイル（このプログラムと同じフォルダに作られる）
HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.txt")


# ---------------- ハイスコアの読み書き ----------------
def load_highscore():
    """ファイルからハイスコアを読み込む（ファイルが無いときは 0）"""
    try:
        with open(HIGHSCORE_FILE, encoding="utf-8") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_highscore(score):
    """ハイスコアをファイルに書き込む"""
    with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
        f.write(str(score))


# ---------------- 描画関数 ----------------
def draw_robot_cat(canvas, x, y):
    """(x, y) を中心に青いネコ型ロボットを描く"""
    t = "player"
    # 体
    canvas.create_oval(x - 38, y + 10, x + 38, y + 80, fill="#1E90FF", outline="black", width=2, tags=t)
    canvas.create_oval(x - 26, y + 22, x + 26, y + 72, fill="white", outline="black", width=2, tags=t)
    # ポケット
    canvas.create_arc(x - 18, y + 30, x + 18, y + 62, start=180, extent=180,
                      fill="white", outline="black", width=2, tags=t)
    # 耳（三角）
    canvas.create_polygon(x - 40, y - 30, x - 30, y - 62, x - 12, y - 44,
                          fill="#1E90FF", outline="black", width=2, tags=t)
    canvas.create_polygon(x + 40, y - 30, x + 30, y - 62, x + 12, y - 44,
                          fill="#1E90FF", outline="black", width=2, tags=t)
    # 頭
    canvas.create_oval(x - 45, y - 50, x + 45, y + 30, fill="#1E90FF", outline="black", width=2, tags=t)
    # 顔（白い部分）
    canvas.create_oval(x - 35, y - 32, x + 35, y + 28, fill="white", outline="black", width=2, tags=t)
    # 目
    canvas.create_oval(x - 16, y - 42, x, y - 20, fill="white", outline="black", width=2, tags=t)
    canvas.create_oval(x, y - 42, x + 16, y - 20, fill="white", outline="black", width=2, tags=t)
    canvas.create_oval(x - 7, y - 33, x - 3, y - 27, fill="black", tags=t)
    canvas.create_oval(x + 3, y - 33, x + 7, y - 27, fill="black", tags=t)
    # 鼻
    canvas.create_oval(x - 5, y - 22, x + 5, y - 12, fill="#FF3030", outline="black", width=1, tags=t)
    # 口（にっこり）
    canvas.create_line(x, y - 12, x, y + 2, fill="black", width=2, tags=t)
    canvas.create_arc(x - 20, y - 18, x + 20, y + 16, start=200, extent=140,
                      style="arc", outline="black", width=2, tags=t)
    # ひげ
    for dy in (-8, 0, 8):
        canvas.create_line(x - 12, y - 4 + dy // 2, x - 32, y - 6 + dy, fill="black", width=1, tags=t)
        canvas.create_line(x + 12, y - 4 + dy // 2, x + 32, y - 6 + dy, fill="black", width=1, tags=t)
    # 首輪と鈴
    canvas.create_rectangle(x - 34, y + 26, x + 34, y + 34, fill="#FF3030", outline="black", width=2, tags=t)
    canvas.create_oval(x - 7, y + 30, x + 7, y + 44, fill="#FFD700", outline="black", width=2, tags=t)
    # 手
    canvas.create_oval(x - 52, y + 28, x - 34, y + 46, fill="white", outline="black", width=2, tags=t)
    canvas.create_oval(x + 34, y + 28, x + 52, y + 46, fill="white", outline="black", width=2, tags=t)


def draw_dorayaki(canvas, x, y, tag):
    """(x, y) を中心にどら焼きを描く"""
    # 下の生地
    canvas.create_oval(x - 22, y - 4, x + 22, y + 14, fill="#B5651D", outline="#5C3317", width=2, tags=tag)
    # あんこ
    canvas.create_rectangle(x - 20, y - 3, x + 20, y + 4, fill="#4B1E1E", outline="", tags=tag)
    # 上の生地
    canvas.create_oval(x - 22, y - 14, x + 22, y + 4, fill="#C68642", outline="#5C3317", width=2, tags=tag)
    # つや
    canvas.create_oval(x - 12, y - 11, x + 2, y - 6, fill="#E3A869", outline="", tags=tag)


def draw_bomb(canvas, x, y, tag, frame):
    """(x, y) を中心にお邪魔アイテム（爆弾）を描く"""
    # 本体
    canvas.create_oval(x - 18, y - 14, x + 18, y + 22, fill="#222222", outline="black", width=2, tags=tag)
    # 光の反射
    canvas.create_oval(x - 10, y - 6, x - 3, y + 1, fill="#888888", outline="", tags=tag)
    # 口金と導火線
    canvas.create_rectangle(x - 6, y - 20, x + 6, y - 12, fill="#555555", outline="black", tags=tag)
    canvas.create_line(x, y - 20, x + 6, y - 28, x + 12, y - 26, fill="#8B4513", width=2, tags=tag)
    # 火花（フレームごとに色を変えてチカチカさせる）
    spark = "#FF4500" if frame % 10 < 5 else "#FFD700"
    canvas.create_oval(x + 9, y - 31, x + 17, y - 23, fill=spark, outline="", tags=tag)


# ---------------- ゲーム本体 ----------------
class Game:
    def __init__(self, root):
        self.root = root
        root.title("どら焼きキャッチ")
        root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#BFEFFF", highlightthickness=0)
        self.canvas.pack()

        # 押されているキーを覚えておく（押しっぱなしで動けるように）
        self.keys = set()
        root.bind("<KeyPress>", self.on_key_down)
        root.bind("<KeyRelease>", self.on_key_up)

        self.highscore = load_highscore()
        self.frame = 0
        self.reset()
        self.loop()

    def reset(self):
        self.player_x = WIDTH // 2
        self.items = []          # 落ちてくるアイテム [種類, x, y, 速さ] のリスト
        self.score = 0
        self.miss = 0
        self.spawn_timer = 0
        self.game_over = False
        self.new_record = False  # ハイスコアを更新したか
        self.flash = 0           # 爆弾に当たったときに画面を赤くする残りフレーム数

    def end_game(self):
        """ゲームオーバーにして、ハイスコアを更新していたら保存する"""
        self.game_over = True
        if self.score > self.highscore:
            self.highscore = self.score
            self.new_record = True
            save_highscore(self.highscore)

    # --- キー入力 ---
    def on_key_down(self, event):
        key = event.keysym.lower()
        self.keys.add(key)
        if self.game_over and key == "space":
            self.reset()

    def on_key_up(self, event):
        self.keys.discard(event.keysym.lower())

    # --- 毎フレームの処理 ---
    def update(self):
        if self.game_over:
            return

        # キャラクターの移動
        if "left" in self.keys or "a" in self.keys:
            self.player_x -= PLAYER_SPEED
        if "right" in self.keys or "d" in self.keys:
            self.player_x += PLAYER_SPEED
        self.player_x = max(50, min(WIDTH - 50, self.player_x))

        # アイテムを出す（点数が上がるほど間隔が短く、速くなる）
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            speed = random.uniform(2.5, 4.0) + self.score * 0.15
            # 爆弾が出る確率：最初は 15%、点数が上がると最大 40% まで増える
            bomb_rate = min(0.4, 0.15 + self.score * 0.01)
            kind = "bomb" if random.random() < bomb_rate else "dorayaki"
            self.items.append([kind, random.randint(30, WIDTH - 30), -20, speed])
            self.spawn_timer = max(20, 70 - self.score * 2)

        # アイテムを落とす & 当たり判定
        remaining = []
        for item in self.items:
            item[2] += item[3]
            kind, x, y = item[0], item[1], item[2]
            # キャラクターの頭のあたりに来たらキャッチ
            if PLAYER_Y - 60 < y < PLAYER_Y - 30 and abs(x - self.player_x) < 50:
                if kind == "dorayaki":
                    self.score += 1
                else:                 # 爆弾をキャッチしてしまった！
                    self.miss += 1
                    self.flash = 15
                continue
            # 画面の下まで落ちた
            if y > HEIGHT + 20:
                if kind == "dorayaki":  # どら焼きを落としたらミス（爆弾は OK）
                    self.miss += 1
                continue
            remaining.append(item)
        self.items = remaining

        if self.miss >= MAX_MISS:
            self.end_game()

    def draw(self):
        c = self.canvas
        c.delete("all")
        # 爆弾に当たった直後は背景を赤く光らせる
        if self.flash > 0:
            self.flash -= 1
            c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#FF9999", outline="")
        # 地面
        c.create_rectangle(0, HEIGHT - 20, WIDTH, HEIGHT, fill="#7CCD7C", outline="")
        # アイテム
        for kind, x, y, _ in self.items:
            if kind == "dorayaki":
                draw_dorayaki(c, x, y, "item")
            else:
                draw_bomb(c, x, y, "item", self.frame)
        # キャラクター
        draw_robot_cat(c, self.player_x, PLAYER_Y)
        # スコア表示
        c.create_text(12, 12, anchor="nw", text=f"スコア: {self.score}",
                      font=("Helvetica", 18, "bold"), fill="#003366")
        c.create_text(12, 40, anchor="nw", text=f"ハイスコア: {max(self.highscore, self.score)}",
                      font=("Helvetica", 14, "bold"), fill="#996600")
        c.create_text(WIDTH - 12, 12, anchor="ne", text="ミス: " + "×" * self.miss + "・" * (MAX_MISS - self.miss),
                      font=("Helvetica", 18, "bold"), fill="#B22222")
        # ゲームオーバー表示
        if self.game_over:
            c.create_rectangle(40, HEIGHT // 2 - 100, WIDTH - 40, HEIGHT // 2 + 100,
                               fill="white", outline="#003366", width=3)
            c.create_text(WIDTH // 2, HEIGHT // 2 - 60, text="ゲームオーバー",
                          font=("Helvetica", 28, "bold"), fill="#B22222")
            c.create_text(WIDTH // 2, HEIGHT // 2 - 15, text=f"キャッチした数: {self.score} 個",
                          font=("Helvetica", 18), fill="#003366")
            if self.new_record:
                c.create_text(WIDTH // 2, HEIGHT // 2 + 22, text="★ ハイスコア更新！ ★",
                              font=("Helvetica", 18, "bold"), fill="#FF8C00")
            else:
                c.create_text(WIDTH // 2, HEIGHT // 2 + 22, text=f"ハイスコア: {self.highscore} 個",
                              font=("Helvetica", 16), fill="#996600")
            c.create_text(WIDTH // 2, HEIGHT // 2 + 65, text="スペースキーでもう一度",
                          font=("Helvetica", 14), fill="#333333")

    def loop(self):
        self.frame += 1
        self.update()
        self.draw()
        self.root.after(FPS_MS, self.loop)


if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
