from __future__ import annotations

import json
from pathlib import Path

import pytest

from airborne_vv.config import (
    ConfigurationError,
    load_cases,
    load_requirements,
    load_software_config,
)
from airborne_vv.models import AlertSample, AlertState, Requirement, VerificationCase
from airborne_vv.traceability import TraceabilityError, validate_traceability

ROOT = Path(__file__).parents[1]


def test_checked_in_configuration_loads() -> None:
    level, config = load_software_config(ROOT / "config/software-config.json")
    requirements = load_requirements(ROOT / "config/requirements.json")
    cases = load_cases(ROOT / "config/verification-cases.json")
    assert level == "C"
    assert config.height_disagreement_limit_ft == 200
    assert len(requirements) == 8
    assert len(cases) == 14
    validate_traceability(requirements, cases)


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"assigned_software_level": "F", "parameters": {}},
        {"assigned_software_level": "C", "parameters": {}},
    ],
)
def test_invalid_software_configuration_is_rejected(tmp_path: Path, payload: object) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_software_config(path)


def test_bad_json_is_reported(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="cannot load"):
        load_requirements(path)


def test_duplicate_requirement_is_rejected() -> None:
    requirement = Requirement("REQ-1", "high", "text", None, "test")
    case = VerificationCase(
        "TC-1", "title", ("REQ-1",), AlertSample(0, 0, 0, False, False), AlertState.NORMAL
    )
    with pytest.raises(TraceabilityError, match="duplicate requirements"):
        validate_traceability((requirement, requirement), (case,))


def test_unknown_requirement_reference_is_rejected() -> None:
    requirement = Requirement("REQ-1", "high", "text", None, "test")
    case = VerificationCase(
        "TC-1", "title", ("REQ-2",), AlertSample(0, 0, 0, False, False), AlertState.NORMAL
    )
    with pytest.raises(TraceabilityError, match="unknown requirements"):
        validate_traceability((requirement,), (case,))


def test_missing_coverage_is_rejected() -> None:
    requirements = (
        Requirement("REQ-1", "high", "text", None, "test"),
        Requirement("REQ-2", "low", "text", "REQ-1", "test"),
    )
    case = VerificationCase(
        "TC-1", "title", ("REQ-1",), AlertSample(0, 0, 0, False, False), AlertState.NORMAL
    )
    with pytest.raises(TraceabilityError, match="without verification cases"):
        validate_traceability(requirements, (case,))
