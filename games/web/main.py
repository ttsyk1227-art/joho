"""
どら焼きキャッチゲーム（pygame 版 / ブラウザでも動く）

青いネコ型ロボットを左右に動かして、上から落ちてくるどら焼きを受け取ろう！

操作方法:
    ← / → キー（または A / D キー） : 左右に移動
    画面の左半分 / 右半分をタッチ   : 左右に移動（タブレット・スマホ用）
    スペースキー / タッチ            : ゲーム開始・リスタート
    M キー                          : 効果音のオン / オフ

ルール:
    - どら焼きをキャッチすると 1 点
    - どら焼きを落とすと ミス 1 回
    - お邪魔アイテム（爆弾）をキャッチしてしまうと ミス 1 回（爆弾は落としても OK）
    - ミスが 3 回になるとゲームオーバー
    - 点数が上がるほど落ちるスピードが速くなり、爆弾も増える
    - ハイスコアは保存され、次に遊ぶときも残る

実行方法:
    パソコンで遊ぶ    : pip install pygame してから python main.py
    ブラウザで遊ぶ    : pip install pygbag してから pygbag main.py があるフォルダ
                        （くわしくは同じフォルダの README.md を参照）

※ ブラウザで動かすために、メインループは async（非同期）で書いています。
   1 フレームごとに「await asyncio.sleep(0)」でブラウザに処理を返すのがポイントです。
"""

import array
import asyncio
import math
import os
import random
import sys

import pygame

# ---------------- 設定 ----------------
WIDTH = 480          # 画面の幅
HEIGHT = 640         # 画面の高さ
FPS = 60             # 1 秒あたりの画面の書きかえ回数
PLAYER_SPEED = 7     # キャラクターの移動速度
PLAYER_Y = HEIGHT - 90   # キャラクターの中心の y 座標
MAX_MISS = 3         # 何回ミスしたらゲームオーバーか

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_FILE = os.path.join(HERE, "assets", "font.otf")   # 日本語フォント（Noto Sans CJK JP の一部）
HIGHSCORE_FILE = os.path.join(HERE, "highscore.txt")

# ブラウザ（pygbag）で動いているかどうか
IN_BROWSER = sys.platform == "emscripten"

# 色
BLUE = (30, 144, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 48, 48)
GOLD = (255, 215, 0)
SKY = (191, 239, 255)
GROUND = (124, 205, 124)


# ---------------- ハイスコアの読み書き ----------------
# パソコンではファイルに、ブラウザでは localStorage（ブラウザの保存場所）に保存する
def load_highscore():
    try:
        if IN_BROWSER:
            import platform   # pygbag では platform.window がブラウザの window になる
            value = platform.window.localStorage.getItem("dorayaki_highscore")
            return int(value) if value else 0
        with open(HIGHSCORE_FILE, encoding="utf-8") as f:
            return int(f.read().strip())
    except Exception:
        return 0


def save_highscore(score):
    try:
        if IN_BROWSER:
            import platform
            platform.window.localStorage.setItem("dorayaki_highscore", str(score))
        else:
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
                f.write(str(score))
    except Exception:
        pass   # 保存できなくてもゲームは続ける


# ---------------- 効果音 ----------------
# 音のデータはプログラムの中で計算して作る（音声ファイルの用意は不要）
def make_tone(rate, notes, volume=0.4, wave_type="square"):
    """音の並び [(周波数Hz, 長さ秒), ...] から波形（-1.0〜1.0 の数のリスト）を作る。周波数 0 は休み"""
    samples = []
    for freq, length in notes:
        n = int(rate * length)
        for i in range(n):
            t = i / rate
            if freq == 0:
                v = 0.0
            elif wave_type == "square":          # 矩形波：ピコピコしたゲームらしい音
                v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            else:                                # 正弦波：やわらかい音
                v = math.sin(2 * math.pi * freq * t)
            fade = min(1.0, (n - i) / (rate * 0.01))   # 音の終わりのプチッという雑音を防ぐ
            samples.append(v * volume * fade)
    return samples


def make_slide(rate, f_start, f_end, length, volume=0.4):
    """周波数をなめらかに変えていく音（ピューン↑ / ヒュルル↓）"""
    samples = []
    n = int(rate * length)
    phase = 0.0
    for i in range(n):
        freq = f_start + (f_end - f_start) * i / n
        phase += 2 * math.pi * freq / rate
        v = 1.0 if math.sin(phase) >= 0 else -1.0
        samples.append(v * volume * (1 - i / n))
    return samples


def make_explosion(rate, length=0.4, volume=0.6):
    """だんだん小さくなる低めの雑音（ドカーン）"""
    samples = []
    n = int(rate * length)
    v = 0.0
    for i in range(n):
        v = v * 0.8 + random.uniform(-1, 1) * 0.2
        samples.append(v * 3 * volume * (1 - i / n) ** 2)
    return samples


class Sound:
    """効果音を作って鳴らすクラス。音が出せない環境では何もしない"""

    def __init__(self):
        self.enabled = True
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1)
            rate, size, channels = pygame.mixer.get_init()
            waves = {
                "catch": make_tone(rate, [(988, 0.05), (1319, 0.10)]),                  # ピコッ
                "miss": make_slide(rate, 600, 200, 0.3),                                # ヒュルル
                "bomb": make_explosion(rate),                                           # ドカーン
                "gameover": make_tone(rate, [(523, 0.18), (392, 0.18), (330, 0.18), (262, 0.45)],
                                      wave_type="sine"),                                # ドソミド↓
                "record": make_tone(rate, [(523, 0.1), (659, 0.1), (784, 0.1), (0, 0.05),
                                           (1047, 0.35)]),                              # ファンファーレ
                "start": make_slide(rate, 300, 900, 0.2, volume=0.3),                   # ピューン↑
            }
            for name, samples in waves.items():
                self.sounds[name] = self.to_sound(samples, size, channels)
        except Exception as e:
            print("効果音を使えません:", e)
            self.sounds = {}

    @staticmethod
    def to_sound(samples, size, channels):
        """波形のリストを pygame の Sound に変換する（ミキサーの形式に合わせる）"""
        if abs(size) == 8:
            data = array.array("B", (int((max(-1, min(1, x)) + 1) * 127.5) for x in samples))
        elif abs(size) == 32:   # 32 ビット浮動小数点
            data = array.array("f", (max(-1.0, min(1.0, x)) for x in samples))
        else:                   # 16 ビット
            data = array.array("h", (int(max(-1, min(1, x)) * 32767) for x in samples))
        if channels > 1:        # ステレオなら同じ音を左右に入れる
            data = array.array(data.typecode, (v for v in data for _ in range(channels)))
        return pygame.mixer.Sound(buffer=data.tobytes())

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()


# ---------------- 描画関数 ----------------
def oval(surf, fill, x0, y0, x1, y1, outline=BLACK, width=2):
    """tkinter の create_oval と同じように (左上, 右下) で楕円を描く"""
    rect = pygame.Rect(round(x0), round(y0), round(x1 - x0), round(y1 - y0))
    if fill:
        pygame.draw.ellipse(surf, fill, rect)
    if outline:
        pygame.draw.ellipse(surf, outline, rect, width)


def poly(surf, fill, points, outline=BLACK, width=2):
    pygame.draw.polygon(surf, fill, points)
    if outline:
        pygame.draw.polygon(surf, outline, points, width)


def draw_robot_cat(surf, x, y):
    """(x, y) を中心に青いネコ型ロボットを描く"""
    # 体
    oval(surf, BLUE, x - 38, y + 10, x + 38, y + 80)
    oval(surf, WHITE, x - 26, y + 22, x + 26, y + 72)
    # ポケット（下半分の半円）
    pocket = [(x + 18 * math.cos(a), y + 46 + 16 * math.sin(a))
              for a in [math.pi * i / 20 for i in range(21)]]
    poly(surf, WHITE, pocket)
    # 耳（三角）
    poly(surf, BLUE, [(x - 40, y - 30), (x - 30, y - 62), (x - 12, y - 44)])
    poly(surf, BLUE, [(x + 40, y - 30), (x + 30, y - 62), (x + 12, y - 44)])
    # 頭と顔
    oval(surf, BLUE, x - 45, y - 50, x + 45, y + 30)
    oval(surf, WHITE, x - 35, y - 32, x + 35, y + 28)
    # 目
    oval(surf, WHITE, x - 16, y - 42, x, y - 20)
    oval(surf, WHITE, x, y - 42, x + 16, y - 20)
    oval(surf, BLACK, x - 7, y - 33, x - 3, y - 27, outline=None)
    oval(surf, BLACK, x + 3, y - 33, x + 7, y - 27, outline=None)
    # 鼻
    oval(surf, RED, x - 5, y - 22, x + 5, y - 12, width=1)
    # 口（にっこり）
    pygame.draw.line(surf, BLACK, (x, y - 12), (x, y + 2), 2)
    pygame.draw.arc(surf, BLACK, pygame.Rect(x - 20, y - 18, 40, 34),
                    math.radians(200), math.radians(340), 2)
    # ひげ
    for dy in (-8, 0, 8):
        pygame.draw.line(surf, BLACK, (x - 12, y - 4 + dy // 2), (x - 32, y - 6 + dy), 1)
        pygame.draw.line(surf, BLACK, (x + 12, y - 4 + dy // 2), (x + 32, y - 6 + dy), 1)
    # 首輪と鈴
    pygame.draw.rect(surf, RED, pygame.Rect(x - 34, y + 26, 68, 8))
    pygame.draw.rect(surf, BLACK, pygame.Rect(x - 34, y + 26, 68, 8), 2)
    oval(surf, GOLD, x - 7, y + 30, x + 7, y + 44)
    # 手
    oval(surf, WHITE, x - 52, y + 28, x - 34, y + 46)
    oval(surf, WHITE, x + 34, y + 28, x + 52, y + 46)


def draw_dorayaki(surf, x, y):
    """(x, y) を中心にどら焼きを描く"""
    oval(surf, (181, 101, 29), x - 22, y - 4, x + 22, y + 14, outline=(92, 51, 23))   # 下の生地
    pygame.draw.rect(surf, (75, 30, 30), pygame.Rect(x - 20, y - 3, 40, 7))          # あんこ
    oval(surf, (198, 134, 66), x - 22, y - 14, x + 22, y + 4, outline=(92, 51, 23))  # 上の生地
    oval(surf, (227, 168, 105), x - 12, y - 11, x + 2, y - 6, outline=None)          # つや


def draw_bomb(surf, x, y, frame):
    """(x, y) を中心にお邪魔アイテム（爆弾）を描く"""
    oval(surf, (34, 34, 34), x - 18, y - 14, x + 18, y + 22)
    oval(surf, (136, 136, 136), x - 10, y - 6, x - 3, y + 1, outline=None)
    pygame.draw.rect(surf, (85, 85, 85), pygame.Rect(x - 6, y - 20, 12, 8))
    pygame.draw.lines(surf, (139, 69, 19), False, [(x, y - 20), (x + 6, y - 28), (x + 12, y - 26)], 2)
    spark = (255, 69, 0) if frame % 10 < 5 else GOLD     # 火花をチカチカさせる
    oval(surf, spark, x + 9, y - 31, x + 17, y - 23, outline=None)


# ---------------- ゲーム本体 ----------------
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.fonts = {}
        self.sound = Sound()
        self.highscore = load_highscore()
        self.frame = 0
        self.state = "title"     # "title"（タイトル画面）→ "play"（プレイ中）→ "over"（ゲームオーバー）
        self.reset()

    def font(self, size):
        """指定した大きさの日本語フォントを用意する（一度作ったら使い回す）"""
        if size not in self.fonts:
            try:
                self.fonts[size] = pygame.font.Font(FONT_FILE, size)
            except Exception:
                self.fonts[size] = pygame.font.Font(None, size)
        return self.fonts[size]

    def text(self, msg, size, color, pos, anchor="center"):
        img = self.font(size).render(msg, True, color)
        rect = img.get_rect(**{anchor: pos})
        self.screen.blit(img, rect)

    def reset(self):
        self.player_x = WIDTH // 2
        self.items = []          # 落ちてくるアイテム [種類, x, y, 速さ] のリスト
        self.score = 0
        self.miss = 0
        self.spawn_timer = 0
        self.new_record = False
        self.flash = 0

    def start(self):
        self.reset()
        self.state = "play"
        self.sound.play("start")

    def end_game(self):
        self.state = "over"
        if self.score > self.highscore:
            self.highscore = self.score
            self.new_record = True
            save_highscore(self.highscore)
            self.sound.play("record")
        else:
            self.sound.play("gameover")

    # --- 入力 ---
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.state != "play":
                self.start()
            elif event.key == pygame.K_m:
                self.sound.enabled = not self.sound.enabled
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            if self.state != "play":
                self.start()

    def move_direction(self):
        """キーやタッチから、左 (-1) / 右 (+1) / 止まる (0) を決める"""
        keys = pygame.key.get_pressed()
        d = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            d -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            d += 1
        # マウスのボタン（タッチ）を押している間は、押した側に動く
        if d == 0 and pygame.mouse.get_pressed()[0]:
            mx, _ = pygame.mouse.get_pos()
            d = -1 if mx < WIDTH // 2 else 1
        return d

    # --- 毎フレームの処理 ---
    def update(self):
        self.frame += 1
        if self.state != "play":
            return

        self.player_x += self.move_direction() * PLAYER_SPEED
        self.player_x = max(50, min(WIDTH - 50, self.player_x))

        # アイテムを出す（点数が上がるほど間隔が短く、速くなる）
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            speed = random.uniform(2.5, 4.0) + self.score * 0.15
            bomb_rate = min(0.4, 0.15 + self.score * 0.01)
            kind = "bomb" if random.random() < bomb_rate else "dorayaki"
            self.items.append([kind, random.randint(30, WIDTH - 30), -20, speed])
            self.spawn_timer = max(20, 70 - self.score * 2)

        # アイテムを落とす & 当たり判定
        remaining = []
        for item in self.items:
            item[2] += item[3]
            kind, x, y = item[0], item[1], item[2]
            if PLAYER_Y - 60 < y < PLAYER_Y - 30 and abs(x - self.player_x) < 50:
                if kind == "dorayaki":
                    self.score += 1
                    self.sound.play("catch")
                else:                 # 爆弾をキャッチしてしまった！
                    self.miss += 1
                    self.flash = 15
                    self.sound.play("bomb")
                continue
            if y > HEIGHT + 20:
                if kind == "dorayaki":
                    self.miss += 1
                    if self.miss < MAX_MISS:
                        self.sound.play("miss")
                continue
            remaining.append(item)
        self.items = remaining

        if self.miss >= MAX_MISS:
            self.end_game()

    def draw(self):
        s = self.screen
        if self.flash > 0:
            self.flash -= 1
            s.fill((255, 153, 153))
        else:
            s.fill(SKY)
        pygame.draw.rect(s, GROUND, pygame.Rect(0, HEIGHT - 20, WIDTH, 20))

        for kind, x, y, _ in self.items:
            if kind == "dorayaki":
                draw_dorayaki(s, x, y)
            else:
                draw_bomb(s, x, y, self.frame)
        draw_robot_cat(s, self.player_x, PLAYER_Y)

        # スコアなどの表示
        self.text(f"スコア: {self.score}", 22, (0, 51, 102), (12, 8), "topleft")
        self.text(f"ハイスコア: {max(self.highscore, self.score)}", 16, (153, 102, 0), (12, 38), "topleft")
        self.text("ミス: " + "×" * self.miss + "・" * (MAX_MISS - self.miss), 22, (178, 34, 34),
                  (WIDTH - 12, 8), "topright")
        self.text("音: オン (M)" if self.sound.enabled else "音: オフ (M)", 14, (85, 85, 85),
                  (WIDTH - 12, 40), "topright")

        cx, cy = WIDTH // 2, HEIGHT // 2
        if self.state == "title":
            self.panel(cx, cy, 200)
            self.text("どら焼きキャッチ", 32, (0, 51, 102), (cx, cy - 65))
            draw_dorayaki(s, cx - 180, cy - 62)
            draw_dorayaki(s, cx + 180, cy - 62)
            self.text("← → キーで動いて どら焼きを受け取ろう", 15, (51, 51, 51), (cx, cy - 18))
            self.text("爆弾はよけてね！ 3 回ミスで終わり", 15, (51, 51, 51), (cx, cy + 8))
            self.text("スペースキー / タッチでスタート", 18, (178, 34, 34), (cx, cy + 55))
        elif self.state == "over":
            self.panel(cx, cy, 200)
            self.text("ゲームオーバー", 32, (178, 34, 34), (cx, cy - 60))
            self.text(f"キャッチした数: {self.score} 個", 20, (0, 51, 102), (cx, cy - 15))
            if self.new_record:
                self.text("★ ハイスコア更新！ ★", 20, (255, 140, 0), (cx, cy + 22))
            else:
                self.text(f"ハイスコア: {self.highscore} 個", 18, (153, 102, 0), (cx, cy + 22))
            self.text("スペースキー / タッチでもう一度", 16, (51, 51, 51), (cx, cy + 65))

    def panel(self, cx, cy, h):
        rect = pygame.Rect(30, cy - h // 2, WIDTH - 60, h)
        pygame.draw.rect(self.screen, WHITE, rect, border_radius=12)
        pygame.draw.rect(self.screen, (0, 51, 102), rect, 3, border_radius=12)


async def main():
    pygame.mixer.pre_init(22050, -16, 1)
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("どら焼きキャッチ")
    clock = pygame.time.Clock()
    game = Game(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)   # ブラウザに処理を返す（これが無いとブラウザが固まる）

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
