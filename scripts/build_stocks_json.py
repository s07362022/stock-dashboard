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

FX = 31.425                                      # 匯率 USD→TWD（2026/05/09 參考）
UPDATE_NOTE = "BigGo 2026/05/08 盤中~14:12 EDT 更新：QCOM +7.46%、SMH +4.51%、AVGO +3.78%、ANET -1.45%、AIXI -15.16%、TSMG -3.0%；QCOM Q2 FY2026 EPS $6.88 超預期 + 超大雲客製矽勝案推動；台股 5/8 收盤 0050 $97(-0.72%)、2330 $2290(-0.87%)；US-Iran 和平談判推升市場至歷史新高。"

# ---- 1.1 台股持倉（依 BigGo 2026/05/08 UTC+8 收盤）----
TW = [
    {"symbol":"0050.TW","name":"元大台灣50","shares":3010,"buy_price":64.1,"close":97.0,"change":-0.7,"pct":-0.72,"sector":"ETF（核心，長期）","tag":"core"},
    {"symbol":"00631L.TW","name":"元大台灣50正2","shares":4150,"buy_price":28.23,"close":32.47,"change":0.0,"pct":0.0,"sector":"ETF (=0050 2X)","tag":"core","underlying":"0050","multiplier":2},
    {"symbol":"00830.TW","name":"國泰費城半導體","shares":120,"buy_price":77.95,"close":78.6,"change":-0.95,"pct":-1.19,"sector":"ETF（費半代理）","tag":"satellite"},
    {"symbol":"2330.TW","name":"台積電","shares":25,"buy_price":2145.6,"close":2290.0,"change":-20,"pct":-0.87,"sector":"半導體","tag":"core"},
    {"symbol":"2337.TW","name":"旺宏電子","shares":100,"buy_price":134.8,"close":153.0,"change":0,"pct":0,"sector":"記憶體 NOR/NAND","tag":"growth"},
    {"symbol":"3711.TW","name":"日月光投控","shares":86,"buy_price":478.58,"close":516.0,"change":0,"pct":0,"sector":"封裝測試","tag":"core"},
]

# ---- 1.2 美股持倉（依 BigGo 2026/05/08 EDT 14:12 盤中）----
US = [
    {"symbol":"ANEL","name":"Defiance 2× Long ANET Daily","shares":50,"buy_price":15.84,"close":15.47,"change":-0.58,"pct":-3.61,"sector":"ANET 2×（日槓桿）","tag":"satellite","underlying":"ANET","multiplier":2},
    {"symbol":"QCOM","name":"Qualcomm","shares":1,"buy_price":226.88,"close":217.67,"change":15.12,"pct":7.46,"sector":"半導體／邊緣AI／資料中心","tag":"core"},
    {"symbol":"AIXI","name":"Xiao-I Corp","shares":70,"buy_price":1.388027,"close":0.6134,"change":-0.1096,"pct":-15.16,"sector":"AI 軟體（高風險）","tag":"exit"},
    {"symbol":"ONDL","name":"Defiance 2× Long ONDS Daily","shares":30,"buy_price":19.85,"close":13.2,"change":0,"pct":0,"sector":"ONDS 2×","tag":"exit","underlying":"ONDS","multiplier":2},
    {"symbol":"AVGO","name":"Broadcom","shares":5,"buy_price":382.957429,"close":428.15,"change":15.59,"pct":3.78,"sector":"AI 半導體龍頭","tag":"core"},
    {"symbol":"QCMU","name":"QCMU（待釐清）","shares":46,"buy_price":39.030381,"close":40.16,"change":0,"pct":0,"sector":"結構型／追蹤部位","tag":"satellite"},
    {"symbol":"SMH","name":"VanEck Semiconductor ETF","shares":6,"buy_price":439.213333,"close":564.485,"change":24.385,"pct":4.51,"sector":"半導體 ETF","tag":"core"},
    {"symbol":"SNDU","name":"T-Rex 2× Long SNDK Daily","shares":3,"buy_price":80.633942,"close":110.2,"change":0,"pct":0,"sector":"SNDK 2×","tag":"growth","underlying":"SNDK","multiplier":2},
    {"symbol":"TSLT","name":"T-Rex 2× Long Tesla Daily","shares":30,"buy_price":17.781309,"close":21.82,"change":0,"pct":0,"sector":"TSLA 2×","tag":"satellite","underlying":"TSLA","multiplier":2},
    {"symbol":"TSMG","name":"Leverage Shares 2× Long TSM Daily","shares":30,"buy_price":36.843334,"close":39.18,"change":-1.21,"pct":-3.0,"sector":"TSM ADR 2×","tag":"core","underlying":"TSM","multiplier":2},
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
        "philosophy": "台股核心 0050/00631L + 2330/3711；美股半導體與槓桿衛星並存。**ANEL 為 2×ANET 日槓桿**，不等同長抱 ANET 正股。AIXI／ONDL 為戰術性虧損部位（使用者意向：反彈後賣）。",
        "leverage_map": [
            {"etf":"00631L","underlying":"0050","multiplier":2,"treat_as":"long_term_core"},
            {"etf":"ANEL","underlying":"ANET","multiplier":2,"treat_as":"underlying_proxy"},
            {"etf":"TSLT","underlying":"TSLA","multiplier":2,"treat_as":"underlying_proxy"},
            {"etf":"TSMG","underlying":"TSM","multiplier":2,"treat_as":"underlying_proxy"},
            {"etf":"SNDU","underlying":"SNDK","multiplier":2,"treat_as":"underlying_proxy"},
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
            "highlight": "0050／00631L 雙核心強勢；新增 00830 費半代理；2330／3711／2337 均獲利。庫存以 2026/05/09 截圖為準。",
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
            "highlight": "BigGo 5/8：QCOM +9%（資料中心／客製晶片敘事）、SMH +3.8%、AVGO +4.2%；AIXI 弱勢；ONDL 仍深虧。",
            "verdict": "半導體與 QCOM 事件驅動強；槓桿標的（ANEL/ONDL/TSLT/SNDU/TSMG）留意衰減與波動。"
        }
    },

    "indices": [
        {"name":"S&P 500","code":"SPX","value":7391.10,"change":54.5,"pct":0.74},
        {"name":"NASDAQ","code":"IXIC","value":26144.57,"change":341.6,"pct":1.32},
        {"name":"Dow Jones","code":"DJI","value":49621.33,"change":24.8,"pct":0.05},
        {"name":"SMH(費半ETF)","code":"SMH","value":564.49,"change":24.39,"pct":4.51},
        {"name":"VIX","code":"VIX","value":15.8,"change":-0.6,"pct":-3.66},
        {"name":"台股加權","code":"TWII","value":38900,"change":-100,"pct":-0.26},
    ],

    "tw_stocks": TW,
    "us_stocks": US,

    "effective_exposure": [
        {"name":"0050＋00631L（台股核心）","icon":"🇹🇼","components":["0050","00631L ×2 槓桿"],"exposure_twd":430000,"pct_effective":52.0,"long_term":True},
        {"name":"台積電／TSM 曝險","icon":"🏭","components":["2330 現股","TSMG 2×"],"exposure_twd":145000,"pct_effective":17.5,"long_term":True},
        {"name":"半導體 ETF（SMH＋00830）","icon":"🔌","components":["SMH","00830.TW"],"exposure_twd":125000,"pct_effective":15.0,"long_term":True},
        {"name":"Broadcom AVGO","icon":"💎","components":["AVGO"],"exposure_twd":67500,"pct_effective":8.2,"long_term":True},
        {"name":"Qualcomm QCOM","icon":"📱","components":["QCOM"],"exposure_twd":6900,"pct_effective":0.8,"long_term":True},
        {"name":"記憶體／槓桿 SNDU","icon":"💾","components":["SNDU 2×"],"exposure_twd":35000,"pct_effective":4.2,"long_term":False},
        {"name":"Tesla 槓桿 TSLT","icon":"🚗","components":["TSLT 2×"],"exposure_twd":20500,"pct_effective":2.5,"long_term":False},
        {"name":"ANET 槓桿 ANEL","icon":"🌐","components":["ANEL 2×"],"exposure_twd":24100,"pct_effective":2.9,"long_term":False},
        {"name":"待出清／高風險","icon":"⚠️","components":["AIXI","ONDL"],"exposure_twd":18000,"pct_effective":2.2,"long_term":False},
    ],

    "underlying_analysis": [
        {
            "ticker":"AVGO","name":"Broadcom","price":429.71,"today_pct":4.16,"in_portfolio_twd":67500,
            "thesis":"AI 客製 ASIC + 網路基礎設施雙引擎；財報與指引為多頭主軸",
            "pros":["AI 相關營收占比提升","客戶涵蓋超大雲","現金流與回購"],
            "cons":["估值不低","單日波動大"],
            "consensus_target":"情境 $430-650（請以法人最新為準）","rating":"Buy","next_catalyst":"下一財報／指引","user_action":"🟢 持有 5 股"
        },
        {
            "ticker":"TSM","name":"TSMC ADR","price":398.0,"today_pct":0,"in_portfolio_twd":70000,
            "thesis":"先進製程＋CoWoS 供不應求；2330＋TSMG 雙重曝險",
            "pros":["AI 資本開支循環","市占領先"],
            "cons":["地緣","資本支出高峰"],
            "consensus_target":"ADR 級距請對照外資最新","rating":"Strong Buy","next_catalyst":"季報法說","user_action":"🟢 2330 為主、TSMG 為槓桿衛星"
        },
        {
            "ticker":"QCOM","name":"Qualcomm","price":217.67,"today_pct":7.46,"in_portfolio_twd":6843,
            "thesis":"Q2 FY2026 EPS $6.88（超預期 173%）+ 超大雲（hyperscaler）客製矽晶片 Q4 2026 出貨；資料中心題材急拉；6/24 投資人日待確認細節",
            "pros":["超大雲客製 ASIC 勝案（首次）","車用 +50% YoY","授權+晶片雙引擎","EPS 超預期彈性高"],
            "cons":["手機業務仍弱（存儲器價格高）","Q3 指引 $9.6B 低於共識","股價已遠超分析師目標 $168","執行風險：客製案多代期限與量能"],
            "consensus_target":"法說前共識 $168.50；RBC 升至 $175；Citi/JPM/WFC 至 $160；股價 $217 已遠超多數目標—升評追價窗口","rating":"Hold→升評中（分歧）","next_catalyst":"6/24 投資人日（資料中心+實體AI）、客製矽初始出貨進度","user_action":"🟡 1 股持有：股價已高於共識，設停利 $240 / 停損 $190"
        },
        {
            "ticker":"ANET","name":"Arista Networks","price":139.69,"today_pct":-1.45,"in_portfolio_twd":24330,
            "thesis":"資料中心高速 Ethernet 400G/800G 龍頭；FY2026 AI 銷售指引 $35 億（全年 $115 億）；分析師均值 $175.18 代表 ~25% 上行空間；**ANEL 為 2×日報酬槓桿 ETF**，長持損耗大",
            "pros":["17 位分析師 Strong Buy 共識","FY2026 AI 營收指引$3.5B (+26.98%)","毛利與淨利率優秀","目標價 $175-200 有 25-43% 上行"],
            "cons":["槓桿 ETF（ANEL）日衰減","估值偏高 Forward P/E ~60","市場期待高、稍弱就受壓"],
            "consensus_target":"均值 $175.18（範圍 $112-200）；Morningstar FV $190","rating":"Strong Buy（17 位一致）","next_catalyst":"ANET Q2 2026 財報；AI 網路訂單擴大","user_action":"🟡 ANEL 短線槓桿：若看好 ANET 25%+ 上行，可留；長期改用 ANET 正股"
        },
        {
            "ticker":"SNDK","name":"SanDisk","price":1200,"today_pct":0,"in_portfolio_twd":35000,
            "thesis":"NAND／儲存週期；SNDU 2× 放大底層波動",
            "pros":["儲存漲價敘事可延續"],
            "cons":["週期性","2× 槓桿耗損"],
            "consensus_target":"參考外資 NAND 報告","rating":"Buy","next_catalyst":"記憶體報價／財報","user_action":"🟡 SNDU 小倉波段"
        },
        {
            "ticker":"TSLA","name":"Tesla","price":400,"today_pct":0,"in_portfolio_twd":20500,
            "thesis":"TSLT 僅為 2× 曝險工具，與長期基本面連動非線性",
            "pros":["Robotaxi／能源敘事"],
            "cons":["槓桿耗損","股價高波動"],
            "consensus_target":"分歧大","rating":"Hold","next_catalyst":"交付與毛利","user_action":"🟡 嚴格資金比重"
        },
    ],

    # ===== horizon_views（必須匹配渲染函式期望）=====
    "horizon_views": {
        "short_term_1m": {
            "title": "🔭 短線（~1 個月）情境預測",
            "intro": "5/8 美股：費半 SMH 創新高（+4.51%），QCOM 財報 + 超大雲勝案（+7.46%），AVGO（+3.78%），Intel +16%。台股 5/8 收小跌但美股強勢可望週一帶動。槓桿 ETF（ANEL、ONDL、TSLT、SNDU）注意**日衰減**。美伊和平推動油價下行 → 通膨壓力減輕利多。",
            "tw_index": {
                "current": 38900,
                "bull": 40500, "p_bull": 45,
                "base": 39300, "p_base": 40,
                "bear": 37500, "p_bear": 15,
                "scenario": "多頭：美股費半新高帶動 + 美伊和平；基本：高檔整理；空頭：和談破裂油價急升或 QCOM 投資人日失望",
            },
            "forecasts": [
                {"symbol":"0050.TW","name":"元大台灣50","current":97.0,"bull":102,"base":98,"bear":92,"view":"費半創新高連動；核心壓艙石；100 為中期目標"},
                {"symbol":"2330.TW","name":"台積電","current":2290,"bull":2500,"base":2350,"bear":2100,"view":"外資目標 2,288-3,030；Q2 指引 $39-40B；7/16 法說前佈局"},
                {"symbol":"2337.TW","name":"旺宏","current":153,"bull":175,"base":160,"bear":138,"view":"Q1 EPS 轉正；投信賣壓待消化後可回測"},
                {"symbol":"3711.TW","name":"日月光","current":516,"bull":560,"base":530,"bear":485,"view":"LEAP/CoWoS 受惠；Q1 超預期；凱基 588"},
                {"symbol":"ANET","name":"Arista Networks","current":139.69,"bull":175,"base":155,"bear":125,"view":"Strong Buy 17 分析師；均值 $175；ANEL 槓桿可博至 $155"},
                {"symbol":"QCOM","name":"Qualcomm","current":217.67,"bull":250,"base":220,"bear":190,"view":"超大雲勝案推動；6/24 投資人日為短期關鍵；股價已超大多數目標"},
                {"symbol":"AVGO","name":"Broadcom","current":428.15,"bull":500,"base":450,"bear":395,"view":"AI 主軸；Morningstar FV $500；Q2 $22B 兌現待確認"},
                {"symbol":"SMH","name":"VanEck SMH","current":564.49,"bull":600,"base":565,"bear":520,"view":"費半創新高後可能短暫獲利了結；守 530"},
                {"symbol":"SNDK","name":"SanDisk","current":1240,"bull":1350,"base":1200,"bear":950,"view":"NAND 強勢延續；注意波動"},
                {"symbol":"TSLA","name":"Tesla","current":395,"bull":450,"base":400,"bear":320,"view":"TSLT 2X 緊盯；Robotaxi 進度催化"},
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
                {"symbol":"AIXI","name":"Xiao-I","view":"深虧仙股；使用者：等反彈賣—仍建議設**時間停損**"},
                {"symbol":"ONDL","name":"ONDS 2X","view":"底層弱勢時 2×失血；使用者：等反彈賣"},
                {"symbol":"ANEL","name":"2×ANET","view":"屬短線槓桿工具；要長抱網路龍頭請對照 ANET 正股"},
            ]
        },
        "peak_decision": {
            "title": "❓ 加碼 / 持有 / 賣？— 我的判斷",
            "current_status": "2026/05/09：庫存已與券商截圖對齊；美股半導體領漲（BigGo 5/8），台股核心部位仍為正報酬。",
            "verdict": "『核心（0050／2330／AVGO／SMH）續抱＋槓桿衛星控比重』；**AIXI／ONDL** 依使用者策略『反彈再賣』，仍須預設時間停損與流動性風險。",
            "actions": [
                {"type":"🟢 加碼／續抱","items":[
                    "00631L 與 0050 核心長抱策略不變",
                    "AVGO／SMH：趨勢未破前續抱；分批逢高鎖利可選擇",
                    "2330／3711：基本面＋封測敘事未破線前續抱",
                ]},
                {"type":"🟡 持有（控槓桿）","items":[
                    "ANEL：等同 **2×ANET 短線曝險**；不宜用『長期買 ANET』心智持有",
                    "TSLT／TSMG／SNDU：守停損與部位上限",
                    "QCOM 1 股：事件波動大，設停利／回撤門檻",
                ]},
                {"type":"🔴 反彈調節／出清","items":[
                    "AIXI：等政策／流動性反彈分批降（依使用者：等回漲再賣）",
                    "ONDL：反彈沿著壓力減碼（依使用者：等回漲再賣）；底層 ONDS 疲弱時 2×仍可能持續失血",
                ]},
                {"type":"⚫ 結構替代","items":[
                    "若確信 ANET 長多但厭惡槓桿：可評估 **ANET 正股**取代 ANEL（非建議買賣，僅配置邏輯）",
                ]},
            ],
            "cash_target": "維持現金緩衝；槓桿標的不宜再加總曝險。"
        },
        "tomorrow_tw_strategy": {
            "title": "📆 星期一（5/11）台股開盤策略",
            "macro_context": [
                "📌 5/8 美股（截至盤中）：S&P 500 7,391（+0.74%）、NASDAQ 26,145（+1.32%）— 雙雙創歷史新高；連第 6 週上漲；83% S&P 500 Q1 EPS 超預期",
                "📌 5/8 半導體強勁：SMH $564.49（+4.51% 創新高）；Intel +16%（Apple 代工談判）、AMD +8%、Micron +13%；費半指數（SOX）創新高",
                "📌 QCOM Q2 FY26 EPS $6.88 超預期 173%；超大雲客製矽 Q4 2026 出貨確認；股價 +7.46% 至 $217.67",
                "📌 美伊和平談判：伊朗回應美方備忘錄，荷姆茲海峽可望重開 → 布蘭特原油 ~$98（5/6 大跌 10.6%）；美股由油價受益並反映風險偏好改善",
                "📌 就業數據強勁：4 月新增 115K（預期 65K）；失業率穩 4.3%；Fed 今年降息預期最早 9 月",
                "📌 台股 5/8 收盤：0050 $97（-0.72%）、2330 $2,290（-0.87%）— 台灣加權指數 ~38,900；台股相對美股弱勢，週一美股新高或帶動跳空開高",
            ],
            "morning_plan": [
                {"step":1,"action":"9:00-9:15 觀察開盤量能","detail":"美股 5/8 連續 6 週新高；台股預期跳空開高；若 +1% 以上 → 觀察量能確認；SMH 創新高帶動 00830、2330 等"},
                {"step":2,"action":"9:00 立即評估 AIXI 賣單（美股）","detail":"🔴 AIXI $0.6134（-15.16% 今日）；70 股 × $0.6134 ≈ $43；繼續等反彈不現實 → 設 $0.75 GTC 賣單，或直接市價止損"},
                {"step":3,"action":"9:30 評估 ONDL 出清（美股）","detail":"🔴 ONDL $13.20（-33.5% 損失）；底層 ONDS 疲弱；等反彈至 $14.50-15 再設 GTC；注意流動性"},
                {"step":4,"action":"10:00 觀察台積電 2330","detail":"🟢 外資目標 2,288-3,030；現價 2,290 已在最低目標；若開盤站穩 2,250 → 持有；若回 2,200 → 考慮加 1 股"},
                {"step":5,"action":"10:30 觀察日月光 3711","detail":"🟢 CoWoS+LEAP 敘事；Q1 EPS 3.24 超預期；目標凱基 588；若回 ≤500 → 考慮加 1 股"},
                {"step":6,"action":"11:00 觀察 ANEL 決策","detail":"🟡 ANEL $15.47（ANET $139.69）；ANET 分析師均值 $175.18（+25% 上行）；小部位（$773）→ 若 ANET 近期有財報催化劑則續持；否則設停損 $13"},
                {"step":7,"action":"收盤前評估 QCOM","detail":"🟡 QCOM $217.67；已遠超分析師均值 $168；6/24 投資人日前暫觀望；1 股設停利 $240 / 停損 $195"},
            ],
            "watch_list_for_tomorrow": [
                {"symbol":"2330.TW","name":"台積電","buy_zone":"2,200-2,250","target":"2,400-3,030","action":"AI 製程核心；回檔加 1 股；外資最低目標 7%+ 折讓"},
                {"symbol":"3711.TW","name":"日月光","buy_zone":"500-510","target":"540-660","action":"LEAP CoWoS 受惠；凱基 588；回 500 以下加 1 股"},
                {"symbol":"AVGO","name":"Broadcom","buy_zone":"$415-425","target":"$480-500","action":"AI 主軸；Morningstar FV $500；今日 $428 逢回可考慮"},
                {"symbol":"ANET","name":"Arista Networks","buy_zone":"$135-140","target":"$175-200","action":"Strong Buy 共識；比持有 ANEL 更直接，可評估替換"},
                {"symbol":"6669.TW","name":"緯穎","buy_zone":"4,700-4,800","target":"5,500-6,700","action":"AI 伺服器龍頭；野村目標 6,670；觀察標的"},
            ],
            "avoid_list": [
                {"symbol":"AIXI","name":"Xiao-I","reason":"今日 -15.16%；仙股；虧損 -55%；繼續等反彈風險極大"},
                {"symbol":"ONDL","name":"ONDS 2X","reason":"底層 ONDS 疲弱；-33.5% 損失；注意流動性"},
                {"symbol":"ANEL","name":"2×ANET","reason":"槓桿日衰減；不宜追加；小部位可留博短期 ANET 上行"},
            ],
            "risk_alerts": [
                "🚨 美伊和平談判破局：油價可能急反彈至 $115+；半導體將承壓",
                "🚨 QCOM 股價大幅高於分析師共識 $168：若 6/24 投資人日不如預期 → 急跌風險",
                "🚨 Fed 若 9 月前不降息（核心 PCE 仍 3.1%）：高估值科技股（ANET P/E ~60）受壓",
                "🚨 台股加權若跌破 38,000（心理支撐）：短線轉弱",
                "🚨 AIXI 流動性風險：極小市值（$1,088 萬）→ 賣單可能無法執行",
            ],
            "one_line": "5/11 週一：順著美股費半創新高 + QCOM/AVGO 強勢，觀察台股是否跟上；主軸是『AIXI/ONDL 設單出場 + 台積/日月光/AVGO 逢回評估加碼 + ANEL 設停損防守』"
        }
    },

    "news": [
        {"date":"2026-05-08","category":"美股大盤","title":"S&P 500 (+0.74%) 7,391 / NASDAQ (+1.32%) 26,145 / Dow (+0.05%) 49,621 — 創歷史新高；美股連 6 週上漲；83% S&P 500 公司 Q1 EPS 超預期","impact":"positive","source":"Yahoo Finance / Marketscreener"},
        {"date":"2026-05-08","category":"半導體","title":"費半 ETF SMH +4.51%（$564.49）創新高；Intel +16%（Apple 晶片代工談判）、AMD +8%、Micron +13%、NVDA +2.3%","impact":"positive","source":"BigGo / Motley Fool"},
        {"date":"2026-05-08","category":"美股","title":"QCOM BigGo 盤中 $217.67（+7.46%）；Q2 FY2026 EPS $6.88 超預期 173%；超大雲客製矽 Q4 2026 初出貨","impact":"positive","source":"BigGo / Quiver Quantitative"},
        {"date":"2026-05-08","category":"美股","title":"AVGO BigGo 盤中 $428.15（+3.78%）跟漲費半；AI 業務 Q1 +106%；Q2 指引 $22B","impact":"positive","source":"BigGo"},
        {"date":"2026-05-08","category":"美股","title":"Arista（ANET）BigGo $139.69（-1.45%）；分析師均值 $175.18（Strong Buy 17 位）；FY2026 AI 指引 $35 億","impact":"mixed","source":"BigGo / StockAnalysis"},
        {"date":"2026-05-08","category":"地緣","title":"美伊和平談判進展：伊朗回應美方備忘錄；荷姆茲海峽再開預期 → 布蘭特原油跌至 ~$98；全球股市大漲","impact":"positive","source":"Bloomberg / CNBC"},
        {"date":"2026-05-08","category":"就業數據","title":"美國 4 月新增就業 115,000（超預期 65,000）；失業率穩 4.3%；勞動市場韌性支撐 Fed 維持利率","impact":"positive","source":"BLS / Yahoo Finance"},
        {"date":"2026-05-07","category":"美中貿易","title":"Trump 計劃訪問北京；美中關稅由 57%→47%（Busan 峰會結果）；中國對非美市場出口+21.8%","impact":"mixed","source":"WEF / Yahoo Finance"},
        {"date":"2026-05-07","category":"Fed政策","title":"Williams（Fed）：關稅通膨效應短暫，但新一波關稅壓力猶在；Fed 今年降息預期推遲至最早 9 月","impact":"negative","source":"Benzinga / Phemex"},
        {"date":"2026-05-01","category":"財報指引","title":"Apple Q3 FY26 指引：營收 ~$110B (+14-17%)，遠優於市場 +9.5%；毛利率 47.5-48.5%","impact":"positive","source":"AppleInsider"},
        {"date":"2026-05-01","category":"資本回饋","title":"Apple 宣布 $100B 股票回購 + 季息提高 4% 至 $0.27","impact":"positive","source":"Apple Newsroom"},
        {"date":"2026-04-30","category":"QCOM 財報","title":"QCOM 超大雲客製矽揭露（4/30）→ 股價單日飆 +16-20%；達 $181 高點；Citi/JPM/WFC 均升目標至 $160","impact":"positive","source":"Morningstar / Business Insider"},
        {"date":"2026-04-30","category":"美股大盤","title":"S&P 500 首破 7,200 (+1.02%)；VIX 降至 16.89；對沖基金單週淨流入 $450 億","impact":"positive","source":"Bloomberg"},
        {"date":"2026-04-16","category":"財報","title":"TSMC Q1 2026：營收 $35.9B (+35.1%)、毛利 66.2%；Q2 指引 $39-40.2B；AI 加速器 CAGR 上修至 54-56%","impact":"positive","source":"TSMC IR"},
        {"date":"2026-04-29","category":"台股","title":"日月光 Q1 2026：EPS 3.24 元超預期；LEAP 先進封測 2026 突破 $35億","impact":"positive","source":"TechNews"},
        {"date":"2026-04-27","category":"台股","title":"旺宏 Q1 2026：EPS 0.9 元終結連 10 季虧損；毛利 40.8%","impact":"positive","source":"Yahoo TW"},
        {"date":"2026-03-04","category":"財報","title":"AVGO Q1 FY26：營收 $19.31B (+29%)、AI 收入 $8.4B (+106%)；Q2 指引 $22B (+47%)、AI $10.7B (+140%)；Morningstar FV $500","impact":"positive","source":"CNBC / Morningstar"},
        {"date":"2026-04","category":"半導體","title":"Intel +16% 單日（Apple 晶片代工談判傳出）；半導體信心大幅提振","impact":"positive","source":"Yahoo Finance"},
        {"date":"2026-04","category":"AI 記憶體","title":"SanDisk 外資 Bernstein 目標 $1,250；NAND 企業合約價 Q1 +55-60%","impact":"positive","source":"Bernstein"},
        {"date":"2026-04","category":"台股（潛力股）","title":"緯穎 6669：野村目標價 6,670（最高）；2026E EPS 326-350；AI 伺服器代工龍頭","impact":"positive","source":"Nomura / cmoney"},
        {"date":"2026-03","category":"地緣","title":"美伊戰爭 2026/2 月爆發：荷姆茲海峽封鎖 → 油價飆至 $130+ 後回落；和平談判可望化解","impact":"negative","source":"Bloomberg / CNN"},
        {"date":"2026-04","category":"美聯準會","title":"FOMC：19 人中 7 人預期 2026 全年零降息；Fed 加息概率 30%（2027 前）；核心 PCE 通膨 3.1%","impact":"negative","source":"Phemex / Fed"},
    ],

    "earnings": [
        {"ticker":"AAPL","name":"Apple","period":"Q2 FY26 (4/30)","revenue":"$111.2B (+17%)","eps":"$2.01 (+22%)","highlight":"服務 $31B 新高；$100B 回購；Q3 指引 +14-17%；毛利 47.5-48.5%","rating":"Buy"},
        {"ticker":"AVGO","name":"Broadcom","period":"Q1 FY26 (3/4)","revenue":"$19.31B (+29%)","eps":"$2.05 (Non-GAAP)","highlight":"AI 收入 $8.4B (+106%)；Q2 指引 $22B；CEO：2027 AI 晶片 >$100B；Morningstar FV $500","rating":"Buy"},
        {"ticker":"QCOM","name":"Qualcomm","period":"Q2 FY26 (5/8)","revenue":"$10.6B (-3% YoY)","eps":"$6.88（超預期 $2.61；+173% YoY）","highlight":"超大雲客製矽 Q4 2026 出貨；車用 +50% YoY；Q3 指引 $9.6B（低於共識）；6/24 投資人日","rating":"Hold→升評中"},
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
            {"symbol":"AVGO","name":"Broadcom","sell":0,"hold":5,"buy":14,"label":"AI ASIC"},
            {"symbol":"SMH","name":"SMH","sell":0,"hold":6,"buy":13,"label":"半導體 ETF"},
        {"symbol":"QCOM","name":"Qualcomm","sell":1,"hold":9,"buy":9,"label":"資料中心客製矽"},
        {"symbol":"ANEL","name":"2×ANET","sell":7,"hold":9,"buy":3,"label":"日槓桿 ANET"},
            {"symbol":"TSMG","name":"2×TSM","sell":5,"hold":10,"buy":4,"label":"ADR 槓桿"},
            {"symbol":"TSLT","name":"2×TSLA","sell":6,"hold":10,"buy":3,"label":"高波動"},
            {"symbol":"SNDU","name":"2×SNDK","sell":3,"hold":9,"buy":7,"label":"記憶體槓桿"},
            {"symbol":"AIXI","name":"AIXI","sell":14,"hold":4,"buy":1,"label":"仙股／反彈賣"},
            {"symbol":"ONDL","name":"ONDL","sell":12,"hold":5,"buy":2,"label":"2×弱底層"},
            {"symbol":"2337.TW","name":"旺宏","sell":2,"hold":9,"buy":8,"label":"記憶體轉機"},
            {"symbol":"QCMU","name":"QCMU","sell":4,"hold":12,"buy":3,"label":"性質待確認"},
        ]
    },

    "picks": [
        {"rank":1,"ticker":"6669","name":"緯穎","market":"TW","price":4845,"target_low":5500,"target_high":6700,"upside_pct":18.7,"thesis":"AI 伺服器組裝龍頭，AI 訂單>70%；野村目標 6,670；2026E EPS 326-350","type":"個股"},
        {"rank":2,"ticker":"2308","name":"台達電","market":"TW","price":2165,"target_low":2400,"target_high":2650,"upside_pct":16.6,"thesis":"AI 電源+液冷+散熱三受惠；2026E EPS 強勁；目標 $2,400-2,650","type":"個股"},
        {"rank":3,"ticker":"3711","name":"日月光投控","market":"TW","price":516,"target_low":540,"target_high":660,"upside_pct":18.0,"thesis":"LEAP 先進封裝 CoWoS 受惠；Q1 EPS 3.24 超預期；凱基目標 588，歐系最高 660","type":"個股"},
        {"rank":4,"ticker":"ANET","name":"Arista Networks","market":"US","price":139.69,"target_low":175,"target_high":200,"upside_pct":25.3,"thesis":"AI Ethernet 400/800G 龍頭；17 位分析師 Strong Buy；均值 $175；≤$300 ✓","type":"個股"},
        {"rank":5,"ticker":"QCOM","name":"Qualcomm","market":"US","price":217.67,"target_low":175,"target_high":300,"upside_pct":8.0,"thesis":"超大雲客製矽 Q4 2026 出貨；AI+資料中心新敘事；6/24 投資人日為近期催化劑；≤$300 ✓","type":"個股"},
    ],

    # ===== actions（A/B 用 strategy/stop/target；C 用 action/reason）=====
    "actions": {
        "A": [
            {"symbol":"0050.TW","name":"元大台灣50","price":97.0,"target":"100-105","stop":90,"strategy":"壓艙石；與 00631L 長期核心；台股大盤重心不動"},
            {"symbol":"2330.TW","name":"台積電","price":2290,"target":"2,400-3,030","stop":2100,"strategy":"外資目標 2,288-3,030；Q2 指引 $39-40B 強勁；7/16 法說"},
            {"symbol":"3711.TW","name":"日月光投控","price":516,"target":"540-660","stop":480,"strategy":"LEAP/CoWoS；凱基 588、歐系 660；守月線"},
            {"symbol":"AVGO","name":"Broadcom","price":428.15,"target":"$450-500","stop":390,"strategy":"AI 主軸；Morningstar FV $500；5/8 +3.78%，分批鎖利可選"},
            {"symbol":"SMH","name":"VanEck 半導體","price":564.49,"target":"$580-620","stop":510,"strategy":"費半代理；5/8 創新高 +4.51%；居高思危"},
            {"symbol":"00631L.TW","name":"台灣50正2","price":32.47,"target":"34-38","stop":29,"strategy":"長期=0050 槓桿版；槓桿自律"},
        ],
        "B": [
            {"symbol":"QCOM","name":"Qualcomm","price":217.67,"target":"$225-250（Q4 客製矽出貨前重估）","stop":190,"strategy":"超大雲客製矽 Q4 2026；6/24 投資人日；1 股設停利 $240 / 停損 $190"},
            {"symbol":"ANEL","name":"2×ANET","price":15.47,"target":"$18-22（ANET 看 $170-175）","stop":13.0,"strategy":"短線槓桿博 ANET 25% 上行；**非**長抱 ANET 正股；建議 ANET $165 附近評估換正股"},
            {"symbol":"TSMG","name":"TSM 2×","price":39.18,"target":"$42-46","stop":34,"strategy":"考慮與 2330 重疊時降總曝險；5/8 -3%"},
            {"symbol":"SNDU","name":"SNDK 2×","price":110.2,"target":"$115-130","stop":88,"strategy":"2× 放大；僅衛星；NAND 週期支撐"},
            {"symbol":"2337.TW","name":"旺宏","price":153,"target":"165-175","stop":140,"strategy":"記憶體轉正；投信賣壓待消化；基本面轉正"},
            {"symbol":"00830.TW","name":"00830","price":78.6,"target":"85-92","stop":72,"strategy":"費半代理；5/8 費半創高帶動；小部位"},
        ],
        "C": [
            {"symbol":"AIXI","name":"Xiao-I","price":0.6134,"action":"等反彈分批賣（使用者策略）；設時程停損","reason":"今日 -15.16%；仙股流動性差；-55% 已虧重，不宜繼續等"},
            {"symbol":"ONDL","name":"ONDS 2×","price":13.2,"action":"反彈沿壓力減碼（使用者：等回漲賣）","reason":"底層 ONDS 疲弱，2× 持續衰減；注意流動性"},
            {"symbol":"TSLT","name":"Tesla 2×","price":21.82,"action":"槓桿上限控管；不宜再加","reason":"日損耗＋TSLA 高波動；目前盈利可設 $18 保護停損"},
        ]
    },

    # ===== next_buy_recommendations（tickers 必須是物件陣列）=====
    "next_buy_recommendations": [
        {
            "scenario": "美股盤中可下單（推薦個股）",
            "tickers": [
                {"ticker":"AVGO","name":"Broadcom","price":410.77,"rationale":"盤中回檔近逢低區；Q2 指引仍為主軸","size_suggest":"1 股 ≈ NT$ 13,006","confidence":"🟢 高"},
                {"ticker":"ANET","name":"Arista Networks","price":164.95,"rationale":"AI 網路 400G/800G 龍頭；目標 $200-220","size_suggest":"1 股 ≈ NT$ 5,222","confidence":"🟢 高"},
                {"ticker":"INTC","name":"Intel","price":108.87,"rationale":"轉機修復 + 量能活躍，適合波段分批","size_suggest":"1 股 ≈ NT$ 3,441","confidence":"🟡 中"},
            ]
        },
        {
            "scenario": "台股星期一（5/5）開盤可下單",
            "tickers": [
                {"ticker":"3711","name":"日月光投控","price":478,"rationale":"凱基目標 588；LEAP CoWoS；逢 470 加 1 股","size_suggest":"1 股 ≈ NT$ 478","confidence":"🟢 高"},
                {"ticker":"2330","name":"台積電","price":2135,"rationale":"外資最低目標 2,288；折讓 7%+；7/16 法說","size_suggest":"1 股 ≈ NT$ 2,135","confidence":"🟢 高"},
                {"ticker":"6669","name":"緯穎","price":4845,"rationale":"AI 伺服器代工龍頭；新標的觀察","size_suggest":"1 股 ≈ NT$ 4,845","confidence":"🟡 中"},
                {"ticker":"2308","name":"台達電","price":2165,"rationale":"電源+液冷+AI機櫃；4/30 收 **NT$2,165**","size_suggest":"1 張約 NT$216.5 萬（1000股）— 一般用零股／小數量","confidence":"🟡 中"},
            ]
        }
    ],

    # ===== allocation（陣列格式，非物件）=====
    "allocation": {
        "current": [
            {"label":"台股核心（0050+00631L+2330+3711+2337+00830）","value":61.6},
            {"label":"美股半導體（AVGO+SMH+QCOM）","value":24.0},
            {"label":"槓桿衛星（ANEL+TSLT+TSMG+SNDU+ONDL）","value":12.0},
            {"label":"高風險／待調節（AIXI+QCMU）","value":2.4},
            {"label":"現金","value":0.0},
        ],
        "target": [
            {"label":"台股核心","value":58},
            {"label":"美股半導體","value":28},
            {"label":"槓桿衛星","value":10},
            {"label":"高風險","value":0},
            {"label":"現金","value":4},
        ]
    },

    "consensus": [
        {"symbol":"QCOM","name":"Qualcomm","rating":"Hold→升評中（分歧）","target":"法說前均值 $168.50；RBC $175、Citi/JPM/WFC $160；股價 $217 遠超共識—升評追蹤中","date":"2026-05"},
        {"symbol":"AVGO","name":"Broadcom","rating":"Buy（11/12 分析師）","target":"$430-500；Morningstar FV $500","date":"2026-05"},
        {"symbol":"AAPL","name":"Apple","rating":"Buy","target":"$215-280","date":"2026-05"},
        {"symbol":"TSM","name":"TSMC ADR","rating":"Strong Buy","target":"概略 $400-480（級距上移，請以最新外資為準）","date":"2026-05"},
        {"symbol":"SNDK","name":"SanDisk","rating":"Buy","target":"$1,000-1,250","date":"2026-04"},
        {"symbol":"CRWV","name":"CoreWeave","rating":"Buy","target":"$130-160","date":"2026-04"},
        {"symbol":"WDC","name":"Western Digital","rating":"Buy","target":"概略 $450-520（股價級距已變，請以最新研報為準）","date":"2026-05"},
        {"symbol":"2330.TW","name":"台積電","rating":"加碼","target":"NT$2,288-3,030","date":"2026-04"},
        {"symbol":"3711.TW","name":"日月光","rating":"加碼","target":"NT$308-588","date":"2026-04"},
        {"symbol":"2337.TW","name":"旺宏","rating":"Hold","target":"NT$92-149","date":"2026-02"},
        {"symbol":"ANET","name":"Arista Networks","rating":"Strong Buy（17/17）","target":"均值 $175.18；範圍 $112-200；Morningstar $190","date":"2026-05"},
        {"symbol":"INTC","name":"Intel","rating":"Hold→Buy(事件驅動)","target":"$120-135","date":"2026-05"},
        {"symbol":"2308.TW","name":"台達電","rating":"偏多（情境參考）","target":"約 NT$2,400-2,650（請對照法人最新報告）","date":"2026-05"},
        {"symbol":"3037.TW","name":"欣興","rating":"注意股‧波動高（情境參考）","target":"約 NT$1,000-1,150（請對照法人最新報告）","date":"2026-05"},
    ],

    "forecast": [
        {"symbol":"AVGO","name":"Broadcom","bull":500,"base":455,"bear":395,"catalyst":"Q2 $22B + AI $10.7B 兌現；Morningstar FV $500"},
        {"symbol":"QCOM","name":"Qualcomm","bull":250,"base":220,"bear":190,"catalyst":"6/24 投資人日；Q4 超大雲客製矽出貨確認"},
        {"symbol":"ANET","name":"Arista Networks","bull":200,"base":175,"bear":130,"catalyst":"FY2026 AI 指引 $35 億兌現；Morningstar FV $190"},
        {"symbol":"TSM","name":"TSMC ADR","bull":460,"base":410,"bear":345,"catalyst":"7/16 法說；CoWoS 擴產；Q2 指引 $39-40B"},
        {"symbol":"SNDK","name":"SanDisk","bull":1350,"base":1200,"bear":950,"catalyst":"NAND 合約漲 55-60%；Bernstein $1,250"},
        {"symbol":"CRWV","name":"CoreWeave","bull":160,"base":135,"bear":95,"catalyst":"Q2 ARR 揭露；Meta $21B 落地"},
        {"symbol":"2330.TW","name":"台積電","bull":2500,"base":2380,"bear":2100,"catalyst":"外資目標 2,288-3,030；7/16 法說"},
        {"symbol":"3711.TW","name":"日月光","bull":560,"base":530,"bear":485,"catalyst":"LEAP/CoWoS；凱基 588，歐系 660"},
        {"symbol":"2337.TW","name":"旺宏","bull":175,"base":162,"bear":140,"catalyst":"投信賣壓消化後；eMMC 漲價"},
        {"symbol":"AAPL","name":"Apple","bull":255,"base":235,"bear":200,"catalyst":"Q3 +14-17% 指引兌現；$100B 回購"},
        {"symbol":"SMH","name":"VanEck SMH","bull":610,"base":565,"bear":520,"catalyst":"費半創新高後延伸；Intel/AMD/Micron 強勢"},
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
