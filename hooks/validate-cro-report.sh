#!/usr/bin/env bash
#
# validate-cro-report.sh — Validate CRO report files
#
# Checks that CRO reports (FULL-AUDIT.md, ACTION-PLAN.md) meet minimum
# quality requirements: presence, minimum content length, score format,
# and required priority sections.
#
# Exit 0 on pass, exit 1 on fail with description.
#
# Usage:
#   ./validate-cro-report.sh [report-directory]
#   ./validate-cro-report.sh ./output/
#
# If no directory is given, checks the current directory.

set -euo pipefail

REPORT_DIR="${1:-.}"
ERRORS=()

# ── Helper functions ───────────────────────────────────────────────────

add_error() {
    ERRORS+=("$1")
}

check_file_exists() {
    local file="$1"
    local label="$2"
    if [ ! -f "${REPORT_DIR}/${file}" ]; then
        add_error "${label}: File '${file}' not found in ${REPORT_DIR}/"
        return 1
    fi
    return 0
}

check_min_length() {
    local file="$1"
    local min_lines="$2"
    local label="$3"
    local filepath="${REPORT_DIR}/${file}"

    if [ ! -f "${filepath}" ]; then
        return 1
    fi

    local line_count
    line_count=$(wc -l < "${filepath}")

    if [ "${line_count}" -lt "${min_lines}" ]; then
        add_error "${label}: File has ${line_count} lines, minimum is ${min_lines}"
        return 1
    fi
    return 0
}

check_score_present() {
    local file="$1"
    local label="$2"
    local filepath="${REPORT_DIR}/${file}"

    if [ ! -f "${filepath}" ]; then
        return 1
    fi

    # Look for score pattern: number/100 or Score: number
    if ! grep -qEi '(score[:\s]*[0-9]{1,3}\s*/\s*100|[0-9]{1,3}/100|score[:\s]*[0-9]{1,3})' "${filepath}"; then
        add_error "${label}: No CRO score found. Expected format: 'Score: XX/100' or 'XX/100'"
        return 1
    fi

    # Validate score is within 0-100
    local scores
    scores=$(grep -oEi '[0-9]{1,3}\s*/\s*100' "${filepath}" | head -5)

    while IFS= read -r score_match; do
        if [ -n "${score_match}" ]; then
            local score_num
            score_num=$(echo "${score_match}" | grep -oE '^[0-9]+')
            if [ "${score_num}" -gt 100 ]; then
                add_error "${label}: Score ${score_num}/100 is out of range (must be 0-100)"
                return 1
            fi
        fi
    done <<< "${scores}"

    return 0
}

check_priority_sections() {
    local file="$1"
    local label="$2"
    local filepath="${REPORT_DIR}/${file}"

    if [ ! -f "${filepath}" ]; then
        return 1
    fi

    local missing_sections=()

    # Check for priority level sections (flexible matching)
    if ! grep -qEi '(critical|p0|priority.*critical)' "${filepath}"; then
        missing_sections+=("Critical")
    fi

    if ! grep -qEi '(high.*priority|priority.*high|\[high\]|p1)' "${filepath}"; then
        missing_sections+=("High")
    fi

    if ! grep -qEi '(medium.*priority|priority.*medium|\[medium\]|p2)' "${filepath}"; then
        missing_sections+=("Medium")
    fi

    if ! grep -qEi '(low.*priority|priority.*low|\[low\]|p3)' "${filepath}"; then
        missing_sections+=("Low")
    fi

    if [ ${#missing_sections[@]} -gt 0 ]; then
        local joined
        joined=$(IFS=', '; echo "${missing_sections[*]}")
        add_error "${label}: Missing priority sections: ${joined}"
        return 1
    fi

    return 0
}

# ── Run checks ─────────────────────────────────────────────────────────

echo "Validating CRO reports in: ${REPORT_DIR}/"
echo ""

# Track which files exist for conditional checks
HAS_AUDIT=false
HAS_PLAN=false

# Check FULL-AUDIT.md
if check_file_exists "FULL-AUDIT.md" "Full Audit"; then
    HAS_AUDIT=true
    check_min_length "FULL-AUDIT.md" 30 "Full Audit"
    check_score_present "FULL-AUDIT.md" "Full Audit"
    check_priority_sections "FULL-AUDIT.md" "Full Audit"
fi

# Check ACTION-PLAN.md
if check_file_exists "ACTION-PLAN.md" "Action Plan"; then
    HAS_PLAN=true
    check_min_length "ACTION-PLAN.md" 15 "Action Plan"
    check_priority_sections "ACTION-PLAN.md" "Action Plan"
fi

# At least one report must exist
if [ "${HAS_AUDIT}" = false ] && [ "${HAS_PLAN}" = false ]; then
    add_error "No CRO report files found (expected FULL-AUDIT.md and/or ACTION-PLAN.md)"
fi

# ── Report results ─────────────────────────────────────────────────────

if [ ${#ERRORS[@]} -eq 0 ]; then
    echo "PASS: All validation checks passed."
    echo ""
    if [ "${HAS_AUDIT}" = true ]; then
        echo "  FULL-AUDIT.md  ... OK"
    fi
    if [ "${HAS_PLAN}" = true ]; then
        echo "  ACTION-PLAN.md ... OK"
    fi
    echo ""
    exit 0
else
    echo "FAIL: ${#ERRORS[@]} validation error(s) found:"
    echo ""
    for error in "${ERRORS[@]}"; do
        echo "  ERROR: ${error}"
    done
    echo ""
    exit 1
fi
