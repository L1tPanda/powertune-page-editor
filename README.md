# PowerTune page editor

A one-file, offline editor for [PowerTune Digital](https://github.com/PowerTuneDigital/PowerTuneDigitalOfficial)
dash pages, plus a few page tools. Unofficial; not affiliated with PowerTune Digital. GPL-3 (it embeds
PowerTune's channel list).

## dash-editor.html

Open it in Chrome or Edge (double-click). It reads and writes the same `.txt` page format as the dash's
**Import / Export** buttons.

- **Open page .txt**, or **Open live pages** from a dash's `/.config/Power-Tune/PowerTune.conf`
  (pages are stored there as `datastore1`, `datastore2`, ... with their backgrounds).
- Drag gauges, arrow keys to nudge (Shift = 10 px), edit position, size, channel, text, colour, font,
  needle settings; **+ Text / + Value / + Square**; Duplicate, Delete, **Undo / Redo** (Ctrl+Z / Ctrl+Y).
- Preview drawn the way the dash draws it: text labels in **points** (1 pt = 1.97 px with the dash's
  screen settings), square gauges in pixels, backgrounds scaled to fit, state pictures in h x h boxes,
  the round-gauge needle from its inset / length / width.
- **Save .txt**, copy it to `/home/pi/UserDashboards` on the dash, then on the dash:
  double-tap - Clear - Import - pick it - Load - Save.

Images and font: the editor looks for the dash's `/home/pi/Logo` at `../dash-files/home/pi/Logo/` and
the Nissan font at `../dash-files/usr/share/fonts/PowertuneDigital/Nissan.ttf` (copy them off your dash).
If it can't read them (e.g. opened from a preview pane), use **Images folder...** and pick your Logo folder.

## tools/

Python 3 + Pillow (`pip install pillow`).

| Script | Does |
|---|---|
| `render_page_hd.py PAGE.txt BACKGROUND.png FONT.ttf OUT.png [scale] [values.json]` | Renders a page as the dash would, at any scale (2 = 1600x960). Image folder: env `PT_LOGO_DIR`. `hd_values.json` = sample readings. |
| `make_page2_diag.py OUT.txt` | Generates a 5x7 diagnostic page of every ME442 channel the ME13 decoder passes on (labels outlined, pressures in psi). |
| `make_page2_background.py OUT.png [scale]` | The matching background: one tinted panel per reading. |
