# 資料夾選擇模式使用說明

## 新功能概述

OpenResearcher 現在支援**資料夾批次處理**模式，可以：

1. 選擇包含所有研究文件的資料夾
2. 自動掃描並處理所有支援的檔案
3. 即時顯示處理進度（灰色文字顯示當前讀取的檔案）
4. AI 先彙總所有文件，再生成研究問題

---

## 使用方式

### 1. 準備你的研究資料夾

```
my_research_project/
├── background.md          # 研究背景
├── methodology.md         # 方法論
├── literature/
│   ├── paper1.md
│   └── paper2.md
├── diagrams/
│   ├── flowchart.png      # 流程圖
│   └── architecture.png   # 架構圖
└── data/
    └── results.csv
```

### 2. 在 Web UI 操作

1. **打開 Tab 1: Document Analysis**
2. **輸入研究背景**: 描述你的研究目標
3. **選擇資料夾**: 點擊「選擇資料夾」按鈕
4. **選擇你的研究專案資料夾**: 例如 `my_research_project/`
5. **查看掃描結果**: 系統會顯示找到多少文字檔、多少圖片
6. **點擊「Generate Questions」**: 開始處理

### 3. 即時進度顯示

處理過程中，你會看到灰色文字顯示：

```
正在處理: background.md (1/10)
正在處理: methodology.md (2/10)
正在處理: literature/paper1.md (3/10)
...
正在分析: 所有文件已讀取，生成摘要中...
正在生成: 基於完整理解生成研究問題...
完成！
```

---

## 技術細節

### 支援的檔案格式

**文字檔案**:
- `.md` - Markdown
- `.txt` - 純文字
- `.py` - Python 代碼
- `.json` - JSON 數據
- `.csv` - CSV 數據
- `.html` - HTML
- `.xml` - XML

**影像檔案**:
- `.png`, `.jpg`, `.jpeg` - 圖片
- `.gif`, `.bmp`, `.webp` - 其他圖片格式

### 處理流程

```
1. 掃描資料夾
   └─> 遞迴找出所有支援的檔案

2. 批次處理文件
   ├─> 逐一讀取每個檔案
   ├─> 文字檔案 → 提取內容
   ├─> 圖片檔案 → 轉 base64
   └─> 即時更新進度

3. 生成文件摘要 (GPT-4o)
   └─> 理解所有文件的整體脈絡

4. 生成研究問題 (GPT-4o)
   └─> 基於完整理解生成問題

5. 研究執行 (GPT-5.4)
   └─> 使用生成的問題進行研究
```

---

## API 端點

### `/api/scan_folder` (POST)
掃描資料夾，返回檔案清單

**Request**:
```json
{
  "folder_path": "/path/to/your/research"
}
```

**Response**:
```json
{
  "success": true,
  "total_files": 15,
  "text_files": 12,
  "image_files": 3,
  "file_list": [
    "background.md",
    "methodology.md",
    "diagrams/flowchart.png",
    ...
  ]
}
```

### `/api/analyze_documents` (POST)
處理資料夾並生成問題

**Request**:
```json
{
  "folder_path": "/path/to/your/research",
  "context": "研究背景描述",
  "num_questions": 5
}
```

**Response**:
```json
{
  "success": true,
  "questions": [...],
  "documents_processed": 15,
  "document_list": [...],
  "summary": "文件摘要...",
  "has_images": true,
  "model_used": "gpt-4o (vision-capable)",
  "progress_id": "progress_1234567890"
}
```

### `/api/progress/<progress_id>` (GET)
查詢處理進度

**Response**:
```json
{
  "status": "processing",
  "current_file": "literature/paper1.md",
  "processed": 3,
  "total": 15,
  "percentage": 20
}
```

---

## 前端實作範例

```javascript
// 選擇資料夾
async function selectFolder() {
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = true;  // 選擇資料夾
    
    input.onchange = async (e) => {
        const files = e.target.files;
        const folderPath = files[0].webkitRelativePath.split('/')[0];
        
        // 掃描資料夾
        const scan = await fetch('/api/scan_folder', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({folder_path: folderPath})
        });
        
        const result = await scan.json();
        console.log(`Found ${result.total_files} files`);
    };
    
    input.click();
}

// 開始處理並顯示進度
async function processDocuments(folderPath, context, numQuestions) {
    const response = await fetch('/api/analyze_documents', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            folder_path: folderPath,
            context: context,
            num_questions: numQuestions
        })
    });
    
    const result = await response.json();
    return result.questions;
}

// 輪詢進度
async function trackProgress(progressId) {
    const interval = setInterval(async () => {
        const response = await fetch(`/api/progress/${progressId}`);
        const progress = await response.json();
        
        // 更新 UI
        document.getElementById('progress-text').textContent = 
            `正在處理: ${progress.current_file} (${progress.processed}/${progress.total})`;
        document.getElementById('progress-bar').style.width = `${progress.percentage}%`;
        
        if (progress.status === 'done') {
            clearInterval(interval);
        }
    }, 500);
}
```

---

## 優勢

✅ **完整理解**: AI 會先看過所有文件再生成問題  
✅ **可追蹤**: 即時顯示正在處理哪個檔案  
✅ **批次處理**: 不用手動上傳每個檔案  
✅ **遞迴掃描**: 自動處理子資料夾  
✅ **智能摘要**: 先彙總再提問，避免遺漏重要資訊  

---

## 注意事項

1. **檔案數量**: 建議單次處理不超過 100 個檔案
2. **檔案大小**: 每個文字檔建議小於 5MB
3. **圖片數量**: 由於 token 限制，最多處理前 3 張圖片
4. **處理時間**: 視檔案數量而定，通常 10-30 秒

---

**版本**: 2.0  
**更新日期**: 2026-03-19  
**新功能**: 資料夾批次處理 + 即時進度追蹤
