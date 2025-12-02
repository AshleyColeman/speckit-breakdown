#!/usr/bin/env bash

# create-task-doc.sh
# Purpose: Generate a dedicated markdown file for a specific task with full context.
# Usage: ./create-task-doc.sh <TASK_ID> <TITLE> <CONTEXT_MARKDOWN>

set -e

TASK_ID="$1"
TITLE="$2"
CONTEXT="$3"

if [[ -z "$TASK_ID" || -z "$TITLE" ]]; then
    echo "Usage: $0 <TASK_ID> <TITLE> [CONTEXT_MARKDOWN]"
    exit 1
fi

# 1. Prepare Directory
TASKS_DIR="tasks"
mkdir -p "$TASKS_DIR"

# 2. Sanitize Title for Filename
# Convert to lowercase, replace spaces/special chars with hyphens
SAFE_TITLE=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//')
FILENAME="${TASKS_DIR}/${TASK_ID}-${SAFE_TITLE}.md"

# 3. Create File Content
cat <<EOF > "$FILENAME"
# Task: $TASK_ID - $TITLE

**Status**: In Progress
**Created**: $(date +%Y-%m-%d)

## Context
$CONTEXT

## Implementation Checklist
- [ ] Read the context above carefully.
- [ ] Implement the required changes.
- [ ] Verify against acceptance criteria.
- [ ] Update this file with notes or decisions.

## Notes
<!-- Add your implementation notes here -->

EOF

echo "Created task file: $FILENAME"
