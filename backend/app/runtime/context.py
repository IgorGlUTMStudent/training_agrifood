"""Application-owned startup state and explicit fail-closed provider."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from fastapi import HTTPException, Request

from app.analytics.crop_median_baseline import CropMedianBaseline
from app.ingestion.raw_reader import RawSnapshot
from app.runtime.artifact import (
    BaselineArtifact, load_pinned_snapshot, membership_sha256, partition_membership,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnalyticsRuntimeContext:
    snapshot: RawSnapshot
    baseline: CropMedianBaseline
    training_ids: frozenset[str]
    held_out_ids: frozenset[str]


@dataclass(frozen=True)
class AnalyticsRuntimeState:
    analytics: Literal["not_configured", "ready", "unavailable"]
    context: AnalyticsRuntimeContext | None = None


def load_runtime(data_dir: Path, artifact_path: Path) -> AnalyticsRuntimeContext:
    artifact = BaselineArtifact.model_validate_json(artifact_path.read_bytes())
    snapshot = load_pinned_snapshot(data_dir)
    training, held_out = partition_membership(snapshot)
    if membership_sha256(training) != artifact.training_membership_sha256:
        raise ValueError("Training membership fingerprint mismatch")
    crops = {
        row["crop_type"].strip() for row in snapshot["batches"].rows
        if row["batch_id"] in training
    }
    if set(artifact.crop_medians) != crops:
        raise ValueError("Artifact crop coverage differs from the training cohort")
    baseline = CropMedianBaseline(dict(artifact.crop_medians), artifact.global_median)
    return AnalyticsRuntimeContext(snapshot, baseline, training, held_out)


def initialize_runtime() -> AnalyticsRuntimeState:
    data_dir = os.getenv("SMART_HARVEST_DATA_DIR")
    artifact_path = os.getenv("SMART_HARVEST_BASELINE_ARTIFACT")
    if data_dir is None and artifact_path is None:
        return AnalyticsRuntimeState("not_configured")
    try:
        if not data_dir or not data_dir.strip() or not artifact_path or not artifact_path.strip():
            raise ValueError("Both runtime settings must be nonempty")
        context = load_runtime(Path(data_dir), Path(artifact_path))
    except Exception:
        logger.exception("Analytics unavailable: runtime validation failed")
        return AnalyticsRuntimeState("unavailable")
    return AnalyticsRuntimeState("ready", context)


def get_runtime(request: Request) -> AnalyticsRuntimeContext:
    state = request.app.state.analytics_runtime
    if state.analytics != "ready" or state.context is None:
        raise HTTPException(503, "Analytics runtime unavailable", headers={"Cache-Control": "no-store"})
    return state.context
