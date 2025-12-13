import pytest

from src.services.parser.spec_parser import SpecificationParser


@pytest.fixture
def specs_dir(tmp_path):
    specs = tmp_path / "specs"
    specs.mkdir()

    spec_dir = specs / "001-user-auth"
    spec_dir.mkdir()

    spec_file = spec_dir / "spec.md"
    spec_file.write_text(
        """# User authentication

## Overview
Some text.
""",
        encoding="utf-8",
    )

    return specs


def test_spec_parser_extracts_feature_code_from_numbered_dir(specs_dir):
    parser = SpecificationParser(specs_dir)
    specs = parser.parse()

    assert len(specs) == 1
    spec = specs[0]

    assert spec.code == "spec"
    assert spec.feature_code == "user-auth"
    assert spec.title == "User authentication"
    assert spec.path.endswith("specs/001-user-auth/spec.md")
