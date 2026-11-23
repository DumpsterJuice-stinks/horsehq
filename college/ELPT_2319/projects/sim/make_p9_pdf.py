"""Builds Project7_CHEAP_Car_Wash_Ladder.pdf: I/O map, drawn ladder rungs, simulation."""
import io, sys, contextlib
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import full_carwash_p9_sim as sim

OUT = sys.argv[1] if len(sys.argv) > 1 else "Project9_Complete_Car_Wash_Ladder.pdf"
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

# ---------------- program (generated from sim.WASHES) ----------------
W = sim.WASHES
RA = [NO("C9", "RESET|ALL")]; NRA = NC("C9", "RESET|ALL")
YNAME = {0: "UNDER CAR/|WHEEL PUMP", 1: "SOAP PUMP", 2: "SOAK LAMP", 3: "RINSE PUMP", 4: "WAX PUMP", 5: "SPOT FREE|RINSE PUMP", 6: "AIR DRY|BLOWER"}
RUNNAME = {w[3]: w[0] + "|RUNNING" for w in W}
rows = []
def S(title, top=None): rows.append(("SECTION", top, title))
def RG(kind, *a): rows.append([kind, *a])
S("SYSTEM SECTION", "9 COMPLETE CAR WASH (ULTRA / SHINE / CLEAN / CHEAP)")
RG("C", [P([NO("X1", "STOP")], [NO("X5", "MASTER|RESET")], [NO("C8", "CARWASH|COMPLETE")])], ("C9", "RESET|ALL"),
  "Resets counters, latches and timers: STOP, MASTER RESET, or end of any wash (C8 from the previous scan).")
RG("C", [P([NO("X0", "GO")], [NO("C0", "SYSTEM|ENABLED")]), NC("X1", "STOP"), NC("X5", "MASTER|RESET")], ("C0", "SYSTEM|ENABLED"),
  "GO enables the facility. Only STOP or MASTER RESET disables it.")
S("COIN COUNTER SECTION (all four counters see every dollar; locked out once the car is in place)")
for name, ct, pre, run, steps in W:
    RG("B", ("CNT", f"{name}|COUNTER", [("Counter Struct", f"CT{ct}"), ("Preset", str(pre))],
        [("UP", [NO("C0", "SYSTEM|ENABLED"), NO("X3", "COIN DROP"), NC("C1", "CAR IS|IN PLACE")]), ("RST", RA)]),
      f"CT{ct}.Done = ${pre} PAID ({name}).")
S("PERMISSIVE SECTION")
RG("C", [P([NO("X4", "CAR-IN-PLACE|PERMISSIVE"), NO("CT3.Done", "$3 PAID")], [NO("C1", "CAR IS|IN PLACE")]), NRA], ("C1", "CAR IS|IN PLACE"),
  "Car drives forward after paying at least $3. Coins are locked out from here on.")
S("WASH SELECTION SECTION (highest package paid for wins)")
for i, (name, ct, pre, run, steps) in enumerate(W):
    br = [NO("C1", "CAR IS|IN PLACE"), NO(f"CT{ct}.Done", f"${pre} PAID")]
    if i > 0: br.append(NC(f"CT{W[i-1][1]}.Done", f"${W[i-1][2]} PAID"))
    br.append(NO("C0", "SYSTEM|ENABLED"))
    RG("C", [P(br, [NO(f"C{run}", RUNNAME[run])]), NRA], (f"C{run}", RUNNAME[run]),
      f"{name}: ${pre}" + (" or more." if i == 0 else f" but not ${W[i-1][2]}. Only one package can be true."))
RG("C", [P([PE("X2", "PAUSE|(leading edge)")], [NO("C3", "PAUSED")]), NC("X6", "RESUME"), NRA], ("C3", "PAUSED"),
  "Leading edge of PAUSE latches C3; RESUME or RESET ALL clears it.")
for name, ct, pre, run, steps in W:
    S(f"{name} SEQUENCE SECTION: TMRA timers (1 s each), then step bits / interposing relays")
    for k, (bit, tn, y, nick) in enumerate(steps):
        en = [NO(f"C{run}", RUNNAME[run])] if k == 0 else [NO(f"T{steps[k-1][1]}.Done", f"{name} {steps[k-1][3]}|DONE")]
        RG("B", ("TMRA", f"{name}|{nick}", [("Timer Struct", f"T{tn}"), ("Preset", "1.000s")],
            [("E", en + [NC("C3", "PAUSED")]), ("R", RA)]), f"{name} step {k + 1}: {nick.lower()} time.")
    for k, (bit, tn, y, nick) in enumerate(steps):
        first = NO(f"C{run}", RUNNAME[run]) if k == 0 else NO(f"T{steps[k-1][1]}.Done", f"{name} {steps[k-1][3]}|DONE")
        RG("C", [first, NC(f"T{tn}.Done", f"{name} {nick}|DONE")], (f"C{bit}", f"{name}|{nick}"),
          f"{name} {nick.lower()} window -> drives Y{y} {YNAME[y].replace('|', ' ').lower()}.")
S("WASH COMPLETE")
RG("C", [P(*[[NO(f"T{w[4][-1][1]}.Done", f"{w[0]} {w[4][-1][3]}|DONE")] for w in W])], ("C8", "CARWASH|COMPLETE"),
  "Last step of any wash done. Next scan RESET ALL clears everything for the next customer.")
S("OUTPUT SECTION (each Y output on exactly one rung; interposing relays in parallel)")
for y in range(7):
    br = [[NO(f"C{b}", f"{w[0]}|{nick}")] for w in W for b, _, yy, nick in w[4] if yy == y]
    ser = [P(*br)] + ([NO("ST5", "$100ms")] if y == 2 else []) + [NC("C3", "PAUSED")]
    RG("C", ser, (f"Y{y}", YNAME[y]), YNAME[y].replace("|", " ").title() + (" blinks on ST5." if y == 2 else "."))
RG("END", None, None, "")
PROG, n = [], 0
for r in rows:
    if r[0] == "SECTION": PROG.append(r)
    else: n += 1; PROG.append(tuple([n] + list(r)))
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
    c.setFont("Helvetica-Bold", 13); c.drawString(30, PH - 30, "ELPT 2319  |  Project 9: Complete Car Wash (Do-more)")
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
c.setTitle("Project 9 Complete Car Wash Ladder"); c.setAuthor("ELPT 2319 student")
header(c, page, "Spec: Harry Franz Car Wash (rev 7/24/2026). Project 9 = complete coin counter, car-in-place permissive, FULL car wash, interposing relays.")
y = PH - 72
c.setFont("Helvetica-Bold", 11); c.drawString(30, y, "I/O Map"); y -= 16
y = table(c, 30, y, [("Address", "Nickname", "Device / Purpose"),
  ("X0", "GO", "PB, enables the facility"), ("X1", "STOP", "PB (NO), stops + resets"), ("X2", "PAUSE", "PB, leading-edge pause"),
  ("X3", "COIN DROP", "Photocell, 1 pulse per dollar"), ("X4", "CAR-IN-PLACE", "Photocell, car drove forward"),
  ("X5", "MASTER RESET", "PB (NO), resets everything"), ("X6", "RESUME", "PB, continue after pause"),
  ("Y0", "UNDER CAR/WHEEL PUMP", "C10, C20, C30"), ("Y1", "SOAP PUMP", "C11, C51, C21, C31, C41"), ("Y2", "SOAK LAMP", "C12, C52, C22, C32, C42 (blinks)"),
  ("Y3", "RINSE PUMP", "C13, C53, C23, C33, C43"), ("Y4", "WAX PUMP", "C14, C24"), ("Y5", "SPOT FREE RINSE PUMP", "C15, C25, C35"), ("Y6", "AIR DRY BLOWER", "C16, C26, C36")],
  [52, 150, 190], 8)
y2 = PH - 72; c.setFont("Helvetica-Bold", 11); c.drawString(450, y2, "Internal Tags"); y2 -= 16
y2 = table(c, 450, y2, [("Address", "Nickname"), ("C0", "SYSTEM ENABLED"), ("C1", "CAR IS IN PLACE"), ("C3", "PAUSED"),
  ("C4 / C5 / C6 / C2", "ULTRA / SHINE / CLEAN / CHEAP RUNNING"), ("C8", "CARWASH COMPLETE (end pulse)"), ("C9", "RESET ALL"),
  ("CT0/CT1/CT2/CT3", "Counters, presets 6 / 5 / 4 / 3"), ("C10-16, C51-53", "ULTRA interposing relays"), ("C20-C26", "SHINE interposing relays"),
  ("C30-33, C35-36", "CLEAN interposing relays"), ("C41-C43", "CHEAP interposing relays"), ("T10-T19 / T20-T26", "ULTRA / SHINE TMRA"),
  ("T30-T35 / T0-T2", "CLEAN / CHEAP TMRA"), ("ST5", "$100ms clock")], [110, 200], 8)
y = min(y, y2) - 16
c.setFont("Helvetica-Bold", 11); c.drawString(30, y, "Sequence of Operation"); y -= 14; c.setFont("Helvetica", 8.6)
for ln in ["1. GO (X0) seals in SYSTEM ENABLED (C0); it stays on between customers. Only STOP or MASTER RESET drops it.",
           "2. Dollars on X3 count up CT0 (6), CT1 (5), CT2 (4) and CT3 (3) together.",
           "3. Car drives forward: X4 latches CAR IS IN PLACE (C1) if at least $3 is paid; coins are then locked out.",
           "4. The highest package paid for starts: ULTRA (C4), SHINE (C5), CLEAN (C6) or CHEAP (C2). Each runs its steps on its own TMRA timers.",
           "5. Each step bit is the interposing relay from the spec chart; each Y output rung ORs the relays that use it.",
           "6. Last step done -> CARWASH COMPLETE (C8) -> next scan RESET ALL (C9) clears counters, latches, timers.",
           "PAUSE (X2 leading edge) holds the timers and drops outputs; RESUME (X6) continues the same step.",
           "Simulator order: GO on/off, COIN on/off per dollar, THEN car X4 on. Every TMRA preset = 1000 (1.000s)."]:
    c.drawString(36, y, ln); y -= 12
c.showPage(); page += 1
header(c, page, "Matrix: which output is on in each step (spec step numbers)")
y = PH - 70
SPEC_NUM = {"ULTRA": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "SHINE": [0, 1, 2, 3, 7, 8, 9], "CLEAN": [0, 1, 2, 3, 8, 9], "CHEAP": [1, 2, 3]}
mrows = [("Wash", "Spec step", "Name", "Relay", "Timer", "Y0", "Y1", "Y2", "Y3", "Y4", "Y5", "Y6")]
for name, ct, pre, run, steps in W:
    for k, (bit, tn, yy, nick) in enumerate(steps):
        mrows.append((f"{name} ${pre}", str(SPEC_NUM[name][k]), nick, f"C{bit}", f"T{tn}") +
                     tuple(("BLINK" if j == 2 else "ON") if j == yy else "-" for j in range(7)))
y = table(c, 30, y, mrows, [70, 60, 80, 50, 50] + [52] * 7, 8)
y -= 12; c.setFont("Helvetica-Bold", 10); c.drawString(30, y, "Coins -> wash"); y -= 14
table(c, 30, y, [("Dollars", "Wash", "Dollars", "Wash"), ("0 - 2", "none", "5", "SHINE (skip 4, 5, 6)"), ("3", "CHEAP (steps 1-3)", "6 or more", "ULTRA (all steps)"),
                 ("4", "CLEAN (skip 4, 5, 6, 7)", "", "")], [60, 150, 70, 160], 8)
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

page += 1; header(c, page, "Scan-by-scan simulation (sim/full_carwash_p9_sim.py, 10 ms scans, simulator-style toggle inputs)")
buf = io.StringIO()
with contextlib.redirect_stdout(buf): sim.main()
y = PH - 70; c.setFont("Helvetica-Bold", 11); c.drawString(30, y, "Test results"); y -= 13
for ln in [l.strip() for l in buf.getvalue().splitlines() if "===" in l or "CHECK" in l or "RESULT" in l]:
    c.setFont("Helvetica-Bold" if "===" in ln or "RESULT" in ln else "Helvetica", 6.6)
    if "FAIL" in ln: c.setFillColor(colors.red)
    c.drawString(34, y, ln[:100]); c.setFillColor(colors.black); y -= 8.4
# timing diagrams: one per wash, outputs only
gx, gw = 470, 300
def trace_for(coins_n):
    sim.reset_state(); tr = {f"Y{k}": [] for k in range(7)}
    sim.X[0] = True; sim.scan(); sim.X[0] = False; sim.scan()
    for _ in range(coins_n): sim.X[3] = True; sim.scan(); sim.X[3] = False; sim.scan()
    sim.X[4] = True
    for _ in range(1050):
        sim.scan()
        for k in range(7): tr[f"Y{k}"].append(sim.Y[k])
    return tr
gy = PH - 78
for name, ct, pre, run, steps in W:
    tr = trace_for(pre); n = 1050; dx = gw / n
    c.setFont("Helvetica-Bold", 9); c.drawString(gx - 70, gy, f"{name} (${pre})"); gy -= 8
    for k in range(7):
        yb = gy - 9 - k * 9.5; c.setFont("Helvetica", 6); c.drawRightString(gx - 4, yb, f"Y{k}")
        vals = tr[f"Y{k}"]; c.setStrokeColor(colors.HexColor("#1565c0")); c.setLineWidth(0.6)
        p = c.beginPath(); p.moveTo(gx, yb + (6 if vals[0] else 0))
        for j, v in enumerate(vals): p.lineTo(gx + j * dx, yb + (6 if v else 0)); p.lineTo(gx + (j + 1) * dx, yb + (6 if v else 0))
        c.drawPath(p); c.setStrokeColor(colors.black)
    gy -= 7 * 9.5 + 4
    c.setFont("Helvetica", 5.5)
    for s in range(0, 11): c.drawCentredString(gx + s * 100 * dx, gy, f"{s}s")
    gy -= 16
c.showPage(); c.save(); print("wrote", OUT, "pages:", page)
