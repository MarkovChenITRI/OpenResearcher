# OpenResearcher Web Application

Flask-based web interface for OpenResearcher deep research tool.

## Quick Start

```bash
# Install dependencies
pip install flask python-dotenv httpx tiktoken

# Run from project root
python app.py
```

Visit http://localhost:5000

## Features

- 📁 Document analysis & question generation
- 📝 Visual question management with AI refinement
- 🚀 Real-time research execution
- 📊 Results tracking & export

## Requirements

- Python 3.8+
- Azure OpenAI API key
- Serper API key (Google Search)

## Configuration

Ensure `.env` file contains:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT=gpt-5.4
AZURE_OPENAI_API_VERSION=2024-12-01-preview
SERPER_API_KEY=your_serper_key
```

## Security

- ✅ App runs from project root (secure)
- ✅ No parent directory access
- ✅ All paths are relative to root

## License

MIT
