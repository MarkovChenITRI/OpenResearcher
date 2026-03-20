# 📚 自動文獻綜述生成器

## 功能說明

從您的 Markdown 大綱自動生成完整的文獻綜述報告，包含：
- ✅ 最新論文引用（2020-2026）
- ✅ 完整 citations（標題、作者、年份、連結）
- ✅ Benchmark 結果比較
- ✅ 所有資訊都有來源驗證
- ✅ 學術寫作風格

---

## 快速開始

### 步驟 1：建立您的大綱

建立一個 Markdown 檔案，定義您想要的綜述結構：

```markdown
# 我的研究主題

## Introduction
## 相關技術背景
## 方法比較
## 應用案例
## 未來展望
## 結論
```

**範例**：`example_review_template.md`

---

### 步驟 2：執行生成器

```powershell
# 基本用法
.\generate_review.ps1 -TemplateFile "my_template.md" -Topic "Vision Transformer"

# 完整參數
.\generate_review.ps1 `
    -TemplateFile "my_template.md" `
    -Topic "Vision Transformer" `
    -OutputDir "results/vit_review"
```

---

### 步驟 3：等待完成

腳本會自動：
1. 📖 解析您的 Markdown 大綱
2. 🎯 為每個章節生成研究問題
3. 🚀 使用 OpenResearcher + Azure GPT-5.4 進行深度研究
4. 📝 合併結果生成完整報告

**預計時間**：1-3 小時（取決於章節數量）

---

### 步驟 4：檢視結果

```powershell
# 輸出檔案位置
results/vit_review/final_review_YYYYMMDD_HHMMSS.md

# 查看報告
code results/vit_review/final_review_*.md
```

---

## 完整範例

### 範例 1：Vision Transformer 綜述

```powershell
# 1. 建立大綱
@"
# Vision Transformer 文獻綜述

## 1. Introduction
## 2. ViT 架構演進
## 3. 效能比較
## 4. 應用領域
## 5. 未來方向
## 6. 結論
"@ | Out-File vit_template.md -Encoding utf8

# 2. 執行生成
.\generate_review.ps1 -TemplateFile vit_template.md -Topic "Vision Transformer"

# 3. 等待完成（約 1-2 小時）

# 4. 查看結果
code results/review/final_review_*.md
```

**生成的報告包含**：
- 15+ 篇論文引用
- 完整 benchmark 比較表
- 所有論文的 arXiv/Papers with Code 連結
- 學術寫作風格的段落

---

### 範例 2：論文 Related Work 部分

```powershell
# 1. 建立大綱（針對您的論文主題）
@"
# Low-Rank Adaptation for Vision-Language Models

## 2. Related Work

### 2.1 Vision-Language Models
### 2.2 Parameter-Efficient Fine-Tuning
### 2.3 Low-Rank Adaptation Methods
### 2.4 Benchmark and Evaluation
"@ | Out-File related_work_template.md -Encoding utf8

# 2. 執行生成
.\generate_review.ps1 `
    -TemplateFile related_work_template.md `
    -Topic "Low-Rank Adaptation for VLMs" `
    -OutputDir "results/related_work"

# 3. 結果可直接複製到論文中
```

---

### 範例 3：多主題批次研究

```powershell
# 研究多個主題
$topics = @(
    @{template="vit_template.md"; topic="Vision Transformer"},
    @{template="bert_template.md"; topic="BERT Variants"},
    @{template="diffusion_template.md"; topic="Diffusion Models"}
)

foreach ($item in $topics) {
    Write-Host "Processing: $($item.topic)"
    .\generate_review.ps1 -TemplateFile $item.template -Topic $item.topic
}
```

---

## 進階技巧

### 技巧 1：更詳細的大綱 = 更好的結果

**❌ 過於簡略**：
```markdown
## Methods
```

**✅ 詳細說明**：
```markdown
## Methods Comparison

比較以下方法：
- LoRA
- Adapter
- Prefix Tuning
- Prompt Tuning

要求：效能數據、參數量、訓練時間
```

---

### 技巧 2：指定年份範圍

```markdown
## Recent Advances (2024-2026)

*僅包含 2024-2026 年的最新研究*
```

---

### 技巧 3：要求特定內容

```markdown
## Performance Analysis

**必須包含**：
- ImageNet 準確率比較表
- 參數量對比
- 訓練時間統計
- Top-5 模型詳細分析
```

---

## 輸出檔案說明

執行後會生成：

```
results/review/
├── final_review_20260319_143022.md    # 🎯 最終報告
├── node_0_shard_0.jsonl                # 原始研究結果
└── review_questions_20260319_143022.json  # 研究問題清單
```

### 最終報告結構

```markdown
# [主題] - Literature Review

**Generated:** 2026-03-19 14:30:22
**Research Time:** 85.3 minutes
**Papers Reviewed:** ~48

---

## [章節 1]
[GPT-5.4 生成的完整內容，包含引用]

## [章節 2]
[完整內容...]

---

## Research Metadata
[統計資訊、來源檔案]
```

---

## 常見問題

### Q1: 需要多少時間？
**A:** 取決於章節數量：
- 5 個章節：約 30-60 分鐘
- 10 個章節：約 1-2 小時
- 20 個章節：約 2-4 小時

### Q2: 結果準確嗎？
**A:** OpenResearcher 會：
- ✅ 實際搜尋 Google、arXiv、Papers with Code
- ✅ 開啟並閱讀論文頁面
- ✅ 驗證引用連結
- ✅ 提取真實的 benchmark 數據

但仍建議人工檢查！

### Q3: 可以自訂研究問題嗎？
**A:** 可以！不使用自動生成，直接提供問題 JSON：

```json
[
  {
    "qid": "custom_1",
    "question": "您的具體研究問題...",
    "answer": ""
  }
]
```

然後執行：
```powershell
python deploy_agent.py `
    --vllm_server_url AZURE_OPENAI `
    --dataset_name custom `
    --data_path your_questions.json `
    --browser_backend serper `
    --output_dir results/custom
```

### Q4: 可以中斷後繼續嗎？
**A:** 可以！OpenResearcher 會跳過已完成的問題。

### Q5: 結果可以編輯嗎？
**A:** 當然！生成的 Markdown 可以直接編輯、調整、補充。

---

## 手動方式（更靈活）

如果您想完全控制每個問題：

### 步驟 1：手動建立問題

```json
// my_research_questions.json
[
  {
    "qid": "intro",
    "question": "Write introduction for Vision Transformer review. Include: background, motivation, scope. Search recent papers for context.",
    "answer": ""
  },
  {
    "qid": "vit_arch",
    "question": "Survey ViT architectures (2020-2026). List 15+ papers with citations, innovations, benchmarks.",
    "answer": ""
  },
  {
    "qid": "performance",
    "question": "Create ImageNet performance comparison table. Include: model name, params, top-1 acc, year, link. Cover 20+ models.",
    "answer": ""
  }
]
```

### 步驟 2：執行研究

```powershell
python deploy_agent.py `
    --vllm_server_url AZURE_OPENAI `
    --dataset_name custom `
    --data_path my_research_questions.json `
    --browser_backend serper `
    --output_dir results/my_review
```

### 步驟 3：手動組裝報告

```powershell
# 讀取結果並組裝
$results = Get-Content results/my_review/node_0_shard_0.jsonl | ConvertFrom-Json

# 建立您的報告
$intro = ($results | Where-Object {$_.qid -eq "intro"}).answer
$arch = ($results | Where-Object {$_.qid -eq "vit_arch"}).answer
$perf = ($results | Where-Object {$_.qid -eq "performance"}).answer

@"
# My Review

## Introduction
$intro

## Architectures
$arch

## Performance
$perf
"@ | Out-File my_final_review.md -Encoding utf8
```

---

## 總結

✅ **自動化工作流程**：大綱 → 研究 → 報告（使用 `generate_review.ps1`）  
✅ **手動控制**：自訂問題 → 執行 → 手動組裝  
✅ **節省時間**：原本 3-5 天的工作，現在 1-3 小時  
✅ **高品質**：實際搜尋驗證，非虛構內容  

**現在就試試看！** 🚀
