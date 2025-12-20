from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from src.core.config import SpeckitConfig
from src.parsing.feature_parser import FeatureParser
from src.parsing.spec_parser import SpecificationParser  
from src.parsing.task_parser import TaskParser
from src.validation.validator import ProjectValidator

logger = logging.getLogger(__name__)

@dataclass
class ParseResult:
    features: List[Dict[str, Any]]
    specs: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    validation_result: Any  # ValidationResult

class UnifiedParser:
    """Single, clear parsing strategy with zero ambiguity"""
    
    def __init__(self, config: SpeckitConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
        
        # Initialize sub-parsers
        self.feature_parser = FeatureParser(config, project_root)
        self.spec_parser = SpecificationParser(config, project_root)
        self.task_parser = TaskParser(config, project_root)
        
        # Initialize validator
        self.validator = ProjectValidator(config, project_root)
    
    def parse(self) -> ParseResult:
        """Parse all project files with comprehensive validation"""
        
        # Step 1: Validate structure first
        logger.info("Validating project structure...")
        validation_result = self.validator.validate()
        
        if validation_result.has_blocking_errors():
            raise ValueError(
                "Project structure validation failed. "
                "Run 'speckit validate' for details."
            )
        
        # Step 2: Parse with clear strategy
        logger.info("Parsing features...")
        features = self.feature_parser.parse()
        
        logger.info("Parsing specifications...")
        specs = self.spec_parser.parse()
        
        logger.info("Parsing tasks...")
        tasks = self.task_parser.parse()
        
        # Step 3: Cross-validate relationships
        logger.info("Validating cross-file relationships...")
        self._validate_relationships(features, specs, tasks)
        
        return ParseResult(
            features=features,
            specs=specs,
            tasks=tasks,
            validation_result=validation_result
        )
    
    def _validate_relationships(
        self, 
        features: List[Dict], 
        specs: List[Dict], 
        tasks: List[Dict]
    ) -> None:
        """Validate relationships between parsed entities"""
        
        # Check that all specs have corresponding features
        feature_codes = {f.get('code') for f in features}
        spec_feature_codes = {s.get('feature_code') for s in specs if s.get('feature_code')}
        
        missing_features = spec_feature_codes - feature_codes
        if missing_features:
            raise ValueError(
                f"Specifications reference non-existent features: {missing_features}"
            )
        
        # Check that all tasks have corresponding features
        task_feature_codes = {t.get('feature_code') for t in tasks if t.get('feature_code')}
        missing_task_features = task_feature_codes - feature_codes
        if missing_task_features:
            raise ValueError(
                f"Tasks reference non-existent features: {missing_task_features}"
            )
