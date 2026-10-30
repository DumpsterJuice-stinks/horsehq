# Car Wash — Project 7 (CHEAP only) — Do-more Ladder Logic

**ELPT 2319 · Unit 11 · Cheap Car Wash Project · Due 11/2/26**
Spec: `INSTRUCTOR_Carwash_Spec_Harry_Franz.pdf` — UHD Prof. Harry Franz, PE

> **Project 7** = coin counter routine using **1 counter**, car-in-place
> permissive, **CHEAP car wash only**.
> Project 8 adds ULTRA; Project 9 is the full wash with all interposing relays.

## Two spec rules that drive the design

1. **"Use TMRA timers on all car wash projects."** TMRA is an *accumulating*
   timer — it **holds its accumulated value** when its rung goes false and
   needs an **explicit reset**. That is exactly what PAUSE/RESUME requires; a
   plain TMR would zero out on pause.
2. **"Only use 1 second timers."** Ignore the 20/15/20 s design values in the
   spec sheet when uploading for grading.

## CHEAP wash definition

$3.00 · **steps 1, 2, 3 only** — Soap, Soak, Rinse.
Counter **CT3**, interposing relays **C41, C42, C43**.

---

## Memory map

| Address | Nickname | Function |
| --- | --- | --- |
| **X0** | `GO_PB` | Permissive to start |
| **X1** | `STOP_PB` | Resets/deactivates the facility |
| **X2** | `PAUSE_PB` | Halts the wash |
| **X3** | `COIN_DROP` | Photocell — one pulse per dollar |
| **X4** | `CAR_IN_PLACE` | Photocell — customer drove forward |
| **X5** | `MASTER_RESET` | Resets outputs, counters, timers, latches |
| **X6** | `RESUME_PB` | Restarts after pause |
| **Y1** | `SOAP_PUMP` | Step 1 |
| **Y2** | `SOAK_LAMP` | Step 2 |
| **Y3** | `RINSE_PUMP` | Step 3 |
| **C0** | `SYS_ENABLE` | System enabled (GO seal-in) |
| **C1** | `CHEAP_AUTH` | $3.00 counted — wash purchased |
| **C2** | `WASH_RUN` | Wash cycle active |
| **C3** | `PAUSED` | Pause latch |
| **C8** | `RESET_PULSE` | Cycle-complete / reset distribution |
| **C41** | `CHEAP_SOAP` | Step 1 interposing relay |
| **C42** | `CHEAP_SOAK` | Step 2 interposing relay |
| **C43** | `CHEAP_RINSE` | Step 3 interposing relay |
| **CT3** | `COIN_CTR` | Coin counter, preset 3 |
| **T1–T3** | — | TMRA step timers, 1000 ms each |

Unused in Project 7 (reserved for Projects 8–9): Y0 under-car/wheel pump,
Y4 wax pump, Y5 spot-free rinse, Y6 air-dry blower.

---

## Ladder program

### Rung 1 — System Enable
```
      X0          X1          X5            C0
  ----] [----+---]/[--------]/[------------( OUT )----
     GO      |  STOP       RESET          SYS_ENABLE
      C0     |
  ----] [----+
```

### Rung 2 — Reset Pulse  (MUST be this early)
```
      T3.Done                                C8
  ----] [----+--------------------------------( OUT )----
      X1     |                              RESET_PULSE
  ----] [----+
      X5     |
  ----] [----+
```

### Rung 3 — Coin Counter
```
      C0          X3
  ----] [--------] [-----[ UPCTR  CT3   PRESET 3 ]----
                         [ RESET: C8              ]
```

### Rung 4 — CHEAP Authorized
```
      CT3.Done                 C8            C1
  ----] [----------+---------]/[------------( OUT )----
      C1           |                       CHEAP_AUTH
  ----] [----------+
```

### Rung 5 — Wash Running
```
      C1          X4           C8            C2
  ----] [--------] [-----+---]/[------------( OUT )----
   CHEAP_AUTH  CAR_PLACE |                   WASH_RUN
      C2                 |
  ----] [----------------+
```

### Rung 6 — Pause Latch
```
      X2                       X6            C3
  ----] [----------+---------]/[------------( OUT )----
    PAUSE          |         RESUME          PAUSED
      C3           |
  ----] [----------+
```

### Rungs 7-9 — TMRA Step Timers (1 second each)
```
R7:   C2          C3
  ----] [--------]/[-------[ TMRA  T1  1000 ]----  SOAP
                           [ RESET: C8       ]

R8:   T1.Done     C3
  ----] [--------]/[-------[ TMRA  T2  1000 ]----  SOAK
                           [ RESET: C8       ]

R9:   T2.Done     C3
  ----] [--------]/[-------[ TMRA  T3  1000 ]----  RINSE
                           [ RESET: C8       ]
```

### Rungs 10-12 — Step Interposing Relays
```
R10:  C2          C3         T1.Done         C41
  ----] [--------]/[--------]/[-------------( OUT )----  SOAP STEP

R11:  T1.Done     C3         T2.Done         C42
  ----] [--------]/[--------]/[-------------( OUT )----  SOAK STEP

R12:  T2.Done     C3         T3.Done         C43
  ----] [--------]/[--------]/[-------------( OUT )----  RINSE STEP
```

### Rungs 13-15 — Dedicated Output Rungs
```
R13:  C41                                     Y1
  ----] [--------------------------------------( OUT )----  SOAP PUMP

R14:  C42                                     Y2
  ----] [--------------------------------------( OUT )----  SOAK LAMP

R15:  C43                                     Y3
  ----] [--------------------------------------( OUT )----  RINSE PUMP
```

### Rung 16 — End
```
  --------------------------------------------[ END ]----
```

---

## Logic description

1. **GO (X0)** energizes `C0`, which seals itself in. STOP or MASTER RESET
   drops it. The facility is now live.
2. Customer drops dollars. Each pulse on **X3** increments **CT3**. At the
   third coin, `CT3.Done` sets.
3. `CT3.Done` latches **C1 (CHEAP_AUTH)** through a seal-in — the wash is
   purchased and remembered even though the coin pulses are momentary.
4. Customer drives forward. **X4 (CAR_IN_PLACE)** plus `C1` latches
   **C2 (WASH_RUN)**, starting the cycle.
5. **Step 1:** `C2` AND NOT paused energizes **C41** → **Y1 soap pump**, and
   starts TMRA **T1**.
6. **Step 2:** `T1.Done` drops C41 and energizes **C42** → **Y2 soak lamp**,
   starting **T2**.
7. **Step 3:** `T2.Done` drops C42 and energizes **C43** → **Y3 rinse pump**,
   starting **T3**.
8. **Reset:** `T3.Done` sets **C8**, which breaks the C1 and C2 seals and
   resets CT3 and all three TMRAs. Everything clears and the system is ready
   for the next customer.

### Pause / Resume

**C3 (PAUSED)** appears on six rungs — the three timer rungs and the three
step rungs. PAUSE therefore does two things at once:

- **Stops the pumps** (step relays drop out)
- **Freezes accumulated time** (TMRA rung goes false but the TMRA *holds* its
  value)

RESUME clears C3 and the TMRA picks up where it left off. **This is why the
spec mandates TMRA** — a standard TMR would reset to zero on pause and the
customer would get a full extra interval.

### Why C8 must be rung 2

C8 is the reset distribution bit. Rungs 4 and 5 (the C1/C2 seals) and rungs
7-9 (the TMRA resets) all consume it, so it must be solved **before** them in
the horizontal scan. Placing it late would delay the reset by a scan and could
let C2 re-latch while `C1` and `X4` were still true.

### Why the outputs get their own rungs

The spec states: *"Each output is dedicated to a rung and cannot be
duplicated on another rung."* Hence the **interposing relay** pattern — the
C-relays carry the step logic and a single rung per output drives the physical
device.

---

## Extending to Projects 8 and 9

The output rungs are built to grow. For **Project 8** (ULTRA + CHEAP), add
ULTRA's relays as **parallel branches** on the same output rungs:

```
      C41                                     Y1
  ----] [----+----------------------------------( OUT )----  SOAP PUMP
      C11    |
  ----] [----+
```

`Y1` still has exactly **one coil** in the program, satisfying the no-duplicate
rule. Project 9 adds C21 (SHINE) and C31 (CLEAN) as further branches.

Per the instructor's chart:

| Wash | Price | Counter | Steps | Relays |
| --- | --- | --- | --- | --- |
| ULTRA | $6.00 | CT0 | all | C10-C16, C51-C53 |
| SHINE | $5.00 | CT1 | skip 4,5,6 | C20-C26 |
| CLEAN | $4.00 | CT2 | skip 4,5,6,7 | C30-C36 |
| **CHEAP** | **$3.00** | **CT3** | **1,2,3 only** | **C41-C43** |

---

## Testing checklist

- [ ] GO latches the system; STOP drops it
- [ ] Three X3 pulses set `CT3.Done` — not two, not four
- [ ] Wash does **not** start until **X4** is also true (car-in-place permissive)
- [ ] Y1 → Y2 → Y3 fire in order, one second each, never overlapping
- [ ] **PAUSE mid-step**: pump stops, `T.Acc` holds its value
- [ ] **RESUME**: timer continues from the held value, not from zero
- [ ] After rinse, CT3 and all timers clear and the system accepts a new customer
- [ ] MASTER RESET (X5) clears everything from any state
- [ ] E-stop behavior per spec: stops **without** reset

## Report deliverables (required by the spec)

Each student must demonstrate the project and produce a report containing a
**sketch, description, matrix, ladder logic diagram, logic description, and
project summary**. The matrix is the instructor's chart; the logic description
is the numbered sequence above.

## AI use disclosure

Course AI policy permits assistance **with attribution, verification, and
reflection**. Note the assistance in the submission. Be ready to explain the
seal-ins, why TMRA is required rather than TMR, and the interposing-relay
pattern — those are what the project is testing.
