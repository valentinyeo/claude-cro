#
# install.ps1 — Install Claude CRO skill package (Windows)
#
# Copies skill definitions, agents, scripts, and reference files to
# $env:USERPROFILE\.claude\ and installs Python dependencies.
#
# Usage:
#   .\install.ps1
#   powershell -ExecutionPolicy Bypass -File install.ps1
#

$ErrorActionPreference = "Stop"

# Resolve source directory (where this script lives)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Target directories
$ClaudeDir = Join-Path $env:USERPROFILE ".claude"
$SkillsDir = Join-Path $ClaudeDir "skills"
$AgentsDir = Join-Path $ClaudeDir "agents"

Write-Host "========================================"
Write-Host "  Claude CRO - Installer (Windows)"
Write-Host "========================================"
Write-Host ""
Write-Host "Source:  $ScriptDir"
Write-Host "Target:  $ClaudeDir"
Write-Host ""

# -- Create target directories -----------------------------------------------

Write-Host "Creating directories..."
$dirs = @(
    (Join-Path $SkillsDir "cro\scripts"),
    (Join-Path $SkillsDir "cro\references"),
    $AgentsDir
)
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# -- Copy main orchestrator --------------------------------------------------

Write-Host "Installing main orchestrator..."
Copy-Item (Join-Path $ScriptDir "cro\SKILL.md") (Join-Path $SkillsDir "cro\SKILL.md") -Force

# -- Copy reference files ----------------------------------------------------

Write-Host "Installing reference files..."
$refsSource = Join-Path $ScriptDir "cro\references"
$refsTarget = Join-Path $SkillsDir "cro\references"
if (Test-Path $refsSource) {
    Get-ChildItem -Path $refsSource -Filter "*.md" | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $refsTarget $_.Name) -Force
    }
}

# -- Copy sub-skills ---------------------------------------------------------

Write-Host "Installing sub-skills..."
$SkillCount = 0
$skillsSource = Join-Path $ScriptDir "skills"
if (Test-Path $skillsSource) {
    Get-ChildItem -Path $skillsSource -Directory | ForEach-Object {
        $targetSkillDir = Join-Path $SkillsDir $_.Name
        if (-not (Test-Path $targetSkillDir)) {
            New-Item -ItemType Directory -Path $targetSkillDir -Force | Out-Null
        }
        Copy-Item -Path (Join-Path $_.FullName "*") -Destination $targetSkillDir -Recurse -Force
        $SkillCount++
    }
}

# -- Copy agents --------------------------------------------------------------

Write-Host "Installing agents..."
$AgentCount = 0
$agentsSource = Join-Path $ScriptDir "agents"
if (Test-Path $agentsSource) {
    Get-ChildItem -Path $agentsSource -Filter "*.md" | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $AgentsDir $_.Name) -Force
        $AgentCount++
    }
}

# -- Copy scripts --------------------------------------------------------------

Write-Host "Installing Python scripts..."
$ScriptCount = 0
$scriptsSource = Join-Path $ScriptDir "scripts"
$scriptsTarget = Join-Path $SkillsDir "cro\scripts"
if (Test-Path $scriptsSource) {
    Get-ChildItem -Path $scriptsSource -Filter "*.py" | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $scriptsTarget $_.Name) -Force
        $ScriptCount++
    }
}

# -- Install Python dependencies -----------------------------------------------

Write-Host ""
Write-Host "Installing Python dependencies..."
$requirementsFile = Join-Path $ScriptDir "requirements.txt"

$pipCmd = $null
if (Get-Command "pip3" -ErrorAction SilentlyContinue) {
    $pipCmd = "pip3"
} elseif (Get-Command "pip" -ErrorAction SilentlyContinue) {
    $pipCmd = "pip"
} else {
    Write-Host "  Warning: pip not found. Install Python dependencies manually:"
    Write-Host "    pip install -r $requirementsFile"
}

if ($pipCmd) {
    try {
        & $pipCmd install -r $requirementsFile 2>$null
        Write-Host "  Python dependencies installed."
    } catch {
        Write-Host "  Warning: Some Python dependencies failed to install."
        Write-Host "  Install manually: $pipCmd install -r $requirementsFile"
    }
}

# -- Install Playwright browsers (optional) ------------------------------------

Write-Host ""
Write-Host "Installing Playwright browser (optional)..."
try {
    if (Get-Command "playwright" -ErrorAction SilentlyContinue) {
        & playwright install chromium 2>$null
        Write-Host "  Chromium browser installed for Playwright."
    } else {
        & python -m playwright install chromium 2>$null
        Write-Host "  Chromium browser installed for Playwright."
    }
} catch {
    Write-Host "  Playwright not found. Screenshot capture is optional."
    Write-Host "  To enable later: pip install playwright; playwright install chromium"
}

# -- Summary -------------------------------------------------------------------

Write-Host ""
Write-Host "========================================"
Write-Host "  Installation Complete"
Write-Host "========================================"
Write-Host ""
Write-Host "  Orchestrator:   cro\SKILL.md"
Write-Host "  Sub-skills:     $SkillCount installed"
Write-Host "  Agents:         $AgentCount installed"
Write-Host "  Scripts:        $ScriptCount installed"
Write-Host ""
Write-Host "  Installed sub-skills:"
Get-ChildItem -Path $SkillsDir -Directory -Filter "cro-*" | ForEach-Object {
    Write-Host "    - $($_.Name)"
}
Write-Host ""
Write-Host "  Installed agents:"
Get-ChildItem -Path $AgentsDir -Filter "cro-*.md" | ForEach-Object {
    Write-Host "    - $($_.BaseName)"
}
Write-Host ""
Write-Host "  Usage: Open Claude Code and type /cro audit <url>"
Write-Host ""
