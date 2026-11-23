"""Scan-by-scan simulation of Project 9 (complete car wash: ULTRA, SHINE, CLEAN, CHEAP), Do-more 2.11.
Data-driven: WASHES below is the single source of truth for the ladder, this sim, and the PDF."""
SCAN = 10

# name, counter CTn, preset ($), run bit, steps [(step bit, timer, Y output, nickname)]
WASHES = [
    ("ULTRA", 0, 6, 4, [(10, 10, 0, "UNDER CAR"), (11, 11, 1, "SOAP 1"), (12, 12, 2, "SOAK 1"), (13, 13, 3, "RINSE 1"),
                        (51, 14, 1, "SOAP 2"), (52, 15, 2, "SOAK 2"), (53, 16, 3, "RINSE 2"),
                        (14, 17, 4, "WAX"), (15, 18, 5, "SPOT-FREE"), (16, 19, 6, "AIR DRY")]),
    ("SHINE", 1, 5, 5, [(20, 20, 0, "UNDER CAR"), (21, 21, 1, "SOAP"), (22, 22, 2, "SOAK"), (23, 23, 3, "RINSE"),
                        (24, 24, 4, "WAX"), (25, 25, 5, "SPOT-FREE"), (26, 26, 6, "AIR DRY")]),
    ("CLEAN", 2, 4, 6, [(30, 30, 0, "UNDER CAR"), (31, 31, 1, "SOAP"), (32, 32, 2, "SOAK"), (33, 33, 3, "RINSE"),
                        (35, 34, 5, "SPOT-FREE"), (36, 35, 6, "AIR DRY")]),
    ("CHEAP", 3, 3, 2, [(41, 0, 1, "SOAP"), (42, 1, 2, "SOAK"), (43, 2, 3, "RINSE")]),
]
EXPECTED_Y = {"ULTRA": [0, 1, 2, 3, 1, 2, 3, 4, 5, 6], "SHINE": [0, 1, 2, 3, 4, 5, 6],
              "CLEAN": [0, 1, 2, 3, 5, 6], "CHEAP": [1, 2, 3]}
ALL_STEP_BITS = [b for w in WASHES for b, _, _, _ in w[4]]

class TMRA:
    def __init__(s, pre=1000): s.pre, s.acc, s.done = pre, 0, False
    def run(s, en, rst):
        if rst: s.acc = 0
        elif en: s.acc = min(s.acc + SCAN, s.pre)
        s.done = s.acc >= s.pre

class CNT:
    def __init__(s, pre): s.pre, s.acc, s.done, s.last = pre, 0, False, False
    def run(s, up, rst):
        if rst: s.acc = 0
        elif up and not s.last: s.acc += 1
        s.last = up; s.done = s.acc >= s.pre

def reset_state():
    global X, C, Y, CT, T, t, last_x2
    X = dict.fromkeys(range(7), False)
    C = dict.fromkeys([0, 1, 2, 3, 4, 5, 6, 8, 9] + ALL_STEP_BITS, False)
    Y = dict.fromkeys(range(7), False)
    CT = {w[1]: CNT(w[2]) for w in WASHES}
    T = {tn: TMRA(1000) for w in WASHES for _, tn, _, _ in w[4]}
    t, last_x2 = 0, False
reset_state()

def scan():
    global t, last_x2
    ST5 = (t // 50) % 2 == 0
    C[9] = X[1] or X[5] or C[8]                                   # RESET ALL
    C[0] = (X[0] or C[0]) and not X[1] and not X[5]               # SYSTEM ENABLED
    up = C[0] and X[3] and not C[1]
    for w in WASHES: CT[w[1]].run(up, C[9])                       # CT0..CT3
    C[1] = ((X[4] and CT[3].done) or C[1]) and not C[9]           # CAR IS IN PLACE
    for i, (name, ct, pre, run, steps) in enumerate(WASHES):      # wash selection
        sel = C[1] and CT[ct].done and C[0]
        if i > 0: sel = sel and not CT[WASHES[i - 1][1]].done
        C[run] = (sel or C[run]) and not C[9]
    edge = X[2] and not last_x2; last_x2 = X[2]
    C[3] = (edge or C[3]) and not X[6] and not C[9]               # PAUSED
    for name, ct, pre, run, steps in WASHES:                      # timers
        for k, (bit, tn, _, _) in enumerate(steps):
            en = C[run] if k == 0 else T[steps[k - 1][1]].done
            T[tn].run(en and not C[3], C[9])
    for name, ct, pre, run, steps in WASHES:                      # step bits (interposing relays)
        for k, (bit, tn, _, _) in enumerate(steps):
            first = C[run] if k == 0 else T[steps[k - 1][1]].done
            C[bit] = first and not T[tn].done
    C[8] = any(T[w[4][-1][1]].done for w in WASHES)               # CARWASH COMPLETE
    p = not C[3]
    for y in range(7):                                            # outputs, one rung each
        on = any(C[b] for w in WASHES for b, _, yy, _ in w[4] if yy == y)
        if y == 2: on = on and ST5
        Y[y] = on and p
    t += SCAN

log, violations = [], []
RUN_BITS = {w[0]: w[3] for w in WASHES}
def active_steps(): return [b for b in ALL_STEP_BITS if C[b]]
def run(ms):
    for _ in range(ms // SCAN):
        scan()
        if len(active_steps()) > 1: violations.append(f"t={t} steps {active_steps()}")
        if sum(C[r] for r in RUN_BITS.values()) > 1: violations.append(f"t={t} two washes running")
def tog(x, on): X[x] = on; run(100)
def press(x): tog(x, True); tog(x, False)
def coins(n):
    for _ in range(n): press(3)
def check(name, cond):
    print(f"  CHECK {name}: {'PASS' if cond else 'FAIL'}"); log.append(bool(cond))
def idle(): return not any(C[r] for r in RUN_BITS.values()) and all(c.acc == 0 for c in CT.values()) and not any(Y.values())

def wash_trace(ms=12000):
    """Car drives in; record (step bit, start time, outputs on (Y2 counted if its step is on)) per step."""
    tr = []; X[4] = True
    for _ in range(ms // SCAN):
        scan()
        a = active_steps()
        if a and (not tr or tr[-1][0] != a[0]):
            y_on = [y for y in range(7) if Y[y] or (y == 2 and C[a[0]] and any(b == a[0] and yy == 2 for w in WASHES for b, _, yy, _ in w[4]))]
            tr.append([a[0], t, y_on])
        if not a and tr and tr[-1][0] is not None: tr.append([None, t, []])
        if idle() and tr and tr[-1][0] is None: break
    X[4] = False; run(100)
    return tr

def main():
    reset_state(); log.clear(); violations.clear()
    press(0)
    for name, ct, pre, run_bit, steps in WASHES:
        print(f"=== ${pre} -> {name} ===")
        coins(pre); tr = wash_trace()
        bits = [b for b, _, _ in tr if b is not None]
        durs = [tr[i + 1][1] - tr[i][1] for i in range(len(tr) - 1)]
        check(f"{name} step bits in order {[s[0] for s in steps]}", bits == [s[0] for s in steps])
        check(f"{name} outputs per step {EXPECTED_Y[name]}", [y[0] if len(y) == 1 else y for b, _t, y in tr if b is not None] == EXPECTED_Y[name])
        check(f"{name} every step 1 s", all(980 <= d <= 1010 for d in durs))
        check(f"{name} only its own bits used", set(bits) <= {s[0] for s in steps})
        check(f"{name} reset afterwards, system still enabled", idle() and C[0])

    print("=== $7 -> ULTRA (overpay) ===")
    coins(7); X[4] = True; run(50); check("$7 selects ULTRA", C[4] and not C[5]); run(11000); X[4] = False; run(100)
    print("=== $2 + car -> nothing ===")
    coins(2); tog(4, True); run(1500); check("no wash, car not latched", not C[1] and idle() is False and CT[3].acc == 2 and not any(Y.values()))
    tog(4, False); press(1); press(0)
    print("=== coins after car in place are ignored ===")
    coins(4); tog(4, True); coins(2); check("still CLEAN, counters frozen at 4", C[6] and CT[0].acc == 4); run(7000); tog(4, False)
    print("=== PAUSE (left ON) during SHINE wax, RESUME ===")
    coins(5); X[4] = True; run(4500)
    in_wax, acc = C[24], T[24].acc
    tog(2, True); run(1500)
    check("paused in SHINE wax, outputs off, timer held", in_wax and not any(Y.values()) and T[24].acc == acc)
    press(6); run(50); check("resumed in wax with PAUSE still ON", C[24] and not C[3])
    run(4000); check("SHINE finished and reset", idle()); tog(2, False); X[4] = False; run(100)
    print("=== STOP during CLEAN ===")
    coins(4); tog(4, True); run(2000); press(1)
    check("STOP cleared everything, system disabled", idle() and not C[0] and all(x.acc == 0 for x in T.values())); tog(4, False)
    print("=== MASTER RESET during ULTRA ===")
    press(0); coins(6); tog(4, True); run(5000); press(5)
    check("MASTER RESET cleared everything", idle() and all(x.acc == 0 for x in T.values())); tog(4, False)
    print("=== car left on pad after wash does not re-trigger ===")
    press(0); coins(3); tog(4, True); run(3500); run(2000); check("no second wash", idle() and not C[1]); tog(4, False)
    print("=== coins before GO ignored ===")
    press(1); coins(6); check("counters stay 0", all(c.acc == 0 for c in CT.values()))
    check("never two steps / two washes at once", not violations)
    if violations: print("   ", violations[:5])
    print(f"\nRESULT: {sum(log)}/{len(log)} checks passed")

if __name__ == "__main__":
    main()
