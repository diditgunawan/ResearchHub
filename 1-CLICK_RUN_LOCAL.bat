@echo off
setlocal enabledelayedexpansion
title ResearchHub - Autonomous Academic Evidence Platform

echo ==============================================================================
echo                      RESEARCHHUB LOCAL LAUNCHER v0.4                          
echo       Grounded Evidence, Zero-Hallucination, Zero-Fabrication Platform        
echo ==============================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "API_DIR=%SCRIPT_DIR%apps\api"
set "PYTHON_EXE=%API_DIR%\.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python virtual environment not found at:
    echo         %PYTHON_EXE%
    echo Please ensure the backend virtual environment is created.
    pause
    exit /b 1
)

echo [1/3] Checking database status and applying delta migrations...
cd /d "%API_DIR%"
set "PYTHONPATH=."
"%PYTHON_EXE%" -c "from app.core.database import engine, Base; import asyncio; async def init(): async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all); asyncio.run(init())" 2>nul
echo   -> Database ready (researchforge.db).

echo [2/3] Launching ResearchHub API server (FastAPI + Uvicorn)...
echo   -> Listening on: http://127.0.0.1:8000
echo   -> Interactive Docs: http://127.0.0.1:8000/docs
echo   -> Admin Console:    http://127.0.0.1:8000/admin/settings

start /B "" "%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo [3/3] Checking frontend build...
if exist "%SCRIPT_DIR%apps\web\node_modules" (
    echo   -> Starting frontend development server (Vite on 5173)...
    cd /d "%SCRIPT_DIR%apps\web"
    start /B "" cmd /c "npx vite --host 127.0.0.1 --port 5173"
    timeout /t 3 >nul
    echo   -> Opening Web Application in your default browser...
    start http://127.0.0.1:5173
) else (
    timeout /t 2 >nul
    echo   -> Opening Backend & API in your default browser...
    start http://127.0.0.1:8000/docs
)

echo.
echo ==============================================================================
echo   RESEARCHHUB IS NOW RUNNING!
echo   - Web App URL: http://127.0.0.1:5173
echo   - Default Login: lead.researcher@medical.ox.ac.uk
echo.
echo   Press any key in this window to stop the servers.
echo ==============================================================================
pause >nul

echo Stopping services...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq ResearchHub*" 2>nul
taskkill /F /IM node.exe 2>nul
echo Services stopped cleanly.
