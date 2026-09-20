# LeadBot AI - Docker Quick Start Script
# Run this to start everything

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "LeadBot AI - Docker Startup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Navigate to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
if ($PSScriptRoot -ne $projectRoot) {
    cd $projectRoot
}

Write-Host "Project directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Stop any existing processes
Write-Host "Stopping local processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "✓ Local processes stopped" -ForegroundColor Green
Write-Host ""

# Build and start containers
Write-Host "Starting Docker containers..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes on first run (downloading images + model)" -ForegroundColor Cyan
Write-Host ""

docker-compose up --build

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "LeadBot AI is running!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard: http://localhost:5174" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Ollama: http://localhost:11434" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop" -ForegroundColor Yellow
