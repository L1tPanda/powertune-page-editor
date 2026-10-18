"""Background for the page 2 diagnostic grid: one panel per reading, tinted by group.

Matches the grid in make_page2_diag.py: 5 columns x 160 px, 7 rows over 480 px,
label at +5 px and value at +21 px inside each cell. 800x480 so the dash shows it 1:1.
"""
import sys
from PIL import Image, ImageDraw, ImageColor

out = sys.argv[1]
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0   # 2 = 1600x960 for HD screenshots
W, H, COLS, ROWS = 800, 480, 5, 7
COL_W, ROW_H = W / COLS, H / ROWS
GROUP_COLOURS = ["lightskyblue", "gold", "lightgreen", "orange", "plum"]   # same as the label colours
SS = 4                                                                     # supersample for smooth corners

BG = (8, 10, 13)          # page
CELL = (22, 26, 32)       # reading panel
EDGE = (40, 46, 56)       # panel outline
GAP = 3                   # space between panels
RADIUS = 7
STRIP_H = 19              # tinted band behind the label (label text is ~14 px at +5)

def mix(c, base, a):
    return tuple(round(base[i] + (c[i] - base[i]) * a) for i in range(3))

im = Image.new("RGB", (W * SS, H * SS), BG)
d = ImageDraw.Draw(im)
s = lambda *v: [round(x * SS) for x in v]

for c in range(COLS):
    accent = ImageColor.getrgb(GROUP_COLOURS[c])
    for r in range(ROWS):
        x0, y0 = c * COL_W + GAP, r * ROW_H + GAP
        x1, y1 = (c + 1) * COL_W - GAP, (r + 1) * ROW_H - GAP
        # panel
        d.rounded_rectangle(s(x0, y0, x1, y1), radius=RADIUS * SS, fill=CELL, outline=EDGE, width=SS)
        # tinted label strip across the top of the panel (clipped to the rounded top)
        strip = Image.new("L", im.size, 0)
        sd = ImageDraw.Draw(strip)
        sd.rounded_rectangle(s(x0 + 1, y0 + 1, x1 - 1, y1 - 1), radius=(RADIUS - 1) * SS, fill=255)
        sd.rectangle(s(x0, y0 + STRIP_H, x1, y1), fill=0)
        im.paste(mix(accent, CELL, 0.22), mask=strip)
        # accent bar on the left edge
        d.rounded_rectangle(s(x0 + 2, y0 + 4, x0 + 5, y1 - 4), radius=2 * SS, fill=mix(accent, CELL, 0.75))

im = im.resize((round(W * SCALE), round(H * SCALE)), Image.LANCZOS)
im.save(out, optimize=True)
print("saved", out, im.size)
