# OpenResearcher Web Application

完整的 Flask Web 介面，讓 OpenResearcher 更容易使用

## 🎯 功能特色

### 1. 📁 文件分析與問題生成
- 上傳 Markdown、簡報、文件、圖片
- AI 自動分析文件內容
- 根據研究目標生成高品質研究問題
- 支援拖放上傳

### 2. 📝 問題管理與優化
- 視覺化問題清單
- 手動編輯、新增、刪除問題
- **對話式 AI 優化**：使用自然語言反饋改進問題
- 即時儲存與載入

### 3. 🚀 研究執行引擎
- 兩種執行模式：
  - **無限時模式**：由您手動停止
  - **限時模式**：設定時間自動停止
- 即時進度追蹤
- 動態日誌更新
- 當前問題顯示

### 4. 📊 結果追蹤與瀏覽
- 所有任務狀態總覽
- 即時進度監控
- 結果瀏覽與分析
- JSON 匯出功能

## 🛠️ 安裝

### 1. 安裝依賴

**重要：必須在 webapp 目錄執行**

```bash
cd webapp
pip install -r requirements.txt
```

### 2. 確認環境變數

確保**專案根目錄**（OpenResearcher/）的 `.env` 已設定：

```bash
# 從 webapp/ 目錄檢查
Get-Content ..\.env

# 應該看到以下變數
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT=gpt-5.4
AZURE_OPENAI_API_VERSION=2024-12-01-preview
SERPER_API_KEY=your_serper_key
```

### 3. 啟動應用

```bash
# 確保在 webapp 目錄
cd webapp

# 執行啟動腳本（推薦）
.\start.ps1

# 或手動啟動
python app.py
```

應用會在 http://localhost:5000 啟動

**注意：** app.py 會自動找到上層目錄的 `deploy_agent.py`，無需手動設定路徑。

## 📖 使用流程

### 方案一：從文件開始

1. **上傳文件** (Tab 1)
   - 拖放或點擊上傳 Markdown、簡報、圖片
   - 填寫研究背景與目標
   - 選擇生成問題數量（3/5/10）
   - 點擊「分析並生成問題」

2. **優化問題** (Tab 2)
   - 查看 AI 生成的問題
   - 使用對話框反饋：
     - "把問題 1 改得更具體"
     - "增加關於實驗設計的問題"
     - "問題太廣泛，請聚焦在最近 3 年"
   - AI 會自動更新問題列表

3. **執行研究** (Tab 3)
   - 選擇執行模式（限時或無限時）
   - 點擊「開始研究」
   - 即時監控進度與日誌
   - 可隨時停止

4. **查看結果** (Tab 4)
   - 瀏覽所有任務
   - 查看詳細結果
   - 匯出 JSON 格式

### 方案二：直接手動建立

1. **手動新增問題** (Tab 2)
   - 直接輸入問題文字
   - 點擊「新增」
   - 重複直到建立完整問題清單

2. **執行 & 追蹤** (Tab 3 & 4)
   - 同上

## 🎨 介面預覽

### 文件分析
```
┌─────────────────────────────────┐
│ 📤 拖放文件或點擊上傳            │
│                                 │
│ 📄 research.md                  │
│ 📄 presentation.pptx            │
│ 📷 diagram.png                  │
│                                 │
│ 研究背景：Vision Transformer... │
│ 生成數量：5 個問題              │
│                                 │
│ [🔍 分析並生成問題]            │
└─────────────────────────────────┘
```

### 對話式優化
```
┌─────────────────────────────────┐
│ User: 把問題 1 改得更聚焦在     │
│       實作細節                  │
│                                 │
│ AI: ✅ 已更新問題！             │
│     新問題：How to implement... │
└─────────────────────────────────┘
```

### 即時監控
```
┌─────────────────────────────────┐
│ Task ID: task_1234567890        │
│ 狀態: 執行中 🟡                 │
│                                 │
│ ████████████░░░░░░░░  60%      │
│                                 │
│ 當前問題: Survey Vision Tra...  │
│ 已完成: 3/5                     │
│ 執行時間: 1245 秒               │
│                                 │
│ 即時日誌:                       │
│ [Worker 0] Round 25             │
│ [NATIVE_TOOLS] browser.search... │
└─────────────────────────────────┘
```

## 🔧 技術細節

### 架構

```
webapp/
├── app.py                 # Flask 主應用
├── file_utils.py          # 文件處理工具
├── templates/
│   └── index.html        # 單頁應用介面
├── requirements.txt      # Python 依賴
└── README.md            # 本文件

注意：app.py 會呼叫上層目錄的 deploy_agent.py
路徑處理：使用 Path(__file__).parent.parent 定位
```

### API 端點

| 端點 | 方法 | 功能 |
|------|------|------|
| `/api/analyze_documents` | POST | 分析文件生成問題 |
| `/api/refine_questions` | POST | 對話式優化問題 |
| `/api/start_research` | POST | 啟動研究任務 |
| `/api/task_status/<id>` | GET | 獲取任務狀態 |
| `/api/stop_research/<id>` | POST | 停止任務 |
| `/api/task_results/<id>` | GET | 獲取結果 |
| `/api/task_logs/<id>` | GET | 獲取日誌 |
| `/api/export_results/<id>` | GET | 匯出 JSON |
| `/api/list_tasks` | GET | 列出所有任務 |

### ResearchTask 類別

管理單一研究任務的完整生命週期：

```python
class ResearchTask:
    - task_id: 唯一識別碼
    - questions: 研究問題清單
    - status: pending/running/completed/stopped/error
    - progress: 0-100%
    - results: 研究結果
    - process: subprocess 物件
    - start(): 啟動研究
    - stop(): 停止研究
    - _update_progress(): 更新進度
    - get_status(): 取得狀態字典
```

### 即時更新機制

- 前端每 3 秒輪詢 `/api/task_status/<id>`
- 動態更新進度條、問題數、日誌
- 任務完成後停止輪詢

### 文件處理

支援的文件類型：
- ✅ Markdown (.md)
- ✅ Text (.txt)
- 🚧 PDF (.pdf) - 待實作
- 🚧 Word (.docx) - 待實作
- 🚧 PowerPoint (.pptx) - 待實作
- ✅ 圖片 (.png, .jpg, .jpeg) - Base64 編碼

## 💡 使用場景

### 場景 1：文獻綜述
```
1. 上傳相關論文的 PDF/摘要
2. 設定背景："Survey Vision Transformer 2020-2026"
3. 生成 5 個問題
4. AI 優化："增加關於 benchmark 比較的問題"
5. 執行研究（限時 2 小時）
6. 查看綜述結果，匯出給 AutoResearch
```

### 場景 2：技術評估
```
1. 上傳技術文件、架構圖
2. 手動新增問題：
   - "Compare React vs Vue performance in 2026"
   - "What are the latest React best practices"
3. 執行無限時研究
4. 即時監控，發現足夠資訊後手動停止
5. 匯出結果作為技術決策依據
```

### 場景 3：實驗設計
```
1. 上傳研究計畫書
2. 生成實驗設計問題
3. 對話優化："聚焦在統計分析方法"
4. 執行研究
5. 結果交給 AutoResearch 自動產生實驗程式碼
```

## 🚀 與 AutoResearch 整合

產出的 JSON 格式直接相容於 AutoResearch：

```json
{
  "task_id": "task_1234567890",
  "questions": [...],
  "results": [
    {
      "question": "...",
      "messages": [...],
      "final_answer": "..."
    }
  ]
}
```

直接匯出後可用於：
- 自動程式碼生成
- 實驗自動化
- 技術原型開發

## ⚠️ 注意事項

### API 使用量
- 每個問題約 15-30 分鐘
- 會消耗 Azure OpenAI tokens
- 建議設定時間限制避免過度使用

### 瀏覽器支援
- Chrome 90+
- Edge 90+
- Firefox 88+
- Safari 14+

### 並行限制
- 同時只能執行一個研究任務
- 使用 subprocess 管理 OpenResearcher
- 前端輪詢避免服務器壓力

## 🔍 故障排除

### 問題：無法啟動應用
```bash
# 檢查依賴
pip install -r requirements.txt

# 檢查環境變數
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('AZURE_OPENAI_ENDPOINT'))"
```

### 問題：研究無法開始
```bash
# 確認 Serper API
echo $SERPER_API_KEY

# 測試 Azure 連線
cd ..
python test_azure_integration.py
```

### 問題：日誌不更新
- 檢查 `results/<task_id>/research.log` 是否存在
- 確認 deploy_agent.py 有寫入權限
- 查看瀏覽器 Console 是否有錯誤

## 📚 進階功能（TODO）

- [ ] PDF/DOCX/PPTX 完整解析
- [ ] 多語言支援（英文/中文切換）
- [ ] 使用者帳號系統
- [ ] 任務排程與批次執行
- [ ] 結果視覺化圖表
- [ ] AI 自動摘要研究結果
- [ ] WebSocket 即時推送
- [ ] 行動版 RWD 優化

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

---

**Made with ❤️ for OpenResearcher Community**
