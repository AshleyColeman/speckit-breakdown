# Task 015: Improve Installer Supply-Chain Guidance (Without Breaking UX)

## Goal
Reduce supply-chain risk and set expectations for users who install via remote download.

## Context (from audit)
- `install.sh` downloads remote workflow code via `curl -fsSL https://raw.githubusercontent.com/...` into `.windsurf/workflows/`.

## Scope
- Add documentation guidance for verifying what is run.
- Consider pinning installer to tags/commits, or documenting how to do so.

## Files likely involved
- `install.sh`
- `README.md`
- Any install docs under `docs/`

## Steps
1. Review install flow and current docs.
2. Add a doc section recommending:
   - pinning to a release tag/commit
   - reviewing scripts before running
   - optionally verifying checksums/signatures (if provided)
3. Optionally adjust the installer to encourage pinning (e.g., instructions or variables).
4. Ensure changes do not disrupt current install path.

## Acceptance criteria
- Docs clearly describe the risk and verification best practices.
- Installer remains functional.

## Non-goals
- Full cryptographic signing infrastructure.
