from __future__ import annotations
import shutil
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import yaml
import logging

from src.parsing.base_parser import MarkdownParser

logger = logging.getLogger(__name__)

class ProjectMigrator:
    """Migrates project structure to the standard format"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.parser = MarkdownParser(project_root)
        
    def plan_migration(self, from_structure: str, to_structure: str) -> List[str]:
        """Plan moves without executing"""
        moves = self._calculate_moves(from_structure)
        plan = []
        for src, dst in moves:
            plan.append(f"MOVE: {src.relative_to(self.project_root)} -> {dst.relative_to(self.project_root)}")
        return plan
        
    def execute_migration(self, from_structure: str, to_structure: str) -> List[Path]:
        """Execute migration moves"""
        moves = self._calculate_moves(from_structure)
        executed_moves = []
        
        for src, dst in moves:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                shutil.move(str(src), str(dst))
                executed_moves.append(dst)
                logger.info(f"Moved {src} to {dst}")
            else:
                logger.warning(f"Destination already exists, skipping: {dst}")
                
        return executed_moves
        
    def create_backup(self) -> Path:
        backup_dir = self.project_root.parent / f"{self.project_root.name}_backup"
        if backup_dir.exists():
             shutil.rmtree(backup_dir)
        shutil.copytree(self.project_root, backup_dir)
        return backup_dir

    def _calculate_moves(self, from_structure: str) -> List[Tuple[Path, Path]]:
        """Calculate necessary moves based on structure type"""
        moves = []
        
        # Target paths (Standard structure)
        features_dst = self.project_root / "docs/features"
        specs_dst = self.project_root / "docs/specs"
        tasks_dst = self.project_root / "docs/tasks"
        
        # 1. Find all markdown files recursively
        all_md_files = list(self.project_root.rglob("*.md"))
        
        for file_path in all_md_files:
            # Skip files already in docs/
            if "docs/" in str(file_path.relative_to(self.project_root)):
                continue
                
            data = self.parser.parse_file(file_path)
            if not data:
                continue
                
            # Identify if it's a feature or spec
            if 'feature_code' in data or file_path.name.endswith("-spec.md"):
                # It's a spec
                moves.append((file_path, specs_dst / file_path.name))
            elif 'code' in data:
                # It's a feature
                moves.append((file_path, features_dst / file_path.name))
                
        # 2. Find tasks.json
        tasks_json = list(self.project_root.rglob("tasks.json"))
        for file_path in tasks_json:
            if "docs/" in str(file_path.relative_to(self.project_root)):
                continue
            moves.append((file_path, tasks_dst / "tasks.json"))
            
        return moves
