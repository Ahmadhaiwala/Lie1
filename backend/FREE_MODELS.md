# Free Models Available on OpenRouter

This project is configured to use **FREE** models available on OpenRouter. No costs incurred!

## 🆓 Current Default Model

**Meta LLaMA 3.2 3B Instruct** (`meta-llama/llama-3.2-3b-instruct:free`)
- Lightweight and fast
- Good for most tasks
- Completely free
- 3 billion parameters

## 🎯 Available Free Models

### Meta LLaMA Models (Recommended)
```python
# Best overall free model
'meta-llama/llama-3.2-3b-instruct:free'      # 3B params - Fast & efficient
'meta-llama/llama-3.2-1b-instruct:free'      # 1B params - Very fast
'meta-llama/llama-3.1-8b-instruct:free'      # 8B params - More capable
```

### Google Gemini Models
```python
'google/gemini-flash-1.5:free'               # Fast responses
'google/gemini-2.0-flash-exp:free'           # Experimental, faster
```

### Mistral Models
```python
'mistralai/mistral-7b-instruct:free'         # 7B params - Good quality
```

### Microsoft Phi Models
```python
'microsoft/phi-3-mini-128k-instruct:free'    # 128k context window
'microsoft/phi-3-medium-128k-instruct:free'  # More capable
```

### Qwen Models
```python
'qwen/qwen-2-7b-instruct:free'               # 7B params - Good performance
```

## 🔄 How to Switch Models

### Method 1: Update .env file
```bash
DEFAULT_MODEL=google/gemini-flash-1.5:free
```

### Method 2: In code
```python
from llm import LLMClient, LLMConfig

config = LLMConfig.from_env()
config.model = "google/gemini-flash-1.5:free"
client = LLMClient(config)
```

### Method 3: Per request
```python
client = LLMClient()
response = await client.complete(
    prompt="Hello!",
    model="mistralai/mistral-7b-instruct:free"
)
```

## 📊 Model Comparison

| Model | Size | Speed | Quality | Context | Best For |
|-------|------|-------|---------|---------|----------|
| llama-3.2-1b:free | 1B | ⚡⚡⚡ | ⭐⭐ | 8k | Simple tasks, speed |
| llama-3.2-3b:free | 3B | ⚡⚡ | ⭐⭐⭐ | 8k | General use (default) |
| llama-3.1-8b:free | 8B | ⚡ | ⭐⭐⭐⭐ | 8k | Complex tasks |
| gemini-flash-1.5:free | - | ⚡⚡⚡ | ⭐⭐⭐ | 32k | Fast responses |
| mistral-7b:free | 7B | ⚡⚡ | ⭐⭐⭐ | 8k | Balanced |
| phi-3-mini:free | 3.8B | ⚡⚡ | ⭐⭐⭐ | 128k | Long context |

## 💡 Recommendations

### For Web Scraping & Summarization
```python
# Fast and efficient
DEFAULT_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

### For Data Extraction
```python
# More accurate for structured data
DEFAULT_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

### For Q&A
```python
# Good balance
DEFAULT_MODEL=mistralai/mistral-7b-instruct:free
```

### For Long Documents
```python
# 128k context window
DEFAULT_MODEL=microsoft/phi-3-mini-128k-instruct:free
```

### For Speed
```python
# Fastest responses
DEFAULT_MODEL=meta-llama/llama-3.2-1b-instruct:free
```

## ⚙️ Configuration Tips

### Adjust Temperature
```python
# More creative (0.7-1.0)
LLM_TEMPERATURE=0.9

# More focused/deterministic (0.0-0.3)
LLM_TEMPERATURE=0.2
```

### Adjust Max Tokens
```python
# For summaries
LLM_MAX_TOKENS=500

# For detailed extraction
LLM_MAX_TOKENS=4096
```

## 🚀 Testing Models

Run the test script to try different models:

```python
import asyncio
from llm import LLMClient, LLMConfig

async def test_model(model_name):
    config = LLMConfig.from_env()
    config.model = model_name
    client = LLMClient(config)
    
    response = await client.complete(
        prompt="Explain what is web scraping in one sentence.",
        max_tokens=100
    )
    
    print(f"\n{model_name}:")
    print(response)

async def main():
    models = [
        "meta-llama/llama-3.2-3b-instruct:free",
        "google/gemini-flash-1.5:free",
        "mistralai/mistral-7b-instruct:free",
    ]
    
    for model in models:
        await test_model(model)

asyncio.run(main())
```

## 📝 Notes

- **All listed models are 100% FREE** on OpenRouter
- No credit card required for free models
- Rate limits may apply (usually generous)
- Free models may have occasional queuing during peak times
- Quality varies by task - experiment to find best fit

## 🔗 Resources

- [OpenRouter Free Models](https://openrouter.ai/models?order=newest&supported_parameters=tools&max_price=0)
- [Model Documentation](https://openrouter.ai/docs)
- [Model Pricing](https://openrouter.ai/models)

## ⚠️ Important

The `.env` file contains your actual API key. Keep it secure and never commit it to version control!

```bash
# Add to .gitignore
.env
```
