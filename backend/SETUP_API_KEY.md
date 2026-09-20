# API Key Setup Guide

⚠️ **IMPORTANT**: Never commit your `.env` file with real API keys to Git!

## Quick Setup

### 1. Copy the example environment file
```bash
copy .env.example .env
```

### 2. Get Your Free OpenRouter API Key

1. Go to [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for a free account
3. Go to [Keys page](https://openrouter.ai/keys)
4. Create a new API key
5. Copy the key (starts with `sk-or-v1-...`)

### 3. Add Your API Key to .env

Open `backend/.env` and replace:
```bash
OPENROUTER_API_KEY=your-openrouter-api-key-here
```

With your actual key:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

### 4. Verify Setup

Run the test script:
```bash
cd backend
python test_llm_connection.py
```

You should see:
```
✅ Connection successful!
```

## Security Best Practices

### ✅ DO:
- Keep `.env` in `.gitignore`
- Use `.env.example` for templates (without real keys)
- Add your real API key only to your local `.env` file
- Rotate API keys periodically
- Use different keys for development and production

### ❌ DON'T:
- Commit `.env` files to Git
- Share API keys in chat, email, or documents
- Hardcode API keys in source code
- Push API keys to public repositories

## Troubleshooting

### Issue: "OPENROUTER_API_KEY environment variable is required"
**Solution**: Make sure you've created the `.env` file and added your API key.

### Issue: "Connection test failed"
**Solutions**:
1. Check your API key is correct
2. Verify you have internet connection
3. Check OpenRouter service status
4. Make sure the API key hasn't expired

### Issue: ".env file not found"
**Solution**: Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

## Free Models

This project uses 100% FREE models by default. You won't be charged anything!

Current default: `meta-llama/llama-3.2-3b-instruct:free`

See `FREE_MODELS.md` for more information about available free models.

## Multiple Developers

Each developer should:
1. Create their own `.env` file (never commit it)
2. Get their own OpenRouter API key
3. Never share API keys

The `.env.example` file serves as a template for all developers.
