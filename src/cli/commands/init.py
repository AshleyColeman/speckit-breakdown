from __future__ import annotations
import click # Still useful for some prompts if needed, but typer.prompt is preferred
import typer
from pathlib import Path
from typing import Optional
import yaml

from src.core.config import SpeckitConfig
from src.templates.template_manager import TemplateManager
from src.validation.validator import ProjectValidator

def register(app: typer.Typer) -> None:
    @app.command("init")
    def init(
        interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive setup"),
        project_name: Optional[str] = typer.Option(None, "--project-name", help="Project name"),
        structure: str = typer.Option("standard", "--structure", help="Project structure type"),
        create_examples: bool = typer.Option(True, "--create-examples", help="Create example files")
    ):
        """Initialize SpecKit in a project"""
        
        project_root = Path.cwd()
        
        try:
            if interactive:
                project_name = typer.prompt("Project name", default=project_name or "my-project")
                structure = typer.prompt("Choose project structure", 
                                       default=structure,
                                       show_choices=True)
                create_examples = typer.confirm("Create example files?", default=create_examples)
                validate_now = typer.confirm("Validate setup after creation?", default=True)
            else:
                project_name = project_name or "my-project"
                validate_now = True
            
            # Create configuration
            config_path = project_root / 'speckit.yaml'
            config = SpeckitConfig._create_default(config_path)
            
            # Update config with user choices
            config.project['name'] = project_name
            config.project['structure'] = structure
            
            # Save updated config
            with open(config_path, 'w') as f:
                yaml.dump({
                    'project': config.project,
                    'directories': config.directories.__dict__,
                    'naming': config.naming.__dict__,
                    'validation': config.validation.__dict__
                }, f, default_flow_style=False)
            
            # Create directories
            for dir_name, dir_path in config.directories.__dict__.items():
                (project_root / dir_path).mkdir(parents=True, exist_ok=True)
            
            # Create example files if requested
            template_manager = TemplateManager(config, project_root)
            
            # ALWAYS create project.md as it is required by the core system
            template_manager.create_project_file(
                config.project['name'].lower().replace(' ', '-'),
                config.project['name']
            )

            if create_examples:
                
                # Create example feature
                template_manager.create_feature_file(
                    'example-feature', 
                    'Example Feature'
                )
                
                # Create example spec
                template_manager.create_spec_file(
                    'example-feature',
                    'Example Feature'
                )
                
                # Create tasks file
                template_manager.create_tasks_file()
            
            typer.echo("✅ Project configured successfully!")
            typer.echo(f"   Project: {project_name}")
            typer.echo(f"   Structure: {structure}")
            typer.echo(f"   Config: speckit.yaml")
            
            if create_examples:
                typer.echo("   Example files created in docs/")
            
            if validate_now:
                typer.echo("\n🔍 Validating setup...")
                validator = ProjectValidator(config, project_root)
                result = validator.validate()
                
                if result.is_valid:
                    typer.echo("✅ Setup is valid!")
                else:
                    typer.echo("⚠️  Setup has issues. Run 'speckit validate' for details.")
            
            typer.echo("\n🚀 Next steps:")
            typer.echo("   1. Review and update docs/features/")
            typer.echo("   2. Run 'speckit validate' to check structure")
            typer.echo("   3. Run 'speckit.db.prepare' when ready")
            
        except Exception as e:
            typer.echo(f"❌ Setup failed: {e}", err=True)
            raise typer.Exit(code=1)
