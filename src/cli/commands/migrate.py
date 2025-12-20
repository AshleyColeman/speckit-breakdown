from __future__ import annotations
import typer
from pathlib import Path
from typing import List, Optional

from src.migration.migrator import ProjectMigrator

def register(app: typer.Typer) -> None:
    @app.command("speckit.migrate")
    def migrate(
        from_structure: str = typer.Option(..., "--from-structure", help="Current structure type (old|nested|flat)"),
        to_structure: str = typer.Option("standard", "--to-structure", help="Target structure type"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without executing"),
        backup: bool = typer.Option(False, "--backup", help="Create backup before migration")
    ):
        """Migrate project from one structure to another"""
        
        project_root = Path.cwd()
        
        try:
            migrator = ProjectMigrator(project_root)
            
            if dry_run:
                changes = migrator.plan_migration(from_structure, to_structure)
                typer.echo("🔍 Migration Plan (Dry Run)")
                typer.echo("=" * 40)
                for change in changes:
                    typer.echo(f"• {change}")
                return
            
            if backup:
                backup_path = migrator.create_backup()
                typer.echo(f"📦 Created backup: {backup_path}")
            
            typer.echo(f"🔄 Migrating from {from_structure} to {to_structure}...")
            changes = migrator.execute_migration(from_structure, to_structure)
            
            typer.echo("✅ Migration completed!")
            typer.echo(f"   Files moved: {len(changes)}")
            
        except Exception as e:
            typer.echo(f"❌ Migration failed: {e}", err=True)
            raise typer.Exit(code=1)
