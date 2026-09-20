# CLOREL Verification Module - API Requirements

## Overview
This document specifies which APIs are required/optional for the CLOREL Search Intent & Business Verification module.

**Key Principle**: All required APIs have FREE tiers. No paid APIs are mandatory.

---

## API Matrix

### REQUIRED (Must Have - All Free)

#### 1. **Google Maps API** ✅ REQUIRED
- **Purpose**: Business discovery, validation, location checks
- **Free Tier**: $200 USD monthly credit
- **Cost After Free**: $7 per 1,000 requests
- **Status**: ✅ Already configured
- **Env Var**: `GOOGLE_MAPS_API_KEY`
- **Setup**: https://cloud.google.com/maps-platform

#### 2. **OpenRouter API** ✅ REQUIRED
- **Purpose**: LLM for evidence summarization, service fit assessment
- **Free Tier**: Free models available (no charges)
  - Meta LLaMA 3.2 (1B, 3B, 8B)
  - Google Gemini Flash
  - Mistral 7B
  - Microsoft Phi
- **Cost After Free**: Pay-as-you-go for premium models
- **Status**: ✅ Already configured
- **Env Var**: `OPENROUTER_API_KEY`
- **Setup**: https://openrouter.ai/keys

#### 3. **Ollama (Local LLM)** ✅ REQUIRED
- **Purpose**: Fallback LLM when OpenRouter unavailable
- **Free Tier**: 100% free, runs locally
- **Cost**: $0 (no API key, no tokens)
- **Status**: ✅ Already configured
- **Env Vars**: 
  - `OLLAMA_URL=http://localhost:11434`
  - `OLLAMA_MODEL=phi4-mini`
- **Setup**: https://ollama.ai/download
- **Download Model**: `ollama pull phi4-mini`

---

### HIGHLY RECOMMENDED (Should Have - All Free)

#### 4. **SerpAPI** ⭐ RECOMMENDED
- **Purpose**: Alternative search provider, SERP results
- **Free Tier**: 100 searches/month
- **Cost After Free**: $0.008-$0.02 per search
- **Status**: ⚠️ Optional but recommended
- **Env Var**: `SERP_API_KEY`
- **Setup**: https://serpapi.com/signup
- **Note**: Use Google Maps as primary, SerpAPI as backup

#### 5. **Google Trends** ✅ NO KEY NEEDED
- **Purpose**: Search volume/trends for demand signals
- **Free Tier**: 100% free (public data)
- **Cost**: $0
- **Status**: ✅ Works without API key
- **Library**: `pytrends` (Python)
- **Setup**: `pip install pytrends`
- **Note**: Optional enrichment signal

#### 6. **Playwright / Firecrawl** ✅ PARTIALLY FREE
- **Purpose**: Website crawling, capability detection
- **Free Tier**: 
  - Playwright: 100% free (local)
  - Firecrawl: Limited free tier
- **Playwright Cost**: $0 (local)
- **Firecrawl Cost**: $0.10-$0.50 per crawl (after free tier)
- **Status**: ✅ Playwright (free), ⭐ Firecrawl (recommended)
- **Env Var**: `FIRECRAWL_API_KEY` (if using Firecrawl)
- **Setup**: 
  - Playwright: `pip install playwright && playwright install`
  - Firecrawl: https://www.firecrawl.dev/

---

### OPTIONAL (Nice to Have)

#### 7. **Bright Data** (Advanced crawling)
- **Purpose**: Advanced web scraping, rotating proxies
- **Free Tier**: Limited (requires credit card)
- **Cost**: $0.01+ per GB
- **Status**: ❌ Not recommended for MVP
- **Note**: Use Firecrawl or Playwright instead

#### 8. **ScaleSerp** (Alternative SERP)
- **Purpose**: Alternative to SerpAPI
- **Free Tier**: 100 free requests/month
- **Status**: ⭐ Alternative to SerpAPI
- **Setup**: https://www.scaleserp.com/

---

## Minimum Setup (MVP - $0 Cost)

To run CLOREL with **zero cost**:

```bash
# Required API Keys
GOOGLE_MAPS_API_KEY=your_key_here
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Local (no keys needed)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=phi4-mini
```

**Setup Steps**:
1. Get Google Maps key (5 min)
2. Get OpenRouter key (2 min)
3. Download Ollama locally (10 min)
4. Done! Total: ~20 minutes, $0 cost

---

## Recommended Setup (Better Results - $0 Cost)

```bash
# Core
GOOGLE_MAPS_API_KEY=your_key_here
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=phi4-mini

# Recommended additions (all free tier)
SERP_API_KEY=your_serp_key_here  # 100 free searches/month
FIRECRAWL_API_KEY=your_key_here  # Limited free crawls
```

**Why**:
- SerpAPI: Backup search provider
- Firecrawl: Website crawling & capability detection
- Google Trends: Demand signal enrichment

---

## Cost Comparison

### Option 1: Minimal (MVP)
- Google Maps: $0 (within $200 credit)
- OpenRouter: $0 (free models)
- Ollama: $0 (local)
- **Total**: $0/month

### Option 2: Recommended
- Google Maps: $0 (within $200 credit)
- OpenRouter: $0 (free models)
- Ollama: $0 (local)
- SerpAPI: $0 (100 free searches)
- Firecrawl: $0 (limited free tier)
- **Total**: $0/month (within free tiers)

### Option 3: Production Scale
- Google Maps: ~$50-100/month
- OpenRouter: ~$10-20/month (premium models)
- SerpAPI: ~$10-20/month (if exceeding 100)
- Firecrawl: ~$5-10/month
- **Total**: ~$75-150/month

---

## How to Get Each Key

### Google Maps
1. Go to https://cloud.google.com/maps-platform
2. Enable "Maps JavaScript API" and "Places API"
3. Create API key
4. Add to `.env`: `GOOGLE_MAPS_API_KEY=your_key`

### OpenRouter
1. Go to https://openrouter.ai/keys
2. Sign up with email
3. Create API key
4. Add to `.env`: `OPENROUTER_API_KEY=sk-or-v1-xxxxx`

### SerpAPI
1. Go to https://serpapi.com/signup
2. Sign up (free, no credit card needed initially)
3. Copy API key
4. Add to `.env`: `SERP_API_KEY=your_key`

### Firecrawl
1. Go to https://www.firecrawl.dev/
2. Sign up
3. Get API key
4. Add to `.env`: `FIRECRAWL_API_KEY=your_key`

### Ollama (Local - No Key)
1. Download from https://ollama.ai/download
2. Install for your OS (Windows/Mac/Linux)
3. Run: `ollama pull phi4-mini`
4. Runs on `http://localhost:11434` automatically

---

## Implementation Status

### ✅ Implemented
- [x] Evidence model with source/timestamp tracking
- [x] LangGraph workflow nodes
- [x] Verification gates (all 4)
- [x] Deterministic routing logic
- [x] Website status checker
- [x] Search intent enrichment
- [x] Campaign filter validation
- [x] Audit trail support

### ⏳ Ready to Use
- [ ] Database persistence (SQLite/Postgres)
- [ ] API endpoints for lead verification
- [ ] Human review dashboard
- [ ] Email/Slack notifications

---

## Acceptance Criteria - API Requirements

✅ **All FREE APIs**:
- Google Maps: Free $200 credit
- OpenRouter: Free models
- Ollama: Free local
- SerpAPI: 100 free/month
- Firecrawl: Limited free tier
- Google Trends: 100% free

✅ **No hidden costs**: All services transparent about usage/costs

✅ **Fallback chains**:
- LLM: OpenRouter → Ollama (local)
- Search: Google Maps → SerpAPI
- Crawling: Playwright (local) → Firecrawl

---

## Troubleshooting

### "OpenRouter API Key not working"
→ Verify key format starts with `sk-or-v1-`
→ Check usage at https://openrouter.ai/account/usage

### "Google Maps quota exceeded"
→ You have $200 free credit/month
→ Enable billing to increase limits
→ Or reduce request frequency

### "Ollama not running"
→ Start Ollama: `ollama serve`
→ Download model: `ollama pull phi4-mini`
→ Check: `curl http://localhost:11434/api/tags`

### "SerpAPI giving 401"
→ Verify key at https://serpapi.com/account
→ Copy exact key (no spaces)

---

## Decisions Documented

Per CLOREL section 15 "Decisions needed before implementation":

1. **First Upstkey service**: Website development ✅
2. **Discovery provider**: Google Maps (primary) + SerpAPI (backup) ✅
3. **Trend enrichment**: Optional phase (can enable with Google Trends) ✅
4. **Minimum evidence**: 3+ evidence items from different sources ✅
5. **Rating/review unknown**: Include (don't treat as zero) ✅
6. **Reviewer tracking**: System logs all reviewer actions ✅

---

## Next Steps

1. **Get API keys** (see "How to Get Each Key" above)
2. **Add to .env**:
   ```bash
   GOOGLE_MAPS_API_KEY=xxx
   OPENROUTER_API_KEY=sk-or-v1-xxx
   SERP_API_KEY=xxx (optional)
   FIRECRAWL_API_KEY=xxx (optional)
   ```
3. **Download Ollama**: https://ollama.ai/download
4. **Run**: `ollama pull phi4-mini`
5. **Start backend**: `python main.py`
6. **Test verification**: API endpoints ready to use

---

**Document Version**: 1.0  
**Last Updated**: 2026-09-20  
**Status**: Implementation Ready
