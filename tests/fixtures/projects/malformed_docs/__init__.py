"""
Helper to create a project with malformed docs.
"""
from pathlib import Path

def create_malformed_project(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    
    (root / "project.md").write_text("---\nid: MAL-001\nname: Malformed Project\n---\n")
    (root / "features").mkdir()
    (root / "features" / "feat.md").write_text("---\nid: FEAT-1\nproject_id: MAL-001\ntitle: Feature 1\n---\n")
    (root / "specs").mkdir()
    (root / "specs" / "spec.md").write_text("---\nid: SPEC-1\nfeature_id: FEAT-1\ntitle: Spec 1\n---\n")
    
    (root / "tasks").mkdir()
    # Task with TODO title
    (root / "tasks" / "t1.md").write_text("---\nid: T-1\nspec_id: SPEC-1\ntitle: TODO: Update this\n---\n# TODO: Update this\nValid description here.")
    # Task with short description
    (root / "tasks" / "t2.md").write_text("---\nid: T-2\nspec_id: SPEC-1\ntitle: Task 2\n---\n# Task 2\nTBD\n")
    
    (root / "dependencies").mkdir()

