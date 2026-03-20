# 問題生成器使用指南

OpenResearcher 需要 JSON 格式的問題檔案。為了方便使用，我們提供了兩種問題生成器：

---

## 🚀 方式 1：PowerShell 互動式生成器（推薦 Windows 用戶）

### 使用方法

```powershell
.\question_generator.ps1
```

### 功能特色

✅ **三種模式**：
1. **快速模式** - 單一問題，快速生成
2. **批次模式** - 多個問題，一次處理
3. **範本模式** - 預設研究範本

✅ **內建範本**：
- 文獻調查（Literature Survey）
- 論文撰寫（Paper Writing）
- 技術比較（Technology Comparison）
- 市場研究（Market Research）
- 實驗設計（Experiment Design）

✅ **自動執行**：
- 生成問題後可立即執行研究
- 自動呼叫 `deploy_agent.py`

### 範例使用

```powershell
# 啟動生成器
.\question_generator.ps1

# 選擇範本模式 (3)
# 選擇文獻調查 (1)
# 輸入主題：Vision Transformer
# 自動生成 3 個研究問題
# 選擇立即執行 (y)
# 等待 30-60 分鐘
# 獲得完整研究報告
```

---

## 🌐 方式 2：Web UI 圖形介面（推薦所有用戶）

### 安裝依賴

```bash
pip install streamlit
```

### 啟動 UI

```bash
streamlit run question_generator_ui.py
```

瀏覽器會自動開啟 `http://localhost:8501`

### 功能特色

✅ **圖形化介面**：
- 視覺化問題編輯
- 即時預覽
- 拖拉操作

✅ **範本系統**：
- 5 種研究範本
- 一鍵生成
- 可自訂修改

✅ **整合執行**：
- UI 內直接執行研究
- 顯示執行進度
- 查看結果

### 使用流程

```
1. 選擇模式（快速/批次/範本）
   ↓
2. 輸入問題或選擇範本
   ↓
3. 預覽問題
   ↓
4. 儲存 JSON 檔案
   ↓
5. 點擊「立即執行」
   ↓
6. 在 UI 中查看結果
```

---

## 📝 手動方式（完全控制）

如果您想完全控制問題格式：

### 建立 JSON 檔案

```json
[
  {
    "qid": "unique_id",
    "question": "您的研究問題",
    "answer": ""
  }
]
```

### 使用文字編輯器

```powershell
# 使用 VS Code
code my_questions.json

# 或使用記事本
notepad my_questions.json
```

### 執行研究

```bash
python deploy_agent.py \
    --vllm_server_url AZURE_OPENAI \
    --dataset_name custom \
    --data_path my_questions.json \
    --browser_backend serper \
    --output_dir results/my_research
```

---

## 🎯 問題撰寫最佳實踐

### ✅ 好的問題範例

```json
{
  "qid": "vit_survey",
  "question": "Survey Vision Transformer papers (2020-2026). Requirements: 1) List top 15 papers by citations, 2) For each paper provide: title, authors, venue, year, key innovation, benchmark results, 3) Include paper links (arXiv or venue), 4) Create comparison table of performance on ImageNet, 5) Identify current limitations and future directions. Search: arXiv, Papers with Code, Google Scholar.",
  "answer": ""
}
```

**為什麼好？**
- ✅ 具體的時間範圍（2020-2026）
- ✅ 明確的數量要求（15 papers）
- ✅ 詳細的輸出格式
- ✅ 要求引用和連結
- ✅ 指定搜尋來源

### ❌ 不好的問題範例

```json
{
  "qid": "bad_example",
  "question": "Tell me about Vision Transformers",
  "answer": ""
}
```

**為什麼不好？**
- ❌ 太籠統
- ❌ 沒有時間範圍
- ❌ 沒有具體要求
- ❌ 沒有輸出格式
- ❌ 可能得到過時資訊

---

## 📚 預設範本說明

### 1. 文獻調查範本

生成 3 個問題：
- **Overview** - 綜合性調查
- **SOTA** - 最新技術比較
- **Trends** - 未來趨勢分析

**適用於**：
- 了解新領域
- 撰寫論文 Related Work
- 技術選型

### 2. 論文撰寫範本

生成 3 個問題：
- **Introduction** - 引言章節
- **Related Work** - 相關工作
- **Experiments** - 實驗設計

**適用於**：
- 撰寫學術論文
- 準備研究提案
- 文獻綜述

### 3. 技術比較範本

生成 2 個問題：
- **Comparison** - 技術對比表
- **Recommendations** - 使用建議

**適用於**：
- 技術選型
- 工具評估
- 方案比較

### 4. 市場研究範本

生成 2 個問題：
- **Market Overview** - 市場概況
- **Competitive Analysis** - 競品分析

**適用於**：
- 產品規劃
- 競品調研
- 市場分析

### 5. 實驗設計範本

生成 3 個問題：
- **Datasets** - 資料集調查
- **Baselines** - 基準方法
- **Metrics** - 評估指標

**適用於**：
- 設計實驗
- 準備 Benchmark
- 論文實驗章節

---

## 🔄 完整工作流程範例

### 情境：撰寫論文 Related Work

```powershell
# 1. 啟動生成器
.\question_generator.ps1

# 2. 選擇「範本模式」(3)

# 3. 選擇「論文撰寫」(2)

# 4. 輸入主題
研究主題：Low-Rank Adaptation for Vision-Language Models

# 5. 自動生成 3 個問題
✅ paper_introduction
✅ paper_related_work  
✅ paper_experiments

# 6. 預覽並儲存
儲存到 paper_questions.json? (y)

# 7. 立即執行
是否立即執行研究? (y)
輸出目錄: results/paper

# 8. 等待完成（約 45-90 分鐘）

# 9. 查看結果
code results/paper/node_0_shard_0.jsonl
```

### 得到的結果

```
results/paper/
└── node_0_shard_0.jsonl

內容：
- Introduction 完整段落（500+ 字）
- Related Work 完整段落（1000+ 字，15+ 引用）
- Experiment 設計（資料集、基準、指標）
```

---

## 💡 進階技巧

### 技巧 1：分階段研究

```powershell
# 第一階段：概覽
.\question_generator.ps1
# 生成：overview 問題

# 執行後根據結果，生成第二階段問題
.\question_generator.ps1  
# 生成：深入特定主題
```

### 技巧 2：迭代優化

```powershell
# 初次生成
.\question_generator.ps1

# 查看結果
code results/*/node_0_shard_0.jsonl

# 根據結果修改問題
code my_questions.json

# 重新執行（會跳過已完成的問題）
python deploy_agent.py ...
```

### 技巧 3：批次處理

```powershell
# 生成多個研究主題的問題
foreach ($topic in @("ViT", "BERT", "Diffusion")) {
    # 使用範本為每個主題生成問題
    # 執行研究
}
```

---

## 🆚 三種方式對比

| 特性 | PowerShell CLI | Web UI | 手動 JSON |
|------|---------------|---------|-----------|
| **易用性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **靈活性** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **視覺化** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **自動化** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **學習曲線** | 低 | 最低 | 中 |

### 建議選擇

- **初學者** → Web UI
- **Windows 用戶** → PowerShell CLI
- **進階用戶** → 手動 JSON
- **批次處理** → PowerShell CLI
- **視覺化編輯** → Web UI

---

## 🎓 總結

✅ **問題生成器讓 OpenResearcher 更易用**  
✅ **三種方式滿足不同需求**  
✅ **範本系統快速上手**  
✅ **自動執行節省時間**  

**推薦流程**：
1. 使用範本快速生成問題
2. 預覽並調整
3. 一鍵執行研究
4. 查看結果並迭代

**現在就試試看！** 🚀
