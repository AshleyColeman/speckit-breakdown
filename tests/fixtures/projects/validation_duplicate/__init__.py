"""
Helper to create a project with duplicate IDs.
"""
from pathlib import Path

def create_duplicate_project(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    
    # Basic structure
    (root / "project.md").write_text("---\nid: DUP-001\nname: Duplicate Project\n---\n")
    (root / "features").mkdir()
    (root / "features" / "feat.md").write_text("---\nid: FEAT-1\nproject_id: DUP-001\ntitle: Feature 1\n---\n")
    (root / "specs").mkdir()
    (root / "specs" / "spec.md").write_text("---\nid: SPEC-1\nfeature_id: FEAT-1\ntitle: Spec 1\n---\n")
    
    # Task with SAME CODE via filename collision in numbered dirs
    (root / "tasks" / "01").mkdir(parents=True)
    (root / "tasks" / "02").mkdir()
    (root / "tasks" / "01" / "t1.md").write_text("---\nid: T-1\nspec_id: SPEC-1\ntitle: Task 1\n---\n")
    (root / "tasks" / "02" / "t1.md").write_text("---\nid: T-1-DUP\nspec_id: SPEC-1\ntitle: Task 1 Copy\n---\n")
    
    (root / "dependencies").mkdir()
