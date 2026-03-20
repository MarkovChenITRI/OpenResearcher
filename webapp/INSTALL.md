# OpenResearcher Web Application 安裝指南

完整的安裝與設定步驟

## 📦 系統需求

### 必要軟體
- Python 3.8+ (推薦 3.11+)
- Windows 10/11 或 Linux/macOS
- 瀏覽器：Chrome 90+, Edge 90+, Firefox 88+

### 必要 API 金鑰
- **Azure OpenAI API** (Microsoft Foundry)
- **Serper API** (Google Search)

## 🚀 快速開始（Windows PowerShell）

### 方法一：使用啟動腳本（推薦）

```powershell
# 1. 進入 webapp 目錄
cd webapp

# 2. 執行啟動腳本
.\start.ps1
```

腳本會自動：
- ✅ 檢查 Python 環境
- ✅ 驗證環境變數
- ✅ 安裝依賴套件
- ✅ 建立必要目錄
- ✅ 啟動應用

### 方法二：手動安裝

```powershell
# 1. 確認目錄結構
Get-Item ..\deploy_agent.py  # 應該存在

# 2. 進入 webapp 目錄
cd OpenResearcher/webapp

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 建立目錄
New-Item -ItemType Directory -Force uploads, results, templates

# 5. 啟動應用
python app.py
```

## 🔧 詳細設定步驟

### 步驟 1：環境變數設定

在專案根目錄（不是 webapp/）確認 `.env` 檔案存在並包含：

```bash
# Azure OpenAI Configuration (必須)
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-5.4
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Serper API (必須)
SERPER_API_KEY=your_serper_key_here

# OpenAI API (選用，僅用於評估)
OPENAI_API_KEY=your_openai_key_here
```

#### 如何取得 API 金鑰

**Azure OpenAI (Microsoft Foundry):**
1. 訪問 https://ai.azure.com/
2. 建立或選擇 Azure OpenAI 資源
3. 部署 GPT-5.4 模型
4. 取得 Endpoint 和 API Key

**Serper API:**
1. 訪問 https://serper.dev/
2. 註冊帳號
3. 免費方案提供 2,500 次搜尋
4. 複製 API Key

### 步驟 2：安裝 Python 依賴

```powershell
cd webapp
pip install -r requirements.txt
```

**核心依賴:**
```
Flask==3.0.0              # Web 框架
python-dotenv==1.0.0      # 環境變數
httpx==0.28.1             # HTTP 客戶端
tiktoken==0.12.0          # GPT tokenizer
markdown==3.5.1           # Markdown 處理
```

**文件處理依賴（選用）:**
```
PyPDF2==3.0.1            # PDF 解析
python-docx==1.1.0       # Word 文件
python-pptx==0.6.23      # PowerPoint
Pillow==10.1.0           # 圖片處理
```

如果不需要處理 PDF/DOCX/PPTX，可以只安裝核心依賴：

```powershell
pip install Flask python-dotenv httpx tiktoken markdown
```

### 步驟 3：測試安裝

```powershell
# 測試 Azure OpenAI 連線
cd ..
python test_azure_integration.py

# 應該看到：
# ✅ All tests passed!
```

### 步驟 4：啟動應用

```powershell
cd webapp
python app.py
```

成功啟動會看到：

```
=" * 60
🚀 OpenResearcher Web Application
=" * 60

📝 Features:
  1. 📁 Document analysis & question generation
  2. 📝 Visual question management
  3. 🚀 Real-time research execution
  4. 📊 Results tracking & export

🌐 Starting server at http://localhost:5000
=" * 60

 * Running on http://0.0.0.0:5000
```

### 步驟 5：開啟瀏覽器

訪問 http://localhost:5000

## 🐛 故障排除

### 問題 1：ModuleNotFoundError: No module named 'flask'

**原因：** Flask 未安裝

**解決：**
```powershell
pip install Flask
# 或安裝所有依賴
pip install -r requirements.txt
```

### 問題 2：找不到 .env 檔案

**原因：** `.env` 不在專案根目錄

**解決：**
```powershell
# 從 webapp/ 目錄檢查
Get-Content ..\.env

# 應該看到 AZURE_OPENAI_ENDPOINT 等變數
```

### 問題 3：Azure OpenAI 連線失敗

**原因：** API 金鑰或端點錯誤

**解決：**
```powershell
# 測試連線
cd ..
python test_azure_integration.py

# 檢查輸出是否有錯誤訊息
```

### 問題 4：研究無法啟動

**原因：** Serper API 金鑰未設定

**解決：**
```powershell
# 檢查 .env
Get-Content ..\.env | Select-String "SERPER"

# 應該看到：
# SERPER_API_KEY=your_key_here
```

### 問題 5：上傳文件後無法分析

**原因：** 文件處理依賴未安裝

**解決：**
```powershell
# 安裝文件處理依賴
pip install PyPDF2 python-docx python-pptx Pillow

# 或只處理 Markdown/Text 文件
# 這些不需要額外依賴
```

### 問題 6：Port 5000 被佔用

**原因：** 其他應用使用 5000 port

**解決：**

修改 `app.py` 最後一行：
```python
# 原本
app.run(debug=True, host='0.0.0.0', port=5000)

# 改成
app.run(debug=True, host='0.0.0.0', port=5001)  # 或其他 port
```

### 問題 7：找不到 deploy_agent.py

**原因：** 目錄結構不正確或不在正確位置執行

**檢查：**
```powershell
# 確認在 webapp 目錄
Get-Location
# 應該顯示：...\OpenResearcher\webapp

# 檢查上層目錄有 deploy_agent.py
Get-Item ..\deploy_agent.py
# 應該存在

# 檢查 app.py 的路徑處理
python -c "from pathlib import Path; print(Path('app.py').parent.parent / 'deploy_agent.py')"
```

**解決：**
```powershell
# 確保目錄結構正確
OpenResearcher/
├── deploy_agent.py          ← 必須在專案根目錄
└── webapp/
    └── app.py              ← 會自動找到上層的 deploy_agent.py

# 必須在 webapp 目錄啟動
cd OpenResearcher/webapp
python app.py
```

## 📋 檢查清單

安裝完成後，請確認：

- [ ] Python 3.8+ 已安裝
- [ ] `.env` 檔案在專案根目錄
- [ ] Azure OpenAI API 金鑰有效
- [ ] Serper API 金鑰有效
- [ ] `test_azure_integration.py` 測試通過
- [ ] Flask 應用成功啟動在 port 5000
- [ ] 可以在瀏覽器訪問 http://localhost:5000
- [ ] 四個 Tab 都能正常顯示
- [ ] 可以上傳文件（至少 .md, .txt）

## 🔄 更新與維護

### 更新依賴

```powershell
pip install --upgrade -r requirements.txt
```

### 清理暫存檔案

```powershell
# 清理上傳的文件
Remove-Item uploads/* -Force

# 清理研究結果（小心！）
Remove-Item results/* -Recurse -Force
```

### 備份資料

```powershell
# 備份重要結果
Copy-Item results backup_results -Recurse

# 備份問題清單（儲存在瀏覽器 localStorage）
# 使用應用內的「匯出」功能
```

## 🌐 部署到生產環境（進階）

### 使用 Gunicorn (Linux/macOS)

```bash
# 安裝 Gunicorn
pip install gunicorn

# 啟動應用
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用 Waitress (Windows)

```powershell
# 安裝 Waitress
pip install waitress

# 啟動應用
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### 使用 Docker（TODO）

```dockerfile
# Dockerfile (待建立)
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 🆘 需要協助？

- 查看 `README.md` 了解功能說明
- 查看 `app.py` 程式碼註解
- 提交 GitHub Issue
- 聯繫專案維護者

## 📚 下一步

安裝完成後：
1. 閱讀 `README.md` 了解功能
2. 嘗試上傳 Markdown 文件生成問題
3. 執行第一個研究任務
4. 查看結果並匯出

---

**祝研究順利！** 🎉
