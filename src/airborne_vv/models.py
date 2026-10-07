from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class AlertState(StrEnum):
    NORMAL = "NORMAL"
    PULL_UP = "PULL_UP"
    SENSOR_DISAGREE = "SENSOR_DISAGREE"
    INHIBITED = "INHIBITED"
    INPUT_INVALID = "INPUT_INVALID"


@dataclass(frozen=True)
class SoftwareConfig:
    minimum_height_ft: float
    maximum_height_ft: float
    maximum_sink_rate_magnitude_fpm: float
    height_disagreement_limit_ft: float
    pull_up_height_threshold_ft: float
    gear_up_sink_rate_threshold_fpm: float
    gear_down_sink_rate_threshold_fpm: float


@dataclass(frozen=True)
class AlertSample:
    primary_height_ft: float
    secondary_height_ft: float
    vertical_speed_fpm: float
    gear_down: bool
    warning_inhibit: bool


@dataclass(frozen=True)
class Requirement:
    requirement_id: str
    level: str
    text: str
    parent_id: str | None
    verification_method: str


@dataclass(frozen=True)
class VerificationCase:
    case_id: str
    title: str
    requirement_ids: tuple[str, ...]
    sample: AlertSample
    expected_state: AlertState


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    title: str
    requirement_ids: tuple[str, ...]
    expected_state: AlertState
    actual_state: AlertState

    @property
    def passed(self) -> bool:
        return self.expected_state == self.actual_state

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["expected_state"] = self.expected_state.value
        data["actual_state"] = self.actual_state.value
        data["passed"] = self.passed
        return data


@dataclass(frozen=True)
class CampaignResult:
    software_level: str
    results: tuple[CaseResult, ...]
    requirement_ids: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return all(result.passed for result in self.results)

    @property
    def covered_requirement_ids(self) -> tuple[str, ...]:
        return tuple(sorted({item for result in self.results for item in result.requirement_ids}))

    @property
    def coverage_percent(self) -> float:
        if not self.requirement_ids:
            return 100.0
        return round(100.0 * len(self.covered_requirement_ids) / len(self.requirement_ids), 2)
