# Flask API 與 WebUI 範例模板

在開發 AI 技術應用程式時，研究成果常停留在工程驗證階段，僅以程式輸出或日誌呈現，雖能支援除錯，但在展示與操作上不足。本模板提供一個基礎的 Flask API + 前端 的模板，讓開發者可以直接套用到自己的專案，快速把研究邏輯包裝成 API 與 WebUI，方便非前後端人員快速完成概念驗證，也能提升成果的理解與效益。

## 快速開始

請先準備好 Python 3.x 與 Flask 套件，並確保瀏覽器可用於測試。在專案根目錄執行以下指令：

```bash
pip install flask
python app.py
```

執行後，瀏覽器開啟 `http://127.0.0.1:5000/` 會顯示如同下方的 WebUI 頁面；訪問 `http://127.0.0.1:5000/api/data` 或點擊「載入資料」按鈕則會顯示 API 回傳的 JSON 資料。

![](https://github.com/R300-AI/flask-webui-template/blob/main/assets/demo_ui.png)

跑起來之後，你會注意到專案是由以下檔案目錄組成，每個檔案在整體流程中都有明確角色，方便理解系統的組成：
```
flask-webui-template/
├── app.py              # 執行這個 Python 程式會啟動 Flask 服務，預設監聽在 127.0.0.1:5000。
                        # 如果要讓外部電腦也能連線，可以在程式裡設定：
                        # app.run(host=0.0.0.0, port=5000)
├── requirements.txt    # 需要安裝的 Python 套件清單，確保服務能正常運作
├── templates/          # 放各個頁面，使用 HTML 定義瀏覽器顯示的內容與結構
│   └── index.html      # 網站的首頁頁面，要新增其他頁面就建立新的 HTML 放在這裡
└── static/             # 放功能元件，支援頁面的美觀與互動
    ├── css/            # 樣式元件，使用 CSS 控制頁面的顏色、字型、排版
    ├── js/             # 互動元件，使用 JavaScript 控制按鈕、輸入框、表單等操作
    └── img/            # 圖片元件，使用 PNG、JPG、SVG 顯示在頁面上的圖示或照片
```

### API

端點回傳 JSON 格式的資料,供前端程式透過**HTTP 請求**或其他服務呼叫。 你可以在 `app.py` 的路由函式中, 將你的運算處理程序添加至 return 之前:

```python
@app.route("/api/data")  # 定義 API 端點路徑, 允許使用者以 http://<ip-address>:<port>/api/data 呼叫該功能
def get_data():
    # 在此執行你的模型推論或演算法(例如: result = your_model.predict(data))

    return jsonify({
        "message": "Hello, this is demo data!",
        "values": [1, 2, 3, 4, 5]
    })  # 將此處替換為你的回傳結果
```

### Web

端點回傳 HTML 渲染頁面,供使用者透過瀏覽器瀏覽。修改 `templates/index.html` 即可調整頁面內容與佈局:

```python
@app.route("/")  # 定義首頁路徑,訪問 http://127.0.0.1:5000/ 會顯示此頁面
def index():
    return render_template("index.html")  # 渲染 templates/index.html 並回傳
```

前端透過 `static/js/main.js` 呼叫 API 並將結果動態顯示在頁面上。

## 完整範例

詳細的程式碼實作請參考專案中的 `app.py`、`templates/index.html` 與 `static/js/main.js`。
