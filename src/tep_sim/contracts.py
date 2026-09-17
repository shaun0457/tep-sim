"""Immutable, agent-independent environment contracts; time is in hours."""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Mapping


class ControlMode(str, Enum):
    CLOSED_LOOP = "closed_loop"
    MANUAL = "manual"
    OPEN_LOOP = "open_loop"


@dataclass(frozen=True)
class EnvironmentConfig:
    seed: int
    backend: str
    control_mode: ControlMode
    record_interval: int
    upstream_revision: str
    artifact_directory: Path = Path("artifacts")


@dataclass(frozen=True)
class Observation:
    simulation_time: float
    measurements: Mapping[str, float]
    manipulated_variables: Mapping[str, float]
    active_disturbances: tuple[str, ...]
    shutdown_state: bool
    safety_margins: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self):
        for name in ("measurements", "manipulated_variables", "safety_margins"):
            object.__setattr__(self, name, MappingProxyType(dict(getattr(self, name))))
        object.__setattr__(self, "active_disturbances", tuple(self.active_disturbances))


@dataclass(frozen=True)
class DisturbanceIntervention:
    target: str
    value: int


@dataclass(frozen=True)
class MVIntervention:
    target: str
    value: float


@dataclass(frozen=True)
class MVConstraint:
    target: str
    min_value: float | None = None
    max_value: float | None = None


@dataclass(frozen=True)
class EnvironmentEvent:
    kind: str
    simulation_time: float
    detail: str = ""


@dataclass(frozen=True)
class StepResult:
    observation: Observation
    events: tuple[EnvironmentEvent, ...] = ()


@dataclass(frozen=True)
class ArtifactRef:
    path: str
    sha256: str


@dataclass(frozen=True)
class RolloutResult:
    observation: Observation
    telemetry: ArtifactRef
    provenance: ArtifactRef
    termination_reason: str
