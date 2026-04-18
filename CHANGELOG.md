# CHANGELOG — Fundamentals Desk

---

## [2026-04-18] — v0.1.0 — Initial ship

**Trigger:** After price-desk fixed stale prices, fundamentals remained the next data-integrity gap. Yesterday's NOW rumble cited P/E 49.70; live today is 57.88 (+14% drift). Web-search-for-fundamentals is as unreliable as web-search-for-price.

### Shipped
- `scripts/fundamentals.py` — yfinance wrapper, full metric coverage
- `scripts/install.sh` — sync to `~/.claude/skills/fundamentals-desk/`
- 5-command surface: menu, TICKER pull, watchlist, log, --check
- Every pull logs to `data/fundamentals-log.jsonl`
- 5% tolerance on --check (wider than price-desk's 2% because fundamentals drift more over days)

### Data coverage per ticker
- Valuation (market cap, P/E trailing + forward, PEG, P/S, P/B, EV)
- Earnings (EPS trailing/forward, growth rates)
- Revenue (total, YoY growth, per share)
- Cashflow (FCF, operating)
- Margins (profit, operating, gross, EBITDA)
- Balance sheet (cash, debt, ratios)
- Returns (ROE, ROA)
- Analyst (consensus target, recommendation, count)
- Dividend (yield, rate, payout)
- Shares (outstanding, float, institutional %, short %)

### Validation
- NOW: all fields returned cleanly; 41 analysts, strong_buy consensus, target $168.65
- --check caught 2026-04-17 rumble's stale P/E 49.70 vs live 57.88 (14% delta → STALE verdict)

### Same pattern as price-desk
```
price-desk       → .price TICKER       → live price
fundamentals-desk → .fundamentals TICKER → live fundamentals
```
Together they cover ~90% of numeric claims a rumble makes.
