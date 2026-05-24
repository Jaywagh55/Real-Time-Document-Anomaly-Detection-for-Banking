$ErrorActionPreference = "Stop"

Write-Host "Starting DocuShield backend and frontend..."

$backendPath = Join-Path $PSScriptRoot "backend"
$frontendPath = Join-Path $PSScriptRoot "frontend"

$pythonPath = Resolve-Path "$backendPath\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "Python virtual environment not found in backend\.venv. Please create it first." -ForegroundColor Yellow
    exit 1
}

$npmCmd = (Get-Command npm.cmd -ErrorAction Stop).Source

Start-Process -NoNewWindow -FilePath $pythonPath -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000' -WorkingDirectory $backendPath
Start-Process -NoNewWindow -FilePath $npmCmd -ArgumentList 'run', 'dev', '--', '--host', '0.0.0.0' -WorkingDirectory $frontendPath

Write-Host "Started backend at http://127.0.0.1:8000 and frontend at http://localhost:5173"
