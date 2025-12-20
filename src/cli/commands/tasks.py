from __future__ import annotations
import typer
from pathlib import Path
import re
import json
import logging
from typing import List, Dict, Any

from src.core.config import SpeckitConfig

logger = logging.getLogger(__name__)

def register(app: typer.Typer) -> None:
    @app.command("tasks")
    def tasks(
        plan_file: Path = typer.Argument(Path("docs/implementation_plan.md"), help="Path to implementation_plan.md"),
        output_file: Path = typer.Option(Path("docs/tasks/tasks.json"), "--output", "-o", help="Output tasks.json path"),
        config_path: Path = typer.Option(Path("speckit.yaml"), "--config", help="Path to speckit.yaml")
    ):
        """Scaffold tasks from implementation_plan.md"""
        
        if not plan_file.exists():
            typer.echo(f"❌ Implementation plan not found: {plan_file}", err=True)
            raise typer.Exit(code=1)
            
        typer.echo(f"🔨 Scaffolding tasks from {plan_file.name}...")
        
        content = plan_file.read_text(encoding='utf-8')
        
        # Simple parser for implementation_plan.md
        # Looking for ## Phase X: ... and then numbered lists
        
        tasks = []
        current_phase = ""
        current_feature = ""
        
        lines = content.split('\n')
        task_counter = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Phase match
            phase_match = re.match(r'^##\s+(Phase\s+\d+:\s+.*)$', line)
            if phase_match:
                current_phase = phase_match.group(1)
                # Try to extract feature code if present in phase title, e.g. (f01) or (FEAT-01)
                feat_match = re.search(r'\(([\w-]+)\)', current_phase)
                if feat_match:
                    current_feature = feat_match.group(1).lower()
                else:
                    current_feature = "general"
                continue
            
            # Task match (numbered list)
            task_match = re.match(r'^(\d+)\.\s+(.*)$', line)
            if task_match:
                task_title = task_match.group(2)
                task_code = f"TASK-{task_counter:03d}"
                
                tasks.append({
                    "code": task_code,
                    "feature_code": current_feature,
                    "title": task_title,
                    "status": "pending",
                    "task_type": "implementation",
                    "acceptance": f"Completed: {task_title}",
                    "metadata": {
                        "phase": current_phase,
                        "dependencies": [],
                        "estimated_hours": 4,
                        "priority": "medium"
                    }
                })
                task_counter += 1
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2)
            
        typer.echo(f"✅ Generated {len(tasks)} tasks in {output_file}")
