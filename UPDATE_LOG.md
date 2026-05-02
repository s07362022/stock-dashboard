# 📋 Stock Dashboard 更新日誌

> 每次更新網頁皆記錄於此，按日期倒序排列。
> Live: https://s07362022.github.io/stock-dashboard/

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
