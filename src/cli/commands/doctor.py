from __future__ import annotations
import typer
import sys
from pathlib import Path
from typing import List

def register(app: typer.Typer) -> None:
    @app.command("doctor")
    def doctor(
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Detailed system information")
    ):
        """Check system health and provide diagnostics"""
        
        typer.echo("🏥 SpecKit System Health Check")
        typer.echo("=" * 40)
        
        issues = []
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 11):
            issues.append("Python 3.11+ required (found: {}.{}.{})".format(
                python_version.major, python_version.minor, python_version.micro
            ))
        else:
            typer.echo("✅ Python version: {}.{}.{}".format(
                python_version.major, python_version.minor, python_version.micro
            ))
        
        # Check required packages
        try:
            import yaml
            typer.echo("✅ PyYAML available")
        except ImportError:
            issues.append("PyYAML not installed")
        
        # Check project structure
        project_root = Path.cwd()
        config_file = project_root / 'speckit.yaml'
        
        if config_file.exists():
            typer.echo("✅ Configuration file found")
            
            try:
                from src.core.config import SpeckitConfig
                config = SpeckitConfig.load(config_file)
                typer.echo(f"✅ Configuration valid for project: {config.project.get('name')}")
            except Exception as e:
                issues.append(f"Configuration error: {e}")
        else:
            issues.append("No speckit.yaml found - run 'speckit.init'")
        
        # Check directories
        required_dirs = ['docs/features', 'docs/specs', 'docs/tasks']
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            if full_path.exists():
                typer.echo(f"✅ Directory exists: {dir_path}")
            else:
                issues.append(f"Missing directory: {dir_path}")
        
        # Summary
        typer.echo("\n📊 Summary")
        if issues:
            typer.echo(f"❌ Found {len(issues)} issues:")
            for issue in issues:
                typer.echo(f"   • {issue}")
            
            typer.echo("\n💡 Suggestions:")
            typer.echo("   • Run 'speckit.init' to set up a new project")
            typer.echo("   • Run 'speckit.validate' to check structure")
            typer.echo("   • Run 'speckit.migrate' to fix structure issues")
        else:
            typer.echo("✅ No issues found!")
        
        if verbose:
            typer.echo("\n🔧 Detailed Information")
            typer.echo(f"   Working directory: {project_root}")
            typer.echo(f"   Config file: {config_file}")
            typer.echo(f"   Python path: {sys.executable}")
