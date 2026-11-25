# Copies both skills into one or more agent skill directories (no plugin system required).
# Examples:
#   ./scripts/install-skills.ps1 -Agent claude
#   ./scripts/install-skills.ps1 -Agent claude,copilot,codex
#   ./scripts/install-skills.ps1 -Path C:\work\my-project\.github\skills
param(
    [ValidateSet("claude", "copilot", "codex", "all")]
    [string[]]$Agent = @(),
    [string[]]$Path = @()
)
$ErrorActionPreference = "Stop"

$Src = (Resolve-Path (Join-Path $PSScriptRoot "..\plugins\apartment-ranking\skills")).Path
$Skills = @("apartment-ranking", "architectural-document-ingestion")
$HomeDir = [Environment]::GetFolderPath("UserProfile")
$Known = [ordered]@{
    claude  = Join-Path $HomeDir ".claude\skills"
    copilot = Join-Path $HomeDir ".copilot\skills"
    codex   = Join-Path $HomeDir ".agents\skills"
}

if ($Agent -contains "all") { $Agent = @($Known.Keys) }
$Targets = @($Agent | ForEach-Object { $Known[$_] }) + $Path
if (-not $Targets) {
    throw "Specify -Agent claude|copilot|codex|all and/or -Path <skills-directory>."
}

$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
foreach ($Target in $Targets) {
    New-Item -ItemType Directory -Force -Path $Target | Out-Null
    # Backups go next to the skills directory, not inside it, so agents do not load them as duplicate skills.
    $BackupRoot = Join-Path (Split-Path $Target -Parent) "skills-backup\$Stamp"
    foreach ($Skill in $Skills) {
        $Dest = Join-Path $Target $Skill
        if (Test-Path $Dest) {
            New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
            Move-Item $Dest (Join-Path $BackupRoot $Skill)
            Write-Host "Existing $Dest backed up to $BackupRoot\$Skill (check its criteria-bank.md for local additions)."
        }
        Copy-Item -Recurse (Join-Path $Src $Skill) $Dest
    }
    Write-Host "Installed $($Skills -join ', ') into $Target"
}
Write-Host "Start a new agent session so the skills are discovered."
