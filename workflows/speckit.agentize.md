---
description: Generate an agent-ready bundle from an existing SpecKit context pack.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Ensure context pack exists**
   - From repo root, run:
     - `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks --require-advanced`
   - If `.speckit/context/context.json` does not exist, run:
     - `.specify/scripts/bash/build-context-pack.sh --json`

2. **Build agent bundle**
   - From repo root, run:
     - `.specify/scripts/bash/build-agent-bundle.sh`
   - This will:
     - Read `.speckit/context/context.json`.
     - Create `.speckit/agent/config.json`.
     - Populate `.speckit/agent/chunks/*.md` and `.speckit/agent/instructions/*.md`.

3. **(Optional) Refine with speckit.agentize prompt**
   - Use `.claude/commands/speckit.agentize.md` as guidance to further tune chunking or instructions if necessary.

4. **Report**
   - Summarise:
     - Number of chunks created and their roles.
     - Instruction files available.
     - Path to `config.json`.

## Notes

- This workflow assumes design-time markdown-only context packs (no code) as per the 006-ai-extensions spec.
- It is safe and idempotent; re-running should refresh the agent bundle to match the latest context pack.
