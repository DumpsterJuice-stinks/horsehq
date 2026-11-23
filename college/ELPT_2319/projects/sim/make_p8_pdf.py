"""Builds Project7_CHEAP_Car_Wash_Ladder.pdf: I/O map, drawn ladder rungs, simulation."""
import io, sys, contextlib
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import ultra_cheap_p8_sim as sim

OUT = sys.argv[1] if len(sys.argv) > 1 else "Project8_ULTRA_CHEAP_Car_Wash_Ladder.pdf"
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
RA = [NO("C9", "RESET|ALL")]
NRA = NC("C9", "RESET|ALL")
def T(n, nick, en):
    return ("B", ("TMRA", nick, [("Timer Struct", f"T{n}"), ("Preset", "1.000s")], [("E", en + [NC("C3", "PAUSED")]), ("R", RA)]))
U = [(10, "UNDER CAR", "C10"), (11, "SOAP 1", "C11"), (12, "SOAK 1", "C12"), (13, "RINSE 1", "C13"), (14, "SOAP 2", "C51"),
     (15, "SOAK 2", "C52"), (16, "RINSE 2", "C53"), (17, "WAX", "C14"), (18, "SPOT-FREE", "C15"), (19, "AIR DRY", "C16")]
PROG = [
 ("SECTION", "8 ULTRA + CHEAP CAR WASH", "SYSTEM SECTION"),
 (1, "C", [P([NO("X1", "STOP")], [NO("X5", "MASTER|RESET")], [NO("C8", "CARWASH|COMPLETE")])], ("C9", "RESET|ALL"),
  "One bit that resets counters, latches and timers: STOP, MASTER RESET, or end of either wash (C8 from the previous scan)."),
 (2, "C", [P([NO("X0", "GO")], [NO("C0", "SYSTEM|ENABLED")]), NC("X1", "STOP"), NC("X5", "MASTER|RESET")], ("C0", "SYSTEM|ENABLED"),
  "GO enables the facility. Only STOP or MASTER RESET disables it (NOT the end of a wash)."),
 ("SECTION", None, "COIN COUNTER SECTION (both counters see every dollar; coins locked out once the car is in place)"),
 (3, "B", ("CNT", "ULTRA|COUNTER", [("Counter Struct", "CT0"), ("Preset", "6")],
   [("UP", [NO("C0", "SYSTEM|ENABLED"), NO("X3", "COIN DROP"), NC("C1", "CAR IS|IN PLACE")]), ("RST", RA)]),
  "CT0.Done = $6 PAID (ULTRA)."),
 (4, "B", ("CNT", "CHEAP|COUNTER", [("Counter Struct", "CT3"), ("Preset", "3")],
   [("UP", [NO("C0", "SYSTEM|ENABLED"), NO("X3", "COIN DROP"), NC("C1", "CAR IS|IN PLACE")]), ("RST", RA)]),
  "CT3.Done = $3 PAID (CHEAP)."),
 ("SECTION", None, "PERMISSIVE SECTION"),
 (5, "C", [P([NO("X4", "CAR-IN-PLACE|PERMISSIVE"), NO("CT3.Done", "$3 PAID")], [NO("C1", "CAR IS|IN PLACE")]), NRA], ("C1", "CAR IS|IN PLACE"),
  "Car drives forward after paying at least $3. A car left on the pad with no money does not latch."),
 ("SECTION", None, "WASH SELECTION SECTION"),
 (6, "C", [P([NO("C1", "CAR IS|IN PLACE"), NO("CT0.Done", "$6 PAID"), NO("C0", "SYSTEM|ENABLED")], [NO("C4", "ULTRA|RUNNING")]), NRA],
  ("C4", "ULTRA|RUNNING"), "$6 or more and car in place: ULTRA."),
 (7, "C", [P([NO("C1", "CAR IS|IN PLACE"), NO("CT3.Done", "$3 PAID"), NC("CT0.Done", "$6 PAID"), NO("C0", "SYSTEM|ENABLED")],
             [NO("C2", "CHEAP|RUNNING")]), NC("C4", "ULTRA|RUNNING"), NRA],
  ("C2", "CHEAP|RUNNING"), "$3 to $5 and car in place: CHEAP. NC C4 makes the two washes mutually exclusive."),
 (8, "C", [P([PE("X2", "PAUSE|(leading edge)")], [NO("C3", "PAUSED")]), NC("X6", "RESUME"), NRA], ("C3", "PAUSED"),
  "Leading edge of PAUSE latches C3; RESUME or RESET ALL clears it."),
 ("SECTION", None, "CHEAP SEQUENCE SECTION (TMRA, 1 s each)"),
 (9,) + T(0, "CHEAP|SOAP", [NO("C2", "CHEAP|RUNNING")]) + ("CHEAP soap time.",),
 (10,) + T(1, "CHEAP|SOAK", [NO("T0.Done", "CHEAP SOAP|DONE")]) + ("CHEAP soak time.",),
 (11,) + T(2, "CHEAP|RINSE", [NO("T1.Done", "CHEAP SOAK|DONE")]) + ("CHEAP rinse time.",),
 ("SECTION", None, "ULTRA SEQUENCE SECTION (TMRA, 1 s each, steps 0-9)"),
]
for i, (n, nick, bit) in enumerate(U):
    en = [NO("C4", "ULTRA|RUNNING")] if n == 10 else [NO(f"T{n-1}.Done", U[i-1][1] + "|DONE")]
    PROG.append((12 + i,) + T(n, "ULTRA|" + nick, en) + (f"ULTRA step {i}: {nick.lower()}.",))
PROG += [
 ("SECTION", None, "STEP BITS (output interposing relays per the spec chart)"),
 (22, "C", [NO("C2", "CHEAP|RUNNING"), NC("T0.Done", "CHEAP SOAP|DONE")], ("C41", "CHEAP|SOAP"), "CHEAP step 1 window."),
 (23, "C", [NO("T0.Done", "CHEAP SOAP|DONE"), NC("T1.Done", "CHEAP SOAK|DONE")], ("C42", "CHEAP|SOAK"), "CHEAP step 2 window."),
 (24, "C", [NO("T1.Done", "CHEAP SOAK|DONE"), NC("T2.Done", "CHEAP RINSE|DONE")], ("C43", "CHEAP|RINSE"), "CHEAP step 3 window."),
]
for i, (n, nick, bit) in enumerate(U):
    first = NO("C4", "ULTRA|RUNNING") if n == 10 else NO(f"T{n-1}.Done", U[i-1][1] + "|DONE")
    PROG.append((25 + i, "C", [first, NC(f"T{n}.Done", nick + "|DONE")], (bit, "ULTRA|" + nick), f"ULTRA step {i} window."))
PROG += [
 (35, "C", [P([NO("T2.Done", "CHEAP RINSE|DONE")], [NO("T19.Done", "AIR DRY|DONE")])], ("C8", "CARWASH|COMPLETE"),
  "End of either wash. Next scan, RESET ALL (rung 1) clears everything for the next customer."),
 ("SECTION", None, "OUTPUT SECTION (each Y output on exactly one rung)"),
 (36, "C", [NO("C10", "ULTRA|UNDER CAR"), NC("C3", "PAUSED")], ("Y0", "UNDER CAR/|WHEEL PUMP"), "Under car / wheel pump."),
 (37, "C", [P([NO("C11", "ULTRA|SOAP 1")], [NO("C51", "ULTRA|SOAP 2")], [NO("C41", "CHEAP|SOAP")]), NC("C3", "PAUSED")], ("Y1", "SOAP PUMP"), "Soap pump: either wash."),
 (38, "C", [P([NO("C12", "ULTRA|SOAK 1")], [NO("C52", "ULTRA|SOAK 2")], [NO("C42", "CHEAP|SOAK")]), NO("ST5", "$100ms"), NC("C3", "PAUSED")],
  ("Y2", "SOAK LAMP"), "Soak lamp blinks on ST5."),
 (39, "C", [P([NO("C13", "ULTRA|RINSE 1")], [NO("C53", "ULTRA|RINSE 2")], [NO("C43", "CHEAP|RINSE")]), NC("C3", "PAUSED")], ("Y3", "RINSE PUMP"), "Rinse pump."),
 (40, "C", [NO("C14", "ULTRA|WAX"), NC("C3", "PAUSED")], ("Y4", "WAX PUMP"), "Wax pump."),
 (41, "C", [NO("C15", "ULTRA|SPOT-FREE"), NC("C3", "PAUSED")], ("Y5", "SPOT FREE|RINSE PUMP"), "Spot-free rinse pump."),
 (42, "C", [NO("C16", "ULTRA|AIR DRY"), NC("C3", "PAUSED")], ("Y6", "AIR DRY|BLOWER"), "Air-dry blower."),
 (43, "END", None, None, ""),
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
    c.setFont("Helvetica-Bold", 13); c.drawString(30, PH - 30, "ELPT 2319  |  Project 8: ULTRA + CHEAP Car Wash (Do-more)")
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
c.setTitle("Project 8 ULTRA + CHEAP Car Wash Ladder"); c.setAuthor("ELPT 2319 student")
header(c, page, "Spec: Harry Franz Car Wash (rev 7/24/2026). Project 8 = complete coin counter, car-in-place permissive, ULTRA ($6) and CHEAP ($3). TMRA, 1 s timers.")
y = PH - 72
c.setFont("Helvetica-Bold", 11); c.drawString(30, y, "I/O Map"); y -= 16
y = table(c, 30, y, [("Address", "Nickname", "Device / Purpose"),
  ("X0", "GO", "PB, enables the facility"), ("X1", "STOP", "PB (NO), stops + resets"), ("X2", "PAUSE", "PB, leading-edge pause"),
  ("X3", "COIN DROP", "Photocell, 1 pulse per dollar"), ("X4", "CAR-IN-PLACE", "Photocell, car drove forward"),
  ("X5", "MASTER RESET", "PB (NO), resets everything"), ("X6", "RESUME", "PB, continue after pause"),
  ("Y0", "UNDER CAR/WHEEL PUMP", "ULTRA step 0"), ("Y1", "SOAP PUMP", "ULTRA 1, 4 / CHEAP 1"), ("Y2", "SOAK LAMP", "ULTRA 2, 5 / CHEAP 2 (blinks)"),
  ("Y3", "RINSE PUMP", "ULTRA 3, 6 / CHEAP 3"), ("Y4", "WAX PUMP", "ULTRA 7"), ("Y5", "SPOT FREE RINSE PUMP", "ULTRA 8"), ("Y6", "AIR DRY BLOWER", "ULTRA 9")],
  [52, 150, 180], 8)
y2 = PH - 72; c.setFont("Helvetica-Bold", 11); c.drawString(440, y2, "Internal Tags"); y2 -= 16
y2 = table(c, 440, y2, [("Address", "Nickname"), ("C0", "SYSTEM ENABLED"), ("C1", "CAR IS IN PLACE"), ("C2", "CHEAP RUNNING"),
  ("C3", "PAUSED"), ("C4", "ULTRA RUNNING"), ("C8", "CARWASH COMPLETE (end pulse)"), ("C9", "RESET ALL"),
  ("CT0 / CT3", "ULTRA counter pre 6 / CHEAP counter pre 3"), ("C10-C13, C51-C53, C14-C16", "ULTRA step bits (spec chart)"),
  ("C41-C43", "CHEAP step bits (spec chart)"), ("T0-T2", "CHEAP TMRA soap/soak/rinse"), ("T10-T19", "ULTRA TMRA steps 0-9"), ("ST5", "$100ms clock")], [130, 190], 8)
y = min(y, y2) - 16
c.setFont("Helvetica-Bold", 11); c.drawString(30, y, "Sequence of Operation"); y -= 14; c.setFont("Helvetica", 8.6)
for ln in ["1. GO (X0) seals in SYSTEM ENABLED (C0). It stays on between customers; only STOP or MASTER RESET drops it.",
           "2. Customer drops dollars on X3. CT0 (preset 6) and CT3 (preset 3) both count every dollar.",
           "3. Customer drives forward: X4 latches CAR IS IN PLACE (C1) if at least $3 is paid. From then on coins are locked out.",
           "4. $6+ -> ULTRA RUNNING (C4): steps 0-9, each 1 s, on T10-T19.  $3-$5 -> CHEAP RUNNING (C2): soap, soak, rinse on T0-T2.",
           "5. Last timer done (T19 or T2) -> CARWASH COMPLETE (C8) -> next scan RESET ALL (C9) clears counters, latches, timers.",
           "PAUSE (X2, leading edge) latches C3: timers hold (TMRA), outputs drop. RESUME (X6) continues the same step.",
           "Simulator order: GO on/off, COIN on/off per dollar, THEN turn the car X4 on (car arrives after paying)."]:
    c.drawString(36, y, ln); y -= 12
c.showPage(); page += 1
header(c, page, "Matrix: which output is on in each step")
y = PH - 74
rows = [("Wash", "Step", "Name", "Bit", "Timer", "Y0", "Y1", "Y2", "Y3", "Y4", "Y5", "Y6")]
for i, (n, nick, bit) in enumerate(U):
    o = [0, 1, 2, 3, 1, 2, 3, 4, 5, 6][i]
    rows.append(("ULTRA $6", str(i), nick, bit, f"T{n} 1 s") + tuple(("BLINK" if k == 2 else "ON") if k == o else "-" for k in range(7)))
for i, (nick, bit) in enumerate([("SOAP", "C41"), ("SOAK", "C42"), ("RINSE", "C43")]):
    rows.append(("CHEAP $3", str(i + 1), nick, bit, f"T{i} 1 s") + tuple(("BLINK" if k == 2 else "ON") if k == i + 1 else "-" for k in range(7)))
y = table(c, 30, y, rows, [70, 40, 80, 50, 60] + [50] * 7, 9)
y -= 20; c.setFont("Helvetica-Bold", 11); c.drawString(30, y, "Coins -> wash selected"); y -= 16
table(c, 30, y, [("Dollars dropped", "Result"), ("0 - 2", "No wash; car-in-place does not latch"), ("3, 4, 5", "CHEAP (SHINE $5 / CLEAN $4 come in Project 9)"),
  ("6 or more", "ULTRA")], [110, 330], 9)
c.showPage()

items = list(PROG); idx = 0
while idx < len(items):
    page += 1; header(c, page, "Ladder Logic (Do-more). Purple = nickname, bold = address. Slash = NC contact. Arrow = leading-edge contact.")
    c.setLineWidth(1.4); top = PH - 62; start = top
    def need(i):
        hgt = rung_height(items[i])
        if items[i][0] == "SECTION" and i + 1 < len(items): hgt += rung_height(items[i + 1])
        return hgt
    while idx < len(items) and top - need(idx) > 18:
        draw_rung(c, items[idx], top); top -= rung_height(items[idx]); idx += 1
    c.setStrokeColor(colors.black); c.setLineWidth(2); c.line(L, start, L, top + 4); c.line(R, start, R, top + 4)
    c.showPage()

page += 1; header(c, page, "Scan-by-scan simulation (sim/ultra_cheap_p8_sim.py, 10 ms scans, simulator-style toggle inputs)")
buf = io.StringIO()
with contextlib.redirect_stdout(buf): sim.main()
y = PH - 72; c.setFont("Helvetica-Bold", 11); c.drawString(30, y, "Test results"); y -= 14
for ln in [l.strip() for l in buf.getvalue().splitlines() if "===" in l or "CHECK" in l or "RESULT" in l]:
    c.setFont("Helvetica-Bold" if "===" in ln or "RESULT" in ln else "Helvetica", 7.4)
    if "FAIL" in ln: c.setFillColor(colors.red)
    c.drawString(34, y, ln[:95]); c.setFillColor(colors.black); y -= 9.6
sim.reset_state()
names = ["C4 ULTRA", "Y0 UNDER", "Y1 SOAP", "Y2 SOAK", "Y3 RINSE", "Y4 WAX", "Y5 SPOTFREE", "Y6 DRY", "C8 DONE"]
tr = {k: [] for k in names}
def rec():
    for k, v in zip(names, [sim.C[4], sim.Y[0], sim.Y[1], sim.Y[2], sim.Y[3], sim.Y[4], sim.Y[5], sim.Y[6], sim.C[8]]): tr[k].append(v)
def step(ms):
    for _ in range(ms // sim.SCAN): sim.scan(); rec()
sim.X[0] = True; step(100); sim.X[0] = False; step(100)
for _ in range(6): sim.X[3] = True; sim.scan(); sim.X[3] = False; sim.scan()
sim.X[4] = True; step(10600)
gx, gy, gw = 470, PH - 92, 300; n = len(tr["C4 ULTRA"]); dx = gw / n
c.setFont("Helvetica-Bold", 11); c.drawString(gx - 80, gy + 12, "Timing diagram: ULTRA ($6)")
for i, (k, vals) in enumerate(tr.items()):
    yb = gy - 22 - i * 26; c.setFont("Helvetica", 7.5); c.drawRightString(gx - 6, yb + 3, k)
    c.setStrokeColor(colors.HexColor("#1565c0")); c.setLineWidth(0.8); p = c.beginPath(); p.moveTo(gx, yb + (12 if vals[0] else 0))
    for j, v in enumerate(vals): p.lineTo(gx + j * dx, yb + (12 if v else 0)); p.lineTo(gx + (j + 1) * dx, yb + (12 if v else 0))
    c.drawPath(p); c.setStrokeColor(colors.black)
c.setFont("Helvetica", 7)
for s in range(0, n * sim.SCAN // 1000 + 1): c.drawCentredString(gx + s * 1000 / sim.SCAN * dx, gy - 22 - len(names) * 26 + 8, f"{s}s")
c.showPage(); c.save(); print("wrote", OUT, "pages:", page)
