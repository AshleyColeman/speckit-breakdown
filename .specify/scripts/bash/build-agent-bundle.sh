#!/usr/bin/env bash

# build-agent-bundle.sh
# Purpose: Convert a SpecKit context pack into an agent-ready bundle under .speckit/agent/.

set -e

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

# shellcheck disable=SC2046
eval $(get_feature_paths)

REPO_ROOT="$REPO_ROOT"
CONTEXT_JSON="$REPO_ROOT/.speckit/context/context.json"
AGENT_ROOT="$REPO_ROOT/.speckit/agent"
CHUNKS_DIR="$AGENT_ROOT/chunks"
INSTR_DIR="$AGENT_ROOT/instructions"

mkdir -p "$CHUNKS_DIR" "$INSTR_DIR"

if [[ ! -f "$CONTEXT_JSON" ]]; then
    echo "ERROR: Context pack not found at $CONTEXT_JSON. Run /speckit.bundle first." >&2
    exit 1
fi

python3 - "$CONTEXT_JSON" "$CHUNKS_DIR" "$INSTR_DIR" "$AGENT_ROOT" << 'PY'
import json
import os
import sys
from pathlib import Path

context_json_path = Path(sys.argv[1])
chunks_dir = Path(sys.argv[2])
instr_dir = Path(sys.argv[3])
agent_root = Path(sys.argv[4])

# Repository root is two levels above the context directory:
#   REPO_ROOT/.speckit/context/context.json
repo_root = context_json_path.parents[2]

with context_json_path.open("r", encoding="utf-8") as f:
    context = json.load(f)

project_name = context.get("projectName", "unknown-project")
feature_id = context.get("featureId") or "feature"
version = context.get("version", "0.0.0")

chunks = []

# Simple 1:1 chunking: one chunk per file in the context pack
for idx, file_info in enumerate(context.get("files", []), start=1):
    rel_path = file_info.get("path")
    role = file_info.get("role", "other")
    title = file_info.get("title", os.path.basename(rel_path or ""))

    if not rel_path:
        continue

    # Paths in context.json are repo-relative (e.g., .speckit/context/spec.md)
    source_abs = (repo_root / rel_path).resolve()
    if not source_abs.is_file():
        continue

    chunk_id = f"{role}-{idx:03d}"
    chunk_filename = f"{chunk_id}.md"
    chunk_path = chunks_dir / chunk_filename

    with source_abs.open("r", encoding="utf-8") as src, chunk_path.open("w", encoding="utf-8") as dst:
        dst.write(src.read())

    chunks.append({
        "chunkId": chunk_id,
        "role": role,
        "sourcePath": rel_path,
        "title": title,
        "order": idx,
        "chunkPath": str(chunk_path.relative_to(agent_root)),
    })

# Basic instructions for three common roles
planner_instr = instr_dir / "planner.md"
implementer_instr = instr_dir / "implementer.md"
reviewer_instr = instr_dir / "reviewer.md"

if not planner_instr.exists():
    planner_instr.write_text(
        """# Planner Instructions\n\nUse spec, plan, and tasks chunks to design or adjust implementation strategies.\nPrioritise P1 user stories and respect constraints from the plan and research.\n""",
        encoding="utf-8",
    )

if not implementer_instr.exists():
    implementer_instr.write_text(
        """# Implementer Instructions\n\nUse tasks, plan, and architecture chunks to implement changes.\nFollow file paths in tasks.md and keep architecture and design docs in sync.\n""",
        encoding="utf-8",
    )

if not reviewer_instr.exists():
    reviewer_instr.write_text(
        """# Reviewer Instructions\n\nUse spec, plan, tasks, architecture, and health report chunks to review work.\nCheck that design intent, implementation, and health status are aligned.\n""",
        encoding="utf-8",
    )

config = {
    "projectName": project_name,
    "featureId": feature_id,
    "version": version,
    "chunksPath": "chunks",
    "instructionsPath": "instructions",
    "chunks": chunks,
}

config_path = agent_root / "config.json"
config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

print(json.dumps({
    "AGENT_ROOT": str(agent_root),
    "CHUNKS": chunks,
    "INSTRUCTIONS": [p.name for p in instr_dir.glob("*.md")],
}, indent=2))
PY

