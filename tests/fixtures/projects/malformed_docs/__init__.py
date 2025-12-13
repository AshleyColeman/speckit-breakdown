"""
Helper to create a project with malformed docs.
"""
from pathlib import Path

def create_malformed_project(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    
    (root / "project.md").write_text("---\nid: MAL-001\n---\n\n# Malformed Project\n")
    (root / "features").mkdir()
    (root / "features" / "feat.md").write_text("""---
project_id: MAL-001
priority: P2
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
    
    (root / "tasks").mkdir()
    # Task with TODO title
    (root / "tasks" / "001-feat").mkdir(parents=True)
    (root / "tasks" / "001-feat" / "t1.md").write_text(
        """# T1 TODO: Update this

Valid description here.
"""
    )
    # Task with short description
    (root / "tasks" / "001-feat" / "t2.md").write_text(
        """# T2 Task 2

TBD
"""
    )
    
    (root / "dependencies").mkdir()

