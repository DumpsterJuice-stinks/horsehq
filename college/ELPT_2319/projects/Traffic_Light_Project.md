# Traffic Light Project — Do-more Ladder Logic

**ELPT 2319 · Unit 10 — Traffic Light · Due 10/26/26**
Target PLC: **AutomationDirect Do-more** (Do-more Designer)

Main Street / Side Street signal with a 60-second repeating cycle, built from
four cascading on-delay timers.

---

## Memory / I/O assignment

Do-more memory prefixes: `X` discrete input · `Y` discrete output ·
`C` control relay · `T` timer

| Address | Nickname | Device |
| --- | --- | --- |
| **X0** | `START_PB` | Start pushbutton (NO, field-wired) |
| **X1** | `STOP_PB` | Stop pushbutton (**NC**, field-wired) |
| **Y0** | `MAIN_GREEN` | Main St green lamp |
| **Y1** | `MAIN_YELLOW` | Main St yellow lamp |
| **Y2** | `MAIN_RED` | Main St red lamp |
| **Y3** | `SIDE_GREEN` | Side St green lamp |
| **Y4** | `SIDE_YELLOW` | Side St yellow lamp |
| **Y5** | `SIDE_RED` | Side St red lamp |
| **C0** | `SYS_RUN` | System running (seal-in bit) |
| **T1** | `MAIN_GRN_TMR` | Main green duration — 30 s |
| **T2** | `MAIN_YEL_TMR` | Main yellow duration — 5 s |
| **T3** | `SIDE_GRN_TMR` | Side green duration — 20 s |
| **T4** | `SIDE_YEL_TMR` | Side yellow duration — 5 s |

> **STOP is wired NC** so a broken wire stops the signal (fail-safe). Because
> the field contact is closed at rest, the **program uses a normally-open
> contact** on X1 — it reads 1 until someone presses STOP.

---

## Sequence — 60 second cycle

| Window | Timer running | Main St | Side St |
| --- | --- | --- | --- |
| 0 – 30 s | T1 | **GREEN** | **RED** |
| 30 – 35 s | T2 | **YELLOW** | **RED** |
| 35 – 55 s | T3 | **RED** | **GREEN** |
| 55 – 60 s | T4 | **RED** | **YELLOW** |

Main Street carries the longer green as the major road.

---

## Ladder program

### Rung 1 — Start / Stop seal-in

```
      X0            X1              C0
  ----] [-----+-----] [------------( OUT )----
   START_PB   |   STOP_PB           SYS_RUN
              |
      C0      |
  ----] [-----+
   SYS_RUN
```

START energizes C0; C0's own contact **seals it in** so the button can be
released. STOP breaks the rung and drops everything.

### Rungs 2–5 — Cascading timers

```
Rung 2:     C0          T4.Done
        ----] [--------]/[---------[ TMR   T1   30000 ]----

Rung 3:     T1.Done
        ----] [--------------------[ TMR   T2    5000 ]----

Rung 4:     T2.Done
        ----] [--------------------[ TMR   T3   20000 ]----

Rung 5:     T3.Done
        ----] [--------------------[ TMR   T4    5000 ]----
```

Each timer's `.Done` bit launches the next. **Do-more's TMR is
non-retentive** — when its rung goes false the accumulator resets to 0, which
is exactly what makes the loop work:

1. T4 finishes → `T4.Done` = 1
2. The NC contact in rung 2 **opens** → T1 drops → `T1.Done` = 0
3. That collapses T2, T3, T4 in the same scan
4. `T4.Done` = 0 → rung 2 re-enables → T1 restarts

No reset instruction needed. The chain resets itself.

### Rungs 6–11 — Lamp outputs

```
Rung 6:     C0          T1.Done
        ----] [--------]/[---------( OUT  Y0 )----   MAIN_GREEN

Rung 7:     T1.Done     T2.Done
        ----] [--------]/[---------( OUT  Y1 )----   MAIN_YELLOW

Rung 8:     T2.Done
        ----] [--------------------( OUT  Y2 )----   MAIN_RED

Rung 9:     T2.Done     T3.Done
        ----] [--------]/[---------( OUT  Y3 )----   SIDE_GREEN

Rung 10:    T3.Done     T4.Done
        ----] [--------]/[---------( OUT  Y4 )----   SIDE_YELLOW

Rung 11:    C0          T2.Done
        ----] [--------]/[---------( OUT  Y5 )----   SIDE_RED
```

### Rung 12 — End

```
        ----------------------------[ END ]----
```

**The output pattern:** every lamp is on *after one timer completes but before
the next completes* — `T(n).Done AND NOT T(n+1).Done`. Contacts alone carve the
cycle into exclusive windows.

---

## Verification

### Safety proof — the greens are mutually exclusive

- `MAIN_GREEN` requires **NOT T1.Done**
- `SIDE_GREEN` requires **T2.Done**
- T2 cannot be done unless T1 is done (they cascade)
- Therefore `T2.Done = 1` forces `NOT T1.Done = 0`

**Both greens can never be energized simultaneously.** State this in the
writeup — it is the property an instructor checks first.

### Logic trace

| t | T1.Done | T2.Done | T3.Done | T4.Done | Y0 | Y1 | Y2 | Y3 | Y4 | Y5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0–30 | 0 | 0 | 0 | 0 | **1** | 0 | 0 | 0 | 0 | **1** |
| 30–35 | 1 | 0 | 0 | 0 | 0 | **1** | 0 | 0 | 0 | **1** |
| 35–55 | 1 | 1 | 0 | 0 | 0 | 0 | **1** | **1** | 0 | 0 |
| 55–60 | 1 | 1 | 1 | 0 | 0 | 0 | **1** | 0 | **1** | 0 |

Exactly one lamp per street is lit in every window.

---

## Building it in Do-more Designer

- **Timer presets are in milliseconds**: 30 s = `30000`, 5 s = `5000`,
  20 s = `20000`. The editor also accepts typed time units.
- **Done bit syntax is `T1.Done`**, not bare `T1`. Other members available:
  `T1.Acc` (accumulated value), `T1.Timing`.
- **Nickname every X and Y** — graded item. Use the table above.
- **Project name above rung 1** as a rung comment; **END alone** on the last rung.
- **Shorten presets while testing** (try 6000/2000/4000/2000) so a full cycle
  runs in 14 seconds instead of 60. Restore real values before submitting.
- Watch `T1.Acc` through `T4.Acc` in the data view to confirm transitions land
  at 30, 35, 55, 60 s and that the cycle loops cleanly.

## Possible extensions (if the assignment asks for more)

- **Pedestrian walk request** — a pushbutton on X2 latching a C bit that
  shortens the main green or inserts a walk phase
- **Flashing night mode** — a selector switch on X3 that bypasses the sequence
  and alternates both reds from a 1-second clock bit
- **All-red clearance interval** — insert a short timer between phases where
  both streets show red

## AI use disclosure

Course AI policy permits assistance **with attribution, verification, and
reflection**. Note the assistance in the submission, and be prepared to explain
the seal-in circuit and the timer cascade — those are the two concepts the
project is testing.
