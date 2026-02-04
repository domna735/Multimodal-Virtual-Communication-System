param(
    [switch]$ByBackend
)

$ErrorActionPreference = 'Stop'

Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$tool = Join-Path $PSScriptRoot 'tools\diagnostics\summarize_session_latency.py'

if (-not (Test-Path $python)) {
    throw "Python venv not found: $python"
}

if ($ByBackend) {
    & $python $tool --by-backend
} else {
    & $python $tool
}
