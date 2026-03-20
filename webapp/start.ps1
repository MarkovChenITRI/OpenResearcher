# OpenResearcher Web Application Quick Start
# 快速啟動腳本

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🚀 OpenResearcher Web Application" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# 確認當前在 webapp 目錄
$currentDir = (Get-Location).Path
if ($currentDir -notlike "*\webapp") {
    Write-Host "❌ 請在 webapp 目錄執行此腳本！" -ForegroundColor Red
    Write-Host "   cd webapp" -ForegroundColor Yellow
    Write-Host "   .\start.ps1" -ForegroundColor Yellow
    exit 1
}

# 檢查 Python
Write-Host "1️⃣  檢查 Python 環境..." -ForegroundColor Green
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ $pythonVersion" -ForegroundColor Gray
} else {
    Write-Host "   ❌ Python 未安裝！請先安裝 Python 3.8+" -ForegroundColor Red
    exit 1
}

# 檢查專案根目錄的 deploy_agent.py
Write-Host ""
Write-Host "2️⃣  檢查專案結構..." -ForegroundColor Green
$projectRoot = Split-Path -Parent $currentDir
$deployAgentPath = Join-Path $projectRoot "deploy_agent.py"
if (Test-Path $deployAgentPath) {
    Write-Host "   ✅ 找到 deploy_agent.py" -ForegroundColor Gray
} else {
    Write-Host "   ❌ 找不到 deploy_agent.py！" -ForegroundColor Red
    Write-Host "   期望位置: $deployAgentPath" -ForegroundColor Yellow
    exit 1
}

# 檢查環境變數
Write-Host ""
Write-Host "3️⃣  檢查環境變數..." -ForegroundColor Green
$envFile = Join-Path $projectRoot ".env"
if (Test-Path $envFile) {
    Write-Host "   ✅ .env 檔案存在" -ForegroundColor Gray
    
    # 檢查必要變數
    $envContent = Get-Content $envFile -Raw
    $requiredVars = @(
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT",
        "SERPER_API_KEY"
    )
    
    $missing = @()
    foreach ($var in $requiredVars) {
        if ($envContent -notmatch "$var=") {
            $missing += $var
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Host "   ⚠️  缺少以下環境變數：" -ForegroundColor Yellow
        foreach ($var in $missing) {
            Write-Host "      - $var" -ForegroundColor Yellow
        }
        Write-Host "   請在 ../.env 中設定這些變數" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ 所有必要環境變數已設定" -ForegroundColor Gray
    }
} else {
    Write-Host "   ❌ 找不到 .env 檔案！" -ForegroundColor Red
    Write-Host "   請在專案根目錄建立 .env 檔案" -ForegroundColor Red
    Write-Host "   位置: $envFile" -ForegroundColor Yellow
    exit 1
}

# 安裝依賴
Write-Host ""
Write-Host "4️⃣  安裝 Python 依賴..." -ForegroundColor Green
if (Test-Path "requirements.txt") {
    Write-Host "   安裝中..." -ForegroundColor Gray
    pip install -q -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ 依賴安裝完成" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️  部分依賴安裝失敗，但仍可繼續" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ 找不到 requirements.txt" -ForegroundColor Red
    exit 1
}

# 建立必要目錄
Write-Host ""
Write-Host "5️⃣  建立必要目錄..." -ForegroundColor Green
$dirs = @("uploads", "results", "templates")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   ✅ 已建立 $dir/" -ForegroundColor Gray
    } else {
        Write-Host "   ✅ $dir/ 已存在" -ForegroundColor Gray
    }
}

# 啟動應用
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🎉 準備完成！啟動應用..." -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 功能：" -ForegroundColor Cyan
Write-Host "   1. 📁 文件分析 & 問題生成" -ForegroundColor White
Write-Host "   2. 📝 視覺化問題管理" -ForegroundColor White
Write-Host "   3. 🚀 即時研究執行" -ForegroundColor White
Write-Host "   4. 📊 結果追蹤 & 匯出" -ForegroundColor White
Write-Host ""
Write-Host "🌐 應用位址: http://localhost:5000" -ForegroundColor Green
Write-Host "⏹️  停止方式: Ctrl+C" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# 啟動
python app.py
