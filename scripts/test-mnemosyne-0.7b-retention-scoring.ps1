$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Project V // Mnemosyne 0.7b - Deterministic Scoring Engine" -ForegroundColor Cyan
Write-Host ""

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
  Write-Host "FAIL  uv was not found" -ForegroundColor Red
  exit 1
}

$argsList = @(
  "run",
  "--package", "hindsight-api-slim",
  "--extra", "test",
  "pytest",
  "hindsight-api-slim/tests/test_retention_scoring.py",
  "hindsight-api-slim/tests/test_phoenix_metadata.py",
  "-q",
  "-n", "0"
)

if ($uvOnPath) {
  & uv @argsList
} else {
  & py -m uv @argsList
}

if ($LASTEXITCODE -ne 0) {
  Write-Host ""
  Write-Host "0.7b GATE: FAIL" -ForegroundColor Red
  exit $LASTEXITCODE
}

Write-Host ""
Write-Host "0.7b GATE: PASS" -ForegroundColor Green
