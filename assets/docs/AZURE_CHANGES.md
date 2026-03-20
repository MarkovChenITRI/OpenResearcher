# Azure OpenAI Integration - Changes Summary

## Modified Files

### 1. `utils/azure_openai_generator.py` (NEW)
**Purpose**: Azure OpenAI API wrapper compatible with OpenResearcher's generator interface

**Key Features**:
- Implements `AzureOpenAIAsyncGenerator` class
- Streaming token generation support
- Native tool calling support (for browser tools)
- Compatible with GPT-4, GPT-5.4 and other Azure OpenAI models
- Uses `max_completion_tokens` parameter for GPT-5.4 compatibility

### 2. `deploy_agent.py` (MODIFIED)
**Changes**: Added Azure OpenAI detection logic

```python
# Automatically detect and use Azure OpenAI when:
if args.vllm_server_url == "AZURE_OPENAI":
    from utils.azure_openai_generator import AzureOpenAIAsyncGenerator
    generator = AzureOpenAIAsyncGenerator(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        use_native_tools=True
    )
```

### 3. `utils/__init__.py` (MODIFIED)
**Changes**: Added conditional imports to avoid vllm dependency errors

```python
# Conditional import for Azure OpenAI
try:
    from .azure_openai_generator import AzureOpenAIAsyncGenerator
except ImportError:
    AzureOpenAIAsyncGenerator = None

# Conditional import for vLLM (optional)
try:
    from .vllm_generator import vLLMAsyncGenerator
except ImportError:
    vLLMAsyncGenerator = None
```

### 4. `.env` (MODIFIED)
**Added**: Azure OpenAI configuration section

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

## New Files

### Documentation
- `assets/docs/azure_integration.md` - Complete Azure OpenAI integration guide

### Testing
- `test_azure_integration.py` - Quick verification script for Azure setup

## Usage (Unchanged from Original Design)

The integration follows OpenResearcher's original design pattern. Users simply specify `AZURE_OPENAI` as the server URL:

### Original Pattern (vLLM)
```bash
bash run_agent.sh results/gaia 8001 2 gaia serper OpenResearcher/OpenResearcher-30B-A3B
```

### New Pattern (Azure OpenAI)
```bash
python deploy_agent.py \
  --vllm_server_url AZURE_OPENAI \
  --dataset_name gaia \
  --browser_backend serper \
  --output_dir results/gaia_azure
```

## Design Principles

1. **Minimal Changes**: Only modified what's necessary for Azure integration
2. **Backward Compatible**: All original functionality remains unchanged
3. **Consistent Interface**: Azure generator implements same interface as OpenAI/vLLM generators
4. **Original UX Preserved**: Usage pattern follows README's existing examples

## No Changes to Original Features

- ✅ Benchmark workflows unchanged
- ✅ Browser tools unchanged
- ✅ Evaluation pipeline unchanged
- ✅ Training recipes unchanged
- ✅ All original scripts work as before

## Important Notes

### UI and Workflow
- **No local UI provided** - This is a command-line batch processing tool
- **Questions must be pre-defined** in JSON files (or use preset benchmarks)
- **Online UI available** at [HuggingFace Demo](https://huggingface.co/spaces/OpenResearcher/OpenResearcher)
- Designed for batch processing multiple research questions

### Browser Backend Requirements
- **Serper API required** - Get free API key at https://serper.dev/ (2,500 free searches)
- Add `SERPER_API_KEY` to `.env` file
- Browser backend provides: web search (`browser.search`), page opening (`browser.open`), keyword finding (`browser.find`)
- Without browser backend, the agent cannot search the web or verify facts

### Output Format
Results are saved as **JSONL** files (JSON Lines format):
```jsonl
{"qid": "q1", "question": "...", "answer": "...", "messages": [...], "latency_s": 12.5, "status": "success"}
```

Each line contains:
- `qid` - Question ID
- `question` - Original question
- `answer` - Final answer
- `messages` - Complete conversation history (including all tool calls and responses)
- `latency_s` - Execution time in seconds
- `status` - "success" or "fail"

View results:
```powershell
# PowerShell
Get-Content results/gaia_azure/node_0_shard_0.jsonl | ConvertFrom-Json | Select-Object qid, answer

# Python
python eval.py --input_dir results/gaia_azure
```

## Limitations

- Azure OpenAI requires `serper` backend (local search not supported)
- BrowseComp-Plus benchmark not compatible (requires local search service)
- All other benchmarks (GAIA, BrowseComp, xbench) fully supported
- Must prepare question files in advance for custom research (no interactive UI)
