import pytest

from src.models.entities import FeatureDTO, ProjectDTO, SpecificationDTO, TaskDTO, TaskDependencyDTO
from src.services.validation.rules import (
    DuplicateEntityRule,
    InvalidDependencyReferenceRule,
    ReferentialIntegrityRule,
    RequiredFieldsRule,
)
from src.services.validation_pipeline import Severity


def test_required_fields_rule_flags_blank_project_code():
    project = ProjectDTO(code="", name="Name", description="")
    rule = RequiredFieldsRule(project, [], [], [])
    issues = list(rule.run())

    assert any(i.severity == Severity.CRITICAL and "Project code" in i.message for i in issues)


def test_referential_integrity_rule_flags_missing_feature_reference():
    project = ProjectDTO(code="P1", name="Name", description="")
    specs = [SpecificationDTO(code="S1", feature_code="missing", title="Spec", path="spec.md")]

    rule = ReferentialIntegrityRule(project, features=[], specs=specs, tasks=[])
    issues = list(rule.run())

    assert any(i.severity == Severity.ERROR and "references missing feature" in i.message for i in issues)


def test_invalid_dependency_reference_rule_reports_unknown_task_codes():
    invalid = [TaskDependencyDTO(task_code="T1", depends_on="T999")]
    rule = InvalidDependencyReferenceRule(invalid)

    issues = list(rule.run())

    assert len(issues) == 1
    assert issues[0].severity == Severity.ERROR
    assert "unknown task" in issues[0].message.lower()


def test_duplicate_entity_rule_reports_duplicate_task_codes_case_insensitive():
    project = ProjectDTO(code="P1", name="Name", description="")
    feature = FeatureDTO(code="feat", project_code="P1", name="Feature", description="", priority="P1")
    spec = SpecificationDTO(code="spec", feature_code="feat", title="Spec", path="spec.md")

    tasks = [
        TaskDTO(code="T1", feature_code="feat", title="Task", status="pending", task_type="impl", acceptance=""),
        TaskDTO(code="t1", feature_code="feat", title="Task dup", status="pending", task_type="impl", acceptance=""),
    ]

    rule = DuplicateEntityRule([project], [feature], [spec], tasks)
    issues = list(rule.run())

    assert any(i.severity == Severity.ERROR and "Duplicate Task Code" in i.message for i in issues)
