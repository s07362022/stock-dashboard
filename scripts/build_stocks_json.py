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

FX = 31.425                                     # 匯率 USD→TWD（2026/06/04 券商截圖）
UPDATE_NOTE = "2026/06/04 庫存以券商截圖為準（美股 8 檔）。核心 0050/00631L/2330 永久不賣；SMH/NVDA/HPQ/VSH/DRAM + 槓桿 ETF（CWVX/NBIL/ORCX）為 3 個月可變現（10/31 需用錢）。"

CASH_ON_HAND = 0                                   # 無額外現金（資金在持倉中）
CASH_TO_DEPLOY = 0
CASH_NEED_DATE = "2026-10-31"                      # 十月底需用錢→美股4檔須於此前變現

# ---- 1.1 台股持倉（BigGo 2026/06/03 收盤）----
TW = [
    {"symbol":"0050.TW","name":"元大台灣50","shares":3210,"buy_price":65.93,"close":107.6,"change":1.9,"pct":1.8,"sector":"ETF（核心，永久持有）","tag":"core"},
    {"symbol":"00631L.TW","name":"元大台灣50正2","shares":4350,"buy_price":28.42,"close":39.22,"change":1.31,"pct":3.46,"sector":"ETF (=0050 2X，核心永久)","tag":"core","underlying":"0050","multiplier":2},
    {"symbol":"2330.TW","name":"台積電","shares":25,"buy_price":2145.6,"close":2425.0,"change":45.0,"pct":1.89,"sector":"半導體（核心永久）","tag":"core"},
]

# ---- 1.2 美股持倉（券商 2026/06/04 截圖；3 個月可變現）----
US = [
    {"symbol":"SMH","name":"VanEck Semiconductor ETF","shares":7,"buy_price":454.734285,"close":636.03,"change":3.82,"pct":0.6,"sector":"半導體 ETF","tag":"satellite"},
    {"symbol":"ORCX","name":"Defiance 2X Long ORCL Daily","shares":10,"buy_price":61.1,"close":59.36,"change":-8.53,"pct":-12.56,"sector":"2X 槓桿 ETF","tag":"speculative"},
    {"symbol":"HPQ","name":"HP Inc.","shares":20,"buy_price":28.9725,"close":26.24,"change":-1.06,"pct":-3.87,"sector":"PC／硬體","tag":"satellite"},
    {"symbol":"NBIL","name":"GraniteShares 2X Long NBIS","shares":5,"buy_price":59.664,"close":50.0,"change":-4.71,"pct":-8.61,"sector":"2X 槓桿 ETF","tag":"speculative"},
    {"symbol":"VSH","name":"Vishay Intertechnology","shares":5,"buy_price":62.55,"close":62.63,"change":0.14,"pct":0.22,"sector":"半導體元件","tag":"satellite"},
    {"symbol":"CWVX","name":"Tradr 2X Long CRWV Daily","shares":5,"buy_price":43.786,"close":35.12,"change":-4.56,"pct":-11.48,"sector":"2X 槓桿 ETF","tag":"speculative"},
    {"symbol":"NVDA","name":"NVIDIA Corporation","shares":1,"buy_price":234.59,"close":215.86,"change":-6.96,"pct":-3.12,"sector":"AI GPU","tag":"satellite"},
    {"symbol":"DRAM","name":"Roundhill Memory ETF","shares":1,"buy_price":66.7,"close":68.86,"change":-0.71,"pct":-1.02,"sector":"記憶體 ETF","tag":"satellite"},
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
        "philosophy": "2026/06/04：核心 0050/00631L/2330 永久持有；美股 8 檔（SMH 為主、含 CWVX/NBIL/ORCX 槓桿 ETF）因 10/31 需用錢→不攤平槓桿 ETF、9 月起分批了結 SMH。",
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
            "highlight": "0050 +63%、00631L +38%、2330 +13%；壓艙石，不變現。",
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
            "highlight": "SMH +40%、DRAM/VSH 持平；NVDA/HPQ/CWVX/NBIL/ORCX 虧損。",
            "verdict": "槓桿 ETF 不攤平；NVDA 反彈先出；SMH 9 月尾段變現。"
        }
    },

    "indices": [
        {"name":"S&P 500","code":"SPX","value":7609.78,"change":9.82,"pct":0.13},
        {"name":"NASDAQ","code":"IXIC","value":27093.90,"change":7.09,"pct":0.03},
        {"name":"Dow Jones","code":"DJI","value":51307.79,"change":228.91,"pct":0.45},
        {"name":"費城半導體","code":"SOX","value":13726.27,"change":760.62,"pct":5.87},
        {"name":"SMH(費半ETF)","code":"SMH","value":636.03,"change":3.82,"pct":0.6},
        {"name":"VIX","code":"VIX","value":16.5,"change":-0.8,"pct":-4.6},
        {"name":"台股加權","code":"TWII","value":45200.0,"change":250.0,"pct":0.56},
    ],

    "tw_stocks": TW,
    "us_stocks": US,

    "effective_exposure": [
        {"name":"0050＋00631L（核心永久）","icon":"🇹🇼","components":["0050×3210","00631L×4350"],"exposure_twd":516003,"pct_effective":65.8,"long_term":True},
        {"name":"台積電 2330（核心永久）","icon":"🏭","components":["2330 25股"],"exposure_twd":60625,"pct_effective":7.7,"long_term":True},
        {"name":"美股半導體（SMH×7）","icon":"🔌","components":["SMH ETF"],"exposure_twd":139912,"pct_effective":17.8,"long_term":False},
        {"name":"美股其他（7檔）","icon":"🤖","components":["NVDA/HPQ/槓桿ETF等"],"exposure_twd":67207,"pct_effective":8.6,"long_term":False},
    ],

    "underlying_analysis": [
        {
            "ticker":"SMH","name":"VanEck SMH（×7）","price":636.03,"today_pct":0.6,"in_portfolio_twd":139912,
            "thesis":"費半超週期；+40% 最大獲利；占美股約 68%。",
            "pros":["AI 晶片超週期","費城半導體 +5.9%","共識 $572-660"],
            "cons":["高檔震盪","10月需變現"],
            "consensus_target":"$620-660","rating":"Buy","next_catalyst":"COMPUTEX 延續","user_action":"🟢 續抱等 $650+；9 月尾段變現；停損$580"
        },
        {
            "ticker":"NVDA","name":"NVIDIA（×1）","price":215.86,"today_pct":-3.12,"in_portfolio_twd":6783,
            "thesis":"財報強但短線走弱；與 SMH 重疊；不建議攤平。",
            "pros":["共識約 $310","AI 龍頭"],
            "cons":["-8% 虧損","與 SMH 重疊"],
            "consensus_target":"均值 $310","rating":"Strong Buy","next_catalyst":"8/26 財報","user_action":"🟡 反彈 $220-230 減碼；跌破 $200 認賠"
        },
        {
            "ticker":"HPQ","name":"HP Inc.（×20）","price":26.24,"today_pct":-3.87,"in_portfolio_twd":16488,
            "thesis":"PC 硬體；分析師多數 Reduce；虧損 -9.4%。",
            "pros":["股息","估值低"],
            "cons":["成長慢","共識目標低於現價爭議"],
            "consensus_target":"$23（均值）","rating":"Reduce","next_catalyst":"6/3 財報","user_action":"🔴 不攤平；反彈 $28-29 減碼"
        },
        {
            "ticker":"CWVX","name":"Tradr 2X CRWV（×5）","price":35.12,"today_pct":-11.48,"in_portfolio_twd":5515,
            "thesis":"日槓桿 ETF；-19.8%；時間衰減風險。",
            "pros":["波動大時短線彈性"],
            "cons":["槓桿衰減","深套"],
            "consensus_target":"—","rating":"高風險","next_catalyst":"—","user_action":"🔴 不攤平；反彈 $40-42 出清"
        },
        {
            "ticker":"NBIL","name":"GraniteShares 2X NBIS（×5）","price":50.0,"today_pct":-8.61,"in_portfolio_twd":7853,
            "thesis":"日槓桿 ETF；-16.2%。",
            "pros":["—"],
            "cons":["槓桿衰減","單日 -8%"],
            "consensus_target":"—","rating":"高風險","next_catalyst":"—","user_action":"🔴 不攤平；$52-55 減碼"
        },
        {
            "ticker":"ORCX","name":"Defiance 2X ORCL（×10）","price":59.36,"today_pct":-12.56,"in_portfolio_twd":18654,
            "thesis":"日槓桿 ETF；今日 -12.6%；不宜長抱。",
            "pros":["ORCL 雲業務強"],
            "cons":["槓桿 ETF 波動","與單日大跌"],
            "consensus_target":"—","rating":"高風險","next_catalyst":"—","user_action":"🟡 不攤平；$62-65 逢反彈減碼"
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
        {"date":"2026-06-04","category":"持倉","title":"庫存更新：美股 8 檔（SMH/NVDA/HPQ/VSH/DRAM + CWVX/NBIL/ORCX 槓桿 ETF）；台股核心不變","impact":"mixed","source":"券商截圖 2026/06/04"},
        {"date":"2026-06-03","category":"美股","title":"S&P 7609 九連漲創高；費城半導體 +5.9%；Marvell +32%；NVDA -0.7%","impact":"positive","source":"Reuters / BigGo"},
        {"date":"2026-06-03","category":"台股","title":"2330 +1.9% 至 2425；0050 107.6；COMPUTEX 行情延續","impact":"positive","source":"BigGo Finance"},
        {"date":"2026-06-03","category":"⚠️ 風險","title":"科技板塊占 S&P 市值 39%+ 創紀錄；指數超買 RSI 75","impact":"negative","source":"Reuters / Meyka"},
        {"date":"2026-06-03","category":"策略","title":"槓桿日 ETF（CWVX/NBIL/ORCX）單日大跌；不建議攤平","impact":"negative","source":"持倉分析"},
        {"date":"2026-06-03","category":"分析師","title":"NVDA 共識目標約 $310（+39% 潛在）；HPQ 多數 Reduce","impact":"mixed","source":"MarketBeat / VCP"},
    ],

    "earnings": [
        {"ticker":"HPQ","name":"HP Inc.（×20）","period":"Q2 FY26","revenue":"待公布","eps":"—","highlight":"6/3 財報日；持倉 -9.4%；不攤平","rating":"Reduce"},
        {"ticker":"NVDA","name":"NVIDIA（×1）","period":"Q1 FY27","revenue":"$81.6B","eps":"$1.87","highlight":"共識 $310；持倉 -8%；8/26 下次財報","rating":"Strong Buy"},
        {"ticker":"SMH","name":"VanEck SMH（×7）","period":"ETF","revenue":"—","eps":"—","highlight":"持倉 +40%；成分 NVDA/TSM/AVGO","rating":"Buy"},
        {"ticker":"VSH","name":"Vishay（×5）","period":"Q2","revenue":"—","eps":"—","highlight":"8/12 財報；持平","rating":"Hold"},
        {"ticker":"2330.TW","name":"台積電（核心）","period":"Q1 2026","revenue":"+35%","eps":"NT$22.08","highlight":"7/16 法說；永久持有","rating":"Strong Buy"},
    ],

    "analysts": {
        "panel": ["巴菲特","芒格","Cathie Wood","Michael Burry","Peter Lynch","Ray Dalio","Druckenmiller","葛拉漢","索羅斯","科斯托蘭尼","Jim Simons","動能派","價值派","成長派","宏觀策略","風控長","產業專家","量化派","ESG"],
        "votes": [
            {"symbol":"2330.TW","name":"台積電（核心永久）","sell":0,"hold":4,"buy":15,"label":"AI 製造主軸"},
            {"symbol":"0050.TW","name":"元大台灣50（核心永久）","sell":0,"hold":6,"buy":13,"label":"大盤壓艙石"},
            {"symbol":"SMH","name":"VanEck SMH（×7）","sell":1,"hold":5,"buy":13,"label":"費半超週期 +40%"},
            {"symbol":"NVDA","name":"NVIDIA（×1）","sell":2,"hold":6,"buy":11,"label":"共識高、與SMH重疊"},
            {"symbol":"HPQ","name":"HP Inc.（×20）","sell":8,"hold":7,"buy":4,"label":"Reduce 居多"},
            {"symbol":"CWVX","name":"2X 槓桿 ETF 群","sell":12,"hold":4,"buy":3,"label":"不適合長抱"},
        ]
    },

    "picks": [
        {"rank":1,"ticker":"SMH","name":"VanEck SMH（×7）","market":"US","price":636.03,"target_low":650,"target_high":660,"upside_pct":4.0,"thesis":"+40% 最大獲利；等 $650+ 再分批獲利；停損$580","type":"續抱等目標"},
        {"rank":2,"ticker":"NVDA","name":"NVIDIA（×1）","market":"US","price":215.86,"target_low":220,"target_high":310,"upside_pct":44.0,"thesis":"共識 $310 但與 SMH 重疊；不攤平；反彈先出","type":"等反彈減碼"},
        {"rank":3,"ticker":"2330","name":"台積電（核心）","market":"TW","price":2425,"target_low":2500,"target_high":2600,"upside_pct":3.0,"thesis":"+13% 永久持有","type":"核心永久"},
        {"rank":4,"ticker":"0050","name":"元大台灣50（核心）","market":"TW","price":107.6,"target_low":110,"target_high":115,"upside_pct":3.0,"thesis":"+63% 壓艙石","type":"核心永久"},
        {"rank":5,"ticker":"VSH","name":"Vishay（×5）","market":"US","price":62.63,"target_low":65,"target_high":68,"upside_pct":5.0,"thesis":"持平；續抱","type":"衛星"},
        {"rank":6,"ticker":"INTC","name":"Intel（觀察 ≤$300）","market":"US","price":22.0,"target_low":25,"target_high":28,"upside_pct":15.0,"thesis":"費半輪動；未持倉","type":"觀察"},
        {"rank":7,"ticker":"AVGO","name":"Broadcom（觀察）","market":"US","price":280.0,"target_low":300,"target_high":320,"upside_pct":8.0,"thesis":"AI 網通；與 SMH 重疊度高","type":"觀察"},
    ],

    # ===== actions（A/B 用 strategy/stop/target；C 用 action/reason）=====
    "actions": {
        "A": [
            {"symbol":"SMH","name":"VanEck SMH（×7）","price":636.03,"target":"650-660","stop":580,"strategy":"+40% 最大獲利；續抱等目標區；9 月尾段變現；不追高加碼"},
        ],
        "B": [
            {"symbol":"NVDA","name":"NVIDIA（×1）","price":215.86,"target":"220-310（共識）","stop":200,"strategy":"不攤平；反彈 $220-230 減碼（與 SMH 重疊）"},
            {"symbol":"VSH","name":"Vishay（×5）","price":62.63,"target":"65-68","stop":58,"strategy":"持平小部位；續抱至 8/12 財報"},
            {"symbol":"DRAM","name":"Roundhill Memory（×1）","price":68.86,"target":"72-75","stop":64,"strategy":"+3% 小部位；記憶體景氣續抱"},
        ],
        "C": [
            {"symbol":"CWVX","name":"Tradr 2X CRWV（×5）","price":35.12,"action":"不攤平；反彈出清","reason":"-19.8% 槓桿 ETF；時間衰減"},
            {"symbol":"NBIL","name":"GraniteShares 2X NBIS（×5）","price":50.0,"action":"不攤平；減碼","reason":"-16.2% 槓桿 ETF"},
            {"symbol":"ORCX","name":"Defiance 2X ORCL（×10）","price":59.36,"action":"不攤平；逢反彈減","reason":"日槓桿；今日 -12.6%"},
            {"symbol":"HPQ","name":"HP Inc.（×20）","price":26.24,"action":"不攤平；反彈減碼","reason":"-9.4%；分析師 Reduce"},
            {"symbol":"0050","name":"元大台灣50（核心）","price":107.6,"action":"永久持有","reason":"+63% 壓艙石"},
            {"symbol":"2330","name":"台積電（核心）","price":2425,"action":"永久持有","reason":"+13% AI 製造主軸"},
        ]
    },

    # ===== next_buy_recommendations（tickers 必須是物件陣列）=====
    "next_buy_recommendations": [
        {
            "scenario": "🔴 10/31 變現排程（美股 8 檔，約 NT$20.7 萬）",
            "tickers": [
                {"ticker":"CWVX","name":"2X 槓桿 ETF 群","price":35.12,"rationale":"深套 + 時間衰減","size_suggest":"反彈出清，不攤平","confidence":"🔴 優先減"},
                {"ticker":"NBIL","name":"NBIL（×5）","price":50.0,"rationale":"-16% 槓桿","size_suggest":"$52-55 減碼","confidence":"🔴 優先減"},
                {"ticker":"NVDA","name":"NVIDIA（×1）","price":215.86,"rationale":"與 SMH 重疊","size_suggest":"$220-230 減碼","confidence":"🟡 中段"},
                {"ticker":"HPQ","name":"HP（×20）","price":26.24,"rationale":"Reduce 共識","size_suggest":"$28-29 減碼","confidence":"🟡 中段"},
                {"ticker":"SMH","name":"VanEck SMH（×7）","price":636.03,"rationale":"+40% 最大獲利","size_suggest":"9 月分批清空","confidence":"🟢 留最後"},
            ]
        },
        {
            "scenario": "🟢 核心永久持有（不變現）",
            "tickers": [
                {"ticker":"0050","name":"元大台灣50","price":107.6,"rationale":"+63% 壓艙石","size_suggest":"永久持有","confidence":"🟢 不賣"},
                {"ticker":"00631L","name":"台灣50正2","price":39.22,"rationale":"+38% =0050 2X","size_suggest":"永久持有","confidence":"🟢 不賣"},
                {"ticker":"2330","name":"台積電","price":2425,"rationale":"+13% AI 主軸","size_suggest":"永久持有","confidence":"🟢 不賣"},
            ]
        }
    ],

    # ===== allocation（陣列格式，非物件）=====
    "allocation": {
        "current": [
            {"label":"台股核心（0050+00631L+2330，永久）","value":73.5},
            {"label":"美股半導體（SMH×7）","value":17.8},
            {"label":"美股其他（7檔含槓桿ETF）","value":8.6},
            {"label":"現金","value":0.0},
        ],
        "target": [
            {"label":"台股核心（永久不動）","value":75},
            {"label":"美股部位（9-10 月分批變現）","value":0},
            {"label":"現金（10/31 到位）","value":25},
        ]
    },

    "consensus": [
        {"symbol":"SMH","name":"VanEck SMH（×7）","rating":"Buy","target":"$620-660 / 聚合 $572","date":"2026-06-03"},
        {"symbol":"NVDA","name":"NVIDIA（×1）","rating":"Strong Buy","target":"均值約 $310（79 位分析師）","date":"2026-06-03"},
        {"symbol":"HPQ","name":"HP Inc.（×20）","rating":"Reduce","target":"均值 $23（16 位）","date":"2026-06-03"},
        {"symbol":"2330.TW","name":"台積電（核心）","rating":"加碼","target":"NT$2,500-2,600","date":"2026-06-03"},
        {"symbol":"0050.TW","name":"元大台灣50","rating":"持有","target":"跟隨大盤","date":"2026-06-03"},
    ],

    "forecast": [
        {"symbol":"SMH","name":"VanEck SMH（×7）","bull":660,"base":640,"bear":580,"catalyst":"+40% 獲利；等 $650+；9 月變現"},
        {"symbol":"NVDA","name":"NVIDIA（×1）","bull":250,"base":220,"bear":200,"catalyst":"共識 $310；不攤平；反彈減碼"},
        {"symbol":"HPQ","name":"HP Inc.（×20）","bull":29,"base":27,"bear":24,"catalyst":"反彈成本區出清；Reduce 共識"},
        {"symbol":"CWVX","name":"2X 槓桿 ETF","bull":42,"base":38,"bear":30,"catalyst":"不攤平；時間衰減"},
        {"symbol":"2330.TW","name":"台積電（核心）","bull":2600,"base":2500,"bear":2300,"catalyst":"COMPUTEX；永久持有"},
        {"symbol":"0050.TW","name":"元大台灣50","bull":115,"base":110,"bear":102,"catalyst":"大盤壓艙石；永久持有"},
    ],

    # ===== capital_plan（含 status / sources / totals / options 結構）=====
    "capital_plan": {
        "title": "2026-06-04 美股 8 檔變現規劃（10/31 用錢）",
        "sources": [
            {"src":"美股 8 檔變現","amount_twd":207219,"amount_usd":6594,"status":"conditional","note":"槓桿 ETF 先出；SMH 留尾段；9-10 月分批現金化"},
        ],
        "totals": {
            "immediate": 0,
            "conditional": 207219,
            "total": 207219
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
