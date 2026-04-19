---
name: fundamentals-desk
version: 0.1.0
role: Equity Analyst — Fundamentals
description: >
  Live fundamental-data single source of truth for Blue Hill Capital. Parallels
  price-desk but for valuation / earnings / cashflow / margins / balance sheet /
  returns / analyst targets / dividend data. Wraps yfinance. Prevents the
  stale-web-data bug that would otherwise contaminate every rumble's fundamental
  claims. Single rule: no committee analysis cites a fundamental number without
  a fundamentals-desk pull.
  Commands: .fundamentals | .fundamentals TICKER | .fundamentals watchlist | .fundamentals --check TICKER FIELD VALUE | .fundamentals log
---

<!-- CHANGELOG pointer: see CHANGELOG.md. -->

# Fundamentals Desk — The Equity Analyst

The **Equity Analyst** for Blue Hill Capital. Pulls every fundamental metric a rumble might cite: valuation, earnings, cashflow, margins, balance sheet, returns, analyst targets, dividends, share data.

**Single job:** provide live, timestamped, sourced fundamentals. Kill the stale-web-data bug for numbers just like price-desk killed it for prices.

---

## 🚨 THE INVIOLABLE RULE

**No rumble, memo, or trade cites a fundamental number (P/E, FCF, revenue growth, margins, etc.) without a fundamentals-desk pull timestamped within the last 24 hours.**

Fundamentals change only quarterly (after earnings), but the CACHED numbers in web searches can be months stale. yfinance pulls direct from Yahoo's backend. Trustworthy.

---

## 🎯 COMMANDS

### `.fundamentals TICKER [TICKER2 ...]`

Pull full fundamental snapshot. Returns nested JSON:
```
valuation:     market_cap, enterprise_value, trailing_pe, forward_pe,
               peg_ratio, price_to_sales, price_to_book
earnings:      eps_trailing, eps_forward, earnings_growth, quarterly_growth
revenue:       total_revenue, revenue_growth_yoy, revenue_per_share
cashflow:      free_cashflow, operating_cashflow
margins:       profit, operating, gross, ebitda
balance_sheet: total_cash, total_debt, debt_to_equity, current/quick ratios
returns:       return_on_equity, return_on_assets
analyst:       count, recommendation_key, price_target_mean/median/high/low
dividend:      yield, rate, payout_ratio
shares:        outstanding, float, institutional/insider ownership %,
               short_ratio, short_percent_of_float
```

Every pull logs to `data/fundamentals-log.jsonl`.

### `.fundamentals --check TICKER FIELD VALUE`

Verify a cited fundamental is within 5% of live.

Known field aliases: `pe`, `forward_pe`, `peg`, `ps`, `pb`, `eps`, `fwd_eps`, `fcf`, `revenue`, `revenue_growth`, `margin`, `operating_margin`, `gross_margin`, `roe`, `roa`, `market_cap`, `debt_to_equity`, `target_mean`, `target`, `yield`, `dividend_yield`.

Returns:
- `verdict: "OK"` — within 5% of live
- `verdict: "STALE"` — diverges >5%, DO NOT use cited value
- `verdict: "UNAVAILABLE"` — yfinance didn't return this field for this ticker
- `verdict: "ERROR"` — invalid field name or ticker

### `.fundamentals watchlist`

Reads `blue-hill-capital/watchlist.md`, pulls full fundamentals for every ticker. Useful for a weekend deep-dive.

### `.fundamentals log [N]`

Show last N (default 10) entries from `data/fundamentals-log.jsonl` — timestamp, ticker, status, trailing P/E.

### `.fundamentals` (no args)

Show the menu.

---

## 🏛️ INTEGRATION — parallel to price-desk

```
royal-rumble      at rumble start → .price TICKER
                                    .fundamentals TICKER
                                    → inject BOTH into subagent prompt
                                    → legends analyze on clean data

journalist        before memo → .fundamentals --check TICKER field value

chief-of-staff    can surface stale-fundamentals warnings
```

**Same architectural pattern as price-desk. Same reliability guarantee.** 🎯

---

## 🎭 HONEST LIMITATIONS

```
✅ GOOD FOR:
   • Large-cap US equities (NYSE/NASDAQ)
   • Recent quarterly data (most recent 10-Q/10-K)
   • Analyst consensus targets (from Yahoo's network)
   • Ownership / short-interest data

⚠️ KNOWN LIMITATIONS:
   • yfinance pulls from Yahoo; fields may be empty for some smaller tickers
   • Data is as fresh as Yahoo's own ingestion (usually 1-2 business days after filing)
   • Some fields (quick_ratio, peg_ratio) occasionally null even for major tickers
   • International ADRs sometimes have partial data

❌ DO NOT USE FOR:
   • Real-time fundamentals (doesn't exist; fundamentals are quarterly by nature)
   • Private company data
   • Point-in-time historical fundamentals (fetches current only)
```

Fundamentals are by nature slow-changing. Daily stale is fine; weekly stale is fine. Quarterly-stale (cited across an earnings event) is where you see the real divergence.

---

## 📊 AUDIT TRAIL

Every pull logs to `data/fundamentals-log.jsonl` — one JSON record per line.
Format matches `price-log.jsonl` pattern: timestamp, ticker, status, primary metric.

---

## IF NO COMMAND GIVEN

When user types `.fundamentals` with no arguments, run:
```bash
python3 ~/.claude/skills/fundamentals-desk/scripts/fundamentals.py
```

The script displays the menu natively.
