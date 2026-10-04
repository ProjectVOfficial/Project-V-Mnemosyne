param(
  [string]$StockUrl = "http://127.0.0.1:8888",
  [string]$CandidateUrl = "http://127.0.0.1:8889",
  [switch]$SkipReflect,
  [switch]$KeepBank
)

$ErrorActionPreference = "Stop"

$argsList = @(
  "scripts\phoenix_compat_smoke.py",
  "--stock-url", $StockUrl,
  "--candidate-url", $CandidateUrl
)

if ($SkipReflect) { $argsList += "--skip-reflect" }
if ($KeepBank) { $argsList += "--keep-bank" }

Write-Host ""
Write-Host "Phoenix <-> Mnemosyne 0.1 compatibility test" -ForegroundColor Cyan
Write-Host "Stock     : $StockUrl"
Write-Host "Candidate : $CandidateUrl"
Write-Host ""

py @argsList
exit $LASTEXITCODE
