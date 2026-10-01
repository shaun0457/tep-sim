"""Deterministic, versioned process-safety limits and rollout evaluation.

Limits mirror the pinned upstream shutdown (ISD) check in
``tep/python_backend.py``. Pressure and temperature limits are on XMEAS directly;
the level limits are upstream liquid-volume limits (m3) converted to the XMEAS
level percent with the same linear formulas upstream uses to compute XMEAS.

Margins are evaluated on recorded measurements, so they carry the upstream
measurement noise and the telemetry record resolution. Shutdown occurrence comes
from the simulator's own shutdown state, never from a margin.
"""
import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from .capability import CAPABILITY_VERSION, UNSUPPORTED_CONSEQUENCE_DOMAINS
from .contracts import ArtifactRef, RolloutResult
from .errors import InvalidEnvironmentState
from .registry import UPSTREAM_REVISION

SAFETY_LIMITS_VERSION = "tep-sim.safety-limits/v0"
SAFETY_EVALUATION_VERSION = "tep-sim.safety-evaluation/v0"
_FT3_PER_M3 = 35.3145
_SOURCE = f"tep/python_backend.py shutdown check @ {UPSTREAM_REVISION}"


@dataclass(frozen=True)
class SafetyLimit:
    limit_id: str
    variable: str
    direction: str  # "max": unsafe when value > threshold; "min": value < threshold
    threshold: float
    unit: str
    description: str
    source: str = _SOURCE

    def margin(self, value: float) -> float:
        return self.threshold - value if self.direction == "max" else value - self.threshold

    def crossed(self, value: float) -> bool:
        return value > self.threshold if self.direction == "max" else value < self.threshold


def _level(volume_m3, offset_ft3, span_ft3):
    """Upstream XMEAS level % for a liquid volume given in m3."""
    return (volume_m3 * _FT3_PER_M3 - offset_ft3) / span_ft3 * 100.0


SAFETY_LIMITS = (
    SafetyLimit("reactor_pressure_high", "XMEAS(7)", "max", 3000.0, "kPa gauge",
                "reactor pressure above the shutdown limit"),
    SafetyLimit("reactor_temperature_high", "XMEAS(9)", "max", 175.0, "deg C",
                "reactor temperature above the shutdown limit"),
    SafetyLimit("reactor_level_high", "XMEAS(8)", "max", _level(24.0, 84.6, 666.7), "%",
                "reactor liquid volume above 24 m3"),
    SafetyLimit("reactor_level_low", "XMEAS(8)", "min", _level(2.0, 84.6, 666.7), "%",
                "reactor liquid volume below 2 m3"),
    SafetyLimit("separator_level_high", "XMEAS(12)", "max", _level(12.0, 27.5, 290.0), "%",
                "separator liquid volume above 12 m3"),
    SafetyLimit("separator_level_low", "XMEAS(12)", "min", _level(1.0, 27.5, 290.0), "%",
                "separator liquid volume below 1 m3"),
    SafetyLimit("stripper_level_high", "XMEAS(15)", "max", _level(8.0, 78.25, 156.5), "%",
                "stripper liquid volume above 8 m3"),
    SafetyLimit("stripper_level_low", "XMEAS(15)", "min", _level(1.0, 78.25, 156.5), "%",
                "stripper liquid volume below 1 m3"),
)


def safety_margins(measurements: Mapping[str, float]) -> dict[str, float]:
    return {limit.limit_id: limit.margin(measurements[limit.variable])
            for limit in SAFETY_LIMITS}


@dataclass(frozen=True)
class LimitCrossing:
    limit_id: str
    variable: str
    simulation_time: float
    value: float
    threshold: float


@dataclass(frozen=True)
class MinimumMargin:
    limit_id: str
    margin: float
    unit: str
    simulation_time: float
    value: float


@dataclass(frozen=True)
class UnsafeInterval:
    limit_id: str
    start_time: float
    end_time: float
    open_at_end: bool
    extreme_value: float


@dataclass(frozen=True)
class ProcessEvent:
    kind: str
    simulation_time: float
    subject: str


@dataclass(frozen=True)
class SafetyEvaluation:
    evaluation_version: str
    limits_version: str
    capability_version: str
    upstream_revision: str
    telemetry_sha256: str
    record_count: int
    shutdown_occurred: bool
    shutdown_time: float | None
    termination_reason: str
    shutdown_limit_ids: tuple[str, ...]
    limit_crossings: tuple[LimitCrossing, ...]
    minimum_safety_margins: Mapping[str, MinimumMargin]
    unsafe_intervals: tuple[UnsafeInterval, ...]
    relevant_process_events: tuple[ProcessEvent, ...]
    unsupported_consequence_domains: tuple[str, ...] = field(
        default=tuple(UNSUPPORTED_CONSEQUENCE_DOMAINS))

    def __post_init__(self):
        object.__setattr__(self, "minimum_safety_margins",
                           MappingProxyType(dict(self.minimum_safety_margins)))


def _records(artifact: ArtifactRef):
    path = Path(artifact.path)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise InvalidEnvironmentState("telemetry artifact is unreadable") from exc
    if hashlib.sha256(data).hexdigest() != artifact.sha256:
        raise InvalidEnvironmentState("telemetry artifact checksum mismatch")
    records = [json.loads(line) for line in data.decode("utf-8").splitlines() if line]
    if not records:
        raise InvalidEnvironmentState("telemetry artifact has no records")
    for record in records:
        values = [record.get("simulation_time"),
                  *(record.get("measurements", {}).get(l.variable) for l in SAFETY_LIMITS)]
        if not all(type(v) in (int, float) and math.isfinite(v) for v in values):
            raise InvalidEnvironmentState("telemetry record lacks finite safety variables")
    return records


def evaluate_safety(rollout: RolloutResult) -> SafetyEvaluation:
    """Pure function of the rollout's checksummed telemetry and termination reason."""
    if not isinstance(rollout, RolloutResult):
        raise InvalidEnvironmentState("RolloutResult required")
    records = _records(rollout.telemetry)
    crossings, intervals, events = [], [], []
    minima: dict[str, MinimumMargin] = {}
    open_since: dict[str, tuple[float, float]] = {}
    previous_disturbances: set[str] = set(records[0].get("active_disturbances", ()))
    shutdown_time = None
    shutdown_limits: tuple[str, ...] = ()
    for position, record in enumerate(records):
        time = float(record["simulation_time"])
        if position:
            current = set(record.get("active_disturbances", ()))
            events += [ProcessEvent("disturbance_activated", time, d)
                       for d in sorted(current - previous_disturbances)]
            events += [ProcessEvent("disturbance_deactivated", time, d)
                       for d in sorted(previous_disturbances - current)]
            previous_disturbances = current
        for limit in SAFETY_LIMITS:
            value = float(record["measurements"][limit.variable])
            margin = limit.margin(value)
            best = minima.get(limit.limit_id)
            if best is None or margin < best.margin:
                minima[limit.limit_id] = MinimumMargin(limit.limit_id, margin, limit.unit,
                                                       time, value)
            if limit.crossed(value):
                if limit.limit_id not in open_since:
                    open_since[limit.limit_id] = (time, value)
                    crossings.append(LimitCrossing(limit.limit_id, limit.variable, time,
                                                   value, limit.threshold))
                    events.append(ProcessEvent("limit_crossed", time, limit.limit_id))
                else:
                    start, extreme = open_since[limit.limit_id]
                    worse = value > extreme if limit.direction == "max" else value < extreme
                    open_since[limit.limit_id] = (start, value if worse else extreme)
            elif limit.limit_id in open_since:
                start, extreme = open_since.pop(limit.limit_id)
                intervals.append(UnsafeInterval(limit.limit_id, start, time, False, extreme))
                events.append(ProcessEvent("limit_recovered", time, limit.limit_id))
        if record.get("shutdown_state") and shutdown_time is None:
            shutdown_time = time
            shutdown_limits = tuple(l.limit_id for l in SAFETY_LIMITS
                                    if l.crossed(float(record["measurements"][l.variable])))
            events.append(ProcessEvent("shutdown", time, ",".join(shutdown_limits)))
    end = float(records[-1]["simulation_time"])
    for limit in SAFETY_LIMITS:
        if limit.limit_id in open_since:
            start, extreme = open_since[limit.limit_id]
            intervals.append(UnsafeInterval(limit.limit_id, start, end, True, extreme))
    shutdown = shutdown_time is not None
    if (rollout.termination_reason == "shutdown") != shutdown:
        raise InvalidEnvironmentState("termination reason disagrees with recorded shutdown")
    order = {l.limit_id: i for i, l in enumerate(SAFETY_LIMITS)}
    return SafetyEvaluation(
        SAFETY_EVALUATION_VERSION, SAFETY_LIMITS_VERSION, CAPABILITY_VERSION,
        UPSTREAM_REVISION, rollout.telemetry.sha256, len(records), shutdown, shutdown_time,
        rollout.termination_reason, shutdown_limits, tuple(crossings),
        {limit.limit_id: minima[limit.limit_id] for limit in SAFETY_LIMITS},
        tuple(sorted(intervals, key=lambda i: (i.start_time, order[i.limit_id]))),
        tuple(events))
