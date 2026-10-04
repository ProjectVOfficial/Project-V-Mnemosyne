param()

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
  Write-Host "Install it with: py -m pip install --user uv" -ForegroundColor Yellow
  exit 1
}

Write-Host ""
Write-Host "Mnemosyne 0.1c Phoenix metadata unit test" -ForegroundColor Cyan
Write-Host ""

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

exit $LASTEXITCODE
