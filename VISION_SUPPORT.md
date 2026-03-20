# 🖼️ Vision Support - Dual Model Architecture

## 架構說明

OpenResearcher 現在使用**雙模型策略**來優化研究流程：

### 🤖 模型分工

| 階段 | 模型 | 用途 | 特點 |
|------|------|------|------|
| **問題生成** | GPT-4o | 分析文檔/圖片，生成研究問題 | ✅ 支援影像理解<br>✅ 可分析流程圖、架構圖<br>✅ 多模態輸入 |
| **問題精煉** | GPT-4o | 根據反饋改進問題 | ✅ 對話式優化 |
| **研究執行** | GPT-5.4 | 執行深度網路研究 | ✅ 研究能力強<br>✅ 成本優化 |

---

## 📁 支援的檔案格式

### 文字檔案
- `.md` - Markdown
- `.txt` - 純文字

### 影像檔案（新增）
- `.png` - PNG 圖片
- `.jpg` / `.jpeg` - JPEG 圖片
- `.gif` - GIF 圖片
- `.bmp` - BMP 圖片
- `.webp` - WebP 圖片

---

## 🎯 影像分析能力

GPT-4o 可以理解並分析：

### ✅ 流程圖
- 識別步驟和決策點
- 理解邏輯流向
- 分析方法論

### ✅ 架構圖
- 系統架構
- 網路拓撲
- 組件關係

### ✅ UML 圖
- 類別圖
- 序列圖
- 活動圖

### ✅ 手繪圖
- 草圖
- 白板筆記
- 概念圖

---

## 🔧 環境變數配置

`.env` 檔案現在包含兩組配置：

```bash
# GPT-5.4 - 研究執行
AZURE_OPENAI_ENDPOINT=https://mb230-m7ey2j9q-eastus2.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=FKY7A5...
AZURE_OPENAI_DEPLOYMENT=gpt-5.4
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# GPT-4o - 問題生成（支援視覺）
AZURE_OPENAI_4O_ENDPOINT=https://eosl-r3-general.openai.azure.com/
AZURE_OPENAI_4O_API_KEY=8Hl6jM...
AZURE_OPENAI_4O_DEPLOYMENT=gpt-4o
AZURE_OPENAI_4O_API_VERSION=2024-12-01-preview
```

---

## 💡 使用範例

### 情境 1: 上傳流程圖生成研究問題

1. **準備材料**:
   - 研究背景描述（文字）
   - 方法流程圖（.png）

2. **操作步驟**:
   ```
   Tab 1: Document Analysis
   1. 輸入研究背景: "探討XX方法的有效性"
   2. 拖曳上傳: methodology_flowchart.png
   3. 設定問題數量: 5
   4. 點擊 "Generate Questions"
   ```

3. **GPT-4o 會**:
   - 閱讀你的文字描述
   - 分析流程圖的每個步驟
   - 理解方法論邏輯
   - 生成針對該方法的深度研究問題

### 情境 2: 純文字生成問題

```
Tab 1: Document Analysis
1. 輸入研究背景: "比較深度學習與傳統機器學習"
2. 不上傳檔案
3. 點擊 "Generate Questions"
```

GPT-4o 直接根據文字生成問題。

### 情境 3: 混合模式（文字 + 圖片）

```
Tab 1: Document Analysis
1. 輸入研究背景
2. 上傳:
   - background.md (文獻背景)
   - architecture.png (系統架構圖)
   - results.jpg (實驗結果截圖)
3. 生成問題
```

GPT-4o 會綜合分析所有材料。

---

## 🚀 完整工作流程

```
1. 問題生成階段 (GPT-4o)
   ├─ 分析文字描述
   ├─ 理解圖片內容（如果有）
   └─ 生成研究問題

2. 問題精煉階段 (GPT-4o)
   └─ 根據用戶反饋優化問題

3. 研究執行階段 (GPT-5.4)
   ├─ 網路搜尋
   ├─ 資料分析
   └─ 生成答案
```

---

## 📊 API 呼叫示例

### GPT-4o Vision API 格式

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "分析這個流程圖並生成研究問題"},
            {
                "type": "image_url",
                "image_url": {
                    "url": "data:image/png;base64,iVBORw0KG..."
                }
            }
        ]
    }
]
```

---

## ⚠️ 注意事項

1. **檔案大小限制**: 50MB
2. **圖片品質**: 建議使用清晰的高解析度圖片
3. **文字圖片**: GPT-4o 可以讀取圖片中的文字，但建議關鍵資訊用純文字提供
4. **成本**: 圖片分析會消耗更多 token，建議只上傳必要的圖片

---

## 🔍 除錯建議

如果圖片無法正確分析：

1. **檢查格式**: 確保是支援的圖片格式
2. **檢查清晰度**: 模糊或低解析度的圖片可能無法正確識別
3. **檢查 API Key**: 確認 `AZURE_OPENAI_4O_API_KEY` 正確
4. **查看日誌**: 檢查 Flask 終端機輸出的錯誤訊息

---

## 📝 API Response 範例

成功的回應會包含：

```json
{
  "success": true,
  "questions": [
    {"qid": "q1", "question": "...", "answer": ""},
    {"qid": "q2", "question": "...", "answer": ""}
  ],
  "documents": ["flowchart.png", "background.md"],
  "has_images": true,
  "model_used": "gpt-4o (vision-capable)"
}
```

---

## 🎉 優勢

✅ **智能分工**: 問題生成用 GPT-4o（視覺能力），研究用 GPT-5.4（研究能力）  
✅ **成本優化**: 只在需要視覺理解時使用 GPT-4o  
✅ **更強理解**: 可以從流程圖、架構圖直接生成研究問題  
✅ **無縫整合**: 用戶體驗不變，自動選擇最佳模型  

---

**版本**: 1.0  
**更新日期**: 2026-03-19  
**作者**: OpenResearcher Team
