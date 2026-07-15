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

FX = 32.215                                      # 匯率 USD→TWD（2026/07/15 券商截圖）
UPDATE_NOTE = "2026/07/15 更新（依券商截圖；台股 6 + 美股 10）。核心 0050/2330 永久不賣；台股衛星加重群創 3481（建議減碼）；美股含多檔日槓桿（ORCX/ONDL/SPCH/MULL/SNDU）優先出清。SMH×4 +27%。10/31 需用錢。7/16 台積電法說為最大催化劑。"

CASH_ON_HAND = 0
CASH_TO_DEPLOY = 0
CASH_NEED_DATE = "2026-10-31"

# ---- 1.1 台股持倉（2026/07/15 券商截圖）----
TW = [
    {"symbol":"0050.TW","name":"元大台灣50","shares":3360,"buy_price":67.69,"close":106.3,"change":1.90,"pct":1.82,"sector":"ETF（核心，永久持有）","tag":"core"},
    {"symbol":"2330.TW","name":"台積電","shares":25,"buy_price":2145.6,"close":2440.0,"change":20.0,"pct":0.83,"sector":"半導體（核心永久）","tag":"core"},
    {"symbol":"2317.TW","name":"鴻海","shares":170,"buy_price":296.09,"close":239.0,"change":3.50,"pct":1.49,"sector":"代工／AI 伺服器","tag":"satellite"},
    {"symbol":"2356.TW","name":"英業達","shares":1275,"buy_price":70.97,"close":61.1,"change":0.80,"pct":1.33,"sector":"ODM／伺服器","tag":"satellite"},
    {"symbol":"2379.TW","name":"瑞昱","shares":3,"buy_price":837.0,"close":753.0,"change":5.0,"pct":0.67,"sector":"IC 設計／網通","tag":"satellite"},
    {"symbol":"3481.TW","name":"群創","shares":2250,"buy_price":68.36,"close":58.5,"change":1.30,"pct":2.27,"sector":"面板（建議減碼）","tag":"satellite"},
]

# ---- 1.2 美股持倉（2026/07/15 券商截圖）----
US = [
    {"symbol":"SMH","name":"VanEck Semiconductor ETF","shares":4,"buy_price":471.28,"close":600.31,"change":14.69,"pct":2.51,"sector":"半導體 ETF","tag":"satellite"},
    {"symbol":"SPCX","name":"SpaceX","shares":12,"buy_price":197.80,"close":136.08,"change":-2.50,"pct":-1.80,"sector":"航太／IPO 後","tag":"speculative"},
    {"symbol":"MULL","name":"GraniteShares 2x Long MU","shares":58,"buy_price":31.59,"close":25.81,"change":2.29,"pct":9.74,"sector":"日槓桿 ETF（2X MU）","tag":"speculative"},
    {"symbol":"ON","name":"ON Semiconductor","shares":6,"buy_price":101.10,"close":93.73,"change":3.36,"pct":3.72,"sector":"功率／車用半導","tag":"satellite"},
    {"symbol":"ONDL","name":"Defiance 2X Long ONDS","shares":59,"buy_price":10.18,"close":6.66,"change":-0.20,"pct":-2.91,"sector":"日槓桿 ETF（2X ONDS）","tag":"speculative"},
    {"symbol":"BB","name":"BlackBerry","shares":30,"buy_price":12.75,"close":11.01,"change":0.10,"pct":0.92,"sector":"資安／IoT","tag":"satellite"},
    {"symbol":"ORCX","name":"Defiance 2X Long ORCL","shares":15,"buy_price":54.04,"close":17.55,"change":-0.80,"pct":-4.36,"sector":"日槓桿 ETF（2X ORCL）","tag":"speculative"},
    {"symbol":"MRVL","name":"Marvell Technology","shares":1,"buy_price":247.10,"close":222.44,"change":3.50,"pct":1.60,"sector":"AI 網通／資料中心","tag":"satellite"},
    {"symbol":"SNDU","name":"T-REX 2X Long SNDK","shares":4,"buy_price":35.73,"close":36.67,"change":0.50,"pct":1.38,"sector":"日槓桿 ETF（2X SNDK）","tag":"speculative"},
    {"symbol":"SPCH","name":"Leverage Shares 2X SPCX","shares":5,"buy_price":26.10,"close":9.50,"change":-0.45,"pct":-4.52,"sector":"日槓桿 ETF（2X SpaceX）","tag":"speculative"},
]

# =============================================================================
#  ==== 2. 結構區（不要改 key 名稱！） ====
# =============================================================================

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

data = {
    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "updated_at_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
    "fx_rate": FX,

    "user_strategy": {
        "philosophy": "2026/07/15：核心 0050/2330 永久持有；台股衛星 2317/2356/2379/3481（群創建議減碼）；美股 10 檔 10/31 前變現。本週優先出清日槓桿 ORCX/ONDL/SPCH/MULL/SNDU；SMH×4 為美股獲利主體；7/16 台積電法說為最大催化劑。",
        "leverage_map": [
            {"etf":"ORCX","underlying":"ORCL","multiplier":2,"treat_as":"exit_asap"},
            {"etf":"ONDL","underlying":"ONDS","multiplier":2,"treat_as":"exit_asap"},
            {"etf":"SPCH","underlying":"SPCX","multiplier":2,"treat_as":"exit_asap"},
            {"etf":"MULL","underlying":"MU","multiplier":2,"treat_as":"exit_asap"},
            {"etf":"SNDU","underlying":"SNDK","multiplier":2,"treat_as":"exit_asap"},
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
            "highlight": "0050 +57.8%、2330 +13.5%（核心）；3481 -14.9% 大倉拖累；2317 -17.8%、2356 -11.9%。",
            "verdict": "0050/2330 永久持有；群創分批減碼；鴻海／英業達不攤平；瑞昱極小部位。"
        },
        "us": {
            "title": f"🇺🇸 美股（10/31 前變現）{'+' if (us_mv_usd - us_cost_usd)>=0 else ''}{round(safe_pct(us_mv_usd - us_cost_usd, us_cost_usd),1)}%",
            "market_value_twd": us_mv_twd, "cost_twd": us_cost_twd,
            "pnl_twd": us_mv_twd - us_cost_twd,
            "pnl_pct": safe_pct(us_mv_twd - us_cost_twd, us_cost_usd),
            "market_value_usd": round(us_mv_usd, 2),
            "cost_usd": round(us_cost_usd, 2),
            "pnl_usd": round(us_mv_usd - us_cost_usd, 2),
            "winners": us_w, "losers": us_l,
            "highlight": "SMH×4 +27.4% 撐組；ORCX -67.5%、SPCH -63.6%、ONDL -34.6% 日槓桿重傷；SPCX -31.2%。",
            "verdict": "本週清日槓桿五檔；SPCX 減碼；SMH 9 月起分批出清；10/25 前全清。"
        }
    },

    "indices": [
        {"name":"S&P 500","code":"SPX","value":7543.89,"change":28.5,"pct":0.38},
        {"name":"NASDAQ","code":"IXIC","value":26107.01,"change":232.0,"pct":0.90},
        {"name":"Dow Jones","code":"DJI","value":52513.24,"change":10.0,"pct":0.02},
        {"name":"費城半導體","code":"SOX","value":6950.0,"change":172.0,"pct":2.54},
        {"name":"SMH(費半ETF)","code":"SMH","value":600.31,"change":14.69,"pct":2.51},
        {"name":"VIX","code":"VIX","value":16.5,"change":-0.8,"pct":-4.60},
        {"name":"台股加權","code":"TWII","value":45631.59,"change":893.64,"pct":2.00},
        {"name":"台指期","code":"TXF","value":45600.0,"change":880.0,"pct":1.97},
    ],

    "tw_stocks": TW,
    "us_stocks": US,

    "effective_exposure": [
        {"name":"0050（核心永久）","icon":"🇹🇼","components":["0050×3360"],"exposure_twd":357168,"pct_effective":39.2,"long_term":True},
        {"name":"台積電 2330（核心永久）","icon":"🏭","components":["2330 25股"],"exposure_twd":61000,"pct_effective":6.7,"long_term":True},
        {"name":"台股衛星（含群創）","icon":"📺","components":["3481×2250","2356×1275","2317×170","2379×3"],"exposure_twd":252416,"pct_effective":27.7,"long_term":False},
        {"name":"美股半導體 SMH×4","icon":"🔌","components":["SMH ETF"],"exposure_twd":77356,"pct_effective":8.5,"long_term":False},
        {"name":"美股日槓桿＋投機","icon":"⚠️","components":["ORCX/ONDL/SPCH/MULL/SNDU/SPCX/ON/BB/MRVL"],"exposure_twd":164150,"pct_effective":18.0,"long_term":False},
    ],

    "underlying_analysis": [
        {
            "ticker":"SMH","name":"VanEck SMH（×4）","price":600.31,"today_pct":2.51,"in_portfolio_twd":77356,
            "thesis":"美股唯一健康大倉；成本 $471.28，約 +27%；9 月起分批出清。",
            "pros":["半導短線反彈","AI 硬體仍占主流","相對個股槓桿更分散"],
            "cons":["10/31 必須變現","AI Capex 疑慮未消","單一 ETF 波動仍高"],
            "consensus_target":"$620-680","rating":"Buy","next_catalyst":"7/16 台積法說／8 月半導體財報潮","user_action":"🟡 守約 $560–580；9/1 起每週減 25–30%"
        },
        {
            "ticker":"ORCX","name":"Defiance 2X ORCL（×15）","price":17.55,"today_pct":-4.36,"in_portfolio_twd":8481,
            "thesis":"日槓桿；約 -67.5%；複利衰減，不適長抱。",
            "pros":["ORCL 雲端長線仍有題材"],
            "cons":["深度虧損","每日重置損耗","與變現期限衝突"],
            "consensus_target":"—","rating":"Sell","next_catalyst":"無","user_action":"🔴 本週開盤無條件出清"
        },
        {
            "ticker":"SPCX","name":"SpaceX（×12）","price":136.08,"today_pct":-1.80,"in_portfolio_twd":52606,
            "thesis":"IPO 後高波動普通股；約 -31%；與 SPCH 槓桿雙重曝險。",
            "pros":["品牌／發射題材長線敘事"],
            "cons":["上市後回檔深","估值不確定","10/31 限期"],
            "consensus_target":"分歧大","rating":"Speculative","next_catalyst":"營運／訂單新聞","user_action":"🔴 7–8 月優先減碼；勿再加 SPCH"
        },
        {
            "ticker":"2330.TW","name":"台積電（×25，核心）","price":2440,"today_pct":0.83,"in_portfolio_twd":61000,
            "thesis":"核心永久；6 月營收創新高；法說聚焦毛利／Capex／全年指引。",
            "pros":["AI／CoWoS 瓶頸位階","法人目標約 2,780–2,866","營收強勁"],
            "cons":["法說前後波動","高估值","短線利多出盡風險"],
            "consensus_target":"NT$2,780-2,866（均值）","rating":"Strong Buy","next_catalyst":"7/16 法說會","user_action":"🟢 永久持有，法說不追槓桿"
        },
        {
            "ticker":"3481.TW","name":"群創（×2250）","price":58.5,"today_pct":2.27,"in_portfolio_twd":131625,
            "thesis":"面板週期；上半年營收改善但 EPS 薄；倉位過重約 14%。",
            "pros":["營收近五年同期高","短線資金炒作可能"],
            "cons":["獲利薄","爆量下跌紀錄","與 AI 核心相關度低"],
            "consensus_target":"分歧／偏保守","rating":"Reduce","next_catalyst":"面板報價","user_action":"🔴 分批減 30–50%；資金可轉 3711"
        },
        {
            "ticker":"ON","name":"ON Semiconductor（×6）","price":93.73,"today_pct":3.72,"in_portfolio_twd":18117,
            "thesis":"功率／車用／資料中心；輕虧；適作清槓桿後乾淨載體。",
            "pros":["法人偏買","目標約 $111–124","AI 資料中心營收成長"],
            "cons":["短線估值偏豐厚","8/3 財報波動","10 月仍須出清"],
            "consensus_target":"均值 ~$111","rating":"Moderate Buy","next_catalyst":"約 8/3 財報","user_action":"🟡 可短暫持有；優先於再開日槓桿"
        },
    ],

    "horizon_views": {
        "short_term_1m": {
            "title": "🔭 短線（7 月中下旬）— 台積法說＋清日槓桿",
            "intro": "7/15：CPI 降溫、台股重返 45.6K；7/16 台積電法說。持倉拖累＝群創＋日槓桿五檔。本週以止血為先。",
            "tw_index": {
                "current": 45631.59,
                "bull": 47000, "p_bull": 30,
                "base": 45000, "p_base": 45,
                "bear": 43000, "p_bear": 25,
                "scenario": "法說優於預期→挑戰 4.7 萬；利多出盡／升息雜音→回測 4.3 萬；基本：45K 附近震盪",
            },
            "forecasts": [
                {"symbol":"0050.TW","name":"元大台灣50","current":106.3,"bull":112,"base":107,"bear":100,"view":"核心永久；隨權值波動"},
                {"symbol":"2330.TW","name":"台積電","current":2440,"bull":2700,"base":2500,"bear":2200,"view":"核心；法說為分水嶺"},
                {"symbol":"3481.TW","name":"群創","current":58.5,"bull":65,"base":58,"bear":52,"view":"減碼優先；反彈賣"},
                {"symbol":"SMH","name":"VanEck SMH（4股）","current":600.31,"bull":660,"base":610,"bear":560,"view":"+27%；9 月起尾段出清"},
                {"symbol":"ORCX","name":"2X ORCL","current":17.55,"bull":22,"base":16,"bear":12,"view":"-67%；本週出清"},
                {"symbol":"SPCX","name":"SpaceX","current":136.08,"bull":160,"base":130,"bear":110,"view":"-31%；7–8 月減碼"},
                {"symbol":"ON","name":"ON Semi","current":93.73,"bull":110,"base":98,"bear":85,"view":"輕虧；乾淨載體"},
            ]
        },
        "long_term": {
            "title": "🏔️ 核心永久 vs 10/31 美股變現",
            "intro": "核心僅 0050/2330；台股衛星可調；美股（含槓桿）全部納入變現池。新資金長線可關注 3711／NVDA／ON／QCOM（≤300）。",
            "core_long_term_buys": [
                {"symbol":"0050.TW","name":"元大台灣50","view":"永久壓艙石 +57.8%"},
                {"symbol":"2330.TW","name":"台積電","view":"AI 製造主軸 +13.5%；永久不賣"},
            ],
            "satellite_growth": [
                {"symbol":"SMH","name":"VanEck SMH（×4）","view":"3 個月部位 +27%；9 月起了結"},
                {"symbol":"ON","name":"ON Semiconductor","view":"功率半導；可暫代槓桿曝險"},
                {"symbol":"3711.TW","name":"日月光（觀察新增）","view":"外資目標 750–835；群創資金可轉"},
            ],
            "exit_or_reduce": [
                {"symbol":"ORCX","name":"2X ORCL","view":"-67%；本週清"},
                {"symbol":"SPCH","name":"2X SPCX","view":"-64%；本週清"},
                {"symbol":"ONDL","name":"2X ONDS","view":"-35%；本週清"},
                {"symbol":"MULL","name":"2X MU","view":"-18%；本週清"},
                {"symbol":"3481.TW","name":"群創","view":"-15%；分批減 30–50%"},
                {"symbol":"SPCX","name":"SpaceX","view":"-31%；7–8 月減"},
            ]
        },
        "peak_decision": {
            "title": "✅ 本週止血 → 法說確認 → 9 月變現節奏",
            "current_status": "2026/07/15：總市值約 NT$91.2 萬；台股約 74%、美股約 26%。日槓桿與群創為主要風險；SMH／0050／2330 為健康部位。",
            "verdict": "本週清日槓桿五檔＋減群創；法說前後核心不動；9/1 起 SMH 分批出；10/25 前美股歸零。",
            "actions": [
                {"type":"🟢 核心永久持有（不動）","items":[
                    "0050／2330：法說前後均不賣、不加槓桿追價",
                ]},
                {"type":"🔴 立即處理（本週）","items":[
                    "ORCX／SPCH／ONDL／SNDU／MULL：開盤起出清日槓桿",
                    "3481 群創：分批減 30–50%",
                ]},
                {"type":"🟡 7–8 月觀察","items":[
                    "SPCX／BB：弱勢或反彈減碼",
                    "ON／MRVL：併入變現池，不開新槓桿",
                    "SMH：守 $560–580，9 月起規律減倉",
                ]},
                {"type":"⚫ 變現紀律（不變）","items":[
                    "9/1 起 SMH 每週減 25–30%",
                    "10/25 前美股全清空（10/31 需用錢）",
                ]},
            ],
            "cash_target": "10/31 前美股 10 檔全數變現；核心台股永久不動。"
        },
        "tomorrow_tw_strategy": {
            "title": "📆 7/16（四）— 台積電法說日操作計畫",
            "macro_context": [
                "📌 7/16 台積電法說：毛利率／Capex／全年指引為市場焦點",
                "📌 7/15 台股大漲約 894 點收 45,632；記憶體／半導領漲",
                "📌 美股：6 月 CPI 低於預期，半導反彈但 AI Capex 疑慮仍在",
                "📌 持倉：0050＋2330 健康；群創＋美股日槓桿優先處理",
                "📌 硬約束：10/31 前美股須變現",
            ],
            "morning_plan": [
                {"step":1,"action":"09:00 開盤","detail":"🟢 核心 0050／2330 不操作；法說前勿追高"},
                {"step":2,"action":"09:00-10:00","detail":"🟡 若權值續強僅觀望；群創反彈可掛減碼單"},
                {"step":3,"action":"盤中","detail":"🔴 不新增面板／日槓桿部位"},
                {"step":4,"action":"法說後（下午～晚間）","detail":"🟡 聽完整指引再評 2330 波動；核心仍不動"},
                {"step":5,"action":"美股時段","detail":"🔴 開盤起出清 ORCX／SPCH／ONDL／SNDU／MULL"},
                {"step":6,"action":"本週收尾","detail":"⚫ 確認日槓桿已清零；更新變現檢查表"},
            ],
            "watch_list_for_tomorrow": [
                {"symbol":"2330","name":"台積電","buy_zone":"持有不追","target":"法人 2780+","action":"永久持有；法說波動忍耐"},
                {"symbol":"3481","name":"群創","buy_zone":"—","target":"減碼","action":"反彈分批賣 30–50%"},
                {"symbol":"SMH","name":"VanEck SMH","buy_zone":"560-580","target":"620-660","action":"持守 4 股；9 月起減"},
            ],
            "avoid_list": [
                {"symbol":"ORCX","name":"2X ORCL","reason":"-67% 日槓桿；立即出清"},
                {"symbol":"SPCH","name":"2X SPCX","reason":"-64% 日槓桿；立即出清"},
                {"symbol":"MULL","name":"2X MU","reason":"與變現期限衝突；出清改 SMH／現金"},
            ],
            "risk_alerts": [
                "⚠️ 法說利多出盡→台股短線回吐",
                "⚠️ 日槓桿續抱將加速耗損本金",
                "⚠️ 群創集中度過高（約 14%）",
                "⚠️ 10/31 用錢：美股不可再開長天期投機",
            ],
            "one_line": "法說日：核心不動、群創減碼、美股清日槓桿；為 9–10 月變現鋪路。"
        }
    },

    "news": [
        {"date":"2026-07-16","category":"🏭 台積電","title":"台積電法說會：市場聚焦毛利率、Capex 與全年營收展望","impact":"neutral","source":"中時／路透"},
        {"date":"2026-07-15","category":"台股","title":"加權收 45,632（＋894／＋2%）；半導與記憶體領漲","impact":"positive","source":"工商時報／永豐"},
        {"date":"2026-07-15","category":"美股","title":"6 月 CPI 低於預期；NASDAQ＋0.9%、費半約＋2.5%；IBM 財報重挫示警軟體","impact":"mixed","source":"Deutsche Bank／TradingKey"},
        {"date":"2026-07-15","category":"半導體","title":"半導短線歸因「超賣反彈」；AI Capex 疑慮未完全解除","impact":"mixed","source":"朝鮮日報英譯"},
        {"date":"2026-07-14","category":"美股","title":"ON Semi 法人偏買、目標約 $111–124；AI 資料中心營收成長","impact":"positive","source":"24/7 Wall St.／Yahoo"},
        {"date":"2026-07-13","category":"台股","title":"台積電 6 月營收約 4,427 億創新高；群創上半年營收近五年同期高","impact":"mixed","source":"經濟日報／UDN"},
        {"date":"2026-07-15","category":"✅ 對帳","title":"7/15 券商對帳：台股 6＋美股 10；日槓桿待清；群創建議減碼","impact":"mixed","source":"Portfolio 截圖"},
        {"date":"2026-07-09","category":"台股","title":"日月光外資目標上看 750–835；先進封裝 Capex 上修","impact":"positive","source":"經濟日報／TechNews"},
    ],

    "earnings": [
        {"ticker":"2330.TW","name":"台積電（核心）","period":"Q2 法說 7/16","revenue":"6月創高","eps":"TTM ~74","highlight":"關注毛利／Capex／全年指引","rating":"Strong Buy"},
        {"ticker":"SMH","name":"VanEck SMH（×4）","period":"ETF","revenue":"—","eps":"—","highlight":"+27%；9月起尾段出清","rating":"Buy"},
        {"ticker":"ON","name":"ON Semi（×6）","period":"Q2 約8/3","revenue":"—","eps":"預估約 $0.71","highlight":"AI 資料中心＋SiC；輕虧","rating":"Moderate Buy"},
        {"ticker":"3481.TW","name":"群創（×2250）","period":"上半年","revenue":"1,302億","eps":"TTM 薄","highlight":"營收改善但獲利弱；建議減碼","rating":"Reduce"},
        {"ticker":"ORCX","name":"2X ORCL（×15）","period":"槓桿ETF","revenue":"—","eps":"—","highlight":"-67%；本週出清","rating":"Sell"},
        {"ticker":"2356.TW","name":"英業達（×1275）","period":"營收追蹤","revenue":"—","eps":"—","highlight":"ODM；-12%；不攤平","rating":"Hold"},
    ],

    "analysts": {
        "panel": ["巴菲特","芒格","Cathie Wood","Michael Burry","Peter Lynch","Ray Dalio","Druckenmiller","葛拉漢","索羅斯","科斯托蘭尼","Jim Simons","動能派","價值派","成長派","宏觀策略","風控長","產業專家","量化派","ESG"],
        "votes": [
            {"symbol":"2330.TW","name":"台積電（核心永久）","sell":0,"hold":3,"buy":16,"label":"法說前 Strong Buy；目標約 2780+"},
            {"symbol":"0050.TW","name":"元大台灣50（核心永久）","sell":0,"hold":5,"buy":14,"label":"壓艙石 +57.8%"},
            {"symbol":"SMH","name":"VanEck SMH（×4）","sell":2,"hold":6,"buy":11,"label":"+27%；9 月變現節奏"},
            {"symbol":"ORCX","name":"2X ORCL（×15）","sell":17,"hold":1,"buy":1,"label":"日槓桿 -67%；立即出清"},
            {"symbol":"3481.TW","name":"群創（×2250）","sell":10,"hold":6,"buy":3,"label":"倉位過重；減碼"},
            {"symbol":"ON","name":"ON Semi（×6）","sell":2,"hold":7,"buy":10,"label":"Moderate Buy；目標 ~111"},
        ]
    },

    "picks": [
        {"rank":1,"ticker":"2330","name":"台積電（核心）","market":"TW","price":2440,"target_low":2600,"target_high":2866,"upside_pct":11.0,"thesis":"核心永久；7/16 法說；AI／CoWoS","type":"核心永久"},
        {"rank":2,"ticker":"0050","name":"元大台灣50（核心）","market":"TW","price":106.3,"target_low":108,"target_high":115,"upside_pct":5.0,"thesis":"+57.8% 壓艙石","type":"核心永久"},
        {"rank":3,"ticker":"3711","name":"日月光投控（建議新）","market":"TW","price":683,"target_low":750,"target_high":835,"upside_pct":15.7,"thesis":"先進封裝；群創資金可轉；分批勿追漲","type":"建議新增"},
        {"rank":4,"ticker":"ON","name":"ON Semiconductor","market":"US","price":93.73,"target_low":111,"target_high":124,"upside_pct":21.6,"thesis":"≤300；清槓桿後載體；10月前仍變現","type":"美股≤300短期"},
        {"rank":5,"ticker":"NVDA","name":"NVIDIA（長線觀察）","market":"US","price":211.74,"target_low":240,"target_high":280,"upside_pct":20.0,"thesis":"≤300；10/31 用錢後再考慮","type":"長期觀察"},
    ],

    "actions": {
        "A": [
            {"symbol":"0050","name":"元大台灣50（核心）","price":106.3,"target":"永久持有","stop":98,"strategy":"永久壓艙石；法說前後不操作"},
            {"symbol":"2330","name":"台積電（核心）","price":2440,"target":"永久持有","stop":2150,"strategy":"核心不動；法說波動忍耐"},
            {"symbol":"SMH","name":"VanEck SMH（×4）","price":600.31,"target":"620-660","stop":560,"strategy":"美股獲利主體；9/1 起每週減 25–30%"},
        ],
        "B": [
            {"symbol":"3711","name":"日月光（建議新建倉）","price":683,"target":"750-835","stop":620,"strategy":"用群創減碼資金分批承接；勿追單日大漲"},
            {"symbol":"ON","name":"ON Semi（×6）","price":93.73,"target":"111-124","stop":85,"strategy":"優於再開日槓桿；10月前隨變現出清"},
            {"symbol":"QCOM","name":"高通（觀察≤300）","price":178.81,"target":"200-220","stop":160,"strategy":"手機＋AI PC；小倉可暫代投機部位"},
        ],
        "C": [
            {"symbol":"ORCX","name":"2X ORCL（×15）","price":17.55,"action":"本週開盤出清","reason":"-67.5% 日槓桿；複利衰減"},
            {"symbol":"SPCH","name":"2X SPCX（×5）","price":9.50,"action":"本週開盤出清","reason":"-63.6% 日槓桿"},
            {"symbol":"ONDL","name":"2X ONDS（×59）","price":6.66,"action":"本週開盤出清","reason":"-34.6% 日槓桿"},
            {"symbol":"MULL","name":"2X MU（×58）","price":25.81,"action":"本週出清","reason":"-18.3%；改曝險用 SMH"},
            {"symbol":"SNDU","name":"2X SNDK（×4）","price":36.67,"action":"本週出清","reason":"日槓桿；金額小亦清"},
            {"symbol":"3481","name":"群創（×2250）","price":58.5,"action":"分批減 30–50%","reason":"倉位過重約 14%；獲利薄"},
            {"symbol":"SPCX","name":"SpaceX（×12）","price":136.08,"action":"7–8 月優先減碼","reason":"-31.2%；IPO 後高波動"},
            {"symbol":"2317","name":"鴻海（×170）","price":239,"action":"不攤平；反彈減","reason":"-17.8%"},
        ]
    },

    "next_buy_recommendations": [
        {
            "scenario": "🔴 本週立即處理（出清／減碼）",
            "tickers": [
                {"ticker":"ORCX","name":"2X ORCL（×15）","price":17.55,"rationale":"日槓桿 -67%；開盤出清","size_suggest":"全部 15 股","confidence":"🔴 立即"},
                {"ticker":"SPCH","name":"2X SPCX（×5）","price":9.50,"rationale":"日槓桿 -64%；開盤出清","size_suggest":"全部 5 股","confidence":"🔴 立即"},
                {"ticker":"3481","name":"群創","price":58.5,"rationale":"集中度過高；分批減","size_suggest":"先減 30–50%","confidence":"🔴 本週起動"},
            ]
        },
        {
            "scenario": "🟡 置換建議（減碼後資金）",
            "tickers": [
                {"ticker":"3711","name":"日月光投控","price":683,"rationale":"外資目標 750–835；先進封裝","size_suggest":"群創資金分批","confidence":"🟡 分批"},
                {"ticker":"ON","name":"ON Semi","price":93.73,"rationale":"≤300；乾淨半導載體","size_suggest":"槓桿出清後可小加","confidence":"🟡 短期"},
                {"ticker":"SMH","name":"VanEck SMH","price":600.31,"rationale":"已持；半導曝險優於單股 2X","size_suggest":"不加倉亦可用作集中載體至 9 月","confidence":"🟡 持守"},
            ]
        },
        {
            "scenario": "🟢 核心永久持有（不動）",
            "tickers": [
                {"ticker":"0050","name":"元大台灣50","price":106.3,"rationale":"+57.8% 壓艙石","size_suggest":"永久持有 3,360 股","confidence":"🟢 不賣"},
                {"ticker":"2330","name":"台積電","price":2440,"rationale":"+13.5% AI 主軸；法說催化","size_suggest":"永久持有 25 股","confidence":"🟢 不賣"},
            ]
        },
        {
            "scenario": "⚫ 10/31 前變現紀律",
            "tickers": [
                {"ticker":"SMH","name":"VanEck SMH（×4）","price":600.31,"rationale":"9/1 起每週減 25–30%；10/25 前全出","size_suggest":"9月起分批","confidence":"⚫ 硬約束"},
                {"ticker":"其餘美股","name":"SPCX/ON/BB/MRVL 等","price":0,"rationale":"7–8 月減碼；10/25 前全清","size_suggest":"分批","confidence":"⚫ 硬約束"},
            ]
        }
    ],

    "allocation": {
        "current": [
            {"label":"台股核心（0050+2330）","value":45.9},
            {"label":"台股衛星（含群創）","value":27.7},
            {"label":"美股 SMH","value":8.5},
            {"label":"美股其他（含日槓桿）","value":18.0},
            {"label":"現金","value":0.0},
        ],
        "target": [
            {"label":"台股核心（永久不動）","value":55},
            {"label":"台股衛星（降群創、可含3711）","value":15},
            {"label":"美股（清槓桿→SMH→變現）","value":10},
            {"label":"現金（10/31 到位）","value":20},
        ]
    },

    "consensus": [
        {"symbol":"2330.TW","name":"台積電（核心）","rating":"Strong Buy","target":"NT$2,780-2,866（均值）","date":"2026-07-15"},
        {"symbol":"SMH","name":"VanEck SMH（×4）","rating":"Buy","target":"$620-680","date":"2026-07-15"},
        {"symbol":"ON","name":"ON Semi（×6）","rating":"Moderate Buy","target":"均值 ~$111（高估 ~$124）","date":"2026-07-15"},
        {"symbol":"3711.TW","name":"日月光（建議）","rating":"買進","target":"NT$750-835","date":"2026-07-09"},
        {"symbol":"ORCX","name":"2X ORCL（×15）","rating":"Sell","target":"—","date":"2026-07-15"},
        {"symbol":"3481.TW","name":"群創（×2250）","rating":"Reduce","target":"減碼優先","date":"2026-07-15"},
    ],

    "forecast": [
        {"symbol":"SMH","name":"VanEck SMH（×4）","bull":660,"base":610,"bear":560,"catalyst":"半導反彈延續 vs Capex 雜音；9 月紀律出清"},
        {"symbol":"ORCX","name":"2X ORCL","bull":22,"base":16,"bear":12,"catalyst":"日槓桿；立即出清"},
        {"symbol":"2330.TW","name":"台積電（核心）","bull":2700,"base":2500,"bear":2200,"catalyst":"7/16 法說；永久持有"},
        {"symbol":"0050.TW","name":"元大台灣50","bull":112,"base":107,"bear":100,"catalyst":"權值＋資金面"},
        {"symbol":"3481.TW","name":"群創","bull":65,"base":58,"bear":52,"catalyst":"減碼；面板週期"},
        {"symbol":"TWII","name":"台股加權","bull":47000,"base":45000,"bear":43000,"catalyst":"法說後方向；8–9 月高檔震盪觀點"},
    ],

    "capital_plan": {
        "title": "2026/07/15 — 清日槓桿＋減群創＋10/31 美股變現",
        "sources": [
            {"src":"美股 10 檔","amount_twd":us_mv_twd,"amount_usd":round(us_mv_usd,2),"status":"conditional","note":"本週先日槓桿；7–8 月 SPCX／BB；9 月起 SMH；10/25 前全清"},
            {"src":"群創減碼（估減半）","amount_twd":65812,"amount_usd":0,"status":"conditional","note":"3481 減約 50% 可轉 3711 或現金"},
        ],
        "totals": {
            "immediate": 0,
            "conditional": us_mv_twd + 65812,
            "total": us_mv_twd + 65812
        },
        "context": [
            "🔴 本週優先出清 ORCX／SPCH／ONDL／SNDU／MULL（日槓桿）",
            "🔴 群創分批減 30–50%，降低單一衛星集中度",
            "核心 0050／2330 永久持有，不參與變現",
            "7/16 台積電法說：核心不加槓桿追價",
            "10/31 用錢硬約束不變，9/1 起啟動 SMH 分批出清",
        ],
        "options": [
            {
                "id": "A",
                "name": "止血後紀律變現（推薦 ⭐）",
                "philosophy": "先清日槓桿與減群創→法說後評估→9 月起 SMH 規律出清",
                "actions": [
                    {"step":1,"fund":"日槓桿五檔","use":"本週開盤出清","rationale":"複利衰減與用錢期限衝突"},
                    {"step":2,"fund":"3481 減半","use":"分批賣出","rationale":"降集中度；可轉 3711"},
                    {"step":3,"fund":"7/16 法說","use":"核心不動","rationale":"聽完整指引"},
                    {"step":4,"fund":"SMH×4","use":"9/1 起每週減 25–30%","rationale":"10/25 前完成"},
                    {"step":5,"fund":"其餘美股","use":"7–10 月分批","rationale":"10/31 硬約束"},
                ],
                "result": {
                    "post_tw_pct": 70,
                    "post_us_pct": 15,
                    "post_cash_pct": 15,
                    "post_leveraged_pct": 0,
                    "summary": "風險倉清零；核心健康；變現節奏可控"
                }
            },
            {
                "id": "B",
                "name": "更積極降美股（保守）",
                "philosophy": "本週連 SMH 先賣 1–2 股，縮短變現尾段壓力",
                "actions": [
                    {"step":1,"fund":"日槓桿五檔","use":"本週全清","rationale":"止血"},
                    {"step":2,"fund":"SMH 先減 1–2 股","use":"降低波動","rationale":"法說＋半導震盪風險"},
                ],
                "result": {
                    "post_tw_pct": 78,
                    "post_us_pct": 10,
                    "post_cash_pct": 12,
                    "post_leveraged_pct": 0,
                    "summary": "更快到手現金；可能少賺 SMH 剩餘升勢"
                }
            },
            {
                "id": "C",
                "name": "僅清最重傷槓桿（積極）",
                "philosophy": "先出 ORCX／SPCH／ONDL，暫留 MULL／SNDU 與 SMH",
                "actions": [
                    {"step":1,"fund":"ORCX/SPCH/ONDL","use":"立即清","rationale":"深套優先"},
                    {"step":2,"fund":"MULL/SNDU","use":"一週內清完","rationale":"仍屬日槓桿"},
                ],
                "result": {
                    "post_tw_pct": 74,
                    "post_us_pct": 20,
                    "post_cash_pct": 6,
                    "post_leveraged_pct": 0,
                    "summary": "仍需盡快清完所有日槓桿，避免拖延"
                }
            }
        ],
        "recommendation": {
            "primary": "A",
            "reason": "本週清所有日槓桿＋啟動減群創；法說週核心不動；9 月起 SMH 紀律變現以符合 10/31。",
            "secondary_if_aggressive": "C"
        },
        "risks": [
            "台積法說利多出盡→台股短線回吐",
            "日槓桿若拖延將繼續侵蝕本金",
            "群創集中度與面板週期雙重風險",
            "SpaceX（SPCX）IPO 後波動劇烈",
            "10/31 用錢：任何新美股部位都須可快速變現",
        ]
    },

    "update_log": "https://github.com/s07362022/stock-dashboard/blob/master/UPDATE_LOG.md"
}

import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, '..', 'data', 'stocks.json')
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'[OK] stocks.json 已重建 → {OUT}')
print(f'  總市值: NT$ {data["summary"]["total_market_value_twd"]:,}')
print(f'  總損益: NT$ {data["summary"]["total_pnl_twd"]:,} ({data["summary"]["total_pnl_pct"]}%)')
print(f'  Top keys: {len(data)}')

required = ['updated_at','fx_rate','user_strategy','summary','pnl_split','indices',
            'tw_stocks','us_stocks','effective_exposure','underlying_analysis',
            'horizon_views','news','earnings','analysts','picks','actions',
            'next_buy_recommendations','allocation','consensus','forecast','capital_plan']
missing = [k for k in required if k not in data]
print(f'  Required keys missing: {missing if missing else "NONE"}')

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
