@echo off
REM ═══════════════════════════════════════════════════════════════
REM  start.bat — Launch Backend + Frontend for DATA ANALYSIS FUL STACK
REM  Double-click this file to start both servers automatically.
REM ═══════════════════════════════════════════════════════════════

SET ROOT=%~dp0

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║      DATA ANALYSIS FUL STACK — Startup Script       ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
echo  [1/2] Starting FastAPI Backend on http://127.0.0.1:8000
echo  [2/2] Starting React Frontend  on http://localhost:3000
echo.

REM ── Start Backend in a new terminal window ──────────────
start "FastAPI Backend [:8000]" cmd /k "cd /d "%ROOT%" && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

REM ── Wait 2 seconds then start Frontend ──────────────────
timeout /t 2 /nobreak >nul

start "React Frontend [:3000]" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

echo.
echo  Both servers are starting...
echo.
echo  Backend  →  http://127.0.0.1:8000
echo  Docs     →  http://127.0.0.1:8000/docs
echo  Frontend →  http://localhost:3000
echo.
echo  Press any key to close this window (servers keep running).
pause >nul

