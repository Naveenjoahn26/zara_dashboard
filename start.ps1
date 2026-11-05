# ═══════════════════════════════════════════════════════════════
#  start.ps1 — PowerShell startup script
#  Run: Right-click → "Run with PowerShell"
#  Or:  powershell -ExecutionPolicy Bypass -File start.ps1
# ═══════════════════════════════════════════════════════════════

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontend = Join-Path $root "frontend"

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║      DATA ANALYSIS FUL STACK — Startup Script       ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  [1/2] Starting FastAPI Backend  →  http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  [2/2] Starting React Frontend   →  http://localhost:3000" -ForegroundColor Blue
Write-Host ""

# ── Backend ───────────────────────────────────────────────────
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$root'; Write-Host ' FastAPI Backend' -ForegroundColor Green; python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
)

# ── Wait then start Frontend ───────────────────────────────────
Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$frontend'; Write-Host ' React Frontend' -ForegroundColor Blue; npm run dev"
)

Write-Host "  ✅ Both servers launched in separate windows." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Backend  →  http://127.0.0.1:8000"       -ForegroundColor White
Write-Host "  API Docs →  http://127.0.0.1:8000/docs"  -ForegroundColor White
Write-Host "  Frontend →  http://localhost:3000"        -ForegroundColor White
Write-Host ""
Write-Host "  Press Enter to close this window..." -ForegroundColor Gray
Read-Host

