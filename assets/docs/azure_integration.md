# Azure OpenAI Integration for OpenResearcher

This document describes how to use Azure OpenAI (e.g., GPT-4, GPT-5.4) as an alternative to the self-hosted vLLM server.

## Setup

### 1. Configure Azure Credentials

Add your Azure OpenAI credentials to `.env`:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Serper API (still required for web search)
SERPER_API_KEY=your_serper_key
```

### 2. Install Required Packages

```bash
uv pip install tiktoken
```

## Usage

The integration is fully compatible with the existing OpenResearcher workflow. Simply use `AZURE_OPENAI` as the `vllm_server_url` parameter.

### Quick Start Example

```python
import asyncio
from deploy_agent import run_one, BrowserPool
from utils.azure_openai_generator import AzureOpenAIAsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    # Initialize Azure OpenAI generator with context manager for proper cleanup
    async with AzureOpenAIAsyncGenerator(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        use_native_tools=True
    ) as generator:
        # Initialize browser pool
        browser_pool = BrowserPool(search_url=None, browser_backend="serper")

        # Run deep research
        await run_one(
            question="What is the latest news about OpenAI?",
            qid="azure_test",
            generator=generator,
            browser_pool=browser_pool,
        )

        browser_pool.cleanup("azure_test")

if __name__ == "__main__":
    asyncio.run(main())
```

### Using deploy_agent.py

The `deploy_agent.py` script automatically detects Azure OpenAI when you set `--vllm_server_url AZURE_OPENAI`:

```bash
python deploy_agent.py \
  --vllm_server_url AZURE_OPENAI \
  --dataset_name gaia \
  --browser_backend serper \
  --output_dir results/gaia_azure
```

### Benchmark Examples

#### GAIA Benchmark
```bash
python deploy_agent.py \
  --vllm_server_url AZURE_OPENAI \
  --dataset_name gaia \
  --browser_backend serper \
  --output_dir results/gaia_azure
```

#### BrowseComp Benchmark
```bash
python deploy_agent.py \
  --vllm_server_url AZURE_OPENAI \
  --dataset_name browsecomp \
  --browser_backend serper \
  --output_dir results/browsecomp_azure
```

#### xbench-DeepResearch Benchmark
```bash
python deploy_agent.py \
  --vllm_server_url AZURE_OPENAI \
  --dataset_name xbench \
  --browser_backend serper \
  --output_dir results/xbench_azure
```

#### Custom Questions
Create a JSON file with your questions:

```json
[
  {
    "qid": "test_001",
    "question": "Your research question here",
    "answer": ""
  }
]
```

Then run:

```bash
python deploy_agent.py \
  --vllm_server_url AZURE_OPENAI \
  --dataset_name custom \
  --data_path your_questions.json \
  --browser_backend serper \
  --output_dir results/custom_azure
```

## Technical Details

### Implementation

The Azure OpenAI integration is implemented in `utils/azure_openai_generator.py`, which provides:

- **AzureOpenAIAsyncGenerator**: A generator class compatible with OpenResearcher's architecture
- **Streaming support**: Token-by-token generation for interactive responses
- **Tool calling**: Native function calling support for browser tools
- **GPT-5.4 compatibility**: Uses `max_completion_tokens` parameter as required by newer models

### Modified Files

1. **utils/azure_openai_generator.py** (new)
   - Azure OpenAI API wrapper
   - Compatible with OpenResearcher's generator interface

2. **deploy_agent.py** (modified)
   - Added Azure OpenAI detection when `--vllm_server_url AZURE_OPENAI`
   - Automatically loads credentials from `.env`

3. **utils/__init__.py** (modified)
   - Conditional imports to avoid vllm dependency errors

### API Parameters

Azure OpenAI GPT-5.4 and newer models require `max_completion_tokens` instead of the legacy `max_tokens` parameter. This is automatically handled by the `AzureOpenAIAsyncGenerator` class.

## Evaluation

Evaluate results the same way as with self-hosted models:

```bash
python eval.py --input_dir results/gaia_azure
```

## Notes

- Azure OpenAI still requires Serper API for web search functionality
- Browser backend must be set to `serper` (local search engine not supported)
- All other OpenResearcher features work identically
- BrowseComp-Plus benchmark requires local search service and is not compatible with Azure OpenAI integration
