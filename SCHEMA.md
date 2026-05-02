# 📐 stocks.json Schema 規範（v3，2026-05-02 起）

> **本文件為 `index.html` 渲染函式所需的 stocks.json 完整欄位規範。**
> 任何 stocks.json 變更必須符合本規範，否則網頁分頁將空白。
> 唯一允許的產生器：[`scripts/build_stocks_json.py`](scripts/build_stocks_json.py)

---

## ⚠️ 關鍵規則

1. **23 個頂層欄位**全部必備，缺一個分頁就會壞
2. **子結構欄位名稱**必須跟 `index.html` 渲染函式預期完全一致
3. **不要用** `update_data.py` 或 `push_dashboard.py --fetch` —— 它們會用內建錯誤的舊持倉清單覆寫
4. **每次更新只改值**，不要動結構

---

## 📋 23 個頂層欄位清單

| # | 欄位 | 類型 | 用途 | index.html 渲染函式 |
|---|------|------|------|-------------------|
| 1 | `updated_at` | string | 更新時間 (`YYYY-MM-DD HH:MM`) | `boot()` |
| 2 | `updated_at_utc` | string | UTC 時間 | (備用) |
| 3 | `fx_rate` | number | 匯率 USD→TWD | `boot()` |
| 4 | `user_strategy` | object | 哲學 + 槓桿映射 | `renderLeverage()` |
| 5 | `summary` | object | 投組總覽（21 個子欄位） | `renderKPI()` |
| 6 | `pnl_split` | object | 台股/美股分開損益 | (圖表) |
| 7 | `indices` | array | 大盤指數 | `renderRibbon()` |
| 8 | `tw_stocks` | array | 台股持倉 | `renderHoldings()` |
| 9 | `us_stocks` | array | 美股持倉 | `renderHoldings()` |
| 10 | `effective_exposure` | array | 槓桿後實質曝險 | `renderLeverage()` |
| 11 | `underlying_analysis` | array | 底層公司深度分析 | `renderLeverage()` |
| 12 | `horizon_views` | object | 短/長/決策/明日 4 個子物件 | `renderHorizon()`, `renderTomorrow()` |
| 13 | `news` | array | 新聞 | `renderNews()` |
| 14 | `earnings` | array | 財報 | `renderEarnings()` |
| 15 | `analysts` | object | 19 位分析師投票 | `renderVotes()` |
| 16 | `picks` | array | 5 檔潛力股 | `renderPicks()` |
| 17 | `actions` | object | A/B/C 操作建議 | `renderActions()` |
| 18 | `next_buy_recommendations` | array | 下單推薦 | `renderLeverage()` |
| 19 | `allocation` | object | 配置現狀 vs 目標 | (圖表) |
| 20 | `consensus` | array | 機構共識 | `renderConsensus()` |
| 21 | `forecast` | array | 個股 1-3 月預測 | (圖表) |
| 22 | `capital_plan` | object | 資金部署 3 方案 | `renderCapital()` |
| 23 | `update_log` | string | UPDATE_LOG.md 連結 | (備用) |

---

## 📐 關鍵子結構欄位（最容易踩雷的地方）

### `actions.A` / `actions.B`（A 首選 / B 衛星）

```typescript
{
  symbol: string;     // 必須
  name: string;       // 必須
  price: number;      // 必須
  target: string;     // 必須（區間字串，例 "540-588"）
  stop: number;       // 必須（停損價）
  strategy: string;   // 必須（策略說明）
}
```

❌ 禁止用 `action`, `ticker`, `shares`, `priority`

### `actions.C`（高風險出清）

```typescript
{
  symbol: string;
  name: string;
  price: number;
  action: string;     // 必須（具體動作）
  reason: string;     // 必須（原因）
}
```

❌ 禁止用 `target`, `stop`, `strategy`

### `picks`（潛力股推薦）

```typescript
{
  rank: number;
  ticker: string;          // ⚠ 是 "ticker" 不是 "symbol"
  name: string;
  market: "TW" | "US";
  price: number;
  target_low: number;
  target_high: number;
  upside_pct: number;
  thesis: string;
  type: string;
}
```

### `horizon_views.short_term_1m`（短線預測）

```typescript
{
  title: string;
  intro: string;            // ⚠ 不是 "summary"
  tw_index: {
    current: number;
    bull: number; p_bull: number;
    base: number; p_base: number;
    bear: number; p_bear: number;
    scenario: string;
  };
  forecasts: [{
    symbol: string; name: string;
    current: number; bull: number; base: number; bear: number;
    view: string;
  }];                       // ⚠ 不是 "tickers"
}
```

### `horizon_views.long_term`

```typescript
{
  title: string;
  intro: string;
  core_long_term_buys: [{symbol, name, view}];   // ⚠ 不是 "tickers"
  satellite_growth: [{symbol, name, view}];
  exit_or_reduce: [{symbol, name, view}];
}
```

### `horizon_views.peak_decision`

```typescript
{
  title: string;
  current_status: string;   // ⚠ 不是 "summary"
  verdict: string;
  actions: [{
    type: string;           // 例如 "🟢 加碼（趁回檔）"
    items: string[];        // 動作清單
  }];
  cash_target: string;
}
```

### `horizon_views.tomorrow_tw_strategy`（明日台股）

```typescript
{
  title: string;
  macro_context: string[];                        // ⚠ 不是 "summary"
  morning_plan: [{step: number, action: string, detail: string}];
  watch_list_for_tomorrow: [{symbol, name, buy_zone, target, action}];
  avoid_list: [{symbol, name, reason}];
  risk_alerts: string[];
  one_line: string;
}
```

### `next_buy_recommendations[].tickers`

```typescript
[{
  ticker: string;
  name: string;
  price: number;
  rationale: string;
  size_suggest: string;     // 例 "1 股 ≈ NT$ 13,338"
  confidence: string;       // 例 "🟢 高"
}]
```

❌ **不要寫成** `["AVGO", "ANET", ...]` 字串陣列

### `allocation`

```typescript
{
  current: [{label: string, value: number}];   // ⚠ 陣列，不是物件
  target:  [{label: string, value: number}];
}
```

❌ **不要寫成** `{ "0050": 44.6, "AVGO": 18.5, ... }` 物件

### `capital_plan`

```typescript
{
  title: string;
  sources: [{
    src: string;
    amount_twd: number;
    amount_usd: number | null;
    status: "immediate" | "conditional" | "invest";
    note: string;
  }];
  totals: {immediate: number, conditional: number, total: number};
  context: string[];
  options: [{
    id: "A" | "B" | "C";
    name: string;
    philosophy: string;
    actions: [{step: number, fund: string, use: string, rationale: string}];
    result: {
      post_tw_pct: number; post_us_pct: number;
      post_cash_pct: number; post_leveraged_pct: number;
      summary: string;
    };
  }];
  recommendation: {
    primary: "A" | "B" | "C";       // ⚠ 必須
    reason: string;
    secondary_if_aggressive: string;
  };
  risks: string[];
}
```

---

## ✅ 自動驗證

`build_stocks_json.py` 結尾會跑 14 項驗證：

```
[OK] actions.A[0].strategy
[OK] actions.A[0].stop
[OK] actions.C[0].action
[OK] actions.C[0].reason
[OK] horizon_views.short_term_1m.tw_index
[OK] horizon_views.short_term_1m.forecasts
[OK] horizon_views.long_term.core_long_term_buys
[OK] horizon_views.peak_decision.actions
[OK] horizon_views.tomorrow_tw_strategy.morning_plan
[OK] next_buy_recommendations[0].tickers[0].rationale
[OK] allocation.current[0].label
[OK] capital_plan.options[0].actions[0].rationale
[OK] capital_plan.recommendation.primary
[OK] capital_plan.totals.immediate
```

任何 `[FAIL]` 都不要 push。

---

## 🔄 標準更新流程

```powershell
# 1. 編輯模板（只改值，不改結構）
code F:\代碼\stock-dashboard\scripts\build_stocks_json.py

# 2. 重建 stocks.json
$env:PYTHONIOENCODING='utf-8'
python F:\代碼\stock-dashboard\scripts\build_stocks_json.py

# 3. 更新 UPDATE_LOG.md（必做）
code F:\代碼\stock-dashboard\UPDATE_LOG.md

# 4. 提交與推送
cd F:\代碼\stock-dashboard
git add data/stocks.json UPDATE_LOG.md scripts/build_stocks_json.py
git commit -m "update: portfolio YYYY-MM-DD HH:MM"
git push origin master

# 5. 等 1-3 分鐘 GitHub Pages 部署
# Live: https://s07362022.github.io/stock-dashboard/
```

---

## 🚫 已知雷區

| 錯誤做法 | 後果 | 正確做法 |
|---------|------|---------|
| `python push_dashboard.py --fetch` | 用 update_data.py 內建錯誤舊持倉覆寫 | 用 `build_stocks_json.py` |
| 只寫 5 個頂層欄位 | 18 個分頁空白 | 必備 23 個 |
| `actions.A` 用 `action/ticker/priority` | 操作分頁空白 | 用 `symbol/name/price/target/stop/strategy` |
| `horizon_views.long_term` 用 `tickers` | 長期分頁空白 | 用 `core_long_term_buys/satellite_growth/exit_or_reduce` |
| `allocation` 用物件 | 配置圖表空白 | 用 `[{label,value}]` 陣列 |
| `next_buy_recommendations[].tickers` 用字串陣列 | 推薦分頁空白 | 用 `[{ticker,name,price,rationale,size_suggest,confidence}]` |

---

**最後更新**：2026-05-02 22:50
**規範版本**：v3
