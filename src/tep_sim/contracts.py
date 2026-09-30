"""Immutable, agent-independent environment contracts; time is in hours."""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


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


class SnapshotFidelity(str, Enum):
    EXACT = "exact"
    RECONSTRUCTED = "reconstructed"
    UNSUPPORTED = "unsupported"


class BranchRandomnessPolicy(str, Enum):
    CLONED_STATE = "cloned_state"


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    """Copy a shallow JSON-like mapping before exposing it publicly."""
    return MappingProxyType(dict(value))


@dataclass(frozen=True)
class Snapshot:
    snapshot_id: str
    parent_run_id: str
    source_branch_id: str
    simulation_time: float
    source_step_count: int
    environment_version: str
    upstream_revision: str
    random_state_metadata: Mapping[str, Any]
    state_format_version: str
    state: ArtifactRef
    checksum: str
    fidelity: SnapshotFidelity
    config: EnvironmentConfig
    metadata: ArtifactRef

    def __post_init__(self):
        object.__setattr__(self, "random_state_metadata",
                           _freeze_mapping(self.random_state_metadata))


@dataclass(frozen=True)
class Branch:
    branch_id: str
    parent_snapshot_id: str
    random_state_policy: BranchRandomnessPolicy
    created_at: str
    intervention_schedule: tuple[Mapping[str, Any], ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "intervention_schedule",
                           tuple(_freeze_mapping(item)
                                 for item in self.intervention_schedule))


@dataclass(frozen=True)
class ReplaySpec:
    source_run_id: str
    source_branch_id: str
    snapshot: Snapshot
    config: EnvironmentConfig
    intervention_schedule: tuple[Mapping[str, Any], ...]
    target_simulation_time: float
    target_step_count: int
    random_state_policy: BranchRandomnessPolicy
    expected_observation_sha256: str

    def __post_init__(self):
        object.__setattr__(self, "intervention_schedule",
                           tuple(_freeze_mapping(item)
                                 for item in self.intervention_schedule))
