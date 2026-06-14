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

FX = 31.475                                     # 匯率 USD→TWD（2026/06/12 參考）
UPDATE_NOTE = "2026/06/14 更新（資料以 6/12 收盤為準，台股 5 + 美股 8）。6/8 已執行：CWVX/ORCX 出清、SMH 減半至 4 股。核心 0050/00631L/2330 永久不賣；2317/2356 台股衛星；美股 8 檔 3 個月可變現（10/31 需用錢）。6/17 FOMC 為本週最大催化劑。"

CASH_ON_HAND = 0                                   # 無額外現金（資金在持倉中）
CASH_TO_DEPLOY = 0
CASH_NEED_DATE = "2026-10-31"                      # 十月底需用錢→美股須於此前變現

# ---- 1.1 台股持倉（2026/06/12 收盤價）----
TW = [
    {"symbol":"0050.TW","name":"元大台灣50","shares":3210,"buy_price":65.93,"close":101.95,"change":2.10,"pct":2.10,"sector":"ETF（核心，永久持有）","tag":"core"},
    {"symbol":"00631L.TW","name":"元大台灣50正2","shares":5350,"buy_price":30.1,"close":34.83,"change":1.60,"pct":4.81,"sector":"ETF (=0050 2X，核心永久)","tag":"core","underlying":"0050","multiplier":2},
    {"symbol":"2330.TW","name":"台積電","shares":25,"buy_price":2145.6,"close":2310.0,"change":60.0,"pct":2.67,"sector":"半導體（核心永久）","tag":"core"},
    {"symbol":"2317.TW","name":"鴻海","shares":170,"buy_price":296.09,"close":260.5,"change":2.00,"pct":0.77,"sector":"代工／AI 伺服器","tag":"satellite"},
    {"symbol":"2356.TW","name":"英業達","shares":1000,"buy_price":71.7,"close":68.0,"change":1.80,"pct":2.72,"sector":"ODM／伺服器","tag":"satellite"},
]

# ---- 1.2 美股持倉（2026/06/12 收盤價；6/8 已出清 CWVX/ORCX、SMH 減至 4 股）----
US = [
    {"symbol":"SMH","name":"VanEck Semiconductor ETF","shares":4,"buy_price":471.28,"close":619.50,"change":10.05,"pct":1.65,"sector":"半導體 ETF","tag":"satellite"},
    {"symbol":"HPQ","name":"HP Inc.","shares":27,"buy_price":28.31,"close":25.24,"change":0.24,"pct":0.96,"sector":"PC／硬體","tag":"satellite"},
    {"symbol":"ASTS","name":"AST SpaceMobile","shares":4,"buy_price":105.255,"close":87.75,"change":-4.75,"pct":-5.14,"sector":"衛星通訊","tag":"speculative"},
    {"symbol":"NVDA","name":"NVIDIA Corporation","shares":1,"buy_price":234.59,"close":204.87,"change":3.28,"pct":1.63,"sector":"AI GPU","tag":"satellite"},
    {"symbol":"VSH","name":"Vishay Intertechnology","shares":5,"buy_price":62.55,"close":59.38,"change":0.78,"pct":1.33,"sector":"半導體元件","tag":"satellite"},
    {"symbol":"DRAM","name":"Roundhill Memory ETF","shares":2,"buy_price":62.75,"close":65.01,"change":-0.11,"pct":-0.17,"sector":"記憶體 ETF","tag":"satellite"},
    {"symbol":"AMZN","name":"Amazon.com","shares":1,"buy_price":253.89,"close":238.55,"change":-2.95,"pct":-1.22,"sector":"雲端／電商","tag":"satellite"},
    {"symbol":"RKLB","name":"Rocket Lab USA","shares":1,"buy_price":114.17,"close":102.39,"change":-12.39,"pct":-10.79,"sector":"航太","tag":"speculative"},
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
        "philosophy": "2026/06/14：6/8 已執行 CWVX/ORCX 出清 + SMH 減半至 4 股。核心 0050/00631L/2330 永久持有；台股 2317/2356 衛星持守；美股 8 檔 10/31 前分批變現。本週核心風險：6/17 FOMC 新主席 Warsh 首次聲明，須靜待政策方向確認再評估。",
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
            "title": f"🇹🇼 台股（核心永久+衛星）{'+' if (tw_mv - tw_cost)>=0 else ''}{round(safe_pct(tw_mv - tw_cost, tw_cost),1)}%",
            "market_value_twd": tw_mv, "cost_twd": tw_cost,
            "pnl_twd": tw_mv - tw_cost,
            "pnl_pct": safe_pct(tw_mv - tw_cost, tw_cost),
            "winners": tw_w, "losers": tw_l,
            "highlight": "0050 +55%、00631L +16%、2330 +8%（核心）；2317 -12%、2356 -5%（衛星）。6/12 大盤回升+1019點。",
            "verdict": "0050/00631L/2330 永久持有；2317/2356 等 FOMC 後觀察，不攤平不追空。"
        },
        "us": {
            "title": f"🇺🇸 美股（3 個月可變現部位）{'+' if (us_mv_usd - us_cost_usd)>=0 else ''}{round(safe_pct(us_mv_usd - us_cost_usd, us_cost_usd),1)}%",
            "market_value_twd": us_mv_twd, "cost_twd": us_cost_twd,
            "pnl_twd": us_mv_twd - us_cost_twd,
            "pnl_pct": safe_pct(us_mv_twd - us_cost_twd, us_cost_usd),
            "market_value_usd": round(us_mv_usd, 2),
            "cost_usd": round(us_cost_usd, 2),
            "pnl_usd": round(us_mv_usd - us_cost_usd, 2),
            "winners": us_w, "losers": us_l,
            "highlight": "SMH(×4) +31% 撐全組；CWVX/ORCX 已出清（6/8 執行）；DRAM/VSH 小正；RKLB 6/12 崩 -11%。",
            "verdict": "FOMC 6/17 前觀望；NVDA 反彈 $210-220 可考慮減碼；ASTS/RKLB 小部位續抱不攤平。"
        }
    },

    "indices": [
        {"name":"S&P 500","code":"SPX","value":7438.0,"change":58.0,"pct":0.78},
        {"name":"NASDAQ","code":"IXIC","value":25980.0,"change":180.0,"pct":0.70},
        {"name":"Dow Jones","code":"DJI","value":51200.0,"change":350.0,"pct":0.69},
        {"name":"費城半導體","code":"SOX","value":6820.0,"change":285.0,"pct":4.36},
        {"name":"SMH(費半ETF)","code":"SMH","value":619.50,"change":10.05,"pct":1.65},
        {"name":"VIX","code":"VIX","value":17.8,"change":-2.1,"pct":-10.55},
        {"name":"台股加權","code":"TWII","value":44169.04,"change":1019.58,"pct":2.36},
        {"name":"台指期","code":"TXF","value":44150.0,"change":980.0,"pct":2.27},
    ],

    "tw_stocks": TW,
    "us_stocks": US,

    "effective_exposure": [
        {"name":"0050＋00631L（核心永久）","icon":"🇹🇼","components":["0050×3210","00631L×5350"],"exposure_twd":513601,"pct_effective":62.3,"long_term":True},
        {"name":"台積電 2330（核心永久）","icon":"🏭","components":["2330 25股"],"exposure_twd":57750,"pct_effective":7.0,"long_term":True},
        {"name":"台股衛星（2317+2356）","icon":"🏭","components":["2317×170","2356×1000"],"exposure_twd":112285,"pct_effective":13.6,"long_term":False},
        {"name":"美股半導體（SMH×4）","icon":"🔌","components":["SMH ETF 已減半"],"exposure_twd":77994,"pct_effective":9.5,"long_term":False},
        {"name":"美股其他（7 檔）","icon":"🤖","components":["NVDA/HPQ/ASTS/VSH/DRAM/AMZN/RKLB"],"exposure_twd":63112,"pct_effective":7.7,"long_term":False},
    ],

    "underlying_analysis": [
        {
            "ticker":"SMH","name":"VanEck SMH（×4，已減半）","price":619.50,"today_pct":1.65,"in_portfolio_twd":77994,
            "thesis":"費半技術性反彈 +4.3%（週）；6/8 已減半至 4 股，持倉成本 $471.28，現 +31%。",
            "pros":["AI 晶片需求未見頂","半導體出貨 YoY +106%","持倉仍大幅獲利"],
            "cons":["FOMC 6/17 前波動率偏高","大型科技估值承壓","10月需變現"],
            "consensus_target":"$630-680","rating":"Buy","next_catalyst":"6/17 FOMC / 6/24 NVDA 股東大會","user_action":"🟡 守 $600 繼續持有；9 月起分批出清；跌破 $580 停損"
        },
        {
            "ticker":"NVDA","name":"NVIDIA（×1）","price":204.87,"today_pct":1.63,"in_portfolio_twd":6447,
            "thesis":"AI GPU 龍頭；與 SMH 曝險重疊；-12.7% 虧損。6/24 股東大會是近期催化劑。",
            "pros":["共識目標 $280-306","AI Capex 超週期","6/24 股東大會"],
            "cons":["-12.7% 虧損","與 SMH 雙重 GPU 曝險","MAGS 週跌 -2.4%"],
            "consensus_target":"均值 ~$290","rating":"Strong Buy","next_catalyst":"6/24 股東大會 / 8/26 財報","user_action":"🟡 反彈 $210-220 減碼；守 $200；6/24 前勿貿然動作"
        },
        {
            "ticker":"RKLB","name":"Rocket Lab（×1）","price":102.39,"today_pct":-10.79,"in_portfolio_twd":3223,
            "thesis":"6/12 Blue Origin 爆炸拖累 -11%；-10.3% 虧損。小部位續持。",
            "pros":["太空防務長期成長","前期飆漲 +400%","SDA 大單"],
            "cons":["6/12 單日 -10.79%","高波動","與大盤連動高"],
            "consensus_target":"$130-160","rating":"Buy","next_catalyst":"季報","user_action":"🟡 小部位不攤平；反彈至 $115 可減碼"
        },
        {
            "ticker":"2330.TW","name":"台積電（×25，核心永久）","price":2310,"today_pct":2.67,"in_portfolio_twd":57750,
            "thesis":"核心永久；6/12 +2.67% 回升；2nm 良率超前；AI/HPC 訂單能見度至 2027。",
            "pros":["AI 製造主軸","毛利率創高","高盛目標 NT$3000"],
            "cons":["估值 31x 偏高","中東油價通膨","FOMC 前短線波動"],
            "consensus_target":"NT$2,800-3,000","rating":"Strong Buy","next_catalyst":"7/16 法說會","user_action":"🟢 永久持有，不操作"
        },
        {
            "ticker":"ASTS","name":"AST SpaceMobile（×4）","price":87.75,"today_pct":-5.14,"in_portfolio_twd":11048,
            "thesis":"低軌衛星通訊；-16.6% 虧損；6/12 受 RKLB/Blue Origin 事件拖累。",
            "pros":["低軌衛星長期需求","SpaceX IPO 帶動題材"],
            "cons":["-16.6% 高波動","資本耗損未盈利","相關性高於預期"],
            "consensus_target":"$100-130","rating":"Speculative Buy","next_catalyst":"財報","user_action":"🔴 不攤平；弱勢持續可考慮停損"
        },
        {
            "ticker":"HPQ","name":"HP Inc.（×27）","price":25.24,"today_pct":0.96,"in_portfolio_twd":21449,
            "thesis":"PC 硬體；分析師 Reduce；-10.8%。AI PC 需求待確認。",
            "pros":["AI PC 換機週期","低估值","股息"],
            "cons":["分析師 Reduce 共識","成長動能弱","AI 替代風險"],
            "consensus_target":"$23（均值）","rating":"Reduce","next_catalyst":"9/1 財報","user_action":"🟡 不攤平；反彈 $28+ 考慮減碼"
        },
    ],

    # ===== horizon_views（必須匹配渲染函式期望）=====
    "horizon_views": {
        "short_term_1m": {
            "title": "🔭 短線（6 月中下旬）— FOMC 前觀望，等方向確認",
            "intro": "6/8 已完成紀律操作（CWVX/ORCX 出清，SMH 減半）。6/12 大盤技術反彈：台股 +1019 點、SMH +1.65%，但 MAGS -2.4%、RKLB -11%。本週核心焦點：6/17 FOMC 新主席 Warsh 首次政策聲明，確認前不宜加碼。",
            "tw_index": {
                "current": 44169.04,
                "bull": 46000, "p_bull": 30,
                "base": 43500, "p_base": 50,
                "bear": 41000, "p_bear": 20,
                "scenario": "FOMC 鴿派→挑戰 4.6 萬；鷹派/意外升息→跌回 4.1 萬；基本：FOMC 維持不動、觀望至 6/26 羅素重構",
            },
            "forecasts": [
                {"symbol":"0050.TW","name":"元大台灣50","current":101.95,"bull":108,"base":104,"bear":97,"view":"核心永久；FOMC 後等方向再判斷"},
                {"symbol":"2330.TW","name":"台積電","current":2310,"bull":2600,"base":2350,"bear":2100,"view":"核心永久；7/16 法說為下一催化劑"},
                {"symbol":"00631L.TW","name":"台灣50正2","current":34.83,"bull":38,"base":35,"bear":31,"view":"2X 波動；FOMC 前不加碼"},
                {"symbol":"SMH","name":"VanEck SMH（4股）","current":619.50,"bull":680,"base":630,"bear":560,"view":"+31% 仍獲利；守 $600；9月起尾段出清"},
                {"symbol":"NVDA","name":"NVIDIA（1股）","current":204.87,"bull":240,"base":215,"bear":190,"view":"-12.7%；6/24 股東大會催化；反彈 $210+ 可減"},
                {"symbol":"2317.TW","name":"鴻海","current":260.5,"bull":280,"base":265,"bear":240,"view":"-12%；等 AI 伺服器訂單確認再評估"},
            ]
        },
        "long_term": {
            "title": "🏔️ 核心永久持有 vs 3 個月變現部位",
            "intro": "核心（0050/00631L/2330）永久不賣；2317/2356 台股衛星觀察；美股 8 檔 10/31 前分批變現。CWVX/ORCX 已 6/8 出清。",
            "core_long_term_buys": [
                {"symbol":"0050.TW","name":"元大台灣50","view":"永久壓艙石 +55%；不變現"},
                {"symbol":"00631L.TW","name":"台灣50正2","view":"永久持有 +16%；2X 波動"},
                {"symbol":"2330.TW","name":"台積電","view":"AI 製造主軸 +8%；永久不賣"},
            ],
            "satellite_growth": [
                {"symbol":"SMH","name":"VanEck SMH（×4）","view":"3個月部位 +31%；9 月起尾段了結"},
                {"symbol":"DRAM","name":"Roundhill Memory ETF","view":"記憶體 +3.6%；小部位續抱"},
                {"symbol":"VSH","name":"Vishay Intertechnology","view":"-5.1%；小部位等底部"},
            ],
            "exit_or_reduce": [
                {"symbol":"ASTS","name":"AST SpaceMobile","view":"-16.6% 高波動；不攤平；弱勢可停損"},
                {"symbol":"NVDA","name":"NVIDIA","view":"-12.7%；6/24 前觀察；反彈 $210+ 出"},
                {"symbol":"RKLB","name":"Rocket Lab","view":"-10.3%；6/12 Blue Origin 事件拖累；小部位"},
            ]
        },
        "peak_decision": {
            "title": "✅ 6/8 已執行 → 6/17 FOMC 為下一決策點",
            "current_status": "2026/06/14：6/8 紀律操作完成（CWVX/ORCX 出清、SMH 減半至 4 股）。總市值約 NT$82.5 萬，台股占 83%，美股占 17%。6/12 大盤技術反彈，但本週 FOMC 前不宜重倉追高。",
            "verdict": "6/8 已出清槓桿 ETF，風險顯著降低。6/17 FOMC 前觀望；Warsh 鴿派表態→可逢低加碼 SMH/NVDA；鷹派→持守等修正。核心台股不動。",
            "actions": [
                {"type":"🟢 核心永久持有（不動）","items":[
                    "0050 / 00631L / 2330：FOMC 前後均不操作",
                ]},
                {"type":"✅ 已完成（6/8）","items":[
                    "CWVX×4、ORCX×10：已出清 ✓",
                    "SMH：已從 8 股減半至 4 股 ✓",
                ]},
                {"type":"🟡 本週觀察（FOMC 前）","items":[
                    "NVDA：6/24 股東大會前不急出；守 $200 支撐",
                    "2317/2356：等台股方向確認，不攤平不追空",
                    "ASTS/RKLB：小部位續持，無力道續弱可停損",
                ]},
                {"type":"⚫ 變現紀律（不變）","items":[
                    "9/1 起 SMH 剩餘每週減 25-30%",
                    "10/25 前美股全清空（10/31 需用錢）",
                ]},
            ],
            "cash_target": "10/31 前美股 8 檔全數變現；核心台股永久不動。"
        },
        "tomorrow_tw_strategy": {
            "title": "📆 6/16（週一）— FOMC 前操作計畫",
            "macro_context": [
                "📌 6/17 FOMC 利率決議：新主席 Warsh 首次聲明，維持 3.75% 為基本預期",
                "📌 6/12 台股大漲 +1019 點（+2.36%）收 44,169；SMH +1.65% 收 $619.5",
                "📌 SpaceX IPO 虹吸效應消化中；6/12 Blue Origin 爆炸拖累 RKLB/ASTS",
                "📌 MAGS（七大科技）週跌 -2.4%；小型股 IWM 週漲 +3.1%",
                "📌 美國 5 月 CPI 4.2%（整體偏高，但核心環比 0.2% 回落）",
                "📌 6/19 美股休市（Juneteenth）；6/24 NVDA 股東大會 + 美光財報",
            ],
            "morning_plan": [
                {"step":1,"action":"09:00 開盤","detail":"🟢 台股核心（0050/00631L/2330）不操作；觀察 FOMC 前情緒"},
                {"step":2,"action":"09:00-09:30","detail":"🟡 加權若延續昨日強勢站上 44,500→觀望；跌破 43,500→確認不攤平"},
                {"step":3,"action":"09:30-10:30","detail":"🟡 2317/2356 衛星：昨漲後若今回測→不追空；反彈未過前高→不加碼"},
                {"step":4,"action":"美股盤前（台灣晚間）","detail":"🟡 等待 FOMC 聲明（6/17 18:00 GMT = 台灣 6/18 凌晨 2:00）"},
                {"step":5,"action":"FOMC 後評估","detail":"🟡 Warsh 鴿派→SMH 可持守至 $640+；鷹派→考慮再減碼 NVDA"},
                {"step":6,"action":"本週重點","detail":"⚫ 6/19 美股休市；6/24 NVDA 股東大會前不輕易動作"},
            ],
            "watch_list_for_tomorrow": [
                {"symbol":"SMH","name":"VanEck SMH","buy_zone":"600-610","target":"640-680","action":"持守；跌破 $590 減碼"},
                {"symbol":"2330","name":"台積電","buy_zone":"2250-2280","target":"2500+","action":"永久持有；逢低不追空"},
                {"symbol":"NVDA","name":"NVIDIA","buy_zone":"200-205","target":"215-220","action":"守 $200 止損；反彈可減"},
            ],
            "avoid_list": [
                {"symbol":"ASTS","name":"AST SpaceMobile","reason":"高波動+Blue Origin 事件後走弱；不追空不攤平"},
                {"symbol":"RKLB","name":"Rocket Lab","reason":"6/12 崩 -11%；情緒未穩前勿加碼"},
            ],
            "risk_alerts": [
                "⚠️ FOMC 6/17 Warsh 意外鷹派→美股短線下殺，台股連動",
                "⚠️ 6/24 羅素 2000 重構：小型股流動性衝擊",
                "⚠️ 6/24 美光財報：記憶體產業景氣確認窗口",
                "⚠️ 中東局勢：油價 WTI $85+，通膨壓力未退",
            ],
            "one_line": "6/16 台股 FOMC 前觀望：核心不動、衛星守位；美股靜待 6/17 Warsh 首次聲明方向確認再動作。"
        }
    },

    "news": [
        {"date":"2026-06-17","category":"🏦 FOMC","title":"聯準會 FOMC 決議：新主席 Warsh 首次聲明（維持 3.75% 預期）","impact":"neutral","source":"FX Empire / 新浪財經"},
        {"date":"2026-06-12","category":"🚀 SpaceX","title":"Blue Origin 火箭爆炸→RKLB -11%、ASTS 急跌；航太類股承壓","impact":"negative","source":"Perplexity Finance"},
        {"date":"2026-06-12","category":"台股","title":"台股大漲 +1019 點收 44,169；台積電 +2.67% 收 2310；費半 ETF 反彈","impact":"positive","source":"PChome / Yahoo股市"},
        {"date":"2026-06-12","category":"美股","title":"SpaceX IPO 虹吸效應消退；SMH +1.65%；MAGS -2.4%；小型股 IWM +3.1%","impact":"mixed","source":"Vocus 市場週期觀察"},
        {"date":"2026-06-10","category":"📊 數據","title":"美國 5 月 CPI 4.2%（整體偏高）；核心 CPI 環比 0.2%（回落）","impact":"mixed","source":"新浪財經 / 惠譽評級"},
        {"date":"2026-06-08","category":"✅ 執行","title":"6/8 紀律操作：CWVX/ORCX 已出清；SMH 已減半至 4 股","impact":"positive","source":"Portfolio 紀錄"},
        {"date":"2026-06-08","category":"台股","title":"英業達 5 月營收 5月 66億元，前5月 AI 伺服器訂單飽滿","impact":"positive","source":"Yahoo股市 / 鉅亨"},
        {"date":"2026-06-06","category":"⚠️ 事件","title":"台指期夜盤 -3006 點（-6.65%）；費半 -10%；費半 YoY +106%（4月史上新高）","impact":"negative","source":"ETtoday"},
    ],

    "earnings": [
        {"ticker":"NVDA","name":"NVIDIA（×1）","period":"Q1 FY27","revenue":"$44.1B","eps":"$0.96","highlight":"6/24 股東大會；8/26 Q2 財報；共識 $290","rating":"Strong Buy"},
        {"ticker":"SMH","name":"VanEck SMH（×4）","period":"ETF","revenue":"—","eps":"—","highlight":"+31% 仍獲利；9月起尾段出清","rating":"Buy"},
        {"ticker":"HPQ","name":"HP Inc.（×27）","period":"Q2 FY26","revenue":"$13.5B","eps":"—","highlight":"9/1 財報；AI PC 待確認；Reduce 共識","rating":"Reduce"},
        {"ticker":"2330.TW","name":"台積電（核心）","period":"Q1 2026","revenue":"+35%","eps":"NT$22.08","highlight":"7/16 法說；毛利率創高；2nm 良率超前","rating":"Strong Buy"},
        {"ticker":"2356.TW","name":"英業達（×1000）","period":"5月營收","revenue":"66億","eps":"—","highlight":"前5月 AI 伺服器滿手訂單；股價自高峰修正 20%","rating":"Buy"},
        {"ticker":"DRAM","name":"Roundhill Memory ETF（×2）","period":"ETF","revenue":"—","eps":"—","highlight":"6/24 美光財報為記憶體確認窗口；+3.6%","rating":"Speculative Buy"},
    ],

    "analysts": {
        "panel": ["巴菲特","芒格","Cathie Wood","Michael Burry","Peter Lynch","Ray Dalio","Druckenmiller","葛拉漢","索羅斯","科斯托蘭尼","Jim Simons","動能派","價值派","成長派","宏觀策略","風控長","產業專家","量化派","ESG"],
        "votes": [
            {"symbol":"2330.TW","name":"台積電（核心永久）","sell":0,"hold":4,"buy":15,"label":"AI 製造主軸；7/16 法說"},
            {"symbol":"0050.TW","name":"元大台灣50（核心永久）","sell":0,"hold":6,"buy":13,"label":"大盤壓艙石 +55%"},
            {"symbol":"SMH","name":"VanEck SMH（×4，已減半）","sell":2,"hold":8,"buy":9,"label":"獲利 +31%；FOMC 前觀望"},
            {"symbol":"NVDA","name":"NVIDIA（×1）","sell":3,"hold":6,"buy":10,"label":"6/24 股東大會催化劑"},
            {"symbol":"ASTS","name":"AST SpaceMobile（×4）","sell":8,"hold":7,"buy":4,"label":"高波動；Blue Origin 事件"},
            {"symbol":"HPQ","name":"HP Inc.（×27）","sell":9,"hold":6,"buy":4,"label":"AI PC 待確認；Reduce"},
        ]
    },

    "picks": [
        {"rank":1,"ticker":"2330","name":"台積電（核心）","market":"TW","price":2310,"target_low":2500,"target_high":2800,"upside_pct":10.8,"thesis":"核心永久；7/16 法說；AI/HPC 訂單至 2027","type":"核心永久"},
        {"rank":2,"ticker":"0050","name":"元大台灣50（核心）","market":"TW","price":101.95,"target_low":106,"target_high":112,"upside_pct":6.0,"thesis":"+55% 壓艙石；台股長線多頭","type":"核心永久"},
        {"rank":3,"ticker":"SMH","name":"VanEck SMH（×4）","market":"US","price":619.50,"target_low":650,"target_high":700,"upside_pct":7.3,"thesis":"+31%；FOMC 後方向確認再評估","type":"FOMC 後觀察"},
        {"rank":4,"ticker":"NVDA","name":"NVIDIA（×1）","market":"US","price":204.87,"target_low":220,"target_high":290,"upside_pct":17.6,"thesis":"6/24 股東大會催化劑；AI GPU 長線需求","type":"持守觀察"},
        {"rank":5,"ticker":"MU","name":"Micron（觀察）","market":"US","price":145,"target_low":170,"target_high":210,"upside_pct":20.7,"thesis":"6/24 財報確認記憶體景氣；與 DRAM ETF 重疊","type":"觀察"},
    ],

    # ===== actions（A/B 用 strategy/stop/target；C 用 action/reason）=====
    "actions": {
        "A": [
            {"symbol":"0050","name":"元大台灣50（核心）","price":101.95,"target":"永久持有","stop":95,"strategy":"FOMC 前後均不操作；永久壓艙石"},
            {"symbol":"2330","name":"台積電（核心）","price":2310,"target":"永久持有","stop":2100,"strategy":"核心不動；7/16 法說前持守"},
            {"symbol":"00631L","name":"台灣50正2（核心）","price":34.83,"target":"永久持有","stop":30,"strategy":"2X 核心；FOMC 前不加碼"},
        ],
        "B": [
            {"symbol":"SMH","name":"VanEck SMH（×4，已減半）","price":619.50,"target":"650-700","stop":590,"strategy":"守 $600 支撐；FOMC 鴿派→持守；9 月起尾段出清"},
            {"symbol":"NVDA","name":"NVIDIA（×1）","price":204.87,"target":"210-290（6/24 催化）","stop":195,"strategy":"6/24 股東大會前觀望；反彈 $215+ 可考慮減碼"},
            {"symbol":"2356","name":"英業達（×1000）","price":68.0,"target":"72-80","stop":62,"strategy":"台股衛星 -5%；等 AI 伺服器旺季訂單確認再加碼"},
        ],
        "C": [
            {"symbol":"ASTS","name":"AST SpaceMobile（×4）","price":87.75,"action":"不攤平；弱勢持續考慮停損","reason":"-16.6% 高波動；Blue Origin 事件後航太板塊情緒弱"},
            {"symbol":"RKLB","name":"Rocket Lab（×1）","price":102.39,"action":"小部位不追空；反彈 $115 考慮減碼","reason":"-10.3%；6/12 爆跌 -11%；高波動"},
            {"symbol":"HPQ","name":"HP Inc.（×27）","price":25.24,"action":"不攤平；反彈 $28+ 考慮減碼","reason":"-10.8%；Reduce 共識；AI PC 待確認"},
            {"symbol":"2317","name":"鴻海（×170）","price":260.5,"action":"不攤平；等 AI 伺服器訂單確認","reason":"-12%；AI 伺服器相關但短線估值壓力"},
        ]
    },

    # ===== next_buy_recommendations（tickers 必須是物件陣列）=====
    "next_buy_recommendations": [
        {
            "scenario": "🟡 6/17 FOMC 後觀察（鴿派確認再布局）",
            "tickers": [
                {"ticker":"SMH","name":"VanEck SMH（×4）","price":619.50,"rationale":"FOMC 鴿派→可守至 $650+；跌破 $590 停損","size_suggest":"現有 4 股持守；不加碼","confidence":"🟡 FOMC 後確認"},
                {"ticker":"NVDA","name":"NVIDIA（×1）","price":204.87,"rationale":"6/24 股東大會前靜待；鴿派後可加至 2 股","size_suggest":"守 $195-200 支撐","confidence":"🟡 6/24 前觀望"},
                {"ticker":"DRAM","name":"Roundhill Memory ETF（×2）","price":65.01,"rationale":"6/24 美光財報確認記憶體景氣；可酌增","size_suggest":"最多+1股","confidence":"🟢 景氣確認後"},
            ]
        },
        {
            "scenario": "🟢 核心永久持有（持守不動）",
            "tickers": [
                {"ticker":"0050","name":"元大台灣50","price":101.95,"rationale":"+55% 壓艙石；FOMC 前後不動","size_suggest":"永久持有 3,210 股","confidence":"🟢 不賣"},
                {"ticker":"00631L","name":"台灣50正2","price":34.83,"rationale":"+16% =0050 2X；永久核心","size_suggest":"永久持有 5,350 股","confidence":"🟢 不賣"},
                {"ticker":"2330","name":"台積電","price":2310,"rationale":"+8% AI 主軸；7/16 法說催化","size_suggest":"永久持有 25 股","confidence":"🟢 不賣"},
            ]
        },
        {
            "scenario": "⚫ 10/31 前變現紀律（不變）",
            "tickers": [
                {"ticker":"SMH","name":"VanEck SMH（×4）","price":619.50,"rationale":"9/1 起每週減 25-30%；10/25 前全出","size_suggest":"9月起分批","confidence":"⚫ 硬約束"},
                {"ticker":"NVDA+HPQ+ASTS","name":"其他美股 7 檔","price":0,"rationale":"FOMC 後評估減碼時機；10/25 前全清","size_suggest":"7-10 月分批","confidence":"⚫ 硬約束"},
            ]
        }
    ],

    # ===== allocation（陣列格式，非物件）=====
    "allocation": {
        "current": [
            {"label":"台股核心（0050+00631L+2330）","value":69.3},
            {"label":"台股衛星（2317+2356）","value":13.6},
            {"label":"美股半導體（SMH×4）","value":9.5},
            {"label":"美股其他（7 檔）","value":7.7},
            {"label":"現金","value":0.0},
        ],
        "target": [
            {"label":"台股核心（永久不動）","value":75},
            {"label":"台股衛星","value":10},
            {"label":"美股（7-10 月分批變現）","value":0},
            {"label":"現金（10/31 到位）","value":15},
        ]
    },

    "consensus": [
        {"symbol":"NVDA","name":"NVIDIA（×1）","rating":"Strong Buy","target":"均值約 $290（分析師）","date":"2026-06-12"},
        {"symbol":"SMH","name":"VanEck SMH（×4）","rating":"Buy","target":"$630-680","date":"2026-06-12"},
        {"symbol":"HPQ","name":"HP Inc.（×27）","rating":"Reduce","target":"均值 $23-24","date":"2026-06-12"},
        {"symbol":"2330.TW","name":"台積電（核心）","rating":"加碼","target":"NT$2,800-3,000（高盛）","date":"2026-06-12"},
        {"symbol":"VSH","name":"Vishay Intertechnology（×5）","rating":"Sell（2 分析師）","target":"$24（保守目標）","date":"2026-06-12"},
        {"symbol":"RKLB","name":"Rocket Lab（×1）","rating":"Buy","target":"$130-160","date":"2026-06-12"},
    ],

    "forecast": [
        {"symbol":"SMH","name":"VanEck SMH（×4）","bull":700,"base":640,"bear":560,"catalyst":"FOMC 鴿派→挑戰 $700；鷹派→修正至 $560"},
        {"symbol":"NVDA","name":"NVIDIA（×1）","bull":250,"base":215,"bear":190,"catalyst":"6/24 股東大會；8/26 Q2 財報"},
        {"symbol":"2330.TW","name":"台積電（核心）","bull":2800,"base":2400,"bear":2100,"catalyst":"永久持有；7/16 法說；2nm 良率"},
        {"symbol":"0050.TW","name":"元大台灣50","bull":110,"base":104,"bear":96,"catalyst":"核心不動；FOMC + 羅素重構 6/26"},
        {"symbol":"ASTS","name":"AST SpaceMobile（×4）","bull":100,"base":88,"bear":70,"catalyst":"衛星訂單確認；高波動"},
        {"symbol":"TWII","name":"台股加權","bull":46000,"base":43500,"bear":41000,"catalyst":"FOMC 後方向；6/26 羅素重構"},
    ],

    # ===== capital_plan（含 status / sources / totals / options 結構）=====
    "capital_plan": {
        "title": "2026/06/14 — 6/8 已執行，FOMC 後評估 + 10/31 變現規劃",
        "sources": [
            {"src":"美股 8 檔（6/8 已出清槓桿 ETF）","amount_twd":141106,"amount_usd":4483,"status":"conditional","note":"SMH×4（9月起出清）+ HPQ/ASTS/NVDA/VSH/DRAM/AMZN/RKLB（7-10月分批）"},
        ],
        "totals": {
            "immediate": 0,
            "conditional": 141106,
            "total": 141106
        },
        "context": [
            "✅ 6/8 已完成：CWVX/ORCX 出清；SMH 減半至 4 股",
            "核心 0050/00631L/2330 永久持有，不參與任何變現",
            "6/17 FOMC 新主席 Warsh 首次聲明：維持/鴿派→美股可繼續持守",
            "鷹派/意外升息→加速 7-8 月美股減碼",
            "10/31 用錢硬約束不變，9/1 起啟動 SMH 分批出清",
        ],
        "options": [
            {
                "id": "A",
                "name": "FOMC 後靜待確認（推薦 ⭐）",
                "philosophy": "等 6/17 Warsh 表態→鴿派持守；9月起紀律出清",
                "actions": [
                    {"step":1,"fund":"6/17 FOMC 聲明","use":"觀察 Warsh 政策方向","rationale":"新主席首次表態是最大不確定性"},
                    {"step":2,"fund":"SMH×4","use":"鴿派→守 $600；鷹派→考慮再減 2 股","rationale":"依 FOMC 結果調整"},
                    {"step":3,"fund":"0050/00631L/2330","use":"不操作","rationale":"核心永久"},
                    {"step":4,"fund":"7-10月","use":"美股 8 檔分批變現","rationale":"10/31 硬約束"},
                ],
                "result": {
                    "post_tw_pct": 83,
                    "post_us_pct": 17,
                    "post_cash_pct": 0,
                    "post_leveraged_pct": 0,
                    "summary": "FOMC 後確認方向再動作；維持台股主體地位"
                }
            },
            {
                "id": "B",
                "name": "提前減碼（保守）",
                "philosophy": "6/16 美股先減半，不等 FOMC 結果",
                "actions": [
                    {"step":1,"fund":"SMH 再減 2 股","use":"6/16 賣出→剩 2 股","rationale":"FOMC 前降低波動風險"},
                    {"step":2,"fund":"NVDA×1","use":"6/16 市價出","rationale":"與 SMH 重疊"},
                ],
                "result": {
                    "post_tw_pct": 88,
                    "post_us_pct": 7,
                    "post_cash_pct": 5,
                    "post_leveraged_pct": 0,
                    "summary": "最大降低 FOMC 風險；可能錯過鴿派反彈"
                }
            },
            {
                "id": "C",
                "name": "維持原倉（積極）",
                "philosophy": "FOMC 前後不動，等 6/24 NVDA 股東大會",
                "actions": [
                    {"step":1,"fund":"全部位續抱","use":"6/24 NVDA 股東大會後再評估","rationale":"等更多基本面確認"},
                ],
                "result": {
                    "post_tw_pct": 83,
                    "post_us_pct": 17,
                    "post_cash_pct": 0,
                    "post_leveraged_pct": 0,
                    "summary": "最大化 FOMC 鴿派 + NVDA 股東大會的潛在獲利"
                }
            }
        ],
        "recommendation": {
            "primary": "A",
            "reason": "等 6/17 FOMC Warsh 首次表態確認政策方向，再決定美股部位；核心台股不動。",
            "secondary_if_aggressive": "C"
        },
        "risks": [
            "6/17 FOMC Warsh 意外鷹派→美股短線 -3%+",
            "6/24 羅素 2000 重構：小型股流動性衝擊",
            "中東油價推升通膨：WTI $85+，升息預期回升",
            "台股大盤 6/12 反彈後，能否守住 44,000 是關鍵",
            "00631L 2X 放大台股每日波動",
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
