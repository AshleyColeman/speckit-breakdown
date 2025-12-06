from pathlib import Path
import shutil

SOURCE_DIR = Path(__file__).parent

def create_full_project(target_dir: Path):
    """Copies the full_project fixture to the target directory."""
    # Copy all files from this directory to target_dir
    # Exclude __init__.py and __pycache__
    
    # We must ensure target_dir exists or let copytree create it?
    # copytree requires destination to NOT exist usually, unless dirs_exist_ok=True (Python 3.8+)
    
    shutil.copytree(
        SOURCE_DIR, 
        target_dir, 
        dirs_exist_ok=True, 
        ignore=shutil.ignore_patterns("__init__.py", "__pycache__")
    )
