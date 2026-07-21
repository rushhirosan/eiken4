#!/usr/bin/env python3
"""Generate Solomaker product icon + 5 explanation images for Eiken Practice."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).resolve().parent

PRIMARY = (124, 108, 255)
PRIMARY_DEEP = (99, 85, 224)
PRIMARY_SOFT = (91, 140, 255)
TEAL = (79, 209, 197)
BG = (247, 248, 252)
BG_SOFT = (238, 241, 248)
TEXT = (22, 27, 46)
MUTED = (63, 71, 92)
WHITE = (255, 255, 255)
CARD_BORDER = (22, 27, 46, 30)

FONT_REG = "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc"
FONT_MED = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size, index=0)
    except OSError:
        return ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", size)


def f_reg(s: int) -> ImageFont.FreeTypeFont:
    return font(FONT_REG, s)


def f_med(s: int) -> ImageFont.FreeTypeFont:
    return font(FONT_MED, s)


def f_bold(s: int) -> ImageFont.FreeTypeFont:
    return font(FONT_BOLD, s)


def lerp(a: tuple[int, ...], b: tuple[int, ...], t: float) -> tuple[int, ...]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def vertical_gradient(size: tuple[int, int], c1: tuple[int, int, int], c2: tuple[int, int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, c1)
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        color = lerp(c1, c2, t)
        for x in range(w):
            px[x, y] = color
    return img


def soft_blob(img: Image.Image, center: tuple[int, int], radius: int, color: tuple[int, int, int], alpha: int = 48) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    x, y = center
    d.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(*color, alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(max(radius // 3, 8)))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def text_width(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    return bbox[2] - bbox[0]


def draw_centered(draw: ImageDraw.ImageDraw, text: str, y: int, font_obj: ImageFont.ImageFont, fill, width: int) -> None:
    tw = text_width(draw, text, font_obj)
    draw.text(((width - tw) / 2, y), text, font=font_obj, fill=fill)


def wrap_chars(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        line = ""
        for ch in para:
            test = line + ch
            if text_width(draw, test, font_obj) <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = ch
        if line:
            lines.append(line)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font_obj: ImageFont.ImageFont,
    fill,
    max_width: int,
    line_gap: int = 8,
) -> int:
    x, y = xy
    lines = wrap_chars(draw, text, font_obj, max_width)
    for line in lines:
        draw.text((x, y), line, font=font_obj, fill=fill)
        bbox = draw.textbbox((0, 0), line or " ", font=font_obj)
        y += (bbox[3] - bbox[1]) + line_gap
    return y


def card(draw: ImageDraw.ImageDraw, xy, radius: int = 24, fill=WHITE, outline=None) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=2 if outline else 0)


def shadow_card(base: Image.Image, xy, radius: int = 24, fill=WHITE) -> Image.Image:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    x0, y0, x1, y1 = xy
    # soft shadow
    d.rounded_rectangle([x0 + 6, y0 + 10, x1 + 6, y1 + 10], radius=radius, fill=(22, 27, 46, 28))
    overlay = overlay.filter(ImageFilter.GaussianBlur(12))
    d2 = ImageDraw.Draw(overlay)
    d2.rounded_rectangle(xy, radius=radius, fill=(*fill, 255))
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def make_base(w: int = 1200, h: int = 675) -> Image.Image:
    img = vertical_gradient((w, h), BG, BG_SOFT)
    img = soft_blob(img, (180, 80), 280, PRIMARY, 36)
    img = soft_blob(img, (1050, 120), 260, TEAL, 28)
    img = soft_blob(img, (900, 580), 300, PRIMARY_SOFT, 22)
    return img


def brand_chip(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rounded_rectangle([x, y, x + 210, y + 36], radius=18, fill=PRIMARY)
    f = f_med(18)
    label = "Eiken Practice"
    tw = text_width(draw, label, f)
    draw.text((x + (210 - tw) / 2, y + 7), label, font=f, fill=WHITE)


def footer_url(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    f = f_reg(18)
    url = "eiken-practice.com"
    tw = text_width(draw, url, f)
    draw.text(((w - tw) / 2, h - 42), url, font=f, fill=MUTED)


# ---------- ICON ----------
def make_icon() -> Path:
    size = 512
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = grad.load()
    for y in range(size):
        for x in range(size):
            t = (0.35 * x + 0.65 * y) / size
            c = lerp(PRIMARY_DEEP, PRIMARY_SOFT, min(1.0, t))
            # slight teal corner
            t2 = max(0.0, (x + y - size) / size)
            c = lerp(c, TEAL, t2 * 0.25)
            px[x, y] = (*c, 255)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([18, 18, size - 18, size - 18], radius=116, fill=255)
    grad.putalpha(mask)
    canvas = Image.alpha_composite(canvas, grad)

    d = ImageDraw.Draw(canvas)
    cx, cy = 256, 228
    # open book
    d.polygon([(cx, cy + 18), (cx - 118, cy - 42), (cx - 118, cy + 68), (cx, cy + 118)], fill=(255, 255, 255, 220))
    d.polygon([(cx, cy + 18), (cx + 118, cy - 42), (cx + 118, cy + 68), (cx, cy + 118)], fill=(255, 255, 255, 255))
    d.line([(cx, cy + 18), (cx, cy + 118)], fill=(*PRIMARY_DEEP, 255), width=7)
    # teal bookmark
    d.polygon([(cx + 72, cy - 8), (cx + 98, cy - 52), (cx + 98, cy + 38), (cx + 72, cy + 58)], fill=(*TEAL, 255))

    f = f_bold(78)
    label = "EP"
    tw = text_width(d, label, f)
    d.text(((size - tw) / 2, 352), label, font=f, fill=WHITE)

    f2 = f_med(22)
    sub = "Eiken Practice"
    tw = text_width(d, sub, f2)
    d.text(((size - tw) / 2, 438), sub, font=f2, fill=(235, 237, 255, 255))

    out = OUT / "icon.png"
    canvas.convert("RGB").save(out, "PNG", optimize=True)
    return out


# ---------- EXPLAIN 1: Hero ----------
def make_explain_01() -> Path:
    w, h = 1200, 675
    img = make_base(w, h)
    img = shadow_card(img, (70, 70, 1130, 580), radius=28)
    d = ImageDraw.Draw(img)
    brand_chip(d, 110, 110)

    title = "ブラウザだけで、英検対策。"
    d.text((110, 175), title, font=f_bold(46), fill=TEXT)

    body = (
        "アプリのインストール不要。スマホを持っていない子でも、"
        "家庭のPCやタブレットのブラウザからすぐ練習できます。"
    )
    draw_wrapped(d, body, (110, 255), f_reg(26), MUTED, 620, line_gap=10)

    # feature pills
    pills = ["無料", "5級・4級・3級", "PCでもOK"]
    x = 110
    y = 390
    for p in pills:
        f = f_med(20)
        tw = text_width(d, p, f)
        pad = 18
        d.rounded_rectangle([x, y, x + tw + pad * 2, y + 40], radius=20, fill=(238, 236, 255))
        d.text((x + pad, y + 8), p, font=f, fill=PRIMARY_DEEP)
        x += tw + pad * 2 + 12

    # right side: browser mock
    bx0, by0, bx1, by1 = 760, 130, 1080, 520
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=16, fill=(11, 16, 32))
    d.rounded_rectangle([bx0 + 10, by0 + 10, bx1 - 10, by0 + 42], radius=8, fill=(30, 38, 64))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([bx0 + 22 + i * 18, by0 + 20, bx0 + 34 + i * 18, by0 + 32], fill=c)
    d.rounded_rectangle([bx0 + 90, by0 + 18, bx1 - 24, by0 + 34], radius=6, fill=(50, 60, 95))
    d.text((bx0 + 100, by0 + 18), "eiken-practice.com", font=f_reg(12), fill=(180, 190, 220))

    # content area
    d.rounded_rectangle([bx0 + 18, by0 + 56, bx1 - 18, by1 - 18], radius=12, fill=BG)
    d.text((bx0 + 40, by0 + 80), "今日の学習", font=f_bold(22), fill=TEXT)
    items = [("文法・語彙", "12問"), ("リスニング", "10問"), ("模擬試験", "開始")]
    yy = by0 + 130
    for name, meta in items:
        d.rounded_rectangle([bx0 + 36, yy, bx1 - 36, yy + 58], radius=12, fill=WHITE, outline=(22, 27, 46, 20))
        d.text((bx0 + 52, yy + 16), name, font=f_med(18), fill=TEXT)
        d.text((bx1 - 120, yy + 18), meta, font=f_reg(16), fill=PRIMARY)
        yy += 72

    footer_url(d, w, h)
    out = OUT / "explain_01_browser.png"
    img.save(out, "PNG", optimize=True)
    return out


# ---------- EXPLAIN 2: Features ----------
def make_explain_02() -> Path:
    w, h = 1200, 675
    img = make_base(w, h)
    d = ImageDraw.Draw(img)
    brand_chip(d, 70, 48)
    d.text((70, 110), "学習に必要な機能をひとつに", font=f_bold(40), fill=TEXT)
    d.text((70, 170), "本番形式に近い問題演習と、続けやすい仕組みを両立", font=f_reg(22), fill=MUTED)

    features = [
        ("文法・語彙", "穴埋め・会話補充など\n基礎を固める問題"),
        ("長文読解", "本文ごとに解き進める\n実戦的な読解練習"),
        ("リスニング", "イラスト・会話・長文\n音声を聞きながら解答"),
        ("進捗管理", "正答率・連続学習\nバッジで継続を支援"),
    ]
    colors = [PRIMARY, PRIMARY_SOFT, TEAL, PRIMARY_DEEP]
    card_w, card_h = 250, 300
    gap = 24
    total = 4 * card_w + 3 * gap
    start_x = (w - total) // 2
    y0 = 240
    for i, ((title, desc), color) in enumerate(zip(features, colors)):
        x = start_x + i * (card_w + gap)
        img = shadow_card(img, (x, y0, x + card_w, y0 + card_h), radius=22)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([x + 24, y0 + 28, x + 72, y0 + 76], radius=14, fill=color)
        # simple glyph
        d.text((x + 36, y0 + 36), str(i + 1), font=f_bold(24), fill=WHITE)
        d.text((x + 24, y0 + 110), title, font=f_bold(24), fill=TEXT)
        draw_wrapped(d, desc, (x + 24, y0 + 160), f_reg(18), MUTED, card_w - 48, line_gap=8)

    footer_url(d, w, h)
    out = OUT / "explain_02_features.png"
    img.save(out, "PNG", optimize=True)
    return out


# ---------- EXPLAIN 3: Levels ----------
def make_explain_03() -> Path:
    w, h = 1200, 675
    img = make_base(w, h)
    d = ImageDraw.Draw(img)
    brand_chip(d, 70, 48)
    d.text((70, 110), "英検5級・4級・3級に対応", font=f_bold(40), fill=TEXT)
    d.text((70, 170), "級ごとに最適化された問題セットで効率的に対策", font=f_reg(22), fill=MUTED)

    levels = [
        ("英検5級", "Level 5", "入門", ["文法・語彙", "会話補充", "語順選択", "リスニング", "模擬試験"], PRIMARY),
        ("英検4級", "Level 4", "初級", ["文法・語彙", "会話補充", "長文読解", "リスニング", "模擬試験"], PRIMARY_SOFT),
        ("英検3級", "Level 3", "中級", ["文法・語彙", "ライティング", "長文読解", "リスニング", "模擬試験"], TEAL),
    ]
    card_w, card_h = 340, 360
    gap = 28
    total = 3 * card_w + 2 * gap
    start_x = (w - total) // 2
    y0 = 230
    for i, (name, en, badge, tags, color) in enumerate(levels):
        x = start_x + i * (card_w + gap)
        img = shadow_card(img, (x, y0, x + card_w, y0 + card_h), radius=24)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([x, y0, x + card_w, y0 + 8], radius=4, fill=color)
        d.text((x + 28, y0 + 36), name, font=f_bold(30), fill=TEXT)
        d.text((x + 28, y0 + 80), en, font=f_reg(18), fill=MUTED)
        bw = text_width(d, badge, f_med(16)) + 24
        d.rounded_rectangle([x + 28, y0 + 118, x + 28 + bw, y0 + 148], radius=12, fill=color)
        d.text((x + 40, y0 + 122), badge, font=f_med(16), fill=WHITE)
        yy = y0 + 180
        for tag in tags:
            d.ellipse([x + 32, yy + 6, x + 44, yy + 18], fill=color)
            d.text((x + 56, yy), tag, font=f_reg(18), fill=MUTED)
            yy += 32

    footer_url(d, w, h)
    out = OUT / "explain_03_levels.png"
    img.save(out, "PNG", optimize=True)
    return out


# ---------- EXPLAIN 4: Progress / compete ----------
def make_explain_04() -> Path:
    w, h = 1200, 675
    img = make_base(w, h)
    img = shadow_card(img, (70, 70, 1130, 580), radius=28)
    d = ImageDraw.Draw(img)
    brand_chip(d, 110, 110)
    d.text((110, 175), "進捗を見比べて、続けられる", font=f_bold(40), fill=TEXT)
    body = (
        "アカウントを作って学習記録を残せます。"
        "正答率・連続学習・バッジでモチベーションを保ち、"
        "友達と同じペースで英検に取り組めます。"
    )
    draw_wrapped(d, body, (110, 245), f_reg(24), MUTED, 520, line_gap=10)

    # stats cards
    stats = [("連続学習", "7日"), ("正答率", "82%"), ("バッジ", "5個")]
    x = 110
    y = 400
    for label, value in stats:
        d.rounded_rectangle([x, y, x + 150, y + 110], radius=18, fill=(238, 236, 255))
        d.text((x + 20, y + 22), label, font=f_reg(16), fill=MUTED)
        d.text((x + 20, y + 52), value, font=f_bold(34), fill=PRIMARY_DEEP)
        x += 170

    # right: leaderboard-ish
    bx0, by0 = 700, 140
    d.rounded_rectangle([bx0, by0, 1080, 520], radius=20, fill=(11, 16, 32))
    d.text((bx0 + 36, by0 + 28), "学習タイムライン", font=f_bold(22), fill=WHITE)
    rows = [
        ("あなた", "模擬試験クリア", "今日"),
        ("友達A", "リスニング10問", "昨日"),
        ("友達B", "バッジ獲得", "2日前"),
        ("あなた", "文法・語彙12問", "3日前"),
    ]
    yy = by0 + 90
    for name, action, when in rows:
        d.rounded_rectangle([bx0 + 24, yy, 1056, yy + 70], radius=14, fill=(30, 38, 64))
        d.ellipse([bx0 + 40, yy + 18, bx0 + 74, yy + 52], fill=PRIMARY)
        d.text((bx0 + 90, yy + 14), name, font=f_med(18), fill=WHITE)
        d.text((bx0 + 90, yy + 40), action, font=f_reg(15), fill=(168, 179, 207))
        d.text((980, yy + 26), when, font=f_reg(14), fill=TEAL)
        yy += 84

    footer_url(d, w, h)
    out = OUT / "explain_04_progress.png"
    img.save(out, "PNG", optimize=True)
    return out


# ---------- EXPLAIN 5: Story / free ----------
def make_explain_05() -> Path:
    w, h = 1200, 675
    img = make_base(w, h)
    img = shadow_card(img, (70, 70, 1130, 580), radius=28)
    d = ImageDraw.Draw(img)
    brand_chip(d, 110, 110)

    d.text((110, 175), "子どもの英検対策から生まれた", font=f_bold(38), fill=TEXT)
    body = (
        "手軽に練習できるWebサービスが少なく、"
        "スマホを持たない子でもアプリなしで使える場が欲しかった。"
        "だからブラウザで完結する学習サイトを作りました。"
    )
    draw_wrapped(d, body, (110, 245), f_reg(24), MUTED, 980, line_gap=10)

    points = [
        ("無料で始められる", "アカウント登録ですぐ演習"),
        ("家庭のPCでOK", "インストール不要"),
        ("フィードバック歓迎", "一人開発の改善に活かします"),
    ]
    x = 110
    y = 400
    for title, sub in points:
        d.rounded_rectangle([x, y, x + 300, y + 120], radius=18, fill=(238, 236, 255))
        d.text((x + 24, y + 28), title, font=f_bold(22), fill=PRIMARY_DEEP)
        d.text((x + 24, y + 68), sub, font=f_reg(18), fill=MUTED)
        x += 320

    footer_url(d, w, h)
    out = OUT / "explain_05_story.png"
    img.save(out, "PNG", optimize=True)
    return out


def main() -> None:
    paths = [
        make_icon(),
        make_explain_01(),
        make_explain_02(),
        make_explain_03(),
        make_explain_04(),
        make_explain_05(),
    ]
    for p in paths:
        size_kb = p.stat().st_size / 1024
        with Image.open(p) as im:
            print(f"{p.name}: {im.size[0]}x{im.size[1]}  {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
