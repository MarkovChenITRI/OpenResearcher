# OpenResearcher Web Application - 架構圖解

## 系統架構總覽

```
┌─────────────────────────────────────────────────────────────────────┐
│                          使用者瀏覽器                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                     index.html (SPA)                          │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │  │
│  │  │  Tab 1  │  │  Tab 2  │  │  Tab 3  │  │  Tab 4  │        │  │
│  │  │ 文件分析 │  │ 問題管理 │  │ 執行研究 │  │ 結果追蹤 │        │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │  │
│  │                           │                                  │  │
│  │                    JavaScript                                │  │
│  │                 (fetch, localStorage)                        │  │
│  └───────────────────────────┼───────────────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────────────┘
                                 │ HTTP/JSON
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Flask 後端 (app.py)                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                        API Routes                             │  │
│  │  /api/analyze_documents    /api/refine_questions             │  │
│  │  /api/start_research       /api/task_status/<id>             │  │
│  │  /api/stop_research/<id>   /api/task_results/<id>            │  │
│  │  /api/task_logs/<id>       /api/export_results/<id>          │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                 │                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    ResearchTask Class                         │  │
│  │  - start()         啟動研究                                    │  │
│  │  - stop()          停止研究                                    │  │
│  │  - _run_research() 執行邏輯                                    │  │
│  │  - _update_progress() 更新進度                                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                 │                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      Utilities                                │  │
│  │  - extract_file_content()        文件解析                     │  │
│  │  - generate_questions_from_documents()  LLM 生成              │  │
│  │  - refine_questions_with_llm()   LLM 優化                     │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
         │                    │                         │
         │ subprocess         │ httpx                   │ file I/O
         ▼                    ▼                         ▼
┌──────────────────┐  ┌────────────────────┐  ┌───────────────┐
│ deploy_agent.py  │  │  Azure OpenAI API  │  │ uploads/      │
│  OpenResearcher  │  │    (GPT-5.4)       │  │ results/      │
│  原始 CLI 工具    │  │  + Serper API      │  │ (JSONL, logs) │
└──────────────────┘  └────────────────────┘  └───────────────┘
```

## 資料流程圖

### 流程 1：文件分析 → 問題生成

```
使用者上傳文件 (Markdown, PDF, etc.)
         │
         ▼
前端：FormData + fetch() → POST /api/analyze_documents
         │
         ▼
後端：接收文件並儲存到 uploads/
         │
         ▼
file_utils.extract_file_content(filepath)
         │
         ├─ .md, .txt   → 直接讀取文字
         ├─ .pdf        → PyPDF2 解析
         ├─ .docx       → python-docx 解析
         ├─ .pptx       → python-pptx 解析
         └─ .png, .jpg  → Base64 編碼（TODO: OCR）
         │
         ▼
構建 LLM Prompt：
"Based on the following documents and context, 
 generate {n} research questions..."
         │
         ▼
Azure OpenAI API 呼叫 (async)
         │
         ▼
解析 LLM Response (JSON extraction)
         │
         ▼
返回 questions[] 給前端
         │
         ▼
前端：顯示生成的問題卡片
         │
         ▼
使用者點擊「儲存」→ localStorage
```

### 流程 2：對話式問題優化

```
使用者輸入反饋：
"把問題 1 改得更聚焦在實作細節"
         │
         ▼
前端：fetch() → POST /api/refine_questions
      Body: { questions: [...], feedback: "..." }
         │
         ▼
後端：構建 Prompt
"You are helping refine research questions.
 Current questions: [...]
 User feedback: ..."
         │
         ▼
Azure OpenAI API 呼叫
         │
         ▼
解析優化後的 questions[]
         │
         ▼
返回給前端
         │
         ▼
前端：
1. 更新 currentQuestions
2. 重新渲染問題清單
3. 儲存到 localStorage
4. 在對話框顯示「✅ 已更新」
```

### 流程 3：執行研究任務

```
使用者點擊「開始研究」
         │
         ▼
前端：選擇模式（限時/無限時）
      fetch() → POST /api/start_research
      Body: { questions: [...], time_limit: 3600 }
         │
         ▼
後端：創建 ResearchTask 物件
         │
         ├─ task_id = "task_" + timestamp
         ├─ output_dir = results/task_xxx/
         ├─ questions.json 寫入磁碟
         └─ 啟動背景執行緒
         │
         ▼
threading.Thread(target=_run_research)
         │
         ▼
subprocess.Popen([
    "python", "deploy_agent.py",
    "--vllm_server_url", "AZURE_OPENAI",
    "--dataset_name", "custom",
    "--data_path", "questions.json",
    ...
])
         │
         ▼
While process 執行中：
    ├─ 檢查時間限制
    ├─ 解析 output JSONL → 更新進度
    ├─ 每 5 秒循環
    └─ 寫入 research.log
         │
         ▼
前端輪詢：每 3 秒呼叫 /api/task_status/<id>
         │
         ├─ 更新進度條 (0-100%)
         ├─ 顯示當前問題
         ├─ 更新完成數/總數
         └─ fetch /api/task_logs/<id> 顯示日誌
         │
         ▼
任務完成：
    status = "completed" | "stopped" | "error"
    前端停止輪詢
```

## 類別關係圖

```
┌──────────────────────────────────────────────────────────┐
│                     Flask App                            │
│  app = Flask(__name__)                                   │
│  app.config['UPLOAD_FOLDER'] = 'uploads'                │
│  app.config['RESULTS_FOLDER'] = 'results'               │
└──────────────────────────────────────────────────────────┘
                         │
                         │ has many
                         ▼
┌──────────────────────────────────────────────────────────┐
│              research_tasks: Dict[str, ResearchTask]     │
│  全域字典，儲存所有任務物件                                 │
└──────────────────────────────────────────────────────────┘
                         │
                         │ contains
                         ▼
┌──────────────────────────────────────────────────────────┐
│                   ResearchTask                           │
├──────────────────────────────────────────────────────────┤
│ Attributes:                                              │
│  - task_id: str                                          │
│  - questions: List[dict]                                 │
│  - output_dir: str                                       │
│  - time_limit: Optional[int]                             │
│  - status: str  (pending/running/completed/stopped)      │
│  - progress: int (0-100)                                 │
│  - process: subprocess.Popen                             │
│  - thread: threading.Thread                              │
├──────────────────────────────────────────────────────────┤
│ Methods:                                                 │
│  + start()           啟動研究                             │
│  + stop()            停止研究                             │
│  + get_status()      返回狀態 dict                        │
│  - _run_research()   私有：執行邏輯                       │
│  - _update_progress() 私有：解析 JSONL 更新進度            │
└──────────────────────────────────────────────────────────┘
                         │
                         │ uses
                         ▼
┌──────────────────────────────────────────────────────────┐
│            AzureOpenAIAsyncGenerator                     │
│  (from utils/azure_openai_generator.py)                 │
├──────────────────────────────────────────────────────────┤
│  + chat_completion(messages, tools, ...)                │
│  + generate(prompt_tokens, ...)                         │
│  + aclose()  清理資源                                     │
└──────────────────────────────────────────────────────────┘
```

## API 端點對應圖

```
前端 Tab                      API 端點                      後端處理
─────────────────────────────────────────────────────────────────────
Tab 1: 文件分析
  上傳文件按鈕          →   POST /api/analyze_documents    →  extract_file_content()
                                                           →  generate_questions_from_documents()
                                                           ←  返回 questions[]

Tab 2: 問題管理
  對話輸入框           →   POST /api/refine_questions      →  refine_questions_with_llm()
                                                           ←  返回 refined questions[]

Tab 3: 執行研究
  開始研究按鈕          →   POST /api/start_research       →  ResearchTask.start()
                                                              subprocess → deploy_agent.py
  
  (每 3 秒輪詢)         →   GET /api/task_status/<id>      →  task.get_status()
                                                           ←  返回 status dict
  
  (每 3 秒輪詢)         →   GET /api/task_logs/<id>        →  讀取 research.log
                                                           ←  返回 logs string
  
  停止研究按鈕          →   POST /api/stop_research/<id>   →  task.stop()
                                                              process.terminate()

Tab 4: 結果追蹤
  刷新按鈕             →   GET /api/list_tasks             →  返回所有 tasks 狀態
  
  查看結果按鈕          →   GET /api/task_results/<id>     →  返回 results[]
  
  查看日誌按鈕          →   GET /api/task_logs/<id>        →  返回 logs
  
  匯出按鈕             →   GET /api/export_results/<id>   →  send_file(json)
```

## 檔案儲存結構

```
OpenResearcher/
├── webapp/
│   ├── app.py                     主應用
│   ├── file_utils.py              文件處理
│   ├── templates/
│   │   └── index.html            前端 SPA
│   ├── uploads/                   上傳的文件
│   │   ├── research.md
│   │   ├── presentation.pptx
│   │   └── diagram.png
│   └── results/                   研究結果
│       ├── task_1234567890/
│       │   ├── questions.json     輸入問題
│       │   ├── node_0_shard_0.jsonl  研究結果
│       │   ├── research.log       執行日誌
│       │   └── task_1234567890_export.json  匯出檔案
│       └── task_9876543210/
│           └── ...
├── utils/
│   └── azure_openai_generator.py  Azure OpenAI 整合
├── deploy_agent.py                原始 CLI 工具
└── .env                           環境變數（共用）
```

## 狀態機圖（ResearchTask）

```
        start()
┌─────────────────►  PENDING  ──────────────────┐
│                                                │
│                                                │ _run_research()
│                                                │ (background thread)
│                                                ▼
│                                           RUNNING
│                                                │
│                                                │
│                            ┌───────────────────┼────────────────────┐
│                            │                   │                    │
│                            │ process complete  │ stop()             │ error
│                            │ returncode == 0   │                    │
│                            ▼                   ▼                    ▼
│                       COMPLETED            STOPPED               ERROR
│                            │                   │                    │
└────────────────────────────┴───────────────────┴────────────────────┘
                             (終止狀態)
```

## 前端狀態管理

```
Browser localStorage
├── researchQuestions: JSON string
│   儲存當前問題清單
│   格式：[{qid, question, answer}, ...]
│
└── (未來擴展)
    ├── userPreferences
    ├── recentTasks
    └── savedFilters

Browser Memory (JavaScript)
├── uploadedFiles: File[]
│   暫存上傳的文件物件
│
├── currentQuestions: Object[]
│   當前編輯中的問題清單
│
├── currentTaskId: string | null
│   正在執行的任務 ID
│
├── statusInterval: number | null
│   輪詢計時器 ID
│
└── chatHistory: Object[]
    對話歷史記錄
```

## 錯誤處理流程

```
使用者操作
    │
    ▼
前端驗證
    │
    ├─ 驗證通過 → 發送 API 請求
    │                  │
    │                  ▼
    │              後端接收
    │                  │
    │                  ├─ try-catch 包裹
    │                  │      │
    │                  │      ├─ 成功 → 返回 {"success": true, ...}
    │                  │      │
    │                  │      └─ 失敗 → 返回 {"error": "message"}, status_code
    │                  │
    │                  ▼
    │              前端接收 Response
    │                  │
    │                  ├─ response.ok == true
    │                  │      └─ 顯示成功訊息、更新 UI
    │                  │
    │                  └─ response.ok == false
    │                         └─ alert(data.error) 或顯示錯誤訊息
    │
    └─ 驗證失敗 → 立即顯示錯誤訊息（不發送請求）
```

## 並行處理模型

```
Flask 主執行緒
    │
    ├─ 處理 HTTP 請求 (同步)
    │   ├─ GET /api/task_status/<id>  ← 快速回應（讀取記憶體）
    │   ├─ POST /api/start_research   ← 快速回應（啟動後台執行緒）
    │   └─ GET /api/task_results/<id> ← 快速回應（讀取檔案）
    │
    └─ 產生背景執行緒
        │
        └─ ResearchTask._run_research()
            │
            ├─ subprocess.Popen(deploy_agent.py)  ← 獨立程序
            │   │
            │   └─ OpenResearcher 執行
            │       ├─ Azure OpenAI API 呼叫
            │       ├─ Serper API 呼叫
            │       └─ 寫入 JSONL 結果
            │
            └─ while loop 監控進度
                ├─ 每 5 秒檢查 JSONL 檔案
                ├─ 更新 task.progress
                └─ 檢查時間限制

Note: 目前只支援單一任務並行
      未來可擴展為多任務佇列（Celery）
```

## 安全層級圖

```
Layer 1: Network (未實作 HTTPS)
    ↓
Layer 2: Flask App
    ├─ secure_filename()  檔案名稱清理
    ├─ 檔案大小限制 (50MB)
    └─ (TODO: CSRF token, rate limiting)
    ↓
Layer 3: File System
    ├─ uploads/  使用者上傳
    ├─ results/  研究結果
    └─ .env      環境變數（不版控）
    ↓
Layer 4: External APIs
    ├─ Azure OpenAI  (API key 認證)
    └─ Serper API    (API key 認證)
```

---

**圖解說明完成** ✅

這些圖解涵蓋了系統的各個層面：
- 整體架構
- 資料流程
- 類別關係
- API 對應
- 檔案結構
- 狀態機
- 錯誤處理
- 並行模型
- 安全層級

有助於快速理解整個 Web 應用的運作方式！
