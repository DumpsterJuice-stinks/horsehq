# Retirement tracker

A single-file, offline tool for someone starting retirement saving from zero:
work out which account you can actually open, see what contributing does over
30+ years, then track contributions and balances against the annual caps.

**File:** `retirement-tracker.html` — open it in any browser. No build step, no
dependencies, no network calls. Entries are saved to the browser's
`localStorage` and never leave the device.

## What's in it

| Section | Purpose |
|---|---|
| Which door | 401(k) vs. IRA vs. Solo 401(k), by situation — the fix differs |
| Order of operations | Cash buffer → match → high-interest debt → IRA → max 401(k) |
| Projection | Monthly-compounded model, split into contributions / match / growth |
| Contribution tracker | Running totals against the 2026 caps, with catch-up tiers |
| Accounts | All balances in one place, with an allocation breakdown |
| Reference + glossary | 2026 limits and the jargon, in plain language |

## Model

Balances compound monthly. Employee contributions are capped at the 402(g)
salary-deferral limit, with the age 50+ and ages 60–63 catch-up tiers applied
automatically. Employer match is `matchRate × min(contribution, matchLimit × pay)`.
Future-year limits are estimated by growing the 2026 figures 2% annually. Results
are nominal unless "today's dollars" is toggled, which deflates by the inflation input.

Verified against a closed-form annuity: 6% of $65,000 over 35 years at 7% returns
$556,209 from both the page and `PMT · ((1+i)^n − 1) / i`.

## Figures

2026 limits are from [IRS Notice 2025-67](https://www.irs.gov/pub/irs-drop/n-25-67.pdf)
(deferral $24,500; catch-up $8,000; ages 60–63 $11,250; total additions $72,000;
IRA $7,500 + $1,100). Update `LIM` in the script when the IRS publishes 2027 figures.

This is educational, not financial advice.
