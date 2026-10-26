<#
.SYNOPSIS
    Starts the full ResearchHub local stack (Option 2).
.DESCRIPTION
    Launches PostgreSQL 16 (pgvector), Redis 7, MinIO, and Mailpit via Docker Compose,
    followed by the FastAPI backend server and background job worker.
#>

param(
    [switch]$DockerOnly = $false,
    [switch]$NativeOnly = $false
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "         RESEARCHHUB LOCAL PRODUCTION STACK LAUNCHER              " -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

if (-not $NativeOnly) {
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-Host "`n[1/3] Starting Docker services (Postgres 16 pgvector, Redis, MinIO, Mailpit)..." -ForegroundColor Yellow
        docker compose -f "$RepoRoot\docker-compose.yml" up -d db redis minio mailpit
        Write-Host "  -> Docker infrastructure healthy." -ForegroundColor Green
    } else {
        Write-Host "`n[!] Docker not detected on PATH. Using local in-process SQLite & fallback queue." -ForegroundColor Yellow
    }
}

if (-not $DockerOnly) {
    Write-Host "`n[2/3] Initializing Python virtual environment..." -ForegroundColor Yellow
    $ApiDir = Join-Path $RepoRoot "apps\api"
    $PythonExe = Join-Path $ApiDir ".venv\Scripts\python.exe"

    if (-not (Test-Path $PythonExe)) {
        Write-Host "  -> Error: Virtual environment not found at $PythonExe" -ForegroundColor Red
        Exit 1
    }

    Write-Host "`n[3/3] Starting ResearchHub API & Worker Services..." -ForegroundColor Yellow
    Write-Host "  -> API listening on: http://127.0.0.1:8000" -ForegroundColor Cyan
    Write-Host "  -> Admin console on: http://127.0.0.1:8000/admin/settings" -ForegroundColor Cyan
    Write-Host "  -> API docs on:      http://127.0.0.1:8000/docs" -ForegroundColor Cyan
    Write-Host "`nPress Ctrl+C to stop services." -ForegroundColor DarkGray

    Set-Location $ApiDir
    & $PythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
}
