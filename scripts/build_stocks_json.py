# -*- coding: utf-8 -*-
"""
=============================================================================
  Equity Cockpit — stocks.json 官方模板（v3，2026-05-02 起）
=============================================================================
本腳本是 dashboard 唯一允許的 stocks.json 產生器。
所有欄位結構嚴格對齊 index.html 的渲染函式（renderXxx）。

★ 更新流程（每日／盤後）：★
  1. 只修改下方「==== 1. 可變值區 ====」的 5 個區塊（持倉、大盤、新聞...）
  2. 不要動「==== 2. 結構區 ====」的任何 key 名稱
  3. 執行：
       python scripts\build_stocks_json.py
  4. 提交：
       git add data/stocks.json UPDATE_LOG.md
       git commit -m "update: portfolio YYYY-MM-DD HH:MM"
       git push origin master

★ 禁止：★
  - 不要用 update_data.py / push_dashboard.py --fetch（會覆寫成錯誤的舊持倉）
  - 不要新增/移除 23 個頂層欄位
  - 不要改 actions.A/B 的 strategy/stop/target 欄位名
  - 不要改 actions.C 的 action/reason 欄位名
  - 不要把 horizon_views.tomorrow_tw_strategy 改成只有 summary

詳細欄位規範見 SCHEMA.md 與 UPDATE_LOG.md。
=============================================================================
"""
import json
from datetime import datetime

# =============================================================================
#  ==== 1. 可變值區（每次更新只改這裡） ====
# =============================================================================

FX = 31.355                                     # 匯率 USD→TWD（2026/05/31 券商截圖）
UPDATE_NOTE = "2026/05/31 庫存以券商截圖為準（7檔全持有）。核心 0050/00631L/2330 永久不賣；SMH/DDOG/CSCO/NVDA 為 3 個月可變現部位（10/31 需用錢）。已清除所有五月過時敘述。"

CASH_ON_HAND = 0                                   # 無額外現金（資金在持倉中）
CASH_TO_DEPLOY = 0
CASH_NEED_DATE = "2026-10-31"                      # 十月底需用錢→美股4檔須於此前變現

# ---- 1.1 台股持倉（券商 2026/05/31 截圖）----
TW = [
    {"symbol":"0050.TW","name":"元大台灣50","shares":3210,"buy_price":65.93,"close":105.4,"change":4.9,"pct":4.88,"sector":"ETF（核心，永久持有）","tag":"core"},
    {"symbol":"00631L.TW","name":"元大台灣50正2","shares":4350,"buy_price":28.42,"close":36.94,"change":2.47,"pct":7.17,"sector":"ETF (=0050 2X，核心永久)","tag":"core","underlying":"0050","multiplier":2},
    {"symbol":"2330.TW","name":"台積電","shares":25,"buy_price":2145.6,"close":2355.0,"change":60.0,"pct":2.61,"sector":"半導體（核心永久）","tag":"core"},
]

# ---- 1.2 美股持倉（券商 2026/05/31 截圖；3 個月可變現部位）----
US = [
    {"symbol":"SMH","name":"VanEck Semiconductor ETF","shares":7,"buy_price":454.734285,"close":598.93,"change":-0.9,"pct":-0.15,"sector":"半導體 ETF（3個月）","tag":"satellite"},
    {"symbol":"DDOG","name":"Datadog Inc.","shares":4,"buy_price":220.661667,"close":247.35,"change":22.11,"pct":9.82,"sector":"雲監控／AI 可觀測性（3個月）","tag":"satellite"},
    {"symbol":"CSCO","name":"Cisco Systems","shares":3,"buy_price":116.583333,"close":120.42,"change":1.78,"pct":1.5,"sector":"通訊／AI 網路（3個月）","tag":"satellite"},
    {"symbol":"NVDA","name":"NVIDIA Corporation","shares":1,"buy_price":234.59,"close":211.14,"change":-3.11,"pct":-1.45,"sector":"AI GPU（3個月）","tag":"satellite"},
]

# =============================================================================
#  ==== 2. 結構區（不要改 key 名稱！） ====
# =============================================================================

# ========= 計算 PnL =========
def calc_tw(stocks):
    tot_mv = tot_cost = 0
    for s in stocks:
        s["market_value"] = round(s["shares"] * s["close"])
        s["cost"] = round(s["shares"] * s["buy_price"])
        s["pnl"] = round(s["market_value"] - s["cost"])
        s["pnl_pct"] = round(s["pnl"]/s["cost"]*100, 2) if s["cost"] else 0
        tot_mv += s["market_value"]; tot_cost += s["cost"]
    for s in stocks:
        s["weight"] = round(s["market_value"]/tot_mv*100, 2) if tot_mv else 0
    return tot_mv, tot_cost

def calc_us(stocks, fx):
    tot_mv_usd = tot_cost_usd = tot_mv_twd = 0
    for s in stocks:
        s["market_value_usd"] = round(s["shares"] * s["close"], 2)
        s["market_value_twd"] = round(s["market_value_usd"] * fx)
        s["cost_usd"] = round(s["shares"] * s["buy_price"], 2)
        s["pnl_usd"] = round(s["market_value_usd"] - s["cost_usd"], 2)
        s["pnl_pct"] = round(s["pnl_usd"]/s["cost_usd"]*100, 2) if s["cost_usd"] else 0
        tot_mv_usd += s["market_value_usd"]; tot_cost_usd += s["cost_usd"]
        tot_mv_twd += s["market_value_twd"]
    for s in stocks:
        s["weight"] = round(s["market_value_twd"]/tot_mv_twd*100, 2) if tot_mv_twd else 0
    return tot_mv_usd, tot_cost_usd, tot_mv_twd

tw_mv, tw_cost = calc_tw(TW)
us_mv_usd, us_cost_usd, us_mv_twd = calc_us(US, FX)
us_cost_twd = round(us_cost_usd * FX)
holdings_mv = tw_mv + us_mv_twd
total_mv = holdings_mv + CASH_ON_HAND
total_cost = tw_cost + us_cost_twd + CASH_ON_HAND

def safe_pct(num, den):
    return round(num / den * 100, 2) if den else 0.0

tw_w = sum(1 for s in TW if s["pnl"] > 0); tw_l = sum(1 for s in TW if s["pnl"] < 0)
us_w = sum(1 for s in US if s["pnl_usd"] > 0); us_l = sum(1 for s in US if s["pnl_usd"] < 0)

# ========= 完整資料 =========
data = {
    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "updated_at_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
    "fx_rate": FX,

    "user_strategy": {
        "philosophy": "2026/05/31：核心 0050/00631L/2330 永久持有不賣；美股 SMH/DDOG/CSCO/NVDA 視為 3 個月可變現部位，因 10/31 需用錢→9 月起分批了結。重點是保護獲利、確保 10 月底現金到位。",
        "leverage_map": [
            {"etf":"00631L","underlying":"0050","multiplier":2,"treat_as":"long_term_core"},
        ]
    },

    "summary": {
        "total_market_value_twd": total_mv,
        "total_cost_twd": total_cost,
        "total_pnl_twd": total_mv - total_cost,
        "total_pnl_pct": safe_pct(total_mv - total_cost, total_cost),
        "tw_market_value_twd": tw_mv,
        "tw_cost_twd": tw_cost,
        "tw_pnl_twd": tw_mv - tw_cost,
        "tw_pnl_pct": safe_pct(tw_mv - tw_cost, tw_cost),
        "us_market_value_twd": us_mv_twd,
        "us_cost_twd": us_cost_twd,
        "us_pnl_twd": us_mv_twd - us_cost_twd,
        "us_pnl_pct": safe_pct(us_mv_twd - us_cost_twd, us_cost_twd),
        "us_market_value_usd": round(us_mv_usd, 2),
        "us_cost_usd": round(us_cost_usd, 2),
        "us_pnl_usd": round(us_mv_usd - us_cost_usd, 2),
        "tw_pct": safe_pct(tw_mv, total_mv),
        "us_pct": safe_pct(us_mv_twd, total_mv),
        "cash_pct": safe_pct(CASH_ON_HAND, total_mv),
        "winners": tw_w + us_w,
        "losers": tw_l + us_l,
        "holdings_count": len(TW) + len(US),
        "cash_on_hand_twd": CASH_ON_HAND,
        "cash_to_deploy_twd": CASH_TO_DEPLOY,
        "cash_need_date": CASH_NEED_DATE,
        "effective_exposure_twd": holdings_mv,
        "effective_leverage_ratio": 1.0,
    },

    "pnl_split": {
        "tw": {
            "title": f"🇹🇼 台股核心（永久持有不賣）+{round(safe_pct(tw_mv - tw_cost, tw_cost),1)}%",
            "market_value_twd": tw_mv, "cost_twd": tw_cost,
            "pnl_twd": tw_mv - tw_cost,
            "pnl_pct": safe_pct(tw_mv - tw_cost, tw_cost),
            "winners": tw_w, "losers": tw_l,
            "highlight": "0050 +60.8%、00631L +29.5%、2330 +9.2%；壓艙石，不變現。",
            "verdict": "0050/00631L/2330 永久持有，不在 10 月變現範圍。"
        },
        "us": {
            "title": f"🇺🇸 美股（3 個月可變現部位）{'+' if (us_mv_usd - us_cost_usd)>=0 else ''}{round(safe_pct(us_mv_usd - us_cost_usd, us_cost_usd),1)}%",
            "market_value_twd": us_mv_twd, "cost_twd": us_cost_twd,
            "pnl_twd": us_mv_twd - us_cost_twd,
            "pnl_pct": safe_pct(us_mv_twd - us_cost_twd, us_cost_twd),
            "market_value_usd": round(us_mv_usd, 2),
            "cost_usd": round(us_cost_usd, 2),
            "pnl_usd": round(us_mv_usd - us_cost_usd, 2),
            "winners": us_w, "losers": us_l,
            "highlight": "SMH +31.7%、DDOG +12.1%、CSCO +3.3%、NVDA -10.0%。",
            "verdict": "因 10/31 用錢→9 月起分批了結；SMH/DDOG 留尾段、NVDA 反彈先出。"
        }
    },

    "indices": [
        {"name":"S&P 500","code":"SPX","value":7580.07,"change":16.44,"pct":0.22},
        {"name":"NASDAQ","code":"IXIC","value":26972.62,"change":55.15,"pct":0.21},
        {"name":"Dow Jones","code":"DJI","value":51032.34,"change":363.37,"pct":0.72},
        {"name":"SMH(費半ETF)","code":"SMH","value":598.93,"change":-0.9,"pct":-0.15},
        {"name":"VIX","code":"VIX","value":16.5,"change":-0.8,"pct":-4.6},
        {"name":"10Y美債","code":"US10Y","value":4.44,"change":-0.01,"pct":-0.23},
        {"name":"台股加權","code":"TWII","value":44954.0,"change":580.0,"pct":1.31},
    ],

    "tw_stocks": TW,
    "us_stocks": US,

    "effective_exposure": [
        {"name":"0050＋00631L（核心永久）","icon":"🇹🇼","components":["0050×3210","00631L×4350"],"exposure_twd":499023,"pct_effective":61.7,"long_term":True},
        {"name":"台積電 2330（核心永久）","icon":"🏭","components":["2330 25股"],"exposure_twd":58875,"pct_effective":7.3,"long_term":True},
        {"name":"美股半導體（SMH×7，3個月）","icon":"🔌","components":["SMH ETF"],"exposure_twd":131456,"pct_effective":16.3,"long_term":False},
        {"name":"美股成長（DDOG/CSCO/NVDA，3個月）","icon":"🤖","components":["DDOG×4","CSCO×3","NVDA×1"],"exposure_twd":48970,"pct_effective":6.1,"long_term":False},
    ],

    "underlying_analysis": [
        {
            "ticker":"SMH","name":"VanEck SMH（×7）","price":598.93,"today_pct":-0.15,"in_portfolio_twd":131456,
            "thesis":"費半超週期；+31.7% 最大獲利部位；占美股約 73%。",
            "pros":["AI 晶片超週期","HBM 短缺","5月費半+22%"],
            "cons":["高檔震盪","10月需變現"],
            "consensus_target":"$620-660","rating":"Buy","next_catalyst":"COMPUTEX/NVDA 供應鏈","user_action":"🟢 留至 9 月尾段；停損$540"
        },
        {
            "ticker":"DDOG","name":"Datadog（×4）","price":247.35,"today_pct":9.82,"in_portfolio_twd":31023,
            "thesis":"5/29 +9.8%；雲監控+AI 可觀測性；BTIG 目標 $255。",
            "pros":["+12.1% 獲利","AI 工作負載","Strong Buy"],
            "cons":["高估值","波動大"],
            "consensus_target":"$255（BTIG）","rating":"Buy","next_catalyst":"8/6 財報","user_action":"🟢 8/6 財報後分批了結"
        },
        {
            "ticker":"CSCO","name":"Cisco（×3）","price":120.42,"today_pct":1.5,"in_portfolio_twd":11327,
            "thesis":"Q3 FY26 +12%；AI 訂單 $9B；HSBC 目標 $137。",
            "pros":["穩健","股息","AI 網通"],
            "cons":["成長較低"],
            "consensus_target":"$124-137","rating":"Buy","next_catalyst":"8/19 財報","user_action":"🟢 穩健留；目標$130 了結"
        },
        {
            "ticker":"NVDA","name":"NVIDIA（×1）","price":211.14,"today_pct":-1.45,"in_portfolio_twd":6620,
            "thesis":"財報強但股價弱；唯一虧損 -10%；與 SMH 重疊。",
            "pros":["共識$304","AI 龍頭"],
            "cons":["-10% 虧損","與 SMH 重疊"],
            "consensus_target":"均值 $304","rating":"Strong Buy","next_catalyst":"8/26 財報","user_action":"🟡 反彈至 $220-230 先出（重疊）"
        },
    ],

    # ===== horizon_views（必須匹配渲染函式期望）=====
    "horizon_views": {
        "short_term_1m": {
            "title": "🔭 短線（~1 個月，6 月）情境",
            "intro": "核心 0050/00631L/2330 永久持有不動。美股 4 檔（SMH/DDOG/CSCO/NVDA）為 3 個月可變現部位：6 月先觀察強弱、守停損，9 月起分批了結以備 10/31 用錢。台股 4.5 萬點過熱（融資新高），不追高。",
            "tw_index": {
                "current": 44954.0,
                "bull": 46500, "p_bull": 30,
                "base": 44000, "p_base": 45,
                "bear": 41000, "p_bear": 25,
                "scenario": "多頭：COMPUTEX+AI CapEx 延續；基本：高檔震盪換手；空頭：融資過熱回檔+Fed 鷹派",
            },
            "forecasts": [
                {"symbol":"0050.TW","name":"元大台灣50","current":105.4,"bull":112,"base":107,"bear":98,"view":"核心永久持有；不變現"},
                {"symbol":"2330.TW","name":"台積電","current":2355,"bull":2600,"base":2450,"bear":2200,"view":"核心永久持有；AI 製造定錨"},
                {"symbol":"SMH","name":"VanEck SMH（7股）","current":598.93,"bull":660,"base":620,"bear":540,"view":"+31.7% 最大獲利；留至 9 月尾段變現；停損$540"},
                {"symbol":"DDOG","name":"Datadog（4股）","current":247.35,"bull":275,"base":255,"bear":225,"view":"+12.1%；8/6 財報後了結"},
                {"symbol":"CSCO","name":"Cisco（3股）","current":120.42,"bull":137,"base":128,"bear":110,"view":"+3.3% 穩健；目標$130 了結"},
                {"symbol":"NVDA","name":"NVIDIA（1股）","current":211.14,"bull":250,"base":220,"bear":185,"view":"-10% 唯一虧損；反彈$220-230 先出（與 SMH 重疊）"},
            ]
        },
        "long_term": {
            "title": "🏔️ 核心永久持有 vs 3 個月變現部位",
            "intro": "核心（0050/00631L/2330）永久不賣；美股 4 檔屬 3 個月部位，因 10/31 需用錢須在此前了結。",
            "core_long_term_buys": [
                {"symbol":"0050.TW","name":"元大台灣50","view":"永久壓艙石 +60.8%；不變現"},
                {"symbol":"00631L.TW","name":"台灣50正2","view":"永久持有 +29.5%；不變現"},
                {"symbol":"2330.TW","name":"台積電","view":"AI 製造主軸 +9.2%；永久不賣"},
            ],
            "satellite_growth": [
                {"symbol":"SMH","name":"VanEck SMH","view":"3個月部位 +31.7%；9 月尾段了結"},
                {"symbol":"DDOG","name":"Datadog","view":"3個月部位 +12.1%；8/6 財報後了結"},
                {"symbol":"CSCO","name":"Cisco","view":"3個月部位 +3.3%；目標$130 了結"},
            ],
            "exit_or_reduce": [
                {"symbol":"NVDA","name":"NVIDIA（1股）","view":"-10% 與 SMH 重疊；反彈先出，或跌破$200 認賠"},
            ]
        },
        "peak_decision": {
            "title": "❓ 持有 / 了結？— 3 個月變現判斷",
            "current_status": "2026/05/31：核心 0050/00631L/2330 永久持有；美股 SMH/DDOG/CSCO/NVDA 共約 NT$18 萬，因 10/31 用錢需於 9-10 月分批了結。",
            "verdict": "核心不動；美股 4 檔以「保護獲利」為先：NVDA 反彈先出、SMH/DDOG 留尾段、CSCO 達標了結。9 月啟動每週減倉。",
            "actions": [
                {"type":"🟢 核心永久持有","items":[
                    "0050 / 00631L / 2330：不在 10 月變現範圍，續抱",
                ]},
                {"type":"🟡 3 個月續抱（守停損）","items":[
                    "SMH×7：+31.7% 最大部位，留至 9 月尾段；停損$540",
                    "DDOG×4：+12.1%；8/6 財報後分批了結",
                    "CSCO×3：+3.3% 穩健；目標$130 了結",
                ]},
                {"type":"🔴 優先了結","items":[
                    "NVDA×1：-10% 與 SMH 重疊；反彈$220-230 先出或跌破$200 認賠",
                ]},
                {"type":"⚫ 變現紀律","items":[
                    "9/1 起每週了結美股部位 25-30%，10/25 前清空",
                    "若 9 月遇急跌，弱者（NVDA）先砍、強者（SMH）留尾段",
                ]},
            ],
            "cash_target": "10/31 前美股 4 檔全數變現為現金；核心台股不動。"
        },
        "tomorrow_tw_strategy": {
            "title": "📆 6 月 / 隔日操作重點",
            "macro_context": [
                "📌 台股 4.5 萬歷史新高；融資創新高為過熱警訊",
                "📌 美股 S&P 7580 九週連漲；DDOG 5/29 +9.8%",
                "📌 Fed 6 月預期維持利率；核心 PCE 3.3% 偏高",
                "📌 核心 0050/00631L/2330 永久不動",
                "📌 美股 4 檔為 3 個月部位，10/31 前須變現",
            ],
            "morning_plan": [
                {"step":1,"action":"核心檢視","detail":"🟢 0050/00631L/2330 永久持有，不操作"},
                {"step":2,"action":"SMH×7","detail":"🟢 +31.7% 留尾段；跌破$540 才減"},
                {"step":3,"action":"DDOG×4","detail":"🟢 +12.1%；8/6 財報前持有"},
                {"step":4,"action":"CSCO×3","detail":"🟢 穩健；達$130 了結"},
                {"step":5,"action":"NVDA×1","detail":"🟡 反彈$220-230 先出（與 SMH 重疊）"},
            ],
            "one_line": "核心永久不動；美股 4 檔守停損、9 月起分批了結，確保 10/31 現金到位。"
        }
    },

    "news": [
        {"date":"2026-05-31","category":"台股","title":"台股 5 月大漲衝 44954 歷史新高；COMPUTEX+黃仁勳行情；外資 5 月買超約 2360 億","impact":"positive","source":"鉅亨網 / 自由財經"},
        {"date":"2026-05-31","category":"⚠️ 警示","title":"投顧示警：融資餘額創新高、市值膨脹快於資金供給；高檔震盪加劇，不宜追高","impact":"mixed","source":"鉅亨網"},
        {"date":"2026-05-31","category":"持倉","title":"庫存現況：台股 0050/00631L/2330（核心永久）；美股 SMH+31.7%、DDOG+12.1%、CSCO+3.3%、NVDA-10.0%","impact":"positive","source":"券商對帳截圖"},
        {"date":"2026-05-29","category":"美股","title":"S&P 約 7580 九週連漲創新高；DDOG +9.8%；5 月 S&P 約 +5%","impact":"positive","source":"Sunday Guardian / Daily Times"},
        {"date":"2026-05-29","category":"Fed","title":"Fed 6 月預期維持利率；核心 PCE 約 3.3% 仍高於 2% 目標；通膨僵固","impact":"mixed","source":"TowneBank / Pluang"},
        {"date":"2026-05-29","category":"台股","title":"2330 +2.61% 至 2355；0050 +4.88% 至 105.4；半導體領漲","impact":"positive","source":"BigGo Finance"},
        {"date":"2026-05-26","category":"分析師","title":"BTIG 上調 DDOG 目標至 $255（Buy）；雲監控／AI 可觀測性受追捧","impact":"positive","source":"GuruFocus"},
    ],

    "earnings": [
        {"ticker":"DDOG","name":"Datadog（持倉×4）","period":"Q1 2026","revenue":"YoY +25%+","eps":"超預期","highlight":"5/29 股價 +9.8%；AI 可觀測性；BTIG 目標 $255；下次財報 8/6","rating":"Buy"},
        {"ticker":"NVDA","name":"NVIDIA（持倉×1）","period":"Q1 FY27 (5/20)","revenue":"$81.6B (+85%)","eps":"$1.87 adj.","highlight":"資料中心$75.2B；下季指引$91B；股價走弱（持倉 -10%）；下次財報 8/26","rating":"Strong Buy"},
        {"ticker":"CSCO","name":"Cisco（持倉×3）","period":"Q3 FY26 (5/13)","revenue":"$15.8B (+12%)","eps":"$1.06 adj.","highlight":"AI 訂單 FY26 $9B；毛利66%；下次財報 8/19","rating":"Buy"},
        {"ticker":"SMH","name":"VanEck SMH（持倉×7）","period":"ETF（成分財報）","revenue":"—","eps":"—","highlight":"費半 5 月約 +22%；持倉 +31.7% 最大獲利；追蹤 NVDA/TSM/AVGO 等","rating":"Buy"},
        {"ticker":"2330.TW","name":"台積電（核心永久）","period":"Q1 2026","revenue":"$35.9B (+35.1%)","eps":"NT$22.08","highlight":"毛利 66.2%；全年指引>30%；CoWoS 滿載至 2027；7/16 法說","rating":"Strong Buy"},
    ],

    "analysts": {
        "panel": ["巴菲特","芒格","Cathie Wood","Michael Burry","Peter Lynch","Ray Dalio","Druckenmiller","葛拉漢","索羅斯","科斯托蘭尼","Jim Simons","動能派","價值派","成長派","宏觀策略","風控長","產業專家","量化派","ESG"],
        "votes": [
            {"symbol":"2330.TW","name":"台積電（核心永久）","sell":0,"hold":4,"buy":15,"label":"AI 製造主軸"},
            {"symbol":"0050.TW","name":"元大台灣50（核心永久）","sell":0,"hold":6,"buy":13,"label":"大盤壓艙石"},
            {"symbol":"SMH","name":"VanEck SMH（持倉×7）","sell":1,"hold":5,"buy":13,"label":"費半超週期"},
            {"symbol":"DDOG","name":"Datadog（持倉×4）","sell":2,"hold":6,"buy":11,"label":"AI 可觀測性"},
            {"symbol":"CSCO","name":"Cisco（持倉×3）","sell":1,"hold":9,"buy":9,"label":"AI 網通穩健"},
            {"symbol":"NVDA","name":"NVIDIA（持倉×1）","sell":2,"hold":6,"buy":11,"label":"AI GPU（與SMH重疊）"},
        ]
    },

    "picks": [
        {"rank":1,"ticker":"SMH","name":"VanEck SMH（持倉×7）","market":"US","price":598.93,"target_low":620,"target_high":660,"upside_pct":7.0,"thesis":"+31.7% 最大獲利；費半超週期；留至 9 月尾段了結；停損$540","type":"3個月續抱"},
        {"rank":2,"ticker":"DDOG","name":"Datadog（持倉×4）","market":"US","price":247.35,"target_low":255,"target_high":275,"upside_pct":9.0,"thesis":"+12.1%；BTIG $255；8/6 財報後分批了結","type":"3個月續抱"},
        {"rank":3,"ticker":"CSCO","name":"Cisco（持倉×3）","market":"US","price":120.42,"target_low":128,"target_high":137,"upside_pct":8.0,"thesis":"+3.3% 穩健；AI 訂單 $9B；達$130 了結","type":"3個月續抱"},
        {"rank":4,"ticker":"NVDA","name":"NVIDIA（持倉×1）","market":"US","price":211.14,"target_low":220,"target_high":250,"upside_pct":5.0,"thesis":"-10% 唯一虧損；與 SMH 重疊；反彈$220-230 先出","type":"優先了結"},
        {"rank":5,"ticker":"2330","name":"台積電（核心永久）","market":"TW","price":2355,"target_low":2450,"target_high":2600,"upside_pct":4.0,"thesis":"+9.2% AI 製造主軸；永久持有，不在變現範圍","type":"核心永久"},
        {"rank":6,"ticker":"0050","name":"元大台灣50（核心永久）","market":"TW","price":105.4,"target_low":107,"target_high":112,"upside_pct":2.0,"thesis":"+60.8% 壓艙石；永久持有不賣","type":"核心永久"},
        {"rank":7,"ticker":"00631L","name":"台灣50正2（核心永久）","market":"TW","price":36.94,"target_low":38,"target_high":40,"upside_pct":3.0,"thesis":"+29.5% =0050 2X；永久持有不賣","type":"核心永久"},
    ],

    # ===== actions（A/B 用 strategy/stop/target；C 用 action/reason）=====
    "actions": {
        "A": [
            {"symbol":"NVDA","name":"NVIDIA（持倉×1）","price":211.14,"target":"反彈$220-230 先出","stop":200,"strategy":"-10% 唯一虧損且與 SMH 重疊；反彈先了結；跌破$200 認賠"},
        ],
        "B": [
            {"symbol":"SMH","name":"VanEck SMH（×7）","price":598.93,"target":"620-660","stop":540,"strategy":"+31.7% 最大部位；留至 9 月尾段，跌破$540 才減"},
            {"symbol":"DDOG","name":"Datadog（×4）","price":247.35,"target":"255-275","stop":225,"strategy":"+12.1%；8/6 財報後分批了結"},
            {"symbol":"CSCO","name":"Cisco（×3）","price":120.42,"target":"128-137","stop":110,"strategy":"+3.3% 穩健；達$130 了結"},
        ],
        "C": [
            {"symbol":"0050","name":"元大台灣50（核心永久）","price":105.4,"action":"永久持有不賣","reason":"+60.8% 壓艙石；不在 10 月變現範圍"},
            {"symbol":"00631L","name":"台灣50正2（核心永久）","price":36.94,"action":"永久持有不賣","reason":"+29.5%；=0050 2X 長期持有"},
            {"symbol":"2330","name":"台積電（核心永久）","price":2355,"action":"永久持有不賣","reason":"+9.2% AI 製造主軸；不變現"},
        ]
    },

    # ===== next_buy_recommendations（tickers 必須是物件陣列）=====
    "next_buy_recommendations": [
        {
            "scenario": "🔴 10/31 變現排程（美股 4 檔，約 NT$18 萬）",
            "tickers": [
                {"ticker":"NVDA","name":"NVIDIA（×1）","price":211.14,"rationale":"-10% 與 SMH 重疊；最優先","size_suggest":"反彈$220-230 先出","confidence":"🔴 先了結"},
                {"ticker":"DDOG","name":"Datadog（×4）","price":247.35,"rationale":"+12.1%；8/6 財報後","size_suggest":"8 月底前分批","confidence":"🟡 中段"},
                {"ticker":"CSCO","name":"Cisco（×3）","price":120.42,"rationale":"+3.3%；達標","size_suggest":"$130 了結","confidence":"🟡 中段"},
                {"ticker":"SMH","name":"VanEck SMH（×7）","price":598.93,"rationale":"+31.7% 最大獲利；留尾段","size_suggest":"9 月分批至 10/25 清空","confidence":"🟢 留最後"},
            ]
        },
        {
            "scenario": "🟢 核心永久持有（不變現，不操作）",
            "tickers": [
                {"ticker":"0050","name":"元大台灣50","price":105.4,"rationale":"+60.8% 壓艙石","size_suggest":"永久持有","confidence":"🟢 不賣"},
                {"ticker":"00631L","name":"台灣50正2","price":36.94,"rationale":"+29.5% =0050 2X","size_suggest":"永久持有","confidence":"🟢 不賣"},
                {"ticker":"2330","name":"台積電","price":2355,"rationale":"+9.2% AI 製造主軸","size_suggest":"永久持有","confidence":"🟢 不賣"},
            ]
        }
    ],

    # ===== allocation（陣列格式，非物件）=====
    "allocation": {
        "current": [
            {"label":"台股核心（0050+00631L+2330，永久）","value":69.0},
            {"label":"美股半導體（SMH×7，3個月）","value":16.3},
            {"label":"美股成長（DDOG/CSCO/NVDA，3個月）","value":6.1},
            {"label":"現金","value":0.0},
        ],
        "target": [
            {"label":"台股核心（永久不動）","value":75},
            {"label":"美股部位（9-10 月分批變現）","value":0},
            {"label":"現金（10/31 到位）","value":25},
        ]
    },

    "consensus": [
        {"symbol":"SMH","name":"VanEck 半導體 ETF（持倉×7）","rating":"Buy","target":"$620-660；費半多頭主軸","date":"2026-05-29"},
        {"symbol":"DDOG","name":"Datadog（持倉×4）","rating":"Buy","target":"$255（BTIG 5/26 上調）","date":"2026-05-26"},
        {"symbol":"CSCO","name":"Cisco（持倉×3）","rating":"Buy","target":"$124-137；AI 訂單 $9B","date":"2026-05"},
        {"symbol":"NVDA","name":"NVIDIA（持倉×1）","rating":"Strong Buy","target":"均值 $304；持倉 -10%（與 SMH 重疊）","date":"2026-05"},
        {"symbol":"2330.TW","name":"台積電（核心永久）","rating":"加碼","target":"NT$2,450-3,030","date":"2026-05"},
    ],

    "forecast": [
        {"symbol":"SMH","name":"VanEck SMH（持倉×7）","bull":660,"base":620,"bear":540,"catalyst":"費半超週期；+31.7% 最大獲利；留至 9 月尾段；停損$540"},
        {"symbol":"DDOG","name":"Datadog（持倉×4）","bull":275,"base":255,"bear":225,"catalyst":"BTIG 目標$255；AI 可觀測性；8/6 財報後了結"},
        {"symbol":"CSCO","name":"Cisco（持倉×3）","bull":137,"base":128,"bear":110,"catalyst":"AI 訂單 $9B；穩健；達$130 了結"},
        {"symbol":"NVDA","name":"NVIDIA（持倉×1）","bull":250,"base":220,"bear":185,"catalyst":"共識$304 但持倉 -10%；與 SMH 重疊；反彈先出"},
        {"symbol":"2330.TW","name":"台積電（核心永久）","bull":2600,"base":2450,"bear":2200,"catalyst":"全年>30%成長；7/16法說；CoWoS 滿載；永久持有"},
        {"symbol":"0050.TW","name":"元大台灣50（核心永久）","bull":112,"base":107,"bear":98,"catalyst":"大盤壓艙石 +60.8%；永久持有不賣"},
    ],

    # ===== capital_plan（含 status / sources / totals / options 結構）=====
    "capital_plan": {
        "title": "2026-05-31 美股 4 檔 3 個月變現規劃（10/31 用錢）",
        "sources": [
            {"src":"美股 SMH/DDOG/CSCO/NVDA 變現","amount_twd":180369,"amount_usd":5752,"status":"conditional","note":"3 個月部位，於 9-10 月分批了結為現金"},
        ],
        "totals": {
            "immediate": 0,
            "conditional": 180369,
            "total": 180369
        },
        "context": [
            "核心 0050/00631L/2330 永久持有，不在變現範圍",
            "美股 4 檔總值約 NT$18 萬，因 10/31 用錢須於 9-10 月了結",
            "美股 T+2，提前 2 個交易日下單；含匯回時間預留至 10/25",
            "原則：弱者（NVDA）先出、強者（SMH）留尾段、達標即了結",
            "無新增現金；不買進新標的",
        ],
        "options": [
            {
                "id": "A",
                "name": "分批了結（推薦 ⭐）",
                "philosophy": "守停損續抱至 8-9 月，9 月起每週減倉，10/25 清空",
                "actions": [
                    {"step":1,"fund":"NVDA×1","use":"反彈$220-230 先出","rationale":"-10% 且與 SMH 重疊，最優先"},
                    {"step":2,"fund":"DDOG×4","use":"8/6 財報後分批了結","rationale":"+12.1%；財報為最後催化"},
                    {"step":3,"fund":"CSCO×3","use":"達$130 了結","rationale":"+3.3% 穩健，達標即出"},
                    {"step":4,"fund":"SMH×7","use":"9 月分批至 10/25 清空","rationale":"+31.7% 最大獲利，留尾段"},
                ],
                "result": {
                    "post_tw_pct": 75,
                    "post_us_pct": 0,
                    "post_cash_pct": 25,
                    "post_leveraged_pct": 0,
                    "summary": "核心永久不動；美股 10/31 前全變現為現金"
                }
            },
            {
                "id": "B",
                "name": "提前了結（保守）",
                "philosophy": "8 月底前清光美股，鎖定獲利避開 9-10 月不確定",
                "actions": [
                    {"step":1,"fund":"NVDA 立即、CSCO 達標","use":"先出弱與達標","rationale":"降低波動"},
                    {"step":2,"fund":"SMH/DDOG 8 月底前分批","use":"提前變現","rationale":"提早鎖利"},
                ],
                "result": {
                    "post_tw_pct": 75,
                    "post_us_pct": 0,
                    "post_cash_pct": 25,
                    "post_leveraged_pct": 0,
                    "summary": "提早出金、確定性高；可能少賺尾段"
                }
            },
            {
                "id": "C",
                "name": "續抱到底（積極）",
                "philosophy": "守停損抱到 10 月，最後一刻才賣",
                "actions": [
                    {"step":1,"fund":"4 檔守停損續抱","use":"等更高價","rationale":"博尾段漲幅"},
                    {"step":2,"fund":"10/20-25 無條件全賣","use":"硬變現","rationale":"10/31 用錢底線"},
                ],
                "result": {
                    "post_tw_pct": 75,
                    "post_us_pct": 0,
                    "post_cash_pct": 25,
                    "post_leveraged_pct": 0,
                    "summary": "報酬上限高但若 10 月回檔恐低賣"
                }
            }
        ],
        "recommendation": {
            "primary": "A",
            "reason": "核心永久不動；美股 NVDA 先出、CSCO 達標、DDOG 過財報、SMH 留尾段，9 月起分批至 10/25 清空。",
            "secondary_if_aggressive": "C"
        },
        "risks": [
            "台股 4.5 萬過熱、融資新高，若回檔費半/SMH 同步受影響",
            "10/31 用錢硬約束→若 9-10 月回檔恐被迫低賣",
            "美股 T+2 + 匯率波動，須提前下單",
            "NVDA 與 SMH 重疊，半導體回檔時雙重曝險",
        ]
    },

    "update_log": "https://github.com/s07362022/stock-dashboard/blob/master/UPDATE_LOG.md"
}

# 寫入（路徑：相對於 repo 根，可在任何目錄執行）
import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, '..', 'data', 'stocks.json')
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'[OK] stocks.json 已重建 → {OUT}')
print(f'  總市值: NT$ {data["summary"]["total_market_value_twd"]:,}')
print(f'  總損益: NT$ {data["summary"]["total_pnl_twd"]:,} ({data["summary"]["total_pnl_pct"]}%)')
print(f'  Top keys: {len(data)}')

# 驗證
required = ['updated_at','fx_rate','user_strategy','summary','pnl_split','indices',
            'tw_stocks','us_stocks','effective_exposure','underlying_analysis',
            'horizon_views','news','earnings','analysts','picks','actions',
            'next_buy_recommendations','allocation','consensus','forecast','capital_plan']
missing = [k for k in required if k not in data]
print(f'  Required keys missing: {missing if missing else "NONE"}')

# 驗證子結構
checks = [
    ('actions.A[0].strategy', data['actions']['A'][0].get('strategy') is not None),
    ('actions.A[0].stop', data['actions']['A'][0].get('stop') is not None),
    ('actions.C[0].action', data['actions']['C'][0].get('action') is not None),
    ('actions.C[0].reason', data['actions']['C'][0].get('reason') is not None),
    ('horizon_views.short_term_1m.tw_index', 'tw_index' in data['horizon_views']['short_term_1m']),
    ('horizon_views.short_term_1m.forecasts', 'forecasts' in data['horizon_views']['short_term_1m']),
    ('horizon_views.long_term.core_long_term_buys', 'core_long_term_buys' in data['horizon_views']['long_term']),
    ('horizon_views.peak_decision.actions', 'actions' in data['horizon_views']['peak_decision']),
    ('horizon_views.tomorrow_tw_strategy.morning_plan', 'morning_plan' in data['horizon_views']['tomorrow_tw_strategy']),
    ('next_buy_recommendations[0].tickers[0].rationale', isinstance(data['next_buy_recommendations'][0]['tickers'][0], dict) and 'rationale' in data['next_buy_recommendations'][0]['tickers'][0]),
    ('allocation.current[0].label', isinstance(data['allocation']['current'][0], dict) and 'label' in data['allocation']['current'][0]),
    ('capital_plan.options[0].actions[0].rationale', 'rationale' in data['capital_plan']['options'][0]['actions'][0]),
    ('capital_plan.recommendation.primary', 'primary' in data['capital_plan']['recommendation']),
    ('capital_plan.totals.immediate', 'immediate' in data['capital_plan']['totals']),
]
print('\nSub-structure validation:')
for name, ok in checks:
    print(f'  [{"OK" if ok else "FAIL"}] {name}')
