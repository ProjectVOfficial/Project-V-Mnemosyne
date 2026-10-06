param(
  [string]$CandidateUrl = "http://127.0.0.1:8889",
  [string]$BankId = "phoenix-mnemosyne-02b-test",
  [string]$Token = "MNEMOSYNE-0.2B-PHOENIX-WRITE-TEST"
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
  exit 1
}

$argsList = @(
  "run",
  "--package", "hindsight-api-slim",
  "python",
  "scripts/test_phoenix_live_metadata.py",
  "--candidate-url", $CandidateUrl,
  "--bank-id", $BankId,
  "--token", $Token
)

if ($uvOnPath) {
  & uv @argsList
} else {
  & py -m uv @argsList
}

exit $LASTEXITCODE
