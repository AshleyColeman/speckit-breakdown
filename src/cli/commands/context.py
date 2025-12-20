from __future__ import annotations
import typer
from pathlib import Path
import json
from typing import Optional

from src.core.config import SpeckitConfig
from src.services.data_store_gateway import DataStoreGateway
from src.models.entities import TaskDTO, FeatureDTO, SpecificationDTO

def register(app: typer.Typer) -> None:
    @app.command("context")
    def context(
        task_code: str = typer.Argument(..., help="Task Code (e.g., TASK-001)"),
        config_path: Path = typer.Option(Path("speckit.yaml"), "--config", help="Path to speckit.yaml"),
        storage_path: Optional[Path] = typer.Option(None, "--storage-path", help="Path to SQLite DB (overrides config)"),
        db_url: Optional[str] = typer.Option(None, "--db-url", help="PostgreSQL Connection String")
    ):
        """
        Generates a detailed markdown context bundle for a given Task.
        This bundle includes:
        - Task Details (Acceptance Criteria, Status)
        - Linked Feature (User Stories, Context)
        - Linked Specification (Technical Specs, APIs)
        
        This output is ideal for feeding into an AI Agent or Automation Workflow (n8n).
        """
        
        project_root = Path.cwd()
        config_file = project_root / config_path
        
        # Load Config
        try:
             config = SpeckitConfig.load(config_file)
        except Exception:
             # If running standalone without config, try default
             config = SpeckitConfig._create_default(config_file)
        
        # Determine Storage Path
        # Config object doesn't have storage_path currently, so we default to .speckit/db.sqlite
        default_storage = project_root / ".speckit/db.sqlite"
        final_storage_path = storage_path if storage_path else default_storage
        
        # Initialize Gateway
        gateway = DataStoreGateway(db_url if db_url else final_storage_path, enable_experimental_postgres=bool(db_url))
        
        # 1. Fetch Task
        task = gateway.get_task(task_code)
        if not task:
            typer.echo(f"❌ Task not found: {task_code}", err=True)
            raise typer.Exit(code=1)
            
        # 2. Fetch Feature
        feature = gateway.get_feature(task.feature_code)
        if not feature:
            typer.echo(f"⚠️  Linked Feature not found: {task.feature_code} (for task {task_code})", err=True)
            # Proceed even if missing?
        
        # 3. Fetch Spec
        # Spec code is usually f01-spec if feature is f01. 
        # But we need to query by feature_code. 
        # SqliteGateway doesn't have get_spec_by_feature. 
        # We can try to guess the spec code or we might need to extend gateway.
        # Standard convention: {feature_code}-spec
        spec_code = f"{task.feature_code}-spec"
        spec = gateway.get_spec(spec_code)
        
        if not spec:
            # Fallback: maybe spec code is different? 
            typer.echo(f"⚠️  Linked Spec not found: {spec_code} (for task {task_code})", err=True)
        
        # 4. Assemble Context Markdown
        markdown = []
        
        markdown.append(f"# Task Context: {task.code}")
        markdown.append(f"**Title**: {task.title}")
        markdown.append(f"**Type**: {task.task_type}")
        markdown.append(f"**Status**: {task.status}")
        markdown.append("")
        
        markdown.append("## Task Acceptance Criteria")
        markdown.append(task.acceptance)
        markdown.append("")
        
        if feature:
            markdown.append("---")
            markdown.append(f"# Linked Feature: {feature.name} ({feature.code})")
            # Pull content from file if possible, or use DB metadata if stored detailed
            # In DB we store description.
            markdown.append(feature.description)
            markdown.append("")
            
            # If we want the FULL file content, we should read it from disk if path available?
            # FeatureDTO doesn't have path. But SpecDTO has path.
            # We can infer path from config.
            
        if spec:
            markdown.append("---")
            markdown.append(f"# Linked Specification: {spec.title}")
            
            # Try to read the actual spec file content for maximum detail
            if spec.path: 
                # Try multiple path resolutions
                possible_paths = [
                    project_root / spec.path,
                    project_root / "docs" / spec.path,
                    project_root / "docs/specs" / Path(spec.path).name 
                ]
                
                content = None
                found_path = None
                
                for p in possible_paths:
                    if p.exists():
                        content = p.read_text(encoding="utf-8")
                        found_path = p
                        break
                
                if content:
                    markdown.append(content)
                else:
                    markdown.append(f"> ⚠️ Spec file missing. Tried: {[str(p) for p in possible_paths]}")
            else:
                 markdown.append("> ⚠️ No path recorded for spec")

        # Output to stdout
        typer.echo("\n".join(markdown))
