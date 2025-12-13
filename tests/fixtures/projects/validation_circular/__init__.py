"""
Helper to create a project with circular task dependencies.
"""
from pathlib import Path

def create_circular_project(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    
    # Basic structure
    (root / "project.md").write_text("---\nid: CIRC-001\n---\n\n# Circular Project\n")
    (root / "features").mkdir()
    (root / "features" / "feat.md").write_text("""---
project_id: CIRC-001
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
    
    # Tasks with cycle: T-1 -> T-2 -> T-1
    (root / "tasks").mkdir()
    (root / "tasks" / "001-feat").mkdir(parents=True)
    (root / "tasks" / "001-feat" / "t1.md").write_text("""# T1 Task 1

Depends on: T2
""")
    (root / "tasks" / "001-feat" / "t2.md").write_text("""# T2 Task 2

Depends on: T1
""")
    
    (root / "dependencies").mkdir()
