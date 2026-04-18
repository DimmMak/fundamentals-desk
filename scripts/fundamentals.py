#!/usr/bin/env python3
"""
fundamentals-desk — live fundamental-data puller with freshness guarantees.

Primary source:  yfinance (Yahoo Finance — same as price-desk)
Parallel to price-desk. Same pattern. Same reliability.

Usage:
  python3 fundamentals.py                     → menu
  python3 fundamentals.py TICKER              → single ticker fundamentals
  python3 fundamentals.py TICKER1 TICKER2 ... → batch
  python3 fundamentals.py watchlist           → reads waypoint-capital/watchlist.md
  python3 fundamentals.py log [N]             → last N log entries
  python3 fundamentals.py --check TICKER FIELD VALUE → verify cited fundamental

Output: JSON on stdout, one record per ticker.
"""
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print(json.dumps({"error": "yfinance not installed. Run: pip install yfinance"}))
    sys.exit(2)

LOG_FILE = Path(__file__).parent.parent / "data" / "fundamentals-log.jsonl"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

CHECK_TOLERANCE_PCT = 5.0  # fundamentals tolerate slightly wider window than prices

MENU = """
📐 FUNDAMENTALS DESK — Equity Analyst
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What do you want to pull?

1. 💼 Single / batch fundamentals
     .fundamentals NVDA
     .fundamentals NVDA AMD MU           (batch)

2. ✅ Verify a cited fundamental
     .fundamentals --check NVDA pe 50    (is PE within 5% of live?)

3. 👀 Pull the watchlist
     .fundamentals watchlist             (reads waypoint-capital/watchlist.md)

4. 📜 Show recent pulls
     .fundamentals log [N]               (last N from fundamentals-log.jsonl)

5. ❓ This menu
     .fundamentals                       (no args = you see this)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: yfinance   Fields: valuation, earnings, cashflow, margins,
        balance sheet, returns, analyst targets, dividend
Logged: data/fundamentals-log.jsonl every pull
"""


def safe_round(val, digits=2):
    if val is None:
        return None
    try:
        return round(float(val), digits)
    except (TypeError, ValueError):
        return None


def log_pull(record):
    try:
        with LOG_FILE.open("a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


def get_fundamentals(ticker):
    """
    Pull full fundamental snapshot for a ticker.
    Returns dict with all metrics grouped by category.
    """
    pulled_at = datetime.now(timezone.utc).isoformat()

    try:
        tkr = yf.Ticker(ticker)
        info = tkr.info or {}

        # Basic sanity — if no info returned at all, ticker is likely invalid
        if not info or info.get("quoteType") is None and not info.get("longName"):
            record = {
                "ticker": ticker.upper(),
                "status": "ERROR",
                "error": "No fundamental data returned (ticker may be invalid)",
                "source": "yfinance",
                "pulled_at": pulled_at,
            }
            log_pull(record)
            return record

        # Build structured record
        record = {
            "ticker": ticker.upper(),
            "status": "OK",
            "name": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "currency": info.get("currency", "USD"),
            "valuation": {
                "market_cap": safe_round(info.get("marketCap"), 0),
                "enterprise_value": safe_round(info.get("enterpriseValue"), 0),
                "trailing_pe": safe_round(info.get("trailingPE")),
                "forward_pe": safe_round(info.get("forwardPE")),
                "peg_ratio": safe_round(info.get("pegRatio")),
                "price_to_sales": safe_round(info.get("priceToSalesTrailing12Months")),
                "price_to_book": safe_round(info.get("priceToBook")),
            },
            "earnings": {
                "eps_trailing": safe_round(info.get("trailingEps")),
                "eps_forward": safe_round(info.get("forwardEps")),
                "earnings_growth": safe_round(info.get("earningsGrowth"), 4),
                "earnings_quarterly_growth": safe_round(info.get("earningsQuarterlyGrowth"), 4),
            },
            "revenue": {
                "total_revenue": safe_round(info.get("totalRevenue"), 0),
                "revenue_growth_yoy": safe_round(info.get("revenueGrowth"), 4),
                "revenue_per_share": safe_round(info.get("revenuePerShare")),
            },
            "cashflow": {
                "free_cashflow": safe_round(info.get("freeCashflow"), 0),
                "operating_cashflow": safe_round(info.get("operatingCashflow"), 0),
            },
            "margins": {
                "profit_margin": safe_round(info.get("profitMargins"), 4),
                "operating_margin": safe_round(info.get("operatingMargins"), 4),
                "gross_margin": safe_round(info.get("grossMargins"), 4),
                "ebitda_margin": safe_round(info.get("ebitdaMargins"), 4),
            },
            "balance_sheet": {
                "total_cash": safe_round(info.get("totalCash"), 0),
                "total_debt": safe_round(info.get("totalDebt"), 0),
                "debt_to_equity": safe_round(info.get("debtToEquity")),
                "current_ratio": safe_round(info.get("currentRatio")),
                "quick_ratio": safe_round(info.get("quickRatio")),
            },
            "returns": {
                "return_on_equity": safe_round(info.get("returnOnEquity"), 4),
                "return_on_assets": safe_round(info.get("returnOnAssets"), 4),
            },
            "analyst": {
                "count": info.get("numberOfAnalystOpinions"),
                "recommendation_mean": safe_round(info.get("recommendationMean")),
                "recommendation_key": info.get("recommendationKey"),
                "price_target_mean": safe_round(info.get("targetMeanPrice")),
                "price_target_median": safe_round(info.get("targetMedianPrice")),
                "price_target_high": safe_round(info.get("targetHighPrice")),
                "price_target_low": safe_round(info.get("targetLowPrice")),
            },
            "dividend": {
                "dividend_yield": safe_round(info.get("dividendYield"), 4),
                "dividend_rate": safe_round(info.get("dividendRate")),
                "payout_ratio": safe_round(info.get("payoutRatio"), 4),
            },
            "shares": {
                "outstanding": safe_round(info.get("sharesOutstanding"), 0),
                "float": safe_round(info.get("floatShares"), 0),
                "held_by_institutions_pct": safe_round(info.get("heldPercentInstitutions"), 4),
                "held_by_insiders_pct": safe_round(info.get("heldPercentInsiders"), 4),
                "short_ratio": safe_round(info.get("shortRatio")),
                "short_percent_of_float": safe_round(info.get("shortPercentOfFloat"), 4),
            },
            "source": "yfinance",
            "pulled_at": pulled_at,
        }
        log_pull(record)
        return record

    except Exception as e:
        record = {
            "ticker": ticker.upper(),
            "status": "ERROR",
            "error": f"{type(e).__name__}: {str(e)}",
            "source": "yfinance",
            "pulled_at": pulled_at,
        }
        log_pull(record)
        return record


# Field aliases for --check mode
FIELD_ALIASES = {
    "pe": ("valuation", "trailing_pe"),
    "fwd_pe": ("valuation", "forward_pe"),
    "forward_pe": ("valuation", "forward_pe"),
    "trailing_pe": ("valuation", "trailing_pe"),
    "peg": ("valuation", "peg_ratio"),
    "ps": ("valuation", "price_to_sales"),
    "pb": ("valuation", "price_to_book"),
    "eps": ("earnings", "eps_trailing"),
    "fwd_eps": ("earnings", "eps_forward"),
    "fcf": ("cashflow", "free_cashflow"),
    "revenue": ("revenue", "total_revenue"),
    "revenue_growth": ("revenue", "revenue_growth_yoy"),
    "margin": ("margins", "profit_margin"),
    "profit_margin": ("margins", "profit_margin"),
    "operating_margin": ("margins", "operating_margin"),
    "gross_margin": ("margins", "gross_margin"),
    "roe": ("returns", "return_on_equity"),
    "roa": ("returns", "return_on_assets"),
    "market_cap": ("valuation", "market_cap"),
    "debt_to_equity": ("balance_sheet", "debt_to_equity"),
    "target_mean": ("analyst", "price_target_mean"),
    "target": ("analyst", "price_target_mean"),
    "yield": ("dividend", "dividend_yield"),
    "dividend_yield": ("dividend", "dividend_yield"),
}


def check_fundamental(ticker, field, cited_value):
    """Verify a cited fundamental is within CHECK_TOLERANCE_PCT of live."""
    live = get_fundamentals(ticker)
    if live["status"] != "OK":
        return {
            "ticker": ticker.upper(),
            "verdict": "ERROR",
            "reason": f"Could not fetch fundamentals: {live.get('error', 'unknown')}",
        }

    alias = FIELD_ALIASES.get(field.lower())
    if not alias:
        return {
            "ticker": ticker.upper(),
            "verdict": "ERROR",
            "reason": f"Unknown field '{field}'. Known: {', '.join(FIELD_ALIASES.keys())}",
        }

    group, key = alias
    live_value = live[group].get(key)
    if live_value is None:
        return {
            "ticker": ticker.upper(),
            "field": field,
            "verdict": "UNAVAILABLE",
            "reason": f"{field} not returned by yfinance for this ticker",
            "cited_value": cited_value,
        }

    try:
        cited_value_f = float(cited_value)
    except (TypeError, ValueError):
        return {
            "ticker": ticker.upper(),
            "verdict": "ERROR",
            "reason": f"Invalid cited value: {cited_value}",
        }

    if live_value == 0:
        delta_pct = 100.0 if cited_value_f != 0 else 0.0
    else:
        delta_pct = abs((live_value - cited_value_f) / live_value * 100)

    verdict = "STALE" if delta_pct > CHECK_TOLERANCE_PCT else "OK"
    return {
        "ticker": ticker.upper(),
        "field": field,
        "verdict": verdict,
        "cited_value": cited_value_f,
        "live_value": live_value,
        "delta_pct": round(delta_pct, 2),
        "tolerance_pct": CHECK_TOLERANCE_PCT,
    }


def read_watchlist():
    """Read tickers from waypoint-capital/watchlist.md."""
    watchlist_path = Path.home() / "Desktop/CLAUDE CODE/waypoint-capital/watchlist.md"
    if not watchlist_path.exists():
        return None, f"No watchlist at {watchlist_path}"
    tickers = []
    try:
        with watchlist_path.open() as f:
            for line in f:
                line = line.strip()
                if line.startswith("|") and "|---|" not in line and "Ticker" not in line:
                    parts = [p.strip() for p in line.split("|")]
                    for p in parts:
                        if p and p.isupper() and 1 <= len(p) <= 6 and p.isalpha():
                            if p not in tickers:
                                tickers.append(p)
                            break
    except Exception as e:
        return None, f"Could not parse watchlist: {e}"
    if not tickers:
        return None, f"No tickers found in {watchlist_path}"
    return tickers, None


def show_recent_log(n=10):
    if not LOG_FILE.exists():
        print("No fundamentals log yet. Pull something first.")
        return
    lines = LOG_FILE.read_text().strip().split("\n")
    recent = lines[-n:] if len(lines) > n else lines
    print(f"📜 Last {len(recent)} fundamentals pulls:\n")
    for line in recent:
        try:
            r = json.loads(line)
            ts = r.get("pulled_at", "—")[:19]
            ticker = r.get("ticker", "—")
            status = r.get("status", "?")
            pe = r.get("valuation", {}).get("trailing_pe", "—") if status == "OK" else "—"
            print(f"  {ts}  {ticker:>6}  {status:>6}  P/E: {pe}")
        except Exception:
            continue


def main():
    args = sys.argv[1:]

    if not args:
        print(MENU)
        sys.exit(0)

    if args[0] == "--check":
        if len(args) != 4:
            print("Usage: fundamentals.py --check TICKER FIELD VALUE")
            print(f"Known fields: {', '.join(FIELD_ALIASES.keys())}")
            sys.exit(1)
        result = check_fundamental(args[1], args[2], args[3])
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("verdict") == "OK" else 1)

    if args[0] == "watchlist":
        tickers, err = read_watchlist()
        if err:
            print(f"❌ {err}")
            sys.exit(1)
        print(f"💼 Pulling fundamentals for {len(tickers)} watchlist tickers: {' '.join(tickers)}\n")
        results = [get_fundamentals(t) for t in tickers]
        print(json.dumps(results, indent=2))
        any_error = any(r["status"] != "OK" for r in results)
        sys.exit(1 if any_error else 0)

    if args[0] == "log":
        n = 10
        if len(args) > 1:
            try:
                n = int(args[1])
            except ValueError:
                pass
        show_recent_log(n)
        sys.exit(0)

    # Default: ticker pull
    results = [get_fundamentals(t) for t in args]
    print(json.dumps(results, indent=2))
    any_error = any(r["status"] != "OK" for r in results)
    sys.exit(1 if any_error else 0)


if __name__ == "__main__":
    main()
