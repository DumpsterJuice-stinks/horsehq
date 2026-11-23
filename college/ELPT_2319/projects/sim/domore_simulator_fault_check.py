import importlib, sys
sys.path.insert(0, "/home/user/horsehq/college/ELPT_2319/projects/sim")
import cheap_carwash_p7_sim as s

def fresh(preset=1000):
    importlib.reload(s)
    if preset != 1000:
        s.T0, s.T1, s.T2 = s.TMRA(preset), s.TMRA(preset), s.TMRA(preset)
def run(ms):
    steps = []
    for _ in range(ms // s.SCAN):
        s.scan(); steps.append((s.Y[1], s.Y[2], s.Y[3]))
    return steps
def toggle(x, on): s.X[x] = on; run(100)
def coins(n):
    for _ in range(n): toggle(3, True); toggle(3, False)
def summary(name, steps):
    y1 = sum(a for a, b, c in steps) * s.SCAN; y3 = sum(c for a, b, c in steps) * s.SCAN
    print(f"{name:55} soap ON {y1:5} ms | rinse ON {y3:5} ms | RUN={int(s.C[2])} CT3={s.CT3.acc}")

# A: correct use of simulator toggles
fresh(); toggle(0, True); toggle(0, False); toggle(4, True); coins(3); summary("A correct: GO on/off, car on, coin on/off x3", run(4000))
# B: GO switch never turned on
fresh(); toggle(4, True); coins(3); summary("B forgot GO first", run(4000))
# C: coin switch turned on 3 times without turning off between
fresh(); toggle(0, True); toggle(4, True); toggle(3, True); toggle(3, True); toggle(3, True); summary("C coin left ON (no off between counts)", run(4000))
# D: timer preset typed as 1 instead of 1000 (1 ms)
fresh(1); toggle(0, True); toggle(4, True); coins(3); summary("D TMRA preset = 1 (1 ms, not 1 s)", run(4000))
# E: STOP or RESET switch left ON in simulator
fresh(); s.X[1] = True; toggle(0, True); toggle(4, True); coins(3); summary("E STOP (X1) left ON", run(4000))
# F: car switch X4 off
fresh(); toggle(0, True); coins(3); summary("F car-in-place X4 never ON", run(4000))
# G: GO left ON the whole time (maintained) -- still OK?
fresh(); toggle(0, True); toggle(4, True); coins(3); summary("G GO left ON", run(4000))
# H: PAUSE toggled on, then RESUME on/off while PAUSE still on
fresh(); toggle(0, True); toggle(4, True); coins(3); run(300); toggle(2, True); toggle(6, True); toggle(6, False)
summary("H PAUSE left ON when RESUME pressed", run(4000))
