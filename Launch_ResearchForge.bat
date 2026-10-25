@echo off
title ResearchForge Launcher
echo ========================================================
echo          RESEARCHFORGE SCHOLARLY STUDIO
echo ========================================================
echo.
echo Starting ResearchForge Core Services...
echo.

set "PROJ_DIR=%~dp0"
cd /d "%PROJ_DIR%"

if exist "ResearchForge.exe" (
    start "" "%PROJ_DIR%ResearchForge.exe" --open
) else (
    start "ResearchForge API" cmd /c "cd /d apps\api && set PYTHONPATH=. && .venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000"
    timeout /t 2 /nobreak >nul
    start "ResearchForge Web" cmd /c "cd /d apps\web && npx vite preview --port 5173 --host 0.0.0.0"
    timeout /t 2 /nobreak >nul
    start http://localhost:5173
)

echo Services launched!
echo Access the application at: http://localhost:5173
echo.
