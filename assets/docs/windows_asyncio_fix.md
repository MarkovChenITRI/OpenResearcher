# Windows AsyncIO Event Loop Fix

## Problem

On Windows, you may see this error when the script exits:

```
Exception ignored in: <function _ProactorBasePipeTransport.__del__ at 0x...>
Traceback (most recent call last):
  ...
RuntimeError: Event loop is closed
```

## Root Cause

This error occurs because the HTTP client (`httpx.AsyncClient`) is not properly closed before the asyncio event loop shuts down on Windows.

## Solution

The `AzureOpenAIAsyncGenerator` class now implements proper async context manager support:

### ✅ Recommended Usage (with context manager)

```python
async with AzureOpenAIAsyncGenerator(...) as generator:
    # Use generator
    response = await generator.chat_completion(...)
# HTTP client automatically closed here
```

### ⚠️ Alternative (manual cleanup)

```python
generator = AzureOpenAIAsyncGenerator(...)
try:
    response = await generator.chat_completion(...)
finally:
    await generator.aclose()  # Explicitly close
```

## Implementation Details

The fix includes:

1. **Async Context Manager** (`__aenter__` / `__aexit__`)
   - Properly closes HTTP client using `await client.aclose()`
   - Ensures cleanup happens within the running event loop

2. **Improved `shutdown()` method**
   - Handles both running and closed event loops
   - Provides fallback cleanup mechanisms

3. **Safe `__del__` destructor**
   - Catches all exceptions to prevent error messages
   - Only calls cleanup if not already closed

## Testing

Run the test to verify the fix:

```bash
python test_azure_integration.py
```

You should see no event loop errors when the script exits.
