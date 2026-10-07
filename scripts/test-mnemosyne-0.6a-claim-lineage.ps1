$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Project V // Mnemosyne 0.6a - Claim Lineage + Contradiction Schema" -ForegroundColor Cyan
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
  Write-Host "Install it with: py -m pip install --user uv" -ForegroundColor Yellow
  exit 1
}

$argsList = @(
  "run",
  "--package", "hindsight-api-slim",
  "--extra", "test",
  "pytest",
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
  Write-Host "0.6a GATE: FAIL" -ForegroundColor Red
  exit $LASTEXITCODE
}

Write-Host ""
Write-Host "0.6a GATE: PASS" -ForegroundColor Green
