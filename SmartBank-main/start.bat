@echo off
title SmartBank AI Platform
echo ============================================
echo   SmartBank - Agentic AI Banking Platform
echo   UiPath AgentHack + UBL FinTech Hackathon
echo ============================================
echo.
echo Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1
echo Installing Node dependencies...
cd ui
call npm install >nul 2>&1
cd ..
echo.
echo Starting SmartBank API Server and React Frontend...
echo.
echo   React Dev  : http://localhost:5173
echo   API        : http://localhost:8000/api
echo   Health     : http://localhost:8000/api/health
echo.
echo Press Ctrl+C to stop both servers
echo ============================================
echo.

start "SmartBank API" node server.js
start "SmartBank UI" cmd /c "cd /d ui && npm run dev"

echo Both servers started. Opening browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173
echo.
echo Close this window to stop both servers.
pause
taskkill /fi "WINDOWTITLE eq SmartBank API" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq SmartBank UI" /f >nul 2>&1
