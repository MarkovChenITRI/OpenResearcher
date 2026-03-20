# ⚠️ 重要：路徑與目錄結構說明

## 問題說明

感謝使用者指出路徑問題！原始設計有誤，已修正。

## 正確的目錄結構

```
OpenResearcher/                      ← 專案根目錄
├── .env                             ← 環境變數（必須）
├── deploy_agent.py                  ← OpenResearcher CLI 工具（必須）
├── utils/
│   └── azure_openai_generator.py   ← Azure OpenAI 整合
├── browser.py                       ← 瀏覽器工具
├── data_utils.py                    ← 資料工具
└── webapp/                          ← Web 應用目錄
    ├── app.py                       ← Flask 主應用
    ├── file_utils.py                ← 文件處理
    ├── templates/
    │   └── index.html              ← 前端介面
    ├── uploads/                     ← 上傳文件儲存
    ├── results/                     ← 研究結果儲存
    ├── start.ps1                    ← 啟動腳本
    ├── requirements.txt             ← Python 依賴
    └── README.md                    ← 說明文件
```

## 路徑處理邏輯

### 問題：app.py 如何找到 deploy_agent.py？

**原本的錯誤設計：**
```python
# ❌ 錯誤：假設 deploy_agent.py 在當前目錄
cmd = ["python", "deploy_agent.py", ...]
```

這樣會失敗，因為：
- `app.py` 在 `webapp/` 目錄
- `deploy_agent.py` 在上層目錄
- subprocess 從 `webapp/` 執行，找不到 `deploy_agent.py`

**修正後的設計：**
```python
# ✅ 正確：使用絕對路徑
from pathlib import Path

webapp_dir = Path(__file__).parent          # webapp/
project_root = webapp_dir.parent            # OpenResearcher/
deploy_agent_path = project_root / "deploy_agent.py"

cmd = ["python", str(deploy_agent_path), ...]
```

並且設定正確的工作目錄：
```python
subprocess.Popen(
    cmd,
    cwd=str(project_root)  # 在專案根目錄執行
)
```

## 為什麼這樣設計？

### 選項 1：把 app.py 放在專案根目錄
```
OpenResearcher/
├── app.py              ← 放在根目錄
├── deploy_agent.py
└── ...
```

**缺點：**
- 混亂！Web 應用與研究工具混在一起
- 難以管理
- 不符合專案組織最佳實踐

### 選項 2：把所有東西放進 webapp/
```
webapp/
├── app.py
├── deploy_agent.py     ← 複製到這裡？
└── ...
```

**缺點：**
- 檔案重複
- 難以維護
- 破壞原始專案結構

### 選項 3：使用相對路徑與工作目錄（✅ 採用）
```
OpenResearcher/          ← 專案根目錄
├── deploy_agent.py
└── webapp/
    └── app.py          ← 使用 Path 找到上層的 deploy_agent.py
```

**優點：**
- ✅ 清晰的專案結構
- ✅ Web 應用獨立模組化
- ✅ 不破壞原始專案
- ✅ 易於維護

## 實際執行流程

### 1. 啟動 Flask 應用

```powershell
# 位置：OpenResearcher/webapp/
PS> python app.py

# app.py 內部：
webapp_dir = Path(__file__).parent
# → OpenResearcher/webapp/

project_root = webapp_dir.parent
# → OpenResearcher/

deploy_agent_path = project_root / "deploy_agent.py"
# → OpenResearcher/deploy_agent.py
```

### 2. 執行研究任務

```python
# ResearchTask._run_research()
cmd = [
    "python",
    "OpenResearcher/deploy_agent.py",  # 絕對路徑
    "--vllm_server_url", "AZURE_OPENAI",
    "--data_path", "OpenResearcher/webapp/results/task_xxx/questions.json",  # 絕對路徑
    ...
]

# 在專案根目錄執行
subprocess.Popen(cmd, cwd="OpenResearcher/")
```

### 3. deploy_agent.py 的匯入

```python
# deploy_agent.py 會匯入：
from utils.azure_openai_generator import AzureOpenAIAsyncGenerator
from browser import BrowserTool
from data_utils import load_dataset

# 這些檔案在專案根目錄，所以必須：
# cwd=project_root  ← 確保匯入路徑正確
```

## 環境變數處理

### .env 位置
```
OpenResearcher/
├── .env              ← 放在專案根目錄
└── webapp/
    └── app.py        ← 可以正常讀取
```

### 為什麼可以讀取？

```python
# app.py 開頭
from dotenv import load_dotenv
load_dotenv()  # 會自動搜尋上層目錄的 .env
```

`python-dotenv` 會往上搜尋目錄樹，找到 `.env` 檔案。

## 啟動檢查清單

在執行 `python app.py` 之前，確認：

```powershell
# 1. 確認在 webapp 目錄
PS> Get-Location
# 應該顯示：...\OpenResearcher\webapp

# 2. 確認 deploy_agent.py 存在
PS> Test-Path ..\deploy_agent.py
# 應該輸出：True

# 3. 確認 .env 存在
PS> Test-Path ..\.env
# 應該輸出：True

# 4. 確認 utils 目錄存在
PS> Test-Path ..\utils
# 應該輸出：True
```

如果上述任何檢查失敗，代表目錄結構不正確！

## 常見錯誤

### 錯誤 1：在專案根目錄執行

```powershell
# ❌ 錯誤
PS OpenResearcher> python webapp/app.py
# 會找不到 templates/

# ✅ 正確
PS OpenResearcher> cd webapp
PS OpenResearcher\webapp> python app.py
```

### 錯誤 2：缺少 deploy_agent.py

```
FileNotFoundError: deploy_agent.py not found at ...
```

**原因：** 目錄結構不完整

**解決：** 確保完整克隆 OpenResearcher 專案

### 錯誤 3：import 錯誤

```
ModuleNotFoundError: No module named 'utils'
```

**原因：** subprocess 的 cwd 設定錯誤

**解決：** 確保 `subprocess.Popen(..., cwd=project_root)`

## 總結

**關鍵要點：**

1. ✅ **app.py 在 `webapp/` 目錄**
2. ✅ **deploy_agent.py 在專案根目錄**
3. ✅ **使用 `Path(__file__).parent.parent` 定位**
4. ✅ **subprocess 設定 `cwd=project_root`**
5. ✅ **必須在 `webapp/` 目錄執行 `python app.py`**

**修正清單：**

- [x] `app.py` - 使用絕對路徑與 cwd
- [x] `start.ps1` - 檢查目錄結構
- [x] `README.md` - 更新安裝說明
- [x] `INSTALL.md` - 新增故障排除
- [x] `PATH_STRUCTURE.md` - 本文件（新增）

---

**感謝回報問題！路徑處理已全面修正。** ✅
