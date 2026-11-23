# CHEAP Car Wash: Go-By Sheet, Blanks Filled (Do-more)

Source: `INSTRUCTOR_Cheap_Carwash_GoBy_Sheet.pdf` (dated 7/6/2021). It requires section
comments and an ST5 contact so Y2 blinks. Simulated in `sim/cheap_carwash_goby_sim.py`.

Internal bits are my choice; the nicknames match the sheet:
C1 = CAR IS IN PLACE, C2 = CHEAP WASH RUNNING, C3 = CHEAP CARWASH RESET. CT0.Done = "$3 PAID".

| Rung | Logic | Output |
|---|---|---|
| Comment | `7 CHEAP CAR WASH-RST` / `COIN COUNTER SECTION` | |
| 1 | UP: `X3` COIN DROP (NO). RST: `X5` MASTER RESET (NO) **OR** `C3` CHEAP CARWASH RESET (NO) | CNT CT0, preset 3 |
| Comment | `PERMISSIVE SECTION` | |
| 2 | (`X4` CAR-IN-PLACE (NO) **OR** `C1` seal (NO)) AND `X5` (NC) AND `C3` (NC) | OUT C1 CAR IS IN PLACE |
| Comment | `CHEAP CAR WASH SEQUENCE SECTION` | |
| 3 | ((`CT0.Done` $3 PAID AND `C1`) **OR** `C2` seal) AND `X5` (NC) AND `C3` (NC) | OUT C2 CHEAP WASH RUNNING |
| 4 | `C2` (NO) AND `T0.Done` (NC) | OUT Y1 SOAP PUMP |
| 5 | `C2` (NO) | TMR T0, 3.000 s |
| 6 | `ST5` $100ms (NO) AND `T0.Done` (NO) AND `T1.Done` (NC) | OUT Y2 SOAK LAMP (blinks) |
| 7 | `T0.Done` (NO) | TMR T1, 3.000 s |
| 8 | (none) | NOP |
| 9 | `T1.Done` (NO) | OUT Y3 RINSE PUMP |
| 10* | `T1.Done` (NO) | TMR T2, 3.000 s |
| 11* | `T2.Done` (NO) | OUT C3 CHEAP CARWASH RESET |
| 12* | | END |

*Rungs 10–11 are not on the sheet, which stops at rung 9. They are needed because rungs 1–3 use
CHEAP CARWASH RESET, and nothing on the sheet turns it on. Without them, rinse never stops.

Simulation results:
1. Car arrives, 3 coins → soap 3 s → soak blinks 3 s → rinse 3 s → one-scan reset clears CT0 and C2. Pass.
2. $3 paid with no car → nothing runs. Car arrives → wash starts. Pass.
3. MASTER RESET mid-wash → everything drops, the $3 is cleared, and the wash does not restart. Pass.

Note: C1 stays sealed in after the car drives away (the sheet draws it that way). It clears on the
end-of-wash reset or on MASTER RESET.
