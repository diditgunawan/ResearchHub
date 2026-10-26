<#
.SYNOPSIS
    Stops the ResearchHub local stack.
#>

$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Stopping ResearchHub Docker services..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker compose -f "$RepoRoot\docker-compose.yml" stop
    Write-Host "Docker services stopped." -ForegroundColor Green
}
