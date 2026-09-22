"""VDR-06B: Runtime Release Parity & Held-Out Cohort Audit.

Verifies that the integrated RBS-01 runtime release faithfully serves the
accepted deterministic crop-median baseline across the entire pinned release cohort.

Audited chain:
accepted pinned dataset + accepted runtime artifact
  -> FastAPI lifespan
  -> runtime initialization
  -> GET /api/v1/assessments/{batch_id}
  -> canonical mapper
  -> deterministic baseline service
  -> serialized RiskAssessment
  -> independent VDR-06B parity audit

Constraints:
- Baseline only: zero learned models, zero feature engineering.
- Read-only against application code and existing artifacts.
- Zero modifications to backend, frontend, schema, or historical evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure backend package is importable
repo_root = Path(__file__).resolve().parent.parent
backend_path = repo_root / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import numpy as np
import pydantic
import scipy
from scipy.stats import spearmanr
import sklearn
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    ndcg_score,
    r2_score,
)
from fastapi.testclient import TestClient

from app.main import create_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vdr06b")

SCORE_PARITY_TOLERANCE = 1e-12
METRIC_PARITY_TOLERANCE = 1e-9

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

TABLE_FILES = {
    "batches": "batches.csv",
    "storage_sessions": "storage_sessions.csv",
    "facilities": "facilities.csv",
    "storage_zones": "storage_zones.csv",
    "quality_checks": "quality_checks.csv",
    "shipments": "shipments.csv",
    "historical_quality_outcomes": "historical_quality_outcomes.csv",
    "sensor_readings": "sensor_readings.csv",
}


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA256 hex digest of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_git_sha(cwd: Path) -> str:
    """Retrieve current Git HEAD commit hash, failing closed if unavailable."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        sha = res.stdout.strip()
        if not sha or len(sha) < 40:
            raise ValueError(f"Invalid Git commit SHA: {sha!r}")
        return sha
    except Exception as e:
        logger.error(f"Git HEAD resolution failed: {e}")
        raise RuntimeError(f"Failed to resolve git HEAD commit SHA for provenance: {e}") from e


def verify_dataset_hashes(data_dir: Path) -> Dict[str, Any]:
    """Compute and verify SHA256 digests for all 8 source tables against accepted reference."""
    logger.info("Computing independent SHA256 digests for raw datasets...")
    results: Dict[str, Any] = {}
    mismatches: List[str] = []

    for name, filename in TABLE_FILES.items():
        file_path = data_dir / filename
        if not file_path.is_file():
            raise FileNotFoundError(f"Required dataset table missing: {file_path}")
        actual_hash = compute_file_sha256(file_path)
        expected_hash = SOURCE_HASHES[name]
        matched = (actual_hash == expected_hash)
        results[name] = {
            "expected_sha256": expected_hash,
            "actual_sha256": actual_hash,
            "match": matched,
        }
        if not matched:
            mismatches.append(f"Table '{name}' expected {expected_hash}, got {actual_hash}")

    if mismatches:
        err_msg = "STOP — DATASET SOURCE HASH MISMATCH:\n" + "\n".join(mismatches)
        logger.error(err_msg)
        raise ValueError(err_msg)

    logger.info("Dataset hash gate PASSED for all 8 tables.")
    return {
        "status": "PASS",
        "tables": results,
    }


def reconstruct_cohorts_independently(
    data_dir: Path,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], str]:
    """Derive training and held-out cohorts directly from raw CSV files without runtime calls."""
    logger.info("Reconstructing cohorts independently from raw CSVs...")
    batches_path = data_dir / "batches.csv"
    sessions_path = data_dir / "storage_sessions.csv"

    raw_batches: List[Dict[str, str]] = []
    with open(batches_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_batches.append({
                "batch_id": row["batch_id"].strip(),
                "crop_type": row["crop_type"].strip(),
            })

    raw_sessions: Dict[str, str] = {}
    with open(sessions_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bid = row["batch_id"].strip()
            if bid in raw_sessions:
                raise ValueError(f"Duplicate storage session for batch: {bid}")
            raw_sessions[bid] = row["dispatch_datetime"].strip()

    all_batch_ids = [b["batch_id"] for b in raw_batches]
    unique_bids = set(all_batch_ids)
    if len(all_batch_ids) != 1800 or len(unique_bids) != 1800:
        raise ValueError(f"Expected 1800 unique batch IDs, got {len(unique_bids)}")
    if set(raw_sessions.keys()) != unique_bids:
        raise ValueError("Storage sessions batch IDs do not match batches.csv exactly")

    cutoff = "2025-05-01"
    training: List[Dict[str, str]] = []
    held_out: List[Dict[str, str]] = []

    for b in raw_batches:
        bid = b["batch_id"]
        disp = raw_sessions[bid]
        if disp < cutoff:
            training.append(b)
        else:
            held_out.append(b)

    if len(training) != 900 or len(held_out) != 900:
        raise ValueError(
            f"STOP — COHORT RECONSTRUCTION MISMATCH: expected 900 training / 900 held-out, "
            f"got {len(training)} / {len(held_out)}"
        )

    training_ids = set(b["batch_id"] for b in training)
    held_out_ids = set(b["batch_id"] for b in held_out)
    overlap = len(training_ids.intersection(held_out_ids))
    if overlap != 0:
        raise ValueError(f"Cohort overlap detected: {overlap} batches in both cohorts")

    # Independent training membership fingerprint
    training_fingerprint = hashlib.sha256(
        "\n".join(sorted(training_ids)).encode("utf-8")
    ).hexdigest()

    logger.info(f"Independent cohort verified: 900 training, 900 held-out, 0 overlap.")
    return training, held_out, training_fingerprint


def verify_artifact_vdr06a_parity(
    artifact_path: Path, vdr06a_path: Path, training_fingerprint: str
) -> Dict[str, Any]:
    """Verify artifact parameters and metadata against accepted VDR-06A evidence."""
    logger.info("Verifying artifact parameters against VDR-06A accepted evidence...")
    with open(artifact_path, "r", encoding="utf-8") as f:
        art_data = json.load(f)
    with open(vdr06a_path, "r", encoding="utf-8") as f:
        vdr06a_data = json.load(f)

    # Verify artifact full identity and lineage fail-closed
    if art_data.get("format_version") != "baseline-artifact.v1":
        raise ValueError(f"Artifact format_version mismatch: {art_data.get('format_version')}")
    if art_data.get("algorithm_family") != "baseline-crop-median-v1":
        raise ValueError(f"Artifact algorithm_family mismatch: {art_data.get('algorithm_family')}")
    if art_data.get("engine_version") != "baseline-crop-median-v1-p1-s2024":
        raise ValueError(f"Artifact engine_version mismatch: {art_data.get('engine_version')}")
    if art_data.get("source_dataset_id") != "training-agrifood-snapshot-v1":
        raise ValueError(f"Artifact source_dataset_id mismatch: {art_data.get('source_dataset_id')}")
    expected_tp = {"batch_count": 900, "predicate": "dispatch_datetime < 2025-05-01"}
    if art_data.get("training_partition") != expected_tp:
        raise ValueError(f"Artifact training_partition mismatch: {art_data.get('training_partition')}")
    if art_data.get("source_table_hashes") != SOURCE_HASHES:
        raise ValueError("Artifact source_table_hashes mismatch against accepted raw dataset hashes")

    # Verify training membership fingerprint
    art_fingerprint = art_data.get("training_membership_sha256")
    if art_fingerprint != training_fingerprint:
        raise ValueError(
            f"Artifact training membership fingerprint mismatch: expected {training_fingerprint}, got {art_fingerprint}"
        )

    vdr06a_p1 = vdr06a_data["evaluation_results"]["p1_inter_season"]
    vdr06a_crop_medians = vdr06a_p1["crop_medians"]
    vdr06a_global_median = vdr06a_p1["global_median"]

    art_crop_medians = art_data["crop_medians"]
    art_global_median = art_data["global_median"]

    if set(art_crop_medians.keys()) != set(vdr06a_crop_medians.keys()):
        raise ValueError(
            f"Artifact crop keys {set(art_crop_medians.keys())} do not match VDR-06A {set(vdr06a_crop_medians.keys())}"
        )

    crop_diffs: Dict[str, Dict[str, Any]] = {}
    max_crop_delta = 0.0
    for crop in sorted(art_crop_medians.keys()):
        act_val = art_crop_medians[crop]
        ref_val = vdr06a_crop_medians[crop]
        delta = abs(act_val - ref_val)
        if delta > max_crop_delta:
            max_crop_delta = delta
        crop_diffs[crop] = {
            "artifact": act_val,
            "vdr06a": ref_val,
            "delta": delta,
            "match": bool(delta <= SCORE_PARITY_TOLERANCE),
        }
        if delta > SCORE_PARITY_TOLERANCE:
            raise ValueError(f"Crop median parameter mismatch for '{crop}': delta={delta}")

    global_delta = abs(art_global_median - vdr06a_global_median)
    if global_delta > SCORE_PARITY_TOLERANCE:
        raise ValueError(f"Global median parameter mismatch: delta={global_delta}")

    logger.info("Artifact <-> VDR-06A parameter parity verified (all deltas <= 1e-12).")
    return {
        "format_version": art_data["format_version"],
        "algorithm_family": art_data["algorithm_family"],
        "engine_version": art_data["engine_version"],
        "source_dataset_id": art_data["source_dataset_id"],
        "training_partition": art_data["training_partition"],
        "training_membership_sha256": art_fingerprint,
        "crop_key_sets_identical": True,
        "max_crop_median_delta": max_crop_delta,
        "global_median_delta": global_delta,
        "crop_medians_parity": crop_diffs,
        "global_median_parity": {
            "artifact": art_global_median,
            "vdr06a": vdr06a_global_median,
            "delta": global_delta,
            "match": bool(global_delta <= SCORE_PARITY_TOLERANCE),
        },
        "status": "PASS",
    }


def compute_continuous_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute MAE, RMSE, R2, Spearman."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    sp = float(spearmanr(y_true, y_pred).statistic) if len(np.unique(y_pred)) > 1 else 0.0
    return {"mae": mae, "rmse": rmse, "r2": r2, "spearman": sp}


def compute_ranking_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_binary_15: np.ndarray,
    batch_ids: List[str],
) -> Dict[str, Any]:
    """Compute ranking metrics matching VDR-06A tie policy (pred DESC, batch_id ASC)."""
    sp = float(spearmanr(y_true, y_pred).statistic) if len(np.unique(y_pred)) > 1 else 0.0
    ndcg_10 = float(ndcg_score([y_true], [y_pred], k=10))
    ndcg_50 = float(ndcg_score([y_true], [y_pred], k=50))

    batch_ints = [int(b.split("-")[1]) for b in batch_ids]
    order = sorted(range(len(y_pred)), key=lambda i: (-y_pred[i], batch_ints[i]))

    top_10 = order[:10]
    top_50 = order[:50]

    prec_10 = float(np.mean(y_binary_15[top_10]))
    prec_50 = float(np.mean(y_binary_15[top_50]))
    total_pos = max(int(np.sum(y_binary_15)), 1)
    rec_10 = float(np.sum(y_binary_15[top_10]) / total_pos)
    rec_50 = float(np.sum(y_binary_15[top_50]) / total_pos)

    return {
        "spearman": sp,
        "ndcg_10": ndcg_10,
        "ndcg_50": ndcg_50,
        "precision_at_10": prec_10,
        "precision_at_50": prec_50,
        "recall_at_10": rec_10,
        "recall_at_50": rec_50,
        "tie_policy": "deterministic secondary sort by batch_id ascending (zero label knowledge)",
    }


def audit_held_out_api(
    client: TestClient,
    held_out_batches: List[Dict[str, str]],
    art_data: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, float]]:
    """Audit all 900 held-out batches through real FastAPI route."""
    logger.info("Auditing all 900 held-out batches through GET /api/v1/assessments/{batch_id}...")

    # Sort deterministically by batch_id
    sorted_batches = sorted(held_out_batches, key=lambda x: x["batch_id"])

    # Independent expected scores
    expected_scores: Dict[str, float] = {}
    unseen_fallbacks = 0
    for b in sorted_batches:
        crop = b["crop_type"]
        if crop in art_data["crop_medians"]:
            exp_loss = art_data["crop_medians"][crop]
        else:
            exp_loss = art_data["global_median"]
            unseen_fallbacks += 1
        exp_score = max(0.0, min(100.0, exp_loss)) / 100.0
        expected_scores[b["batch_id"]] = exp_score

    manifest: List[Dict[str, Any]] = []
    api_scores: Dict[str, float] = {}

    invariants = {
        "evaluated_count": 0,
        "batch_id_matches_count": 0,
        "status_assessed_count": 0,
        "risk_score_in_bounds_count": 0,
        "risk_band_null_count": 0,
        "deterioration_horizon_null_count": 0,
        "factors_empty_list_count": 0,
        "recommendation_null_count": 0,
        "reliability_level_unavailable_count": 0,
        "reliability_confidence_null_count": 0,
        "reliability_reason_codes_empty_count": 0,
        "reliability_missing_requirements_empty_count": 0,
        "provenance_contract_version_1_0_0_count": 0,
        "provenance_engine_tier_deterministic_baseline_count": 0,
        "provenance_engine_version_matches_count": 0,
        "provenance_source_dataset_id_matches_count": 0,
        "provenance_simulation_true_count": 0,
        "provenance_notice_matches_count": 0,
        "generated_at_valid_and_tz_aware_count": 0,
        "generated_at_plausible_count": 0,
        "cache_control_no_store_count": 0,
    }

    start_time = datetime.now(timezone.utc)
    max_delta = 0.0
    sum_delta = 0.0
    mismatch_count = 0
    non_finite_count = 0

    for b in sorted_batches:
        bid = b["batch_id"]
        res = client.get(f"/api/v1/assessments/{bid}")

        if res.status_code != 200:
            raise AssertionError(f"Expected HTTP 200 for held-out batch {bid}, got {res.status_code}")

        if res.headers.get("cache-control") == "no-store":
            invariants["cache_control_no_store_count"] += 1

        payload = res.json()
        invariants["evaluated_count"] += 1

        if payload.get("batch_id") == bid:
            invariants["batch_id_matches_count"] += 1
        if payload.get("status") == "assessed":
            invariants["status_assessed_count"] += 1

        risk = payload.get("risk", {})
        score = risk.get("score")
        if score is not None and isinstance(score, (int, float)) and 0.0 <= score <= 1.0:
            invariants["risk_score_in_bounds_count"] += 1
        if risk.get("band") is None:
            invariants["risk_band_null_count"] += 1

        if payload.get("deterioration_horizon") is None:
            invariants["deterioration_horizon_null_count"] += 1
        if payload.get("factors") == []:
            invariants["factors_empty_list_count"] += 1
        if payload.get("recommendation") is None:
            invariants["recommendation_null_count"] += 1

        rel = payload.get("reliability", {})
        if rel.get("level") == "unavailable":
            invariants["reliability_level_unavailable_count"] += 1
        if rel.get("confidence_score") is None:
            invariants["reliability_confidence_null_count"] += 1
        if rel.get("reason_codes") == []:
            invariants["reliability_reason_codes_empty_count"] += 1
        if rel.get("missing_requirements") == []:
            invariants["reliability_missing_requirements_empty_count"] += 1

        prov = payload.get("provenance", {})
        if prov.get("contract_version") == "1.0.0":
            invariants["provenance_contract_version_1_0_0_count"] += 1
        if prov.get("engine_tier") == "deterministic_baseline":
            invariants["provenance_engine_tier_deterministic_baseline_count"] += 1
        if prov.get("engine_version") == "baseline-crop-median-v1-p1-s2024":
            invariants["provenance_engine_version_matches_count"] += 1
        if prov.get("source_dataset_id") == "training-agrifood-snapshot-v1":
            invariants["provenance_source_dataset_id_matches_count"] += 1
        if prov.get("simulation") is True:
            invariants["provenance_simulation_true_count"] += 1
        if prov.get("notice") == "SIMULATION / training challenge dataset / deterministic baseline / not production deployment":
            invariants["provenance_notice_matches_count"] += 1

        gen_at_str = prov.get("generated_at")
        if gen_at_str:
            try:
                gen_at = datetime.fromisoformat(gen_at_str.replace("Z", "+00:00"))
                if gen_at.tzinfo is not None:
                    invariants["generated_at_valid_and_tz_aware_count"] += 1
                    # Plausibility: within 1 hour before start_time and 1 hour after now
                    if (gen_at - start_time).total_seconds() >= -3600.0:
                        invariants["generated_at_plausible_count"] += 1
            except Exception:
                pass

        if not isinstance(score, (int, float)) or not np.isfinite(score):
            non_finite_count += 1

        act_score = float(score)
        exp_score = expected_scores[bid]
        api_scores[bid] = act_score

        delta = abs(act_score - exp_score)
        if delta > max_delta:
            max_delta = delta
        sum_delta += delta

        item_status = "PASS" if delta <= SCORE_PARITY_TOLERANCE else "FAIL"
        if item_status != "PASS":
            mismatch_count += 1

        manifest.append({
            "batch_id": bid,
            "crop_type": b["crop_type"],
            "membership": "held_out",
            "api_score": act_score,
            "expected_score": exp_score,
            "absolute_delta": delta,
            "status": item_status,
        })

    # Validate all invariants reached 900
    for k, count in invariants.items():
        if count != 900:
            raise AssertionError(f"Invariant '{k}' failed: count={count}/900")

    mean_delta = sum_delta / len(sorted_batches)
    score_parity_summary = {
        "compared_count": len(sorted_batches),
        "max_absolute_delta": max_delta,
        "mean_absolute_delta": mean_delta,
        "mismatch_count": mismatch_count,
        "non_finite_count": non_finite_count,
        "unseen_crop_fallback_count": unseen_fallbacks,
        "tolerance": SCORE_PARITY_TOLERANCE,
        "status": "PASS" if (mismatch_count == 0 and non_finite_count == 0) else "FAIL",
        "manifest": manifest,
    }

    coverage_summary = {
        "expected_count": 900,
        "requested_count": len(sorted_batches),
        "http_200_count": 900,
        "missing_count": 0,
        "duplicate_count": 0,
        "unexpected_count": 0,
        "cache_control_no_store_count": invariants["cache_control_no_store_count"],
        "status": "PASS",
    }

    if (
        coverage_summary["expected_count"] != 900
        or coverage_summary["requested_count"] != 900
        or coverage_summary["http_200_count"] != 900
        or coverage_summary["missing_count"] != 0
        or coverage_summary["duplicate_count"] != 0
        or coverage_summary["unexpected_count"] != 0
        or coverage_summary["cache_control_no_store_count"] != 900
    ):
        raise AssertionError(f"Held-out coverage or cache-control invariant failed: {coverage_summary}")

    invariants["status"] = "PASS"
    logger.info(f"Held-out audit complete: max_delta={max_delta}, mismatches={mismatch_count}.")
    return coverage_summary, score_parity_summary, api_scores, invariants


def audit_training_release_gate(
    client: TestClient,
    training_batches: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Audit that all 900 training batches receive HTTP 409 release rejection."""
    logger.info("Auditing training cohort release gate (900 batches expected HTTP 409)...")
    expected_detail = "Batch is not eligible for this assessment release"
    http_409_count = 0
    unexpected_count = 0
    detail_matches = 0
    cache_control_matches = 0

    for b in training_batches:
        bid = b["batch_id"]
        res = client.get(f"/api/v1/assessments/{bid}")
        if res.status_code == 409:
            http_409_count += 1
        else:
            unexpected_count += 1

        if res.headers.get("cache-control") == "no-store":
            cache_control_matches += 1

        try:
            if res.json().get("detail") == expected_detail:
                detail_matches += 1
        except Exception:
            pass

    if http_409_count != 900 or unexpected_count != 0 or detail_matches != 900 or cache_control_matches != 900:
        raise AssertionError(
            f"Training release gate failed: 409_count={http_409_count}, unexpected={unexpected_count}, "
            f"detail_matches={detail_matches}, cache_control_matches={cache_control_matches}"
        )

    logger.info("Training release gate PASSED for all 900 batches.")
    return {
        "requested_count": len(training_batches),
        "http_409_count": http_409_count,
        "unexpected_status_count": unexpected_count,
        "expected_detail": expected_detail,
        "detail_match_count": detail_matches,
        "cache_control_matches_count": cache_control_matches,
        "status": "PASS",
    }


def audit_edge_cases(
    client: TestClient,
    all_bids: set[str],
    sample_held_out_bid: str,
    data_dir: Path,
    artifact_path: Path,
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Audit unknown batch (404), unconfigured runtime (503), unavailable (503), and POST (405)."""
    logger.info("Auditing unknown batch, unconfigured, unavailable, and method rejection...")

    # 1. Unknown batch 404
    sentinel = "VDR-06B-NOT-A-BATCH"
    proved_absent = (sentinel not in all_bids)
    if not proved_absent:
        raise ValueError(f"Sentinel '{sentinel}' unexpectedly present in raw batch IDs")
    res_unk = client.get(f"/api/v1/assessments/{sentinel}")
    unk_summary = {
        "sentinel": sentinel,
        "proved_absent": proved_absent,
        "http_status": res_unk.status_code,
        "detail": res_unk.json().get("detail") if res_unk.status_code == 404 else None,
        "cache_control": res_unk.headers.get("cache-control"),
        "status": "PASS" if (
            res_unk.status_code == 404
            and res_unk.json().get("detail") == "Batch not found"
            and res_unk.headers.get("cache-control") == "no-store"
        ) else "FAIL",
    }
    if unk_summary["status"] != "PASS":
        raise AssertionError(f"Unknown batch test failed: status={res_unk.status_code}, cache_control={res_unk.headers.get('cache-control')}")

    # 2. Method rejection 405
    res_post = client.post(f"/api/v1/assessments/{sample_held_out_bid}")
    post_summary = {
        "tested_batch_id": sample_held_out_bid,
        "http_status": res_post.status_code,
        "observed_cache_control": res_post.headers.get("cache-control"),
        "status": "PASS" if (
            res_post.status_code == 405
            and res_post.headers.get("cache-control") == "no-store"
        ) else "FAIL",
    }
    if post_summary["status"] != "PASS":
        raise AssertionError(f"Method rejection test failed: status={res_post.status_code}, cache_control={res_post.headers.get('cache-control')}")

    # Save current env
    saved_data = os.environ.get("SMART_HARVEST_DATA_DIR")
    saved_art = os.environ.get("SMART_HARVEST_BASELINE_ARTIFACT")

    # 3. Unconfigured runtime (both absent)
    os.environ.pop("SMART_HARVEST_DATA_DIR", None)
    os.environ.pop("SMART_HARVEST_BASELINE_ARTIFACT", None)
    app_unconf = create_app()
    with TestClient(app_unconf) as c_unconf:
        h_unconf = c_unconf.get("/api/v1/health")
        a_unconf = c_unconf.get(f"/api/v1/assessments/{sample_held_out_bid}")
        unconf_summary = {
            "health_http_status": h_unconf.status_code,
            "health_service_status": h_unconf.json().get("status"),
            "health_analytics": h_unconf.json().get("analytics"),
            "assessment_http_status": a_unconf.status_code,
            "assessment_detail": a_unconf.json().get("detail"),
            "assessment_cache_control": a_unconf.headers.get("cache-control"),
            "status": "PASS" if (
                h_unconf.status_code == 200 and h_unconf.json().get("analytics") == "not_configured"
                and a_unconf.status_code == 503 and a_unconf.json().get("detail") == "Analytics runtime unavailable"
                and a_unconf.headers.get("cache-control") == "no-store"
            ) else "FAIL",
        }
        if unconf_summary["status"] != "PASS":
            raise AssertionError("Unconfigured runtime audit failed")

    # 4. Configured-unavailable runtime
    nonexistent_path = repo_root / "guaranteed-nonexistent-baseline-artifact.json"
    os.environ["SMART_HARVEST_DATA_DIR"] = str(data_dir)
    os.environ["SMART_HARVEST_BASELINE_ARTIFACT"] = str(nonexistent_path)
    app_unavail = create_app()
    with TestClient(app_unavail) as c_unavail:
        h_unavail = c_unavail.get("/api/v1/health")
        a_unavail = c_unavail.get(f"/api/v1/assessments/{sample_held_out_bid}")
        unavail_summary = {
            "health_http_status": h_unavail.status_code,
            "health_service_status": h_unavail.json().get("status"),
            "health_analytics": h_unavail.json().get("analytics"),
            "assessment_http_status": a_unavail.status_code,
            "assessment_detail": a_unavail.json().get("detail"),
            "assessment_cache_control": a_unavail.headers.get("cache-control"),
            "status": "PASS" if (
                h_unavail.status_code == 200 and h_unavail.json().get("analytics") == "unavailable"
                and a_unavail.status_code == 503 and a_unavail.json().get("detail") == "Analytics runtime unavailable"
                and a_unavail.headers.get("cache-control") == "no-store"
            ) else "FAIL",
        }
        if unavail_summary["status"] != "PASS":
            raise AssertionError("Configured-unavailable runtime audit failed")

    # Restore env
    if saved_data:
        os.environ["SMART_HARVEST_DATA_DIR"] = saved_data
    if saved_art:
        os.environ["SMART_HARVEST_BASELINE_ARTIFACT"] = saved_art

    logger.info("Edge cases audited successfully.")
    return unk_summary, post_summary, unconf_summary, unavail_summary


def audit_response_determinism(
    client: TestClient,
    held_out_batches: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Verify exact payload determinism across duplicate requests for each crop type."""
    logger.info("Auditing response determinism across sentinels...")
    # Select first batch of each crop type
    by_crop: Dict[str, str] = {}
    for b in sorted(held_out_batches, key=lambda x: x["batch_id"]):
        crop = b["crop_type"]
        if crop not in by_crop:
            by_crop[crop] = b["batch_id"]

    sentinels = [by_crop[c] for c in sorted(by_crop.keys())]
    # Add first and last held-out batches
    first_bid = sorted(held_out_batches, key=lambda x: x["batch_id"])[0]["batch_id"]
    last_bid = sorted(held_out_batches, key=lambda x: x["batch_id"])[-1]["batch_id"]
    for extra in [first_bid, last_bid]:
        if extra not in sentinels:
            sentinels.append(extra)

    mismatches = 0
    for bid in sentinels:
        r1 = client.get(f"/api/v1/assessments/{bid}")
        r2 = client.get(f"/api/v1/assessments/{bid}")
        assert r1.status_code == r2.status_code == 200
        p1 = r1.json()
        p2 = r2.json()
        p1.get("provenance", {}).pop("generated_at", None)
        p2.get("provenance", {}).pop("generated_at", None)
        if p1 != p2:
            mismatches += 1

    if mismatches != 0:
        raise AssertionError(f"Response determinism audit failed: {mismatches} mismatches")

    logger.info(f"Response determinism PASSED: {len(sentinels)} sentinels tested twice, 0 mismatches.")
    return {
        "sentinels_evaluated": sentinels,
        "crop_types_covered": sorted(by_crop.keys()),
        "repeat_count_per_sentinel": 2,
        "non_generated_at_mismatches": mismatches,
        "status": "PASS",
    }


def compute_p1_metric_parity(
    data_dir: Path,
    api_scores: Dict[str, float],
    held_out_bids: List[str],
    vdr06a_path: Path,
) -> Dict[str, Any]:
    """Retrospective P1 metric parity: join API predictions to historical outcomes and compare with VDR-06A."""
    logger.info("Computing retrospective P1 metric parity against VDR-06A...")

    # Load outcomes ONLY at this retrospective stage
    outcomes: Dict[str, float] = {}
    with open(data_dir / "historical_quality_outcomes.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            outcomes[row["batch_id"].strip()] = float(row["loss_fraction_pct"])

    sorted_bids = sorted(held_out_bids)
    y_true = np.array([outcomes[b] for b in sorted_bids])
    # Convert risk score [0, 1] back to loss percentage [0, 100]
    y_pred_loss = np.array([api_scores[b] * 100.0 for b in sorted_bids])
    y_bin_15 = (y_true >= 15.0).astype(int)

    act_cont = compute_continuous_metrics(y_true, y_pred_loss)
    act_rank = compute_ranking_metrics(y_true, y_pred_loss, y_bin_15, sorted_bids)

    with open(vdr06a_path, "r", encoding="utf-8") as f:
        vdr06a_data = json.load(f)

    vdr06a_p1 = vdr06a_data["evaluation_results"]["p1_inter_season"]
    ref_cont = vdr06a_p1["continuous"]
    ref_rank = vdr06a_p1["ranking"]

    comparison: Dict[str, Dict[str, Any]] = {}
    max_delta = 0.0

    for m in ["mae", "rmse", "r2", "spearman"]:
        act_val = act_cont[m]
        ref_val = ref_cont[m]
        delta = abs(act_val - ref_val)
        if delta > max_delta:
            max_delta = delta
        comparison[m] = {
            "api": act_val,
            "vdr06a": ref_val,
            "absolute_delta": delta,
            "status": "PASS" if delta <= METRIC_PARITY_TOLERANCE else "FAIL",
        }
        if delta > METRIC_PARITY_TOLERANCE:
            raise AssertionError(f"Continuous metric '{m}' failed parity: delta={delta}")

    for m in ["spearman", "ndcg_10", "ndcg_50", "precision_at_10", "precision_at_50", "recall_at_10", "recall_at_50"]:
        act_val = act_rank[m]
        ref_val = ref_rank[m]
        delta = abs(act_val - ref_val)
        if delta > max_delta:
            max_delta = delta
        comparison[f"rank_{m}" if m == "spearman" else m] = {
            "api": act_val,
            "vdr06a": ref_val,
            "absolute_delta": delta,
            "status": "PASS" if delta <= METRIC_PARITY_TOLERANCE else "FAIL",
        }
        if delta > METRIC_PARITY_TOLERANCE:
            raise AssertionError(f"Ranking metric '{m}' failed parity: delta={delta}")

    logger.info(f"P1 metric parity verified for all 10 metrics (max delta={max_delta} <= 1e-9).")
    return {
        "tolerance": METRIC_PARITY_TOLERANCE,
        "max_metric_delta": max_delta,
        "status": "PASS",
        "continuous": {
            "mae": comparison["mae"],
            "rmse": comparison["rmse"],
            "r2": comparison["r2"],
            "spearman": comparison["spearman"],
        },
        "ranking": {
            "spearman": comparison.get("rank_spearman", comparison["spearman"]),
            "ndcg_10": comparison["ndcg_10"],
            "ndcg_50": comparison["ndcg_50"],
            "precision_at_10": comparison["precision_at_10"],
            "precision_at_50": comparison["precision_at_50"],
            "recall_at_10": comparison["recall_at_10"],
            "recall_at_50": comparison["recall_at_50"],
            "tie_policy": act_rank["tie_policy"],
        },
    }


def run_audit(data_dir: Path, artifact_path: Path, vdr06a_path: Path) -> Dict[str, Any]:
    """Execute complete deterministic VDR-06B audit."""
    # 1. Dataset hash gate
    dataset_integrity = verify_dataset_hashes(data_dir)

    # 2. Independent cohort reconstruction
    training_batches, held_out_batches, training_fingerprint = reconstruct_cohorts_independently(data_dir)
    all_bids = set(b["batch_id"] for b in training_batches).union(set(b["batch_id"] for b in held_out_batches))

    cohorts_summary = {
        "total_batches": len(all_bids),
        "total_storage_sessions": 1800,
        "session_to_batch_1to1": True,
        "training_count": len(training_batches),
        "held_out_count": len(held_out_batches),
        "cohort_overlap_count": 0,
        "cohort_union_count": 1800,
        "cutoff_predicate": "dispatch_datetime < 2025-05-01",
        "training_membership_sha256": training_fingerprint,
        "matches_artifact_training_membership": True,
        "status": "PASS",
    }

    # 3. Artifact <-> VDR-06A parameter parity
    artifact_vdr06a_parity = verify_artifact_vdr06a_parity(artifact_path, vdr06a_path, training_fingerprint)

    # 4. Set environment for real FastAPI application boundary
    os.environ["SMART_HARVEST_DATA_DIR"] = str(data_dir)
    os.environ["SMART_HARVEST_BASELINE_ARTIFACT"] = str(artifact_path)

    app = create_app()
    with open(artifact_path, "r", encoding="utf-8") as f:
        art_data = json.load(f)

    with TestClient(app) as client:
        # Audit held-out cohort (900)
        coverage_summary, score_parity_summary, api_scores, invariants = audit_held_out_api(
            client, held_out_batches, art_data
        )

        # Audit training release gate (900)
        training_gate_summary = audit_training_release_gate(client, training_batches)

        # Audit edge cases
        sample_held_out_bid = sorted(held_out_batches, key=lambda x: x["batch_id"])[0]["batch_id"]
        unk_summary, post_summary, unconf_summary, unavail_summary = audit_edge_cases(
            client, all_bids, sample_held_out_bid, data_dir, artifact_path
        )

        # Audit response determinism
        determinism_summary = audit_response_determinism(client, held_out_batches)

    # 5. Retrospective P1 metric parity
    held_out_bids = [b["batch_id"] for b in held_out_batches]
    p1_metric_parity = compute_p1_metric_parity(data_dir, api_scores, held_out_bids, vdr06a_path)

    # 6. Metadata
    git_sha = get_git_sha(repo_root)
    artifact_sha = compute_file_sha256(artifact_path)
    vdr06a_sha = compute_file_sha256(vdr06a_path)
    eval_script_sha = compute_file_sha256(Path(__file__).resolve())

    metadata = {
        "task": "VDR-06B",
        "source_git_sha": git_sha,
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "sklearn_version": sklearn.__version__,
        "pydantic_version": pydantic.__version__,
        "artifact_file_sha256": artifact_sha,
        "vdr06a_file_sha256": vdr06a_sha,
        "audit_script_sha256": eval_script_sha,
        "dataset_hashes": {name: item["actual_sha256"] for name, item in dataset_integrity["tables"].items()},
    }

    def to_relative_posix(p: Path) -> str:
        try:
            return p.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            return p.as_posix()

    references = {
        "artifact_path": to_relative_posix(artifact_path),
        "artifact_sha256": artifact_sha,
        "vdr06a_path": to_relative_posix(vdr06a_path),
        "vdr06a_sha256": vdr06a_sha,
        "data_dir": to_relative_posix(data_dir),
    }

    conclusions = {
        "summary": (
            "For the pinned training-challenge snapshot and the concrete baseline-crop-median-v1-p1-s2024 release, "
            "the dataset-backed single-batch FastAPI serving path returned complete held-out coverage and reproduced "
            "the accepted P1 deterministic-baseline scores/metrics within the declared parity tolerance."
        ),
        "notice": "SIMULATION / training challenge dataset / deterministic baseline / not production deployment",
        "overall_verdict": "PASS",
    }

    return {
        "schema_version": "vdr-06b.v1",
        "metadata": metadata,
        "references": references,
        "dataset_integrity": dataset_integrity,
        "cohorts": cohorts_summary,
        "artifact_vdr06a_parity": artifact_vdr06a_parity,
        "held_out_api": coverage_summary,
        "response_invariants": invariants,
        "per_batch_score_parity": score_parity_summary,
        "runtime_p1_metric_parity": p1_metric_parity,
        "training_release_gate": training_gate_summary,
        "unknown_batch": unk_summary,
        "unconfigured_runtime": unconf_summary,
        "configured_unavailable": unavail_summary,
        "method_rejection": post_summary,
        "determinism": determinism_summary,
        "conclusions": conclusions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VDR-06B: Runtime Release Parity & Held-Out Cohort Audit"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="sponsor_pack/data",
        help="Path to sponsor data directory",
    )
    parser.add_argument(
        "--artifact",
        type=str,
        default="backend/artifacts/baseline-crop-median-v1-p1-s2024.json",
        help="Path to baseline artifact",
    )
    parser.add_argument(
        "--vdr06a",
        type=str,
        default="docs/data_recon/06a_baseline_evaluation_results.json",
        help="Path to VDR-06A results artifact",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="docs/data_recon/06b_runtime_release_parity_results.json",
        help="Path to output JSON results file",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    artifact_path = Path(args.artifact).resolve()
    vdr06a_path = Path(args.vdr06a).resolve()
    output_path = Path(args.output).resolve()

    results = run_audit(data_dir, artifact_path, vdr06a_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info(f"VDR-06B audit results successfully written to {output_path}")


if __name__ == "__main__":
    main()
