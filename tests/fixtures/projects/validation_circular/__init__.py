"""
Helper to create a project with circular task dependencies.
"""
from pathlib import Path

def create_circular_project(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    
    # Basic structure
    (root / "project.md").write_text("---\nid: CIRC-001\nname: Circular Project\n---\n")
    (root / "features").mkdir()
    (root / "features" / "feat.md").write_text("---\nid: FEAT-1\nproject_id: CIRC-001\ntitle: Feature 1\n---\n")
    (root / "specs").mkdir()
    (root / "specs" / "spec.md").write_text("---\nid: SPEC-1\nfeature_id: FEAT-1\ntitle: Spec 1\n---\n")
    
    # Tasks with cycle: T-1 -> T-2 -> T-1
    (root / "tasks").mkdir()
    (root / "tasks" / "t1.md").write_text("---\nid: T-1\nspec_id: SPEC-1\ntitle: Task 1\n---\nDepends on: t2\n")
    (root / "tasks" / "t2.md").write_text("---\nid: T-2\nspec_id: SPEC-1\ntitle: Task 2\n---\nDepends on: t1\n")
    
    (root / "dependencies").mkdir()
