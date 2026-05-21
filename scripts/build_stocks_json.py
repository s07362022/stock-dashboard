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

FX = 31.65                                      # 匯率 USD→TWD（2026/05/19 券商截圖）
UPDATE_NOTE = "2026/05/22 深度報告：5/21 台股大漲（加權+3.4%至41,368）；NVDA 財報營收816億但股價走弱；QCMU反彈至$34.27仍虧-12.6%。台股63.2%/美股36.8%。策略：減碼QCMU、守0050/2330/SMH、3711停損450、台積5/26法說前不追高。"

# ---- 1.1 台股持倉（券商 2026/05/19 截圖；報價 5/21 收盤）----
TW = [
    {"symbol":"0050.TW","name":"元大台灣50","shares":3110,"buy_price":65.08,"close":95.85,"change":3.35,"pct":3.62,"sector":"ETF（核心，長期）","tag":"core"},
    {"symbol":"00631L.TW","name":"元大台灣50正2","shares":4350,"buy_price":28.42,"close":31.58,"change":2.07,"pct":7.01,"sector":"ETF (=0050 2X)","tag":"core","underlying":"0050","multiplier":2},
    {"symbol":"2330.TW","name":"台積電","shares":25,"buy_price":2145.6,"close":2230.0,"change":45.0,"pct":2.06,"sector":"半導體","tag":"core"},
    {"symbol":"3711.TW","name":"日月光投控","shares":30,"buy_price":516.0,"close":510.0,"change":34.0,"pct":7.14,"sector":"封裝測試","tag":"core"},
]

# ---- 1.2 美股持倉（券商 2026/05/19 截圖；報價 5/21 美東）----
US = [
    {"symbol":"SMH","name":"VanEck Semiconductor ETF","shares":7,"buy_price":454.734285,"close":562.45,"change":-2.21,"pct":-0.39,"sector":"半導體 ETF","tag":"core"},
    {"symbol":"QCMU","name":"Direxion Daily QCOM Bull 2X ETF","shares":95,"buy_price":39.203447,"close":34.27,"change":1.65,"pct":5.06,"sector":"QCOM 2×日槓桿","tag":"satellite","underlying":"QCOM","multiplier":2},
    {"symbol":"ANEL","name":"Defiance 2× Long ANET Daily","shares":45,"buy_price":15.769091,"close":16.325,"change":0.875,"pct":5.66,"sector":"ANET 2×（日槓桿）","tag":"satellite","underlying":"ANET","multiplier":2},
    {"symbol":"QCOM","name":"Qualcomm Inc.","shares":2,"buy_price":197.66,"close":207.69,"change":5.18,"pct":2.56,"sector":"半導體（正股）","tag":"satellite"},
    {"symbol":"PLTU","name":"Direxion Daily PLTR Bull 2X ETF","shares":10,"buy_price":34.76,"close":36.99,"change":-0.13,"pct":0.35,"sector":"PLTR 2×日槓桿","tag":"satellite","underlying":"PLTR","multiplier":2},
    {"symbol":"CSCO","name":"Cisco Systems","shares":3,"buy_price":116.583333,"close":116.89,"change":2.54,"pct":2.22,"sector":"通訊／AI 網路","tag":"satellite"},
    {"symbol":"NVDA","name":"NVIDIA Corporation","shares":1,"buy_price":234.59,"close":219.29,"change":-4.18,"pct":-1.87,"sector":"AI GPU","tag":"core"},
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
total_mv = tw_mv + us_mv_twd
total_cost = tw_cost + us_cost_twd

tw_w = sum(1 for s in TW if s["pnl"] > 0); tw_l = sum(1 for s in TW if s["pnl"] < 0)
us_w = sum(1 for s in US if s["pnl_usd"] > 0); us_l = sum(1 for s in US if s["pnl_usd"] < 0)

# ========= 完整資料 =========
data = {
    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "updated_at_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
    "fx_rate": FX,

    "user_strategy": {
        "philosophy": "2026/05/22：台股 63.2%（0050/00631L/2330/3711）+ 美股 36.8%（SMH×7 核心、QCMU×95 仍為最大風險）。5/21 台股強彈、NVDA 財報利多出盡。QCMU 減至 50–60 股；守 0050/2330/SMH；3711 停損 450。",
        "leverage_map": [
            {"etf":"00631L","underlying":"0050","multiplier":2,"treat_as":"long_term_core"},
            {"etf":"QCMU","underlying":"QCOM","multiplier":2,"treat_as":"underlying_proxy"},
            {"etf":"ANEL","underlying":"ANET","multiplier":2,"treat_as":"underlying_proxy"},
            {"etf":"PLTU","underlying":"PLTR","multiplier":2,"treat_as":"underlying_proxy"},
        ]
    },

    "summary": {
        "total_market_value_twd": total_mv,
        "total_cost_twd": total_cost,
        "total_pnl_twd": total_mv - total_cost,
        "total_pnl_pct": round((total_mv - total_cost)/total_cost*100, 2),
        "tw_market_value_twd": tw_mv,
        "tw_cost_twd": tw_cost,
        "tw_pnl_twd": tw_mv - tw_cost,
        "tw_pnl_pct": round((tw_mv - tw_cost)/tw_cost*100, 2),
        "us_market_value_twd": us_mv_twd,
        "us_cost_twd": us_cost_twd,
        "us_pnl_twd": us_mv_twd - us_cost_twd,
        "us_pnl_pct": round((us_mv_twd - us_cost_twd)/us_cost_twd*100, 2),
        "us_market_value_usd": round(us_mv_usd, 2),
        "us_cost_usd": round(us_cost_usd, 2),
        "us_pnl_usd": round(us_mv_usd - us_cost_usd, 2),
        "tw_pct": round(tw_mv/total_mv*100, 2),
        "us_pct": round(us_mv_twd/total_mv*100, 2),
        "winners": tw_w + us_w,
        "losers": tw_l + us_l,
        "holdings_count": len(TW) + len(US),
        "effective_exposure_twd": round(total_mv * 1.25),
        "effective_leverage_ratio": 1.25,
    },

    "pnl_split": {
        "tw": {
            "title": f"🇹🇼 台股 — 表現傑出 +{round((tw_mv - tw_cost)/tw_cost*100, 1)}%",
            "market_value_twd": tw_mv, "cost_twd": tw_cost,
            "pnl_twd": tw_mv - tw_cost,
            "pnl_pct": round((tw_mv - tw_cost)/tw_cost*100, 2),
            "winners": tw_w, "losers": tw_l,
            "highlight": "0050 +47.3% 壓艙石；00631L +11.1%；2330 +3.9%；3711 反彈 +7.14% 仍略低於成本。",
            "verdict": "5/21 台股 V 型反彈；0050/正2 強勢，台積電 5/26 法說前不宜追高。"
        },
        "us": {
            "title": f"🇺🇸 美股 — {'+' if (us_mv_twd - us_cost_twd) >= 0 else ''}{round((us_mv_twd - us_cost_twd)/us_cost_twd*100, 1)}%",
            "market_value_twd": us_mv_twd, "cost_twd": us_cost_twd,
            "pnl_twd": us_mv_twd - us_cost_twd,
            "pnl_pct": round((us_mv_twd - us_cost_twd)/us_cost_twd*100, 2),
            "market_value_usd": round(us_mv_usd, 2),
            "cost_usd": round(us_cost_usd, 2),
            "pnl_usd": round(us_mv_usd - us_cost_usd, 2),
            "winners": us_w, "losers": us_l,
            "highlight": "SMH×7 +23.7%；QCMU×95 反彈但仍 -12.6%；NVDA 財報後 -6.5%（1股）；CSCO Q3 超預期 +0.3%。",
            "verdict": "NVDA 營收 816 億但股價走弱＝預期過高；QCMU 宜減 30–50 股；SMH/CSCO 續抱。"
        }
    },

    "indices": [
        {"name":"S&P 500","code":"SPX","value":7500.0,"change":45.0,"pct":0.60},
        {"name":"NASDAQ","code":"IXIC","value":26500.0,"change":120.0,"pct":0.45},
        {"name":"Dow Jones","code":"DJI","value":50000.0,"change":200.0,"pct":0.40},
        {"name":"SMH(費半ETF)","code":"SMH","value":562.45,"change":-2.21,"pct":-0.39},
        {"name":"VIX","code":"VIX","value":17.8,"change":-1.2,"pct":-6.3},
        {"name":"10Y美債","code":"US10Y","value":4.55,"change":-0.02,"pct":-0.44},
        {"name":"台股加權","code":"TWII","value":41368.21,"change":1347.39,"pct":3.36},
    ],

    "tw_stocks": TW,
    "us_stocks": US,

    "effective_exposure": [
        {"name":"0050＋00631L（台股核心）","icon":"🇹🇼","components":["0050×3110","00631L×4350"],"exposure_twd":435467,"pct_effective":54.4,"long_term":True},
        {"name":"台積電 2330","icon":"🏭","components":["2330 25股"],"exposure_twd":55750,"pct_effective":7.0,"long_term":True},
        {"name":"半導體 SMH×7","icon":"🔌","components":["SMH ETF"],"exposure_twd":124606,"pct_effective":15.6,"long_term":True},
        {"name":"QCOM 曝險（QCMU×95 + 正股×2）","icon":"📱","components":["QCMU 2×","QCOM 正股"],"exposure_twd":103194,"pct_effective":12.9,"long_term":False},
        {"name":"AI 衛星（NVDA+PLTU+ANEL）","icon":"🤖","components":["NVDA×1","PLTU 2×PLTR","ANEL 2×ANET"],"exposure_twd":42006,"pct_effective":5.2,"long_term":False},
        {"name":"通訊 CSCO×3","icon":"🌐","components":["Cisco 正股"],"exposure_twd":11089,"pct_effective":1.4,"long_term":False},
        {"name":"日月光 3711×30","icon":"📦","components":["3711 正股"],"exposure_twd":15300,"pct_effective":1.9,"long_term":True},
    ],

    "underlying_analysis": [
        {
            "ticker":"NVDA","name":"NVIDIA（持倉×1）","price":219.29,"today_pct":-1.87,"in_portfolio_twd":6933,
            "thesis":"5/20 財報：營收$81.6B YoY+85%、資料中心$75.2B；下季指引$91B。股價走弱＝預期已 price-in。",
            "pros":["AI 需求仍爆發","$80B 回購+股息大增","下季指引超共識"],
            "cons":["估值透支","與 SMH 重疊","財報後獲利了結"],
            "consensus_target":"多數 $250+","rating":"Buy","next_catalyst":"供應鏈/Blackwell 出貨","user_action":"🟡 1股觀察倉；不追；跌破$200 出清"
        },
        {
            "ticker":"QCOM","name":"Qualcomm（底層 QCMU×95）","price":207.69,"today_pct":2.56,"in_portfolio_twd":103194,
            "thesis":"QCMU 5/21 反彈+5%至$34.27，仍虧-12.6%（成本$39.20）。QCOM 正股+2.56%與槓桿雙重曝險。",
            "pros":["5/21 強彈","6/24 投資人日","車用/Edge AI"],
            "cons":["日槓桿衰減","95股集中","營收 YoY 仍負"],
            "consensus_target":"Baird $300、均值 $225","rating":"Hold","next_catalyst":"6/24 投資人日","user_action":"🔴 減碼30-50股；守$32 停損"
        },
        {
            "ticker":"ANET","name":"Arista（底層 ANEL×45）","price":144.53,"today_pct":2.87,"in_portfolio_twd":23262,
            "thesis":"AI 資料中心網路；ANEL 2× 日槓桿。5/21 ANET +2.87%。",
            "pros":["Raymond James $164","AI 800G 需求","與 CSCO 互補"],
            "cons":["ANEL 日衰減","估值偏高"],
            "consensus_target":"$164-190","rating":"Strong Buy","next_catalyst":"Q2 財報 8/3","user_action":"🟡 短線工具；長線改 ANET 正股"
        },
        {
            "ticker":"CSCO","name":"Cisco（×3）","price":116.89,"today_pct":2.22,"in_portfolio_twd":11089,
            "thesis":"Q3 FY26 營收$15.8B +12%；AI 基建訂單 FY26 上修$9B。",
            "pros":["財報超預期","AI 網通","穩健股息"],
            "cons":["成長低於純半導體","與 ANET 部分重疊"],
            "consensus_target":"$125-135","rating":"Buy","next_catalyst":"Q4 財報 8/19","user_action":"🟢 3股續抱；目標$125"
        },
        {
            "ticker":"PLTR","name":"Palantir（底層 PLTU×10）","price":36.99,"today_pct":0.35,"in_portfolio_twd":11711,
            "thesis":"PLTU 2× 日槓桿；政府+企業 AI 軟體敘事。",
            "pros":["+6.4% 持倉獲利","AI 題材"],
            "cons":["高波動","2× 衰減","投機衛星"],
            "consensus_target":"分歧","rating":"Hold","next_catalyst":"PLTR 財報","user_action":"🟡 10股衛星；破$30 減碼"
        },
    ],

    # ===== horizon_views（必須匹配渲染函式期望）=====
    "horizon_views": {
        "short_term_1m": {
            "title": "🔭 短線（~1 個月）情境預測",
            "intro": "5/14 台灣時間 1AM：持倉重組完成（出清AVGO/AIXI/MULL/SNDU/VSH；QCMU均攤至92股@$39.42；SMH×7；+PLUG+LNOK）。美股5/13強力V形反彈：**QCMU +6.9%**、**TSLT +7.6%**、**SMH +2.2%**；PLUG財報超預期+14.5%。台股5/14預期跟漲+0.5-1.5%，旺宏NOR主題延續。核心任務：TSLT今日鎖利10-15股；ONDL 20股出清；QCMU守住$39.42成本線等6/24催化劑。",
            "tw_index": {
                "current": 41374.5,
                "bull": 43000, "p_bull": 30,
                "base": 40500, "p_base": 45,
                "bear": 39000, "p_bear": 25,
                "scenario": "多頭：川習會協議+AI超週期持續；基本：通膨頑固+震盪消化；空頭：油價升溫+美中談判破裂+費半持續修正",
            },
            "forecasts": [
                {"symbol":"0050.TW","name":"元大台灣50","current":95.5,"bull":103,"base":98,"bear":90,"view":"5/13 -1.39%；美股反彈→5/14應跟漲；核心壓艙石不動"},
                {"symbol":"2330.TW","name":"台積電","current":2220,"bull":2600,"base":2350,"bear":2050,"view":"5/13 -1.55%技術修正；EPS NT$22.08歷史新高；全年>30%；5/14預期反彈"},
                {"symbol":"2337.TW","name":"旺宏","current":168,"bull":300,"base":200,"bear":140,"view":"🔥 5/13漲停+9.8%；NOR缺貨初期；等回測155-165加碼；目標300元"},
                {"symbol":"3711.TW","name":"日月光","current":548,"bull":620,"base":570,"bear":500,"view":"5/13 -1.26%；CoWoS受惠；EPS 3.24超預期；凱基目標588；5/14預期回升"},
                {"symbol":"QCOM","name":"Qualcomm（QCMU底層）","current":212.61,"bull":280,"base":225,"bear":185,"view":"5/12 -11.4%→5/13 +6-7%反彈；6/24投資人日為最大催化劑；QCMU 92股均攤$39.42"},
                {"symbol":"ANET","name":"Arista Networks（ANEL底層）","current":92,"bull":120,"base":105,"bear":78,"view":"ANEL底層；AI資料中心400/800G受惠；Strong Buy共識；5/14預期跟漲"},
                {"symbol":"SMH","name":"VanEck SMH（7股）","current":573.62,"bull":660,"base":600,"bear":500,"view":"5/13 +2.2%=$573；7股核心不動；NVDA 5/20財報前布局視窗"},
                {"symbol":"TSLA","name":"Tesla（TSLT底層）","current":426,"bull":530,"base":420,"bear":320,"view":"TSLT 2X今日+7.6%=$23.88；已獲利+29%；今日賣10-15股鎖利"},
                {"symbol":"PLUG","name":"Plug Power","current":3.87,"bull":7.50,"base":4.50,"bear":2.80,"view":"🆕 Q1財報超預期+14.5%；Project Quantum Leap降本；目標$4-7中線"},
            ]
        },
        "long_term": {
            "title": "🏔️ 長期（6 個月+）持有分析",
            "intro": "AI 結構性多頭至 2027；先進製程、AI ASIC、AI 雲算力、AI NAND 為四大核心。「核心 + 衛星」配置。",
            "core_long_term_buys": [
                {"symbol":"0050.TW","name":"元大台灣50","view":"永遠不賣的壓艙石，長期 8-12%/年"},
                {"symbol":"00631L.TW","name":"台灣50正2","view":"宣告長期持有，2X 放大 14-20%/年"},
                {"symbol":"2330.TW","name":"台積電","view":"AI 製造主軸無對手；目標 3,000+"},
                {"symbol":"AVGO","name":"Broadcom","view":"AI 客製 ASIC 龍頭；2027 AI 收入 $100B+"},
                {"symbol":"SMH","name":"VanEck SMH","view":"半導體大盤代理；長期目標 $580+"},
                {"symbol":"3711.TW","name":"日月光","view":"後段封測+CoWoS 受惠；目標 600+"},
            ],
            "satellite_growth": [
                {"symbol":"SNDK","name":"SanDisk","view":"AI NAND Pure Play；3 年 EPS 5→130+"},
                {"symbol":"CRWV","name":"CoreWeave","view":"AI 雲算力新星；ARR 大幅跳升"},
                {"symbol":"WDC","name":"Western Digital","view":"獨立後 HDD AI 儲存崛起"},
                {"symbol":"6669.TW","name":"緯穎","view":"AI 伺服器代工龍頭；新標的觀察"},
                {"symbol":"ANET","name":"Arista Networks","view":"AI 網路 400G/800G 龍頭"},
            ],
            "exit_or_reduce": [
                {"symbol":"ONDL","name":"ONDS 2X（20股）","view":"🔥 策略翻轉！ONDS Q1財報破紀錄→出清策略暫緩；若開盤站穩$16.50持有至$20-22；跌回$14恢復出清"},
                {"symbol":"TSMG","name":"TSM 2X（15股）","view":"建議賣出換 2330 正股；消除日槓桿衰減"},
                {"symbol":"ANEL","name":"2×ANET","view":"屬短線槓桿工具；若長抱 ANET 邏輯請考慮正股"},
                {"symbol":"LNOK","name":"2×Nokia（3股）","view":"🔥 連兩日爆漲+24.76%+8.13%；AI訂單爆發；小倉可持有；目標$110-120"},
            ]
        },
        "peak_decision": {
            "title": "❓ 加碼 / 持有 / 賣？— 我的判斷",
            "current_status": "2026/05/14 凌晨：持倉重組完成（出清AVGO/AIXI/MULL/SNDU/VSH）。美股核心→**SMH×7股**；最大槓桿→**QCMU×92股**（均攤$39.42）；新增PLUG/LNOK小倉。6/24 QCOM投資人日為最重要催化劑。",
            "verdict": "**SMH×7** 為核心多頭錨；**QCMU×92** 為最大風險＋最大機會點（6/24決戰）；TSLT今日+7.6%→應鎖利；**ONDL必須本週出清**；PLUG財報超預期是本週最佳操盤。",
            "actions": [
                {"type":"🟢 加碼／續抱","items":[
                    "00631L 與 0050 核心長抱策略不變",
                    "AVGO／SMH：趨勢未破前續抱；分批逢高鎖利可選擇",
                    "2330／3711：基本面＋封測敘事未破線前續抱",
                ]},
                {"type":"🟡 持有（控槓桿）","items":[
                    "ANEL：等同 **2×ANET 短線曝險**；不宜用『長期買 ANET』心智持有",
                    "TSLT／TSMG／SNDU／**QCMU／MULL**：守停損與**合計槓桿上限**（與 SMH 重疊時尤甚）",
                    "VSH：小衛星，可續抱或與 SMH 精簡二擇一",
                ]},
                {"type":"🔴 本週必做","items":[
                    "ONDL 20股：掛 GTC $13.80 出清，虧損-32.6%無反彈催化",
                    "TSLT 10-15股：今日+7.6%→鎖利，留20-25股長抱",
                    "TSMG 15股：考慮賣出換 2330 正股 1 股（消除日衰減）",
                ]},
                {"type":"⚫ 結構替代","items":[
                    "若確信 TSM 長多：TSMG（2×日槓桿）→ 2330 正股，更合適長期持有",
                    "若確信 ANET 長多：ANEL（2×日槓桿）→ ANET 正股，降低衰減風險",
                ]},
            ],
            "cash_target": "維持現金緩衝；槓桿標的不宜再加總曝險。"
        },
        "tomorrow_tw_strategy": {
            "title": "📆 5/22（週四）台股／美股策略",
            "macro_context": [
                "📌 5/21 台股 +1,347pts 收41,368（+3.36%）量價齊揚",
                "📌 5/20 輝達財報營收816億但股價走弱（利多出盡）",
                "📌 5/21 QCMU反彈+5%仍虧-12.6%；SMH -0.39%休息",
                "📌 台積電 5/26 法說；創意 5/22 財報",
                "📌 川習緩和+AI CapEx 主線不變；短線勿追高",
            ],
            "morning_plan": [
                {"step":1,"action":"9:00 確認美股收盤","detail":"NVDA 盤後走向；若續弱→台股科技開低機率升"},
                {"step":2,"action":"9:10 台積電","detail":"🟢 2,230 核心不動；5/26法說前不追高；停損2,100"},
                {"step":3,"action":"9:30 QCMU減碼","detail":"🔴 開盤掛減30-50股；守$32；保留QCOM正股"},
                {"step":4,"action":"3711 日月光","detail":"🟡 510反彈；未站530不補；破450出清"},
                {"step":5,"action":"21:30 美股","detail":"SMH/CSCO持有；NVDA不追；00631L獲利可轉0050"},
            ],
            "one_line": "5/22：台股強彈後降槓桿→減QCMU、守0050/2330/SMH；等台積5/26法說。"
        }
    },

    "news": [
        {"date":"2026-05-21","category":"科技","title":"🔥 輝達 Q1 FY27 營收$81.6B（+85%）超預期；盤後仍跌～1.3%（利多出盡）","impact":"mixed","source":"NVIDIA IR / Yahoo Finance"},
        {"date":"2026-05-21","category":"台股","title":"台股加權 +1,347pts 收41,368（+3.36%），史上第五大點數漲幅；成交逾1兆","impact":"positive","source":"Taiwan News"},
        {"date":"2026-05-21","category":"半導體","title":"聯發科漲停、台積電+2.06%、日月光+7.14%；半導體領漲","impact":"positive","source":"Taiwan News / BigGo"},
        {"date":"2026-05-21","category":"美股","title":"QCOM +2.56%、ANEL底層ANET鏈+5.66%；SMH -0.39% 休息","impact":"mixed","source":"BigGo Finance"},
        {"date":"2026-05-20","category":"科技","title":"輝達宣布$80B 額外回購、季股息$0.01→$0.25","impact":"positive","source":"Al Jazeera"},
        {"date":"2026-05-19","category":"台股","title":"台股加權 -716pts 收40,176（-1.75%），跌破月線；台積電 -1.56% 至2,205；聯發科 -7.21%；記憶體股跌停","impact":"negative","source":"Taiwan News / Yahoo TW"},
        {"date":"2026-05-19","category":"半導體","title":"費半/SMH -1.83%；MU -5.95%；MULL(2×MU) -11.84%；半導體獲利了結延續","impact":"negative","source":"BigGo Finance"},
        {"date":"2026-05-18","category":"美股","title":"Nasdaq 收跌：科技／晶片領跌；10Y美債殖利率升至2025/2以來高點~4.6%","impact":"negative","source":"Economic Times / TradingView"},
        {"date":"2026-05-15","category":"通膨/Fed","title":"CPI 3.8%、核心2.8%超預期；市場估Fed年底可能升息25bp","impact":"negative","source":"CNBC / Yahoo Finance"},
        {"date":"2026-05-19","category":"資金輪動","title":"資金由大型科技轉向金融、電信；中華電創新高","impact":"mixed","source":"Taiwan News"},
        {"date":"2026-05-14","category":"⚠️ 警示","title":"QCMU(2×QCOM)盤前-6.72%至$34.03；QCOM持續面臨Apple modem流失+Android疲弱；92股×2倍曝險需警戒；若開盤跌破$34需減碼20-30股","impact":"negative","source":"BigGo 盤前 09:02 EDT"},
        {"date":"2026-05-14","category":"台股","title":"🎉 台股大漲+377pts(+0.91%)收41,752；台積電+50元收2,270；成交1.22兆；記憶體三雄成焦點；川習峰會帶動AI半導體樂觀","impact":"positive","source":"壹蘋、Yahoo財經"},
        {"date":"2026-05-14","category":"美股","title":"🏆 S&P 500創歷史新高7,444(+0.58%)；NASDAQ歷史新高+1.2%；Alphabet、NVIDIA大漲帶動；川習會+AI樂觀情緒驅動","impact":"positive","source":"MarketScreener、Moneycontrol"},
        {"date":"2026-05-14","category":"地緣政治","title":"川習峰會正向收場：習稱「貿易戰無贏家」；美中擬各降300億商品關稅；惟習嚴正警告台灣問題可能引發衝突","impact":"mixed","source":"CBS News、Business Times"},
        {"date":"2026-05-13","category":"台股","title":"台股加權 -523.82pts(-1.25%) 收41,374；盤中最深跌883pts；台積電-1.55%收2,220；失守5日線","impact":"negative","source":"聯合、PChome"},
        {"date":"2026-05-13","category":"記憶體","title":"🔥 旺宏(2337)漲停+9.80%（168元）；AI NOR Flash缺貨爆發；大廠撤出2D NAND，旺宏成「最後供應商」；本土機構目標300元","impact":"positive","source":"CMoney、理財周刊"},
        {"date":"2026-05-13","category":"地緣政治","title":"川習會5/13-14北京登場；美稀土 vs 中半導體出口管制為談判核心；中國重稀土出口量同比-50%，傳考慮延長休戰期","impact":"mixed","source":"經濟日報、時報資訊"},
        {"date":"2026-05-12","category":"通膨/Fed","title":"美國4月CPI年增3.8%（創2023年5月新高，超預期3.7%）；核心CPI 2.8%；Fed降息推至2027；6月降息概率僅2.4%","impact":"negative","source":"鉅亨網、工商時報"},
        {"date":"2026-05-12","category":"半導體","title":"⚠️ QCOM暴跌-11.4%（2020年來最糟單日）；AI rally退潮獲利了結；費半SOX -3.01%；QCMU(2×QCOM)實際收盤-23%至$35.52","impact":"negative","source":"FXLeaders、CNBC"},
        {"date":"2026-05-12","category":"美股","title":"ANEL(2×ANET)+8.80%；AVGO -2.13%收$419.30（盤前5/13回升$421.95）；SMH -2.61%收$561.25（盤前+1.92%）","impact":"mixed","source":"BigGo"},
        {"date":"2026-05-13","category":"半導體","title":"美商務部禁止晶片設備商向華虹半導體供貨；鎖定阻礙中國7nm晶片；美中半導體出口管制持續升級","impact":"negative","source":"Now新聞"},
        {"date":"2026-05-13","category":"關稅","title":"美國際貿易法院裁定川普10%全球關稅違法；未來恐改以半導體/稀土232條款繼續加碼","impact":"mixed","source":"經濟日報"},
        {"date":"2026-05-12","category":"能源","title":"美伊緊張局勢升高；中東油價一度突破$100/桶；CPI能源分項年增17.9%；通膨主要推手","impact":"negative","source":"多方來源"},
        {"date":"2026-05-13","category":"🆕 財報","title":"🔥 PLUG（Plug Power）Q1 2026 財報超預期：EPS -$0.08（估-$0.09）；營收$163M +22% YoY；毛利率-13%（大幅改善自-55%）；Project Quantum Leap降本；CEO：Q4 2026 正EBITDAS；股價今日+14.5%","impact":"positive","source":"Proactive Investors / Motley Fool"},
        {"date":"2026-05-13","category":"美股反彈","title":"QCMU +6.9%($37.97)、TSLT +7.64%($23.88)、SMH +2.2%($573.62) — 半導體 V 形反彈；市場認為 CPI 引發賣壓過度反應；AVGO 小跌 -0.49%($417.22)","impact":"positive","source":"BigGo Finance 5/13 盤中"},
        {"date":"2026-05-13","category":"分析師","title":"PLUG 多家分析師上調目標：B.Riley $5.00、HC Wainwright $7.00（Buy）、Canaccord $4.00（升自$2.50）、Susquehanna $3.75（Neutral）","impact":"positive","source":"MarketBeat / 247wallst"},
        {"date":"2026-05-13","category":"台股","title":"台股 5/13 大盤 41,374.5 (-523pt, -1.25%)；旺宏 2337 +9.8% 漲停；日月光 3711 -1.26%；台積電 2330 -1.55%；電子股普跌","impact":"negative","source":"TechNews / BigGo"},
        {"date":"2026-05-12","category":"美股","title":"QCOM 暴跌 -11.4%（2020年最糟）→ QCMU -23%；原因：4月核心CPI +0.4% MoM超預期(vs +0.3%)；半導體賣壓擴大","impact":"negative","source":"CNBC / fxleaders"},
        {"date":"2026-05-12","category":"宏觀","title":"美國 4月核心CPI +0.4% MoM（預期+0.3%）；年增 3.2%；Fed 降息預期進一步延後至最早 12月","impact":"negative","source":"BLS / Bloomberg"},
        {"date":"2026-05-08","category":"美股大盤","title":"S&P 500 (+0.74%) 7,391 / NASDAQ (+1.32%) 26,145 / Dow (+0.05%) 49,621 — 創歷史新高；美股連 6 週上漲；83% S&P 500 公司 Q1 EPS 超預期","impact":"positive","source":"Yahoo Finance / Marketscreener"},
        {"date":"2026-05-08","category":"半導體","title":"費半 ETF SMH BigGo 收 $566.54（+4.9%）；Intel +16%（Apple 晶片代工談判）、AMD +8%、Micron +13%","impact":"positive","source":"BigGo / Motley Fool"},
        {"date":"2026-05-08","category":"美股","title":"QCOM BigGo 收 $219.09（+8.17%）；Q2 FY2026 EPS $6.88 超預期；超大雲客製矽 Q4 2026 初出貨；5天內共+41%","impact":"positive","source":"BigGo / Trefis"},
        {"date":"2026-05-08","category":"美股","title":"Arista（ANET）BigGo 收 $141.77（+0.01%）；FY2026 AI 指引延續","impact":"mixed","source":"BigGo / StockAnalysis"},
        {"date":"2026-05-08","category":"地緣","title":"美伊和平談判進展：伊朗回應美方備忘錄；荷姆茲海峽再開預期 → 布蘭特原油跌至 ~$98；全球股市大漲","impact":"positive","source":"Bloomberg / CNBC"},
        {"date":"2026-05-07","category":"美中貿易","title":"川習會談判持續；美中關稅降幅討論中；稀土出口管制預期鬆綁 → 半導體製造成本利好","impact":"mixed","source":"WEF / Yahoo Finance"},
        {"date":"2026-05-08","category":"就業數據","title":"美國 4 月新增就業 115,000（超預期 65,000）；失業率穩 4.3%；勞動市場韌性支撐 Fed 維持利率","impact":"positive","source":"BLS / Yahoo Finance"},
        {"date":"2026-04-30","category":"QCOM 財報","title":"QCOM 超大雲客製矽揭露（4/30）→ 股價單日飆 +16-20%；5天連漲達 $219；Q2 EPS $6.88 (+173% YoY)；車用+50%","impact":"positive","source":"Morningstar / Business Insider"},
        {"date":"2026-04-25","category":"財報","title":"台積電Q1 2026：EPS NT$22.08歷史新高；毛利率66.2%；全年成長上修>30%；N2量產良率良好","impact":"positive","source":"民報、fiisual"},
        {"date":"2026-04-27","category":"台股","title":"旺宏 Q1 2026：EPS 0.9 元終結連 10 季虧損；毛利 40.8%；NOR Flash 缺貨行情確立","impact":"positive","source":"Yahoo TW"},
        {"date":"2026-04-29","category":"台股","title":"日月光 Q1 2026：EPS 3.24 元超預期；LEAP 先進封測 2026 突破 $35億；CoWoS 受惠","impact":"positive","source":"TechNews"},
        {"date":"2026-04","category":"美聯準會","title":"FOMC：19 人中 7 人預期 2026 全年零降息；Fed 加息概率 30%（2027 前）；核心 PCE 通膨 3.1%","impact":"negative","source":"Phemex / Fed"},
    ],

    "earnings": [
        {"ticker":"NVDA","name":"NVIDIA","period":"Q1 FY27 (5/20)","revenue":"$81.6B (+85%)","eps":"$1.87 adj.","highlight":"資料中心$75.2B +92%；下季指引$91B；股價財報後走弱","rating":"Buy"},
        {"ticker":"CSCO","name":"Cisco","period":"Q3 FY26 (5/13)","revenue":"$15.8B (+12%)","eps":"$1.06 adj.","highlight":"AI 訂單 FY26 $9B；毛利66%","rating":"Buy"},
        {"ticker":"PLUG","name":"Plug Power","period":"Q1 2026 (5/13)","revenue":"$163M (+22% YoY)","eps":"-$0.08（超預期 -$0.09）","highlight":"毛利率-13%（大幅改善自-55%）；Project Quantum Leap降本；Q4 2026 正EBITDAS目標；$8B電解槽管線；今日+14.5%","rating":"Buy（B.Riley目標$5）"},
        {"ticker":"AAPL","name":"Apple","period":"Q2 FY26 (4/30)","revenue":"$111.2B (+17%)","eps":"$2.01 (+22%)","highlight":"服務 $31B 新高；$100B 回購；Q3 指引 +14-17%；毛利 47.5-48.5%","rating":"Buy"},
        {"ticker":"AVGO","name":"Broadcom","period":"Q1 FY26 (3/4)","revenue":"$19.31B (+29%)","eps":"$2.05 (Non-GAAP)","highlight":"AI 收入 $8.4B (+106%)；Q2 指引 $22B；CEO：2027 AI 晶片 >$100B；下次財報 6/3","rating":"Buy"},
        {"ticker":"QCOM","name":"Qualcomm","period":"Q2 FY26 (5/8)","revenue":"$10.6B (-3% YoY)","eps":"$6.88（超預期 $2.61；+173% YoY）","highlight":"超大雲客製矽 Q4 2026 出貨；車用 +50% YoY；6/24 投資人日（最重要催化劑）","rating":"Hold→升評中"},
        {"ticker":"2330.TW","name":"台積電","period":"Q1 2026","revenue":"$35.9B (+35.1%)","eps":"NT$22.08","highlight":"毛利 66.2%；全年指引>30%；AI 加速器 CAGR 54-56%；CoWoS 滿載至 2027；CapEx $52-56B","rating":"Strong Buy"},
        {"ticker":"3711.TW","name":"日月光投控","period":"Q1 2026","revenue":"超預期","eps":"NT$3.24","highlight":"LEAP 先進封測 2026 突破 $35億；CoWoS 受惠","rating":"Buy"},
        {"ticker":"2337.TW","name":"旺宏","period":"Q1 2026","revenue":"轉正","eps":"NT$0.90","highlight":"終結連 10 季虧損；毛利 40.8%；投信賣壓仍在","rating":"Hold"},
        {"ticker":"SNDK","name":"SanDisk","period":"FY26 Q3","revenue":"上行週期","eps":"2026E $127","highlight":"NAND 合約漲 55-60%；5 年期 $42B 合約；Bernstein 目標 $1,250","rating":"Buy"},
        {"ticker":"INTC","name":"Intel","period":"Q2 2026E","revenue":"$14.39B（市場估）","eps":"$0.21（市場估）","highlight":"Apple 晶片代工談判 → 單日 +16%；修復+事件驅動","rating":"Hold→Buy(事件)"},
        {"ticker":"TSLA","name":"Tesla","period":"Q1 2026","revenue":"$22.39B","eps":"$0.41","highlight":"Robotaxi 進度；Capex 上修；TSLT 2× 衰減注意","rating":"Hold"},
        {"ticker":"CRWV","name":"CoreWeave","period":"Q1 2026","revenue":"ARR 跳升","eps":"轉虧為盈中","highlight":"Meta $21B + Jane Street $7B；雲算力核心標的","rating":"Buy"},
    ],

    "analysts": {
        "panel": ["巴菲特","芒格","Cathie Wood","Michael Burry","Peter Lynch","Ray Dalio","Druckenmiller","葛拉漢","索羅斯","科斯托蘭尼","Jim Simons","動能派","價值派","成長派","宏觀策略","風控長","產業專家","量化派","ESG"],
        "votes": [
            {"symbol":"0050.TW","name":"元大台灣50","sell":0,"hold":5,"buy":14,"label":"核心 +44%"},
            {"symbol":"00631L.TW","name":"台灣50正2","sell":1,"hold":11,"buy":7,"label":"槓桿長持"},
            {"symbol":"2330.TW","name":"台積電","sell":0,"hold":6,"buy":13,"label":"AI 定錨"},
            {"symbol":"3711.TW","name":"日月光","sell":3,"hold":12,"buy":4,"label":"已減碼 -9%"},
            {"symbol":"SMH","name":"SMH","sell":0,"hold":5,"buy":14,"label":"核心 +18%"},
            {"symbol":"QCMU","name":"2×QCOM","sell":11,"hold":6,"buy":2,"label":"🔴 -12.6% 減碼"},
            {"symbol":"ANEL","name":"2×ANET","sell":5,"hold":11,"buy":3,"label":"縮至45股"},
            {"symbol":"PLTU","name":"2×PLTR","sell":4,"hold":12,"buy":3,"label":"小倉衛星"},
            {"symbol":"CSCO","name":"Cisco","sell":2,"hold":14,"buy":3,"label":"5/20 財報"},
            {"symbol":"NVDA","name":"NVIDIA","sell":4,"hold":10,"buy":5,"label":"財報利多出盡"},
            {"symbol":"QCOM","name":"QCOM 正股","sell":3,"hold":13,"buy":3,"label":"與 QCMU 重疊"},
        ]
    },

    "picks": [
        {"rank":1,"ticker":"2454","name":"聯發科","market":"TW","price":3550,"target_low":4000,"target_high":5000,"upside_pct":41.0,"thesis":"AI ASIC；高盛目標5000（5/02）；5/21漲停","type":"個股"},
        {"rank":2,"ticker":"6669","name":"緯穎科技","market":"TW","price":5345,"target_low":5800,"target_high":6400,"upside_pct":20.0,"thesis":"AI 伺服器 ODM；5/21 +8.86%","type":"個股"},
        {"rank":3,"ticker":"3443","name":"創意電子","market":"TW","price":5065,"target_low":5400,"target_high":5800,"upside_pct":15.0,"thesis":"ASIC 設計；5/22 財報","type":"個股"},
        {"rank":4,"ticker":"AMD","name":"Advanced Micro Devices","market":"US","price":442.12,"target_low":480,"target_high":550,"upside_pct":24.0,"thesis":"AI GPU/CPU；共識~$405；≤$300 ✓","type":"個股"},
        {"rank":5,"ticker":"ANET","name":"Arista Networks","market":"US","price":144.53,"target_low":164,"target_high":190,"upside_pct":31.0,"thesis":"AI 網路；Raymond James $164；≤$300 ✓","type":"個股"},
    ],

    # ===== actions（A/B 用 strategy/stop/target；C 用 action/reason）=====
    "actions": {
        "A": [
            {"symbol":"0050.TW","name":"元大台灣50","price":95.85,"target":"100-105","stop":90,"strategy":"壓艙石 +47%；5/21大漲不追；核心不動"},
            {"symbol":"2330.TW","name":"台積電","price":2230,"target":"2400-2600","stop":2100,"strategy":"5/26 法說前持有；25股核心；不追高"},
            {"symbol":"SMH","name":"VanEck 半導體（7股）","price":562.45,"target":"600-620","stop":520,"strategy":"+23.7% 獲利；半導體 ETF 核心；NVDA財報後續抱"},
            {"symbol":"00631L.TW","name":"台灣50正2","price":31.58,"target":"33-35","stop":28,"strategy":"+11% 可部分鎖利轉0050降波"},
        ],
        "B": [
            {"symbol":"CSCO","name":"Cisco","price":116.89,"target":"125-135","stop":108,"strategy":"Q3超預期；AI訂單$9B；3股續抱"},
            {"symbol":"QCOM","name":"Qualcomm 正股","price":207.69,"target":"220-230","stop":190,"strategy":"2股；減QCMU後保留正股曝險"},
            {"symbol":"PLTU","name":"2×PLTR","price":36.99,"target":"42-48","stop":30,"strategy":"10股衛星；日槓桿勿長抱"},
            {"symbol":"ANEL","name":"2×ANET","price":16.33,"target":"18-20","stop":14,"strategy":"45股短線；ANET+2.87%"},
            {"symbol":"3711.TW","name":"日月光","price":510,"target":"540-560","stop":450,"strategy":"反彈+7%；仍略虧成本；破450出清"},
        ],
        "C": [
            {"symbol":"QCMU","name":"2×QCOM（95股）","price":34.27,"action":"減碼 30-50 股","reason":"仍虧-12.6%；成本$39.20；與QCOM雙重曝險；守$32"},
            {"symbol":"NVDA","name":"NVIDIA","price":219.29,"action":"觀察／跌破$200出清","reason":"財報強但股價弱；1股與SMH重疊"},
        ]
    },

    # ===== next_buy_recommendations（tickers 必須是物件陣列）=====
    "next_buy_recommendations": [
        {
            "scenario": "美股持續觀察（5/13盤中）",
            "tickers": [
                {"ticker":"ANET","name":"Arista Networks","price":165.0,"rationale":"AI 網路 400G/800G 龍頭；Strong Buy 17/17；目標$175-200","size_suggest":"1 股 ≈ NT$ 5,200","confidence":"🟢 高"},
                {"ticker":"AVGO","name":"Broadcom","price":417.22,"rationale":"剛賣出但仍可再關注；6/3 財報催化；AI ASIC Q2 $22B指引","size_suggest":"1 股 ≈ NT$ 13,150","confidence":"🟢 高"},
                {"ticker":"INTC","name":"Intel","price":109.0,"rationale":"轉機修復 + Apple晶片代工；量能活躍","size_suggest":"1 股 ≈ NT$ 3,434","confidence":"🟡 中"},
            ]
        },
        {
            "scenario": "台股 5/14（週四）開盤可下單",
            "tickers": [
                {"ticker":"2337","name":"旺宏電子","price":168,"rationale":"NOR Flash缺貨主題；昨漲停；等回測155-165加碼；目標300","size_suggest":"零股 5-10 股 ≈ NT$ 840-1,680","confidence":"🟢 高"},
                {"ticker":"3711","name":"日月光投控","price":548,"rationale":"CoWoS/LEAP先進封測；Q1超預期；逢回520-530加碼","size_suggest":"1 股 ≈ NT$ 548","confidence":"🟢 高"},
                {"ticker":"2330","name":"台積電","price":2220,"rationale":"外資最低目標 2,288；折讓 3%+；5/14 可能反彈","size_suggest":"零股 1 股 ≈ NT$ 2,220","confidence":"🟢 高"},
            ]
        }
    ],

    # ===== allocation（陣列格式，非物件）=====
    "allocation": {
        "current": [
            {"label":"台股核心（0050+00631L+2330+3711）","value":63.2},
            {"label":"美股核心 ETF（SMH×7+NVDA）","value":16.5},
            {"label":"美股槓桿（QCMU+ANEL+PLTU）","value":17.2},
            {"label":"美股衛星（CSCO+QCOM）","value":3.0},
            {"label":"現金","value":0.1},
        ],
        "target": [
            {"label":"台股核心","value":58},
            {"label":"美股核心 ETF","value":16},
            {"label":"美股槓桿","value":10},
            {"label":"美股衛星","value":8},
            {"label":"現金","value":8},
        ]
    },

    "consensus": [
        {"symbol":"QCMU","name":"Direxion 2× QCOM（92股）","rating":"🟡 均攤觀察","target":"QCOM 分析師均值$225-300；今日QCMU+6.9%=$37.97；守$39.42均攤成本；6/24投資人日為定論日","date":"2026-05-14"},
        {"symbol":"PLUG","name":"Plug Power（20股）","rating":"🆕 Buy/Neutral 分歧","target":"B.Riley $5.00；HC Wainwright $7.00；Canaccord $4.00；Susquehanna $3.75；Q1財報超預期","date":"2026-05-13"},
        {"symbol":"LNOK","name":"Defiance 2×Nokia（3股）","rating":"中性","target":"Nokia ADR $5-7；LNOK跟隨2×波動；小倉觀察","date":"2026-05-14"},
        {"symbol":"AAPL","name":"Apple","rating":"Buy","target":"$215-280","date":"2026-05"},
        {"symbol":"TSM","name":"TSMC ADR","rating":"Strong Buy","target":"$400-480","date":"2026-05"},
        {"symbol":"2330.TW","name":"台積電","rating":"加碼","target":"NT$2,288-3,030","date":"2026-04"},
        {"symbol":"3711.TW","name":"日月光","rating":"加碼","target":"NT$308-588","date":"2026-04"},
        {"symbol":"2337.TW","name":"旺宏","rating":"🔥 強力買進","target":"NT$200-300；本土機構目標300元；NOR缺貨初期；5/13漲停+9.8%；AI邊緣推理需求引爆","date":"2026-05-13"},
        {"symbol":"ANET","name":"Arista Networks","rating":"Strong Buy（17/17）","target":"均值 $175.18；範圍 $112-200；Morningstar $190","date":"2026-05"},
        {"symbol":"INTC","name":"Intel","rating":"Hold→Buy(事件驅動)","target":"$120-135","date":"2026-05"},
        {"symbol":"SMH","name":"VanEck 半導體 ETF","rating":"Buy","target":"$620-680；費半多頭主軸","date":"2026-05"},
        {"symbol":"CRWV","name":"CoreWeave","rating":"Buy","target":"$130-160","date":"2026-05"},
    ],

    "forecast": [
        {"symbol":"QCMU","name":"2×QCOM ETF（92股）","bull":52,"base":40,"bear":26,"catalyst":"6/24投資人日揭露超大雲路線圖（最大催化）；今日+6.9%=$37.97；QCOM底層若站穩$215→目標QCMU $42-48"},
        {"symbol":"PLUG","name":"Plug Power（正股）","bull":7.50,"base":4.50,"bear":2.80,"catalyst":"Q1財報超預期；Project Quantum Leap降本；Q4 2026 EBITDAS正數目標；電解槽$8B管線"},
        {"symbol":"LNOK","name":"2×Nokia ETF","bull":115,"base":88,"bear":65,"catalyst":"企業5G+AI網路合約；諾基亞Q2財報；3股小倉"},
        {"symbol":"ANET","name":"Arista Networks（ANEL底層）","bull":120,"base":100,"bear":75,"catalyst":"FY2026 AI指引；Strong Buy共識；ANEL底層"},
        {"symbol":"TSM","name":"TSMC ADR（TSMG底層）","bull":460,"base":405,"bear":340,"catalyst":"7/16法說；CoWoS擴產；Q2指引$39-40B；N2量產"},
        {"symbol":"TSLA","name":"Tesla（TSLT底層）","bull":530,"base":420,"bear":320,"catalyst":"Robotaxi FSD進展；Q2交付數據；TSLT今日+7.6%"},
        {"symbol":"CRWV","name":"CoreWeave","bull":160,"base":135,"bear":90,"catalyst":"Meta $21B合約；Q2 ARR揭露；AI雲算力"},
        {"symbol":"2330.TW","name":"台積電","bull":2600,"base":2350,"bear":2050,"catalyst":"EPS NT$22.08歷史新高；全年>30%成長；7/16法說；N2量產"},
        {"symbol":"3711.TW","name":"日月光","bull":620,"base":560,"bear":490,"catalyst":"CoWoS封裝供不應求；EPS 10.85超預期；AI封測訂單"},
        {"symbol":"2337.TW","name":"旺宏","bull":300,"base":200,"bear":140,"catalyst":"🔥 NOR Flash缺貨爆發；今日漲停+9.8%；AI邊緣推理+AI-in-Car需求爆發"},
        {"symbol":"AAPL","name":"Apple","bull":255,"base":235,"bear":200,"catalyst":"Q3 +14-17%指引；$100B回購；服務收入$31B新高"},
        {"symbol":"SMH","name":"VanEck SMH","bull":640,"base":580,"bear":510,"catalyst":"費半超賣後NVDA 5/20財報催化；$545-555支撐；盤前+1.92%反彈"},
    ],

    # ===== capital_plan（含 status / sources / totals / options 結構）=====
    "capital_plan": {
        "title": "2026-05-02 資金部署策略 v6（5 月底用錢計畫 + 星期一開盤）",
        "sources": [
            {"src":"AIXI 立即 Market 賣 50 股","amount_twd":1290,"amount_usd":40.75,"status":"immediate","note":"-48.91%；繼續清，止血"},
            {"src":"ONDL GTC $18.50 賣 30 股","amount_twd":17500,"amount_usd":553.0,"status":"conditional","note":"底層 ONDS 失效；條件觸發"},
            {"src":"信昌電 6173 觸 88-90 出 150 股","amount_twd":13500,"amount_usd":None,"status":"conditional","note":"逢 88-90 全出"},
            {"src":"TSLT 減 24 股（若 TSLA<$300）","amount_twd":11000,"amount_usd":347.5,"status":"conditional","note":"槓桿日損耗；分散度過高"},
        ],
        "totals": {
            "immediate": 1290,
            "conditional": 42000,
            "total": 43290
        },
        "context": [
            "5 月底用錢需求未變（NT$25,000-30,000）",
            "AIXI/ONDL 必清，越拖越糟（已虧損）",
            "AVGU + AAOX 已於 5/2 出清，新建倉 WDCX 4 股",
            "Apple Q2 + AVGO Q1 + TSMC Q1 + 日月光 Q1 全部超預期，AI 主軸不變",
            "週一台股料受外圍跳高帶動，正常順勢",
        ],
        "options": [
            {
                "id": "A",
                "name": "保守清理（最低風險）",
                "philosophy": "只清 AIXI+ONDL，不動其他部位；現金留作 5 月用錢",
                "actions": [
                    {"step":1,"fund":"AIXI Market 賣 50 股 ≈ NT$1,290","use":"留現金","rationale":"立即止血"},
                    {"step":2,"fund":"ONDL GTC $18.50 賣 30 股 ≈ NT$17,500","use":"留現金","rationale":"條件觸發回收"},
                ],
                "result": {
                    "post_tw_pct": 60.3,
                    "post_us_pct": 37.5,
                    "post_cash_pct": 2.2,
                    "post_leveraged_pct": 26.5,
                    "summary": "回收 NT$18,790；保留所有核心；不足 5 月缺口 NT$10,000"
                }
            },
            {
                "id": "B",
                "name": "平衡部署（推薦 ⭐）",
                "philosophy": "清 AIXI+ONDL+信昌電；現金 7%；補一點 AVGO 加倉位",
                "actions": [
                    {"step":1,"fund":"AIXI Market 賣 50 股 ≈ NT$1,290","use":"留現金","rationale":"立即止血"},
                    {"step":2,"fund":"ONDL GTC $18.50 賣 30 股 ≈ NT$17,500","use":"留現金","rationale":"條件觸發回收"},
                    {"step":3,"fund":"信昌電 6173 觸 88-90 出 150 股 ≈ NT$13,500","use":"留現金","rationale":"處置股；補 5 月缺口"},
                    {"step":4,"fund":"AVGO 逢 $400-410 加 1 股 ≈ NT$13,000","use":"從現金扣","rationale":"Q2 $22B 指引高確定性"},
                    {"step":5,"fund":"日月光 3711 逢 470 加 1 股 ≈ NT$470","use":"從現金扣","rationale":"凱基目標 588"},
                ],
                "result": {
                    "post_tw_pct": 58.5,
                    "post_us_pct": 38.0,
                    "post_cash_pct": 3.5,
                    "post_leveraged_pct": 25.0,
                    "summary": "回收 NT$32,290；補強 AVGO+日月光；覆蓋 5 月缺口；推薦"
                }
            },
            {
                "id": "C",
                "name": "積極調整（高槓桿降）",
                "philosophy": "B + 減 TSLT 24 股；TSMG 換 2330",
                "actions": [
                    {"step":1,"fund":"清 AIXI+ONDL+信昌電 ≈ NT$32,290","use":"留現金","rationale":"全清待出清部位"},
                    {"step":2,"fund":"TSLT 減 24 股（若 TSLA<$300）≈ NT$11,000","use":"留現金","rationale":"降槓桿"},
                    {"step":3,"fund":"TSMG 30 股 ≈ NT$35,400","use":"換 2330 16 股","rationale":"消除槓桿衰減；直接持有原股"},
                    {"step":4,"fund":"剩餘現金","use":"AVGO+日月光+SMH 分批","rationale":"主升段攤平"},
                ],
                "result": {
                    "post_tw_pct": 64.0,
                    "post_us_pct": 32.0,
                    "post_cash_pct": 4.0,
                    "post_leveraged_pct": 18.0,
                    "summary": "回收 NT$43,290；降槓桿至 18%；台股權重升至 64%"
                }
            }
        ],
        "recommendation": {
            "primary": "B",
            "reason": "B 方案兼顧資金回收與成長部位補強：清三個拖累部位 + 補強 AVGO + 日月光，現金 3.5% 足以週一執行；不衝動降槓桿。",
            "secondary_if_aggressive": "C"
        },
        "risks": [
            "ONDL 流動性差，可能滑價；GTC 可能等不到 $18.50",
            "信昌電未必觸 88-90，需有耐心",
            "TSLT 槓桿耗損若 TSLA 在高檔盤整，每日倍增仍可能月均顯著衰減",
            "美債若升至 4.6%+，高 P/E 科技股修正壓力上升",
            "週一若外圍急跌，台股 ADR 跳空低開風險"
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
