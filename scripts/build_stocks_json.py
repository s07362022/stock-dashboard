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

FX = 31.405                                      # 匯率 USD→TWD（2026/05/14 台灣時間）
UPDATE_NOTE = "2026/05/14 盤後更新：台股+377pts(+0.91%)收41,752；台積電+50元收2,270；日月光548(平盤)；0050收96.05；美股S&P 7,444創歷史新高；川習峰會貿易正面、AI樂觀情緒驅動雙市創高。QCMU實際5/13收盤$36.48（已更正）；SMH收$572.46(+2%)；旺宏NOR缺貨主題持續；更新5檔潛力股：台股旺宏/世芯/聯發科，美股AMD/ORCL。匯率31.405。"

# ---- 1.1 台股持倉（BigGo 2026/05/14 UTC+8 收盤）----
TW = [
    {"symbol":"0050.TW","name":"元大台灣50","shares":3010,"buy_price":64.1,"close":96.05,"change":0.55,"pct":0.58,"sector":"ETF（核心，長期）","tag":"core"},
    {"symbol":"00631L.TW","name":"元大台灣50正2","shares":4150,"buy_price":28.23,"close":32.20,"change":0.35,"pct":1.10,"sector":"ETF (=0050 2X)","tag":"core","underlying":"0050","multiplier":2},
    {"symbol":"00830.TW","name":"國泰費城半導體","shares":120,"buy_price":77.95,"close":85.00,"change":1.55,"pct":1.86,"sector":"ETF（費半代理）","tag":"satellite"},
    {"symbol":"2330.TW","name":"台積電","shares":25,"buy_price":2145.6,"close":2270.0,"change":50.0,"pct":2.25,"sector":"半導體","tag":"core"},
    {"symbol":"2337.TW","name":"旺宏電子","shares":100,"buy_price":134.8,"close":172.0,"change":4.0,"pct":2.38,"sector":"記憶體 NOR/NAND","tag":"growth"},
    {"symbol":"3711.TW","name":"日月光投控","shares":86,"buy_price":478.58,"close":548.0,"change":0.0,"pct":0.0,"sector":"封裝測試","tag":"core"},
]

# ---- 1.2 美股持倉（BigGo 2026/05/13 實際收盤價；美東時間 4:00 PM）----
# 持倉：出清 AVGO/AIXI/MULL/SNDU/VSH；QCMU×92（均攤$39.42）；SMH×7；ONDL×20（待出清）；LNOK×3；PLUG×20
US = [
    {"symbol":"SMH","name":"VanEck Semiconductor ETF","shares":7,"buy_price":454.734285,"close":572.46,"change":11.21,"pct":2.00,"sector":"半導體 ETF","tag":"core"},
    {"symbol":"QCMU","name":"Direxion Daily QCOM Bull 2X ETF","shares":92,"buy_price":39.418777,"close":36.48,"change":0.96,"pct":2.70,"sector":"QCOM 2×日槓桿","tag":"satellite","underlying":"QCOM","multiplier":2},
    {"symbol":"ANEL","name":"Defiance 2× Long ANET Daily","shares":55,"buy_price":15.769091,"close":15.56,"change":-0.52,"pct":-3.23,"sector":"ANET 2×（日槓桿）","tag":"satellite","underlying":"ANET","multiplier":2},
    {"symbol":"TSLT","name":"T-Rex 2× Long Tesla Daily","shares":35,"buy_price":18.541122,"close":23.44,"change":1.26,"pct":5.68,"sector":"TSLA 2×","tag":"satellite","underlying":"TSLA","multiplier":2},
    {"symbol":"ONDL","name":"Defiance 2× Long ONDS Daily","shares":20,"buy_price":19.85,"close":13.24,"change":-0.48,"pct":-3.50,"sector":"ONDS 2×","tag":"exit","underlying":"ONDS","multiplier":2},
    {"symbol":"TSMG","name":"Leverage Shares 2× Long TSM Daily","shares":15,"buy_price":36.843334,"close":37.38,"change":0.31,"pct":0.84,"sector":"TSM ADR 2×","tag":"satellite","underlying":"TSM","multiplier":2},
    {"symbol":"LNOK","name":"Defiance 2× Long NOK Daily","shares":3,"buy_price":87.22,"close":87.83,"change":0.61,"pct":0.69,"sector":"Nokia 2×（日槓桿）","tag":"satellite","underlying":"NOK","multiplier":2},
    {"symbol":"PLUG","name":"Plug Power Inc.","shares":20,"buy_price":3.74,"close":3.87,"change":0.13,"pct":3.47,"sector":"氫能／燃料電池","tag":"growth"},
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
        "philosophy": "台股核心 0050/00631L + 2330/2337/3711；美股已重組：**SMH×7股**為核心，**QCMU×92股（2×QCOM）**為最大槓桿部位（均攤成本$39.42，6/24投資人日催化）；**TSLT+ANEL+TSMG** 衛星槓桿群；🆕 **PLUG**（氫能財報轉機）+ **LNOK**（2×Nokia AI網路）小部位；已出清 AVGO/AIXI/MULL/SNDU/VSH。ONDL 待出清。",
        "leverage_map": [
            {"etf":"00631L","underlying":"0050","multiplier":2,"treat_as":"long_term_core"},
            {"etf":"QCMU","underlying":"QCOM","multiplier":2,"treat_as":"underlying_proxy"},
            {"etf":"ANEL","underlying":"ANET","multiplier":2,"treat_as":"underlying_proxy"},
            {"etf":"TSLT","underlying":"TSLA","multiplier":2,"treat_as":"underlying_proxy"},
            {"etf":"TSMG","underlying":"TSM","multiplier":2,"treat_as":"underlying_proxy"},
            {"etf":"LNOK","underlying":"NOK","multiplier":2,"treat_as":"underlying_proxy"},
            {"etf":"ONDL","underlying":"ONDS","multiplier":2,"treat_as":"exit"},
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
            "highlight": "0050／00631L 雙核心強勢；00830 費半代理跟漲；3711／2337 5/11 強勢；2330 隨盤回檔。庫存以 portfolio 為準、報價 BigGo。",
            "verdict": "台股部位與 AI／封測敘事一致；00830 貼費半但權重小，屬衛星。"
        },
        "us": {
            "title": f"🇺🇸 美股 — 修復中 +{round((us_mv_twd - us_cost_twd)/us_cost_twd*100, 1)}%",
            "market_value_twd": us_mv_twd, "cost_twd": us_cost_twd,
            "pnl_twd": us_mv_twd - us_cost_twd,
            "pnl_pct": round((us_mv_twd - us_cost_twd)/us_cost_twd*100, 2),
            "market_value_usd": round(us_mv_usd, 2),
            "cost_usd": round(us_cost_usd, 2),
            "pnl_usd": round(us_mv_usd - us_cost_usd, 2),
            "winners": us_w, "losers": us_l,
            "highlight": "券商 5/12：SMH +30.97%、SNDU +46.4%、TSLT +23.45%、QCMU +11.61%、AVGO +12.25%；ONDL -25.44%、AIXI -62.08%、ANEL -5.95%。**QCOM 曝險僅剩 QCMU（71 股 2×）**；新增 **MULL（2×MU）**、**VSH**。",
            "verdict": "半導體多層槓桿（QCMU/MULL/ANEL/TSLT/TSMG/SNDU）與 SMH 重疊—宜設**總槓桿上限**；正股型核心仍看 AVGO+SMH。"
        }
    },

    "indices": [
        {"name":"S&P 500","code":"SPX","value":7444.25,"change":43.24,"pct":0.58},
        {"name":"NASDAQ","code":"IXIC","value":26558.40,"change":312.60,"pct":1.19},
        {"name":"Dow Jones","code":"DJI","value":49967.80,"change":144.20,"pct":0.29},
        {"name":"SMH(費半ETF)","code":"SMH","value":572.46,"change":11.21,"pct":2.00},
        {"name":"VIX","code":"VIX","value":17.2,"change":-0.6,"pct":-3.37},
        {"name":"台股加權","code":"TWII","value":41751.75,"change":377.25,"pct":0.91},
    ],

    "tw_stocks": TW,
    "us_stocks": US,

    "effective_exposure": [
        {"name":"0050＋00631L（台股核心）","icon":"🇹🇼","components":["0050","00631L ×2 槓桿"],"exposure_twd":420000,"pct_effective":43.0,"long_term":True},
        {"name":"台積電曝險（2330＋TSMG）","icon":"🏭","components":["2330 現股","TSMG 2×"],"exposure_twd":128000,"pct_effective":13.1,"long_term":True},
        {"name":"半導體 ETF（SMH×7＋00830）","icon":"🔌","components":["SMH×7","00830.TW"],"exposure_twd":136300,"pct_effective":13.9,"long_term":True},
        {"name":"QCOM 槓桿 QCMU（×92）","icon":"📱","components":["QCMU 2× 92 股"],"exposure_twd":110400,"pct_effective":11.3,"long_term":False},
        {"name":"Tesla 槓桿 TSLT（×35）","icon":"🚗","components":["TSLT 2×"],"exposure_twd":26200,"pct_effective":2.7,"long_term":False},
        {"name":"ANET 槓桿 ANEL（×55）","icon":"🌐","components":["ANEL 2×"],"exposure_twd":25600,"pct_effective":2.6,"long_term":False},
        {"name":"旺宏電子 2337","icon":"💾","components":["2337 正股"],"exposure_twd":16800,"pct_effective":1.7,"long_term":True},
        {"name":"PLUG 氫能（×20）","icon":"⚗️","components":["PLUG 正股"],"exposure_twd":2440,"pct_effective":0.2,"long_term":False},
        {"name":"LNOK Nokia 2×（×3）","icon":"📡","components":["LNOK 2×"],"exposure_twd":8310,"pct_effective":0.8,"long_term":False},
        {"name":"待出清（ONDL）","icon":"⚠️","components":["ONDL 20股"],"exposure_twd":8440,"pct_effective":0.9,"long_term":False},
    ],

    "underlying_analysis": [
        {
            "ticker":"QCOM","name":"Qualcomm（底層 QCMU×92）","price":212.61,"today_pct":1.1,"in_portfolio_twd":110400,
            "thesis":"**92 股 QCMU（2×QCOM）**為最大美股部位；5/12 -11.4% 後已於5/13反彈+7%回穩；6/24 投資人日揭露超大雲客製矽路線圖為最大催化劑。",
            "pros":["超大雲客製矽Q4 2026出貨確認","車用收入+38% YoY破紀錄","Edge AI Snapdragon龍頭","分析師目標$225-300"],
            "cons":["日槓桿衰減（2× ETF 長持不適合）","92股曝險集中風險","若QCOM跌回$190 QCMU跌至$29"],
            "consensus_target":"Baird $300、Tigress $280、Daiwa $225；目前$212.61約30%折讓","rating":"Buy（多數分析師）","next_catalyst":"6/24 投資人日（最關鍵）；Q3 FY26 財報（7月）","user_action":"🟡 守$39.42均攤成本；QCOM站穩$215+才加碼；跌破$195立即減碼20-25股"
        },
        {
            "ticker":"TSM","name":"TSMC ADR（底層 TSMG×15）","price":411.0,"today_pct":0,"in_portfolio_twd":128000,
            "thesis":"先進製程＋CoWoS 供不應求；2330 正股25股＋TSMG×15 槓桿雙重曝險；5/13 -1.55% 為技術修正",
            "pros":["AI 製程唯一供應商","Q1 EPS NT$22.08歷史新高","全年>30%成長"],
            "cons":["地緣政治","TSMG日槓桿衰減"],
            "consensus_target":"外資 NT$2,288-3,030；建議 TSMG 轉 2330 正股","rating":"Strong Buy","next_catalyst":"7/16 法說","user_action":"🟡 TSMG 考慮賣出換 2330 正股 1 股"
        },
        {
            "ticker":"ANET","name":"Arista Networks（底層 ANEL×55）","price":92.0,"today_pct":1.5,"in_portfolio_twd":25600,
            "thesis":"AI 資料中心 400G/800G 乙太網路龍頭；ANEL 為 2× 日報酬槓桿 ETF",
            "pros":["Strong Buy 共識","AI 網路需求爆發","FY2026 AI 指引$3.5B"],
            "cons":["ANEL 日衰減","估值偏高"],
            "consensus_target":"分析師均值 $175.18；Morningstar FV $190","rating":"Strong Buy","next_catalyst":"ANET Q2 2026 財報","user_action":"🟡 ANEL 小部位短線工具；看好 ANET 可評估轉正股"
        },
        {
            "ticker":"TSLA","name":"Tesla（底層 TSLT×35）","price":426.0,"today_pct":3.8,"in_portfolio_twd":26200,
            "thesis":"TSLT 2× 日槓桿；今日+7.6% 大幅反彈；已獲利+29%",
            "pros":["Robotaxi FSD 進展","能源儲存業務","Optimus 機器人"],
            "cons":["高估值","交付季節性"],
            "consensus_target":"分析師分歧 $250-500","rating":"Hold","next_catalyst":"Q2 2026 交付／毛利","user_action":"🔴 今日+7.6%→賣出10-15股鎖利，留20-25股等後段"
        },
        {
            "ticker":"PLUG","name":"Plug Power（正股×20）","price":3.87,"today_pct":14.5,"in_portfolio_twd":2440,
            "thesis":"氫能燃料電池轉機股；Q1 2026 財報超預期（EPS -0.08 vs -0.09預期）；Project Quantum Leap降本；CEO 承諾 2027 轉盈",
            "pros":["Q1 營收$163M +22%","毛利率大幅改善（-13% vs -55%）","$8B 電解槽訂單管線","HC Wainwright目標$7"],
            "cons":["仍虧損","氫能基礎建設投資緩慢","現金流依賴資本市場"],
            "consensus_target":"B. Riley $5.00、HC Wainwright $7.00、Canaccord $4.00","rating":"分歧（Buy/Neutral）","next_catalyst":"Q2 EBITDAS 進度；電解槽大客戶訂單","user_action":"🟡 20股小倉保留；若站穩$3.75→目標$4-5；跌破$3.20停損"
        },
        {
            "ticker":"NOK","name":"Nokia（底層 LNOK×3）","price":5.3,"today_pct":0.5,"in_portfolio_twd":8310,
            "thesis":"Nokia 企業 5G + AI 網路設備；LNOK 為 Defiance 2× 日槓桿 ETF；小部位押注諾基亞 AI 企業化轉型",
            "pros":["企業5G網路升級潮","AI機房網路需求間接受惠","估值便宜"],
            "cons":["利潤率偏低","競爭激烈（Ericsson/Cisco）","2×日衰減"],
            "consensus_target":"Nokia ADR 約 $5-7 法人目標","rating":"Hold/中性","next_catalyst":"Nokia Q2 2026財報；企業AI合約訂單","user_action":"🟡 3股小試水溫；停損 $75/LNOK；等Nokia AI合約消息才加碼"
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
                {"symbol":"ONDL","name":"ONDS 2X（20股）","view":"虧損-32.6%；本週出清；底層ONDS無反彈催化"},
                {"symbol":"TSMG","name":"TSM 2X（15股）","view":"建議賣出換 2330 正股；消除日槓桿衰減"},
                {"symbol":"ANEL","name":"2×ANET","view":"屬短線槓桿工具；若長抱 ANET 邏輯請考慮正股"},
                {"symbol":"LNOK","name":"2×Nokia（3股）","view":"小倉觀察；若6個月無Nokia重大合約消息→停損出場"},
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
            "title": "📆 5/15（週五）台股開盤策略",
            "macro_context": [
                "📌 台股5/14大漲+377pts(+0.91%)收41,752；台積電+50元收2,270；日月光平盤548；旺宏NOR主題延續；成交1.22兆",
                "📌 美股S&P 7,444(+0.58%歷史新高)；NASDAQ +1.2%歷史新高；SMH 5/13收$572.46(+2%)；費半強勢",
                "📌 川習峰會正向收場：美中貿易「互利共贏」；300億美元商品關稅互降談判中；習提台灣警告",
                "📌 QCMU 5/13實際收盤$36.48(+2.7%，非盤中高點$37.97)；盤前5/14已跌-6.83%至$33.99，需密切監控",
                "📌 NVDA 5/20財報為下一大催化：若EPS>$4.50且指引強→SMH挑戰$620-650；5/15-5/19最後布局視窗",
            ],
            "morning_plan": [
                {"step":1,"action":"9:00 確認美股夜盤方向","detail":"台股5/14已大漲；5/15開盤預期高開後整理；旺宏若量縮→觀察165-170支撐"},
                {"step":2,"action":"9:10 台積電(2330)策略","detail":"🟢 昨收2,270(+50)；外資目標2,288-3,030；繼續持有；若5/15開高走低2,250→伺機加零股1-2股"},
                {"step":3,"action":"9:30 旺宏(2337)觀察","detail":"🔥 5/13漲停+5/14延續；NOR主題；若量縮回測165-170→持有等待；量持續放大→持有目標250；停損155"},
                {"step":4,"action":"美股QCMU盤前注意（台灣時間晚上9:30）","detail":"🔴 QCMU盤前$33.99(-6.83%)=QCOM出現疑似利空；若美股開盤QCOM繼續跌→考慮減碼20-25股；確認跌因"},
                {"step":5,"action":"10:30 日月光(3711)策略","detail":"🟢 昨平盤548；CoWoS封裝；若5/15開高站穩548→持有；回520-530可加1股；目標580-620"},
                {"step":6,"action":"ONDL繼續掛出清","detail":"🔴 掛GTC限價$13.80出清20股；每日衰減中；本週最後一天盤中確認成交"},
                {"step":7,"action":"NVDA 5/20財報前布局","detail":"🟢 SMH 7股核心不動；5/15-5/19 SMH$560+可考慮加第8股（若資金允許）"},
            ],
            "watch_list_for_tomorrow": [
                {"symbol":"2330.TW","name":"台積電","buy_zone":"2,230-2,250","target":"2,500-2,700","action":"5/14收2,270；外資目標2,288-3,030；AI製程核心；逢回2,230-2,250加零股"},
                {"symbol":"2337.TW","name":"旺宏電子","buy_zone":"165-172","target":"250-300","action":"NOR缺貨主題；量縮回測165-172為進場區；停損155"},
                {"symbol":"3711.TW","name":"日月光投控","buy_zone":"520-535","target":"580-620","action":"CoWoS封裝；平盤後若回520可加；目標580-620"},
                {"symbol":"SMH","name":"VanEck SMH","buy_zone":"$558-572","target":"$620-660","action":"NVDA 5/20前布局；7股核心不動；$558-572加第8股"},
                {"symbol":"3661.TW","name":"世芯-KY","buy_zone":"1,150-1,200","target":"1,600-2,000","action":"AI ASIC設計龍頭；新進潛力股；小量試倉觀察"},
                {"symbol":"ORCL","name":"Oracle","buy_zone":"$180-188","target":"$230-260","action":"OCI AI雲端；回測$180-188為進場機會；目標$230"},
            ],
            "avoid_list": [
                {"symbol":"ONDL","name":"ONDS 2×","reason":"虧損持續惡化；底層ONDS無反彈催化；盡快出清"},
                {"symbol":"TSMG","name":"TSM 2×","reason":"日槓桿衰減；建議賣出換2330正股更有效率"},
                {"symbol":"QCMU（謹慎）","name":"2×QCOM","reason":"盤前-6.83%疑似出現未知利空；5/15開盤前先確認QCOM跌因，再決定是否減碼"},
            ],
            "risk_alerts": [
                "🚨 QCMU盤前-6.83%($33.99)：QCOM疑似有利空；92股×2倍=巨大風險；5/15美股開盤第一時間確認原因",
                "🚨 習近平台灣警告：「處理不當可能引發衝突」；地緣溢價長期存在於台股；注意突發消息",
                "🚨 美國通膨數據5/14超預期：Fed降息時程再度延後；高估值科技股面臨持續壓力",
                "🚨 NVDA 5/20財報：若EPS指引低於預期→SMH可能跌10%；勿在財報前重倉追高",
                "🚨 美中貿易談判：僅有象徵性聲明，無具體協議日期；後續執行存在不確定性",
                "🚨 ONDL 20股：每日持續衰減；必須本週出清",
            ],
            "one_line": "5/15：台美股雙雙在歷史高位；重點是監控QCMU盤前暴跌原因，NVDA5/20財報前布局SMH，以及持續推進ONDL出清。"
        }
    },

    "news": [
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
            {"symbol":"0050.TW","name":"元大台灣50","sell":0,"hold":5,"buy":14,"label":"核心指數"},
            {"symbol":"00631L.TW","name":"台灣50正2","sell":0,"hold":7,"buy":12,"label":"槓桿長持"},
            {"symbol":"2330.TW","name":"台積電","sell":0,"hold":6,"buy":13,"label":"CoWoS"},
            {"symbol":"3711.TW","name":"日月光","sell":0,"hold":6,"buy":13,"label":"先進封測"},
            {"symbol":"00830.TW","name":"費城半導體 ETF","sell":0,"hold":12,"buy":7,"label":"費半代理"},
            {"symbol":"SMH","name":"SMH","sell":0,"hold":4,"buy":15,"label":"核心 ETF +2.2%"},
            {"symbol":"QCMU","name":"2×QCOM","sell":6,"hold":9,"buy":4,"label":"🔄 均攤中，今日反彈+6.9%"},
            {"symbol":"ANEL","name":"2×ANET","sell":5,"hold":10,"buy":4,"label":"AI 網路衛星"},
            {"symbol":"TSMG","name":"2×TSM","sell":8,"hold":8,"buy":3,"label":"⚠️ 建議轉正股"},
            {"symbol":"TSLT","name":"2×TSLA","sell":4,"hold":9,"buy":6,"label":"🔥 今日+7.6%，鎖利"},
            {"symbol":"LNOK","name":"2×Nokia","sell":7,"hold":9,"buy":3,"label":"🆕 小倉 Nokia AI"},
            {"symbol":"PLUG","name":"Plug Power","sell":3,"hold":8,"buy":8,"label":"🆕 財報超預期 +14.5%"},
            {"symbol":"ONDL","name":"ONDL","sell":16,"hold":2,"buy":1,"label":"🔴 待出清 20 股"},
            {"symbol":"2337.TW","name":"旺宏","sell":1,"hold":3,"buy":15,"label":"🔥 漲停+9.8%，NOR主題"},
        ]
    },

    "picks": [
        {"rank":1,"ticker":"2337","name":"旺宏電子","market":"TW","price":172,"target_low":250,"target_high":300,"upside_pct":57.0,"thesis":"NOR Flash「最後供應商」缺貨爆發；大廠撤出2D NAND；AI邊緣推理+AI-in-Car需求；5/13漲停+9.8%；本土機構目標300元；5/14 成交量放大NOR主題延續","type":"個股"},
        {"rank":2,"ticker":"3661","name":"世芯-KY","market":"TW","price":1200,"target_low":1600,"target_high":2000,"upside_pct":49.2,"thesis":"AI ASIC客製化設計龍頭（HyperScaler訂單）；蘋果/Google/Meta超大雲ASIC單一供應商；技術護城河高；AI推論晶片需求指數爆發；毛利率40-50%護持","type":"個股"},
        {"rank":3,"ticker":"2454","name":"聯發科","market":"TW","price":3405,"target_low":4200,"target_high":4800,"upside_pct":26.6,"thesis":"Edge AI SoC龍頭；Dimensity AI旗艦系列手機市占攀升；5/14技術回測3,405為進場機會；AI換機潮+車用AI雙引擎；外資目標4,200+","type":"個股"},
        {"rank":4,"ticker":"AMD","name":"Advanced Micro Devices","market":"US","price":165,"target_low":210,"target_high":240,"upside_pct":33.3,"thesis":"MI300X AI GPU持續搶食NVDA份額（資料中心AI推論）；EPYC伺服器CPU市占擴大；美中貿易和解受惠晶片出口；估值相對合理；≤$300 ✓","type":"個股"},
        {"rank":5,"ticker":"ORCL","name":"Oracle","market":"US","price":186.83,"target_low":230,"target_high":260,"upside_pct":27.7,"thesis":"OCI多租戶雲端AI需求爆發；Q1雲端業務超預期；Moderate Buy(42位分析師)；AI向量DB/RAG基礎建設指定平台；Oppenheimer目標$235；≤$300 ✓","type":"個股"},
    ],

    # ===== actions（A/B 用 strategy/stop/target；C 用 action/reason）=====
    "actions": {
        "A": [
            {"symbol":"0050.TW","name":"元大台灣50","price":95.5,"target":"100-105","stop":88,"strategy":"壓艙石核心；長期定期定額不動；5/14 美股反彈應跟漲回補"},
            {"symbol":"2330.TW","name":"台積電","price":2220,"target":"2,400-2,600","stop":2050,"strategy":"Q1 EPS NT$22.08歷史新高；毛利率66.2%；全年>30%成長；5/13 -1.55%為技術修正，5/14 預期回升"},
            {"symbol":"3711.TW","name":"日月光投控","price":548,"target":"580-620","stop":500,"strategy":"CoWoS封裝供不應求；Q1 EPS 3.24元超預期；等回測520-530可加碼"},
            {"symbol":"SMH","name":"VanEck 半導體（7股）","price":573.62,"target":"$620-660","stop":520,"strategy":"核心ETF × 7 股；今日+2.2%強勢；美股半導體主軸不動；6/24 QCOM投資人日前不減"},
            {"symbol":"00631L.TW","name":"台灣50正2","price":31.85,"target":"34-37","stop":27,"strategy":"與0050長期核心；槓桿放大下行幅度注意，勿過度集中"},
            {"symbol":"TSLT","name":"T-Rex 2×Tesla","price":23.875,"target":"$26-28","stop":19,"strategy":"🔴 已獲利+29%，今日再+7.6%→ 賣出10-15股（約$238-$358）鎖利，留20-25股等後段行情"},
        ],
        "B": [
            {"symbol":"2337.TW","name":"旺宏電子","price":168,"target":"250-300","stop":140,"strategy":"🔥 昨漲停+9.8%；NOR Flash缺貨行情持續；5/14等回測158-165支撐再加碼；目標300元"},
            {"symbol":"QCMU","name":"2×QCOM（92股）","price":37.97,"target":"$42-48（QCOM $215-225）","stop":34,"strategy":"均攤成本$39.42；今日+6.9%反彈中；守住$39.42成本線；QCOM站穩$215→轉多信號；6/24投資人日為最大催化；跌破$34（QCOM $185）減碼20-25股"},
            {"symbol":"ANEL","name":"2×ANET","price":16.06,"target":"$20-25","stop":12.5,"strategy":"ANET資料中心400/800G受惠；AI網路需求爆發；等ANET正股站穩$95再評估"},
            {"symbol":"TSMG","name":"TSM 2×","price":37.52,"target":"$42-46","stop":33,"strategy":"⚠️ 建議逐步賣出轉換 2330 正股 1 股；日槓桿衰減問題"},
            {"symbol":"PLUG","name":"Plug Power","price":3.87,"target":"$4.00-5.00","stop":3.20,"strategy":"🆕 Q1財報超預期；B.Riley目標$5；HC Wainwright $7；觀察能否站穩$3.75；中線看$5-7"},
            {"symbol":"00830.TW","name":"費城半導體ETF","price":83.45,"target":"90-98","stop":75,"strategy":"費半代理；SMH今日+2.2%利好；5/14 跟漲預期"},
            {"symbol":"LNOK","name":"2×Nokia ETF","price":87.83,"target":"$95-110","stop":75,"strategy":"🆕 小倉3股；停損$75（-14%）；等諾基亞企業5G/AI合約訂單消息才評估加碼"},
        ],
        "C": [
            {"symbol":"ONDL","name":"ONDS 2×（20股）","price":13.38,"action":"🔴 繼續減碼；掛 GTC 限價 $13.80；目標出清至0","reason":"虧損-32.6%；底層ONDS業務不透明；日槓桿持續衰減，無反彈催化劑"},
            {"symbol":"TSMG","name":"TSM 2× ETF","price":37.52,"action":"⚠️ 考慮賣出換 2330 正股","reason":"日槓桿衰減 + TSM 正股上漲才有意義；持有成本$36.84，目前小幅獲利；建議TSMG→2330正股1股長持"},
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
            {"label":"台股核心（0050+00631L+2330+3711+2337+00830）","value":62.7},
            {"label":"美股核心 ETF（SMH×7）","value":15.6},
            {"label":"美股槓桿群（QCMU×92+ANEL+TSLT+TSMG+LNOK）","value":19.9},
            {"label":"新倉成長（PLUG）","value":0.3},
            {"label":"待出清（ONDL）","value":1.0},
            {"label":"現金","value":0.5},
        ],
        "target": [
            {"label":"台股核心","value":60},
            {"label":"美股核心 ETF","value":18},
            {"label":"美股槓桿","value":14},
            {"label":"成長新倉","value":2},
            {"label":"高風險／待出清","value":0},
            {"label":"現金","value":6},
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
