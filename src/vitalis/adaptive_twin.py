"""Causal streaming deviation estimator for the VITALIS research prototype.

This module detects within-person deviation patterns; it does not diagnose,
produce clinical probabilities, or forecast a validated time to deterioration.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from statistics import median
from typing import Mapping, Sequence

DEFAULT_CHANNEL_SYSTEMS = {
    "heart_rate": "cardiovascular", "hrv": "cardiovascular",
    "systolic_bp": "cardiovascular", "diastolic_bp": "cardiovascular",
    "spo2": "oxygenation", "respiratory_rate": "respiratory",
    "temperature": "temperature", "peripheral_temperature": "perfusion",
    "capillary_refill_seconds": "perfusion",
}


@dataclass(frozen=True)
class TwinConfig:
    """Research parameters, not clinically selected thresholds."""
    min_history: int = 5
    history_window: int = 48
    min_channels: int = 2
    min_systems: int = 2
    min_coverage: float = 0.5
    z_clip: float = 4.0
    ewma_alpha: float = 0.35
    deviation_z: float = 2.5
    high_deviation_z: float = 3.5
    persistence_steps: int = 3
    baseline_update_z_limit: float = 2.5
    scale_floor: float = 1e-3
    cusum_allowance: float = 0.5
    cusum_threshold: float = 5.0

    def __post_init__(self):
        if self.min_history < 2 or self.history_window < self.min_history:
            raise ValueError("history_window must be >= min_history >= 2")
        if self.min_channels < 1 or self.min_systems < 1:
            raise ValueError("minimum channel/system counts must be positive")
        if not 0 < self.min_coverage <= 1:
            raise ValueError("min_coverage must be in (0, 1]")
        if not 0 < self.ewma_alpha <= 1:
            raise ValueError("ewma_alpha must be in (0, 1]")
        if self.z_clip <= 0 or self.scale_floor <= 0:
            raise ValueError("z_clip and scale_floor must be positive")
        if self.persistence_steps < 1:
            raise ValueError("persistence_steps must be positive")
        if not 0 < self.deviation_z <= self.high_deviation_z <= self.z_clip:
            raise ValueError("deviation thresholds must be positive, ordered, and <= z_clip")
        if self.cusum_allowance < 0 or self.cusum_threshold <= 0:
            raise ValueError("CUSUM allowance must be non-negative and threshold positive")


@dataclass
class ChannelState:
    values: list[float] = field(default_factory=list)
    reference_center: float | None = None
    reference_scale: float | None = None
    cusum_positive: float = 0.0
    cusum_negative: float = 0.0
    consecutive_deviations: int = 0


class AdaptivePhysiologicalTwin:
    """Online robust baselines, reference-shift detection and multisystem trajectory.

    The current observation is scored before baseline updates. A robust reference
    is frozen after the first minimum-history window while a rolling baseline
    adapts. Two-sided CUSUM on the frozen reference helps expose gradual drift
    that the rolling baseline could otherwise absorb. Large deviations are
    withheld from the rolling baseline. The initial reference may itself be
    abnormal, and long-term recovery/re-baselining requires an explicit reset.
    """

    def __init__(
        self,
        channels: Sequence[str] | None = None,
        *,
        channel_systems: Mapping[str, str] | None = None,
        scale_floors: Mapping[str, float] | None = None,
        config: TwinConfig | None = None,
    ):
        self.config = config or TwinConfig()
        systems = dict(DEFAULT_CHANNEL_SYSTEMS)
        systems.update(channel_systems or {})
        self.channels = tuple(channels or systems.keys())
        if not self.channels or len(set(self.channels)) != len(self.channels):
            raise ValueError("channels must be non-empty and unique")
        unknown = set(self.channels).difference(systems)
        if unknown:
            raise ValueError("Provide channel_systems for: " + ", ".join(sorted(unknown)))
        self.channel_systems = {key: systems[key] for key in self.channels}
        self.scale_floors = {key: self.config.scale_floor for key in self.channels}
        for name, floor in (scale_floors or {}).items():
            if name not in self.scale_floors:
                raise ValueError(f"Scale floor supplied for unknown channel: {name}")
            if not isfinite(float(floor)) or float(floor) <= 0:
                raise ValueError(f"Scale floor for {name} must be finite and positive")
            self.scale_floors[name] = float(floor)
        self.states = {key: ChannelState() for key in self.channels}
        self.steps = 0
        self._trajectory_score: float | None = None

    def _reference(self, history: list[float], channel: str) -> tuple[float, float]:
        center = median(history)
        mad = median([abs(x - center) for x in history])
        return center, max(1.4826 * mad, self.scale_floors[channel])

    def update(self, observations: Mapping[str, float | int | None]) -> dict[str, object]:
        """Return a unitless deviation summary for one synchronized time step."""
        self.steps += 1
        valid: dict[str, float] = {}
        for name in self.channels:
            raw = observations.get(name)
            if raw is None:
                continue
            try:
                value = float(raw)
            except (TypeError, ValueError):
                continue
            if isfinite(value):
                valid[name] = value

        # Missing/non-finite observations break a channel's persistence streak.
        for name in set(self.channels).difference(valid):
            self.states[name].consecutive_deviations = 0

        coverage = len(valid) / len(self.channels)
        channel_results: dict[str, dict[str, object]] = {}
        system_values: dict[str, list[float]] = {}
        scored = 0

        for name, value in valid.items():
            state = self.states[name]
            baseline = z_score = reference_z = None
            cusum_triggered = False
            if len(state.values) >= self.config.min_history:
                baseline, adaptive_scale = self._reference(state.values, name)
                if state.reference_center is None:
                    state.reference_center, state.reference_scale = baseline, adaptive_scale
                z_score = (value - baseline) / adaptive_scale
                reference_z = (
                    (value - state.reference_center) / state.reference_scale
                    if state.reference_center is not None and state.reference_scale is not None
                    else z_score
                )
                state.cusum_positive = max(
                    0.0, state.cusum_positive + reference_z - self.config.cusum_allowance
                )
                state.cusum_negative = max(
                    0.0, state.cusum_negative - reference_z - self.config.cusum_allowance
                )
                cusum_score = max(state.cusum_positive, state.cusum_negative)
                cusum_triggered = cusum_score >= self.config.cusum_threshold
                effective_z = max(abs(z_score), abs(reference_z))
                magnitude = min(effective_z, self.config.z_clip) / self.config.z_clip
                system_values.setdefault(self.channel_systems[name], []).append(magnitude)
                state.consecutive_deviations = (
                    state.consecutive_deviations + 1
                    if effective_z >= self.config.deviation_z else 0
                )
                scored += 1
            else:
                cusum_score = max(state.cusum_positive, state.cusum_negative)

            channel_results[name] = {
                "value": value,
                "baseline": baseline,
                "reference_baseline": state.reference_center,
                "z_score": z_score,
                "reference_z_score": reference_z,
                "cusum_score": cusum_score,
                "cusum_triggered": cusum_triggered,
                "history_count": len(state.values),
                "baseline_updated": False,
            }
            # Score first; do not absorb a large deviation or a detected cumulative shift.
            if (
                z_score is None
                or (abs(z_score) <= self.config.baseline_update_z_limit and not cusum_triggered)
            ):
                state.values.append(value)
                if len(state.values) > self.config.history_window:
                    state.values.pop(0)
                if state.reference_center is None and len(state.values) >= self.config.min_history:
                    state.reference_center, state.reference_scale = self._reference(state.values, name)
                channel_results[name]["baseline_updated"] = True

        system_scores = {
            system: sum(values) / len(values)
            for system, values in system_values.items() if values
        }
        eligible = (
            coverage >= self.config.min_coverage
            and scored >= self.config.min_channels
            and len(system_scores) >= self.config.min_systems
        )
        trajectory_score = concordance = trajectory_delta = None
        trajectory_direction = None
        persistent_channels = cumulative_shift_channels = cumulative_shift_systems = 0
        if eligible:
            instantaneous = sum(system_scores.values()) / len(system_scores)
            previous_score = self._trajectory_score
            trajectory_score = (
                instantaneous if previous_score is None else
                self.config.ewma_alpha * instantaneous
                + (1 - self.config.ewma_alpha) * previous_score
            )
            if previous_score is not None:
                trajectory_delta = trajectory_score - previous_score
                if trajectory_delta > 0.02:
                    trajectory_direction = "rising"
                elif trajectory_delta < -0.02:
                    trajectory_direction = "falling"
                else:
                    trajectory_direction = "stable"
            self._trajectory_score = trajectory_score
            concordance = sum(
                score >= self.config.deviation_z / self.config.z_clip
                for score in system_scores.values()
            ) / len(system_scores)
            persistent_channels = sum(
                state.consecutive_deviations >= self.config.persistence_steps
                for state in self.states.values()
            )
            cumulative_shift_channels = sum(
                max(state.cusum_positive, state.cusum_negative) >= self.config.cusum_threshold
                for state in self.states.values()
            )
            cumulative_shift_systems = len({
                self.channel_systems[name] for name, state in self.states.items()
                if max(state.cusum_positive, state.cusum_negative) >= self.config.cusum_threshold
            })

        if not eligible:
            label = "insufficient_data"
        elif persistent_channels >= self.config.min_channels and (concordance or 0) >= 0.5:
            label = "persistent_multisystem_deviation"
        elif cumulative_shift_channels >= self.config.min_channels and cumulative_shift_systems >= self.config.min_systems:
            label = "cumulative_multisystem_shift"
        elif cumulative_shift_channels:
            label = "cumulative_shift_detected"
        elif (trajectory_score or 0) >= self.config.high_deviation_z / self.config.z_clip:
            label = "marked_deviation"
        elif (trajectory_score or 0) >= self.config.deviation_z / self.config.z_clip:
            label = "deviation_detected"
        else:
            label = "within_person_range"

        return {
            "step": self.steps, "state": label, "coverage": coverage,
            "eligible": eligible, "trajectory_score": trajectory_score,
            "trajectory_delta": trajectory_delta, "trajectory_direction": trajectory_direction,
            "score_semantics": "unitless heuristic; not a probability or clinical risk",
            "cross_system_concordance": concordance, "system_scores": system_scores,
            "persistent_channels": persistent_channels,
            "cumulative_shift_channels": cumulative_shift_channels,
            "cumulative_shift_systems": cumulative_shift_systems,
            "channels": channel_results, "clinical_recommendation": None,
            "warning": "Research-only deviation detection; not for patient-care decisions.",
        }

    def reset_channel(self, channel: str) -> None:
        """Clear one channel's history after a known sensor/source replacement."""
        if channel not in self.states:
            raise ValueError(f"Unknown channel: {channel}")
        self.states[channel] = ChannelState()
        # A changed input stream invalidates continuity of the aggregate trajectory.
        self._trajectory_score = None

    def reset(self) -> None:
        """Clear patient-specific state before processing a different patient."""
        self.states = {key: ChannelState() for key in self.channels}
        self.steps = 0
        self._trajectory_score = None
