$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    throw "Codex CLI was not found in PATH. Install/enable Codex CLI, then rerun this script."
}

Write-Host "Registering Apartment Ranking marketplace from: $RepoRoot"
& codex plugin marketplace add "$RepoRoot"
if ($LASTEXITCODE -ne 0) {
    throw "codex plugin marketplace add failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "Marketplace registered."
Write-Host "Restart ChatGPT desktop / Codex, open the Plugin Directory, select 'Apartment Ranking Tools', and install 'Apartment Ranking'."
