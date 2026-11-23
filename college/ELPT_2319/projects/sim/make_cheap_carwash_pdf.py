"""Builds Project7_CHEAP_Car_Wash_Ladder.pdf: I/O map, drawn ladder rungs, simulation."""
import io, sys, contextlib
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import cheap_carwash_p7_sim as sim

OUT = sys.argv[1] if len(sys.argv) > 1 else "Project7_CHEAP_Car_Wash_Ladder.pdf"
PW, PH = landscape(letter)
L, R = 46, PW - 30            # power rails
CW, CH = 92, 54               # contact cell width, branch row height
COIL_X = R - 120
PURPLE, BLUE, GREY = colors.HexColor("#7a2a7a"), colors.HexColor("#1565c0"), colors.HexColor("#555555")

def NO(a, n): return ("NO", a, n)
def NC(a, n): return ("NC", a, n)
def PE(a, n): return ("PE", a, n)
def P(*b): return ("PAR", list(b))

def w(it): return CW if it[0] in ("NO", "NC", "PE") else max(sw(b) for b in it[1]) + 16
def h(it): return CH if it[0] in ("NO", "NC", "PE") else sum(sh(b) for b in it[1])
def sw(s): return sum(w(i) for i in s)
def sh(s): return max(h(i) for i in s)

def contact(c, it, x, y):
    k, a, n = it; cx = x + CW / 2
    c.setStrokeColor(colors.black); c.setLineWidth(1.2)
    c.line(x, y, cx - 7, y); c.line(cx + 7, y, x + CW, y)
    c.line(cx - 7, y - 9, cx - 7, y + 9); c.line(cx + 7, y - 9, cx + 7, y + 9)
    if k == "NC": c.line(cx - 10, y - 10, cx + 10, y + 10)
    if k == "PE":
        c.line(cx, y - 7, cx, y + 7); c.line(cx, y + 7, cx - 3, y + 2); c.line(cx, y + 7, cx + 3, y + 2)
    c.setFillColor(PURPLE); c.setFont("Helvetica", 6.6)
    lines = n.split("|")
    for i, ln in enumerate(reversed(lines)):
        c.drawCentredString(cx, y + 13 + 7.5 * i, ln)
    c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(cx, y - 19, a)

def series(c, s, x, y, to_x=None):
    for it in s:
        if it[0] in ("NO", "NC", "PE"): contact(c, it, x, y); x += CW
        else:
            bw = w(it); yy = y; last = y
            for b in it[1]:
                c.line(x, yy, x + 8, yy)
                ex = series(c, b, x + 8, yy, x + bw - 8)
                c.line(x + bw - 8, yy, x + bw, yy)
                last = yy; yy -= sh(b)
            c.line(x, y, x, last); c.line(x + bw, y, x + bw, last)
            x += bw
    if to_x and x < to_x: c.line(x, y, to_x, y); x = to_x
    return x

def coil(c, addr, name, y):
    c.line(COIL_X - 12, y, COIL_X - 6, y)
    c.arc(COIL_X - 12, y - 10, COIL_X + 2, y + 10, 100, 160); c.arc(COIL_X + 26, y - 10, COIL_X + 40, y + 10, -80, 160)
    c.setFont("Helvetica-Bold", 7.5); c.drawCentredString(COIL_X + 14, y - 3, "OUT")
    c.line(COIL_X + 38, y, R, y)
    c.setFillColor(PURPLE); c.setFont("Helvetica", 6.6)
    for i, ln in enumerate(reversed(name.split("|"))): c.drawCentredString(COIL_X + 14, y + 22 + 7.5 * i, ln)
    c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 7.5); c.drawCentredString(COIL_X + 14, y + 12, addr)

def box(c, title, nick, lines, legs, ys):
    bx, top = R - 175, ys[0] + 22; bot = ys[-1] - 22
    c.setFillColor(colors.white); c.rect(bx, bot, 165, top - bot, fill=1); c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 7.5); c.drawString(bx + 5, top - 10, title)
    c.setFillColor(PURPLE); c.setFont("Helvetica", 6.6); c.drawRightString(bx + 160, top - 10, nick)
    c.setFillColor(colors.black); c.setFont("Helvetica", 7.5)
    for i, ln in enumerate(lines):
        k, v = ln; c.drawString(bx + 5, top - 22 - 10 * i, k); c.drawRightString(bx + 160, top - 22 - 10 * i, v)
    for (lab, _), y in zip(legs, ys):
        c.setFont("Helvetica-Bold", 6.5); c.rect(bx - 26, y - 5, 26, 10); c.drawCentredString(bx - 13, y - 2.5, lab)
    c.line(bx + 165, (top + bot) / 2, R, (top + bot) / 2)

# ---------------- program ----------------
STOP, MRST, CRST = NC("X1", "STOP"), NC("X5", "MASTER|RESET"), NC("C8", "CHEAP CARWASH|RESET")
RST_BR = [P([NO("X1", "STOP")], [NO("X5", "MASTER|RESET")], [NO("C8", "CHEAP CARWASH|RESET")])]
PROG = [
 ("SECTION", "7 CHEAP CAR WASH-RST", "SYSTEM SECTION"),
 (1, "C", [P([NO("X0", "GO")], [NO("C0", "SYSTEM|ENABLED")]), STOP, MRST], ("C0", "SYSTEM|ENABLED"),
  "GO starts the facility and C0 seals it in. STOP or MASTER RESET drops it."),
 ("SECTION", None, "COIN COUNTER SECTION"),
 (2, "B", ("CNT", "CHEAP CAR WASH|COUNTER", [("Counter Struct", "CT3"), ("Preset", "3")],
   [("UP", [NO("C0", "SYSTEM|ENABLED"), NO("X3", "COIN DROP")]), ("RST", RST_BR)]),
  "Counts each dollar (leading edge of X3) while enabled. CT3.Done = $3 PAID. Cleared by STOP, MASTER RESET or end of wash."),
 ("SECTION", None, "PERMISSIVE SECTION"),
 (3, "C", [P([NO("X4", "CAR-IN-PLACE|PERMISSIVE")], [NO("C1", "CAR IS|IN PLACE")]), STOP, MRST, CRST], ("C1", "CAR IS|IN PLACE"),
  "Photocell X4 latches CAR IS IN PLACE until STOP, MASTER RESET or end of wash."),
 ("SECTION", None, "CHEAP CAR WASH SEQUENCE SECTION"),
 (4, "C", [P([NO("CT3.Done", "$3 PAID"), NO("C1", "CAR IS|IN PLACE"), NO("C0", "SYSTEM|ENABLED")], [NO("C2", "CHEAP WASH|RUNNING")]), STOP, MRST, CRST],
  ("C2", "CHEAP WASH|RUNNING"), "$3 paid AND car in place AND system enabled starts the wash; C2 seals in."),
 (5, "C", [P([PE("X2", "PAUSE|(rising edge)")], [NO("C3", "PAUSED")]), NC("X6", "RESUME"), STOP, MRST], ("C3", "PAUSED"),
  "Rising edge of PAUSE latches C3 (works even if the PAUSE switch is left on). RESUME, STOP or MASTER RESET unlatches it."),
 (6, "B", ("TMRA", "SOAP|TIME", [("Timer Struct", "T0"), ("Preset", "1.000s")],
   [("E", [NO("C2", "CHEAP WASH|RUNNING"), NC("C3", "PAUSED")]), ("R", RST_BR)]),
  "Soap step time. Accumulating: holds its time while paused."),
 (7, "B", ("TMRA", "SOAK|TIME", [("Timer Struct", "T1"), ("Preset", "1.000s")],
   [("E", [NO("T0.Done", "SOAP|DONE"), NC("C3", "PAUSED")]), ("R", RST_BR)]), "Soak step time."),
 (8, "B", ("TMRA", "RINSE|TIME", [("Timer Struct", "T2"), ("Preset", "1.000s")],
   [("E", [NO("T1.Done", "SOAK|DONE"), NC("C3", "PAUSED")]), ("R", RST_BR)]), "Rinse step time."),
 (9, "C", [NO("C2", "CHEAP WASH|RUNNING"), NC("T0.Done", "SOAP|DONE")], ("C41", "CHEAP|SOAP STEP"), "Step 1 window: running, soap not done."),
 (10, "C", [NO("T0.Done", "SOAP|DONE"), NC("T1.Done", "SOAK|DONE")], ("C42", "CHEAP|SOAK STEP"), "Step 2 window."),
 (11, "C", [NO("T1.Done", "SOAK|DONE"), NC("T2.Done", "RINSE|DONE")], ("C43", "CHEAP|RINSE STEP"), "Step 3 window."),
 (12, "C", [NO("T2.Done", "RINSE|DONE")], ("C8", "CHEAP CARWASH|RESET"),
  "End of wash: one-scan pulse resets CT3, C1, C2 and all timers, ready for the next customer."),
 ("SECTION", None, "OUTPUT SECTION (each output on one dedicated rung)"),
 (13, "C", [NO("C41", "CHEAP|SOAP STEP"), NC("C3", "PAUSED")], ("Y1", "SOAP PUMP"), "Soap pump."),
 (14, "C", [NO("C42", "CHEAP|SOAK STEP"), NO("ST5", "$100ms"), NC("C3", "PAUSED")], ("Y2", "SOAK LAMP"), "Soak lamp blinks via the ST5 100 ms clock."),
 (15, "C", [NO("C43", "CHEAP|RINSE STEP"), NC("C3", "PAUSED")], ("Y3", "RINSE PUMP"), "Rinse pump."),
 (16, "END", None, None, ""),
]

def rung_height(r):
    if r[0] == "SECTION": return 30 if r[1] is None else 46
    if r[1] == "END": return 40
    if r[1] == "C": return sh(r[2]) + 40
    legs = r[2][3]; return sum(sh(s) for _, s in legs) + 44

def draw_rung(c, r, top):
    if r[0] == "SECTION":
        c.setFillColor(BLUE); c.setFont("Helvetica-Bold", 10.5)
        y = top - 14
        if r[1]: c.setFillColor(colors.black); c.drawString(L + 8, y, r[1]); y -= 16; c.setFillColor(BLUE)
        c.drawString(L + 8, y, r[2]); c.setFillColor(colors.black); return
    num = r[0]; y = top - 30
    c.setFont("Helvetica-Oblique", 9); c.drawRightString(L - 8, y - 3, str(num))
    if r[1] == "END":
        c.line(L, y, COIL_X - 12, y); c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(COIL_X + 14, y - 3, "END"); c.line(COIL_X + 38, y, R, y); return
    if r[1] == "C":
        series(c, r[2], L, y, COIL_X - 12); coil(c, *r[3], y)
    else:
        title, nick, lines, legs = r[2]; ys = []; yy = y
        for lab, s in legs:
            ys.append(yy); series(c, s, L, yy, R - 201); yy -= sh(s)
        box(c, title, nick.replace("|", " "), lines, legs, ys)
    c.setFont("Helvetica-Oblique", 6.8); c.setFillColor(GREY)
    c.drawString(L + 8, top - rung_height(r) + 6, r[-1]); c.setFillColor(colors.black)

def header(c, page, sub):
    c.setFont("Helvetica-Bold", 13); c.drawString(30, PH - 30, "ELPT 2319  |  Project 7: CHEAP Car Wash (Do-more)")
    c.setFont("Helvetica", 9); c.drawString(30, PH - 44, sub); c.drawRightString(PW - 30, PH - 30, f"Page {page}")
    c.line(30, PH - 50, PW - 30, PH - 50)

def table(c, x, y, rows, widths, size=8.5):
    for i, row in enumerate(rows):
        c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", size)
        if i == 0: c.setFillColor(colors.HexColor("#e8e8f4")); c.rect(x, y - 4, sum(widths), 14, fill=1, stroke=0); c.setFillColor(colors.black)
        xx = x
        for cell, wd in zip(row, widths): c.drawString(xx + 3, y, cell); xx += wd
        y -= 14
    return y

c = canvas.Canvas(OUT, pagesize=landscape(letter)); page = 1
c.setTitle("Project 7 CHEAP Car Wash Ladder"); c.setAuthor("ELPT 2319 student")
header(c, page, "Spec: Harry Franz Car Wash (rev 7/24/2026), CHEAP = $3, steps 1-3 (soap, soak, rinse), TMRA timers, 1-second timers only")
y = PH - 72
c.setFont("Helvetica-Bold", 11); c.drawString(30, y, "I/O Map"); y -= 16
y = table(c, 30, y, [("Address", "Nickname", "Device / Purpose"),
  ("X0", "GO", "PB, permissive: enables the car wash facility"), ("X1", "STOP", "PB (NO), stops and resets the system"),
  ("X2", "PAUSE", "PB, halts the wash (timers hold)"), ("X3", "COIN DROP", "Photocell, one pulse per dollar"),
  ("X4", "CAR-IN-PLACE PERMISSIVE", "Photocell, car drove forward"), ("X5", "MASTER RESET", "PB (NO), resets everything"),
  ("X6", "RESUME", "PB, restarts after PAUSE"), ("Y1", "SOAP PUMP", "Output, step 1"), ("Y2", "SOAK LAMP", "Output, step 2 (blinks)"),
  ("Y3", "RINSE PUMP", "Output, step 3")], [60, 150, 240])
y2 = PH - 72; c.setFont("Helvetica-Bold", 11); c.drawString(490, y2, "Internal Tags"); y2 -= 16
y2 = table(c, 490, y2, [("Address", "Nickname"), ("C0", "SYSTEM ENABLED"), ("C1", "CAR IS IN PLACE"), ("C2", "CHEAP WASH RUNNING"),
  ("C3", "PAUSED"), ("C8", "CHEAP CARWASH RESET"), ("C41/C42/C43", "CHEAP soap/soak/rinse step"),
  ("CT3", "CHEAP CAR WASH COUNTER (pre 3)"), ("T0/T1/T2", "TMRA soap/soak/rinse, 1.000 s"), ("ST5", "$100ms system clock")], [80, 190])
y = min(y, y2) - 18
c.setFont("Helvetica-Bold", 11); c.drawString(30, y, "Sequence of Operation"); y -= 15; c.setFont("Helvetica", 9)
for ln in ["1. Press GO (X0): SYSTEM ENABLED (C0) seals in.",
           "2. Customer drops 3 dollars: COIN DROP (X3) pulses CT3 up to 3, so CT3.Done ($3 PAID) turns on.",
           "3. Car drives forward: CAR-IN-PLACE (X4) latches C1. With $3 paid and the car in place, CHEAP WASH RUNNING (C2) seals in.",
           "4. Soap (C41 -> Y1) for T0, soak (C42 -> Y2, blinking on ST5) for T1, rinse (C43 -> Y3) for T2.",
           "5. T2.Done fires CHEAP CARWASH RESET (C8) for one scan, which clears CT3, C1, C2 and all TMRA timers.",
           "PAUSE (X2, rising edge) latches C3: timer enables and all outputs drop, TMRA keeps its time. RESUME (X6) continues the same step.",
           "STOP (X1) or MASTER RESET (X5) clears the counter, timers, latches and outputs at any time."]:
    c.drawString(36, y, ln); y -= 13
y -= 6; c.setFont("Helvetica-Bold", 11); c.drawString(30, y, "Matrix (which output is on in each step)"); y -= 16
table(c, 30, y, [("Step", "Bit", "Timer", "Y1 SOAP", "Y2 SOAK", "Y3 RINSE"), ("1 Soap", "C41", "T0 1 s", "ON", "-", "-"),
  ("2 Soak", "C42", "T1 1 s", "-", "BLINK", "-"), ("3 Rinse", "C43", "T2 1 s", "-", "-", "ON")], [70, 60, 70, 70, 70, 70])
c.showPage()

# ladder pages
items = list(PROG); idx = 0
while idx < len(items):
    page += 1; header(c, page, "Ladder Logic (Do-more). Purple = nickname, bold = address. Slash = NC contact. Arrow = rising-edge contact.")
    c.setLineWidth(1.4); top = PH - 62; start = top
    def need(i):
        hgt = rung_height(items[i])
        if items[i][0] == "SECTION" and i + 1 < len(items): hgt += rung_height(items[i + 1])
        return hgt
    while idx < len(items) and top - need(idx) > 18:
        draw_rung(c, items[idx], top); top -= rung_height(items[idx]); idx += 1
    c.setStrokeColor(colors.black); c.setLineWidth(2); c.line(L, start, L, top + 4); c.line(R, start, R, top + 4)
    c.showPage()

# simulation page
page += 1; header(c, page, "Scan-by-scan simulation (sim/cheap_carwash_p7_sim.py, 10 ms scans)")
import importlib; importlib.reload(sim)
buf = io.StringIO()
with contextlib.redirect_stdout(buf): sim.main()
checks = [l.strip() for l in buf.getvalue().splitlines() if "===" in l or "CHECK" in l or "RESULT" in l]
y = PH - 72; c.setFont("Helvetica-Bold", 11); c.drawString(30, y, "Test results"); y -= 15
for ln in checks:
    c.setFont("Helvetica-Bold" if "===" in ln or "RESULT" in ln else "Helvetica", 8.5)
    if "FAIL" in ln: c.setFillColor(colors.red)
    c.drawString(36, y, ln); c.setFillColor(colors.black); y -= 11.5
# timing diagram from a fresh run of test 1
importlib.reload(sim); trace = {k: [] for k in ["X0 GO", "X3 COIN", "X4 CAR", "C2 RUN", "Y1 SOAP", "Y2 SOAK", "Y3 RINSE", "C8 RESET"]}
def rec():
    v = [sim.X[0], sim.X[3], sim.X[4], sim.C[2], sim.Y[1], sim.Y[2], sim.Y[3], sim.C[8]]
    for k, b in zip(trace, v): trace[k].append(b)
def step(ms):
    for _ in range(ms // sim.SCAN): sim.scan(); rec()
def pr(x): sim.X[x] = True; step(100); sim.X[x] = False; step(100)
step(100); pr(0); sim.X[4] = True; step(100)
for _ in range(3): pr(3)
step(3400); sim.X[4] = False; step(200)
gx, gy, gw = 430, PH - 90, 330; n = len(trace["C2 RUN"]); dx = gw / n
c.setFont("Helvetica-Bold", 11); c.drawString(gx - 80, gy + 12, "Timing diagram, Test 1 (full CHEAP wash)")
for i, (k, vals) in enumerate(trace.items()):
    yb = gy - 22 - i * 26; c.setFont("Helvetica", 7.5); c.drawRightString(gx - 6, yb + 3, k)
    c.setStrokeColor(colors.HexColor("#1565c0")); c.setLineWidth(0.8); p = c.beginPath(); p.moveTo(gx, yb + (12 if vals[0] else 0))
    for j, v in enumerate(vals): p.lineTo(gx + j * dx, yb + (12 if v else 0)); p.lineTo(gx + (j + 1) * dx, yb + (12 if v else 0))
    c.drawPath(p); c.setStrokeColor(colors.black)
c.setFont("Helvetica", 7)
for s in range(0, n * sim.SCAN // 1000 + 1): c.drawCentredString(gx + s * 1000 / sim.SCAN * dx, gy - 22 - 8 * 26 + 8, f"{s}s")
c.showPage(); c.save(); print("wrote", OUT, "pages:", page)
