#!/usr/bin/env python3
"""Draw the 20 November 2026 world-news poster (1024x1024 PNG).

Every story on the poster was verified against real reporting on the
morning of Friday 20 November 2026 (Reuters, BBC, CNN, Le Monde,
The Hindu, Space.com, Council on Foreign Relations, USA Today).
All artwork is drawn here with PIL primitives; no photos, no downloads.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 36

PAPER = (246, 241, 227)
INK = (26, 26, 26)
RED = (179, 39, 30)
NAVY = (22, 50, 79)
GOLD = (200, 155, 60)
GREY = (90, 86, 76)
LIGHT_LINE = (190, 182, 160)
PANEL_BG = (255, 253, 246)
BLUE = (38, 84, 124)
TEAL = (18, 110, 105)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines fitting max_w pixels."""
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


def draw_centered(draw, cx, y, text, fnt, fill=INK, spacing=0):
    if spacing:
        total = sum(draw.textlength(ch, font=fnt) + spacing for ch in text) - spacing
        x = cx - total / 2
        for ch in text:
            draw.text((x, y), ch, font=fnt, fill=fill)
            x += draw.textlength(ch, font=fnt) + spacing
        return total
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


def flag_us(d, x, y, w, h):
    stripe = h / 13
    for i in range(13):
        if i % 2 == 0:
            d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe], fill=RED)
    d.rectangle([x, y, x + w * 0.4, y + stripe * 7], fill=NAVY)
    for r in range(4):
        for c in range(5):
            px = x + 5 + c * (w * 0.4 - 10) / 4
            py = y + 4 + r * (stripe * 7 - 8) / 3
            d.ellipse([px, py, px + 3, py + 3], fill=(255, 255, 255))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    cx, cy = x + w * 0.22, y + h * 0.28
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 222, 0))
    for sx, sy in [(0.55, 0.12), (0.72, 0.28), (0.72, 0.55), (0.55, 0.68)]:
        px, py = x + w * sx, y + h * sy
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 222, 0))


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def draw_scales(d, cx, cy, s, color=NAVY):
    # Justice scales: pillar, beam, two pans.
    d.line([cx, cy - s, cx, cy + s], fill=color, width=5)
    d.line([cx - s, cy - s * 0.55, cx + s, cy - s * 0.55], fill=color, width=5)
    d.ellipse([cx - 6, cy - s - 6, cx + 6, cy - s + 6], fill=color)
    for side in (-1, 1):
        px = cx + side * s
        d.line([px, cy - s * 0.55, px - 13, cy + s * 0.25], fill=color, width=3)
        d.line([px, cy - s * 0.55, px + 13, cy + s * 0.25], fill=color, width=3)
        d.pieslice([px - 20, cy + s * 0.25, px + 20, cy + s * 0.25 + 18],
                   0, 180, fill=color)
    d.rectangle([cx - s * 0.5, cy + s - 4, cx + s * 0.5, cy + s + 4], fill=color)


def draw_calendar(d, x, y, w, h, big="2027"):
    d.rounded_rectangle([x, y, x + w, y + h], radius=8, outline=RED, width=4)
    d.rectangle([x, y, x + w, y + h * 0.30], fill=RED)
    f = font(SANS_B, 30)
    tw = d.textlength(big, font=f)
    d.text((x + (w - tw) / 2, y + h * 0.36), big, font=f, fill=INK)
    for bx in (x + w * 0.25, x + w * 0.75):
        d.rectangle([bx - 3, y - 5, bx + 3, y + 7], fill=INK)


def draw_cyclone(d, cx, cy, r, color=BLUE):
    for i, rr in enumerate(range(r, 8, -13)):
        width = 7 if i < 2 else 5
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr],
              start=200 + i * 55, end=200 + i * 55 + 250, fill=color, width=width)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=color)


def draw_talk(d, x, y, w, h, color=TEAL):
    # Two overlapping speech bubbles.
    d.rounded_rectangle([x, y, x + w * 0.62, y + h * 0.62], radius=12,
                        outline=color, width=4)
    d.polygon([(x + 12, y + h * 0.62), (x + 30, y + h * 0.62),
               (x + 16, y + h * 0.85)], fill=color)
    d.rounded_rectangle([x + w * 0.34, y + h * 0.30, x + w, y + h], radius=12,
                        fill=color)
    d.polygon([(x + w - 30, y + h), (x + w - 12, y + h),
               (x + w - 16, y + h * 0.78)], fill=color)
    for dx in (0.14, 0.30, 0.46):
        px = x + w * dx
        d.ellipse([px, y + h * 0.24, px + 10, y + h * 0.24 + 10], fill=color)
    for dx in (0.48, 0.64, 0.80):
        px = x + w * dx
        d.ellipse([px, y + h * 0.58, px + 10, y + h * 0.58 + 10],
                  fill=(255, 255, 255))


def draw_probe(d, cx, cy, s, color=NAVY):
    # Spacecraft body with solar panels; asteroid with a red cross.
    d.rectangle([cx - s * 0.85, cy - s * 0.42, cx - s * 0.16, cy + s * 0.42],
                fill=(120, 140, 170), outline=INK, width=2)
    d.rectangle([cx + s * 0.16, cy - s * 0.42, cx + s * 0.85, cy + s * 0.42],
                fill=(120, 140, 170), outline=INK, width=2)
    d.rectangle([cx - s * 0.16, cy - s * 0.28, cx + s * 0.16, cy + s * 0.28],
                fill=color, outline=INK, width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=GOLD)
    ax, ay, ar = cx + s * 1.15, cy + s * 0.5, s * 0.36
    d.ellipse([ax - ar, ay - ar, ax + ar, ay + ar], fill=(150, 135, 120),
              outline=INK, width=2)
    d.line([ax - ar * 0.7, ay - ar * 0.7, ax + ar * 0.7, ay + ar * 0.7],
           fill=RED, width=5)
    d.line([ax - ar * 0.7, ay + ar * 0.7, ax + ar * 0.7, ay - ar * 0.7],
           fill=RED, width=5)


def draw_controller(d, cx, cy, s, color=NAVY):
    d.rounded_rectangle([cx - s, cy - s * 0.55, cx + s, cy + s * 0.55],
                        radius=20, fill=color)
    for dx, dy in ((-0.55, -0.1), (-0.38, -0.1), (-0.465, -0.28), (-0.465, 0.08)):
        d.rectangle([cx + s * dx - 5, cy + s * dy - 5,
                     cx + s * dx + 5, cy + s * dy + 5], fill=(255, 255, 255))
    for dx, dy, c in ((0.42, -0.22, RED), (0.58, -0.05, GOLD),
                      (0.42, 0.12, (255, 255, 255)), (0.26, -0.05, (255, 255, 255))):
        d.ellipse([cx + s * dx - 6, cy + s * dy - 6,
                   cx + s * dx + 6, cy + s * dy + 6], fill=c)


def story_panel(d, x, y, w, h, tag, headline, body, icon_fn, tag_color=RED):
    """Grid panel: tag, headline (top, icon at top-right), body below icon."""
    d.rectangle([x, y, x + w, y + h], fill=PANEL_BG, outline=LIGHT_LINE, width=2)
    d.rectangle([x, y, x + w, y + 6], fill=tag_color)
    d.text((x + 18, y + 16), tag, font=font(SANS_B, 20), fill=tag_color)
    f_head = font(SANS_B, 28)
    lines = wrap(d, headline, f_head, w - 150)
    ly = y + 48
    for ln in lines:
        d.text((x + 18, ly), ln, font=f_head, fill=INK)
        ly += 34
    # Icon occupies the top-right corner, above the body text.
    icon_fn(d, x + w - 116, y + 44)
    f_body = font(SANS, 22)
    blines = wrap(d, body, f_body, w - 36)
    by = max(ly + 4, y + 128)
    for ln in blines[:2]:
        d.text((x + 18, by), ln, font=f_body, fill=(60, 58, 50))
        by += 28


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    draw_centered(d, W // 2, 28, "THE WORLD TODAY",
                  font(SERIF_B, 80), fill=INK)
    d.line([MARGIN, 128, W - MARGIN, 128], fill=INK, width=4)
    d.line([MARGIN, 134, W - MARGIN, 134], fill=INK, width=2)
    draw_centered(d, W // 2, 148, "FRIDAY  20  NOVEMBER  2026",
                  font(SANS_B, 35), fill=RED, spacing=2)
    draw_centered(d, W // 2, 192,
                  "The day's news, in one page  ·  Seven stories from every corner of the globe",
                  font(SANS, 22), fill=GREY)

    # ---- Lead story: trilateral summit ----
    ly, lh = 228, 196
    d.rectangle([MARGIN, ly, W - MARGIN, ly + lh], fill=PANEL_BG,
                outline=LIGHT_LINE, width=2)
    d.rectangle([MARGIN, ly, W - MARGIN, ly + 6], fill=RED)
    d.text((MARGIN + 18, ly + 16), "DIPLOMACY  ·  SHENZHEN, CHINA",
           font=font(SANS_B, 20), fill=RED)
    f_head = font(SANS_B, 40)
    d.text((MARGIN + 18, ly + 48), "TRUMP, XI AND PUTIN MEET —",
           font=f_head, fill=INK)
    d.text((MARGIN + 18, ly + 94), "A FIRST", font=f_head, fill=INK)
    f_body = font(SANS, 23)
    for i, ln in enumerate(wrap(
            d, "The three leaders hold the first-ever trilateral summit "
               "at APEC and pledge talks on cutting nuclear risks.",
            f_body, 660)):
        d.text((MARGIN + 18, ly + 146 + i * 29), ln, font=f_body,
               fill=(60, 58, 50))
    fx, fy, fw, fh = 748, ly + 52, 84, 54
    flag_us(d, fx, fy, fw, fh)
    flag_ru(d, fx + 104, fy, fw, fh)
    flag_cn(d, fx, fy + 66, fw, fh)
    d.text((fx + 104, fy + 66), "90 MIN", font=font(SANS_B, 26), fill=NAVY)
    d.text((fx + 104, fy + 98), "NO BREAKTHROUGH", font=font(SANS_B, 12), fill=GREY)

    # ---- 2x2 grid ----
    gy, gh, gap = 440, 204, 16
    gw = (W - 2 * MARGIN - gap) // 2
    gx = [MARGIN, MARGIN + gw + gap]
    gy2 = [gy, gy + gh + gap]

    story_panel(d, gx[0], gy2[0], gw, gh,
                "JUSTICE  ·  THE HAGUE",
                "MYANMAR GUILTY OF GENOCIDE",
                "World court rules on the Rohingya — a first for a state.",
                lambda dd, x, y: draw_scales(dd, x + 50, y + 38, 30))
    story_panel(d, gx[1], gy2[0], gw, gh,
                "WASHINGTON  ·  IRAN",
                "TRUMP PUTS IRAN DECISION OFF TO 2027",
                "\u201cWe\u2019ll see what happens\u201d after Jan 1, he says — "
                "no rush on war.",
                lambda dd, x, y: draw_calendar(dd, x + 10, y + 4, 88, 80),
                tag_color=NAVY)
    story_panel(d, gx[0], gy2[1], gw, gh,
                "WEATHER  ·  INDIA",
                "CYCLONE AKVAN HITS ODISHA",
                "300,000 evacuated as the storm lands near Gopalpur at noon.",
                lambda dd, x, y: draw_cyclone(dd, x + 54, y + 40, 42))
    story_panel(d, gx[1], gy2[1], gw, gh,
                "WAR IN UKRAINE",
                "EUROPE OPEN TO TALKS WITH RUSSIA",
                "Leaders signal talks as strikes damage Kyiv embassies.",
                lambda dd, x, y: draw_talk(dd, x - 4, y + 2, 112, 84),
                tag_color=TEAL)

    # ---- Bottom band: space + culture ----
    by, bh = 880, 88
    bw = (W - 2 * MARGIN - gap) // 2
    d.rectangle([MARGIN, by, MARGIN + bw, by + bh], fill=PANEL_BG,
                outline=LIGHT_LINE, width=2)
    d.rectangle([MARGIN, by, MARGIN + bw, by + 6], fill=NAVY)
    d.text((MARGIN + 14, by + 14), "SPACE  ·  JAPAN", font=font(SANS_B, 18),
           fill=NAVY)
    d.text((MARGIN + 14, by + 38), "HAYABUSA2 LANDING OFF",
           font=font(SANS_B, 22), fill=INK)
    d.text((MARGIN + 14, by + 64), "Engine trouble ends the asteroid plan.",
           font=font(SANS, 19), fill=(60, 58, 50))
    draw_probe(d, MARGIN + bw - 78, by + 48, 26)

    x2 = MARGIN + bw + gap
    d.rectangle([x2, by, x2 + bw, by + bh], fill=PANEL_BG,
                outline=LIGHT_LINE, width=2)
    d.rectangle([x2, by, x2 + bw, by + 6], fill=GOLD)
    d.text((x2 + 14, by + 14), "CULTURE  ·  GAMES", font=font(SANS_B, 18),
           fill=(150, 110, 20))
    d.text((x2 + 14, by + 38), "GTA 6 OUTSELLS $1.8BN EPIC",
           font=font(SANS_B, 22), fill=INK)
    d.text((x2 + 14, by + 64), "Sales pass The Odyssey\u2019s global run.",
           font=font(SANS, 19), fill=(60, 58, 50))
    draw_controller(d, x2 + bw - 56, by + 48, 30)

    # ---- Footer ----
    d.line([MARGIN, 984, W - MARGIN, 984], fill=LIGHT_LINE, width=2)
    draw_centered(d, W // 2, 992,
                  "Sources: Reuters  ·  BBC  ·  CNN  ·  Le Monde  ·  The Hindu  ·  "
                  "Space.com  ·  Council on Foreign Relations",
                  font(SANS, 18), fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
