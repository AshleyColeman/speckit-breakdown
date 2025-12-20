from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional
import typer

from src.core.config import SpeckitConfig
from src.validation.validator import ProjectValidator
from src.validation.error_formatter import ErrorFormatter

logger = logging.getLogger(__name__)

def register(app: typer.Typer) -> None:
    @app.command("speckit.validate")
    def validate(
        strict: bool = typer.Option(False, "--strict", help="Treat warnings as errors"),
        fix: bool = typer.Option(False, "--fix", help="Auto-fix fixable issues"),
        explain: bool = typer.Option(False, "--explain", help="Show detailed explanations"),
        config_path: Path = typer.Option(Path("speckit.yaml"), "--config-path", help="Path to config file")
    ):
        """Validate project structure and files"""
        
        project_root = Path.cwd()
        config_file = project_root / config_path
        
        try:
            # Load configuration
            config = SpeckitConfig.load(config_file)
            
            # Create validator
            validator = ProjectValidator(config, project_root)
            
            # Auto-fix if requested
            if fix:
                typer.echo("🔧 Auto-fixing issues...")
                result = validator.auto_fix()
            else:
                result = validator.validate(strict=strict)
            
            # Format and display results
            formatter = ErrorFormatter()
            output = formatter.format_validation_result(result)
            typer.echo(output)
            
            # Exit with appropriate code
            if result.has_blocking_errors():
                raise typer.Exit(code=1)
            elif strict and len(result.warnings) > 0:
                raise typer.Exit(code=1)
            else:
                raise typer.Exit(code=0)
                
        except Exception as e:
            typer.echo(f"❌ Validation failed: {e}", err=True)
            raise typer.Exit(code=1)
