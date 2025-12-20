from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class ValidationError:
    code: str
    message: str
    file_path: Optional[Path] = None
    suggestion: Optional[str] = None
    auto_fixable: bool = False

class ValidationRule:
    """Base class for all validation rules"""
    
    def validate(self) -> List[ValidationError]:
        """Run validation logic"""
        raise NotImplementedError
        
    def auto_fix(self) -> None:
        """Attempt to fix issues"""
        pass
