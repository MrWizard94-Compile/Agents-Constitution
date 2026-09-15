#requires -Version 7.0
<#
.SYNOPSIS
  Install or refresh generated local copies of the canonical agents-constitution skill.
.DESCRIPTION
  Resolves the requested branch/tag exactly once, then fetches every source file
  from that immutable commit. This prevents a moving main branch from producing
  a mixed-revision local skill. Installed copies are generated mirrors, never
  editable source. When -TargetSkillPaths is omitted, paths come from SOURCE.json
  default_mirror_paths (Grok and Codex). After writing canonical files, leftover
  files from older vendored copies are removed.
#>
[CmdletBinding()]
param(
    [string]$Repository = "MrWizard94-Compile/Agents-Constitution",
    [string]$Ref = "main",
    [string[]]$TargetSkillPaths = @(),
    [string]$PackRoot = "",
    [switch]$UseGitHubCli
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Expand-HomePath([string]$PathText) {
    if ($PathText -match '^[~][\\/]?(.*)$') {
        if ($Matches[1]) { return (Join-Path $HOME $Matches[1]) }
        return $HOME
    }
    return $PathText
}

function Resolve-Commit([string]$RequestedRef) {
    if ($UseGitHubCli -or (Get-Command gh -ErrorAction SilentlyContinue)) {
        $sha = (& gh api "repos/$Repository/commits/$RequestedRef" --jq .sha).Trim()
    } else {
        $headers = @{ "User-Agent" = "agents-constitution-sync"; "Accept" = "application/vnd.github+json" }
        $token = [Environment]::GetEnvironmentVariable("GITHUB_TOKEN")
        if (-not $token) { $token = [Environment]::GetEnvironmentVariable("GH_TOKEN") }
        if ($token) { $headers["Authorization"] = "Bearer $token" }
        $payload = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repository/commits/$RequestedRef" -Headers $headers
        $sha = [string]$payload.sha
    }
    if ($sha -notmatch '^[0-9a-fA-F]{40}$') {
        throw "Could not resolve $Repository@$RequestedRef to an immutable commit."
    }
    return $sha.ToLowerInvariant()
}

function Get-Text([string]$Commit, [string]$Path) {
    if ($UseGitHubCli -or (Get-Command gh -ErrorAction SilentlyContinue)) {
        $encoded = (& gh api "repos/$Repository/contents/$Path?ref=$Commit" --jq .content) -replace "`n", ""
        return [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($encoded))
    }
    $uri = "https://raw.githubusercontent.com/$Repository/$Commit/$Path"
    return (Invoke-WebRequest -UseBasicParsing -Uri $uri).Content
}

function Write-Atomic([string]$Path, [string]$Content) {
    $parent = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    $tmp = "$Path.__new__"
    [IO.File]::WriteAllText($tmp, $Content, [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}

function Test-SkillDirectory([string]$Target) {
    $sourcePath = Join-Path $Target "SOURCE.json"
    if (Test-Path -LiteralPath $sourcePath -PathType Leaf) {
        try {
            $parsed = Get-Content -LiteralPath $sourcePath -Raw | ConvertFrom-Json
            if ($parsed.name -eq "agents-constitution") { return $true }
        } catch {}
    }
    $skillPath = Join-Path $Target "SKILL.md"
    if (Test-Path -LiteralPath $skillPath -PathType Leaf) {
        $head = Get-Content -LiteralPath $skillPath -TotalCount 20 -ErrorAction SilentlyContinue
        if ($head -and ($head -join "`n") -match "name:\s*agents-constitution") { return $true }
    }
    return $false
}

function Remove-StaleMirrorFiles([string]$Target, [string[]]$KeepRel) {
    if (-not (Test-SkillDirectory $Target)) { return }
    $keep = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($rel in $KeepRel) { [void]$keep.Add(($rel -replace "/", [IO.Path]::DirectorySeparatorChar)) }
    Get-ChildItem -LiteralPath $Target -Recurse -Force | Sort-Object FullName -Descending | ForEach-Object {
        if ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) { return }
        $rel = $_.FullName.Substring($Target.Length).TrimStart('\','/')
        if (-not $_.PSIsContainer) {
            if (-not $keep.Contains($rel)) { Remove-Item -LiteralPath $_.FullName -Force }
        } elseif (-not (Get-ChildItem -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue)) {
            Remove-Item -LiteralPath $_.FullName -Force
        }
    }
}

$commit = Resolve-Commit $Ref
$source = Get-Text $commit "SOURCE.json" | ConvertFrom-Json
if ($source.canonical_repository -ne $Repository) {
    throw "Canonical repository mismatch: expected $Repository, source declares $($source.canonical_repository)"
}
$version = (Get-Text $commit "VERSION").Trim()

$effectiveTargets = @($TargetSkillPaths | Where-Object { $_ })
if ($effectiveTargets.Count -eq 0 -and $source.PSObject.Properties.Name -contains "default_mirror_paths") {
    $effectiveTargets = @($source.default_mirror_paths)
}
if ($effectiveTargets.Count -eq 0) {
    throw "No sync targets given and SOURCE.json has no default_mirror_paths."
}

$files = @(
    "SKILL.md",
    "VERSION",
    "SOURCE.json",
    "references/always-load.md",
    "references/pack-root.local.example",
    "references/.gitignore",
    "scripts/resolve-pack.ps1"
)
$keepRel = $files + @(".GENERATED-MIRROR.json", "references/pack-root.local")

$payload = @{}
foreach ($rel in $files) {
    $payload[$rel] = Get-Text $commit $rel
}

$canonicalUrl = "https://github.com/$Repository"
if ($source.PSObject.Properties.Name -contains "canonical_url" -and $source.canonical_url) {
    $canonicalUrl = [string]$source.canonical_url
}

foreach ($target in $effectiveTargets) {
    if (-not $target) { continue }
    $resolvedTarget = Expand-HomePath $target
    foreach ($rel in $files) {
        Write-Atomic (Join-Path $resolvedTarget ($rel -replace "/", [IO.Path]::DirectorySeparatorChar)) $payload[$rel]
    }
    if ($PackRoot) {
        $pin = Join-Path $resolvedTarget "references\pack-root.local"
        Write-Atomic $pin ($PackRoot.TrimEnd("`r", "`n") + "`n")
    }
    Remove-StaleMirrorFiles $resolvedTarget $keepRel
    $provenance = [ordered]@{
        generated = $true
        canonical_repository = $Repository
        canonical_url = $canonicalUrl
        requested_ref = $Ref
        source_commit = $commit
        skill_version = $version
        installed_at_utc = [DateTime]::UtcNow.ToString("o")
    } | ConvertTo-Json -Depth 5
    Write-Atomic (Join-Path $resolvedTarget ".GENERATED-MIRROR.json") ($provenance + "`n")
    Write-Host "Synced agents-constitution $version ($($commit.Substring(0,12))) -> $resolvedTarget"
}
