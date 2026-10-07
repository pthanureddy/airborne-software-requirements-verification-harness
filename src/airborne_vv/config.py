from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from airborne_vv.models import (
    AlertSample,
    AlertState,
    Requirement,
    SoftwareConfig,
    VerificationCase,
)


class ConfigurationError(ValueError):
    pass


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"cannot load {path}: {exc}") from exc


def _require_keys(record: dict[str, Any], expected: set[str], context: str) -> None:
    actual = set(record)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ConfigurationError(f"{context}: missing={missing}, extra={extra}")


def load_software_config(path: Path) -> tuple[str, SoftwareConfig]:
    raw = _load_json(path)
    if not isinstance(raw, dict):
        raise ConfigurationError("software configuration must be an object")
    expected = {"assigned_software_level", "parameters"}
    _require_keys(raw, expected, "software configuration")
    level = raw["assigned_software_level"]
    if level not in {"A", "B", "C", "D", "E"}:
        raise ConfigurationError("assigned_software_level must be A, B, C, D, or E")
    parameters = raw["parameters"]
    if not isinstance(parameters, dict):
        raise ConfigurationError("parameters must be an object")
    names = {
        "minimum_height_ft",
        "maximum_height_ft",
        "maximum_sink_rate_magnitude_fpm",
        "height_disagreement_limit_ft",
        "pull_up_height_threshold_ft",
        "gear_up_sink_rate_threshold_fpm",
        "gear_down_sink_rate_threshold_fpm",
    }
    _require_keys(parameters, names, "parameters")
    try:
        config = SoftwareConfig(**{name: float(parameters[name]) for name in names})
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f"parameters must be numeric: {exc}") from exc
    if config.minimum_height_ft >= config.maximum_height_ft:
        raise ConfigurationError("minimum_height_ft must be lower than maximum_height_ft")
    if config.maximum_sink_rate_magnitude_fpm <= 0:
        raise ConfigurationError("maximum sink-rate magnitude must be positive")
    return str(level), config


def load_requirements(path: Path) -> tuple[Requirement, ...]:
    raw = _load_json(path)
    if not isinstance(raw, list):
        raise ConfigurationError("requirements must be a list")
    requirements: list[Requirement] = []
    expected = {"id", "level", "text", "parent_id", "verification_method"}
    for index, record in enumerate(raw):
        if not isinstance(record, dict):
            raise ConfigurationError(f"requirement {index} must be an object")
        _require_keys(record, expected, f"requirement {index}")
        requirements.append(
            Requirement(
                requirement_id=str(record["id"]),
                level=str(record["level"]),
                text=str(record["text"]),
                parent_id=None if record["parent_id"] is None else str(record["parent_id"]),
                verification_method=str(record["verification_method"]),
            )
        )
    return tuple(requirements)


def load_cases(path: Path) -> tuple[VerificationCase, ...]:
    raw = _load_json(path)
    if not isinstance(raw, list):
        raise ConfigurationError("verification cases must be a list")
    cases: list[VerificationCase] = []
    case_keys = {"id", "title", "requirement_ids", "input", "expected_state"}
    sample_keys = {
        "primary_height_ft",
        "secondary_height_ft",
        "vertical_speed_fpm",
        "gear_down",
        "warning_inhibit",
    }
    for index, record in enumerate(raw):
        if not isinstance(record, dict):
            raise ConfigurationError(f"case {index} must be an object")
        _require_keys(record, case_keys, f"case {index}")
        sample = record["input"]
        if not isinstance(sample, dict):
            raise ConfigurationError(f"case {index} input must be an object")
        _require_keys(sample, sample_keys, f"case {index} input")
        if type(sample["gear_down"]) is not bool or type(sample["warning_inhibit"]) is not bool:
            raise ConfigurationError(f"case {index} flags must be booleans")
        refs = record["requirement_ids"]
        if not isinstance(refs, list) or not refs:
            raise ConfigurationError(f"case {index} requires at least one requirement id")
        try:
            expected_state = AlertState(str(record["expected_state"]))
            alert_sample = AlertSample(
                primary_height_ft=float(sample["primary_height_ft"]),
                secondary_height_ft=float(sample["secondary_height_ft"]),
                vertical_speed_fpm=float(sample["vertical_speed_fpm"]),
                gear_down=sample["gear_down"],
                warning_inhibit=sample["warning_inhibit"],
            )
        except (TypeError, ValueError) as exc:
            raise ConfigurationError(f"case {index} contains an invalid value: {exc}") from exc
        cases.append(
            VerificationCase(
                case_id=str(record["id"]),
                title=str(record["title"]),
                requirement_ids=tuple(str(item) for item in refs),
                sample=alert_sample,
                expected_state=expected_state,
            )
        )
    return tuple(cases)
