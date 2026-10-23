# Traffic Light Project — Do-more Ladder Logic

**ELPT 2319 · Unit 10 — Traffic Light · Due 10/26/26**
Target PLC: **AutomationDirect Do-more** (Do-more Designer)

**Built to the instructor's published specification:**
`INSTRUCTOR_Traffic_Light_Logic.pdf` — "A Few Ways to Organize the Traffic
Light Logic," R. Tunstall.

---

## Instructor's output assignment

Order is **Red, Yellow, Green** per street — note Y0 is Main **RED**, not green.

| | Red | Yellow | Green |
| --- | --- | --- | --- |
| **Main Street** | **Y0** | **Y1** | **Y2** |
| **Side Street** | **Y3** | **Y4** | **Y5** |

## Full memory map

| Address | Nickname | Device |
| --- | --- | --- |
| **X0** | `START_PB` | Start pushbutton (NO) |
| **X1** | `STOP_PB` | Stop pushbutton (**NC** field-wired, NO contact in program) |
| **Y0** | `MAIN_RED` | Main St red |
| **Y1** | `MAIN_YELLOW` | Main St yellow |
| **Y2** | `MAIN_GREEN` | Main St green |
| **Y3** | `SIDE_RED` | Side St red |
| **Y4** | `SIDE_YELLOW` | Side St yellow |
| **Y5** | `SIDE_GREEN` | Side St green |
| **C0** | `SYS_RUN` | System running (seal-in) |
| **T0–T5** | — | Six sequence timers |

---

## Instructor's state table

His spec reads: *"when the element below is energized, these actions result."*

| Element | Turns ON | Turns OFF | Starts |
| --- | --- | --- | --- |
| **C0** | Y0, Y3 | — | T0 |
| **T0** | Y2 | Y0 | T1 |
| **T1** | Y1 | Y2 | T2 |
| **T2** | Y0 | Y1 | T3 |
| **T3** | Y5 | Y3 | T4 |
| **T4** | Y4 | Y5 | T5 |
| **T5** | **resets T0** | — | — |

### Which lamps are lit in each interval

| Timer running | Main Street | Side Street | Purpose |
| --- | --- | --- | --- |
| **T0** | **RED** | **RED** | **All-red clearance** |
| **T1** | **GREEN** | RED | Main traffic flows |
| **T2** | **YELLOW** | RED | Main warning |
| **T3** | **RED** | **RED** | **All-red clearance** |
| **T4** | RED | **GREEN** | Side traffic flows |
| **T5** | RED | **YELLOW** | Side warning |

> **Timer numbering is offset by one.** T0's preset sets the *all-red* duration,
> T1's sets *Main green*, T2's sets *Main yellow*, and so on. Each timer times
> the interval that follows the element above it in the instructor's table.

### Suggested presets (milliseconds)

| Timer | Interval | Preset |
| --- | --- | --- |
| T0 | All-red clearance | `2000` (2 s) |
| T1 | Main green | `30000` (30 s) |
| T2 | Main yellow | `5000` (5 s) |
| T3 | All-red clearance | `2000` (2 s) |
| T4 | Side green | `20000` (20 s) |
| T5 | Side yellow | `5000` (5 s) |

Total cycle = **64 seconds**.

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

### Rungs 2–7 — Cascading timers

```
Rung 2:     C0          T5.Done
        ----] [--------]/[---------[ TMR   T0    2000 ]----

Rung 3:     T0.Done
        ----] [--------------------[ TMR   T1   30000 ]----

Rung 4:     T1.Done
        ----] [--------------------[ TMR   T2    5000 ]----

Rung 5:     T2.Done
        ----] [--------------------[ TMR   T3    2000 ]----

Rung 6:     T3.Done
        ----] [--------------------[ TMR   T4   20000 ]----

Rung 7:     T4.Done
        ----] [--------------------[ TMR   T5    5000 ]----
```

**The reset** is the NC `T5.Done` contact in rung 2 — the instructor's
"T5 RESETS T0." Do-more's TMR is **non-retentive**, so when T0's rung goes
false the accumulator clears, which collapses T1 through T5 in the same scan.
`T5.Done` then clears, rung 2 re-enables, and T0 restarts. No reset
instruction required.

### Rungs 8–13 — Lamp outputs

```
Rung 8:     C0          T0.Done                      MAIN_RED
        ----] [--------]/[-----+------------( OUT  Y0 )----
                               |
            T2.Done            |
        ----] [----------------+

Rung 9:     T1.Done     T2.Done                      MAIN_YELLOW
        ----] [--------]/[------------------( OUT  Y1 )----

Rung 10:    T0.Done     T1.Done                      MAIN_GREEN
        ----] [--------]/[------------------( OUT  Y2 )----

Rung 11:    C0          T3.Done                      SIDE_RED
        ----] [--------]/[------------------( OUT  Y3 )----

Rung 12:    T4.Done     T5.Done                      SIDE_YELLOW
        ----] [--------]/[------------------( OUT  Y4 )----

Rung 13:    T3.Done     T4.Done                      SIDE_GREEN
        ----] [--------]/[------------------( OUT  Y5 )----
```

**Rung 8 is the only branched rung.** Main Red is lit in *two separate parts*
of the cycle — the opening all-red while T0 times, and everything from the
second clearance onward (T3, T4, T5). Two parallel branches OR those together.

### Rung 14 — End

```
        ----------------------------[ END ]----
```

---

## Verification

### Logic trace

| Interval | T0.D | T1.D | T2.D | T3.D | T4.D | T5.D | Y0 | Y1 | Y2 | Y3 | Y4 | Y5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T0 timing | 0 | 0 | 0 | 0 | 0 | 0 | **1** | 0 | 0 | **1** | 0 | 0 |
| T1 timing | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** | **1** | 0 | 0 |
| T2 timing | 1 | 1 | 0 | 0 | 0 | 0 | 0 | **1** | 0 | **1** | 0 | 0 |
| T3 timing | 1 | 1 | 1 | 0 | 0 | 0 | **1** | 0 | 0 | **1** | 0 | 0 |
| T4 timing | 1 | 1 | 1 | 1 | 0 | 0 | **1** | 0 | 0 | 0 | 0 | **1** |
| T5 timing | 1 | 1 | 1 | 1 | 1 | 0 | **1** | 0 | 0 | 0 | **1** | 0 |

Matches the instructor's table row for row.

### Safety proof — greens are mutually exclusive

- `MAIN_GREEN` (Y2) requires **T0.Done AND NOT T1.Done**
- `SIDE_GREEN` (Y5) requires **T3.Done**
- T3 cannot be done unless T2 is done, which requires T1 done
- So `T3.Done = 1` forces `NOT T1.Done = 0`

**Both greens can never be energized at once.** State this in the writeup.

The two **all-red clearance intervals** add a second layer of protection:
traffic on one street gets red before the other street sees green, so the
intersection empties between phases.

---

## Building it in Do-more Designer

- **Presets are in milliseconds.** The editor also accepts typed time units.
- **Done bit is `T0.Done`**, not bare `T0`. Also available: `T0.Acc`, `T0.Timing`.
- **Nickname every X and Y** using the table above — graded item.
- **Project name** as a comment above rung 1; **END alone** on the last rung.
- **Test with short presets** — e.g. 1000 / 6000 / 2000 / 1000 / 4000 / 2000
  gives a 16-second cycle. Restore real values before submitting.
- Watch `T0.Acc` through `T5.Acc` in the data view and confirm each handoff,
  and that `T5.Done` cleanly restarts T0.
- **Check both all-red intervals appear** — they are the part most likely to
  be missed, and the part the instructor's spec emphasizes.

## AI use disclosure

Course AI policy permits assistance **with attribution, verification, and
reflection**. Note the assistance in the submission. Be ready to explain the
seal-in circuit, the timer cascade, the self-reset, and why rung 8 needs a
parallel branch.
