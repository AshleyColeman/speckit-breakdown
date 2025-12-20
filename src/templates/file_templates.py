from __future__ import annotations
from typing import Dict, Any
from pathlib import Path

class FileTemplates:
    """Standardized templates for all file types"""
    
    @staticmethod
    def project_template(project_code: str, project_name: str) -> str:
        return f"""---
code: {project_code}
name: "{project_name}"
type: project
status: active
---

# Project: {project_name}

[Enter high-level project description here]
"""

    @staticmethod
    def feature_template(feature_code: str, feature_name: str) -> str:
        return f"""---
code: {feature_code}
project_code: {{{{project_code}}}}
name: {feature_name}
description: [Description of what this feature delivers]
priority: P2
---

# Feature: {feature_name}

[Detailed description of the feature, including user stories and acceptance criteria.]

## User Stories
- **US1**: As a [user type], I want [feature] so that [benefit].

## Acceptance Criteria
- **AC1**: [Given/When/Then format]
- **AC2**: [Given/When/Then format]

## Technical Notes
[Any technical implementation notes or constraints]
"""

    @staticmethod
    def spec_template(feature_code: str, feature_name: str) -> str:
        return f"""---
code: {feature_code}-spec
feature_code: {feature_code}
title: "Specification: {feature_name}"
---

# Specification: {feature_name}

## 1. Overview
[Brief overview of what this specification defines.]

## 2. User Stories
[List user stories from the feature, expanded with details.]

## 3. Functional Requirements
- **FR1**: [Functional requirement in testable format]
- **FR2**: [Functional requirement in testable format]

## 4. Non-Functional Requirements
- **NFR1**: [Performance, security, or other NFRs]
- **NFR2**: [Performance, security, or other NFRs]

## 5. Technical Constraints
[Any technical constraints or dependencies]

## 6. Success Criteria
[How to determine if this specification is successfully implemented]
"""

    @staticmethod
    def tasks_template() -> str:
        return """[
  {
    "code": "FEATURE-T001",
    "feature_code": "feature-code",
    "title": "Task title",
    "status": "pending",
    "task_type": "implementation",
    "acceptance": "Clear acceptance criteria",
    "metadata": {
      "dependencies": [],
      "estimated_hours": 8,
      "priority": "high"
    }
  }
]"""
