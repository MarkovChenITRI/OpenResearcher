# Azure OpenAI Integration - Windows Event Loop Fix

## 問題描述

在 Windows 上使用 Azure OpenAI 整合時，您可能看到以下錯誤：

```
Exception ignored in: <function _ProactorBasePipeTransport.__del__ at 0x...>
Traceback (most recent call last):
  ...
RuntimeError: Event loop is closed
```

## 原因

此錯誤發生在 Windows 的 `asyncio` 事件循環關閉時，HTTP 客戶端（`httpx.AsyncClient`）尚未正確關閉。

## 解決方案

已在以下文件中實施修正：

### 1. `utils/azure_openai_generator.py`

**新增功能**：
- ✅ Async context manager 支援（`__aenter__` / `__aexit__`）
- ✅ `aclose()` 方法用於正確的異步關閉
- ✅ 改進的 `shutdown()` 方法處理各種情況

**推薦用法**（使用 context manager）：
```python
async with AzureOpenAIAsyncGenerator(...) as generator:
    response = await generator.chat_completion(...)
# HTTP 客戶端在這裡自動關閉
```

**替代方案**（手動清理）：
```python
generator = AzureOpenAIAsyncGenerator(...)
try:
    response = await generator.chat_completion(...)
finally:
    await generator.aclose()
```

### 2. `deploy_agent.py`

**修改位置**：Worker 函數的 `finally` 區塊

```python
finally:
    # Clean up generator
    if hasattr(generator, 'aclose'):
        await generator.aclose()
    elif hasattr(generator, 'shutdown'):
        generator.shutdown()
    print(f"[Worker {worker_idx}] Done.")
```

### 3. `test_azure_integration.py`

**更新**：使用 async context manager 進行測試

```python
async with AzureOpenAIAsyncGenerator(...) as generator:
    response = await generator.chat_completion(...)
```

## 技術細節

### Context Manager 實作

```python
async def __aenter__(self):
    """Async context manager entry"""
    return self

async def __aexit__(self, exc_type, exc_val, exc_tb):
    """Async context manager exit - properly close client"""
    await self.aclose()
    return False

async def aclose(self):
    """Async close method"""
    if not self._closed:
        self._closed = True
        await self.client.aclose()
```

### 改進的 shutdown() 方法

處理三種情況：
1. **事件循環正在運行**：使用 `create_task()` 調度關閉
2. **事件循環未運行**：創建新循環並使用 `run_until_complete()`
3. **備用方案**：直接關閉底層傳輸層

## 驗證

執行測試確認修正：

```bash
python test_azure_integration.py
```

✅ 腳本應該正常結束，不會出現事件循環錯誤訊息

## 相關文件

- `assets/docs/azure_integration.md` - 完整使用指南
- `assets/docs/windows_asyncio_fix.md` - Windows asyncio 修正詳情
- `assets/docs/AZURE_CHANGES.md` - 所有修改的總結

## 原始專案相容性

✅ 此修正不影響原始 OpenResearcher 的任何功能
✅ 所有現有的 vLLM 和 OpenAI generator 正常運作
✅ 僅新增 Azure OpenAI 的清理邏輯
