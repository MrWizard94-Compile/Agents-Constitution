#requires -Version 7.0
<#
.SYNOPSIS
  Install or refresh generated local copies of the canonical agents-constitution skill.
.DESCRIPTION
  Fetches the canonical source from GitHub, validates provenance, then atomically
  replaces one or more local skill directories. Installed copies are generated
  mirrors, never editable source.
#>
[CmdletBinding()]
param(
    [string]$Repository = "MrWizard94-Compile/Agents-Constitution",
    [string]$Ref = "main",
    [string[]]$TargetSkillPaths = @((Join-Path $HOME ".codex\skills\agents-constitution")),
    [string]$PackRoot = "",
    [switch]$UseGitHubCli
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-Text([string]$Path) {
    if ($UseGitHubCli -or (Get-Command gh -ErrorAction SilentlyContinue)) {
        return (& gh api "repos/$Repository/contents/$Path?ref=$Ref" --jq .content) -replace "`n", "" |
            ForEach-Object { [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_)) }
    }
    $uri = "https://raw.githubusercontent.com/$Repository/$Ref/$Path"
    return (Invoke-WebRequest -UseBasicParsing -Uri $uri).Content
}

function Write-Atomic([string]$Path, [string]$Content) {
    $parent = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    $tmp = "$Path.__new__"
    [IO.File]::WriteAllText($tmp, $Content, [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}

$source = Get-Text "SOURCE.json" | ConvertFrom-Json
if ($source.canonical_repository -ne $Repository) {
    throw "Canonical repository mismatch: expected $Repository, source declares $($source.canonical_repository)"
}
$version = (Get-Text "VERSION").Trim()
$files = @(
    "SKILL.md",
    "VERSION",
    "SOURCE.json",
    "references/always-load.md",
    "references/pack-root.local.example",
    "scripts/resolve-pack.ps1"
)

foreach ($target in $TargetSkillPaths) {
    if (-not $target) { continue }
    foreach ($rel in $files) {
        Write-Atomic (Join-Path $target ($rel -replace "/", [IO.Path]::DirectorySeparatorChar)) (Get-Text $rel)
    }
    if ($PackRoot) {
        $pin = Join-Path $target "references\pack-root.local"
        Write-Atomic $pin ($PackRoot.TrimEnd("`r", "`n") + "`n")
    }
    $provenance = [ordered]@{
        generated = $true
        canonical_repository = $Repository
        source_ref = $Ref
        skill_version = $version
        installed_at_utc = [DateTime]::UtcNow.ToString("o")
    } | ConvertTo-Json -Depth 5
    Write-Atomic (Join-Path $target ".GENERATED-MIRROR.json") ($provenance + "`n")
    Write-Host "Synced agents-constitution $version -> $target"
}
