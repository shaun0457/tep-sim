"""Trusted local snapshot artifacts and portable replay metadata."""
from __future__ import annotations

import hashlib
import json
import pickle
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .contracts import (ArtifactRef, BranchRandomnessPolicy, ControlMode,
                        EnvironmentConfig, ReplaySpec, Snapshot,
                        SnapshotFidelity)
from .errors import SnapshotFailure
from .registry import UPSTREAM_REVISION


ENVIRONMENT_VERSION = "0.1.0"
STATE_FORMAT_VERSION = "tep-python-pickle-v1"
RANDOMNESS_POLICY = BranchRandomnessPolicy.CLONED_STATE


def artifact_ref(path: Path) -> ArtifactRef:
    path = path.resolve()
    return ArtifactRef(str(path), hashlib.sha256(path.read_bytes()).hexdigest())


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def canonical_json_bytes(data: Mapping[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def config_to_data(config: EnvironmentConfig) -> dict[str, Any]:
    data = asdict(config)
    data["control_mode"] = config.control_mode.value
    data["artifact_directory"] = str(Path(config.artifact_directory).resolve())
    return data


def config_from_data(data: Mapping[str, Any]) -> EnvironmentConfig:
    try:
        return EnvironmentConfig(
            seed=data["seed"],
            backend=data["backend"],
            control_mode=ControlMode(data["control_mode"]),
            record_interval=data["record_interval"],
            upstream_revision=data["upstream_revision"],
            artifact_directory=Path(data["artifact_directory"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise SnapshotFailure("invalid persisted environment config") from exc


def _snapshot_to_data(snapshot: Snapshot) -> dict[str, Any]:
    return {
        "snapshot_id": snapshot.snapshot_id,
        "parent_run_id": snapshot.parent_run_id,
        "source_branch_id": snapshot.source_branch_id,
        "simulation_time": snapshot.simulation_time,
        "source_step_count": snapshot.source_step_count,
        "environment_version": snapshot.environment_version,
        "upstream_revision": snapshot.upstream_revision,
        "random_state_metadata": dict(snapshot.random_state_metadata),
        "state_format_version": snapshot.state_format_version,
        "state": asdict(snapshot.state),
        "checksum": snapshot.checksum,
        "fidelity": snapshot.fidelity.value,
        "config": config_to_data(snapshot.config),
    }


def _snapshot_from_data(data: Mapping[str, Any], metadata: ArtifactRef) -> Snapshot:
    try:
        state = ArtifactRef(**data["state"])
        snapshot = Snapshot(
            snapshot_id=data["snapshot_id"],
            parent_run_id=data["parent_run_id"],
            source_branch_id=data["source_branch_id"],
            simulation_time=data["simulation_time"],
            source_step_count=data["source_step_count"],
            environment_version=data["environment_version"],
            upstream_revision=data["upstream_revision"],
            random_state_metadata=data["random_state_metadata"],
            state_format_version=data["state_format_version"],
            state=state,
            checksum=data["checksum"],
            fidelity=SnapshotFidelity(data["fidelity"]),
            config=config_from_data(data["config"]),
            metadata=metadata,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise SnapshotFailure("invalid snapshot metadata") from exc
    if snapshot.checksum != snapshot.state.sha256:
        raise SnapshotFailure("snapshot checksum and state artifact disagree")
    return snapshot


def create_snapshot_artifacts(environment, snapshot_id: str) -> Snapshot:
    """Serialize the complete supported simulator state without advancing it."""
    try:
        process = environment._sim.process
        rng_state = int(process._g)
        payload = {
            "state_format_version": STATE_FORMAT_VERSION,
            "environment_version": ENVIRONMENT_VERSION,
            "upstream_revision": UPSTREAM_REVISION,
            "simulation_time": environment._sim.time,
            "step_count": environment._sim.step_count,
            "simulator": environment._sim,
            "constraints": dict(environment._constraints),
            "terminated": environment._terminated,
        }
        encoded = pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as exc:
        raise SnapshotFailure(
            "the pinned Python simulator state could not be serialized exactly"
        ) from exc

    directory = environment._directory / "snapshots"
    state_path = directory / f"{snapshot_id}.pickle"
    metadata_path = directory / f"{snapshot_id}.json"
    if state_path.exists() or metadata_path.exists():
        raise SnapshotFailure(f"snapshot already exists: {snapshot_id}")
    try:
        atomic_write(state_path, encoded)
        state = artifact_ref(state_path)
        config = replace(
            environment.config,
            artifact_directory=Path(environment.config.artifact_directory).resolve(),
        )
        provisional = Snapshot(
            snapshot_id=snapshot_id,
            parent_run_id=environment.run_id,
            source_branch_id=environment.branch_id,
            simulation_time=float(environment._sim.time),
            source_step_count=int(environment._sim.step_count),
            environment_version=ENVIRONMENT_VERSION,
            upstream_revision=UPSTREAM_REVISION,
            random_state_metadata={
                "algorithm": "upstream_lcg_mod_2_32",
                "state": rng_state,
                "seed": environment.config.seed,
                "fork_policy": RANDOMNESS_POLICY.value,
            },
            state_format_version=STATE_FORMAT_VERSION,
            state=state,
            checksum=state.sha256,
            fidelity=SnapshotFidelity.EXACT,
            config=config,
            metadata=ArtifactRef(str(metadata_path.resolve()), ""),
        )
        atomic_write(metadata_path, canonical_json_bytes(_snapshot_to_data(provisional)))
        return replace(provisional, metadata=artifact_ref(metadata_path))
    except SnapshotFailure:
        raise
    except Exception as exc:
        raise SnapshotFailure("failed to persist snapshot artifacts") from exc


def load_snapshot(source: str | Path | ArtifactRef) -> Snapshot:
    expected = source.sha256 if isinstance(source, ArtifactRef) else None
    path = Path(source.path if isinstance(source, ArtifactRef) else source).resolve()
    try:
        metadata = artifact_ref(path)
        if expected is not None and metadata.sha256 != expected:
            raise SnapshotFailure("snapshot metadata checksum mismatch")
        data = json.loads(path.read_text(encoding="utf-8"))
    except SnapshotFailure:
        raise
    except Exception as exc:
        raise SnapshotFailure("failed to load snapshot metadata") from exc
    return _snapshot_from_data(data, metadata)


def _safe_identifier(value: str, name: str) -> str:
    if (type(value) is not str or not value
            or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
                   for char in value)):
        raise SnapshotFailure(f"invalid {name} in snapshot metadata")
    return value


def load_snapshot_payload(snapshot: Snapshot,
                          trusted_artifact_root: str | Path) -> dict[str, Any]:
    if snapshot.fidelity is not SnapshotFidelity.EXACT:
        raise SnapshotFailure(f"unsupported snapshot fidelity: {snapshot.fidelity.value}")
    if snapshot.environment_version != ENVIRONMENT_VERSION:
        raise SnapshotFailure("snapshot environment version is unsupported")
    if snapshot.upstream_revision != UPSTREAM_REVISION:
        raise SnapshotFailure("snapshot upstream revision is unsupported")
    if snapshot.state_format_version != STATE_FORMAT_VERSION:
        raise SnapshotFailure("snapshot state format is unsupported")

    snapshot_id = _safe_identifier(snapshot.snapshot_id, "snapshot_id")
    run_id = _safe_identifier(snapshot.parent_run_id, "parent_run_id")
    branch_id = _safe_identifier(snapshot.source_branch_id, "source_branch_id")
    trusted_root = Path(trusted_artifact_root).resolve()
    run_root = (trusted_root / run_id).resolve()
    try:
        run_root.relative_to(trusted_root)
    except ValueError as exc:
        raise SnapshotFailure("snapshot run is outside the trusted artifact root") from exc
    source_root = (run_root if branch_id == "root" else
                   run_root / "branches" / branch_id)
    snapshot_root = source_root / "snapshots"
    expected_state_path = (snapshot_root / f"{snapshot_id}.pickle").resolve()
    expected_metadata_path = (snapshot_root / f"{snapshot_id}.json").resolve()
    state_path = Path(snapshot.state.path).resolve()
    metadata_path = Path(snapshot.metadata.path).resolve()
    if state_path != expected_state_path or metadata_path != expected_metadata_path:
        raise SnapshotFailure("snapshot artifacts are outside the trusted source location")
    try:
        metadata = artifact_ref(metadata_path)
        if metadata.sha256 != snapshot.metadata.sha256:
            raise SnapshotFailure("snapshot metadata checksum mismatch")
        persisted = _snapshot_from_data(
            json.loads(metadata_path.read_text(encoding="utf-8")), metadata
        )
        if persisted != snapshot:
            raise SnapshotFailure("snapshot object differs from persisted metadata")
        state = artifact_ref(state_path)
        if state.sha256 != snapshot.state.sha256 or state.sha256 != snapshot.checksum:
            raise SnapshotFailure("snapshot state checksum mismatch")
        payload = pickle.loads(state_path.read_bytes())
    except SnapshotFailure:
        raise
    except Exception as exc:
        raise SnapshotFailure("failed to load exact snapshot state") from exc

    if not isinstance(payload, dict):
        raise SnapshotFailure("invalid snapshot state payload")
    expected = {
        "state_format_version": snapshot.state_format_version,
        "environment_version": snapshot.environment_version,
        "upstream_revision": snapshot.upstream_revision,
        "simulation_time": snapshot.simulation_time,
        "step_count": snapshot.source_step_count,
    }
    if any(payload.get(key) != value for key, value in expected.items()):
        raise SnapshotFailure("snapshot payload does not match its metadata")
    simulator = payload.get("simulator")
    process = getattr(simulator, "process", None)
    if (getattr(simulator, "backend", None) != "python"
            or int(getattr(process, "_g", -1))
            != snapshot.random_state_metadata.get("state")):
        raise SnapshotFailure("snapshot simulator or random state is invalid")
    return payload


def observation_sha256(observation) -> str:
    data = {
        "simulation_time": observation.simulation_time,
        "measurements": dict(observation.measurements),
        "manipulated_variables": dict(observation.manipulated_variables),
        "active_disturbances": list(observation.active_disturbances),
        "shutdown_state": observation.shutdown_state,
        "safety_margins": dict(observation.safety_margins),
    }
    return hashlib.sha256(canonical_json_bytes(data)).hexdigest()


def replay_spec_to_data(spec: ReplaySpec) -> dict[str, Any]:
    snapshot_data = _snapshot_to_data(spec.snapshot)
    snapshot_data["metadata"] = asdict(spec.snapshot.metadata)
    return {
        "source_run_id": spec.source_run_id,
        "source_branch_id": spec.source_branch_id,
        "snapshot": snapshot_data,
        "config": config_to_data(spec.config),
        "intervention_schedule": [dict(item)
                                  for item in spec.intervention_schedule],
        "target_simulation_time": spec.target_simulation_time,
        "target_step_count": spec.target_step_count,
        "random_state_policy": spec.random_state_policy.value,
        "expected_observation_sha256": spec.expected_observation_sha256,
    }


def persist_replay_spec(spec: ReplaySpec, path: Path) -> ArtifactRef:
    try:
        atomic_write(path, canonical_json_bytes(replay_spec_to_data(spec)))
        return artifact_ref(path)
    except Exception as exc:
        raise SnapshotFailure("failed to persist replay specification") from exc


def load_replay_spec(source: str | Path | ArtifactRef) -> ReplaySpec:
    expected = source.sha256 if isinstance(source, ArtifactRef) else None
    path = Path(source.path if isinstance(source, ArtifactRef) else source).resolve()
    try:
        artifact = artifact_ref(path)
        if expected is not None and artifact.sha256 != expected:
            raise SnapshotFailure("replay specification checksum mismatch")
        data = json.loads(path.read_text(encoding="utf-8"))
        snapshot_data = dict(data["snapshot"])
        snapshot_metadata = ArtifactRef(**snapshot_data.pop("metadata"))
        snapshot = _snapshot_from_data(snapshot_data, snapshot_metadata)
        return ReplaySpec(
            source_run_id=data["source_run_id"],
            source_branch_id=data["source_branch_id"],
            snapshot=snapshot,
            config=config_from_data(data["config"]),
            intervention_schedule=tuple(data["intervention_schedule"]),
            target_simulation_time=data["target_simulation_time"],
            target_step_count=data["target_step_count"],
            random_state_policy=BranchRandomnessPolicy(data["random_state_policy"]),
            expected_observation_sha256=data["expected_observation_sha256"],
        )
    except SnapshotFailure:
        raise
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        raise SnapshotFailure("invalid replay specification") from exc
