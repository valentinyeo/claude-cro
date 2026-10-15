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
cp "${SCRIPT_DIR}/skills/cro/SKILL.md" "${SKILLS_DIR}/cro/SKILL.md"

# ── Copy reference files ──────────────────────────────────────────────

echo "Installing reference files..."
if [ -d "${SCRIPT_DIR}/skills/cro/references" ]; then
    cp "${SCRIPT_DIR}/skills/cro/references/"*.md "${SKILLS_DIR}/cro/references/" 2>/dev/null || true
fi

# ── Copy scripts ───────────────────────────────────────────────────────

echo "Installing Python scripts..."
SCRIPT_COUNT=0
if [ -d "${SCRIPT_DIR}/skills/cro/scripts" ]; then
    for script_file in "${SCRIPT_DIR}/skills/cro/scripts/"*.py "${SCRIPT_DIR}/skills/cro/scripts/cro-py"; do
        if [ -f "${script_file}" ]; then
            cp "${script_file}" "${SKILLS_DIR}/cro/scripts/"
            chmod +x "${SKILLS_DIR}/cro/scripts/$(basename "${script_file}")"
            SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
        fi
    done
fi

# ── Copy sub-skills ────────────────────────────────────────────────────

echo "Installing sub-skills..."
SKILL_COUNT=0
for skill_dir in "${SCRIPT_DIR}/skills/cro-"*/; do
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

# ── Install Python dependencies (private venv: system pip is often locked) ──

echo ""
echo "Installing Python dependencies into ${SKILLS_DIR}/cro/.venv ..."
VENV="${SKILLS_DIR}/cro/.venv"
if python3 -m venv "${VENV}" && "${VENV}/bin/pip" install -q -r "${SCRIPT_DIR}/requirements.txt"; then
    echo "  Python dependencies installed."
    if "${VENV}/bin/python" -m playwright install chromium >/dev/null; then
        echo "  Chromium installed for screenshots."
    else
        echo "  Warning: Chromium install failed; screenshots will be skipped."
        echo "    Retry: ${VENV}/bin/python -m playwright install chromium"
    fi
else
    echo "  ERROR: could not build the Python env. Scripts will not run."
    echo "    Needs python3-venv. Retry: python3 -m venv ${VENV} && ${VENV}/bin/pip install -r ${SCRIPT_DIR}/requirements.txt"
    exit 1
fi

# ── Summary ────────────────────────────────────────────────────────────

echo ""
echo "========================================"
echo "  Installation Complete"
echo "========================================"
echo ""
echo "  Orchestrator:   skills/cro/SKILL.md"
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
echo "  Or install as a plugin:"
echo "    /plugin install claude-cro@valentinyeo/claude-cro"
echo ""
