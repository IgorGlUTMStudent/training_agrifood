"""Private versioned artifact contract and pinned source validation."""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.ingestion.raw_reader import RawSnapshot, read_raw_snapshot
from app.ingestion.structural_manifest import TABLE_MANIFEST

FAMILY = "baseline-crop-median-v1"
ENGINE_VERSION = "baseline-crop-median-v1-p1-s2024"
DATASET_ID = "training-agrifood-snapshot-v1"
NOTICE = "SIMULATION / training challenge dataset / deterministic baseline / not production deployment"
CUTOFF = datetime(2025, 5, 1)
SOURCE_HASHES = {
    "batches": "bbaf3cb4064ccdefed5eaca0b3fe7d6303bd918b1abc09a8c27cb20309d6072b",
    "storage_sessions": "f38a99dfeb808eaab3b3d91d0494d303649131ee2d5de9a6efa0da99fdf9e04f",
    "facilities": "148de414dcff6d601d327ce17414d8b9e04aaa38c6bc0ecbb769be32d6f3a960",
    "storage_zones": "e2c4b7170c47ab0896ed962c588256e3407d84d30afa758372a704d8085c4ee4",
    "quality_checks": "95ccf7d6d898249f6bf444a874817be74b7ce4338b3099f3bf8687f22fa9b627",
    "shipments": "bfad682700f58936ca383868febd09181bd810e81bd3287fa28d16d204ea9796",
    "historical_quality_outcomes": "567334f44f41b980c67de496736c077dc1d980b4cb02c14ee355597087732606",
    "sensor_readings": "6b27adaf43a6646d32cccddc95872bfed03a6220075d9508ccc54be5bdf9edbb",
}


class ArtifactModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)


class TrainingPartition(ArtifactModel):
    predicate: Literal["dispatch_datetime < 2025-05-01"]
    batch_count: Literal[900]


class BaselineArtifact(ArtifactModel):
    format_version: Literal["baseline-artifact.v1"]
    algorithm_family: Literal["baseline-crop-median-v1"]
    engine_version: Literal["baseline-crop-median-v1-p1-s2024"]
    source_dataset_id: Literal["training-agrifood-snapshot-v1"]
    training_partition: TrainingPartition
    source_table_hashes: dict[str, str]
    training_membership_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    crop_medians: dict[str, float] = Field(min_length=1)
    global_median: float

    @field_validator("source_table_hashes")
    @classmethod
    def validate_hashes(cls, value: dict[str, str]) -> dict[str, str]:
        if value != SOURCE_HASHES:
            raise ValueError("Artifact source hashes do not identify the accepted snapshot")
        return value

    @field_validator("crop_medians")
    @classmethod
    def validate_crops(cls, value: dict[str, float]) -> dict[str, float]:
        if any(not crop or crop != crop.strip() for crop in value):
            raise ValueError("Crop keys must be nonempty and normalized")
        return value


def source_hashes(data_dir: Path) -> dict[str, str]:
    result = {}
    for name in SOURCE_HASHES:
        with (data_dir / TABLE_MANIFEST[name].filename).open("rb") as stream:
            result[name] = hashlib.file_digest(stream, "sha256").hexdigest()
    return result


def load_pinned_snapshot(data_dir: Path) -> RawSnapshot:
    if source_hashes(data_dir) != SOURCE_HASHES:
        raise ValueError("Source snapshot hash mismatch")
    snapshot = read_raw_snapshot(data_dir)
    if not snapshot.diagnostics.is_valid():
        raise ValueError("Source snapshot structural diagnostics failed")
    # Reject files changed while the reader was consuming them.
    if source_hashes(data_dir) != SOURCE_HASHES:
        raise ValueError("Source snapshot changed during loading")
    return snapshot


def partition_membership(snapshot: RawSnapshot) -> tuple[frozenset[str], frozenset[str]]:
    """Reconstruct dispatch cohorts without reading historical outcomes."""
    batch_ids = [row["batch_id"] for row in snapshot["batches"].rows]
    if len(set(batch_ids)) != len(batch_ids):
        raise ValueError("Duplicate batch identity")
    sessions: dict[str, list[dict[str, str]]] = {}
    for row in snapshot["storage_sessions"].rows:
        sessions.setdefault(row["batch_id"], []).append(row)
    if set(sessions) != set(batch_ids):
        raise ValueError("Session membership does not match batches")
    training, held_out = set(), set()
    for batch_id in batch_ids:
        rows = sessions[batch_id]
        if len(rows) != 1:
            raise ValueError("Expected exactly one storage session per batch")
        dispatch = datetime.fromisoformat(rows[0]["dispatch_datetime"])
        (training if dispatch < CUTOFF else held_out).add(batch_id)
    if len(training) != 900 or len(held_out) != 900:
        raise ValueError("Expected 900 training and 900 held-out batches")
    return frozenset(training), frozenset(held_out)


def membership_sha256(batch_ids: frozenset[str]) -> str:
    return hashlib.sha256("\n".join(sorted(batch_ids)).encode("utf-8")).hexdigest()
