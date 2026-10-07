from __future__ import annotations

import math

import pytest

from airborne_vv.models import AlertSample, AlertState, SoftwareConfig
from airborne_vv.sut import AltitudeAlertComputer


@pytest.fixture
def computer() -> AltitudeAlertComputer:
    return AltitudeAlertComputer(
        SoftwareConfig(
            minimum_height_ft=0,
            maximum_height_ft=2500,
            maximum_sink_rate_magnitude_fpm=10000,
            height_disagreement_limit_ft=200,
            pull_up_height_threshold_ft=500,
            gear_up_sink_rate_threshold_fpm=-1000,
            gear_down_sink_rate_threshold_fpm=-700,
        )
    )


@pytest.mark.parametrize("bad_value", [math.nan, math.inf, -math.inf])
@pytest.mark.parametrize(
    "field", ["primary_height_ft", "secondary_height_ft", "vertical_speed_fpm"]
)
def test_non_finite_input_is_invalid(
    computer: AltitudeAlertComputer, field: str, bad_value: float
) -> None:
    values: dict[str, float | bool] = {
        "primary_height_ft": 100.0,
        "secondary_height_ft": 100.0,
        "vertical_speed_fpm": 0.0,
        "gear_down": False,
        "warning_inhibit": False,
    }
    values[field] = bad_value
    sample = AlertSample(**values)  # type: ignore[arg-type]
    assert computer.evaluate(sample) == AlertState.INPUT_INVALID


@pytest.mark.parametrize(
    ("sample", "expected"),
    [
        (AlertSample(1000, 1000, 0, False, False), AlertState.NORMAL),
        (AlertSample(300, 300, -1100, False, False), AlertState.PULL_UP),
        (AlertSample(300, 300, -800, True, False), AlertState.PULL_UP),
        (AlertSample(300, 300, -1100, False, True), AlertState.INHIBITED),
        (AlertSample(600, 801, 0, False, False), AlertState.SENSOR_DISAGREE),
        (AlertSample(600, 800, 0, False, False), AlertState.NORMAL),
        (AlertSample(500, 500, -1100, False, False), AlertState.NORMAL),
        (AlertSample(300, 300, -1000, False, False), AlertState.NORMAL),
        (AlertSample(-1, 0, 0, False, False), AlertState.INPUT_INVALID),
        (AlertSample(2501, 2500, 0, False, False), AlertState.INPUT_INVALID),
        (AlertSample(1000, 1000, 10001, False, False), AlertState.INPUT_INVALID),
        (AlertSample(1000, 1000, -10001, False, False), AlertState.INPUT_INVALID),
    ],
)
def test_alert_decisions(
    computer: AltitudeAlertComputer, sample: AlertSample, expected: AlertState
) -> None:
    assert computer.evaluate(sample) == expected
