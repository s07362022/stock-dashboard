# 📋 Stock Dashboard 更新日誌

> 每次更新網頁皆記錄於此，按日期倒序排列。
> Live: https://s07362022.github.io/stock-dashboard/

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
