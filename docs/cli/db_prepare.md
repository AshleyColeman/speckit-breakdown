# `speckit.db.prepare`

The `speckit.db.prepare` command initializes the local system data store by parsing, validating, and persisting your Speckit specification files.

YAML frontmatter parsing is performed via `PyYAML` (required) to ensure deterministic behavior across environments.

## Key Features

- **Recursive Discovery**: If your documentation is nested (e.g., `specs/F01/tasks/*.md`), the system automatically discovers these files.
- **Topological Orchestration**: Calculates the optimal execution order (Step 1, Step 2, etc.) based on task dependencies.
- **Validation Pipeline**: Checks for circular dependencies, missing metadata, and schema drift before persisting.

## Options

| Option | Shorthand | Description | Default |
|--------|-----------|-------------|---------|
| `--docs-path` | | Path to documentation root (projects, specs, etc.) | `specs/` |
| `--storage-path` | | Path to SQLite database | `.speckit/db.sqlite` |
| `--db-url` | | PostgreSQL connection string (overrides `--storage-path`) | | 
| `--enable-experimental-postgres` | | Allow use of PostgreSQL backend (experimental; disabled by default) | `False` |
| `--dry-run` | | Validate and summarize changes without writing to DB | `False` |
| `--force` | | Overwrite existing entities even if they conflict | `False` |
| `--verbose`, `-v` | | Enable debug logging (shows **Execution Plan**) | `False` |
| `--log-format` | | Output format (`human` or `json`) | `human` |

## Support tiers

- **SQLite**: Stable (default).
- **PostgreSQL**: Experimental and **disabled by default**.

## PostgreSQL Integration

To connect to an external PostgreSQL database, you must provide a valid connection string and enable the experimental backend.

### CLI Usage
```bash
python -m src.cli.main speckit.db.prepare \
  --db-url "postgresql://user:password@localhost:5432/dbname" \
  --enable-experimental-postgres
```

### Schema Requirements
The PostgreSQL backend does **not** run migrations. It enforces a strict schema contract on startup and will refuse to run if the following tables and columns are missing or incorrectly typed:

| Table | Required Columns | Notes |
|-------|------------------|-------|
| `projects` | `id`, `name`, `description`, `status` | |
| `features` | `id`, `project_id`, `name`, `description`, `priority`, `status` | |
| `specs` | `id`, `feature_id`, `name`, `file_path`, `status` | |
| `tasks` | `id`, `name`, `status`, `description`, `metadata`, `feature_id`, `project_id`, `step_order` | `metadata` must be `json` or `jsonb` |
| `task_dependencies` | `predecessor_id`, `successor_id` | |

> [!IMPORTANT]
> The system requires `metadata->>'code'` lookups for stable identifiers. If `tasks.metadata` is not a JSON type, the command will fail.

### Recommended PostgreSQL DDL
If you are setting up a new PostgreSQL database, you can use the following DDL as a starting point:

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    status TEXT DEFAULT 'active'
);

CREATE TABLE features (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    name TEXT NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 0,
    status TEXT DEFAULT 'planned',
    UNIQUE(project_id, name)
);

CREATE TABLE specs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feature_id UUID REFERENCES features(id),
    name TEXT NOT NULL,
    file_path TEXT,
    status TEXT DEFAULT 'draft',
    UNIQUE(feature_id, name)
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    feature_id UUID REFERENCES features(id),
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo',
    step_order INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE task_dependencies (
    predecessor_id UUID REFERENCES tasks(id),
    successor_id UUID REFERENCES tasks(id),
    PRIMARY KEY (predecessor_id, successor_id)
);
```

## Orchestration Plan

When using `--verbose`, the system will print the calculated execution order:

```text
DEBUG | src.services.bootstrap_orchestrator - Calculated Execution Plan:
DEBUG | src.services.bootstrap_orchestrator -   [Step 1] t001
DEBUG | src.services.bootstrap_orchestrator -   [Step 2] t002 (Parallelizable)
```

## Examples

**1. Validate and view execution plan (Dry Run):**
```bash
python -m src.cli.main --dry-run --verbose
```

**2. Bootstrap a nested workflow project:**
```bash
python -m src.cli.main --docs-path my-project-docs/ --verbose
```

**3. Force update a specific project:**
```bash
python -m src.cli.main --project P-123 --force
```
