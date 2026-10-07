from __future__ import annotations

import math

from airborne_vv.models import AlertSample, AlertState, SoftwareConfig


class AltitudeAlertComputer:
    """Small deterministic software-under-test used by the verification harness."""

    def __init__(self, config: SoftwareConfig) -> None:
        self._config = config

    def evaluate(self, sample: AlertSample) -> AlertState:
        if not self._is_valid(sample):
            return AlertState.INPUT_INVALID

        if sample.warning_inhibit:
            return AlertState.INHIBITED

        disagreement = abs(sample.primary_height_ft - sample.secondary_height_ft)
        if disagreement > self._config.height_disagreement_limit_ft:
            return AlertState.SENSOR_DISAGREE

        sink_threshold = (
            self._config.gear_down_sink_rate_threshold_fpm
            if sample.gear_down
            else self._config.gear_up_sink_rate_threshold_fpm
        )
        average_height = (sample.primary_height_ft + sample.secondary_height_ft) / 2.0
        if (
            average_height < self._config.pull_up_height_threshold_ft
            and sample.vertical_speed_fpm < sink_threshold
        ):
            return AlertState.PULL_UP

        return AlertState.NORMAL

    def _is_valid(self, sample: AlertSample) -> bool:
        numeric_values = (
            sample.primary_height_ft,
            sample.secondary_height_ft,
            sample.vertical_speed_fpm,
        )
        if not all(math.isfinite(value) for value in numeric_values):
            return False

        heights = (sample.primary_height_ft, sample.secondary_height_ft)
        if any(
            value < self._config.minimum_height_ft or value > self._config.maximum_height_ft
            for value in heights
        ):
            return False

        return (
            -self._config.maximum_sink_rate_magnitude_fpm
            <= sample.vertical_speed_fpm
            <= self._config.maximum_sink_rate_magnitude_fpm
        )
