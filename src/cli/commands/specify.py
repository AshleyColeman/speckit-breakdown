from __future__ import annotations
import typer
from pathlib import Path
from typing import Optional

from src.core.config import SpeckitConfig
from src.templates.template_manager import TemplateManager

def register(app: typer.Typer) -> None:
    @app.command("specify")
    def specify(
        feature_code: str = typer.Argument(..., help="Feature code (e.g. f01)"),
        feature_name: str = typer.Option("New Feature", "--name", "-n", help="Feature name (if new)"),
        config_path: Path = typer.Option(Path("speckit.yaml"), "--config", help="Path to speckit.yaml")
    ):
        """Generates a corresponding spec file in docs/specs/<feature_code>-spec.md"""
        
        project_root = Path.cwd()
        config_file = project_root / config_path
        
        if not config_file.exists():
             # Basic config loading if not present? Or fail?
             # For robustness, we load default if missing or let it fail?
             # Init command loads default. Here we assume project exists.
             pass

        try:
            config = SpeckitConfig.load(config_file)
        except Exception:
             # Fallback if running outside of initialized project but that's unlikely
             typer.echo(f"⚠️  Config not found at {config_file}, using defaults.")
             config = SpeckitConfig._create_default(config_file) # Don't rewrite file though?
             # Actually, just load default config object without file
             # But TemplateManager needs config.
             pass

        tm = TemplateManager(config, project_root)
        
        typer.echo(f"🔨 Creating spec for {feature_code}...")
        path = tm.create_spec_file(feature_code, feature_name)
        
        typer.echo(f"✅ Created spec: {path}")
