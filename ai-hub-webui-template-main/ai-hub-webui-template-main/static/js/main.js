// 當頁面載入完成後,為按鈕綁定事件
document.addEventListener('DOMContentLoaded', function() {
    const loadButton = document.getElementById('loadData');
    const outputElement = document.getElementById('output');

    loadButton.addEventListener('click', async function() {
        try {
            // 顯示載入中狀態
            outputElement.textContent = '載入中...';
            loadButton.disabled = true;

            // 呼叫 API
            const response = await fetch('/api/data');
            
            // 檢查回應是否成功
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // 解析 JSON 資料
            const data = await response.json();
            
            // 顯示結果(格式化 JSON)
            outputElement.textContent = JSON.stringify(data, null, 2);
            
        } catch (error) {
            // 錯誤處理
            outputElement.textContent = `錯誤: ${error.message}`;
            console.error('載入資料時發生錯誤:', error);
        } finally {
            // 恢復按鈕狀態
            loadButton.disabled = false;
        }
    });
});