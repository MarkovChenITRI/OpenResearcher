# OpenResearcher 使用完整說明

## ❓ 您的三個問題

### 1. 一定要先寫好研究問題的檔案嗎？

**答案：是的，目前必須事先準備檔案**

OpenResearcher 是一個**命令列工具（CLI）**，**沒有提供本地互動式 UI**。使用方式有兩種：

#### 方式 A：使用預設 Benchmark（不需要寫檔案）
```bash
# 直接使用內建的 GAIA、BrowseComp、xbench 等資料集
python deploy_agent.py \
    --vllm_server_url AZURE_OPENAI \
    --dataset_name gaia \              # 使用預設的 103 個問題
    --browser_backend serper \
    --output_dir results/gaia
```

**可用的預設資料集**：
- `gaia` - 103 個英文問答（自動下載）
- `browsecomp` - 1,266 個瀏覽器問題（自動下載）
- `xbench` - 100 個中文深度搜尋問題（自動下載）
- `browsecomp-plus` - 830 個問題（需要手動下載資料）

#### 方式 B：自訂問題（需要先寫檔案）
```bash
# 1. 先建立問題檔案 my_questions.json
cat > my_questions.json << 'EOF'
[
  {
    "qid": "unique_id_1",
    "question": "Survey Vision Transformer papers (2020-2026)",
    "answer": ""
  },
  {
    "qid": "unique_id_2", 
    "question": "Explain quantum computing in simple terms",
    "answer": ""
  }
]
EOF

# 2. 執行研究
python deploy_agent.py \
    --vllm_server_url AZURE_OPENAI \
    --dataset_name custom \            # 使用自訂問題
    --data_path my_questions.json \    # 指定檔案路徑
    --browser_backend serper \
    --output_dir results/my_research
```

#### 💡 快速建立問題檔案（PowerShell）
```powershell
# 互動式建立
$questions = @()
do {
    $id = Read-Host "問題 ID (例如: q1)"
    $question = Read-Host "問題內容"
    $questions += @{qid=$id; question=$question; answer=""}
    $continue = Read-Host "繼續新增問題? (y/n)"
} while ($continue -eq 'y')

$questions | ConvertTo-Json | Out-File questions.json -Encoding utf8
Write-Host "✅ 已建立 questions.json"
```

#### 🌐 有 UI 嗎？

**本地沒有 UI**，但可以使用：

1. **HuggingFace Demo**（線上）
   - URL: https://huggingface.co/spaces/OpenResearcher/OpenResearcher
   - 可以直接輸入問題，使用網頁介面
   - 使用 Gradio 框架

2. **本地沒有內建 UI**
   - 這是一個研究工具/命令列工具
   - 設計用於批次處理大量問題
   - 適合研究人員、開發者使用

---

### 2. Browser 沒有提供 API？

**browser_backend 是指網頁搜尋的方式，有兩種選擇：**

#### 選項 1：`serper` - Serper API（推薦）

```bash
--browser_backend serper
```

**這是一個付費的 Google 搜尋 API 服務**：
- 官網：https://serper.dev/
- 免費額度：2,500 次搜尋
- 付費方案：$50/月 = 5萬次搜尋

**設定步驟**：
```bash
# 1. 註冊 Serper 帳號並取得 API Key
# 2. 在 .env 中設定
echo "SERPER_API_KEY=your_api_key_here" >> .env

# 3. 使用
python deploy_agent.py \
    --browser_backend serper \
    ...
```

**Serper 會做什麼**：
- 搜尋 Google（`browser.search`）
- 開啟網頁並提取內容（`browser.open`）
- 在網頁中搜尋關鍵字（`browser.find`）

#### 選項 2：`local` - 本地搜尋引擎

```bash
--browser_backend local \
--search_url http://localhost:8000
```

**這需要您自己架設搜尋服務**：
```bash
# 啟動本地搜尋服務（需要下載索引）
bash scripts/start_search_service.sh dense 8000
```

**限制**：
- ❌ 僅支援 `browsecomp-plus` benchmark
- ❌ 不支援 Azure OpenAI（因為需要本地索引）
- ❌ 需要下載大量資料（corpus + embeddings）

#### 🤔 為什麼需要 Browser API？

OpenResearcher 是一個**深度研究 Agent**，會執行以下流程：

```
問題 → 搜尋網頁 → 瀏覽多個網站 → 提取資訊 → 推理 → 產生答案
      ↑____________Browser Backend_____________↑
```

**範例：研究 "Vision Transformer 論文調查"**

1. **搜尋**：`browser.search("Vision Transformer papers 2020-2026")`
   - 找到相關網頁連結

2. **瀏覽**：`browser.open("https://arxiv.org/abs/2010.11929")`
   - 開啟論文頁面
   - 提取標題、作者、摘要

3. **查找**：`browser.find("benchmark results")`
   - 在頁面中搜尋特定資訊

4. **推理**：GPT-5.4 分析所有資訊
   - 整理成文獻調查報告

**沒有 Browser Backend 會怎樣？**
- ❌ 無法搜尋網路
- ❌ 只能依靠模型內建知識（可能過時）
- ❌ 無法驗證事實

---

### 3. 最後的結果會輸出什麼？

結果會儲存在 `--output_dir` 指定的目錄中，格式為 **JSONL**（每行一個 JSON 物件）。

#### 輸出檔案結構

```
results/gaia_azure/
└── node_0_shard_0.jsonl    # 主要結果檔案
```

#### 結果檔案內容（JSONL 格式）

每行是一個完整的研究記錄：

```jsonl
{"qid": "問題ID", "question": "問題內容", "messages": [...對話歷史...], "answer": "最終答案", "latency_s": 執行時間, "status": "success"}
```

#### 詳細範例

```json
{
  "qid": "gaia_001",
  "question": "What is the capital of France?",
  "messages": [
    {
      "role": "system",
      "content": "You are a research assistant with browser tools..."
    },
    {
      "role": "user", 
      "content": "What is the capital of France?"
    },
    {
      "role": "assistant",
      "content": "I'll search for this information.",
      "tool_calls": [
        {
          "function": {
            "name": "browser.search",
            "arguments": "{\"query\": \"capital of France\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "name": "browser.search",
      "content": "Search results: 1. Paris - Wikipedia..."
    },
    {
      "role": "assistant",
      "content": "The capital of France is Paris."
    }
  ],
  "answer": "Paris",
  "latency_s": 12.5,
  "status": "success",
  "attempts": 1
}
```

#### 查看結果的方式

**方式 1：使用 PowerShell**
```powershell
# 查看所有結果
Get-Content results/gaia_azure/node_0_shard_0.jsonl | ConvertFrom-Json

# 只看問題和答案
Get-Content results/gaia_azure/node_0_shard_0.jsonl | 
    ConvertFrom-Json | 
    Select-Object qid, question, answer

# 匯出成可讀的格式
Get-Content results/gaia_azure/node_0_shard_0.jsonl | 
    ConvertFrom-Json | 
    ConvertTo-Json -Depth 10 | 
    Out-File results_readable.json -Encoding utf8

# 統計成功率
$results = Get-Content results/gaia_azure/node_0_shard_0.jsonl | ConvertFrom-Json
$success = ($results | Where-Object {$_.status -eq "success"}).Count
$total = $results.Count
Write-Host "成功率: $success / $total"
```

**方式 2：使用評估工具**
```bash
# 自動評估答案正確率
python eval.py --input_dir results/gaia_azure

# 輸出評估報告
```

**方式 3：使用 Python**
```python
import json

# 讀取結果
with open('results/gaia_azure/node_0_shard_0.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        result = json.loads(line)
        print(f"問題: {result['question']}")
        print(f"答案: {result['answer']}")
        print(f"用時: {result['latency_s']}秒")
        print("-" * 50)
```

#### 結果包含的資訊

| 欄位 | 說明 | 範例 |
|------|------|------|
| `qid` | 問題 ID | `"gaia_001"` |
| `question` | 原始問題 | `"What is the capital of France?"` |
| `answer` | 最終答案 | `"Paris"` |
| `messages` | 完整對話歷史 | 陣列，包含所有輪次 |
| `latency_s` | 執行時間（秒） | `12.5` |
| `status` | 執行狀態 | `"success"` / `"fail"` |
| `attempts` | 嘗試次數 | `1` |
| `error` | 錯誤訊息（如果失敗） | 錯誤詳情 |

#### 對話歷史（messages）詳細內容

包含完整的推理過程：
- 系統提示詞
- 使用者問題
- AI 的思考過程
- 工具呼叫（搜尋、瀏覽）
- 工具回傳的結果
- AI 的最終答案

**這讓您可以**：
- 📊 追蹤 AI 的推理路徑
- 🔍 檢查搜尋了哪些網站
- 🐛 Debug 錯誤答案
- 📈 分析研究品質

---

## 🎯 完整工作流程範例

### 情境：研究 Vision Transformer 論文

```powershell
# 1. 建立研究問題
@"
[
  {
    "qid": "vit_survey",
    "question": "Survey Vision Transformer papers (2020-2026). List top 15 papers with: 1) Title and authors, 2) Key innovations, 3) Benchmark results, 4) Citations. Include paper links.",
    "answer": ""
  }
]
"@ | Out-File vit_research.json -Encoding utf8

# 2. 執行深度研究（需要 20-30 分鐘）
python deploy_agent.py `
    --vllm_server_url AZURE_OPENAI `
    --dataset_name custom `
    --data_path vit_research.json `
    --browser_backend serper `
    --output_dir results/vit_survey `
    --model_name_or_path gpt-5.4

# 3. 查看結果
Get-Content results/vit_survey/node_0_shard_0.jsonl | ConvertFrom-Json | Select-Object -ExpandProperty answer

# 4. 匯出成 Markdown 報告
$result = Get-Content results/vit_survey/node_0_shard_0.jsonl | ConvertFrom-Json
@"
# Vision Transformer 文獻調查報告

**研究日期**: $(Get-Date -Format 'yyyy-MM-dd')
**執行時間**: $($result.latency_s) 秒

## 研究結果

$($result.answer)

## 完整對話歷史

$(($result.messages | ForEach-Object { "### $($_.role)`n$($_.content)`n" }) -join "`n")
"@ | Out-File vit_report.md -Encoding utf8

Write-Host "✅ 報告已儲存至 vit_report.md"
```

---

## 💡 總結

| 問題 | 答案 |
|------|------|
| **需要事先寫檔案嗎？** | 自訂問題需要，但可以用預設 benchmark（gaia、browsecomp、xbench） |
| **有 UI 嗎？** | 本地沒有，但可用 HuggingFace 線上 Demo |
| **Browser API 是什麼？** | Serper Google Search API（付費），或本地搜尋引擎 |
| **結果是什麼？** | JSONL 檔案，包含問題、答案、完整對話歷史、執行時間 |
| **如何查看結果？** | PowerShell、Python、或評估工具（`eval.py`） |

**這是一個命令列批次處理工具，不是互動式聊天介面** ✅
