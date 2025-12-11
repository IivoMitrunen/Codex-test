# Codex-test
Testing how codex works

## Graphic design portfolio site overview
This repository contains a single-page portfolio built for graphic designer **Aria Lane**. The site is composed of two files: `index.html` for the markup and `styles.css` for all visual styling. It is a static site (no build tools or JavaScript) that can be opened directly in a browser.

### Page structure (`index.html`)
* **Header navigation** — A sticky header with the designer’s name and anchor links to each section.
* **Hero** — Introductory copy, call-to-action buttons, and a featured project card set against animated gradient blobs.
* **Selected work** — Three project cards with animated gradient thumbnails, titles, and descriptions.
* **Capabilities** — A muted background section with a grid of service cards describing brand, campaign, and print offerings.
* **About** — Bio copy alongside a stat card highlighting years of experience, project count, and disciplines.
* **Contact** — A two-column layout with a contact form and supporting copy encouraging inquiries.
* **Footer** — Brand statement plus external links for email, Dribbble, and Behance.

### Visual design (`styles.css`)
* **Color system & typography** — Neon-inspired palette defined as CSS variables and the “Space Grotesk” typeface for a futuristic feel.
* **Layout** — Reusable `.container` widths, responsive CSS Grid layouts for the hero, work, services, contact, and footer sections, and a sticky header with backdrop blur.
* **Components** — Gradient animated thumbnails, glassy cards with subtle borders/shadows, pill buttons (primary gradient and ghost styles), and stat/service cards.
* **Effects & animation** — Soft glow background gradients (`--gradient`), shifting background animations for work thumbnails, and a floating animation for the hero blob to keep the page lively.
* **Responsive behavior** — Media queries collapse the navigation, adjust hero spacing, and stack flex/grid layouts on smaller screens.

### How to view
Open `index.html` in any modern browser. No additional setup is required because all styling lives in `styles.css` and fonts are loaded from Google Fonts.

## Backtesting helper

A lightweight Python helper is included to fetch 1H BTC OHLCV data and scan for range-sweep entries that follow the EMA/market-structure rules you described.

### Setup
1. Install dependencies (recommend a virtual environment):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

### Download BTC OHLCV data
Fetch recent Binance candles (default: BTC/USDT, 1h, 1500 bars) and save them to CSV:
```bash
python backtest.py download --output data/btc_1h.csv
```
You can override the pair, timeframe, or limit via flags such as `--symbol BTC/BUSD --timeframe 1h --limit 2000`.

### Generate sweep signals
Run the sweep/structure-break scan against a CSV (columns: `timestamp,open,high,low,close,volume`):
```bash
python backtest.py signals data/btc_1h.csv
```
The script will print every detected setup that matches:
* **Long bias:** close > EMA50 > EMA200, sweep of range low, then close back above the range high.
* **Short bias:** close < EMA50 < EMA200, sweep of range high, then close back below the range low.
* **Range definition:** swing highs/lows detected with a three-candle pivot on each side; a range forms once both sides exist with at least three bars between them.

Use the printed timestamps and prices as a starting point for building and refining your backtests.
