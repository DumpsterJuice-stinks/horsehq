"""Scan-by-scan simulation of the CHEAP CAR WASH go-by ladder (Do-more).
Each scan evaluates rungs top to bottom, exactly like the PLC."""
SCAN_MS = 10

class TMR:  # Do-more TMR: E/R input, non-retentive
    def __init__(s, preset): s.pre, s.acc, s.done = preset, 0, False
    def run(s, en):
        if en:
            s.acc = min(s.acc + SCAN_MS, s.pre); s.done = s.acc >= s.pre
        else:
            s.acc, s.done = 0, False

class CNT:  # Do-more CNT: counts on UP leading edge, RST clears
    def __init__(s, preset): s.pre, s.acc, s.done, s.last = preset, 0, False, False
    def run(s, up, rst):
        if rst: s.acc = 0
        elif up and not s.last: s.acc += 1
        s.last = up; s.done = s.acc >= s.pre

X = {3: False, 4: False, 5: False}           # X3 coin, X4 car-in-place, X5 master reset
C1 = C2 = C3 = False                          # CAR IS IN PLACE, CHEAP WASH RUNNING, CHEAP CARWASH RESET
Y = {1: False, 2: False, 3: False}
CT0, T0, T1, T2 = CNT(3), TMR(3000), TMR(3000), TMR(3000)
t = 0

def scan():
    global C1, C2, C3, t
    ST5 = (t // 50) % 2 == 0                                   # $100ms clock: 50 ms on / 50 ms off
    CT0.run(X[3], X[5] or C3)                                  # R1  COIN COUNTER
    C1 = (X[4] or C1) and not X[5] and not C3                  # R2  CAR IS IN PLACE
    C2 = ((CT0.done and C1) or C2) and not X[5] and not C3     # R3  CHEAP WASH RUNNING
    Y[1] = C2 and not T0.done                                  # R4  SOAP PUMP
    T0.run(C2)                                                 # R5  soap time
    Y[2] = ST5 and T0.done and not T1.done                     # R6  SOAK LAMP (blinks)
    T1.run(T0.done)                                            # R7  soak time
    pass                                                       # R8  NOP
    Y[3] = T1.done                                             # R9  RINSE PUMP
    T2.run(T1.done)                                            # R10 rinse time
    C3 = T2.done                                               # R11 CHEAP CARWASH RESET
    t += SCAN_MS

def state():
    return (f"CT0={CT0.acc} $3PAID={int(CT0.done)} CAR={int(C1)} RUN={int(C2)} "
            f"Y1 soap={int(Y[1])} Y2 soak={int(Y[2])} Y3 rinse={int(Y[3])} "
            f"T0={T0.acc} T1={T1.acc} T2={T2.acc} RST={int(C3)}")

def run_ms(ms, note="", every=None):
    last = None
    blink_on = 0
    for _ in range(ms // SCAN_MS):
        scan()
        blink_on += Y[2]
        s = state()
        key = s.split(" Y2")[0] + s.split("Y3")[1].split(" T0")[0] + f"RST{int(C3)}"
        if key != last:
            print(f"t={t/1000:6.2f}s  {s}"); last = key
    if note: print(f"   -> {note}")
    return blink_on

def pulse(x, note):
    X[x] = True; run_ms(100); X[x] = False; run_ms(100, note)

print("=== TEST 1: car pulls in, 3 coins, full wash ===")
X[4] = True; run_ms(100, "car in place latched; no money yet, nothing runs")
pulse(3, "coin 1"); pulse(3, "coin 2")
pulse(3, "coin 3 -> $3 PAID, wash starts (soap)")
on = run_ms(3000, "soap 3 s then soak starts")
on = run_ms(3000, "soak lamp blinked; rinse starts")
print(f"   (Y2 was ON for {on} of 300 soak scans -> blinking, not steady)")
run_ms(3200, "rinse 3 s, then RESET pulse clears counter + run bit")
X[4] = False; run_ms(100, "car drives out")

print("\n=== TEST 2: coins with NO car -> must not wash ===")
X[4] = False; pulse(5, "start clean: master reset, no car on the pad")
for i in range(3): pulse(3, f"coin {i+1}")
run_ms(1000, "paid but no car: RUN stays 0, outputs off")
X[4] = True; run_ms(500, "car arrives -> wash starts")

print("\n=== TEST 3: MASTER RESET mid-wash ===")
run_ms(3500)
X[5] = True; run_ms(100, "master reset pressed -> everything drops")
X[5] = False; run_ms(500, "released: car re-detected, but $3 cleared -> no wash")
