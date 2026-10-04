param(
  [string]$CandidateUrl = "http://127.0.0.1:8889"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Mnemosyne 0.1b identity smoke test" -ForegroundColor Cyan
Write-Host "Candidate : $CandidateUrl"
Write-Host ""

$version = Invoke-RestMethod "$CandidateUrl/version"
$identity = Invoke-RestMethod "$CandidateUrl/.well-known/project-v-mnemosyne"
$ext = Invoke-RestMethod "$CandidateUrl/ext/mnemosyne/status"

if (-not $version.api_version) { throw "Hindsight-compatible /version did not return api_version." }
if ($identity.product -ne "Project V // Mnemosyne") { throw "Well-known identity endpoint did not identify Mnemosyne." }
if ($ext.product -ne "Project V // Mnemosyne") { throw "Extension status endpoint did not identify Mnemosyne." }
if ($identity.mnemosyne_version -ne "0.2") { throw "Expected Mnemosyne 0.2 identity." }
if ($identity.compatibility.phoenix_contract -ne "0.2") { throw "Expected Phoenix contract 0.2." }
if ($identity.phoenix_metadata.schema_version -ne "1") { throw "Expected Phoenix metadata schema v1." }
if ($identity.phoenix_metadata.prefix -ne "pv_") { throw "Expected reserved pv_ metadata prefix." }
if ($identity.phoenix_metadata.authority -ne "context_only") { throw "Phoenix metadata authority invariant is missing." }
if ($identity.runtime.production_cutover_authorized -ne $false) { throw "0.1b must not authorize production cutover." }
if ($identity.safety.memory_is_context_not_authority -ne $true) { throw "Mnemosyne safety invariant is missing." }

Write-Host "PASS  /version compatibility       $($version.api_version)" -ForegroundColor Green
Write-Host "PASS  well-known identity          $($identity.product) $($identity.mnemosyne_version)" -ForegroundColor Green
Write-Host "PASS  Phoenix contract             $($identity.compatibility.phoenix_contract)" -ForegroundColor Green
Write-Host "PASS  metadata schema              $($identity.phoenix_metadata.prefix) v$($identity.phoenix_metadata.schema_version)" -ForegroundColor Green
Write-Host "PASS  extension identity           /ext/mnemosyne/status" -ForegroundColor Green
Write-Host "PASS  production cutover           blocked" -ForegroundColor Green
Write-Host "PASS  memory authority invariant   enforced" -ForegroundColor Green
