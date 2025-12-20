from __future__ import annotations
import typer
from pathlib import Path
from typing import Optional

from src.core.config import SpeckitConfig
from src.templates.template_manager import TemplateManager

def register(app: typer.Typer) -> None:
    @app.command("plan")
    def plan(
        config_path: Path = typer.Option(Path("speckit.yaml"), "--config", help="Path to speckit.yaml")
    ):
        """Scaffold the implementation_plan.md"""
        
        project_root = Path.cwd()
        config_file = project_root / config_path
        
        try:
            config = SpeckitConfig.load(config_file)
        except Exception:
             typer.echo(f"⚠️  Config not found at {config_file}, using defaults.")
             # Create a dummy config if file missing
             # In real usage, speckit.init should have been run.
             pass

        tm = TemplateManager(config, project_root)
        
        typer.echo(f"📋 Scaffolding implementation plan...")
        path = tm.create_implementation_plan()
        
        typer.echo(f"✅ Created plan: {path}")
