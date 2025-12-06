from pathlib import Path

def create_scoped_project(root: Path):
    """
    Creates a workspace with two distinct projects (P-A and P-B) 
    to test filtering logic.
    """
    root.mkdir(parents=True, exist_ok=True)
    
    # Project A (Main)
    (root / "project.md").write_text("---\nid: P-A\nname: Project A\n---\n")
    # Features (Flat)
    (root / "features").mkdir(parents=True)
    (root / "features" / "feat-a.md").write_text("---\nid: F-A\nproject_id: P-A\ntitle: Feature A\n---\n")
    (root / "features" / "feat-b.md").write_text("---\nid: F-B\nproject_id: P-B\ntitle: Feature B\n---\n")

    # Specs (Numbered)
    (root / "specs" / "01").mkdir(parents=True)
    (root / "specs" / "01" / "spec.md").write_text("---\nid: S-A\nfeature_id: F-A\ntitle: Spec A\n---\n")
    (root / "specs" / "02").mkdir(parents=True)
    (root / "specs" / "02" / "spec.md").write_text("---\nid: S-B\nfeature_id: F-B\ntitle: Spec B\n---\n")

    # Tasks (Numbered)
    (root / "tasks" / "01").mkdir(parents=True)
    (root / "tasks" / "01" / "task.md").write_text("---\nid: T-A\nspec_id: S-A\ntitle: Task A\n---\n# Task A\nDescription A.")
    (root / "tasks" / "02").mkdir(parents=True)
    (root / "tasks" / "02" / "task.md").write_text("---\nid: T-B\nspec_id: S-B\ntitle: Task B\n---\n# Task B\nDescription B.")
    
    (root / "dependencies").mkdir()
