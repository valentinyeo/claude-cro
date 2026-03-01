#!/usr/bin/env bash
#
# uninstall.sh — Uninstall Claude CRO skill package
#
# Removes all CRO skills, agents, and scripts from ~/.claude/
#
# Usage:
#   ./uninstall.sh
#   bash uninstall.sh

set -euo pipefail

CLAUDE_DIR="${HOME}/.claude"
SKILLS_DIR="${CLAUDE_DIR}/skills"
AGENTS_DIR="${CLAUDE_DIR}/agents"

echo "========================================"
echo "  Claude CRO — Uninstaller"
echo "========================================"
echo ""

# ── Discover what will be removed ──────────────────────────────────────

ITEMS_TO_REMOVE=()

# Main orchestrator directory
if [ -d "${SKILLS_DIR}/cro" ]; then
    ITEMS_TO_REMOVE+=("${SKILLS_DIR}/cro/")
fi

# Sub-skill directories
for dir in "${SKILLS_DIR}/cro-"*/; do
    if [ -d "${dir}" ]; then
        ITEMS_TO_REMOVE+=("${dir}")
    fi
done

# Agent files
for file in "${AGENTS_DIR}/cro-"*.md; do
    if [ -f "${file}" ]; then
        ITEMS_TO_REMOVE+=("${file}")
    fi
done

# ── Show what will be removed ──────────────────────────────────────────

if [ ${#ITEMS_TO_REMOVE[@]} -eq 0 ]; then
    echo "Nothing to remove. Claude CRO does not appear to be installed."
    exit 0
fi

echo "The following items will be removed:"
echo ""
for item in "${ITEMS_TO_REMOVE[@]}"; do
    echo "  ${item}"
done

echo ""
read -p "Proceed with uninstall? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

# ── Remove items ───────────────────────────────────────────────────────

echo ""
echo "Removing..."

REMOVED_COUNT=0

# Remove main orchestrator directory
if [ -d "${SKILLS_DIR}/cro" ]; then
    rm -rf "${SKILLS_DIR}/cro"
    echo "  Removed: ${SKILLS_DIR}/cro/"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
fi

# Remove sub-skill directories
for dir in "${SKILLS_DIR}/cro-"*/; do
    if [ -d "${dir}" ]; then
        rm -rf "${dir}"
        echo "  Removed: ${dir}"
        REMOVED_COUNT=$((REMOVED_COUNT + 1))
    fi
done

# Remove agent files
for file in "${AGENTS_DIR}/cro-"*.md; do
    if [ -f "${file}" ]; then
        rm -f "${file}"
        echo "  Removed: ${file}"
        REMOVED_COUNT=$((REMOVED_COUNT + 1))
    fi
done

# ── Summary ────────────────────────────────────────────────────────────

echo ""
echo "========================================"
echo "  Uninstall Complete"
echo "========================================"
echo ""
echo "  Items removed: ${REMOVED_COUNT}"
echo ""
echo "  Note: Python packages (requests, beautifulsoup4, lxml, playwright)"
echo "  were NOT uninstalled. Remove them manually if desired:"
echo "    pip uninstall requests beautifulsoup4 lxml playwright"
echo ""
