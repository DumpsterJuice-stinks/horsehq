# TheHorseHQ.com Build Notes

## What Was Built

Full marketplace website for TheHorseHQ.com — a horse marketplace with 9 categories.

## Structure
```
work/thehorsehq/output/
├── index.html        — SPA with 4 pages (home, listings, submit, pricing) + detail modal
├── styles.css        — White + green (#16a34a) theme, mobile responsive
├── app.js            — Listings logic, filtering, localStorage persistence, form submission
├── data/
│   └── listings.json — 14 seed listings across all 9 categories
└── notes.md          — This file
```

## Seed Data
14 listings across all 9 categories:
- Racing Quarter Horse: O Reilly (featured)
- Racing Thoroughbred: Midnight Dash
- Yearlings: First Down filly, Lil Joe, Pier 59 Filly
- Roping/Rodeo Horses: Flashy Kid (featured), Vaquero Lines
- Ranch Horses: Chicks Capo (featured), Wrangler
- Horses Under 3k: Steel Gray, Slick Tricky
- Hay: Coastal Bermuda Hay
- Transporters: Lone Star Horse Transport
- Art: Custom Horse Portrait

## Features
- Featured listings section on homepage (4 featured)
- Category browsing with counts
- Listing detail modal with contact info
- Filter + sort (newest, price, featured)
- Submit form with featured toggle + live total
- Pricing page with 3 tiers
- localStorage persistence for new submissions
- Mobile responsive (hamburger menu, grid reflow)
- Green accent color throughout

## Color Palette
- Primary green: #16a34a
- Green dark: #15803d
- Green light: #dcfce7
- Background: #ffffff
- Gray scale for text hierarchy

## Fonts
- Inter (Google Fonts) — 400, 500, 600, 700, 800, 900

## Notes
- Photo placeholders via placehold.co with green/white theme
- Form submissions persist to localStorage as demo
- Real payment flow would be Square/Venmo/PayPal email links (not implemented)
- No backend — fully static with localStorage
