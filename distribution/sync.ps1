#requires -Version 5.1
<#
.SYNOPSIS
  Sync verified WPAI Constitution mirrors from one accepted GitHub commit.
.DESCRIPTION
  Thin PowerShell adapter for sync.py. It does not implement a second set of
  manifest, pruning, or trust rules.
#>
[CmdletBinding()]
param(
    [string]$Ref = "main",
    [string[]]$TargetSkillPaths = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$python = (Get-Command python -ErrorAction Stop).Source
$argsList = @((Join-Path $PSScriptRoot "sync.py"), "--ref", $Ref) + $TargetSkillPaths
& $python @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
