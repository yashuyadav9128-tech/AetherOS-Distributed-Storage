# AetherStore Distributed Storage Demo PowerShell Launcher
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$ScriptDir\demo.py" @argspython "$ScriptDir\demo.py" @args
if ($args.Count -gt 0) {
    python "$ScriptDir\demo.py" @args
    exit $LASTEXITCODE
}

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "              AETHERSTORE DISTRIBUTED OBJECT STORAGE ENGINE                   " -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " [1] Run Full 12-Step Automated Demo (Default)"
Write-Host " [2] Run Demo and Keep Cluster Alive (Inspect Web Dashboard at :8000)"
Write-Host " [3] Run Automated Unit Tests"
Write-Host ""
$choice = Read-Host "Select an option [1-3] (Press Enter for 1)"

if ($choice -eq "2") {
    Write-Host "Starting demo with Web Dashboard keep-alive..." -ForegroundColor Yellow
    python "$ScriptDir\demo.py" --keep-alive
} elseif ($choice -eq "3") {
    Write-Host "Running automated test suite..." -ForegroundColor Cyan
    python -m unittest "$ScriptDir\tests\test_cluster.py"
} else {
    Write-Host "Starting standard 12-step demo..." -ForegroundColor Green
    python "$ScriptDir\demo.py"
}
