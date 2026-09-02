# INTC 1343 — Instrumentation and Process Control Workbook

*Instrumentation and Process Control Workbook*, Weedon, American Technical
Publishers, © 2019 (ISBN 9780826934475) — the required workbook for INTC 1343.

**Part 1 Instrumentation · Chapter 1 — Instrumentation Overview · Activities**

## Activity 1-1 — Fractions and Decimals (p. 3)

Fractions → decimals: 1) 1/4 = .25 · 2) 7/8 = .875 · 3) 9/16 = .5625 ·
4) 7/12 = .583 (repeating; .58 rounded) · 5) 11/20 = .55

Fractions → percentages: 6) 25% · 7) 87.5% · 8) 56.25% · 9) 58.33% · 10) 55%

Decimals → fractions: 11) 23/100 · 12) 47/100 · 13) 83/100 · 14) 0.375 = 3/8 ·
15) 0.625 = 5/8  *(23, 47, 83 are prime — those three don't reduce)*

Decimals → percentages: 16) 23% · 17) 47% · 18) 83% · 19) 37.5% · 20) 62.5%

Percentages → decimals: 21) 0.13 · 22) 0.03 · 23) 0.67 · 24) 0.355 ·
25) 183.2% = **1.832** *(>1 — over-range, normal in instrumentation)*

## Activity 1-2 — Calculation Order and Rearranging Equations (p. 4)

Order of operations: **1. powers and roots · 2. multiplication and division ·
3. addition and subtraction.** Nested parentheses: innermost set first, work out.

1) [(2.9)² × (30−3)^⅓ + 1.03]² = **689.59**
2) [(5.9)^½ − 2.1]² − [(8.0)^⅓ − 1.1]² = **−0.702**
3) {(2.3−1.1)³ × [0.31 × (5.7−2.6)]² ÷ (8.7+0.7)^½}^½ = **0.721**

| # | Equation | Solve for | Answer |
| --- | --- | --- | --- |
| 4 | E = I × R | R | R = E ÷ I |
| 5 | E = I × R | I | I = E ÷ R |
| 6 | F = C√ΔP | C | C = F ÷ √ΔP |
| 7 | F = C√ΔP | ΔP | **ΔP = (F ÷ C)²** — two steps: divide, then square |
| 8 | F = P × A | P | P = F ÷ A |
| 9 | F = P × A | A | A = F ÷ P |
| 10 | P = H × ρ | ρ | ρ = P ÷ H |
| 11 | P = H × ρ | H | H = P ÷ ρ |

## Activity 1-3 — Scientific Notation (p. 5-6)

Rules: decimal part must be between 1 and 10. Negative exponent = reciprocal
(10⁻² = 1/100 = 0.01). Add/subtract requires **matching exponents**. Multiply:
multiply decimals, **add** exponents. Divide: divide decimals, **subtract**
exponents.

Decimal → sci: 1) 3.785×10³ · 2) 2.8312×10⁴ · 3) 2.642×10² · 4) 6.510×10¹ ·
5) 3.526×10⁶ · 11) 1.667×10⁻² · 12) 2.642×10⁻⁴ · 13) 6.0×10⁻⁵ ·
14) 9.23×10⁻¹¹ · 15) 1.00003×10⁻²

Sci → decimal: 6) 154 · 7) 28,312 · 8) 73,400 · 9) 5,643,000 · 10) 863.5 ·
16) 0.02271 · 17) 0.00003532 · 18) 0.0079 · 19) 0.0000000003953 ·
20) 0.005000002

Add/subtract: 21) 4.17×10² · 22) 8.80×10⁻⁴ · 23) 1.2412×10³ *(renormalized)* ·
24) 1.93×10² · 25) 1.019×10⁹ *(exponents differ — convert first)*

Multiply/divide: 26) 4.0502×10⁴ · 27) 5.5751×10⁻⁶ · 28) 4.77386×10³
*(renormalized)* · 29) 5.466×10⁻⁵ · 30) 6.25×10⁵ *(renormalized)*

## Saturated steam table exercise (p. 8) — linear interpolation

| Pressure (psia) | Temp (°F) | Sp Vol (ft³/lb) |
| --- | --- | --- |
| 195.729 | 380.0 | 2.3353 |
| 153.010 | 360.0 | 2.9573 |

At **365.5 °F**, position = (365.5 − 360) ÷ (380 − 360) = **0.275**

1. Pressure = 153.010 + 0.275 × 42.719 = **164.76 psia**
2. Sp Vol = 2.9573 − 0.275 × 0.6220 = **2.786 ft³/lb**

**Key trap:** specific volume moves **inversely** to temperature/pressure here —
higher pressure packs the steam denser, so each pound takes up less space.
Sanity check: the answer must fall between the two table values.
