#!/usr/bin/env bash

# build-context-pack.sh
# Purpose: Gather design-time SpecKit artifacts and build a context pack under .speckit/context.
#
# Usage:
#   ./build-context-pack.sh [--scope=project|feature] [--json]
#
# Notes:
# - This script is intentionally conservative: it only works with design-time markdown artifacts
#   (specs, plans, tasks, architecture, research, data-model, quickstart, etc.).
# - It does not include source code.

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

# Get feature paths
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

CONTEXT_ROOT="$REPO_ROOT/.speckit/context"
mkdir -p "$CONTEXT_ROOT"

# Helper to safely copy if file exists
copy_if_exists() {
    local src="$1"
    local dest="$2"
    if [[ -f "$src" ]]; then
        cp "$src" "$dest"
    fi
}

# Always copy core feature files into context root
copy_if_exists "$FEATURE_SPEC" "$CONTEXT_ROOT/spec.md"
copy_if_exists "$IMPL_PLAN" "$CONTEXT_ROOT/plan.md"
copy_if_exists "$TASKS" "$CONTEXT_ROOT/tasks.md"

# Optional feature-level files
ARCH_SOURCE="$FEATURE_DIR/architecture.md"
copy_if_exists "$ARCH_SOURCE" "$CONTEXT_ROOT/architecture.md"
copy_if_exists "$RESEARCH" "$CONTEXT_ROOT/research.md"
copy_if_exists "$DATA_MODEL" "$CONTEXT_ROOT/data-model.md"
copy_if_exists "$QUICKSTART" "$CONTEXT_ROOT/quickstart.md"

VERSION_FILE="$REPO_ROOT/VERSION"
VERSION="0.0.0"
if [[ -f "$VERSION_FILE" ]]; then
    VERSION="$(head -n 1 "$VERSION_FILE" | tr -d '\r')"
fi

PROJECT_NAME="$(basename "$REPO_ROOT")"
FEATURE_ID="$(basename "$FEATURE_DIR")"
GENERATED_AT="$(date -Iseconds)"

export REPO_ROOT CONTEXT_ROOT PROJECT_NAME FEATURE_ID VERSION GENERATED_AT

CONTEXT_JSON="$CONTEXT_ROOT/context.json"

python3 - "$CONTEXT_JSON" << 'PY'
import json
import os
import sys

context_json_path = sys.argv[1]

repo_root = os.environ["REPO_ROOT"]
context_root = os.environ["CONTEXT_ROOT"]
project_name = os.environ["PROJECT_NAME"]
feature_id = os.environ["FEATURE_ID"]
version = os.environ["VERSION"]
generated_at = os.environ["GENERATED_AT"]

files = []

def add_file(name, role, title):
    path_relative = os.path.join(".speckit", "context", name)
    abs_path = os.path.join(repo_root, path_relative)
    if os.path.isfile(abs_path):
        files.append({
            "path": path_relative,
            "role": role,
            "title": title,
            "contentStrategy": "full",
        })

add_file("spec.md", "spec", "Feature Specification")
add_file("plan.md", "plan", "Implementation Plan")
add_file("tasks.md", "tasks", "Task List")
add_file("architecture.md", "architecture", "Architecture Snapshot")
add_file("research.md", "other", "Research & Decisions")
add_file("data-model.md", "other", "Data Model")
add_file("quickstart.md", "other", "Feature Quickstart")

context = {
    "id": f"feature-{feature_id}",
    "projectName": project_name,
    "featureId": feature_id,
    "version": version,
    "generatedAt": generated_at,
    "files": files,
    "techStack": [],
    "constraints": [],
}

os.makedirs(os.path.dirname(context_json_path), exist_ok=True)
with open(context_json_path, "w", encoding="utf-8") as f:
    json.dump(context, f, indent=2)

print(json.dumps({
    "CONTEXT_ROOT": os.path.relpath(context_root, repo_root),
    "CONTEXT_JSON": os.path.relpath(context_json_path, repo_root),
    "FILES": files,
}, indent=2))
PY

# Python prints a JSON summary that we want to re-use
# Capture it from the last command's stdout
# (Bash will have already printed it; we only adjust behaviour for non-JSON mode)

if ! $JSON_MODE; then
    echo "Context pack written under: $CONTEXT_ROOT"
    echo "Context JSON: $CONTEXT_JSON"
fi

if $JSON_MODE; then
    # Nothing to do: JSON already printed by Python
    :
fi
