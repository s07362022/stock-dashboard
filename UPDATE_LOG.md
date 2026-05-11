# 📋 Stock Dashboard 更新日誌

> 每次更新網頁皆記錄於此，按日期倒序排列。
> Live: https://s07362022.github.io/stock-dashboard/
> Schema 規範：[SCHEMA.md](SCHEMA.md)
> 唯一產生器：[scripts/build_stocks_json.py](scripts/build_stocks_json.py)

---

## 2026-05-12 — 券商美股庫存截圖全量更新（QCMU 71、MULL、VSH；無 QCOM 正股）

### 變更
- **匯率**：`31.405`（截圖）。
- **美股 11 檔**：SMH、QCMU、AVGO、ANEL、TSLT、ONDL、TSMG、MULL、SNDU、VSH、AIXI — 股數／成本／市價依 **2026/05/12 券商表**；**已移除 QCOM 正股**。
- **新增**：**MULL**（GraniteShares 2× Long MU Daily）、**VSH**（Vishay）。
- **QCMU**：46→**71** 股；**ANEL** 50→**55**；**TSLT** 30→**35**；**TSMG** 30→**15**；**SNDU** 3→**2**；**AIXI** 70→**3**（成本結構已變）。
- **`user_strategy` / `leverage_map` / `effective_exposure` / `underlying_analysis` / `analysts.votes` / `actions` / `allocation` / `forecast` / `horizon_views`**：同步新結構與論述。
- **台股**：`TW` 區仍為前次 BigGo 值；`portfolio.md` 已註記待補台股新截圖。
- **產出驗證**：`python scripts/build_stocks_json.py` → 總市值 **NT$945,624**、總損益 **+22.1%**（+NT$171,128）；23 key + 子結構 **OK**。

---

## 2026-05-11 — BigGo 台股 5/11 盤中 + 美股 5/8 收盤同步儀表板

### 變更
- **台股（BigGo ~13:30 UTC+8）**：0050 **96.9**、00631L **32.66**、00830 **82.3**、2330 **2235**、2337 **159.5**、3711 **537**；`UPDATE_NOTE` 與 `news` 首條同步。
- **美股（BigGo 5/8 美東收盤）**：QCOM **219.09**（+8.17%）、SMH **566.54**（+4.9%）、AVGO **430**（+4.23%）、QCMU **39.5**（+15.77%）、ANEL **15.98**、AIXI **0.6101**、TSMG **39.61**；ONDL／TSLT／SNDU BigGo 無即時價處沿用前次 **close**。
- **QCMU**：名稱改為 **Direxion Daily QCOM Bull 2X ETF**；分析師票 label 改為「QCOM 2×槓桿」。
- **大盤 ribbon**：SMH **566.54**、台股加權參考 **41,138**（媒體前段創高區間）、VIX 略上修敘述。
- **actions / picks / horizon_views / underlying_analysis / consensus**：價格與字串對齊新報價。
- **產出驗證**：`python scripts/build_stocks_json.py` → 總市值 **NT$900,657**、總損益 **+21.71%**（+NT$160,639）；23 key + 子結構 **全部 OK**。

---

## 2026-05-09 v2 — BigGo 5/8 盤中最新報價 + QCOM 財報大漲 + 美伊和平 + 費半新高

### 變更
- **美股報價（BigGo 5/8 EDT ~14:12）**：QCOM $217.67（+7.46%）、AVGO $428.15（+3.78%）、SMH $564.49（+4.51% 創新高）、ANET $139.69（-1.45%）、ANEL $15.47（-3.61%）、AIXI $0.6134（-15.16%）、TSMG $39.18（-3.0%）。
- **台股**：0050 $97（-0.72%）、2330 $2,290（-0.87%）維持不變。
- **大盤指數更新**：S&P 500 7,391（+0.74%）、NASDAQ 26,145（+1.32%）、Dow 49,621（+0.05%）——創歷史新高。
- **QCOM 財報**：Q2 FY2026 EPS $6.88（超預期 $2.61，+173% YoY）；超大雲客製矽 Q4 2026 初出貨。
- **新聞更新**：美伊和平談判、就業數據強勁（115K vs 預期 65K）、Intel +16% Apple 代工談判。
- **分析師票 更新**：QCOM 由 (2/11/6) → (1/9/9) 反映新資料中心題材。
- **ANEL/QCOM 策略更新**：ANEL 設停損 $13；QCOM 設停利 $240 / 停損 $190。
- **明日策略**：更新為 5/11（週一）台股開盤策略。
- **預測**：加入 QCOM、ANET 1-3 月情境；更新 SMH。
- **產出驗證**：`python scripts/build_stocks_json.py` → 總市值 **NT$897,675**、總損益 **+21.3%**（+NT$157,657）；23 key + 14 子結構 **全部 OK**。

---

## 2026-05-09 — 依券商庫存截圖全量覆寫可變值區 + BigGo 5/8 驗價

### 變更
- **台股**：`0050`、`00631L`、`2330`、`2337`、`3711` 股數／成本與截圖一致；**新增 `00830`**。
- **美股**：與截圖一致 **10 檔** — `ANEL`、`QCOM`、`AIXI`、`ONDL`、`AVGO`、`QCMU`、`SMH`、`SNDU`、`TSLT`、`TSMG`；**移除**舊版 `CWVX`／`ORCX`／`INTC` 等非當前部位。
- **匯率**：`31.425`（截圖參考）。
- **報價來源**：[BigGo](https://finance.biggo.com.tw) 台股 **5/8 收盤**、美股 **5/8 美東**（`QCOM`/`SMH`/`AVGO` 等）；`close` 與截圖差異處以 **BigGo 為儀表主顯示**。
- **論述**：`user_strategy`、`pnl_split`、`effective_exposure`、`underlying_analysis`、`analysts.votes`、`actions`、`allocation`、`news`（新增 5/8 條）、`picks`（ANET/ORCL）同步庫存。
- **產出驗證**：`python scripts/build_stocks_json.py` → 總市值 **NT$897,875**、總損益 **+21.33%**；內建 23 key + 子結構檢查 **OK**。

### 驗證
- 本地：`python scripts/build_stocks_json.py`
- Live：推送後待 Pages 重建，開 live 首頁確認圖表與表格載入。

---

## 2026-05-05 — 依 05/05 最新庫存截圖重建 + 修復空白頁驗證

### 變更
- 以使用者 **05/05 券商截圖**覆蓋 `scripts/build_stocks_json.py` 可變值區持倉：
  - 台股改為 5 檔：`0050`、`00631L`、`2330`、`2337`、`3711`
  - 美股改為 10 檔：新增/保留 `INTC`、`ORCX`，並同步 `SNDU`、`TSLT` 股數變更
- 匯率更新為 `31.615`（與截圖一致）
- 對照上一版結構保留 23 個頂層 key，不改結構區欄位名稱
- 依對話偏好移除推薦中的 `ORCL` / `NVDA`，改為 `INTC`

### 驗證
- 執行 `python scripts/build_stocks_json.py`：內建 required keys + 子結構驗證全數通過
- 產出檔：`data/stocks.json` 已重建（UTF-8）
- 後續以 `check_live_dashboard.py` 驗證 GitHub Pages 顯示

---

## 2026-05-04 — 美股盤中再分析 + Dashboard 全量更新

**Commit**: `7581a46` — `feat: US re-analysis BigGo 2026-05-04 EDT snapshot`

### 變更
- **報價**：`AIXI`/`AVGO`/`SMH`/`CRWV`/`ONDS`/`SNDK`/`TSLA`/`TSM`/`WDC` 依 BigGo **5/4 ~12:29 EDT**；**2X ETF** 由模板內前收 ×（1+2×底層單日報酬）連結。
- **論述**：`pnl_split.us`、`peak_decision`、`short_term_1m` intro/forecasts、`actions`、`underlying_analysis`、`indices`（台股加權約 **40,550** 僅作儀表參考—`TW` 陣列仍舊）、`news` 新增 5/4 輪動條、`forecast` 微調。
- **產出**：總市值 **NT$825,316**、總損益 **NT$124,432（+17.75%）**。

---

## 2026-05-04 — BigGo 重抓美股報價 + 2X ETF 近似更新

**Commit**: `9931822` / `94ca976` — `merge: US BigGo refresh 2026-05-04`

### 變更
- **資料**：`UPDATE_NOTE` 註記 BigGo **2026-05-04** 重抓；直連標的（`AIXI`/`AVGO`/`SMH`）盤面仍為 **5/1 美東收盤**（與前次相同）。
- **2X ETF**：`CWVX`/`ONDL`/`SNDU`/`TSLT`/`TSMG`/`WDCX` 依底層 **CRWV、ONDS、SNDK、TSLA、TSM、WDC** 之 5/1 漲跌幅做 **單日 2X 近似**（BigGo ETF 頁無收盤列）。
- **連動**：`effective_exposure`、`underlying_analysis`（曝險台幣）、`actions.B/C` 價格與說明、`pnl_split.us.highlight` 已對齊新 `US` 陣列。
- **產出**：`python scripts/build_stocks_json.py` → 總市值約 **NT$824,886**、總損益約 **NT$124,002（+17.69%）**（台股列仍為模板舊收盤，與美股更新混算；若需完全一致請另更新 `TW` 陣列）。

---

## 2026-05-03 — 潛力股 欣興（3037）價錯更正

**Commit**: `292b83e` — `fix: Unimicron 3037 TW BigGo NT$883 replaces wrong NT$210 in picks`

- **問題**：`picks` 將欣興誤載 **NT$210**（與現價差數倍）。
- **正解**：[BigGo 3037.TW](https://finance.biggo.com.tw/quote/3037.TW) — **2026/4/30 收 NT$883**，**+80（約 +9.96%）**，為**注意股**。
- **連動**：`target_low/high` 改為情境參考 **NT$1,000–1,150**，`upside_pct` ≈ **21.8%**；新增 `consensus`／`forecast` 3037 列。

---

## 2026-05-03 — 潛力股 台達電（2308）價錯更正

**Commit**: `3732014` — `fix: Delta 2308 TW BigGo NT$2165 replaces wrong NT$360 in picks`

- **問題**：`picks`、`next_buy_recommendations`、portfolio 觀察清單將 2308 誤載為 **NT$360**。
- **正解**：[BigGo 2308.TW](https://finance.biggo.com.tw/quote/2308.TW) — **2026/4/30 收 NT$2,165**。
- **連動調整**：`target_low/high` 改為情境參考 **NT$2,400–2,650**、`upside_pct` 約 **16.6%**；新增 `consensus`／`forecast` 2308 列；下單說明改為「1 張約 216.5 萬／零股」。
- （**法人目標請您自行核對**，此處級距為佔位，非投顧）。

---

## 2026-05-03 — BigGo/Yahoo 全檔報價重驗 + 更正底層誤植

**Commit**: `ccc7b83` — `fix: verify quotes BigGo Yahoo, correct TSM TSLA WDC underlying 2026-05-03`

### 驗證來源與時間
| 市場 | 來源 | 說明 |
|------|------|------|
| 🇹🇼 台股 7 檔 | [BigGo](https://finance.biggo.com.tw/) | 「今天」為 **2026/4/30 收盤**（週末前最後交易日）|
| 🇺🇸 美股 liquid | BigGo `AVGO`、`SMH`、`AIXI`、`TSMG` 等 | 收盤 **2026/5/1 EDT** |
| 🇺🇸 ETF CWVX/ONDL/SNDU/TSLT/WDCX | **Yahoo Finance**（BigGo 頁無報價列） | 收盤價維持與您截圖一致；**一日漲跌幅**以 Yahoo **最後交易日** 補 |

### 重大更正（先前網頁 `underlying_analysis` 誤植）
| 標的 | 錯誤舊值 | **BigGo 5/1 收盤（正）** |
|------|----------|--------------------------|
| TSM ADR | ~$248 | **$397.67** |
| TSLA | ~$290 | **$390.82** |
| WDC | ~$85 | **$431.52** |

### 其餘欄位校正
- **00631L**：涨跌 **-0.21／-0.73%**（非 +1.45%）。
- **信昌電 6173**：**+1.7／+2.02%**（非先前負向誤填）。
- **AIXI**：**-0.1591／-16.33%**（5/1 單日；累計獲利率仍約 -49%，由總計自行計）。
- **CWVX/ONDL/SNDU**：`change`／`pct` 改為 Yahoo 一日波動。
- **TSMG**：名目改為 BigGo：**Leverage Shares 2× Long TSM Daily**。
- **`consensus` TSM／WDC 目標價級距**：由原過時區間改為「概略／請以最新研報為準」敘述，避免繼續誤導。

### Dashboard 結果（重建後）
- 總市值 **NT$812,096**、總損益 **+NT$111,212（15.87%）** — 持股收盤價未改故與前一版總計相同；**文案與風險提示已反映正確報價**。

---

## 2026-05-02 23:05 — 週末完整深度報告 + 5/4 週一開市策略

**Commit**: `(待 push)` — `update: deep equity report + Monday 5/4 strategy`

### 變更
- **時間軸校正**：將 `tomorrow_tw_strategy.title` 由「星期一（5/5）」改為正確的「星期一（5/4）」
- **新聞區強化**：新增 6 則 — Apple Q3 指引 +14-17%（遠優於市場 +9.5%）、AVGO Q2 $22B (+47%) / AI $10.7B (+140%)、>80% S&P 500 EPS 超預期、伊朗修正版和平方案壓油價、緯穎/日月光最新目標、SanDisk 5 年合約 $42B
- **morning_plan**：擴充至 7 步驟，新增「11:00 緯穎試單」步驟
- **macro_context**：補充 TSMC CoWoS 滿載 2027、Apple 各部門細項、SanDisk Q1 NAND +55-60%
- **one_line**：明示主軸「AIXI/ONDL 必清、日月光/AVGO/台積逢回加、緯穎試單」
- **報價驗證**：BigGo 已驗 2330=NT$2,135、AVGO=$421.28、SMH=$509.82（全與庫存截圖一致）

### 投組總計（無變動）
- 🇹🇼 台股 NT$489,404（+21.0%）
- 🇺🇸 美股 NT$322,691（+8.8%）
- **合計 NT$812,095，總損益 +NT$110,946（+15.83%）**

### 5/4 週一三大行動
1. 🔴 AIXI 50 股 9:00 美股 Market 賣（已等不到 GTC $1.00）
2. 🔴 ONDL 30 股 GTC $18.50 限價賣（盤前掛單）
3. 🟢 台積電 / 日月光 / AVGO / SMH 逢回分批加碼

---

## 2026-05-02 22:55 — 結構固化（v3.1，模板化）

**Commit**: `(待 push)` — `chore: lock schema into scripts/build_stocks_json.py + SCHEMA.md`

### 🔒 結構固化內容

依使用者要求「**之後更新只換值，不要動結構**」，建立三層保護：

1. **官方產生器** — `scripts/build_stocks_json.py`
   - 頂部明確分為「**1. 可變值區**」與「**2. 結構區**」
   - 可變值區：FX、TW 持倉、US 持倉、新聞、財報、picks 等
   - 結構區：所有 23 個頂層欄位 + 子結構，**禁止更動 key 名稱**

2. **Schema 規範** — [`SCHEMA.md`](SCHEMA.md)
   - 23 個頂層欄位完整 TypeScript 類型定義
   - 6 個最容易踩雷的子結構（actions / horizon_views / picks / next_buy / allocation / capital_plan）詳細範例
   - 已知雷區對照表

3. **Cursor Rule** — `f:\代碼\202602\.cursor\rules\stock-dashboard-update.mdc`
   - `alwaysApply: true`：每次助理被要求更新 dashboard 都會自動套用
   - 嚴禁清單 + 唯一正確流程
   - 引用 SCHEMA.md 與 build_stocks_json.py

### 📋 標準更新流程

```powershell
# 1. 編輯模板「可變值區」
code F:\代碼\stock-dashboard\scripts\build_stocks_json.py

# 2. 重建（含 14 項 schema 自動驗證）
$env:PYTHONIOENCODING='utf-8'
python F:\代碼\stock-dashboard\scripts\build_stocks_json.py

# 3. 補 UPDATE_LOG.md（必做）

# 4. 提交推送
cd F:\代碼\stock-dashboard
git add data/stocks.json UPDATE_LOG.md scripts/build_stocks_json.py
git commit -m "update: portfolio YYYY-MM-DD HH:MM"
git push origin master

# 5. 驗證 live
python F:\代碼\字幕\check_live_dashboard.py
```

### 🚫 禁止事項
- ❌ `python push_dashboard.py --fetch`（用 update_data.py 內建錯誤舊持倉覆寫）
- ❌ 從零寫 stocks.json
- ❌ 更動 stocks.json key 名稱

---

## 2026-05-02 22:35 — 修復子結構欄位（v3，解決分頁空白）

**Commit**: `(待 push)` — `fix: align all 23 keys with index.html sub-structure`

### 🔧 v2 還是有問題的原因
v2 補齊了 23 個頂層欄位，但 **子結構欄位名稱跟 index.html 渲染函式預期的不同**，所以選擇「操作 / 預測 / 明日台股 / 資金部署 / 推薦」分頁時仍然空白。

對照 [`index.html`](https://github.com/s07362022/stock-dashboard/blob/master/index.html) JavaScript 渲染函式，必須使用以下精確欄位：

| 區塊 | v2 我寫的（錯） | 正確（v3） |
|------|------------|-----------|
| `actions.A` / `B` | `action`, `ticker`, `shares`, `priority` | `symbol`, `name`, `price`, `target`, `stop`, `strategy` |
| `actions.C` | `action`, `ticker`, `shares`, `priority` | `symbol`, `name`, `price`, `action`, `reason` |
| `picks` | `ticker` | `ticker`（OK）+ 其他 OK |
| `horizon_views.short_term_1m` | `summary`, `tickers` | `intro`, `tw_index{current,bull,base,bear,p_bull...}`, `forecasts[]` |
| `horizon_views.long_term` | `summary`, `tickers` | `intro`, `core_long_term_buys[]`, `satellite_growth[]`, `exit_or_reduce[]` |
| `horizon_views.peak_decision` | `summary` | `current_status`, `verdict`, `actions[{type,items}]`, `cash_target` |
| `horizon_views.tomorrow_tw_strategy` | `summary`, `items` | `macro_context[]`, `morning_plan[{step,action,detail}]`, `watch_list_for_tomorrow[]`, `avoid_list[]`, `risk_alerts[]`, `one_line` |
| `next_buy_recommendations[].tickers` | `["text",...]` | `[{ticker,name,price,rationale,size_suggest,confidence}]` |
| `capital_plan` | 簡化版 | `sources[{src,amount_twd,status,note}]`, `totals{immediate,conditional,total}`, `options[{id,name,philosophy,actions,result}]`, `recommendation{primary,reason,secondary_if_aggressive}`, `risks[]` |
| `allocation.current` / `target` | `{key:value,...}` 物件 | `[{label,value},...]` 陣列 |

### ✅ v3 修正
重寫 `rebuild_stocks_json_v2.py`，所有子結構嚴格對齊渲染函式預期。新增 14 項自動驗證 — 全部通過。

### 📊 持倉概況（同 v2，未變動）
- 總市值 NT$ 812,096（+15.87%）
- 台股 7 檔 NT$ 489,404（+21.0%）
- 美股 9 檔 NT$ 322,691（+8.8%）／USD $10,192

---

## 2026-05-02 18:00 — 修復顯示問題（v2）

**Commit**: `(待 push)` — `restore: full schema with all 23 keys`

### 🔧 修復內容
- ❌ **前次問題**：上一版 commit `6210250` 寫入的 `stocks.json` 只有 5 個頂層欄位（`updated_at`、`tw_stocks`、`us_stocks`、`watchlist`、`summary`），缺少網頁所需的 18 個欄位（`fx_rate`、`user_strategy`、`pnl_split`、`indices`、`effective_exposure`、`underlying_analysis`、`horizon_views`、`news`、`earnings`、`analysts`、`picks`、`actions`、`next_buy_recommendations`、`allocation`、`consensus`、`forecast`、`capital_plan`），導致圖表/分析師/新聞/財報等所有區塊空白。
- ✅ **本次修復**：以前一版 (`371d642`) schema 為基礎，重建 23 個完整欄位，並用 2026/05/02 最新持倉資料替換。

### 📊 持倉變更（vs 4/30）
| 項目 | 變更 |
|------|------|
| AVGU（27 股） | ❌ 出清 |
| AAOX（3 股） | ❌ 出清 |
| AIXI | 150 → 50 股 |
| CWVX | 4 → 19 股 |
| ONDL | 20 → 30 股 |
| SNDU | 3 → 16 股 |
| WDCX | ✨ 新建倉 4 股 @ $65.06 |

### 💰 投組概況
- **總市值**：NT$ 812,096
- **總損益**：+NT$ 111,213（**+15.87%**）
- **台股**：NT$ 489,404（+21.08%）
- **美股**：NT$ 322,691（+8.77%）／USD $10,192

### 🌐 大盤
- S&P 500：7,230（+0.29%，連六週新高）
- NASDAQ：25,114（+0.89%）
- SOX：10,595（+0.87%）
- VIX：16.89（-10%+）

---

## 2026-05-02 17:11 — Daily update（v1，有問題）

**Commit**: `1157181` Daily update 2026-05-02 17:11
**Commit**: `6210250` fix: update portfolio to correct holdings 2026-05-02

### ⚠️ 已知問題
- `push_dashboard.py --fetch` 用內建 `generate_report.py` 抓取股價，但內建股票清單為**舊持倉**（聯發科、華邦電、SIDU、SOFI 等），覆寫了正確資料。
- 後續手動修正只填了 5 個頂層欄位，**遺失** news/earnings/analysts 等 18 個欄位 → 網頁多區塊空白。

---

## 2026-04-30 19:15 — 完整 schema v5

**Commit**: `371d642` fix: restore full stocks.json schema (news/earnings/votes)

- 完整 23 欄位 schema：
  - `updated_at`, `fx_rate`, `user_strategy`
  - `summary`, `pnl_split`, `indices`
  - `tw_stocks`, `us_stocks`
  - `effective_exposure`, `underlying_analysis`, `horizon_views`
  - `news`, `earnings`, `analysts`
  - `picks`, `actions`, `next_buy_recommendations`
  - `allocation`, `consensus`, `forecast`, `capital_plan`

---

## 📐 stocks.json Schema 規範（必備欄位）

每次更新 stocks.json **必須**包含以下 23 個頂層欄位，否則網頁區塊將空白：

```typescript
{
  updated_at: string;          // "2026-05-02 18:00"
  updated_at_utc: string;
  fx_rate: number;             // 31.66
  user_strategy: { philosophy, leverage_map };
  summary: { total/tw/us 各種小計 };
  pnl_split: { tw, us };
  indices: Index[];            // SPX, IXIC, SOX, TWII...
  tw_stocks: Stock[];          // 完整欄位 incl. weight, tag, sector
  us_stocks: USStock[];        // 額外 market_value_usd / underlying / multiplier
  effective_exposure: Exposure[];
  underlying_analysis: Underlying[];
  horizon_views: { short_term_1m, long_term, peak_decision, tomorrow_tw_strategy };
  news: News[];                // ≥ 20 條
  earnings: Earnings[];
  analysts: { panel: 19 人, votes: VotesPerStock[] };
  picks: Pick[];               // 5 檔 (台3 + 美2)
  actions: { A, B, C };
  next_buy_recommendations: Scenario[];
  allocation: { current, target };
  consensus: Consensus[];
  forecast: Forecast[];
  capital_plan: { sources, totals, options, recommendation, risks };
}
```

**⚠️ 重要**：直接執行 `python push_dashboard.py --fetch` 會用內建腳本覆寫成簡化版本，**不要這樣做**。請改用：

```powershell
# 1. 用自訂腳本重建 stocks.json
python "F:\代碼\字幕\rebuild_stocks_json.py"

# 2. 推送（不加 --fetch）
cd "F:\代碼\stock-dashboard"
git add data/stocks.json UPDATE_LOG.md
git commit -m "update: portfolio YYYY-MM-DD HH:MM"
git push origin master
```

---

## 🔗 相關檔案

- 重建腳本：`F:\代碼\字幕\rebuild_stocks_json.py`
- 寄信腳本：`F:\代碼\字幕\send_report_20260502.py`
- 持倉檔：`C:\Users\User\.cursor\skills\stock-analyzer\portfolio.md`
- Live Dashboard：https://s07362022.github.io/stock-dashboard/
