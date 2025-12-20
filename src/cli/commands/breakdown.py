from __future__ import annotations
import typer
from pathlib import Path
from typing import Optional, List, Dict
import re
import yaml

from src.core.config import SpeckitConfig
from src.templates.template_manager import TemplateManager

def register(app: typer.Typer) -> None:
    @app.command("speckit.breakdown")
    def breakdown(
        mvp_file: Path = typer.Argument(..., help="Path to MVP.md file"),
        output_dir: Path = typer.Option(Path.cwd(), "--output-dir", "-o", help="Output directory"),
        project_name: str = typer.Option("my-project", "--project-name", "-n", help="Project name")
    ):
        """Break down an MVP.md file into SpecKit features and specs"""
        
        if not mvp_file.exists():
            typer.echo(f"❌ MVP file not found: {mvp_file}", err=True)
            raise typer.Exit(code=1)
            
        typer.echo(f"🔨 Breaking down {mvp_file.name}...")
        
        # 1. Load context
        config_path = output_dir / 'speckit.yaml'
        if not config_path.exists():
            SpeckitConfig._create_default(config_path)
        config = SpeckitConfig.load(config_path)
        tm = TemplateManager(config, output_dir)
        
        content = mvp_file.read_text(encoding='utf-8')
        
        # 2. Extract features (Simple Heading-based extraction)
        # Assuming ## Feature: Name format
        feature_matches = list(re.finditer(r'^## (?:Feature|Requirement):\s*(.*)$', content, re.MULTILINE))
        
        if not feature_matches:
             # Try simpler ## Heading format if no "Feature" keyword
             feature_matches = list(re.finditer(r'^##\s*(?!User Stories|Acceptance Criteria|Technical)(.*)$', content, re.MULTILINE))

        typer.echo(f"📝 Found {len(feature_matches)} features.")
        
        # 1. Ensure project.md exists (Required for db.prepare)
        # Assuming output_dir is the project root for now
        docs_dir = output_dir / config.directories.features
        if docs_dir.name == 'features': # If features is a subdirectory of docs, get the parent
            docs_dir = docs_dir.parent
            
        project_file = docs_dir / "project.md"
        # Use the project_name from config, falling back to the CLI option, then default
        project_code = config.project.get('name', project_name).lower().replace(' ', '-')
        if not project_file.exists():
            typer.echo(f"   • Creating project.md (required for sync)")
            tm.create_project_file(project_code, config.project.get('name', project_name))

        # 2. Extract and create features
        for i, match in enumerate(feature_matches):
            feature_name = match.group(1).strip()
            # Standardized Lowercase Codes
            feature_code = f"f{i+1:02d}"
            
            typer.echo(f"   • Creating Feature: {feature_code} ({feature_name})")
            tm.create_feature_file(feature_code, feature_name)
            
            # Create spec
            tm.create_spec_file(feature_code, feature_name)
            
        # 3. Create tasks.json summary
        tm.create_tasks_file()
        # Optional: update project-breakdown.md summary
        
        typer.echo(f"\n✅ Breakdown complete!")
        typer.echo(f"   Files generated in: {docs_dir}")
        
        # Self-normalization loop to ensure everything is lowercase
        # (Already handled in template manager, but good for robustness)
        typer.echo("\nNext steps:")
        typer.echo("   1. Review the generated files in docs/features")
        typer.echo("   2. Run 'speckit validate' to verify")
        typer.echo("   3. Run 'speckit.db.prepare' to sync")
