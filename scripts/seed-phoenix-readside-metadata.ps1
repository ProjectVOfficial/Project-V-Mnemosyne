param(
  [string]$CandidateUrl = "http://127.0.0.1:8889",
  [string]$BankId = "phoenix-mnemosyne-02c-read-test",
  [string]$Token = "MNEMOSYNE-0.2C-READ-SIDE-TEST",
  [switch]$Cleanup
)

$ErrorActionPreference = "Stop"
$scriptPath = Join-Path $PSScriptRoot "seed_phoenix_readside_metadata.py"

$argsList = @(
  $scriptPath,
  "--candidate-url", $CandidateUrl,
  "--bank-id", $BankId,
  "--token", $Token
)

if ($Cleanup) { $argsList += "--cleanup" }

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
  & py @argsList
  exit $LASTEXITCODE
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
  & python @argsList
  exit $LASTEXITCODE
}

Write-Host "Python was not found." -ForegroundColor Red
exit 1
