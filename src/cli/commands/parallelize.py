from __future__ import annotations
import typer
from pathlib import Path
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def register(app: typer.Typer) -> None:
    @app.command("parallelize")
    def parallelize(
        tasks_file: Path = typer.Argument(Path("docs/tasks/tasks.json"), help="Path to tasks.json"),
        config_path: Path = typer.Option(Path("speckit.yaml"), "--config", help="Path to speckit.yaml")
    ):
        """Identify parallel tasks in tasks.json"""
        
        if not tasks_file.exists():
            typer.echo(f"❌ Tasks file not found: {tasks_file}", err=True)
            raise typer.Exit(code=1)
            
        typer.echo(f"🚀 Identifying parallel tasks in {tasks_file.name}...")
        
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
            
        # Group tasks by their dependencies
        dep_groups: Dict[str, List[str]] = {}
        
        for task in tasks:
            deps = sorted(task.get('metadata', {}).get('dependencies', []))
            dep_key = ",".join(deps) if deps else "none"
            
            if dep_key not in dep_groups:
                dep_groups[dep_key] = []
            dep_groups[dep_key].append(task['code'])
            
        parallel_count = 0
        for dep_key, task_codes in dep_groups.items():
            if len(task_codes) > 1:
                typer.echo(f"   • Parallel Group (deps: {dep_key}): {', '.join(task_codes)}")
                parallel_count += 1
                
                # Mark tasks as parallel in metadata
                for task in tasks:
                    if task['code'] in task_codes:
                        if 'metadata' not in task:
                            task['metadata'] = {}
                        task['metadata']['parallel_group'] = dep_key
        
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2)
            
        typer.echo(f"✅ Identified {parallel_count} parallel groups.")
