#!/usr/bin/env bash

# expand-tasks.sh
# Purpose: Safely insert new sub-tasks into tasks.md, handling ID generation and indentation.
# Usage: ./expand-tasks.sh <PARENT_TASK_ID> <JSON_TASK_LIST>

set -e

PARENT_ID="$1"
JSON_TASKS="$2"
TASKS_FILE="tasks.md"

if [[ -z "$PARENT_ID" || -z "$JSON_TASKS" ]]; then
    echo "Usage: $0 <PARENT_TASK_ID> <JSON_TASK_LIST>"
    exit 1
fi

if [[ ! -f "$TASKS_FILE" ]]; then
    echo "Error: tasks.md not found in current directory."
    exit 1
fi

# 1. Find the highest existing Task ID (Txxx)
# We look for patterns like "T001", "T123" and extract the number.
MAX_ID=$(grep -o "T[0-9]\{3\}" "$TASKS_FILE" | sed 's/^T//' | sort -rn | head -1)
if [[ -z "$MAX_ID" ]]; then
    MAX_ID=0
else
    # Remove leading zeros for arithmetic
    MAX_ID=$((10#$MAX_ID))
fi

echo "Current Max ID: T$(printf "%03d" $MAX_ID)"

# 2. Parse JSON and generate new task lines
# We use python3 for robust JSON parsing if jq is not available, or simple string manipulation if needed.
# Assuming python3 is available as it's standard on linux.

NEW_TASKS_BLOCK=$(python3 -c "
import sys, json

parent_id = '$PARENT_ID'
start_id = $MAX_ID + 1
try:
    tasks = json.loads('$JSON_TASKS')
except json.JSONDecodeError as e:
    print(f'Error parsing JSON: {e}', file=sys.stderr)
    sys.exit(1)

output = []
current_id = start_id

for task in tasks:
    desc = task.get('description', 'No description')
    # Format: - [ ] Txxx [P] [ParentID] Description
    # We add [P] for parallel and reference the parent ID for traceability
    line = f'- [ ] T{current_id:03d} [P] [{parent_id}] {desc}'
    output.append(line)
    current_id += 1

print('\n'.join(output))
")

if [[ $? -ne 0 ]]; then
    echo "Failed to generate new task lines."
    exit 1
fi

# 3. Insert into tasks.md
# We use sed to find the parent line and append the new block after it.
# We also want to mark the parent task as checked [x] or modified.

# Escape special characters for sed
ESCAPED_BLOCK=$(echo "$NEW_TASKS_BLOCK" | sed 's/\\/\\\\/g' | sed 's/&/\\&/g' | sed ':a;N;$!ba;s/\n/\\n/g')

# Find line number of parent task
PARENT_LINE_NUM=$(grep -n "$PARENT_ID" "$TASKS_FILE" | cut -d: -f1 | head -1)

if [[ -z "$PARENT_LINE_NUM" ]]; then
    echo "Error: Parent task $PARENT_ID not found in $TASKS_FILE"
    exit 1
fi

# Insert new tasks AFTER the parent line
# And update parent line to be checked [x] if it was unchecked [ ]
sed -i "${PARENT_LINE_NUM}s/- \[ \]/- [x]/" "$TASKS_FILE"
sed -i "${PARENT_LINE_NUM}a\\$ESCAPED_BLOCK" "$TASKS_FILE"

echo "Successfully expanded task $PARENT_ID with $(echo "$NEW_TASKS_BLOCK" | wc -l) new sub-tasks."
