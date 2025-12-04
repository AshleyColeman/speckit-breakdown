#!/usr/bin/env bash

# build-architecture.sh
# Purpose: Resolve paths and scope for architecture generation for a SpecKit feature or project.
# This script does NOT call the LLM directly; it prepares canonical paths for the speckit.arch workflow.
#
# Usage:
#   ./build-architecture.sh [--scope project|feature] [--json]
#
# Outputs (JSON when --json is provided):
#   {"SCOPE":"feature|project","FEATURE_DIR":"...","FEATURE_SPEC":"...",
#    "IMPL_PLAN":"...","TASKS":"...","ARCH_PATH":"..."}

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
            echo "Usage: $0 [--scope project|feature] [--json]"
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

# Resolve feature paths from common helpers
eval "$(get_feature_paths)"

REPO_ROOT="$REPO_ROOT"
FEATURE_DIR="$FEATURE_DIR"
FEATURE_SPEC="$FEATURE_SPEC"
IMPL_PLAN="$IMPL_PLAN"
TASKS="$TASKS"

# Decide architecture output path
if [[ "$SCOPE" == "project" ]]; then
    ARCH_PATH="$REPO_ROOT/docs/architecture.md"
else
    ARCH_PATH="$FEATURE_DIR/architecture.md"
fi

# Ensure parent directory exists
ARCH_DIR="$(dirname "$ARCH_PATH")"
mkdir -p "$ARCH_DIR"

if $JSON_MODE; then
    printf '{"SCOPE":"%s","FEATURE_DIR":"%s","FEATURE_SPEC":"%s","IMPL_PLAN":"%s","TASKS":"%s","ARCH_PATH":"%s"}
' \
        "$SCOPE" "$FEATURE_DIR" "$FEATURE_SPEC" "$IMPL_PLAN" "$TASKS" "$ARCH_PATH"
else
    echo "SCOPE: $SCOPE"
    echo "FEATURE_DIR: $FEATURE_DIR"
    echo "FEATURE_SPEC: $FEATURE_SPEC"
    echo "IMPL_PLAN: $IMPL_PLAN"
    echo "TASKS: $TASKS"
    echo "ARCH_PATH: $ARCH_PATH"
fi
