"""Scan-by-scan simulation of Project 8 (ULTRA + CHEAP car wash), Do-more 2.11 style.
Rungs evaluated top-to-bottom each scan. Inputs behave like the simulator's toggle switches."""
SCAN = 10

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

ULTRA_STEPS = [  # (step bit, timer, output, name) in spec order 0-9
    (10, 10, 0, "under car"), (11, 11, 1, "soap"), (12, 12, 2, "soak"), (13, 13, 3, "rinse"),
    (51, 14, 1, "soap 2"), (52, 15, 2, "soak 2"), (53, 16, 3, "rinse 2"),
    (14, 17, 4, "wax"), (15, 18, 5, "spot-free"), (16, 19, 6, "air dry")]
CHEAP_STEPS = [(41, 0, 1, "soap"), (42, 1, 2, "soak"), (43, 2, 3, "rinse")]

def reset_state():
    global X, C, Y, CT, T, t, last_x2
    X = dict.fromkeys(range(7), False)
    C = dict.fromkeys([0, 1, 2, 3, 4, 8, 9, 10, 11, 12, 13, 14, 15, 16, 41, 42, 43, 51, 52, 53], False)
    Y = dict.fromkeys(range(7), False)
    CT = {0: CNT(6), 3: CNT(3)}
    T = {n: TMRA(1000) for n in [0, 1, 2] + list(range(10, 20))}
    t, last_x2 = 0, False
reset_state()

def scan():
    global t, last_x2
    ST5 = (t // 50) % 2 == 0
    # SYSTEM SECTION
    C[9] = X[1] or X[5] or C[8]                                                  # R1  RESET ALL
    C[0] = (X[0] or C[0]) and not X[1] and not X[5]                              # R2  SYSTEM ENABLED
    # COIN COUNTER SECTION (coins accepted only before the car is in place)
    up = C[0] and X[3] and not C[1]
    CT[0].run(up, C[9])                                                          # R3  ULTRA counter, preset 6
    CT[3].run(up, C[9])                                                          # R4  CHEAP counter, preset 3
    # PERMISSIVE SECTION
    C[1] = ((X[4] and CT[3].done) or C[1]) and not C[9]                          # R5  CAR IS IN PLACE (paid >= $3)
    # WASH SELECTION SECTION
    C[4] = ((C[1] and CT[0].done and C[0]) or C[4]) and not C[9]                 # R6  ULTRA RUNNING
    C[2] = ((C[1] and CT[3].done and not CT[0].done and C[0]) or C[2]) and not C[4] and not C[9]  # R7 CHEAP RUNNING
    edge = X[2] and not last_x2; last_x2 = X[2]
    C[3] = (edge or C[3]) and not X[6] and not C[9]                              # R8  PAUSED
    # CHEAP SEQUENCE
    T[0].run(C[2] and not C[3], C[9])                                            # R9
    T[1].run(T[0].done and not C[3], C[9])                                       # R10
    T[2].run(T[1].done and not C[3], C[9])                                       # R11
    # ULTRA SEQUENCE
    T[10].run(C[4] and not C[3], C[9])                                           # R12
    for n in range(11, 20): T[n].run(T[n - 1].done and not C[3], C[9])           # R13-R21
    # STEP BITS
    C[41] = C[2] and not T[0].done                                               # R22
    C[42] = T[0].done and not T[1].done                                          # R23
    C[43] = T[1].done and not T[2].done                                          # R24
    prev = C[4]
    for bit, tn, _, _ in ULTRA_STEPS:                                            # R25-R34
        C[bit] = (C[4] if tn == 10 else T[tn - 1].done) and not T[tn].done
    C[8] = T[2].done or T[19].done                                               # R35 CARWASH COMPLETE
    # OUTPUT SECTION
    p = not C[3]
    Y[0] = C[10] and p                                                           # R36
    Y[1] = (C[11] or C[51] or C[41]) and p                                       # R37
    Y[2] = (C[12] or C[52] or C[42]) and ST5 and p                               # R38
    Y[3] = (C[13] or C[53] or C[43]) and p                                       # R39
    Y[4] = C[14] and p                                                           # R40
    Y[5] = C[15] and p                                                           # R41
    Y[6] = C[16] and p                                                           # R42
    t += SCAN

log, violations = [], []
def run(ms, trace=None):
    for _ in range(ms // SCAN):
        scan()
        steps_on = [b for b in (41, 42, 43, 10, 11, 12, 13, 51, 52, 53, 14, 15, 16) if C[b]]
        if len(steps_on) > 1: violations.append(f"t={t} two steps on {steps_on}")
        if C[2] and C[4]: violations.append(f"t={t} CHEAP and ULTRA both running")
        if trace is not None:
            cur = next((b for b in steps_on), None)
            if not trace or trace[-1][0] != cur: trace.append([cur, t])
def tog(x, on): X[x] = on; run(100)
def press(x): tog(x, True); tog(x, False)
def coins(n):
    for _ in range(n): press(3)
def check(name, cond):
    print(f"  CHECK {name}: {'PASS' if cond else 'FAIL'}"); log.append(bool(cond))
def idle(): return not C[2] and not C[4] and CT[0].acc == 0 and CT[3].acc == 0 and not any(Y.values())

def step_order(trace):
    return [b for b, _ in trace if b is not None]
def durations(trace):
    out = []
    for i in range(len(trace) - 1):
        if trace[i][0] is not None: out.append(trace[i + 1][1] - trace[i][1])
    return out

def main():
    reset_state(); log.clear(); violations.clear()
    print("=== TEST 1: $6 -> ULTRA, all 10 steps in order, 1 s each ===")
    press(0); coins(6); tr = []
    outs_seen = []
    X[4] = True
    for _ in range(1110):
        scan()
        cur = [b for b in (10, 11, 12, 13, 51, 52, 53, 14, 15, 16) if C[b]]
        if cur and (not tr or tr[-1][0] != cur[0]): tr.append([cur[0], t]); outs_seen.append([o for o in range(7) if o != 2 and Y[o]])
        if not cur and tr and tr[-1][0] is not None: tr.append([None, t])
    check("ULTRA step order 10,11,12,13,51,52,53,14,15,16", step_order(tr) == [10, 11, 12, 13, 51, 52, 53, 14, 15, 16])
    check("each ULTRA step lasts 1.00 s", all(980 <= d <= 1010 for d in durations(tr)) and len(durations(tr)) == 10)
    exp = [[0], [1], [], [3], [1], [], [3], [4], [5], [6]]
    check("correct output for every step (Y0,Y1,Y2*,Y3,Y1,Y2*,Y3,Y4,Y5,Y6)", outs_seen == exp)
    check("CHEAP never ran during ULTRA", not any(b in (41, 42, 43) for b, _ in tr))
    check("everything reset after air dry", idle())
    tog(4, False)

    print("=== TEST 2: $3 -> CHEAP only (Y1, Y2 blink, Y3) ===")
    coins(3); tr = []; tog(4, True); run(3500, tr)
    check("CHEAP step order 41,42,43", step_order(tr) == [41, 42, 43])
    check("ULTRA never ran", not any(b in (10, 11, 12, 13, 51, 52, 53, 14, 15, 16) for b, _ in tr))
    check("reset after rinse", idle()); tog(4, False)

    print("=== TEST 3: $4 and $5 -> CHEAP (no SHINE/CLEAN until Project 9) ===")
    coins(4); tog(4, True); run(50); a = C[2] and not C[4]; run(3500); tog(4, False)
    coins(5); tog(4, True); run(50); b = C[2] and not C[4]; run(3500); tog(4, False)
    check("$4 runs CHEAP", a); check("$5 runs CHEAP", b)

    print("=== TEST 4: $2 + car -> nothing ===")
    coins(2); tog(4, True); run(2000)
    check("no wash, car bit not latched", not C[1] and not C[2] and not C[4] and not any(Y.values()))
    tog(4, False); press(5)

    print("=== TEST 5: coins dropped after the car is in place are ignored ===")
    press(0); coins(3); tog(4, True); coins(3)
    check("CT0 stayed below 6 -> still CHEAP", CT[0].acc == 3 and C[2] and not C[4])
    run(3500); tog(4, False)

    print("=== TEST 6: PAUSE (switch left ON) during ULTRA wax, RESUME ===")
    coins(6); tog(4, True); run(7300)
    in_wax = C[14]; acc = T[17].acc
    tog(2, True); run(1500)
    check("paused in wax, outputs off, timer held", in_wax and not any(Y.values()) and T[17].acc == acc)
    press(6); run(50)
    check("resumed in wax even with PAUSE still ON", C[14] and not C[3])
    run(3500)
    check("ULTRA finished and reset", idle())
    tog(2, False); tog(4, False)

    print("=== TEST 7: STOP during ULTRA ===")
    coins(6); tog(4, True); run(2500); press(1)
    check("STOP reset everything (and disabled system)", idle() and not C[0] and all(x.acc == 0 for x in T.values()))
    tog(4, False)

    print("=== TEST 8: MASTER RESET during CHEAP ===")
    press(0); coins(3); tog(4, True); run(1500); press(5)
    check("MASTER RESET cleared everything", idle() and all(x.acc == 0 for x in T.values()))
    tog(4, False)

    print("=== TEST 9: car still on pad after wash does not re-trigger ===")
    press(0); coins(3); tog(4, True); run(3500); run(2000)
    check("no second wash with car sitting there", idle() and not C[1])
    tog(4, False)

    print("=== TEST 10: coins before GO are ignored ===")
    press(5); coins(6)
    check("counters stay 0", CT[0].acc == 0 and CT[3].acc == 0)

    check("never two steps on at once / never both washes", not violations)
    if violations: print("   ", violations[:5])
    print(f"\nRESULT: {sum(log)}/{len(log)} checks passed")

if __name__ == "__main__":
    main()
