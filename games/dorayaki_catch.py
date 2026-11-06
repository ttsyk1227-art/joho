"""
どら焼きキャッチゲーム（tkinter 版）

青いネコ型ロボットを左右に動かして、上から落ちてくるどら焼きを受け取ろう！

操作方法:
    ← / → キー（または A / D キー） : 左右に移動
    スペースキー                    : ゲームオーバー後にリスタート

ルール:
    - どら焼きをキャッチすると 1 点
    - 3 個落とすとゲームオーバー
    - 点数が上がるほど落ちるスピードが速くなる

実行方法（パソコンで）:
    python dorayaki_catch.py

※ tkinter は Python に最初から入っているので追加インストールは不要です。
※ Google Colab では画面（ウィンドウ）を表示できないため、パソコンの Python で実行してください。
"""

import random
import tkinter as tk

# ---------------- 設定 ----------------
WIDTH = 480          # 画面の幅
HEIGHT = 640         # 画面の高さ
FPS_MS = 16          # 1 フレームの時間（ミリ秒）約 60fps
PLAYER_SPEED = 7     # キャラクターの移動速度
PLAYER_Y = HEIGHT - 90   # キャラクターの中心の y 座標
MAX_MISS = 3         # 何個落としたらゲームオーバーか


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

        self.reset()
        self.loop()

    def reset(self):
        self.player_x = WIDTH // 2
        self.items = []          # 落ちてくるどら焼き [x, y, 速さ] のリスト
        self.score = 0
        self.miss = 0
        self.spawn_timer = 0
        self.game_over = False

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

        # どら焼きを出す（点数が上がるほど間隔が短く、速くなる）
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            speed = random.uniform(2.5, 4.0) + self.score * 0.15
            self.items.append([random.randint(30, WIDTH - 30), -20, speed])
            self.spawn_timer = max(20, 70 - self.score * 2)

        # どら焼きを落とす & 当たり判定
        remaining = []
        for item in self.items:
            item[1] += item[2]
            x, y = item[0], item[1]
            # キャラクターの頭のあたりに来たらキャッチ
            if PLAYER_Y - 60 < y < PLAYER_Y - 30 and abs(x - self.player_x) < 50:
                self.score += 1
                continue
            # 画面の下まで落ちたらミス
            if y > HEIGHT + 20:
                self.miss += 1
                if self.miss >= MAX_MISS:
                    self.game_over = True
                continue
            remaining.append(item)
        self.items = remaining

    def draw(self):
        c = self.canvas
        c.delete("all")
        # 地面
        c.create_rectangle(0, HEIGHT - 20, WIDTH, HEIGHT, fill="#7CCD7C", outline="")
        # どら焼き
        for x, y, _ in self.items:
            draw_dorayaki(c, x, y, "item")
        # キャラクター
        draw_robot_cat(c, self.player_x, PLAYER_Y)
        # スコア表示
        c.create_text(12, 12, anchor="nw", text=f"スコア: {self.score}",
                      font=("Helvetica", 18, "bold"), fill="#003366")
        c.create_text(WIDTH - 12, 12, anchor="ne", text="ミス: " + "×" * self.miss + "・" * (MAX_MISS - self.miss),
                      font=("Helvetica", 18, "bold"), fill="#B22222")
        # ゲームオーバー表示
        if self.game_over:
            c.create_rectangle(40, HEIGHT // 2 - 90, WIDTH - 40, HEIGHT // 2 + 70,
                               fill="white", outline="#003366", width=3)
            c.create_text(WIDTH // 2, HEIGHT // 2 - 45, text="ゲームオーバー",
                          font=("Helvetica", 28, "bold"), fill="#B22222")
            c.create_text(WIDTH // 2, HEIGHT // 2, text=f"キャッチした数: {self.score} 個",
                          font=("Helvetica", 18), fill="#003366")
            c.create_text(WIDTH // 2, HEIGHT // 2 + 40, text="スペースキーでもう一度",
                          font=("Helvetica", 14), fill="#333333")

    def loop(self):
        self.update()
        self.draw()
        self.root.after(FPS_MS, self.loop)


if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
