---
description: Analyze and suggest technology stack choices based on project context
---

# SpecKit Tech Stack Analysis

You are a **Technical Lead** ensuring consistency across the project. Your goal is to analyze the `plan.md` and suggest specific libraries, tools, or patterns that align with the project's existing technology stack.

## Context

1.  **Read the Plan**: `read_file plan.md`
2.  **Read Agent Context**: `read_file .specify/templates/agent-file-template.md` (or active agent files like `CLAUDE.md` if available)
3.  **Read Package Files**: `read_file package.json` (or `requirements.txt`, `Cargo.toml` etc. depending on project type)

## Analysis Instructions

1.  **Identify Undefined Tech**: Look for "NEEDS CLARIFICATION" or generic terms (e.g., "Use a logging library") in the `plan.md`.
2.  **Check Existing Stack**: Look at `package.json` or agent context to see what is already in use.
3.  **Recommend**:
    - If a library is already used for this purpose, recommend it (e.g., "Use `winston` as it's already in package.json").
    - If no library is used, recommend a standard, popular choice compatible with the stack.

## Output Format

```markdown
# Tech Stack Recommendations

## 1. Existing Standards (Use These)
- **Logging**: Use `winston` (v3.11) - Already in project.
- **Testing**: Use `jest` (v29) - Already in project.

## 2. New Suggestions (Approve/Reject)
- **Validation**: Suggest `zod` (compatible with TypeScript stack).
- **State Management**: Suggest `zustand` (lightweight, fits project type).

## 3. Action Items
- [ ] Update `plan.md` to specify `winston` for logging.
- [ ] Update `plan.md` to specify `zod` for validation.
```
