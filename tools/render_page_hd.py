"""Render a PowerTune page file as the dash draws it, at any scale (default 2x = 1600x960).

Follows the dash source (dash-files/home/pi/src/Gauges):
- items are drawn in file order, later on top
- page background is scaled to fit 800x480 (PreserveAspectFit)
- Text label sizes are POINTS: 1 pt = 1.97 px (startpowertune.sh: 86 mm tall for 480 px)
- Square gauge value is centred in the box; unit pinned 5 px from the right edge at value size / 1.8
- State gauge picture sits in an h x h box, scaled to fit, shown when the channel >= trigger
- Round gauge needle runs from -inset% to -inset%+length% of the radius, tapering to tipWidth px

usage: render_page_hd.py PAGE.txt BACKGROUND.png|- FONT.ttf OUT.png [scale] [values.json]
"""
import json, math, os, sys
from PIL import Image, ImageColor, ImageDraw, ImageFont

page, bg_path, font_path, out = sys.argv[1:5]
S = float(sys.argv[5]) if len(sys.argv) > 5 else 2.0
VALUES = json.load(open(sys.argv[6])) if len(sys.argv) > 6 else {}
LOGO = os.environ.get("PT_LOGO_DIR", "dash-files/home/pi/Logo/")   # the dash's /home/pi/Logo
PT = (480 / (86 / 25.4)) / 72
W, H = round(800 * S), round(480 * S)

def colour(c, default=None):
    c = (c or "").strip()
    if not c or c == "transparent":
        return default
    return ImageColor.getrgb(c)

def font(px):
    return ImageFont.truetype(font_path, max(1, round(px * S)))

def num(v, d=0.0):
    try:
        return float(v)
    except ValueError:
        return d

def value(src, dec):
    v = VALUES.get(src.strip())
    return None if v is None else (f"{v:.{dec}f}" if isinstance(v, (int, float)) else str(v))

def logo(path):
    if not path or "/home/pi/Logo/" not in path or path.endswith("/Logo"):
        return None
    try:
        return Image.open(LOGO + path.split("/home/pi/Logo/")[1]).convert("RGBA")
    except OSError:
        return None

def fit(img, w, h):
    s = min(w / img.width, h / img.height)
    return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)

canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
if bg_path != "-":
    bg = fit(Image.open(bg_path).convert("RGBA"), W, H)
    canvas.alpha_composite(bg, ((W - bg.width) // 2, (H - bg.height) // 2))
draw = ImageDraw.Draw(canvas)

for line in open(page, encoding="utf-8").read().splitlines():
    p = line.split(",")
    kind, c = p[0], p[1:]
    if kind == "Text label gauge":
        x, y, text, fam, pt, col, src, bold, dec = num(c[0]), num(c[1]), c[2], c[3], num(c[4]), c[5], c[6], c[7], int(num(c[8]))
        shown = value(src, dec) if src.strip() else text
        if shown is None or not shown.strip():
            continue
        rgb = colour(col, (255, 255, 255))
        draw.text((x * S, y * S), shown, font=font(pt * PT), fill=rgb, anchor="la",
                  stroke_width=round(S * 0.6) if bold == "true" else 0, stroke_fill=rgb)
    elif kind == "Square gauge":
        w, h, x, y = num(c[0]), num(c[1]), num(c[2]), num(c[3])
        dec, unit, src = int(num(c[4 + 1])), c[6].strip(), c[12]
        frame, back, textc, size = colour(c[16]), colour(c[17]), colour(c[20], (255, 255, 255)), num(c[23], 40)
        box = [x * S, y * S, (x + w) * S, (y + h) * S]
        if back:
            draw.rectangle(box, fill=back)
        if frame:
            draw.rectangle(box, outline=frame, width=round(2 * S))
        shown = value(src, dec)
        if shown is not None:
            draw.text(((x + w / 2) * S, (y + h / 2) * S), shown, font=font(size), fill=textc, anchor="mm")
        if unit:
            draw.text(((x + w - 5) * S, (y + h / 2) * S), unit, font=font(size / 1.8), fill=textc, anchor="rm",
                      stroke_width=round(S * 0.4), stroke_fill=textc)
    elif kind in ("State gauge", "State GIF"):
        x, y, h, src, trig = num(c[0]), num(c[1]), num(c[2]), c[3], num(c[4])
        v = VALUES.get(src.strip(), 0)
        img = logo(c[6] if num(v) >= trig else c[5])
        if img:
            img = fit(img, h * S, h * S)
            canvas.alpha_composite(img, (round(x * S + (h * S - img.width) / 2), round(y * S + (h * S - img.height) / 2)))
    elif kind == "gauge image":
        x, y, h = num(c[0]), num(c[1]), num(c[2])
        img = logo(c[3])
        if img:
            img = fit(img, h * S, h * S)
            canvas.alpha_composite(img, (round(x * S + (h * S - img.width) / 2), round(y * S + (h * S - img.height) / 2)))
    elif kind == "Round gauge":
        w, x, y, src = num(c[0]), num(c[1]), num(c[2]), c[3]
        vmax, vmin, a0, a1 = num(c[4]), num(c[5]), num(c[8]), num(c[9])
        inset, tipw, length, basew, ncol = num(c[16]), num(c[29]), num(c[30]), num(c[31]), colour(c[34], (255, 0, 0))
        if c[48] != "true":
            continue
        r = w / 2
        cx, cy = (x + r) * S, (y + r) * S
        v = num(VALUES.get(src.strip(), vmin))
        a = math.radians(a0 + (a1 - a0) * min(1, max(0, (v - vmin) / ((vmax - vmin) or 1))))
        ux, uy, px_, py_ = math.sin(a), -math.cos(a), math.cos(a), math.sin(a)
        rb, rt = -r * inset / 100 * S, (-r * inset / 100 + r * length / 100) * S
        hb, ht = r * basew / 100 / 2 * S, max(0.5, tipw / 2) * S
        pts = [(cx + ux * rb + px_ * hb, cy + uy * rb + py_ * hb), (cx + ux * rt + px_ * ht, cy + uy * rt + py_ * ht),
               (cx + ux * rt - px_ * ht, cy + uy * rt - py_ * ht), (cx + ux * rb - px_ * hb, cy + uy * rb - py_ * hb)]
        draw.polygon(pts, fill=ncol)

canvas.convert("RGB").save(out, optimize=True)
print("saved", out, canvas.size)
