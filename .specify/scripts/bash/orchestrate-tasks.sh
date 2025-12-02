#!/usr/bin/env bash

# orchestrate-tasks.sh
# Purpose: Batch generate task files from a JSON list.
# Usage: ./orchestrate-tasks.sh '<JSON_TASK_LIST>'

set -e

JSON_TASKS="$1"
TASKS_DIR="tasks"

if [[ -z "$JSON_TASKS" ]]; then
    echo "Usage: $0 '<JSON_TASK_LIST>'"
    exit 1
fi

mkdir -p "$TASKS_DIR"

# Parse JSON and iterate
# We use python3 for robust JSON parsing
python3 -c "
import sys, json, os, re

try:
    tasks = json.loads('$JSON_TASKS')
except json.JSONDecodeError as e:
    print(f'Error parsing JSON: {e}', file=sys.stderr)
    sys.exit(1)

tasks_dir = '$TASKS_DIR'

for task in tasks:
    t_id = task.get('id')
    desc = task.get('description', 'No description')
    order = task.get('order', 1)
    parallel = task.get('parallel', False)
    phase = task.get('phase', 'Unknown Phase')
    
    # Sanitize title for filename
    safe_desc = re.sub(r'[^a-z0-9]', '-', desc.lower()).strip('-')
    safe_desc = re.sub(r'-+', '-', safe_desc)
    
    # Filename format: order-id-desc.md (e.g., 01-T001-setup.md)
    filename = f'{order:02d}-{t_id}-{safe_desc}.md'
    filepath = os.path.join(tasks_dir, filename)
    
    content = f'''---
id: {t_id}
order: {order}
parallel: {str(parallel).lower()}
phase: \"{phase}\"
---

# Task: {t_id} - {desc}

**Status**: Pending
**Execution Order**: {order}
**Parallel**: {parallel}

## Context
<!-- Extracted from tasks.md and plan.md -->
This task belongs to **{phase}**.

## Implementation Checklist
- [ ] Read the full spec/plan context if needed.
- [ ] Implement the changes.
- [ ] Verify functionality.
'''
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f'Generated: {filepath}')
"
