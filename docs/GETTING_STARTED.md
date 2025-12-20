# Getting Started with SpecKit Reliability

Welcome to the enhanced SpecKit experience! This project adds deep validation, standardized templates, and a guided "Golden Path" for your project documentation.

## Running the CLI

All commands are executed via:
```bash
python -m src.cli.main [command]
```

### 1. Initialize Your Project
Set up a fresh project with the correct structure and `speckit.yaml` config.
```bash
python -m src.cli.main speckit.init
```

### 2. Verify Your Documentation
Run the pre-flight check to find broken references, naming issues, or missing metadata.
```bash
python -m src.cli.main speckit.validate
```

### 3. Check System Health
Need to debug your environment? Running `doctor` will check for Python versions, config files, and directory requirements.
```bash
python -m src.cli.main speckit.doctor
```

### 4. Migrate Existing Projects
Coming from an older SpecKit structure? Use `migrate` to move your files to the new `docs/` standard automatically.
```bash
python -m src.cli.main speckit.migrate --from-structure old
```

## The New Standard
- **Centralized Config**: All settings live in `speckit.yaml`.
- **Strict Frontmatter**: Every feature and spec needs a `code` field.
- **Recursive Discovery**: Deep folder structures are now supported in features and specs.
- **Robust Tasks**: Use `tasks.json` for high-fidelity task definitions.
