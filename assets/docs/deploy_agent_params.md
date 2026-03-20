# deploy_agent.py 參數說明

## 命令範例

```bash
python deploy_agent.py \
    --vllm_server_url AZURE_OPENAI \
    --dataset_name gaia \
    --browser_backend serper \
    --output_dir results/gaia_azure
```

## 參數詳解

### 🔧 必要參數

#### `--output_dir` (必填)
**作用**：指定研究結果的儲存目錄

**範例**：
```bash
--output_dir results/gaia_azure
--output_dir outputs/my_research
--output_dir /path/to/save/results
```

**產生的檔案**：
- `node_0_shard_0.jsonl` - 研究結果（JSONL 格式，每行一個 JSON 物件）
- 包含完整的對話歷史、搜尋結果、最終答案

**查看結果**：
```powershell
# 列出結果檔案
ls results/gaia_azure/

# 查看 JSON 內容
Get-Content results/gaia_azure/node_0_shard_0.jsonl | ConvertFrom-Json

# 只看最終答案
Get-Content results/gaia_azure/node_0_shard_0.jsonl | ConvertFrom-Json | Select-Object -ExpandProperty messages | Select-Object -Last 1
```

---

#### `--vllm_server_url` (必填)
**作用**：指定語言模型服務的 URL

**三種模式**：

1. **Azure OpenAI**（我們的整合）
   ```bash
   --vllm_server_url AZURE_OPENAI
   ```
   - 特殊關鍵字，會自動從 `.env` 讀取 Azure 憑證
   - 需要在 `.env` 設定：
     - `AZURE_OPENAI_ENDPOINT`
     - `AZURE_OPENAI_DEPLOYMENT`
     - `AZURE_OPENAI_API_KEY`
     - `AZURE_OPENAI_API_VERSION`

2. **外部 vLLM 服務器**（原始設計）
   ```bash
   # 單一服務器
   --vllm_server_url http://localhost:8001/v1
   
   # 多個服務器（負載平衡）
   --vllm_server_url http://localhost:8001/v1,http://localhost:8002/v1
   ```
   - 連接到已啟動的 vLLM OpenAI 相容 API 服務器
   - 支援多個 URL（逗號分隔）進行負載平衡

3. **不指定**（使用本地模型）
   ```bash
   # 不指定此參數，會在本地直接載入模型
   python deploy_agent.py --model_name_or_path OpenResearcher/OpenResearcher-30B-A3B ...
   ```
   - 需要 GPU
   - 啟動較慢（需要載入模型到記憶體）

---

#### `--dataset_name` (必填)
**作用**：指定要使用的資料集類型

**可用選項**：

1. **`gaia`** - GAIA 文字問答 Benchmark
   ```bash
   --dataset_name gaia
   ```
   - 103 個文字問答題目
   - 評估 LLM 的推理和資訊檢索能力
   - 自動下載資料集

2. **`browsecomp`** - BrowseComp 瀏覽器 Benchmark
   ```bash
   --dataset_name browsecomp
   ```
   - 1,266 個需要網頁瀏覽的問題
   - 測試瀏覽代理能力

3. **`browsecomp-plus`** - BrowseComp-Plus（需要本地搜尋）
   ```bash
   --dataset_name browsecomp-plus
   --data_path data/browsecomp-plus/  # 需要指定資料路徑
   ```
   - 830 個深度研究題目
   - ⚠️ 需要本地搜尋引擎，不支援 Azure OpenAI

4. **`xbench`** - xbench-DeepResearch 中文 Benchmark
   ```bash
   --dataset_name xbench
   ```
   - 100 個中文深度搜尋問題
   - 測試中文深度研究能力

5. **`custom`** - 自訂問題
   ```bash
   --dataset_name custom
   --data_path my_questions.json
   ```
   - 使用您自己的問題檔案
   - 需要 `--data_path` 指定 JSON 檔案

**自訂問題檔案格式**：
```json
[
  {
    "qid": "unique_id_1",
    "question": "您的研究問題",
    "answer": ""
  },
  {
    "qid": "unique_id_2",
    "question": "另一個問題",
    "answer": ""
  }
]
```

---

#### `--browser_backend` (必填)
**作用**：指定網頁搜尋的後端服務

**兩種選擇**：

1. **`serper`** - Serper Google Search API（推薦用於 Azure）
   ```bash
   --browser_backend serper
   ```
   - 使用 Serper 提供的 Google 搜尋 API
   - 需要在 `.env` 設定 `SERPER_API_KEY`
   - 取得金鑰：https://serper.dev/
   - ✅ 支援所有 benchmark（除了 browsecomp-plus）
   - ✅ 與 Azure OpenAI 相容

2. **`local`** - 本地搜尋引擎（僅限 browsecomp-plus）
   ```bash
   --browser_backend local
   --search_url http://localhost:8000  # 需要指定搜尋服務 URL
   ```
   - 使用本地部署的 BM25 或 Dense 搜尋服務
   - 僅適用於 `browsecomp-plus` benchmark
   - 需要先啟動搜尋服務：
     ```bash
     bash scripts/start_search_service.sh dense 8000
     ```
   - ❌ 不支援 Azure OpenAI

**Serper API 設定**：
```bash
# 在 .env 中新增
SERPER_API_KEY=your_serper_api_key_here
```

---

### 📊 進階參數（選用）

#### `--model_name_or_path`
**預設值**：無（通常需要指定）

**作用**：指定模型名稱或路徑

**範例**：
```bash
# 使用 Azure OpenAI 時（僅用於日誌顯示）
--model_name_or_path gpt-5.4

# 使用 vLLM 服務器時
--model_name_or_path OpenResearcher/OpenResearcher-30B-A3B

# 使用本地模型時（模型路徑）
--model_name_or_path /path/to/local/model
```

---

#### `--data_path`
**預設值**：`None`

**作用**：指定資料集的路徑

**使用時機**：
- `--dataset_name custom`：必須指定 JSON 檔案路徑
- `--dataset_name browsecomp-plus`：必須指定資料目錄

**範例**：
```bash
# 自訂問題
--dataset_name custom --data_path my_questions.json

# BrowseComp-Plus
--dataset_name browsecomp-plus --data_path data/browsecomp-plus/
```

---

#### `--search_url`
**預設值**：需要指定

**作用**：本地搜尋服務的 URL（僅用於 `--browser_backend local`）

**範例**：
```bash
--search_url http://localhost:8000  # 本地搜尋服務
--search_url NONE                    # 不使用（使用 serper 時設為 NONE）
```

---

#### `--max_concurrency_per_worker`
**預設值**：`8`

**作用**：每個 worker 同時處理的最大任務數

**範例**：
```bash
--max_concurrency_per_worker 4   # 降低並發（減少記憶體使用）
--max_concurrency_per_worker 16  # 提高並發（加快處理速度）
```

---

#### `--reasoning_effort`
**預設值**：`'high'`

**作用**：推理強度（影響模型思考深度）

**選項**：`'low'`, `'medium'`, `'high'`

---

#### `--tensor_parallel_size`
**預設值**：`1`

**作用**：張量並行大小（僅用於本地 vLLM 模型）

**範例**：
```bash
--tensor_parallel_size 2  # 使用 2 個 GPU 並行
--tensor_parallel_size 4  # 使用 4 個 GPU 並行
```

⚠️ 使用 `--vllm_server_url` 時此參數會被忽略

---

## 完整範例

### 範例 1：Azure OpenAI + GAIA Benchmark
```bash
python deploy_agent.py \
    --vllm_server_url AZURE_OPENAI \
    --model_name_or_path gpt-5.4 \
    --search_url NONE \
    --dataset_name gaia \
    --browser_backend serper \
    --output_dir results/gaia_azure
```

**說明**：
- 使用 Azure OpenAI GPT-5.4
- 執行 GAIA benchmark（103 個題目）
- 使用 Serper 進行網頁搜尋
- 結果儲存到 `results/gaia_azure/`

---

### 範例 2：Azure OpenAI + 自訂問題
```bash
# 1. 建立問題檔案 my_research.json
cat > my_research.json << 'EOF'
[
  {
    "qid": "vit_survey",
    "question": "Survey Vision Transformer papers (2020-2026). List top 10 papers with key innovations.",
    "answer": ""
  }
]
EOF

# 2. 執行研究
python deploy_agent.py \
    --vllm_server_url AZURE_OPENAI \
    --model_name_or_path gpt-5.4 \
    --search_url NONE \
    --dataset_name custom \
    --data_path my_research.json \
    --browser_backend serper \
    --output_dir results/my_research
```

---

### 範例 3：vLLM 服務器 + BrowseComp
```bash
# 需要先啟動 vLLM 服務器
# bash scripts/start_nemotron_servers.sh 2 8001 0,1,2,3

python deploy_agent.py \
    --vllm_server_url http://localhost:8001/v1 \
    --model_name_or_path OpenResearcher/OpenResearcher-30B-A3B \
    --search_url NONE \
    --dataset_name browsecomp \
    --browser_backend serper \
    --output_dir results/browsecomp
```

---

## 常見組合

| 使用情境 | 命令 |
|---------|------|
| **Azure + GAIA** | `--vllm_server_url AZURE_OPENAI --dataset_name gaia --browser_backend serper` |
| **Azure + 自訂問題** | `--vllm_server_url AZURE_OPENAI --dataset_name custom --data_path xxx.json --browser_backend serper` |
| **Azure + BrowseComp** | `--vllm_server_url AZURE_OPENAI --dataset_name browsecomp --browser_backend serper` |
| **Azure + xbench（中文）** | `--vllm_server_url AZURE_OPENAI --dataset_name xbench --browser_backend serper` |
| **vLLM + 本地搜尋** | `--vllm_server_url http://localhost:8001/v1 --dataset_name browsecomp-plus --browser_backend local --search_url http://localhost:8000` |

---

## 環境變數需求

使用 Azure OpenAI 時，需要在 `.env` 設定：

```bash
# Azure OpenAI（必須）
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT=gpt-5.4
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Serper API（使用 serper backend 時必須）
SERPER_API_KEY=your_serper_api_key
```

---

## 檢查結果

執行完成後：

```bash
# 查看結果檔案
ls results/gaia_azure/

# 讀取結果
python eval.py --input_dir results/gaia_azure
```
