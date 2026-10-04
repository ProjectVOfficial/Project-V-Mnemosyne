param(
  [int]$Port = 8889,
  [string]$Model = "qwen3:14b",
  [string]$OllamaUrl = "http://127.0.0.1:11434",
  [string]$DatabaseName = "project-v-mnemosyne-01"
)

$ErrorActionPreference = "Stop"

$uvOnPath = Get-Command uv -ErrorAction SilentlyContinue
$usePythonModule = $false

if (-not $uvOnPath) {
  try {
    py -m uv --version *> $null
    if ($LASTEXITCODE -eq 0) { $usePythonModule = $true }
  } catch {
    $usePythonModule = $false
  }
}

if (-not $uvOnPath -and -not $usePythonModule) {
  Write-Host "uv was not found." -ForegroundColor Red
  Write-Host "Install it with:"
  Write-Host "  py -m pip install --user uv" -ForegroundColor Yellow
  Write-Host "Then run this launcher again."
  exit 1
}

$env:HINDSIGHT_API_DATABASE_URL = "pg0://$DatabaseName"
$env:HINDSIGHT_API_LLM_PROVIDER = "ollama"
$env:HINDSIGHT_API_LLM_MODEL = $Model
$env:HINDSIGHT_API_LLM_BASE_URL = $OllamaUrl
$env:HINDSIGHT_API_HOST = "127.0.0.1"
$env:HINDSIGHT_API_PORT = "$Port"

Write-Host ""
Write-Host "Project V // Mnemosyne 0.1 candidate" -ForegroundColor Cyan
Write-Host "Endpoint : http://127.0.0.1:$Port"
Write-Host "Database : $($env:HINDSIGHT_API_DATABASE_URL)"
Write-Host "LLM      : ollama / $Model"
Write-Host "Ollama   : $OllamaUrl"
Write-Host ""
Write-Host "This is the isolated candidate runtime. Production Phoenix should remain on stock Hindsight." -ForegroundColor Yellow
Write-Host ""

if ($uvOnPath) {
  & uv run --package hindsight-api hindsight-api --host 127.0.0.1 --port $Port
} else {
  & py -m uv run --package hindsight-api hindsight-api --host 127.0.0.1 --port $Port
}

exit $LASTEXITCODE
