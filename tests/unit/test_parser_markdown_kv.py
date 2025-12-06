
import pytest
from pathlib import Path
from src.services.parser.feature_parser import FeatureParser

@pytest.fixture
def feature_file_markdown_kv(tmp_path):
    f = tmp_path / "feature-login.md"
    f.write_text("""# Feature: User Login

**Priority**: P1
**Business Value**: 10/10
**Dependencies**: None
**Project Code**: PROJ-001

## Description
This is a description.
""", encoding="utf-8")
    return f

def test_feature_parser_markdown_kv(feature_file_markdown_kv, tmp_path):
    parser = FeatureParser(tmp_path, "DEFAULT")
    feature = parser._parse_feature_file(feature_file_markdown_kv)
    
    assert feature.code == "feature-login"
    # These assertions are expected to fail before the fix
    assert feature.priority == "P1"
    assert feature.project_code == "PROJ-001"
    assert feature.metadata.get("Business Value") == "10/10"
