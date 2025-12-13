"""
Helper to create a project with duplicate IDs.
"""
from pathlib import Path

def create_duplicate_project(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    
    # Basic structure
    (root / "project.md").write_text("---\nid: DUP-001\n---\n\n# Duplicate Project\n")
    (root / "features").mkdir()
    (root / "features" / "feat.md").write_text("""---
project_id: DUP-001
priority: P1
---

# Feature 1
""")
    (root / "specs").mkdir()
    (root / "specs" / "001-feat").mkdir(parents=True)
    (root / "specs" / "001-feat" / "spec.md").write_text("""---
feature_code: feat
---

# Spec 1
""")
    
    # Task with SAME CODE via filename collision in numbered dirs
    (root / "tasks" / "01-feat").mkdir(parents=True)
    (root / "tasks" / "02-feat").mkdir()
    (root / "tasks" / "01-feat" / "t1.md").write_text("""# T1 Task 1
""")
    (root / "tasks" / "02-feat" / "t1.md").write_text("""# T1 Task 1 Copy
""")
    
    (root / "dependencies").mkdir()
