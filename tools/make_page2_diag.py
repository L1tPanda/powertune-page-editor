"""Generate page 2: a diagnostic grid of every ME442 value the dash's ME13 decoder passes on.

Channel names were matched to ME1_4.dbc signals by comparing ME13's UDP output
(strace, 2026-10-17) with the raw CAN frames captured at the same session.
Text label sizes are in points; on this dash 1 pt = 1.97 px.
"""
import sys

# (label, PowerTune data source, decimals, DBC signal it carries)
COLUMNS = [
    [("RPM", "rpm", 0, "RPM"),
     ("TPS", "TPS", 1, "TPS"),
     ("MAP psi", "MAP", 1, "MAP"),
     ("MAP TGT psi", "targetbstlelkpa", 1, "MAP_Target"),
     ("BOOST psi", "BoostPreskpa", 1, "MAP - 101.3 (dash calc)"),
     ("GEAR", "Gear", 0, "Gear_Pos"),
     ("SPEED kph", "speed", 0, "Vehicle_Speed (if speed source = ECU)")],
    [("CLT C", "Watertemp", 1, "CLT"),
     ("IAT C", "Intaketemp", 1, "IAT"),
     ("OIL T C", "oiltemp", 1, "Oil_T"),
     ("OIL P psi", "oilpres", 0, "Oil_P"),
     ("FUEL P psi", "FuelPress", 0, "Fuel_Press"),
     ("FUEL T C", "Fueltemp", 0, "Fuel_Temp"),
     ("BATT V", "BatteryV", 1, "VBAT")],
    [("AFR 1", "AFRcyl1", 2, "AFRCurr_1"),
     ("AFR 2", "AFRcyl2", 2, "AFRCurr_2"),
     ("AFR TGT", "AFRLEFTBANKTARGET", 2, "AFR_Target"),
     ("LAM TRIM", "LAMBDA", 2, "Lambda_Trim"),
     ("ETHANOL", "fuelcomposition", 1, "Fuel_Eth_Perc"),
     ("REV LIMIT", "Flag1", 0, "RPM_HardLimit"),
     ("BOOST DUTY", "BoostDuty", 1, "Boost_Ctrl_Duty")],
    [("IGN ADV", "Ign", 1, "IgnAdvAngle"),
     ("DWELL ms", "Dwell", 1, "IgnDwell"),
     ("INJ DUTY", "InjDuty", 1, "Pri_InjDuty"),
     ("INJ PW ms", "Primaryinp", 1, "Pri_InjPw"),
     ("INJ ANGLE", "InjAngle", 0, "Pri_InjAngle"),
     ("SEC DUTY", "InjDuty2", 1, "Sec_InjDuty"),
     ("SEC PW ms", "Secinjpulse", 1, "Sec_InjPw")],
    [("SEC ANGLE", "Inj2", 0, "Sec_InjAngle"),
     ("KNOCK PEAK", "Knock", 0, "Knock_Peak_Reading"),
     ("KNOCK MOD", "knockretardbank1", 1, "Knock_Ign_Adv_Mod (unconfirmed)"),
     ("EGT 1 C", "egt2", 0, "EGT_1 (ME13 swaps EGT 1/2)"),
     ("EGT 2 C", "egt1", 0, "EGT_2"),
     ("GPT 1", "Analog0", 0, "GPT_1"),
     ("GPT 2", "Analog1", 0, "GPT_2")],
]
# label colour per group so the columns read as blocks
# Note: the Nissan font has no "%" glyph, so percentage labels carry no unit.
# Pressures show in psi: the dash has pressure units set to imperial (unitSelector2=1),
# so DashBoard converts kPa x 0.145038 before display.
GROUP_COLOURS = ["lightskyblue", "gold", "lightgreen", "orange", "plum"]

COL_W, ROWS, H = 160, 7, 480
ROW_H = H / ROWS
LABEL_PT, VALUE_PT = 7, 13          # about 14 px and 26 px on screen
X_PAD, LABEL_Y, VALUE_Y = 12, 5, 21

def text_label(x, y, text, pt, colour, source=" ", dec=0):
    return ",".join(["Text label gauge", str(round(x)), str(round(y)), text, "Nissan", str(pt), colour,
                     source, "true", str(dec), "20000", "-20000", ""])

# Text labels have no outline option on the dash, so each label gets four black copies
# nudged 1 px diagonally underneath it (items later in the file draw on top).
OUTLINE = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
OUTLINE_COLOUR = "black"

lines = []
for c, column in enumerate(COLUMNS):
    for r, (label, source, dec, _signal) in enumerate(column):
        x, y = c * COL_W + X_PAD, r * ROW_H
        for dx, dy in OUTLINE:
            lines.append(text_label(x + dx, y + LABEL_Y + dy, label, LABEL_PT, OUTLINE_COLOUR))
        lines.append(text_label(x, y + LABEL_Y, label, LABEL_PT, GROUP_COLOURS[c]))
        lines.append(text_label(x, y + VALUE_Y, "0", VALUE_PT, "white", source, dec))

out = sys.argv[1]
open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print(f"{len(lines)} gauges ({sum(1 for l in lines if l.split(',')[7].strip())} readings) -> {out}")
for c, column in enumerate(COLUMNS):
    for label, source, dec, signal in column:
        print(f"  col {c+1}  {label:12} {source:18} {signal}")
