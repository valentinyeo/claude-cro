#!/usr/bin/env bash
#
# install.sh — Install Claude CRO skill package
#
# Copies skill definitions, agents, scripts, and reference files to
# ~/.claude/ and installs Python dependencies.
#
# Usage:
#   ./install.sh
#   bash install.sh

set -euo pipefail

# Resolve the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Target directories
CLAUDE_DIR="${HOME}/.claude"
SKILLS_DIR="${CLAUDE_DIR}/skills"
AGENTS_DIR="${CLAUDE_DIR}/agents"

echo "========================================"
echo "  Claude CRO — Installer"
echo "========================================"
echo ""
echo "Source:  ${SCRIPT_DIR}"
echo "Target:  ${CLAUDE_DIR}"
echo ""

# ── Create target directories ──────────────────────────────────────────

echo "Creating directories..."
mkdir -p "${SKILLS_DIR}/cro/scripts"
mkdir -p "${SKILLS_DIR}/cro/references"
mkdir -p "${AGENTS_DIR}"

# ── Copy main orchestrator ─────────────────────────────────────────────

echo "Installing main orchestrator..."
cp "${SCRIPT_DIR}/cro/SKILL.md" "${SKILLS_DIR}/cro/SKILL.md"

# ── Copy reference files ──────────────────────────────────────────────

echo "Installing reference files..."
if [ -d "${SCRIPT_DIR}/cro/references" ]; then
    cp "${SCRIPT_DIR}/cro/references/"*.md "${SKILLS_DIR}/cro/references/" 2>/dev/null || true
fi

# ── Copy sub-skills ────────────────────────────────────────────────────

echo "Installing sub-skills..."
SKILL_COUNT=0
for skill_dir in "${SCRIPT_DIR}/skills/"*/; do
    if [ -d "${skill_dir}" ]; then
        skill_name="$(basename "${skill_dir}")"
        mkdir -p "${SKILLS_DIR}/${skill_name}"
        cp -r "${skill_dir}"* "${SKILLS_DIR}/${skill_name}/" 2>/dev/null || true
        SKILL_COUNT=$((SKILL_COUNT + 1))
    fi
done

# ── Copy agents ────────────────────────────────────────────────────────

echo "Installing agents..."
AGENT_COUNT=0
for agent_file in "${SCRIPT_DIR}/agents/"*.md; do
    if [ -f "${agent_file}" ]; then
        cp "${agent_file}" "${AGENTS_DIR}/"
        AGENT_COUNT=$((AGENT_COUNT + 1))
    fi
done

# ── Copy scripts ───────────────────────────────────────────────────────

echo "Installing Python scripts..."
SCRIPT_COUNT=0
for script_file in "${SCRIPT_DIR}/scripts/"*.py; do
    if [ -f "${script_file}" ]; then
        cp "${script_file}" "${SKILLS_DIR}/cro/scripts/"
        chmod +x "${SKILLS_DIR}/cro/scripts/$(basename "${script_file}")"
        SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
    fi
done

# ── Install Python dependencies ────────────────────────────────────────

echo ""
echo "Installing Python dependencies..."
if command -v pip3 &>/dev/null; then
    PIP_CMD="pip3"
elif command -v pip &>/dev/null; then
    PIP_CMD="pip"
else
    echo "  Warning: pip not found. Install Python dependencies manually:"
    echo "    pip install -r ${SCRIPT_DIR}/requirements.txt"
    PIP_CMD=""
fi

if [ -n "${PIP_CMD}" ]; then
    if ${PIP_CMD} install -r "${SCRIPT_DIR}/requirements.txt" 2>/dev/null; then
        echo "  Python dependencies installed."
    else
        echo "  Warning: Some Python dependencies failed to install."
        echo "  You can install them manually: ${PIP_CMD} install -r ${SCRIPT_DIR}/requirements.txt"
    fi
fi

# ── Install Playwright browsers (optional) ─────────────────────────────

echo ""
echo "Installing Playwright browser (optional)..."
if command -v playwright &>/dev/null; then
    if playwright install chromium 2>/dev/null; then
        echo "  Chromium browser installed for Playwright."
    else
        echo "  Warning: Failed to install Chromium for Playwright."
        echo "  Screenshot capture will not work until you run:"
        echo "    playwright install chromium"
    fi
elif python3 -m playwright install chromium 2>/dev/null; then
    echo "  Chromium browser installed for Playwright."
else
    echo "  Playwright not found. Screenshot capture is optional."
    echo "  To enable it later, run:"
    echo "    pip install playwright && playwright install chromium"
fi

# ── Summary ────────────────────────────────────────────────────────────

echo ""
echo "========================================"
echo "  Installation Complete"
echo "========================================"
echo ""
echo "  Orchestrator:   cro/SKILL.md"
echo "  Sub-skills:     ${SKILL_COUNT} installed"
echo "  Agents:         ${AGENT_COUNT} installed"
echo "  Scripts:        ${SCRIPT_COUNT} installed"
echo ""
echo "  Installed sub-skills:"
for skill_dir in "${SKILLS_DIR}/cro-"*/; do
    if [ -d "${skill_dir}" ]; then
        echo "    - $(basename "${skill_dir}")"
    fi
done
echo ""
echo "  Installed agents:"
for agent_file in "${AGENTS_DIR}/cro-"*.md; do
    if [ -f "${agent_file}" ]; then
        echo "    - $(basename "${agent_file}" .md)"
    fi
done
echo ""
echo "  Usage: Open Claude Code and type /cro audit <url>"
echo ""
