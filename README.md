# 📐 Fundamentals Desk

> Equity Analyst — Fundamentals for Waypoint Capital.
> Live fundamentals via yfinance. Kills stale-web-data for numbers.

---

## Why this exists

Price-desk fixed stale prices. Fundamentals were still being cited from web search, which can return P/E values 3-6 months out of date.

**Verified example:** NOW rumble on 2026-04-17 cited P/E 49.70. Live P/E today (2026-04-18): **57.88** — 14% delta. Fundamentals-desk caught it.

---

## Install

```bash
./scripts/install.sh
```

Requires `python3` + `yfinance` (auto-installed if missing).

---

## Commands

```
.fundamentals              → menu
.fundamentals NVDA         → full fundamental snapshot
.fundamentals NVDA AMD MU  → batch
.fundamentals watchlist    → pulls everything in waypoint-capital/watchlist.md
.fundamentals log [N]      → last N log entries
.fundamentals --check TICKER FIELD VALUE → verify cited value
```

---

## Data categories pulled

- **Valuation** — market cap, EV, P/E (trailing + forward), PEG, P/S, P/B
- **Earnings** — EPS trailing/forward, growth rates
- **Revenue** — total, YoY growth, per share
- **Cashflow** — free cashflow, operating cashflow
- **Margins** — profit, operating, gross, EBITDA
- **Balance sheet** — cash, debt, debt/equity, current/quick ratios
- **Returns** — ROE, ROA
- **Analyst** — consensus target (mean/median/high/low), recommendation
- **Dividend** — yield, rate, payout ratio
- **Shares** — outstanding, float, institutional %, short interest %

---

## Honest limits

```
✅ US large-caps with recent filings
⚠️ Smaller tickers may have missing fields
⚠️ ADRs sometimes partial
❌ Real-time (doesn't exist — fundamentals are quarterly)
❌ Historical point-in-time (current only)
```

For Waypoint's watchlist (mostly large-cap tech + semis), data quality is excellent.

🃏⚔️
