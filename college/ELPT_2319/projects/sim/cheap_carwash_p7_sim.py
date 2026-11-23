"""Scan-by-scan simulation of Project 7 (CHEAP car wash), Do-more.
Rungs are evaluated top to bottom every scan, like the PLC does."""
SCAN = 10  # ms per scan

class TMRA:  # Do-more accumulating timer: Enable leg + Reset leg, holds Acc when disabled
    def __init__(s, pre): s.pre, s.acc, s.done = pre, 0, False
    def run(s, en, rst):
        if rst: s.acc = 0
        elif en: s.acc = min(s.acc + SCAN, s.pre)
        s.done = s.acc >= s.pre

class CNT:  # Do-more CNT: counts UP leading edges, RST clears
    def __init__(s, pre): s.pre, s.acc, s.done, s.last = pre, 0, False, False
    def run(s, up, rst):
        if rst: s.acc = 0
        elif up and not s.last: s.acc += 1
        s.last = up; s.done = s.acc >= s.pre

X = dict.fromkeys(range(7), False)
X[1] = X[5] = False        # STOP / RESET are NO pushbuttons (True only while pressed)
C = dict.fromkeys([0, 1, 2, 3, 8, 41, 42, 43], False)
Y = dict.fromkeys([1, 2, 3], False)
CT3, T0, T1, T2 = CNT(3), TMRA(1000), TMRA(1000), TMRA(1000)
t = 0
log = []
last_x2 = False  # for the rising-edge PAUSE contact

def scan():
    global t, last_x2
    ST5 = (t // 50) % 2 == 0                                                    # $100ms clock
    C[0] = (X[0] or C[0]) and not X[1] and not X[5]                             # R1 SYSTEM ENABLED
    CT3.run(C[0] and X[3], X[1] or X[5] or C[8])                                # R2 CHEAP COIN COUNTER
    C[1] = (X[4] or C[1]) and not X[1] and not X[5] and not C[8]                # R3 CAR IS IN PLACE
    C[2] = ((CT3.done and C[1] and C[0]) or C[2]) and not X[1] and not X[5] and not C[8]  # R4 WASH RUNNING
    pause_edge = X[2] and not last_x2; last_x2 = X[2]                           # rising edge of PAUSE
    C[3] = (pause_edge or C[3]) and not X[6] and not X[1] and not X[5]          # R5 PAUSED (edge contact X2)
    rst = X[1] or X[5] or C[8]
    T0.run(C[2] and not C[3], rst)                                              # R6 soap timer
    T1.run(T0.done and not C[3], rst)                                           # R7 soak timer
    T2.run(T1.done and not C[3], rst)                                           # R8 rinse timer
    C[41] = C[2] and not T0.done                                                # R9  soap step
    C[42] = T0.done and not T1.done                                             # R10 soak step
    C[43] = T1.done and not T2.done                                             # R11 rinse step
    C[8] = T2.done                                                              # R12 CHEAP CARWASH RESET
    Y[1] = C[41] and not C[3]                                                   # R13 SOAP PUMP
    Y[2] = C[42] and ST5 and not C[3]                                           # R14 SOAK LAMP blinks
    Y[3] = C[43] and not C[3]                                                   # R15 RINSE PUMP
    t += SCAN

def snap():
    return (f"CT3={CT3.acc} EN={int(C[0])} CAR={int(C[1])} RUN={int(C[2])} PAUSE={int(C[3])} "
            f"step={'soap' if C[41] else 'soak' if C[42] else 'rinse' if C[43] else '-':5} "
            f"Y1={int(Y[1])} Y3={int(Y[3])} T0={T0.acc:4} T1={T1.acc:4} T2={T2.acc:4} RST={int(C[8])}")

def run(ms):
    last, y2 = None, []
    for _ in range(ms // SCAN):
        scan(); y2.append(Y[2]); s = snap()
        if s != last: print(f"  t={t/1000:6.2f}s  {s}"); last = s
    return y2

def press(x, ms=100):
    X[x] = True; run(ms); X[x] = False; run(50)

def check(name, cond):
    print(f"  CHECK {name}: {'PASS' if cond else 'FAIL'}"); log.append(cond)

def main():
    print("=== TEST 1: GO, car in place, $3, full CHEAP wash ===")
    press(0); X[4] = True; run(50)
    for _ in range(3): press(3)
    check("wash started after 3rd coin", C[2] and Y[1])
    y2 = run(3200)
    check("soak lamp blinked (Y2 toggled)", any(y2) and not all(y2[100:200]))
    check("system reset after rinse", not C[2] and CT3.acc == 0 and not any(Y.values()))
    X[4] = False; press(5)  # car leaves; clear the latched car bit for the next test

    print("=== TEST 2: only $2 -> no wash ===")
    press(0); X[4] = True; run(50); press(3); press(3); run(2000)
    check("no outputs with $2", not C[2] and not any(Y.values()))
    press(3); check("3rd dollar starts wash", C[2])

    print("=== TEST 3: PAUSE during soak, RESUME continues where it left off ===")
    run(1100)  # into soak
    acc_before = T1.acc
    press(2); run(1000)
    check("outputs off while paused", not any(Y.values()))
    check("TMRA held its accumulated time", T1.acc == acc_before)
    press(6); run(50)
    check("resumed in soak step", C[42] and not C[3])
    run(3000)
    check("finished and reset after resume", not C[2] and CT3.acc == 0)
    X[4] = False; press(5)

    print("=== TEST 4: STOP mid-wash resets everything ===")
    press(0); X[4] = True; run(50)
    for _ in range(3): press(3)
    run(500); press(1)
    check("STOP cleared wash, counter, timers", not C[0] and not C[2] and CT3.acc == 0 and T0.acc == 0)
    X[4] = False

    print("=== TEST 5: coins before GO are not counted ===")
    press(3); press(3); press(3)
    check("counter stays 0 while system disabled", CT3.acc == 0)

    print("=== TEST 6: MASTER RESET mid-rinse ===")
    press(0); X[4] = True; run(50)
    for _ in range(3): press(3)
    run(2500); press(5)
    check("master reset cleared everything", not C[2] and CT3.acc == 0 and not any(Y.values()) and T2.acc == 0)

    print(f"\nRESULT: {sum(log)}/{len(log)} checks passed")

if __name__ == '__main__':
    main()
