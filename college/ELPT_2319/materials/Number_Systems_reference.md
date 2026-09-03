# Number Systems Reference — Binary, Octal, Decimal, Hexadecimal

Supports **Exam 04 (Ch 2 – Number Systems & Codes)** and **Digital Challenges
01 (Binary Counting), 02 (Octal Counting), 03 (Hexadecimal Counting)** — all due
**9/21/26**. Also underpins the octal I/O addressing used throughout the course
(first input card 0–7, second card 8–15).

## The one idea

The **base** of a number system is simply **how many digits it has before it
must carry**.

| System | Base | Digits | Bits per digit |
| --- | --- | --- | --- |
| Binary | 2 | 0 1 | 1 |
| Octal | 8 | 0–7 | 3 |
| Decimal | 10 | 0–9 | — |
| **Hexadecimal** | **16** | **0–9 then A B C D E F** | **4** |

In hex, **A–F are digits, not letters**: A=10, B=11, C=12, D=13, E=14, F=15.

## The odometer model

Each digit position is a wheel. A wheel spins through all its symbols; when it
passes its last symbol it snaps to **0** and **nudges the wheel to its left**.
Identical machine in every base — only the number of notches differs.

## Add-one algorithm (works in any base)

Look at the **rightmost digit** and ask:

> **Is it the highest digit in this base?** (F in hex, 7 in octal, 1 in binary,
> 9 in decimal)
>
> - **No** → replace it with the next symbol. **Done.**
> - **Yes** → write **0**, move one place left, ask again.

No arithmetic required — just walk the digit sequence and handle rollovers.
**Carries ripple only as far as they need to**, then stop.

## Worked examples (Digital Challenge 03)

**Column 1 — from 35**
```
35 36 37 38 39 3A 3B 3C 3D 3E 3F 40 41 42 43 44
              ^^^ 9 -> A, NOT 40    ^^^ F -> 0, carry
```
**Column 2 — from 3FC**
```
3FC 3FD 3FE 3FF 400 401 402 403 404 405 406 407 408 409 40A 40B
                ^^^^^^^ double carry: F->0, F->0, 3->4
```
**Column 3 — from 42FB**
```
42FB 42FC 42FD 42FE 42FF 4300 4301 4302 4303 4304 4305 4306 4307
                    ^^^^^^^^^ F->0, F->0, 2->3; the leading 4 never moves
```

## Place values

| Base | Place values (right to left) |
| --- | --- |
| Binary | 1, 2, 4, 8, 16, 32, 64, 128 |
| Octal | 1, 8, 64, 512 |
| Hex | **1, 16, 256, 4096** |

**Verification method:** convert to decimal, add 1, convert back.
- 3F = 3(16) + 15 = 63 → 64 = 40 (4 × 16) ✓
- 3FF = 3(256) + 15(16) + 15 = 1023 → 1024 = 400 ✓
- 42FF = 4(4096) + 2(256) + 15(16) + 15 = 17,151 → 17,152 = 4300 ✓

## Hex ↔ binary (why hex exists)

**One hex digit = exactly four bits.** Hex is shorthand for binary.

| Hex | Binary | Dec | | Hex | Binary | Dec |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0000 | 0 | | 8 | 1000 | 8 |
| 1 | 0001 | 1 | | 9 | 1001 | 9 |
| 2 | 0010 | 2 | | A | 1010 | 10 |
| 3 | 0011 | 3 | | B | 1011 | 11 |
| 4 | 0100 | 4 | | C | 1100 | 12 |
| 5 | 0101 | 5 | | D | 1101 | 13 |
| 6 | 0110 | 6 | | E | 1110 | 14 |
| 7 | 0111 | 7 | | **F** | **1111** | **15** |

F = 1111 = all four bits on — which is *why* F is the carry point.

Conversion is grouping: 3FC = 0011 1111 1100. Chop binary into **4-bit groups
from the right** for hex, **3-bit groups** for octal.

## Common mistakes

1. **9 → 10.** Wrong. After 9 comes **A**; six more symbols before any carry.
2. **Carrying too far.** Stop at the first digit that isn't the max (42FF → 4300,
   the 4 stays).
3. **Leading zeros.** The activity explicitly says not to add them.
