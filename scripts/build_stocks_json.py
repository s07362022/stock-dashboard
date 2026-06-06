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

FX = 31.475                                     # 匯率 USD→TWD（2026/06/06 券商參考）
UPDATE_NOTE = "2026/06/06 庫存以券商截圖為準（台股 5 + 美股 10）。核心 0050/00631L/2330 永久不賣；2317/2356 為台股衛星；美股 10 檔 3 個月可變現（10/31 需用錢）。6/5 非農+費半崩盤，台指期夜盤 -3006 點。"

CASH_ON_HAND = 0                                   # 無額外現金（資金在持倉中）
CASH_TO_DEPLOY = 0
CASH_NEED_DATE = "2026-10-31"                      # 十月底需用錢→美股4檔須於此前變現

# ---- 1.1 台股持倉（券商 2026/06/06 參考價）----
TW = [
    {"symbol":"0050.TW","name":"元大台灣50","shares":3210,"buy_price":65.93,"close":104.15,"change":-1.95,"pct":-1.84,"sector":"ETF（核心，永久持有）","tag":"core"},
    {"symbol":"00631L.TW","name":"元大台灣50正2","shares":5350,"buy_price":30.1,"close":36.67,"change":-1.63,"pct":-4.26,"sector":"ETF (=0050 2X，核心永久)","tag":"core","underlying":"0050","multiplier":2},
    {"symbol":"2330.TW","name":"台積電","shares":25,"buy_price":2145.6,"close":2365.0,"change":-20.0,"pct":-0.84,"sector":"半導體（核心永久）","tag":"core"},
    {"symbol":"2317.TW","name":"鴻海","shares":170,"buy_price":296.09,"close":284.5,"change":-8.5,"pct":-2.9,"sector":"代工／AI 伺服器","tag":"satellite"},
    {"symbol":"2356.TW","name":"英業達","shares":1000,"buy_price":71.7,"close":76.8,"change":0.0,"pct":0.0,"sector":"ODM／伺服器","tag":"satellite"},
]

# ---- 1.2 美股持倉（券商 2026/06/06 參考價；3 個月可變現）----
US = [
    {"symbol":"SMH","name":"VanEck Semiconductor ETF","shares":8,"buy_price":471.28,"close":569.69,"change":-57.84,"pct":-9.22,"sector":"半導體 ETF","tag":"satellite"},
    {"symbol":"HPQ","name":"HP Inc.","shares":27,"buy_price":28.31,"close":25.58,"change":-0.72,"pct":-2.74,"sector":"PC／硬體","tag":"satellite"},
    {"symbol":"ORCX","name":"Defiance 2X Long ORCL Daily","shares":10,"buy_price":61.1,"close":50.85,"change":-12.19,"pct":-19.34,"sector":"2X 槓桿 ETF","tag":"speculative"},
    {"symbol":"ASTS","name":"AST SpaceMobile","shares":4,"buy_price":105.255,"close":93.60,"change":-11.66,"pct":-11.07,"sector":"衛星通訊","tag":"speculative"},
    {"symbol":"NVDA","name":"NVIDIA Corporation","shares":1,"buy_price":234.59,"close":205.10,"change":-13.56,"pct":-6.2,"sector":"AI GPU","tag":"satellite"},
    {"symbol":"VSH","name":"Vishay Intertechnology","shares":5,"buy_price":62.55,"close":57.20,"change":-6.47,"pct":-10.16,"sector":"半導體元件","tag":"satellite"},
    {"symbol":"CWVX","name":"Tradr 2X Long CRWV Daily","shares":4,"buy_price":43.786,"close":27.74,"change":-4.74,"pct":-14.59,"sector":"2X 槓桿 ETF","tag":"speculative"},
    {"symbol":"DRAM","name":"Roundhill Memory ETF","shares":2,"buy_price":62.75,"close":55.79,"change":-6.96,"pct":-11.09,"sector":"記憶體 ETF","tag":"satellite"},
    {"symbol":"AMZN","name":"Amazon.com","shares":1,"buy_price":253.89,"close":246.03,"change":-7.86,"pct":-3.09,"sector":"雲端／電商","tag":"satellite"},
    {"symbol":"RKLB","name":"Rocket Lab USA","shares":1,"buy_price":114.17,"close":110.08,"change":-4.09,"pct":-3.58,"sector":"航太","tag":"speculative"},
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
        "philosophy": "2026/06/06：核心 0050/00631L/2330 永久持有；台股 2317/2356 衛星續抱；美股 10 檔因 10/31 需用錢。6/5 非農+費半崩盤→週一先出清槓桿 ETF、SMH 守 $580 停損。",
        "leverage_map": [
            {"etf":"00631L","underlying":"0050","multiplier":2,"treat_as":"long_term_core"},
            {"etf":"ORCX","underlying":"ORCL","multiplier":2,"treat_as":"liquidate_first"},
            {"etf":"CWVX","underlying":"CRWV","multiplier":2,"treat_as":"liquidate_first"},
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
            "highlight": "0050 +59%、00631L +22%、2330 +10%；2317/2356 衛星。核心不變現。",
            "verdict": "0050/00631L/2330 永久持有；2317/2356 週一不追空、不攤平。"
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
            "highlight": "SMH +21% 撐全組；其餘 9 檔合計虧損。CWVX/ORCX 槓桿深套。",
            "verdict": "週一優先出清 CWVX/ORCX；SMH 已破 $580 停損須減碼；9 月尾段變現。"
        }
    },

    "indices": [
        {"name":"S&P 500","code":"SPX","value":7383.74,"change":-200.57,"pct":-2.64},
        {"name":"NASDAQ","code":"IXIC","value":25709.43,"change":-1121.53,"pct":-4.18},
        {"name":"Dow Jones","code":"DJI","value":50866.78,"change":-695.15,"pct":-1.35},
        {"name":"費城半導體","code":"SOX","value":0,"change":0,"pct":-10.0},
        {"name":"SMH(費半ETF)","code":"SMH","value":569.69,"change":-57.84,"pct":-9.22},
        {"name":"VIX","code":"VIX","value":22.0,"change":6.0,"pct":37.5},
        {"name":"台股加權","code":"TWII","value":45070.94,"change":-606.52,"pct":-1.33},
        {"name":"台指期夜盤","code":"TXF","value":42220.0,"change":-3006.0,"pct":-6.65},
    ],

    "tw_stocks": TW,
    "us_stocks": US,

    "effective_exposure": [
        {"name":"0050＋00631L（核心永久）","icon":"🇹🇼","components":["0050×3210","00631L×5350"],"exposure_twd":530506,"pct_effective":56.3,"long_term":True},
        {"name":"台積電 2330（核心永久）","icon":"🏭","components":["2330 25股"],"exposure_twd":59125,"pct_effective":6.3,"long_term":True},
        {"name":"台股衛星（2317+2356）","icon":"🏭","components":["2317×170","2356×1000"],"exposure_twd":125165,"pct_effective":13.3,"long_term":False},
        {"name":"美股半導體（SMH×8）","icon":"🔌","components":["SMH ETF"],"exposure_twd":143462,"pct_effective":15.2,"long_term":False},
        {"name":"美股其他（9 檔）","icon":"🤖","components":["NVDA/HPQ/槓桿ETF/AMZN等"],"exposure_twd":83204,"pct_effective":8.8,"long_term":False},
    ],

    "underlying_analysis": [
        {
            "ticker":"SMH","name":"VanEck SMH（×8）","price":569.69,"today_pct":-9.22,"in_portfolio_twd":143462,
            "thesis":"費半超週期；+21% 仍獲利但已破停損 $580。",
            "pros":["AI 晶片長需求未變","仍大幅獲利"],
            "cons":["6/5 單日 -9%","已觸 $580 停損","10月需變現"],
            "consensus_target":"$620-660","rating":"Buy","next_catalyst":"6/16-17 FOMC","user_action":"🔴 週一減碼 50%；餘看 $600 站回"
        },
        {
            "ticker":"NVDA","name":"NVIDIA（×1）","price":205.10,"today_pct":-6.2,"in_portfolio_twd":6453,
            "thesis":"費半連動；與 SMH 重疊；不攤平。",
            "pros":["共識約 $306","AI 龍頭"],
            "cons":["-12.6% 虧損","與 SMH 雙重曝險"],
            "consensus_target":"均值 $306","rating":"Strong Buy","next_catalyst":"8/26 財報","user_action":"🟡 反彈 $210-220 減碼；跌破 $200 認賠"
        },
        {
            "ticker":"CWVX","name":"Tradr 2X CRWV（×4）","price":27.74,"today_pct":-14.59,"in_portfolio_twd":3492,
            "thesis":"日槓桿 ETF；-36.6%；週一優先出清。",
            "pros":["—"],
            "cons":["槓桿衰減","深套","崩盤日雙倍跌幅"],
            "consensus_target":"—","rating":"高風險","next_catalyst":"—","user_action":"🔴 週一開盤市價出清"
        },
        {
            "ticker":"ORCX","name":"Defiance 2X ORCL（×10）","price":50.85,"today_pct":-19.34,"in_portfolio_twd":16005,
            "thesis":"日槓桿 ETF；-16.8%；週一優先出清。",
            "pros":["ORCL 雲業務強"],
            "cons":["槓桿 ETF","6/5 單日 -19%"],
            "consensus_target":"—","rating":"高風險","next_catalyst":"—","user_action":"🔴 週一開盤市價出清"
        },
        {
            "ticker":"2330.TW","name":"台積電（×25）","price":2365,"today_pct":-0.84,"in_portfolio_twd":59125,
            "thesis":"核心永久；ADR 折價暗示週一再壓。",
            "pros":["AI 製造主軸","長線需求"],
            "cons":["週一 gap 風險","夜盤 ADR -6.7%"],
            "consensus_target":"NT$2,500-2,600","rating":"Strong Buy","next_catalyst":"7/16 法說","user_action":"🟢 永久持有；不 panic sell"
        },
        {
            "ticker":"HPQ","name":"HP Inc.（×27）","price":25.58,"today_pct":-2.74,"in_portfolio_twd":21749,
            "thesis":"PC 硬體；分析師 Reduce；-9.7%。",
            "pros":["股息","估值低"],
            "cons":["成長慢","弱勢"],
            "consensus_target":"$23（均值）","rating":"Reduce","next_catalyst":"9/1 財報","user_action":"🟡 不攤平；反彈 $28-29 減碼"
        },
    ],

    # ===== horizon_views（必須匹配渲染函式期望）=====
    "horizon_views": {
        "short_term_1m": {
            "title": "🔭 短線（~1 個月，6 月）情境 — 崩盤後修正",
            "intro": "6/5 非農 17.2 萬→升息預期升溫；費半 -10%、台指期夜盤 -3006 點。核心 0050/00631L/2330 永久不賣；週一 gap down 後觀察 4.2 萬支撐。美股先出槓桿 ETF、SMH 守紀律。",
            "tw_index": {
                "current": 45070.94,
                "bull": 44000, "p_bull": 25,
                "base": 42000, "p_base": 50,
                "bear": 40000, "p_bear": 25,
                "scenario": "週一 gap 至 4.2 萬（夜盤暗示）；基本：4.0-4.3 萬整理；空頭：融資斷頭+多殺多",
            },
            "forecasts": [
                {"symbol":"0050.TW","name":"元大台灣50","current":104.15,"bull":110,"base":102,"bear":95,"view":"核心永久；週一不追空"},
                {"symbol":"2330.TW","name":"台積電","current":2365,"bull":2500,"base":2300,"bear":2100,"view":"核心永久；ADR 折價後收斂"},
                {"symbol":"00631L.TW","name":"台灣50正2","current":36.67,"bull":40,"base":34,"bear":30,"view":"2X 波動；週一勿盲目加碼"},
                {"symbol":"SMH","name":"VanEck SMH（8股）","current":569.69,"bull":620,"base":560,"bear":500,"view":"+21% 仍賺；已破 $580→減碼 50%"},
                {"symbol":"NVDA","name":"NVIDIA（1股）","current":205.10,"bull":230,"base":210,"bear":185,"view":"-12.6%；反彈 $210-220 出"},
                {"symbol":"2317.TW","name":"鴻海","current":284.5,"bull":300,"base":275,"bear":250,"view":"-4%；週一跟跌不攤平"},
            ]
        },
        "long_term": {
            "title": "🏔️ 核心永久持有 vs 3 個月變現部位",
            "intro": "核心（0050/00631L/2330）永久不賣；2317/2356 台股衛星；美股 10 檔 10/31 前了結。",
            "core_long_term_buys": [
                {"symbol":"0050.TW","name":"元大台灣50","view":"永久壓艙石 +59%；不變現"},
                {"symbol":"00631L.TW","name":"台灣50正2","view":"永久持有 +22%；2X 波動大"},
                {"symbol":"2330.TW","name":"台積電","view":"AI 製造主軸 +10%；永久不賣"},
            ],
            "satellite_growth": [
                {"symbol":"SMH","name":"VanEck SMH","view":"3個月部位 +21%；9 月尾段了結"},
                {"symbol":"2317.TW","name":"鴻海","view":"台股衛星 -4%；不攤平"},
                {"symbol":"2356.TW","name":"英業達","view":"台股衛星 +7%；續抱"},
            ],
            "exit_or_reduce": [
                {"symbol":"CWVX","name":"2X 槓桿 ETF","view":"-36.6%；週一出清"},
                {"symbol":"ORCX","name":"2X ORCL","view":"-16.8%；週一出清"},
                {"symbol":"NVDA","name":"NVIDIA","view":"-12.6% 與 SMH 重疊；反彈先出"},
            ]
        },
        "peak_decision": {
            "title": "❓ 6/8 週一崩盤考驗 — 持有 / 了結？",
            "current_status": "2026/06/06：總市值約 NT$94.1 萬；台指期夜盤 42,220（-6.65%）；SMH 收 $569.69 已破 $580 停損。",
            "verdict": "核心不動；週一 A 級：出清 CWVX/ORCX → SMH 減半 → 其餘觀察。不逆勢攤平槓桿與融資股。",
            "actions": [
                {"type":"🟢 核心永久持有","items":[
                    "0050 / 00631L / 2330：週一 gap 不 panic sell",
                ]},
                {"type":"🔴 週一立即（A）","items":[
                    "CWVX×4、ORCX×10：開盤市價全出",
                    "SMH×8：減碼 50%（4 股）；餘 4 股停損 $550",
                ]},
                {"type":"🟡 週一觀察（B）","items":[
                    "NVDA：$210-220 反彈減碼；$200 以下認賠",
                    "2317/2356：不追空、不攤平",
                    "HPQ/ASTS/DRAM/VSH：小部位續抱",
                ]},
                {"type":"⚫ 變現紀律","items":[
                    "9/1 起 SMH 剩餘每週減 25-30%",
                    "10/25 前美股全清空",
                ]},
            ],
            "cash_target": "10/31 前美股 10 檔全數變現；核心台股不動。"
        },
        "tomorrow_tw_strategy": {
            "title": "📆 6/8（週一）台股＋美股操作計畫",
            "macro_context": [
                "📌 5月非農 +17.2 萬→12月升息機率 ~63%；10Y 美債 4.54%",
                "📌 費半 -10%+；NVDA -6.2%；SMH -9.22%（已破 $580）",
                "📌 台指期夜盤 42,220（-3006 點）；加權週五 45,071",
                "📌 博通 AI 指引未上調→AI 估值修正",
                "📌 融資逾 5,500 億→週一斷頭／多殺多風險",
                "📌 FOMC 6/16-17 為下個關鍵",
            ],
            "morning_plan": [
                {"step":1,"action":"09:00 開盤前","detail":"🔴 美股盤前：CWVX、ORCX 掛市價賣出（優先）"},
                {"step":2,"action":"09:00 開盤前","detail":"🔴 SMH 減半 4 股；餘 4 股停損 $550"},
                {"step":3,"action":"09:00-09:30 台股","detail":"🟢 0050/00631L/2330 不操作；觀察 gap 幅度"},
                {"step":4,"action":"09:30-10:00 台股","detail":"🟡 若加權守 42,000→不追空；破 41,500→2317/2356 不攤平"},
                {"step":5,"action":"10:00-13:30","detail":"🟡 NVDA 反彈 $210+ 減碼 1 股；HPQ $27+ 可減 1/3"},
                {"step":6,"action":"收盤後","detail":"📋 檢視融資／保證金；勿在恐慌日加槓桿"},
            ],
            "one_line": "週一：美股先砍槓桿 ETF + SMH 減半；台股核心不動、不追空不攤平，等 10 日線／4.2 萬止穩再評估。"
        }
    },

    "news": [
        {"date":"2026-06-06","category":"⚠️ 崩盤","title":"台指期夜盤 -3006 點（-6.65%）創史上最大跌點；盤中一度跌停","impact":"negative","source":"ETtoday / 聯合報"},
        {"date":"2026-06-05","category":"美股","title":"非農 +17.2 萬→12月升息機率 63%；納指 -4.18%、費半 -10%+","impact":"negative","source":"財聯社 / 新浪"},
        {"date":"2026-06-04","category":"美股","title":"博通 AI 指引 $160 億低於預期 $172 億；AI 估值修正開始","impact":"negative","source":"Reuters / 24/7 Wall St"},
        {"date":"2026-06-05","category":"台股","title":"加權 -606 點收 45,071；2330 2365（-20）；00631L -4.26%","impact":"negative","source":"BigGo / TVBS"},
        {"date":"2026-06-05","category":"地緣","title":"中東局勢推升油價 WTI ~$93；通膨隱憂升溫","impact":"negative","source":"Wagner / Bloomberg"},
        {"date":"2026-06-06","category":"策略","title":"融資逾 5,500 億+信貸槓桿；週一斷頭／多殺多風險","impact":"negative","source":"阮慕驊 / Yahoo"},
    ],

    "earnings": [
        {"ticker":"NVDA","name":"NVIDIA（×1）","period":"Q1 FY27","revenue":"$81.6B","eps":"$1.87","highlight":"共識 $306；8/26 下次財報","rating":"Strong Buy"},
        {"ticker":"SMH","name":"VanEck SMH（×8）","period":"ETF","revenue":"—","eps":"—","highlight":"+21% 仍獲利；已破 $580","rating":"Buy"},
        {"ticker":"HPQ","name":"HP Inc.（×27）","period":"Q2 FY26","revenue":"—","eps":"—","highlight":"9/1 財報；Reduce 共識","rating":"Reduce"},
        {"ticker":"2330.TW","name":"台積電（核心）","period":"Q1 2026","revenue":"+35%","eps":"NT$22.08","highlight":"7/16 法說；永久持有","rating":"Strong Buy"},
        {"ticker":"2317.TW","name":"鴻海（×170）","period":"Q2","revenue":"—","eps":"—","highlight":"AI 伺服器；週一跟跌","rating":"Buy"},
    ],

    "analysts": {
        "panel": ["巴菲特","芒格","Cathie Wood","Michael Burry","Peter Lynch","Ray Dalio","Druckenmiller","葛拉漢","索羅斯","科斯托蘭尼","Jim Simons","動能派","價值派","成長派","宏觀策略","風控長","產業專家","量化派","ESG"],
        "votes": [
            {"symbol":"2330.TW","name":"台積電（核心永久）","sell":0,"hold":5,"buy":14,"label":"AI 製造主軸"},
            {"symbol":"0050.TW","name":"元大台灣50（核心永久）","sell":0,"hold":7,"buy":12,"label":"大盤壓艙石"},
            {"symbol":"SMH","name":"VanEck SMH（×8）","sell":3,"hold":8,"buy":8,"label":"獲利豐但破停損"},
            {"symbol":"NVDA","name":"NVIDIA（×1）","sell":4,"hold":7,"buy":8,"label":"共識高、與SMH重疊"},
            {"symbol":"CWVX","name":"2X 槓桿 ETF 群","sell":15,"hold":3,"buy":1,"label":"週一出清"},
            {"symbol":"HPQ","name":"HP Inc.（×27）","sell":9,"hold":6,"buy":4,"label":"Reduce 居多"},
        ]
    },

    "picks": [
        {"rank":1,"ticker":"2330","name":"台積電（核心）","market":"TW","price":2365,"target_low":2500,"target_high":2600,"upside_pct":5.0,"thesis":"核心永久；週一不 panic sell","type":"核心永久"},
        {"rank":2,"ticker":"0050","name":"元大台灣50（核心）","market":"TW","price":104.15,"target_low":108,"target_high":112,"upside_pct":4.0,"thesis":"+59% 壓艙石","type":"核心永久"},
        {"rank":3,"ticker":"QCOM","name":"Qualcomm（觀察 ≤$300）","market":"US","price":229,"target_low":275,"target_high":300,"upside_pct":31.0,"thesis":"資料中心 AI；未持倉","type":"觀察"},
        {"rank":4,"ticker":"SMH","name":"VanEck SMH（×8）","market":"US","price":569.69,"target_low":600,"target_high":650,"upside_pct":5.0,"thesis":"+21%；減半後續抱","type":"減碼續抱"},
        {"rank":5,"ticker":"MU","name":"Micron（觀察）","market":"US","price":150,"target_low":170,"target_high":200,"upside_pct":15.0,"thesis":"記憶體；與 DRAM ETF 重疊","type":"觀察"},
    ],

    # ===== actions（A/B 用 strategy/stop/target；C 用 action/reason）=====
    "actions": {
        "A": [
            {"symbol":"0050","name":"元大台灣50（核心）","price":104.15,"target":"永久持有","stop":98,"strategy":"週一 gap 不 panic sell；永久不賣"},
            {"symbol":"2330","name":"台積電（核心）","price":2365,"target":"永久持有","stop":2200,"strategy":"核心不動；ADR 折價收斂前不加碼"},
        ],
        "B": [
            {"symbol":"SMH","name":"VanEck SMH（×8）","price":569.69,"target":"600-650（餘4股）","stop":550,"strategy":"週一減半 4 股；餘 4 股停損 $550；9 月尾段清空"},
            {"symbol":"NVDA","name":"NVIDIA（×1）","price":205.10,"target":"210-306（共識）","stop":200,"strategy":"反彈 $210-220 減碼；與 SMH 重疊"},
            {"symbol":"2356","name":"英業達（×1000）","price":76.8,"target":"80-85","stop":70,"strategy":"台股衛星 +7%；不攤平、不追空"},
        ],
        "C": [
            {"symbol":"CWVX","name":"Tradr 2X CRWV（×4）","price":27.74,"action":"週一開盤市價全出","reason":"-36.6% 槓桿 ETF；崩盤日雙倍跌幅"},
            {"symbol":"ORCX","name":"Defiance 2X ORCL（×10）","price":50.85,"action":"週一開盤市價全出","reason":"-16.8%；6/5 單日 -19%"},
            {"symbol":"ASTS","name":"AST SpaceMobile（×4）","price":93.60,"action":"不攤平；弱勢觀察","reason":"-11.1% 高波動"},
            {"symbol":"HPQ","name":"HP Inc.（×27）","price":25.58,"action":"不攤平；反彈減碼","reason":"-9.7%；Reduce 共識"},
            {"symbol":"2317","name":"鴻海（×170）","price":284.5,"action":"不攤平；週一不追空","reason":"-4.0%；跟跌不加碼"},
        ]
    },

    # ===== next_buy_recommendations（tickers 必須是物件陣列）=====
    "next_buy_recommendations": [
        {
            "scenario": "🔴 6/8 週一優先賣出（崩盤紀律）",
            "tickers": [
                {"ticker":"CWVX","name":"2X CRWV（×4）","price":27.74,"rationale":"-36.6% 槓桿深套","size_suggest":"開盤市價全出","confidence":"🔴 第一優先"},
                {"ticker":"ORCX","name":"2X ORCL（×10）","price":50.85,"rationale":"-16.8% 日槓桿","size_suggest":"開盤市價全出","confidence":"🔴 第一優先"},
                {"ticker":"SMH","name":"VanEck SMH（×8）","price":569.69,"rationale":"已破 $580 停損","size_suggest":"減半 4 股；餘停損 $550","confidence":"🔴 第二優先"},
                {"ticker":"NVDA","name":"NVIDIA（×1）","price":205.10,"rationale":"與 SMH 重疊","size_suggest":"$210-220 反彈出","confidence":"🟡 第三"},
            ]
        },
        {
            "scenario": "🟢 核心永久持有（週一不動）",
            "tickers": [
                {"ticker":"0050","name":"元大台灣50","price":104.15,"rationale":"+59% 壓艙石","size_suggest":"永久持有","confidence":"🟢 不賣"},
                {"ticker":"00631L","name":"台灣50正2","price":36.67,"rationale":"+22% =0050 2X","size_suggest":"永久持有","confidence":"🟢 不賣"},
                {"ticker":"2330","name":"台積電","price":2365,"rationale":"+10% AI 主軸","size_suggest":"永久持有","confidence":"🟢 不賣"},
            ]
        }
    ],

    # ===== allocation（陣列格式，非物件）=====
    "allocation": {
        "current": [
            {"label":"台股核心（0050+00631L+2330）","value":59.0},
            {"label":"台股衛星（2317+2356）","value":13.3},
            {"label":"美股半導體（SMH×8）","value":15.2},
            {"label":"美股其他（9 檔）","value":8.8},
            {"label":"現金","value":0.0},
        ],
        "target": [
            {"label":"台股核心（永久不動）","value":60},
            {"label":"台股衛星","value":10},
            {"label":"美股（9-10 月分批變現）","value":0},
            {"label":"現金（10/31 到位）","value":30},
        ]
    },

    "consensus": [
        {"symbol":"NVDA","name":"NVIDIA（×1）","rating":"Strong Buy","target":"均值約 $306（54 位）","date":"2026-06-05"},
        {"symbol":"SMH","name":"VanEck SMH（×8）","rating":"Buy","target":"$600-650","date":"2026-06-06"},
        {"symbol":"HPQ","name":"HP Inc.（×27）","rating":"Reduce","target":"均值 $23","date":"2026-06-05"},
        {"symbol":"2330.TW","name":"台積電（核心）","rating":"加碼","target":"NT$2,500-2,600","date":"2026-06-06"},
        {"symbol":"AVGO","name":"Broadcom","rating":"Buy the dip","target":"$525-580","date":"2026-06-05"},
    ],

    "forecast": [
        {"symbol":"SMH","name":"VanEck SMH（×8）","bull":620,"base":560,"bear":500,"catalyst":"減半後續抱；9 月變現"},
        {"symbol":"NVDA","name":"NVIDIA（×1）","bull":230,"base":210,"bear":185,"catalyst":"反彈減碼；8/26 財報"},
        {"symbol":"2330.TW","name":"台積電（核心）","bull":2500,"base":2300,"bear":2100,"catalyst":"永久持有；FOMC 6/17"},
        {"symbol":"0050.TW","name":"元大台灣50","bull":110,"base":102,"bear":95,"catalyst":"核心不動"},
        {"symbol":"CWVX","name":"2X 槓桿 ETF","bull":32,"base":28,"bear":22,"catalyst":"週一出清"},
        {"symbol":"TWII","name":"台股加權","bull":44000,"base":42000,"bear":40000,"catalyst":"夜盤 42220 暗示 gap"},
    ],

    # ===== capital_plan（含 status / sources / totals / options 結構）=====
    "capital_plan": {
        "title": "2026-06-08 週一崩盤應對 + 10/31 變現規劃",
        "sources": [
            {"src":"美股 10 檔變現","amount_twd":226662,"amount_usd":7201,"status":"conditional","note":"週一先出 CWVX/ORCX + SMH 減半；9-10 月分批現金化"},
        ],
        "totals": {
            "immediate": 0,
            "conditional": 226662,
            "total": 226662
        },
        "context": [
            "核心 0050/00631L/2330 永久持有，週一不 panic sell",
            "台指期夜盤 42,220→週一 gap down 預期",
            "SMH 已破 $580→紀律減半",
            "槓桿 ETF 週一無條件出清",
            "10/31 用錢硬約束不變",
        ],
        "options": [
            {
                "id": "A",
                "name": "週一紀律減碼（推薦 ⭐）",
                "philosophy": "出清槓桿→SMH 減半→核心不動→等止穩",
                "actions": [
                    {"step":1,"fund":"CWVX+ORCX","use":"開盤市價全出","rationale":"槓桿深套+時間衰減"},
                    {"step":2,"fund":"SMH×4","use":"減半賣出","rationale":"已破 $580 停損"},
                    {"step":3,"fund":"0050/00631L/2330","use":"不操作","rationale":"核心永久"},
                    {"step":4,"fund":"NVDA","use":"$210+ 反彈出","rationale":"與 SMH 重疊"},
                ],
                "result": {
                    "post_tw_pct": 76,
                    "post_us_pct": 10,
                    "post_cash_pct": 14,
                    "post_leveraged_pct": 0,
                    "summary": "週一降風險；保留 SMH 尾段與核心"
                }
            },
            {
                "id": "B",
                "name": "全面防禦（保守）",
                "philosophy": "週一美股全賣、台股衛星也減",
                "actions": [
                    {"step":1,"fund":"美股全 10 檔","use":"週一清空","rationale":"避開 FOMC 前波動"},
                    {"step":2,"fund":"2317/2356","use":"減碼 30%","rationale":"降低台股曝險"},
                ],
                "result": {
                    "post_tw_pct": 70,
                    "post_us_pct": 0,
                    "post_cash_pct": 30,
                    "post_leveraged_pct": 0,
                    "summary": "現金最大化；可能錯過反彈"
                }
            },
            {
                "id": "C",
                "name": "硬扛等反彈（不推薦）",
                "philosophy": "週一不賣、等 V 型反彈",
                "actions": [
                    {"step":1,"fund":"全部位續抱","use":"不操作","rationale":"賭週二反彈"},
                ],
                "result": {
                    "post_tw_pct": 76,
                    "post_us_pct": 24,
                    "post_cash_pct": 0,
                    "post_leveraged_pct": 5,
                    "summary": "槓桿 ETF 可能再 -20%；斷頭風險高"
                }
            }
        ],
        "recommendation": {
            "primary": "A",
            "reason": "週一出清 CWVX/ORCX + SMH 減半；核心不動；NVDA 反彈出。",
            "secondary_if_aggressive": "C"
        },
        "risks": [
            "台指期夜盤 -6.65%→週一 gap 可能超預期",
            "融資 5,500 億+→多殺多連鎖",
            "00631L 2X→週一跌幅可能 2 倍於 0050",
            "FOMC 6/16-17 前波動率偏高",
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
