# `speckit.db.prepare`

The `speckit.db.prepare` command initializes the local system data store by parsing, validating, and persisting your Speckit specification files.

## Usage

```bash
/speckit.db.prepare [OPTIONS]
```

## Options

| Option | Shorthand | Description | Default |
|--------|-----------|-------------|---------|
| `--docs-path` | | Path to documentation root (projects, specs, etc.) | `specs/` |
| `--storage-path` | | Path to SQLite database | `.speckit/db.sqlite` |
| `--dry-run` | | Validate and summarize changes without writing to DB | `False` |
| `--force` | | Overwrite existing entities even if they conflict | `False` |
| `--verbose`, `-v` | | Enable debug logging | `False` |
| `--log-format` | | Output format (`human` or `json`) | `human` |

### Selective Bootstrap Options

You can limit the scope of the bootstrap process to specific projects or entity types.

| Option | Shorthand | Description |
|--------|-----------|-------------|
| `--project` | `-p` | Limit processing to a specific project code (e.g. `P-123`). Features, Specs, and Tasks belonging to other projects will be ignored. |
| `--skip-task-runs` | | Do not auto-create Task Run entities. |
| `--skip-ai-jobs` | | Do not auto-create AI Job entities. |

## Examples

**1. Validate documentation without changes (Dry Run):**
```bash
/speckit.db.prepare --dry-run
```

**2. Bootstrap a specific project only:**
```bash
/speckit.db.prepare --project P-MOBILE-APP
```

**3. Force update an existing project:**
```bash
/speckit.db.prepare --project P-MOBILE-APP --force
```

**4. Bootstrap core entities only (skip derived runs/jobs):**
```bash
/speckit.db.prepare --skip-task-runs --skip-ai-jobs
```
