#!/usr/bin/env bash

# health-check.sh
# Purpose: Assess SpecKit project/feature health and emit JSON + markdown reports.
#
# Usage:
#   ./health-check.sh [--scope=project|feature] [--json]
#
# Exit codes:
#   0 = healthy or only informational issues
#   1 = warnings present, no critical issues
#   2 = critical issues present

set -e

SCOPE="feature"
JSON_MODE=false

for arg in "$@"; do
    case "$arg" in
        --scope=project)
            SCOPE="project"
            ;;
        --scope=feature)
            SCOPE="feature"
            ;;
        --json)
            JSON_MODE=true
            ;;
        --help|-h)
            echo "Usage: $0 [--scope=project|feature] [--json]"
            exit 0
            ;;
        *)
            echo "WARNING: Unknown argument '$arg' ignored" >&2
            ;;
    esac
done

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

# Resolve feature paths
# shellcheck disable=SC2046
eval $(get_feature_paths)

REPO_ROOT="$REPO_ROOT"
FEATURE_DIR="$FEATURE_DIR"
FEATURE_SPEC="$FEATURE_SPEC"
IMPL_PLAN="$IMPL_PLAN"
TASKS="$TASKS"
RESEARCH="$RESEARCH"
DATA_MODEL="$DATA_MODEL"
QUICKSTART="$QUICKSTART"

HEALTH_ROOT="$REPO_ROOT/.speckit/health"
mkdir -p "$HEALTH_ROOT"

VERSION_FILE="$REPO_ROOT/VERSION"
VERSION="0.0.0"
if [[ -f "$VERSION_FILE" ]]; then
    VERSION="$(head -n 1 "$VERSION_FILE" | tr -d '\r')"
fi

PROJECT_NAME="$(basename "$REPO_ROOT")"
FEATURE_ID="$(basename "$FEATURE_DIR")"
GENERATED_AT="$(date -Iseconds)"

issues_json="[]"

add_issue() {
    local issueId="$1" severity="$2" message="$3" file="$4" suggestion="$5"
    local entry
    entry=$(cat <<EOF
{"issueId":"$issueId","severity":"$severity","message":"$message","file":"$file","suggestion":"$suggestion"}
EOF
)
    if [[ "$issues_json" == "[]" ]]; then
        issues_json="[$entry]"
    else
        issues_json="${issues_json%]} , $entry]"
    fi
}

# Basic checks: presence of key design files
if [[ ! -f "$FEATURE_SPEC" ]]; then
    add_issue "MISSING_SPEC" "critical" "spec.md is missing for feature" "$FEATURE_SPEC" "Run /speckit.specify and /speckit.plan for this feature."
fi

if [[ ! -f "$IMPL_PLAN" ]]; then
    add_issue "MISSING_PLAN" "critical" "plan.md is missing for feature" "$IMPL_PLAN" "Run /speckit.plan to generate the implementation plan."
fi

if [[ ! -f "$TASKS" ]]; then
    add_issue "MISSING_TASKS" "critical" "tasks.md is missing for feature" "$TASKS" "Run /speckit.tasks to generate the task list."
fi

# Optional docs: warn if absent
if [[ ! -f "$RESEARCH" ]]; then
    add_issue "MISSING_RESEARCH" "warning" "research.md not found; decisions may not be documented." "$RESEARCH" "Run /speckit.plan to complete research.md or document decisions manually."
fi

if [[ ! -f "$DATA_MODEL" ]]; then
    add_issue "MISSING_DATA_MODEL" "warning" "data-model.md not found; entities/relationships may be under-specified." "$DATA_MODEL" "Ensure data-model.md is generated and maintained via /speckit.plan."
fi

STATUS="healthy"
EXIT_CODE=0

case "$issues_json" in
    "[]")
        STATUS="healthy"
        EXIT_CODE=0
        ;;
    *"\"severity\":\"critical\""*)
        STATUS="critical"
        EXIT_CODE=2
        ;;
    *"\"severity\":\"warning\""*)
        STATUS="warning"
        EXIT_CODE=1
        ;;
    *)
        STATUS="healthy"
        EXIT_CODE=0
        ;;
esac

REPORT_JSON="$HEALTH_ROOT/report.json"

cat > "$REPORT_JSON" <<EOF
{
  "id": "health-${FEATURE_ID}",
  "projectName": "${PROJECT_NAME}",
  "scope": "${SCOPE}",
  "featureId": "${FEATURE_ID}",
  "version": "${VERSION}",
  "generatedAt": "${GENERATED_AT}",
  "status": "${STATUS}",
  "issues": ${issues_json}
}
EOF

REPORT_MD="$HEALTH_ROOT/report.md"

{
  echo "# SpecKit Health Report: ${PROJECT_NAME} (${FEATURE_ID})"
  echo
  echo "**Scope**: ${SCOPE}"
  echo "**Status**: ${STATUS}"
  echo "**Generated At**: ${GENERATED_AT}"
  echo
  echo "## Issues"
  if [[ "$issues_json" == "[]" ]]; then
      echo "- No issues detected."
  else
      echo "- See JSON report at .speckit/health/report.json for full details."
  fi
} > "$REPORT_MD"

if $JSON_MODE; then
    cat "$REPORT_JSON"
else
    echo "Health report written to: $REPORT_JSON and $REPORT_MD"
fi

exit "$EXIT_CODE"
