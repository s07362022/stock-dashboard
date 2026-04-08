#!/usr/bin/env python3
"""
Stock Dashboard Data Updater
Fetches latest stock data for portfolio holdings and saves to data/stocks.json
Runs via GitHub Actions daily after market close.
"""

import json
import os
from datetime import datetime, timezone, timedelta

try:
    import yfinance as yf
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])
    import yfinance as yf

TW_TZ = timezone(timedelta(hours=8))

PORTFOLIO = {
    "tw": [
        {"symbol": "2454.TW", "name": "聯發科", "buy_price": 1741, "currency": "TWD"},
        {"symbol": "2344.TW", "name": "華邦電", "buy_price": 102,  "currency": "TWD"},
        {"symbol": "1802.TW", "name": "台玻",   "buy_price": 64.5, "currency": "TWD"},
        {"symbol": "6505.TW", "name": "台塑化", "buy_price": 61.4, "currency": "TWD"},
        {"symbol": "1711.TW", "name": "永光",   "buy_price": 43,   "currency": "TWD"},
        {"symbol": "2312.TW", "name": "金寶",   "buy_price": 24.1, "currency": "TWD"},
    ],
    "us": [
        {"symbol": "AIXI", "name": "Xiao-I 小i",      "buy_price": 2.46,   "shares": 100, "currency": "USD"},
        {"symbol": "AMD",  "name": "AMD",               "buy_price": 222,    "shares": 2,   "currency": "USD"},
        {"symbol": "AVGO", "name": "Broadcom",          "buy_price": 322.10, "shares": 2,   "currency": "USD"},
        {"symbol": "ON",   "name": "ON Semiconductor",  "buy_price": 67.68,  "shares": 6,   "currency": "USD"},
        {"symbol": "ONDS", "name": "Ondas Holdings",    "buy_price": 9,      "shares": 150, "currency": "USD"},
        {"symbol": "SIDU", "name": "Sidus Space",       "buy_price": 4,      "shares": 150, "currency": "USD"},
        {"symbol": "SMH",  "name": "VanEck半導體ETF",   "buy_price": 389,    "shares": 5,   "currency": "USD"},
        {"symbol": "SOFI", "name": "SoFi Technologies", "buy_price": 16.70,  "shares": 20,  "currency": "USD"},
        {"symbol": "UNH",  "name": "UnitedHealth",      "buy_price": 309.80, "shares": 2,   "currency": "USD"},
    ],
    "watchlist": [
        {"symbol": "2330.TW", "name": "台積電", "currency": "TWD"},
        {"symbol": "2317.TW", "name": "鴻海",   "currency": "TWD"},
        {"symbol": "MRVL",    "name": "Marvell",      "currency": "USD"},
        {"symbol": "INTC",    "name": "Intel",         "currency": "USD"},
        {"symbol": "SMCI",    "name": "Super Micro",   "currency": "USD"},
    ]
}


def fetch_stock_data(symbol: str) -> dict:
    """Fetch latest stock data using yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="5d")

        if hist.empty:
            return {"error": f"No data for {symbol}"}

        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else hist.iloc[0]

        close = round(float(latest["Close"]), 2)
        prev_close = round(float(prev["Close"]), 2)
        change = round(close - prev_close, 2)
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0
        volume = int(latest["Volume"])
        high = round(float(latest["High"]), 2)
        low = round(float(latest["Low"]), 2)
        open_price = round(float(latest["Open"]), 2)

        eps = info.get("trailingEps", None)
        pe = info.get("trailingPE", None)
        market_cap = info.get("marketCap", None)
        week52_high = info.get("fiftyTwoWeekHigh", None)
        week52_low = info.get("fiftyTwoWeekLow", None)

        last_date = hist.index[-1].strftime("%Y-%m-%d")

        return {
            "close": close,
            "prev_close": prev_close,
            "change": change,
            "change_pct": change_pct,
            "open": open_price,
            "high": high,
            "low": low,
            "volume": volume,
            "eps": round(eps, 2) if eps else None,
            "pe": round(pe, 2) if pe else None,
            "market_cap": market_cap,
            "week52_high": week52_high,
            "week52_low": week52_low,
            "last_date": last_date,
        }
    except Exception as e:
        return {"error": str(e)}


def build_stock_entry(stock_def: dict, data: dict) -> dict:
    entry = {
        "symbol": stock_def["symbol"],
        "name": stock_def["name"],
        "currency": stock_def["currency"],
    }

    if "error" in data:
        entry["error"] = data["error"]
        return entry

    entry.update(data)

    if "buy_price" in stock_def:
        bp = stock_def["buy_price"]
        shares = stock_def.get("shares", 1)
        entry["buy_price"] = bp
        entry["shares"] = shares
        entry["cost"] = round(bp * shares, 2)
        entry["market_value"] = round(data["close"] * shares, 2)
        entry["pnl"] = round(data["close"] - bp, 2)
        entry["pnl_pct"] = round(((data["close"] - bp) / bp) * 100, 2)
        entry["pnl_total"] = round((data["close"] - bp) * shares, 2)

    return entry


def main():
    now = datetime.now(TW_TZ)
    result = {
        "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "tw_stocks": [],
        "us_stocks": [],
        "watchlist": [],
    }

    print(f"[{now.strftime('%H:%M:%S')}] Fetching Taiwan stocks...")
    for stock in PORTFOLIO["tw"]:
        print(f"  -> {stock['symbol']} ({stock['name']})")
        data = fetch_stock_data(stock["symbol"])
        result["tw_stocks"].append(build_stock_entry(stock, data))

    print(f"[{now.strftime('%H:%M:%S')}] Fetching US stocks...")
    for stock in PORTFOLIO["us"]:
        print(f"  -> {stock['symbol']} ({stock['name']})")
        data = fetch_stock_data(stock["symbol"])
        result["us_stocks"].append(build_stock_entry(stock, data))

    print(f"[{now.strftime('%H:%M:%S')}] Fetching watchlist...")
    for stock in PORTFOLIO["watchlist"]:
        print(f"  -> {stock['symbol']} ({stock['name']})")
        data = fetch_stock_data(stock["symbol"])
        result["watchlist"].append(build_stock_entry(stock, data))

    tw_total_pnl = sum(s.get("pnl_pct", 0) for s in result["tw_stocks"]) / max(len(result["tw_stocks"]), 1)
    us_total_cost = sum(s.get("cost", 0) for s in result["us_stocks"])
    us_total_value = sum(s.get("market_value", 0) for s in result["us_stocks"])
    us_total_pnl_pct = round((us_total_value - us_total_cost) / us_total_cost * 100, 2) if us_total_cost else 0
    result["summary"] = {
        "tw_avg_pnl_pct": round(tw_total_pnl, 2),
        "us_avg_pnl_pct": us_total_pnl_pct,
        "us_total_cost": round(us_total_cost, 2),
        "us_total_value": round(us_total_value, 2),
        "us_total_pnl": round(us_total_value - us_total_cost, 2),
        "tw_winners": sum(1 for s in result["tw_stocks"] if s.get("pnl", 0) > 0),
        "tw_losers": sum(1 for s in result["tw_stocks"] if s.get("pnl", 0) <= 0),
        "us_winners": sum(1 for s in result["us_stocks"] if s.get("pnl", 0) > 0),
        "us_losers": sum(1 for s in result["us_stocks"] if s.get("pnl", 0) <= 0),
    }

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "..", "data", "stocks.json")
    os.makedirs(os.path.dirname(data_path), exist_ok=True)

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] Data saved to {data_path}")
    print(f"  TW avg PnL: {result['summary']['tw_avg_pnl_pct']}%")
    print(f"  US avg PnL: {result['summary']['us_avg_pnl_pct']}%")


if __name__ == "__main__":
    main()
