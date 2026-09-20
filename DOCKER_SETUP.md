# LeadBot AI - Docker Setup Guide

Complete setup to get real lead generation working with Crawl4AI, Ollama, and React dashboard.

## Prerequisites

- **Docker Desktop** installed on Windows: https://www.docker.com/products/docker-desktop
- **Git** (to clone or manage the repo)
- ~10GB disk space (for Docker images)

## Quick Start (3 Steps)

### Step 1: Stop the Local Processes

Kill any running processes:

```powershell
# Kill the Python backend process (if running)
Get-Process python | Stop-Process -Force

# Kill the Node frontend process (if running)
Get-Process node | Stop-Process -Force
```

### Step 2: Start Docker Containers

```powershell
cd C:\Users\aman\Lie1

# Build and start all containers
docker-compose up --build

# First time will take 5-10 minutes:
# - Downloads Python 3.11 image
# - Installs all dependencies + Crawl4AI
# - Downloads Ollama image
# - Pulls llama3 model (4.7GB - one time)
# - Starts all 3 services
```

**Expected output:**
```
leadbot-ollama      | Listening on 127.0.0.1:11434
leadbot-backend     | INFO:     Uvicorn running on http://0.0.0.0:8000
leadbot-frontend    | VITE v... ready in ... ms
```

### Step 3: Open the Dashboard

Go to **http://localhost:5174** in your browser.

---

## What Each Container Does

### 1. Ollama Container
- Runs local LLM (llama3)
- Port: 11434
- Auto-pulls llama3 model on first start
- Scoring leads in real-time

### 2. Backend Container
- FastAPI server with Crawl4AI
- Port: 8000
- Full agentic loop:
  - Generates search queries (LLM)
  - Crawls websites (Crawl4AI - NOW WORKS!)
  - Scores leads (LLM)
  - Enriches data (LLM)
  - Saves to `/backend/leads_output/`

### 3. Frontend Container
- React + Vite dev server
- Port: 5174
- Auto-reloads on code changes
- Connects to backend on `http://localhost:8000`

---

## Testing the System

### Test 1: API Health

```powershell
curl http://localhost:8000/health
```

Should return:
```json
{"status":"ok","service":"LeadBot AI API","version":"1.0.0"}
```

### Test 2: Run a Lead Generation Job

Open http://localhost:5174/run and:

1. **Service:** Select `website`
2. **Query:** Enter `Digital Marketing Agencies in New York`
3. **Click:** "Start Job"

**What happens:**
- Job submits to backend
- Crawl4AI crawls real websites (now working!)
- Ollama scores each lead (0-1 scale)
- Results appear on dashboard in ~30-60 seconds

### Test 3: View Dashboard

Go to http://localhost:5174/dashboard

You should see:
- Real leads from Crawl4AI (not mock data!)
- Lead scores
- Filter by service, location, score
- Analytics charts

---

## Common Commands

### View Live Logs

```powershell
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just Ollama
docker-compose logs -f ollama

# Just frontend
docker-compose logs -f frontend
```

### Stop Containers

```powershell
docker-compose down

# Remove volumes too (clears data)
docker-compose down -v
```

### Rebuild Backend (after code changes)

```powershell
docker-compose up --build backend
```

### Access Backend Shell

```powershell
docker-compose exec backend bash
```

### Check Container Status

```powershell
docker-compose ps
```

---

## Troubleshooting

### Port Already in Use

If ports 8000, 5174, or 11434 are in use:

```powershell
# Find what's using the port
Get-NetTCPConnection -LocalPort 8000

# Kill it
Stop-Process -Id <PID> -Force

# Or change ports in docker-compose.yml
```

### Ollama Model Not Downloading

```powershell
# Check Ollama logs
docker-compose logs ollama

# Manually pull llama3
docker-compose exec ollama ollama pull llama3
```

### Backend Can't Connect to Ollama

```powershell
# Test connection from backend
docker-compose exec backend curl http://ollama:11434/api/tags

# Check network
docker network ls
docker network inspect leadbot-network
```

### Out of Memory (Ollama)

Llama3 needs ~8GB RAM. If system is slow:

```powershell
# Switch to smaller model in docker-compose.yml
DEFAULT_MODEL=phi4-mini  # 2.5GB
# or
DEFAULT_MODEL=qwen2.5-coder:1.5b  # 986MB
```

### Leads Still Not Showing

1. Check backend logs: `docker-compose logs backend`
2. Check for errors in `/backend/logs/scheduler_*.log`
3. Verify Ollama is running: `docker-compose logs ollama`
4. Try running job again with different query

---

## Development Workflow

### Edit Backend Code

Changes are auto-reloaded in container:

```powershell
# Edit a Python file
vim backend/llm/llm_client.py

# Changes apply automatically (hot reload enabled)
```

### Edit Frontend Code

Changes are auto-reloaded in browser:

```powershell
# Edit a React component
vim frontend/src/pages/Dashboard.jsx

# Browser refreshes automatically
```

### View Output Files

Real leads are saved to:

```powershell
dir C:\Users\aman\Lie1\backend\leads_output\

# View a lead file
type C:\Users\aman\Lie1\backend\leads_output\leads_*.json
```

---

## Production Deployment

To deploy LeadBot to AWS, Google Cloud, or your own server:

```bash
# Push image to registry
docker tag leadbot-backend myregistry/leadbot-backend:latest
docker push myregistry/leadbot-backend:latest

# Deploy on server
docker-compose up -d
```

---

## Performance Notes

- **First start:** 5-10 minutes (downloads ~2GB Docker images + 4.7GB llama3)
- **Subsequent starts:** ~30 seconds
- **Lead generation job:** 30-60 seconds (depends on number of queries)
- **Ollama inference:** 5-15 seconds per lead (depends on model and prompt)

---

## What You Now Have

✅ **Crawl4AI Working** - No more subprocess issues  
✅ **Real Lead Generation** - Crawls websites, extracts data  
✅ **Local LLM** - Ollama scoring leads with llama3  
✅ **Full Agentic Loop** - Plan → Discover → Qualify → Enrich → Output  
✅ **Live Dashboard** - See results in real-time  
✅ **Easy Development** - Hot reload for frontend & backend  
✅ **Production Ready** - All containerized, portable, scalable  

---

## Next Steps

1. **Run:** `docker-compose up --build`
2. **Wait:** For containers to start (5-10 mins first time)
3. **Visit:** http://localhost:5174
4. **Run Job:** Submit a lead generation job
5. **See Results:** Real data on dashboard!

---

## Questions?

- **Backend logs:** `docker-compose logs backend`
- **Frontend logs:** `docker-compose logs frontend`  
- **All logs:** `docker-compose logs -f`

Good luck! 🚀
