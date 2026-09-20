# LeadBot AI - Docker Stop Script

Write-Host "Stopping Docker containers..." -ForegroundColor Yellow
docker-compose down

Write-Host "✓ Docker containers stopped" -ForegroundColor Green
Write-Host ""
Write-Host "To remove volumes and data:" -ForegroundColor Cyan
Write-Host "  docker-compose down -v" -ForegroundColor Gray
