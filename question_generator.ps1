# OpenResearcher Question Generator
# 互動式問題生成工具

param(
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "research_questions_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
)

Write-Host "📝 OpenResearcher - Question Generator" -ForegroundColor Cyan
Write-Host "=" * 60

$questions = @()

Write-Host "`n選擇模式：" -ForegroundColor Yellow
Write-Host "1. 快速模式（單一問題）"
Write-Host "2. 批次模式（多個問題）"
Write-Host "3. 範本模式（使用預設範本）"
$mode = Read-Host "`n選擇 (1-3)"

switch ($mode) {
    "1" {
        # 快速模式
        Write-Host "`n📌 快速模式" -ForegroundColor Green
        $question = Read-Host "請輸入您的研究問題"
        $qid = "q_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        
        $questions += @{
            qid = $qid
            question = $question
            answer = ""
        }
        
        Write-Host "✅ 問題已新增！" -ForegroundColor Green
    }
    
    "2" {
        # 批次模式
        Write-Host "`n📋 批次模式" -ForegroundColor Green
        Write-Host "輸入問題（輸入空白行結束）`n" -ForegroundColor Yellow
        
        $counter = 1
        do {
            $question = Read-Host "問題 #$counter"
            
            if ($question) {
                $qid = Read-Host "  問題 ID（直接按 Enter 使用自動 ID）"
                if (-not $qid) {
                    $qid = "q$counter"
                }
                
                $questions += @{
                    qid = $qid
                    question = $question
                    answer = ""
                }
                
                Write-Host "  ✅ 已新增！`n" -ForegroundColor Green
                $counter++
            }
        } while ($question)
        
        Write-Host "`n✅ 共新增 $($questions.Count) 個問題！" -ForegroundColor Green
    }
    
    "3" {
        # 範本模式
        Write-Host "`n📚 範本模式" -ForegroundColor Green
        Write-Host "`n選擇研究類型：" -ForegroundColor Yellow
        Write-Host "1. 文獻調查（Literature Survey）"
        Write-Host "2. 論文撰寫（Paper Writing）"
        Write-Host "3. 技術比較（Technology Comparison）"
        Write-Host "4. 市場研究（Market Research）"
        Write-Host "5. 實驗設計（Experiment Design）"
        
        $template_choice = Read-Host "`n選擇 (1-5)"
        $topic = Read-Host "研究主題（例如：Vision Transformer）"
        
        switch ($template_choice) {
            "1" {
                # 文獻調查
                $questions += @{
                    qid = "survey_overview"
                    question = "Provide a comprehensive survey of $topic (2020-2026). Include: 1) Historical development, 2) Top 15-20 papers with full citations, 3) Key innovations, 4) Performance benchmarks, 5) Current limitations. All papers must include links."
                    answer = ""
                }
                $questions += @{
                    qid = "survey_sota"
                    question = "Identify state-of-the-art methods in $topic. Compare: 1) Performance metrics, 2) Computational efficiency, 3) Practical applications. Create comparison table with sources."
                    answer = ""
                }
                $questions += @{
                    qid = "survey_trends"
                    question = "Analyze future research trends in $topic based on recent papers (2024-2026). Include emerging directions and open challenges."
                    answer = ""
                }
            }
            
            "2" {
                # 論文撰寫
                $questions += @{
                    qid = "paper_introduction"
                    question = "Write an Introduction section for a paper on '$topic'. Include: 1) Broad context and motivation, 2) Problem statement, 3) Existing solutions and their limitations, 4) Research gap, 5) Proposed contribution, 6) Paper organization. Use academic writing style with citations from recent papers (2022-2026)."
                    answer = ""
                }
                $questions += @{
                    qid = "paper_related_work"
                    question = "Write a Related Work section for '$topic'. Organize into subsections: 1) Foundational approaches (5-8 papers), 2) Recent advances (5-8 papers), 3) Related domains. Include full citations and quantitative comparisons where applicable."
                    answer = ""
                }
                $questions += @{
                    qid = "paper_experiments"
                    question = "Design comprehensive experiments for evaluating '$topic'. Specify: 1) Standard benchmarks and datasets (with download links), 2) Baseline methods for comparison, 3) Evaluation metrics, 4) Ablation study components. Base on experimental setups from recent papers (2023-2026)."
                    answer = ""
                }
            }
            
            "3" {
                # 技術比較
                $questions += @{
                    qid = "tech_comparison"
                    question = "Compare top approaches/tools for $topic. Create detailed comparison table including: 1) Features, 2) Performance metrics, 3) Pros and cons, 4) Use cases, 5) Pricing/licensing. Include at least 10 items with sources."
                    answer = ""
                }
                $questions += @{
                    qid = "tech_recommendations"
                    question = "Based on comparison of $topic approaches, provide recommendations for: 1) Research/academic use, 2) Industry production use, 3) Resource-constrained scenarios. Justify with benchmark results."
                    answer = ""
                }
            }
            
            "4" {
                # 市場研究
                $questions += @{
                    qid = "market_overview"
                    question = "Research the $topic market landscape. Include: 1) Major players and their market share, 2) Recent developments and trends (2024-2026), 3) Market size and growth projections, 4) Key competitors comparison. Provide sources for all claims."
                    answer = ""
                }
                $questions += @{
                    qid = "market_analysis"
                    question = "Analyze competitive advantages and differentiators in the $topic market. Compare features, pricing, target users, and unique selling points. Create comparison matrix."
                    answer = ""
                }
            }
            
            "5" {
                # 實驗設計
                $questions += @{
                    qid = "exp_dataset"
                    question = "Identify appropriate datasets for evaluating $topic. List: 1) Dataset name, 2) Size and composition, 3) Download link, 4) Previous works using this dataset, 5) Benchmark results. Include at least 5 datasets."
                    answer = ""
                }
                $questions += @{
                    qid = "exp_baselines"
                    question = "Identify baseline methods for $topic experiments. For each baseline: 1) Method name, 2) Key papers, 3) Reported performance, 4) Implementation availability (GitHub links), 5) Hyperparameters. Include 5-10 strong baselines."
                    answer = ""
                }
                $questions += @{
                    qid = "exp_metrics"
                    question = "Recommend evaluation metrics for $topic. Explain: 1) Standard metrics used in the field, 2) Why each metric is important, 3) How to calculate them, 4) Typical value ranges. Cite papers that use these metrics."
                    answer = ""
                }
            }
        }
        
        Write-Host "`n✅ 已生成 $($questions.Count) 個範本問題！" -ForegroundColor Green
    }
}

# 顯示問題預覽
Write-Host "`n" + "=" * 60
Write-Host "📋 問題預覽：" -ForegroundColor Cyan
Write-Host "=" * 60
foreach ($q in $questions) {
    Write-Host "`n[$($q.qid)]" -ForegroundColor Yellow
    Write-Host $q.question -ForegroundColor White
}

# 詢問是否儲存
Write-Host "`n" + "=" * 60
$save = Read-Host "儲存到 $OutputFile? (y/n)"

if ($save -eq 'y') {
    $questions | ConvertTo-Json -Depth 10 | Out-File $OutputFile -Encoding utf8
    Write-Host "`n✅ 已儲存到: $OutputFile" -ForegroundColor Green
    
    # 詢問是否立即執行
    Write-Host "`n是否立即執行研究？" -ForegroundColor Yellow
    $execute = Read-Host "(y/n)"
    
    if ($execute -eq 'y') {
        $output_dir = Read-Host "輸出目錄（預設: results/research）"
        if (-not $output_dir) {
            $output_dir = "results/research"
        }
        
        Write-Host "`n🚀 開始執行..." -ForegroundColor Cyan
        Write-Host "預計時間: $($questions.Count * 10-20) 分鐘`n" -ForegroundColor Gray
        
        python deploy_agent.py `
            --vllm_server_url AZURE_OPENAI `
            --dataset_name custom `
            --data_path $OutputFile `
            --browser_backend serper `
            --output_dir $output_dir `
            --model_name_or_path gpt-5.4
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ 研究完成！" -ForegroundColor Green
            Write-Host "結果位置: $output_dir/node_0_shard_0.jsonl" -ForegroundColor Cyan
            
            $view = Read-Host "`n是否查看結果？(y/n)"
            if ($view -eq 'y') {
                $results = Get-Content "$output_dir/node_0_shard_0.jsonl" | ConvertFrom-Json
                foreach ($result in $results) {
                    Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
                    Write-Host "[$($result.qid)] $($result.question)" -ForegroundColor Yellow
                    Write-Host "=" * 60 -ForegroundColor Cyan
                    Write-Host $result.answer -ForegroundColor White
                }
            }
        }
    }
} else {
    Write-Host "`n❌ 已取消" -ForegroundColor Red
}

Write-Host "`n" + "=" * 60
Write-Host "📚 提示：" -ForegroundColor Yellow
Write-Host "  - 手動執行: python deploy_agent.py --dataset_name custom --data_path $OutputFile ..." -ForegroundColor Gray
Write-Host "  - 編輯問題: code $OutputFile" -ForegroundColor Gray
Write-Host "=" * 60
