#!/usr/bin/env python3
"""Draw the 22 November 2026 world-news summary image.

Renders a one-page newspaper front page at 2x supersampling and
downscales to 1024x1024. Fully deterministic: fixed seed, no clock,
no network, no randomness in layout. Run: python3 draw.py
Writes entry.png next to this file.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

S = 2                      # supersample factor
W, H = 1024 * S, 1024 * S  # render size
OUT_W, OUT_H = 1024, 1024

PAPER = (247, 243, 234)
INK = (18, 28, 52)
RED = (178, 34, 34)
RED_DK = (140, 22, 22)
BLUE = (31, 78, 150)
TEAL = (14, 116, 110)
GOLD = (198, 142, 20)
GREY = (90, 96, 110)
LIGHT_LINE = (205, 198, 184)
NAVY_BG = (18, 28, 52)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size * S)


F_SERIF = lambda s: font("DejaVuSerif-Bold.ttf", s)      # noqa: E731
F_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)        # noqa: E731
F_REG = lambda s: font("DejaVuSans.ttf", s)              # noqa: E731


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap, returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill, leading=1.22):
    for i, line in enumerate(lines):
        draw.text((x, y + i * int(fnt.size * leading)), line, font=fnt, fill=fill)
    return y + len(lines) * int(fnt.size * leading)


def starburst(draw, cx, cy, r_out, r_in, n, fill):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill)


def icon_missile(draw, x0, y0, s):
    """Explosion over a dark sea: lead story icon."""
    draw.rectangle([x0, y0, x0 + s, y0 + s], fill=(24, 42, 78))
    draw.rectangle([x0, y0 + int(s * 0.68), x0 + s, y0 + s], fill=(13, 27, 54))
    for i in range(3):  # waves
        yy = y0 + int(s * (0.74 + i * 0.08))
        draw.arc([x0 + 8 * S, yy, x0 + s - 8 * S, yy + 14 * S], 0, 180,
                 fill=(90, 140, 200), width=3 * S)
    starburst(draw, x0 + s // 2, y0 + int(s * 0.42), int(s * 0.34),
              int(s * 0.16), 12, (255, 176, 32))
    starburst(draw, x0 + s // 2, y0 + int(s * 0.42), int(s * 0.20),
              int(s * 0.09), 10, (255, 226, 120))
    draw.ellipse([x0 + s // 2 - 9 * S, y0 + int(s * 0.42) - 9 * S,
                  x0 + s // 2 + 9 * S, y0 + int(s * 0.42) + 9 * S],
                 fill=(255, 255, 255))
    # missile arc
    draw.line([(x0 + int(s * 0.12), y0 + int(s * 0.30)),
               (x0 + int(s * 0.42), y0 + int(s * 0.10))],
              fill=(255, 255, 255), width=4 * S)
    draw.polygon([(x0 + int(s * 0.42), y0 + int(s * 0.10)),
                  (x0 + int(s * 0.34), y0 + int(s * 0.13)),
                  (x0 + int(s * 0.40), y0 + int(s * 0.18))], fill=(255, 255, 255))


def icon_globe(draw, x0, y0, s):
    draw.rectangle([x0, y0, x0 + s, y0 + s], fill=(14, 116, 110))
    cx, cy, r = x0 + s // 2, y0 + s // 2, int(s * 0.36)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(126, 200, 227),
                 outline=(255, 255, 255), width=4 * S)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r],
                 outline=(255, 255, 255), width=3 * S)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=(255, 255, 255), width=3 * S)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 0, 180,
             fill=(255, 255, 255), width=3 * S)
    # rising sun / thermometer accent: small red flame of urgency
    draw.polygon([(x0 + int(s * 0.78), y0 + int(s * 0.82)),
                  (x0 + int(s * 0.86), y0 + int(s * 0.62)),
                  (x0 + int(s * 0.94), y0 + int(s * 0.82))], fill=(255, 176, 32))


def icon_summit(draw, x0, y0, s):
    draw.rectangle([x0, y0, x0 + s, y0 + s], fill=(31, 78, 150))
    # three flag stripes: US, China, Russia
    cols = [(178, 34, 34), (222, 41, 16), (255, 255, 255)]
    bw = s // 3
    for i, c in enumerate(cols):
        draw.rectangle([x0 + i * bw, y0 + int(s * 0.18),
                        x0 + (i + 1) * bw, y0 + int(s * 0.62)], fill=c)
        draw.line([(x0 + i * bw, y0 + int(s * 0.18)),
                   (x0 + i * bw, y0 + int(s * 0.62))],
                  fill=(18, 28, 52), width=2 * S)
    draw.line([(x0 + int(s * 0.10), y0 + int(s * 0.78)),
               (x0 + int(s * 0.90), y0 + int(s * 0.78))],
              fill=(255, 255, 255), width=4 * S)
    draw.ellipse([x0 + int(s * 0.42), y0 + int(s * 0.70),
                  x0 + int(s * 0.58), y0 + int(s * 0.86)], fill=(255, 255, 255))


def icon_badge(draw, x0, y0, s):
    draw.rectangle([x0, y0, x0 + s, y0 + s], fill=(90, 60, 20))
    cx, cy = x0 + s // 2, y0 + int(s * 0.46)
    starburst(draw, cx, cy, int(s * 0.36), int(s * 0.15), 5, (255, 209, 61))
    draw.ellipse([cx - 8 * S, cy - 8 * S, cx + 8 * S, cy + 8 * S],
                 fill=(90, 60, 20))
    # handcuff links
    draw.ellipse([x0 + int(s * 0.16), y0 + int(s * 0.78),
                  x0 + int(s * 0.38), y0 + s - int(s * 0.06)],
                 outline=(255, 255, 255), width=5 * S)
    draw.ellipse([x0 + int(s * 0.62), y0 + int(s * 0.78),
                  x0 + int(s * 0.84), y0 + s - int(s * 0.06)],
                 outline=(255, 255, 255), width=5 * S)
    draw.line([(x0 + int(s * 0.38), y0 + int(s * 0.86)),
               (x0 + int(s * 0.62), y0 + int(s * 0.86))],
              fill=(255, 255, 255), width=5 * S)


def icon_chart(draw, x0, y0, s):
    draw.rectangle([x0, y0, x0 + s, y0 + s], fill=(140, 22, 22))
    base = y0 + int(s * 0.80)
    bars = [0.30, 0.48, 0.38, 0.58, 0.44, 0.66]
    bw = int(s * 0.11)
    for i, h in enumerate(bars):
        bx = x0 + int(s * 0.10) + i * int(s * 0.135)
        draw.rectangle([bx, base - int(s * h), bx + bw, base],
                       fill=(255, 255, 255))
    draw.line([(x0 + int(s * 0.08), y0 + int(s * 0.22)),
               (x0 + int(s * 0.50), y0 + int(s * 0.48)),
               (x0 + int(s * 0.92), y0 + int(s * 0.78))],
              fill=(255, 209, 61), width=6 * S)
    draw.polygon([(x0 + int(s * 0.92), y0 + int(s * 0.78)),
                  (x0 + int(s * 0.80), y0 + int(s * 0.74)),
                  (x0 + int(s * 0.86), y0 + int(s * 0.88))], fill=(255, 209, 61))


def icon_trade(draw, x0, y0, s):
    draw.rectangle([x0, y0, x0 + s, y0 + s], fill=(31, 78, 150))
    # cargo ship: hull + containers
    draw.polygon([(x0 + int(s * 0.10), y0 + int(s * 0.62)),
                  (x0 + int(s * 0.90), y0 + int(s * 0.62)),
                  (x0 + int(s * 0.80), y0 + int(s * 0.80)),
                  (x0 + int(s * 0.20), y0 + int(s * 0.80))],
                 fill=(255, 255, 255))
    draw.rectangle([x0 + int(s * 0.22), y0 + int(s * 0.42),
                    x0 + int(s * 0.38), y0 + int(s * 0.60)], fill=(178, 34, 34))
    draw.rectangle([x0 + int(s * 0.42), y0 + int(s * 0.42),
                    x0 + int(s * 0.58), y0 + int(s * 0.60)], fill=(255, 209, 61))
    draw.rectangle([x0 + int(s * 0.62), y0 + int(s * 0.42),
                    x0 + int(s * 0.78), y0 + int(s * 0.60)], fill=(255, 255, 255))
    draw.rectangle([x0 + int(s * 0.08), y0 + int(s * 0.86),
                    x0 + int(s * 0.92), y0 + int(s * 0.90)],
                   fill=(126, 200, 227))


def icon_city(draw, x0, y0, s):
    draw.rectangle([x0, y0, x0 + s, y0 + s], fill=(52, 58, 74))
    base = y0 + s - int(s * 0.10)
    heights = [0.42, 0.62, 0.34, 0.55, 0.46]
    bw = int(s * 0.16)
    for i, h in enumerate(heights):
        bx = x0 + int(s * 0.06) + i * int(s * 0.18)
        draw.rectangle([bx, base - int(s * h), bx + bw, base], fill=(18, 28, 52))
    starburst(draw, x0 + int(s * 0.68), y0 + int(s * 0.30), int(s * 0.20),
              int(s * 0.09), 10, (255, 176, 32))
    draw.line([(x0 + int(s * 0.10), y0 + int(s * 0.16)),
               (x0 + int(s * 0.34), y0 + int(s * 0.16))],
              fill=(255, 255, 255), width=3 * S)


def icon_cricket(draw, x0, y0, s):
    draw.rectangle([x0, y0, x0 + s, y0 + s], fill=(27, 94, 46))
    # bat
    draw.rounded_rectangle([x0 + int(s * 0.44), y0 + int(s * 0.22),
                            x0 + int(s * 0.58), y0 + int(s * 0.78)],
                           radius=8 * S, fill=(222, 184, 135),
                           outline=(18, 28, 52), width=3 * S)
    draw.rectangle([x0 + int(s * 0.48), y0 + int(s * 0.08),
                    x0 + int(s * 0.54), y0 + int(s * 0.24)], fill=(222, 184, 135))
    # ball
    cx, cy, r = x0 + int(s * 0.74), y0 + int(s * 0.30), int(s * 0.11)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 34, 34),
                 outline=(255, 255, 255), width=3 * S)
    # stumps
    for i in range(3):
        bx = x0 + int(s * (0.14 + i * 0.09))
        draw.rectangle([bx, y0 + int(s * 0.66), bx + 5 * S, y0 + int(s * 0.86)],
                       fill=(255, 209, 61))


ICONS = {
    "missile": icon_missile,
    "globe": icon_globe,
    "summit": icon_summit,
    "badge": icon_badge,
    "chart": icon_chart,
    "trade": icon_trade,
    "city": icon_city,
    "cricket": icon_cricket,
}

# (kicker, headline, summary, icon, accent)
STORIES = [
    ("CLIMATE", "COP31 talks run into overtime",
     "Antalya summit passes its deadline, split over fossil fuels.",
     "globe", TEAL),
    ("DIPLOMACY", "Trump, Xi and Putin meet in Shenzhen",
     "The three leaders agree to open talks on cutting nuclear risk.",
     "summit", BLUE),
    ("MEXICO", "Cartel boss \u2018El Chapo Isidro\u2019 captured",
     "Mexican forces seize Fausto Isidro Meza Flores in Sinaloa; 11 killed.",
     "badge", (90, 60, 20)),
    ("MARKETS", "AI sell-off drags stocks down",
     "S&P 500 falls 3.7% into correction; Japan\u2019s Nikkei drops 5.1%.",
     "chart", RED),
    ("TRADE", "EU and Indonesia sign trade deal",
     "Ten years of talks end in a pact scrapping 98.5% of tariffs.",
     "trade", BLUE),
    ("UKRAINE", "Missile hits Zelensky\u2019s hometown",
     "Russian strike on Kryvyi Rih kills two and wounds dozens.",
     "city", (52, 58, 74)),
    ("SPORT", "India pile up 720/9 vs New Zealand",
     "India declare in Wellington and lead the first Test by 352 runs.",
     "cricket", (27, 94, 46)),
]

BRIEFS = [
    "INDONESIA \u2014 Cikande factory fire kills 3; 36 missing.  \u00b7  "
    "NIGERIA \u2014 Mourners\u2019 boat capsizes; at least 24 dead.",
    "BRAZIL \u2014 Jailed ex-president Bolsonaro in intensive care.",
]


def main():
    random.seed(20261122)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 36 * S  # margin

    # ---- Masthead ----
    d.text((W // 2, 30 * S), "THE WORLD TODAY", font=F_SERIF(58),
           fill=INK, anchor="ma")
    d.text((W // 2, 100 * S), "SUNDAY, 22 NOVEMBER 2026",
           font=F_BOLD(30), fill=RED, anchor="ma")
    d.text((W // 2, 138 * S),
           "THE DAY'S WORLD NEWS \u2014 IN ONE IMAGE",
           font=F_REG(19), fill=GREY, anchor="ma")
    d.line([(mx, 168 * S), (W - mx, 168 * S)], fill=INK, width=4 * S)
    d.line([(mx, 176 * S), (W - mx, 176 * S)], fill=RED, width=2 * S)

    # ---- Lead story ----
    ly = 192 * S
    icon_s = 190 * S
    ICONS["missile"](d, mx, ly, icon_s)
    tx = mx + icon_s + 22 * S
    tw = W - mx - tx
    d.text((tx, ly), "LEAD STORY \u2014 MIDDLE EAST", font=F_BOLD(20),
           fill=RED)
    hl = wrap(d, "Iran strikes Bahrain as Gulf tensions flare",
              F_BOLD(40), tw)
    y = text_block(d, tx, ly + 30 * S, hl, F_BOLD(40), INK, leading=1.08)
    sm = wrap(d, "Tehran hits sites in Bahrain and two tankers near the "
                 "Strait of Hormuz; Bahrain says civilian property was hit.",
              F_REG(23), tw)
    text_block(d, tx, y + 8 * S, sm, F_REG(23), (52, 58, 74), leading=1.25)
    d.line([(mx, 402 * S), (W - mx, 402 * S)], fill=LIGHT_LINE, width=2 * S)

    # ---- Story grid: 2 cols x 3 rows + 1 wide row ----
    grid_y = 420 * S
    col_w = (W - 2 * mx - 24 * S) // 2
    row_h = 140 * S
    for i, (kicker, headline, summary, icon, accent) in enumerate(STORIES[:6]):
        col = i % 2
        row = i // 2
        x0 = mx + col * (col_w + 24 * S)
        y0 = grid_y + row * row_h
        isz = 104 * S
        ICONS[icon](d, x0, y0 + 6 * S, isz)
        tx2 = x0 + isz + 14 * S
        tw2 = x0 + col_w - tx2
        d.text((tx2, y0), kicker, font=F_BOLD(16), fill=accent)
        hl2 = wrap(d, headline, F_BOLD(24), tw2)
        y2 = text_block(d, tx2, y0 + 22 * S, hl2, F_BOLD(24), INK,
                        leading=1.08)
        sm2 = wrap(d, summary, F_REG(19), tw2)
        text_block(d, tx2, y2 + 4 * S, sm2, F_REG(19), (52, 58, 74),
                   leading=1.18)
        if row < 2:
            d.line([(x0, y0 + row_h - 12 * S), (x0 + col_w, y0 + row_h - 12 * S)],
                   fill=LIGHT_LINE, width=2 * S)

    # ---- Wide bottom story (sport) ----
    wy = grid_y + 3 * row_h + 6 * S
    d.line([(mx, wy - 8 * S), (W - mx, wy - 8 * S)], fill=LIGHT_LINE,
           width=2 * S)
    kicker, headline, summary, icon, accent = STORIES[6]
    isz = 84 * S
    ICONS[icon](d, mx, wy, isz)
    tx3 = mx + isz + 14 * S
    d.text((tx3, wy), "SPORT \u2014 ", font=F_BOLD(21), fill=accent)
    tw3 = W - mx - tx3
    d.text((tx3 + d.textlength("SPORT \u2014 ", font=F_BOLD(21)), wy),
           headline, font=F_BOLD(21), fill=INK)
    sm3 = wrap(d, summary, F_REG(20), tw3)
    text_block(d, tx3, wy + 30 * S, sm3, F_REG(20), (52, 58, 74),
               leading=1.2)

    # ---- Also today strip: label line + two brief lines ----
    by = 906 * S
    d.rectangle([mx, by, W - mx, by + 82 * S], fill=NAVY_BG)
    d.text((mx + 14 * S, by + 8 * S), "ALSO TODAY", font=F_BOLD(18),
           fill=(255, 209, 61))
    d.text((mx + 14 * S, by + 32 * S), BRIEFS[0], font=F_REG(16),
           fill=(255, 255, 255))
    d.text((mx + 14 * S, by + 54 * S), BRIEFS[1], font=F_REG(16),
           fill=(255, 255, 255))

    # ---- Footer ----
    d.text((W // 2, 996 * S), "Sources: wire reports of 22 November 2026",
           font=F_REG(15), fill=GREY, anchor="ma")

    out = img.resize((OUT_W, OUT_H), Image.LANCZOS)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "entry.png")
    out.save(path, format="PNG", optimize=True)
    print("wrote", path, out.size, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
