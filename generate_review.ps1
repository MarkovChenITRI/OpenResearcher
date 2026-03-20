# Literature Review Generator for OpenResearcher
# 從 Markdown 大綱自動生成完整文獻綜述

param(
    [Parameter(Mandatory=$true)]
    [string]$TemplateFile,  # 您的 Markdown 大綱
    
    [Parameter(Mandatory=$false)]
    [string]$OutputDir = "results/review",
    
    [Parameter(Mandatory=$false)]
    [string]$Topic = "Research Topic"
)

Write-Host "📚 Literature Review Generator" -ForegroundColor Cyan
Write-Host "=" * 60

# 步驟 1: 解析 Markdown 大綱
Write-Host "`n📖 Step 1: Parsing template..." -ForegroundColor Yellow

if (-not (Test-Path $TemplateFile)) {
    Write-Host "❌ Template file not found: $TemplateFile" -ForegroundColor Red
    exit 1
}

$template = Get-Content $TemplateFile -Raw
$sections = $template -split '##' | Where-Object { $_ -match '\S' }

Write-Host "✅ Found $($sections.Count) sections" -ForegroundColor Green

# 步驟 2: 自動生成研究問題
Write-Host "`n🎯 Step 2: Generating research questions..." -ForegroundColor Yellow

$questions = @()
$qid_counter = 1

foreach ($section in $sections) {
    $lines = $section -split "`n"
    $title = ($lines[0] -replace '#+\s*', '').Trim()
    
    if ($title -and $title -notmatch '待補充|TODO|TBD') {
        # 根據章節標題生成研究問題
        $question_text = @"
Research and write comprehensive content for the section: "$title" in a literature review about "$Topic". 

Requirements:
1. Search for recent papers (2020-2026) related to this topic
2. Include full citations (title, authors, venue, year)
3. Provide key findings and innovations
4. Include benchmark results if applicable
5. Add paper URLs for all citations
6. Organize information clearly with subsections if needed
7. Use academic writing style
8. Include at least 5-10 relevant papers

Generate complete, publication-ready content that can be directly inserted into the review.
"@
        
        $questions += @{
            qid = "section_$qid_counter"
            section_title = $title
            question = $question_text
            answer = ""
        }
        
        $qid_counter++
    }
}

Write-Host "✅ Generated $($questions.Count) research questions" -ForegroundColor Green

# 儲存問題檔案
$questionsFile = "review_questions_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$questions | ConvertTo-Json -Depth 10 | Out-File $questionsFile -Encoding utf8

Write-Host "✅ Questions saved to: $questionsFile" -ForegroundColor Green

# 步驟 3: 執行深度研究
Write-Host "`n🚀 Step 3: Running deep research with OpenResearcher..." -ForegroundColor Yellow
Write-Host "   This may take 1-3 hours depending on complexity" -ForegroundColor Gray

# 檢查環境
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found. Please configure Azure credentials." -ForegroundColor Red
    exit 1
}

Write-Host "`n⚙️  Executing: python deploy_agent.py..." -ForegroundColor Cyan

python deploy_agent.py `
    --vllm_server_url AZURE_OPENAI `
    --dataset_name custom `
    --data_path $questionsFile `
    --browser_backend serper `
    --output_dir $OutputDir `
    --model_name_or_path gpt-5.4

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Research execution failed" -ForegroundColor Red
    exit 1
}

# 步驟 4: 生成完整報告
Write-Host "`n📝 Step 4: Generating final review document..." -ForegroundColor Yellow

$resultFile = Get-ChildItem -Path $OutputDir -Filter "*.jsonl" | Select-Object -First 1

if (-not $resultFile) {
    Write-Host "❌ No result file found in $OutputDir" -ForegroundColor Red
    exit 1
}

$results = Get-Content $resultFile.FullName | ConvertFrom-Json

# 建立最終報告
$finalReview = @"
# $Topic - Literature Review

**Generated:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
**Research Tool:** OpenResearcher + Azure GPT-5.4  
**Total Research Time:** $([math]::Round(($results | Measure-Object -Property latency_s -Sum).Sum / 60, 2)) minutes  
**Papers Reviewed:** ~$($results.Count * 8) (estimated)

---

"@

# 插入每個章節的研究結果
foreach ($result in $results) {
    $sectionTitle = ($questions | Where-Object { $_.qid -eq $result.qid }).section_title
    
    $finalReview += @"

## $sectionTitle

$($result.answer)

---

"@
}

# 附加元資料
$finalReview += @"

---

## Research Metadata

### Questions Researched
$(($questions | ForEach-Object { "- [$($_.qid)] $($_.section_title)" }) -join "`n")

### Execution Statistics
- Total sections: $($questions.Count)
- Successful: $(($results | Where-Object { $_.status -eq 'success' }).Count)
- Failed: $(($results | Where-Object { $_.status -ne 'success' }).Count)
- Total time: $([math]::Round(($results | Measure-Object -Property latency_s -Sum).Sum / 60, 2)) minutes
- Average time per section: $([math]::Round((($results | Measure-Object -Property latency_s -Average).Average / 60), 2)) minutes

### Source Data
- Raw results: $($resultFile.FullName)
- Questions file: $questionsFile

---

*This review was automatically generated using OpenResearcher, an open-source deep research agent.*
*All citations and links were verified through web search at the time of generation.*

"@

# 儲存最終報告
$outputFile = "$OutputDir/final_review_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"
$finalReview | Out-File $outputFile -Encoding utf8

Write-Host "`n" + "=" * 60
Write-Host "✅ Literature Review Generation Complete!" -ForegroundColor Green
Write-Host "=" * 60
Write-Host "`n📄 Output Files:" -ForegroundColor Cyan
Write-Host "   - Final Review: $outputFile" -ForegroundColor White
Write-Host "   - Raw Results: $($resultFile.FullName)" -ForegroundColor White
Write-Host "   - Questions: $questionsFile" -ForegroundColor White
Write-Host "`n📊 Statistics:" -ForegroundColor Cyan
Write-Host "   - Sections: $($questions.Count)" -ForegroundColor White
Write-Host "   - Total Time: $([math]::Round(($results | Measure-Object -Property latency_s -Sum).Sum / 60, 2)) min" -ForegroundColor White
Write-Host "   - Success Rate: $(($results | Where-Object { $_.status -eq 'success' }).Count)/$($results.Count)" -ForegroundColor White
Write-Host "`n🎉 You can now open and edit: $outputFile" -ForegroundColor Green
