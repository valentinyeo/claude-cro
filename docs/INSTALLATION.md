# Installation Guide

## Prerequisites

- **Python 3.9+** — Required for utility scripts
- **Claude Code** — The CLI tool from Anthropic
- **pip** — Python package manager
- **Git** — For cloning the repository
- **Playwright** (optional) — For screenshot capture

## Plugin Install (Recommended)

Install directly as a Claude Code plugin:

```
/plugin install claude-cro@valentinyeo/claude-cro
```

This automatically discovers all skills and agents. No manual file copying needed.

## Quick Install (Manual)

One-line install for Linux and macOS:

```bash
git clone https://github.com/valentinyeo/claude-cro.git && cd claude-cro && ./install.sh
```

## Step-by-Step Install (Linux/macOS)

### 1. Clone the repository

```bash
git clone https://github.com/valentinyeo/claude-cro.git
cd claude-cro
```

### 2. Make the installer executable

```bash
chmod +x install.sh
```

### 3. Run the installer

```bash
./install.sh
```

The installer will:
- Create `~/.claude/skills/` and `~/.claude/agents/` directories
- Copy the main orchestrator to `~/.claude/skills/cro/`
- Copy all 12 sub-skills to `~/.claude/skills/cro-*/`
- Copy agent definitions to `~/.claude/agents/`
- Copy Python scripts to `~/.claude/skills/cro/scripts/`
- Install Python dependencies (`requests`, `beautifulsoup4`, `lxml`)
- Attempt to install Playwright's Chromium browser (optional)

### 4. Verify installation

Open Claude Code and type:

```
/cro
```

You should see the CRO skill recognized with its available commands.

## Windows Install

### 1. Clone the repository

```powershell
git clone https://github.com/valentinyeo/claude-cro.git
cd claude-cro
```

### 2. Run the PowerShell installer

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

This installs to `%USERPROFILE%\.claude\` with the same directory structure as Linux/macOS.

## Manual Install

If you prefer to install manually or the installer does not work for your setup:

### 1. Create directories

```bash
mkdir -p ~/.claude/skills/cro/scripts
mkdir -p ~/.claude/skills/cro/references
mkdir -p ~/.claude/agents
```

### 2. Copy files

```bash
# Main orchestrator + references + scripts
cp -r skills/cro/* ~/.claude/skills/cro/
chmod +x ~/.claude/skills/cro/scripts/*.py

# Sub-skills
for dir in skills/cro-*/; do
    skill=$(basename "$dir")
    mkdir -p ~/.claude/skills/$skill
    cp -r "$dir"* ~/.claude/skills/$skill/
done

# Agents
cp agents/*.md ~/.claude/agents/
```

### 3. Install Python packages

```bash
pip install requests beautifulsoup4 lxml
```

### 4. Install Playwright (optional)

```bash
pip install playwright
playwright install chromium
```

## Updating

To update to the latest version:

```bash
cd claude-cro
git pull origin main
./install.sh
```

The installer overwrites existing files, so this is safe to run repeatedly.

## Uninstalling

Run the uninstall script:

```bash
./uninstall.sh
```

This removes all CRO skills, agents, and scripts from `~/.claude/`. Python
packages are left installed (remove manually with `pip uninstall` if desired).

## Troubleshooting

### "Skills not appearing in Claude Code"

1. Verify the files were copied:
   ```bash
   ls ~/.claude/skills/cro/SKILL.md
   ls ~/.claude/skills/cro-*/SKILL.md
   ```
2. Restart Claude Code after installation.
3. Check that Claude Code looks for skills in `~/.claude/skills/`.

### "pip not found"

Install pip:
```bash
# Ubuntu/Debian
sudo apt install python3-pip

# macOS
python3 -m ensurepip --upgrade

# Windows
python -m ensurepip --upgrade
```

### "Playwright browser not installing"

Playwright is optional. If it fails to install:

```bash
# Try installing manually
pip install playwright
playwright install chromium

# On Linux, you may need dependencies
playwright install-deps chromium
```

Without Playwright, all CRO commands work normally except screenshot capture
in `capture_screenshot.py`.

### "Permission denied on install.sh"

```bash
chmod +x install.sh
./install.sh
```

Or run with bash directly:

```bash
bash install.sh
```

### "lxml installation fails"

On some systems, lxml requires system libraries:

```bash
# Ubuntu/Debian
sudo apt install libxml2-dev libxslt-dev python3-dev

# macOS
brew install libxml2

# Then retry
pip install lxml
```

If lxml refuses to install, the parse_cro.py script will fall back to
Python's built-in `html.parser` (slower but functional).
