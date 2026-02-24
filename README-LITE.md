# Daily Market Digest - 精簡版

自動化財經分析報告系統（LLM + 多資料源 + 自動排程）

---

## 系統架構

```
collectors/ (資料收集)     →  analyzers/ (LLM 分析)  →  outputs/ (Notion)
├── NewsCollector              ├── NewsAnalyzer            ├── Markdown
├── StockCollector             ├── StockAnalyzer           └── NotionPublisher
├── YouTubeCollector           ├── VideoAnalyzer
├── SECEdgarCollector          └── IndustryAnalyzer (6-step)
├── FDACollector
├── ArxivCollector
└── IntelAggregator
```

---

## 報告類型與排程

| 報告 | 台北時間 | Cron (UTC) | LLM 調用 |
|------|----------|------------|----------|
| Pre-market | 18:00 (週一至五) | `0 10 * * 1-5` | 6 次 |
| Post-market | 08:00 (週二至六) | `0 0 * * 2-6` | 4 次 |
| Saturday | 09:00 (週六) | `0 1 * * 6` | 5 次 (6-step) |
| Sunday | 18:00 (週日) | `0 10 * * 0` | 3 次 |

---

## LLM 設定

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=16384,
    ),
)
```

---

## 核心 Prompts

### 1. 全球快覽

```
你是一位全球財經早報編輯，風格簡潔有力。

請生成「隔夜核心行情」快覽：
● [資產名稱]: [價格] [漲跌幅] ([一句話市場解讀])

要求：
1. 括號內解讀精準點出漲跌原因
2. 只用 4-6 個 bullet points

### 今日關鍵主題
🏛️ **宏觀**: [10-15字]
⚡ **科技**: [10-15字]
🏢 **產業**: [10-15字]
```

### 2. 新聞分類

```
將新聞分類為：
- 宏觀與政策：央行、財政、地緣政治
- 科技與地緣：AI、晶片、中美競爭
- 巨頭與產業：財報、併購、商品

輸出格式：
◆ **[標題8-12字]**
[2-3句說明，包含市場影響]

每類最多 4 條
```

### 3. 市場分析

```
你是頂尖投資顧問。

【最重要原則】
所有分析必須 100% 基於「今日新聞」推導。
禁止「假設」「可能」等空泛措辭。

分析框架：
1. 今日市場解讀
2. 總經與政策環境
3. 市場情緒與風險評估
4. 資金流向與配置建議
5. 操作建議（標的、價位、停損）
```

### 4. 收盤覆盤

```
你是專業投資顧問，進行收盤後覆盤。

輸入：盤前報告（預測）+ 實際收盤數據

框架：
1. 預期 vs 現實對比
2. 實際驅動因素
3. 預測準確度評估
4. 需要調整的策略
```

### 5. 產業分析 - 資料分類 (Step 2)

```
【本步驟限制】
- 不允許第一性原則、宏觀解釋、高階推論
- 不允許「本質上」「從根本上」等抽象語言
- 僅限訊號分類與重要性篩選

分類為：
a) 直接事實
b) 行為訊號
c) 約束或激勵線索
d) 噪音

列出 5-8 個「高信號事件」
```

### 6. 產業分析 - 範式移轉 (Step 3)

```
【範式移轉必要條件】

必須先回答，否則不得宣稱範式移轉：

1. 哪個「不可壓縮的基本約束」正在改變？
2. 過去為何不可突破？現在什麼改變？
3. 從第一性原則推導，行業結構是否必然改寫？

標註：【First-principles lens】，不超過 3 句話

變化類型：
- 成本曲線改變
- 性能曲線躍遷
- 供給約束改變
- 合規邊界移動

表述為「從 A → B」句型
```

### 7. 產業分析 - 技術分析 (Step 4)

```
【第一性原則下的工作拆解】

- 該工作的不可再分單位是什麼？
- 人類過去為何必須親自完成？
- 技術是替代、加速、還是重構？

禁止：功能清單、「效率提升」「更聰明」等詞

框架：
1. Capability Delta - 新增什麼以前做不到的能力
2. Workflow Rewrite - Before vs After
3. Elite Usage Pattern - 任務如何被拆解
4. New Bottleneck - 問題從哪轉移到哪
```

### 8. 產業分析 - 公司分析 (Step 5)

```
【必要輸出】
明確指出至少一個【Constraint that cannot be negotiated】
例如：資本結構、算力、監管風險、組織治理成本

框架：
1. 表層動作
2. 隱含約束
3. 戰略意圖（守什麼？打什麼？延遲什麼？）
4. 外溢影響（供應鏈、競爭者、客戶）
5. 下一個可觀測信號
```

### 9. 產業分析 - 最終報告 (Step 6)

```
讀者：頂尖管理顧問與投資顧問
- 學習速度極快
- 不預設熟悉單一產業
- 對「資訊重述」零容忍

報告結構：
0. This Week's Thesis（一句話）
1. Executive Brief（8 條高密度洞察）
2. Paradigm Shift Radar
3. Industry Cognition Map Updates
4. Technology Frontier
5. Company Moves & Strategic Implications
6. IP / Regulation / Talent Signals
7. Key Metrics & Benchmarks
8. Watchlist & Scenarios

寫作要求：
- 顧問語言，非媒體語言
- 區分【事實】【推論】【假說】
- 禁止「震驚」「重磅」等形容詞
```

---

## 環境變數

```env
GEMINI_API_KEY=xxx
YOUTUBE_API_KEY=xxx
NOTION_API_KEY=xxx
NOTION_DATABASE_ID=xxx
```

---

## 成本

| 報告 | 成本/篇 |
|------|---------|
| Pre-market | ~$0.005 |
| Post-market | ~$0.003 |
| Saturday | ~$0.009 |
| Sunday | ~$0.004 |
| **月總計** | **~$0.24** |

---

## 執行

```bash
python -m src.main pre-market
python -m src.main post-market
python -m src.main saturday
python -m src.main sunday
```
