#requires -Version 5.1
<#
.SYNOPSIS
  Resolve AGENTS Constitution pack root for the agents-constitution skill.
.DESCRIPTION
  Discovery order matches SKILL.md Step 0.
  Prints the absolute pack root path to stdout on success; exit 0.
  Exit 1 if not found. Optional -SkillDir for pack-root.local lookup.
  -RequestedPackRoot validates a human-specified root without falling back.
  This locates binding pack law. It does not locate skill source; skill source is
  https://github.com/MrWizard94-Compile/Agents-Constitution.
#>
[CmdletBinding()]
param(
    [string]$SkillDir = "",
    [string]$StartPath = "",
    [Alias("PackRoot")]
    [string]$RequestedPackRoot = ""
)

$ErrorActionPreference = "Stop"

function Test-PackRoot([string]$path) {
    if (-not $path) { return $false }
    if (-not (Test-Path -LiteralPath $path -PathType Container)) { return $false }
    $need = @("VERSION", "AGENTS.md", "SOP.md", "tools")
    foreach ($n in $need) {
        $p = Join-Path $path $n
        if (-not (Test-Path -LiteralPath $p)) { return $false }
    }
    $verify = Join-Path $path "tools\verify-pack.ps1"
    if (-not (Test-Path -LiteralPath $verify)) { return $false }
    $agents = Get-Content -LiteralPath (Join-Path $path "AGENTS.md") -Raw -ErrorAction SilentlyContinue
    if (-not $agents -or $agents -notmatch "CONST-GATE-001") { return $false }
    return $true
}

function Assert-ExplicitPackRoot([string]$path, [string]$source) {
    if (Test-PackRoot $path) { Emit $path }
    $missing = New-Object System.Collections.Generic.List[string]
    if (-not (Test-Path -LiteralPath $path -PathType Container)) {
        [void]$missing.Add("directory")
    } else {
        foreach ($relative in @("VERSION", "AGENTS.md", "SOP.md", "tools\verify-pack.ps1")) {
            if (-not (Test-Path -LiteralPath (Join-Path $path $relative) -PathType Leaf)) {
                [void]$missing.Add($relative)
            }
        }
        $agents = Join-Path $path "AGENTS.md"
        if ((Test-Path -LiteralPath $agents -PathType Leaf) -and
            -not ((Get-Content -LiteralPath $agents -Raw) -match "CONST-GATE-001")) {
            [void]$missing.Add("CONST-GATE-001 in AGENTS.md")
        }
    }
    throw "$source is not a binding PACK_ROOT: '$path' (missing: $($missing -join ', ')). A canonical skill-source checkout is not automatically a law pack. Supply a root containing VERSION, AGENTS.md with CONST-GATE-001, SOP.md, and tools/verify-pack.ps1."
}

function Emit([string]$path) {
    $resolved = (Resolve-Path -LiteralPath $path).Path
    Write-Output $resolved
    exit 0
}

if ($RequestedPackRoot) {
    Assert-ExplicitPackRoot $RequestedPackRoot "RequestedPackRoot"
}

foreach ($envName in @("AGENTS_CONSTITUTION_ROOT", "WPAI_CONSTITUTION")) {
    $v = [Environment]::GetEnvironmentVariable($envName)
    if ($v) { Assert-ExplicitPackRoot $v $envName }
}

if (-not $SkillDir) {
    $SkillDir = Split-Path -Parent $PSScriptRoot
}
$pin = Join-Path $SkillDir "references\pack-root.local"
if (Test-Path -LiteralPath $pin) {
    $line = (Get-Content -LiteralPath $pin -TotalCount 1).Trim()
    if ($line -and -not $line.StartsWith("#") -and (Test-PackRoot $line)) { Emit $line }
}

$starts = New-Object System.Collections.Generic.List[string]
if ($StartPath) { [void]$starts.Add($StartPath) }
if ($PWD -and $PWD.Path) { [void]$starts.Add($PWD.Path) }
try {
    if ($PSScriptRoot) {
        [void]$starts.Add($PSScriptRoot)
        [void]$starts.Add((Split-Path -Parent $PSScriptRoot))
        [void]$starts.Add((Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
    }
} catch {}

$seen = New-Object "System.Collections.Generic.HashSet[string]"

foreach ($start in $starts) {
    if (-not $start -or -not (Test-Path -LiteralPath $start)) { continue }
    $cur = (Resolve-Path -LiteralPath $start).Path
    while ($cur) {
        if ($seen.Add($cur)) {
            if (Test-PackRoot $cur) { Emit $cur }
            $parent = Split-Path -Parent $cur
            if ($parent) {
                try {
                    Get-ChildItem -LiteralPath $parent -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                        if (Test-PackRoot $_.FullName) { Emit $_.FullName }
                    }
                } catch {}
            }
        }
        $next = Split-Path -Parent $cur
        if (-not $next -or $next -eq $cur) { break }
        $cur = $next
    }
}

Write-Error "AGENTS Constitution pack root not found. Set AGENTS_CONSTITUTION_ROOT or create references/pack-root.local. Skill source remains https://github.com/MrWizard94-Compile/Agents-Constitution"
exit 1
