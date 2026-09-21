"""VDR-06A: Deterministic Baseline Evaluation Harness & Application Parity.

Evaluates the current application baseline engine (app.analytics.crop_median_baseline)
through the canonical ingestion path (read_raw_snapshot -> build_batch_assessment_input)
and verifies strict numerical parity (<= 1e-9) against accepted VDR-04A baseline evidence.

Scope constraints:
- Baseline only: zero learned models, zero feature engineering.
- Parity verification: implementation <-> evidence alignment.
- Zero changes to backend, frontend, schema, or historical evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure backend package is importable
repo_root = Path(__file__).resolve().parent.parent
backend_path = repo_root / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import numpy as np
import pandas as pd
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
from sklearn.model_selection import GroupKFold

from app.analytics.crop_median_baseline import (
    CropMedianBaseline,
    CropMedianTrainingRecord,
    fit_crop_median_baseline,
    predict_loss_fraction_pct,
)
from app.domain.batch import BatchAssessmentInput
from app.ingestion.canonical_mapper import build_batch_assessment_input
from app.ingestion.raw_reader import RawSnapshot, read_raw_snapshot

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vdr06a")

RANDOM_SEED = 42
PARITY_TOLERANCE = 1e-9


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


def verify_integrity_and_hashes(data_dir: Path) -> Dict[str, Any]:
    """Verify presence of raw data files, calculate hashes, and verify structural cardinalities."""
    logger.info("Executing raw dataset verification and hash calculation...")
    required_files = {
        "batches": data_dir / "batches.csv",
        "storage_sessions": data_dir / "storage_sessions.csv",
        "facilities": data_dir / "facilities.csv",
        "storage_zones": data_dir / "storage_zones.csv",
        "quality_checks": data_dir / "quality_checks.csv",
        "shipments": data_dir / "shipments.csv",
        "historical_quality_outcomes": data_dir / "historical_quality_outcomes.csv",
        "sensor_readings": data_dir / "sensor_readings.csv",
    }

    hashes: Dict[str, str] = {}
    for name, path in required_files.items():
        if not path.is_file():
            raise FileNotFoundError(f"Required raw dataset file missing: {path}")
        hashes[name] = compute_file_sha256(path)

    batches_df = pd.read_csv(required_files["batches"])
    sessions_df = pd.read_csv(required_files["storage_sessions"])
    facilities_df = pd.read_csv(required_files["facilities"])
    zones_df = pd.read_csv(required_files["storage_zones"])
    qc_df = pd.read_csv(required_files["quality_checks"])
    shipments_df = pd.read_csv(required_files["shipments"])
    outcomes_df = pd.read_csv(required_files["historical_quality_outcomes"])

    assert len(batches_df) == 1800, f"Expected 1800 batches, got {len(batches_df)}"
    assert len(sessions_df) == 1800, f"Expected 1800 sessions, got {len(sessions_df)}"
    assert len(shipments_df) == 1800, f"Expected 1800 shipments, got {len(shipments_df)}"
    assert len(outcomes_df) == 1800, f"Expected 1800 outcomes, got {len(outcomes_df)}"
    assert len(qc_df) == 5400, f"Expected 5400 quality checks, got {len(qc_df)}"
    assert len(facilities_df) == 10, f"Expected 10 facilities, got {len(facilities_df)}"
    assert len(zones_df) == 25, f"Expected 25 storage zones, got {len(zones_df)}"

    assert batches_df["batch_id"].is_unique, "batches.batch_id PK is not unique"
    assert sessions_df["batch_id"].is_unique, "storage_sessions does not have 1:1 batch_id"
    assert outcomes_df["batch_id"].is_unique, "historical_quality_outcomes does not have 1:1 batch_id"

    return {
        "hashes": hashes,
        "counts": {
            "batches": len(batches_df),
            "storage_sessions": len(sessions_df),
            "facilities": len(facilities_df),
            "storage_zones": len(zones_df),
            "quality_checks": len(qc_df),
            "shipments": len(shipments_df),
            "historical_quality_outcomes": len(outcomes_df),
        },
    }


def verify_accepted_dataset_hashes(
    actual_hashes: Dict[str, str], historical_path: Path
) -> Dict[str, Any]:
    """Verify exact equality of actual dataset hashes against accepted VDR-04A metadata hashes."""
    if not historical_path.is_file():
        raise FileNotFoundError(
            f"Historical VDR-04A results artifact not found at {historical_path}. "
            "Cannot verify accepted dataset hashes."
        )
    with open(historical_path, "r", encoding="utf-8") as f:
        vdr04a_data = json.load(f)

    expected_hashes = vdr04a_data.get("metadata", {}).get("dataset_hashes", {})
    required_datasets = [
        "batches",
        "storage_sessions",
        "facilities",
        "storage_zones",
        "quality_checks",
        "shipments",
        "historical_quality_outcomes",
        "sensor_readings",
    ]

    missing_expected = set(required_datasets) - set(expected_hashes.keys())
    if missing_expected:
        raise ValueError(
            f"Historical VDR-04A artifact missing expected dataset hashes for: {sorted(missing_expected)}"
        )

    missing_actual = set(required_datasets) - set(actual_hashes.keys())
    if missing_actual:
        raise ValueError(
            f"Actual dataset hashes missing required datasets: {sorted(missing_actual)}"
        )

    dataset_comparison: Dict[str, Dict[str, Any]] = {}
    mismatches: List[str] = []

    for name in required_datasets:
        exp = expected_hashes[name]
        act = actual_hashes[name]
        matched = (exp == act)
        dataset_comparison[name] = {
            "expected_sha256": exp,
            "actual_sha256": act,
            "match": matched,
        }
        if not matched:
            mismatches.append(
                f"STOP — DATASET SNAPSHOT MISMATCH: dataset '{name}' expected {exp}, got {act}"
            )

    if mismatches:
        err_msg = "\n".join(mismatches)
        logger.error(err_msg)
        raise ValueError(err_msg)

    logger.info("Accepted dataset hash gate PASSED for all 8 datasets.")
    return {
        "accepted_reference": str(historical_path).replace("\\", "/"),
        "status": "PASS",
        "datasets": dataset_comparison,
    }


def reconstruct_chamber_clusters(sessions_df: pd.DataFrame) -> Tuple[Dict[str, int], int, int]:
    """Reconstruct 157 chamber-time connected components within storage zones."""
    df = sessions_df.copy()
    df["entry_datetime"] = pd.to_datetime(df["entry_datetime"])
    df["dispatch_datetime"] = pd.to_datetime(df["dispatch_datetime"])

    clusters: Dict[str, int] = {}
    cluster_id = 0

    for _, df_zone in df.groupby("zone_id"):
        df_zone = df_zone.sort_values("entry_datetime")
        current_cluster: List[str] = []
        current_end: pd.Timestamp | None = None

        for _, row in df_zone.iterrows():
            if current_end is None:
                current_cluster.append(row["batch_id"])
                current_end = row["dispatch_datetime"]
            elif row["entry_datetime"] <= current_end:
                current_cluster.append(row["batch_id"])
                if row["dispatch_datetime"] > current_end:
                    current_end = row["dispatch_datetime"]
            else:
                for b in current_cluster:
                    clusters[b] = cluster_id
                cluster_id += 1
                current_cluster = [row["batch_id"]]
                current_end = row["dispatch_datetime"]
        if current_cluster:
            for b in current_cluster:
                clusters[b] = cluster_id
            cluster_id += 1

    cluster_counts = pd.Series(clusters).value_counts()
    multi_count = int(sum(cluster_counts[cluster_counts > 1]))
    assert cluster_id == 157, f"Expected 157 clusters, got {cluster_id}"
    assert multi_count == 1734, f"Expected 1734 batches in multi-batch clusters, got {multi_count}"
    logger.info(f"Reconstructed {cluster_id} chamber-time clusters ({multi_count}/1800 batches in multi-batch clusters).")
    return clusters, cluster_id, multi_count


def evaluate_continuous(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute standard continuous metrics."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    sp = float(spearmanr(y_true, y_pred).statistic) if len(np.unique(y_pred)) > 1 else 0.0
    return {"mae": mae, "rmse": rmse, "r2": r2, "spearman": sp}


def evaluate_ranking(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_binary_15: np.ndarray,
    batch_ids: np.ndarray,
) -> Dict[str, Any]:
    """Compute ranking metrics with deterministic secondary sort by batch_id ASC."""
    sp = float(spearmanr(y_true, y_pred).statistic) if len(np.unique(y_pred)) > 1 else 0.0
    ndcg_10 = float(ndcg_score([y_true], [y_pred], k=10))
    ndcg_50 = float(ndcg_score([y_true], [y_pred], k=50))

    # Tie policy: sort by (predicted_loss DESC, batch_id ASC)
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


def _extract_all_keys(obj: Any) -> set[str]:
    keys = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.add(k)
            keys.update(_extract_all_keys(v))
    elif isinstance(obj, list):
        for item in obj:
            keys.update(_extract_all_keys(item))
    return keys


def verify_target_leakage_absence(sample_input: BatchAssessmentInput) -> None:
    """Verify that BatchAssessmentInput does not contain target outcome fields."""
    forbidden_terms = [
        "loss_fraction_pct",
        "quality_status",
        "quality_score",
        "economic_loss_eur",
        "actual_departure_datetime",
        "actual_arrival_datetime",
        "actual_delay_minutes",
        "cold_chain_incident",
        "transit_temp_mean_c",
        "arrival_firmness_kg_cm2",
        "arrival_sugar_brix",
        "arrival_defect_pct",
        "arrival_check_datetime",
    ]
    all_keys = _extract_all_keys(sample_input.model_dump())
    for term in forbidden_terms:
        assert term not in all_keys, f"Leakage detected: {term} found in BatchAssessmentInput keys"


def verify_reference_parity(
    p1_results: Dict[str, Any],
    p2_results: Dict[str, Any],
    historical_path: Path,
) -> Dict[str, Any]:
    """Verify exact parity against accepted historical VDR-04A baseline results."""
    logger.info(f"Loading historical VDR-04A evidence from {historical_path}...")
    if not historical_path.is_file():
        raise FileNotFoundError(
            f"Historical VDR-04A results artifact not found at {historical_path}. "
            "Evaluation cannot proceed without reference baseline artifact."
        )

    with open(historical_path, "r", encoding="utf-8") as f:
        vdr04a_data = json.load(f)

    historical_sha256 = compute_file_sha256(historical_path)

    # Reference metrics from VDR-04A
    br = vdr04a_data.get("benchmark_results", {})
    baselines = br.get("baselines", {})
    p1_ref_cont = baselines.get("p1", {}).get("crop_median_loss", {})
    p1_ref_rank = baselines.get("p1", {}).get("crop_median_ranking", {})
    p2_ref_cont = baselines.get("p2", {}).get("crop_median_loss", {})
    p2_ref_rank = baselines.get("p2", {}).get("crop_median_ranking", {})

    if not p1_ref_cont or not p2_ref_cont:
        raise ValueError("Historical VDR-04A JSON is missing expected baseline metric entries.")

    def compare_metrics(
        actual_cont: Dict[str, float],
        ref_cont: Dict[str, float],
        actual_rank: Dict[str, Any],
        ref_rank: Dict[str, Any],
    ) -> Dict[str, Any]:
        diffs = {
            "mae_diff": abs(actual_cont["mae"] - ref_cont["mae"]),
            "rmse_diff": abs(actual_cont["rmse"] - ref_cont["rmse"]),
            "r2_diff": abs(actual_cont["r2"] - ref_cont["r2"]),
            "spearman_diff": abs(actual_cont["spearman"] - ref_cont["spearman"]),
            "ndcg_10_diff": abs(actual_rank["ndcg_10"] - ref_rank["ndcg_10"]),
            "ndcg_50_diff": abs(actual_rank["ndcg_50"] - ref_rank["ndcg_50"]),
            "precision_at_10_diff": abs(actual_rank["precision_at_10"] - ref_rank["precision_at_10"]),
            "precision_at_50_diff": abs(actual_rank["precision_at_50"] - ref_rank["precision_at_50"]),
            "recall_at_10_diff": abs(actual_rank["recall_at_10"] - ref_rank["recall_at_10"]),
            "recall_at_50_diff": abs(actual_rank["recall_at_50"] - ref_rank["recall_at_50"]),
        }
        all_passed = all(d <= PARITY_TOLERANCE for d in diffs.values())
        diffs["status"] = "PASS" if all_passed else "FAIL"
        return diffs

    p1_parity = compare_metrics(
        p1_results["continuous"],
        p1_ref_cont,
        p1_results["ranking"],
        p1_ref_rank,
    )
    p2_parity = compare_metrics(
        p2_results["continuous"],
        p2_ref_cont,
        p2_results["ranking"],
        p2_ref_rank,
    )

    overall_status = "PASS" if (p1_parity["status"] == "PASS" and p2_parity["status"] == "PASS") else "FAIL"

    if overall_status != "PASS":
        logger.error(f"Parity check failed! P1: {p1_parity}, P2: {p2_parity}")
        raise AssertionError("Baseline application output deviates from historical VDR-04A evidence beyond tolerance.")

    logger.info("Reference parity verification PASSED (all metric diffs <= 1e-9).")
    return {
        "source_vdr04a_artifact": str(historical_path).replace("\\", "/"),
        "source_vdr04a_sha256": historical_sha256,
        "tolerance": PARITY_TOLERANCE,
        "p1": p1_parity,
        "p2": p2_parity,
        "overall_status": overall_status,
    }


def run_evaluation(data_dir: Path, historical_vdr04a: Path) -> Dict[str, Any]:
    """Execute complete deterministic baseline evaluation pipeline."""
    # 0. Early check for required reference evidence
    if not historical_vdr04a.is_file():
        raise FileNotFoundError(
            f"Historical VDR-04A results artifact not found at {historical_vdr04a}. "
            "Evaluation cannot proceed without reference baseline artifact."
        )

    # 1. Verification of data and hashes against accepted snapshot
    integrity_meta = verify_integrity_and_hashes(data_dir)
    dataset_integrity = verify_accepted_dataset_hashes(integrity_meta["hashes"], historical_vdr04a)

    # 2. Reconstruct chamber-time clusters
    sessions_df = pd.read_csv(data_dir / "storage_sessions.csv")
    clusters, n_clusters, multi_count = reconstruct_chamber_clusters(sessions_df)

    # 3. Load Raw Snapshot via application raw reader and enforce fail-closed diagnostics gate
    logger.info("Reading raw snapshot via app.ingestion.raw_reader...")
    snapshot = read_raw_snapshot(data_dir)

    if snapshot.diagnostics.has_errors() or not snapshot.diagnostics.is_valid():
        issue_details = [
            f"[{issue.code}] table='{issue.table_name}' message='{issue.message}' source='{issue.source_path}'"
            for issue in snapshot.diagnostics.issues
        ]
        err_msg = (
            f"Raw snapshot diagnostics contain {len(snapshot.diagnostics.issues)} blocking issues; "
            f"evaluation cannot proceed:\n" + "\n".join(issue_details)
        )
        logger.error(err_msg)
        raise ValueError(err_msg)
    logger.info("Raw snapshot diagnostics verified clean (0 issues).")

    # 4. Prepare evaluation ground truth table sorted deterministically by batch_id
    batches_df = pd.read_csv(data_dir / "batches.csv")
    outcomes_df = pd.read_csv(data_dir / "historical_quality_outcomes.csv")
    eval_df = batches_df.sort_values("batch_id").reset_index(drop=True)
    eval_df = eval_df.merge(sessions_df, on="batch_id", validate="one_to_one")
    eval_df = eval_df.merge(outcomes_df, on="batch_id", validate="one_to_one")
    eval_df["chamber_cluster_id"] = eval_df["batch_id"].map(clusters)

    batch_ids = eval_df["batch_id"].values
    y_loss = eval_df["loss_fraction_pct"].values
    y_bin_15 = (y_loss >= 15.0).astype(int)
    groups = eval_df["chamber_cluster_id"].values

    # 5. Build canonical inputs via canonical mapper
    logger.info("Building 1,800 canonical BatchAssessmentInput objects...")
    canonical_inputs: Dict[str, BatchAssessmentInput] = {}
    for bid in batch_ids:
        canonical_inputs[bid] = build_batch_assessment_input(snapshot, bid)

    assert len(canonical_inputs) == 1800, f"Expected 1800 canonical inputs, got {len(canonical_inputs)}"

    # Check leakage on sample input
    verify_target_leakage_absence(canonical_inputs[batch_ids[0]])

    # =========================================================================
    # PROTOCOL P1: Forward Inter-Season Holdout
    # =========================================================================
    logger.info("Evaluating Protocol P1: Forward Inter-Season Holdout...")
    eval_df["dispatch_datetime"] = pd.to_datetime(eval_df["dispatch_datetime"])
    s2024_mask = eval_df["dispatch_datetime"] < pd.Timestamp("2025-05-01")
    p1_train_idx = np.where(s2024_mask)[0]
    p1_test_idx = np.where(~s2024_mask)[0]
    assert len(p1_train_idx) == 900 and len(p1_test_idx) == 900

    # Fit application crop-median baseline on Season 2024
    p1_train_records = [
        CropMedianTrainingRecord(
            crop_type=canonical_inputs[batch_ids[i]].batch.crop_type,
            loss_fraction_pct=float(y_loss[i]),
        )
        for i in p1_train_idx
    ]
    p1_baseline = fit_crop_median_baseline(p1_train_records)

    # Predict on Season 2025 test set
    p1_preds = np.array([
        predict_loss_fraction_pct(p1_baseline, canonical_inputs[batch_ids[i]])
        for i in p1_test_idx
    ])
    p1_y_test = y_loss[p1_test_idx]
    p1_batch_ids_test = batch_ids[p1_test_idx]
    p1_y_bin_15_test = y_bin_15[p1_test_idx]

    # Explicit count, uniqueness, and finiteness assertions for P1
    assert len(p1_preds) == 900, f"Expected 900 P1 predictions, got {len(p1_preds)}"
    assert len(set(p1_batch_ids_test)) == 900, f"Expected 900 unique P1 test batch IDs, got {len(set(p1_batch_ids_test))}"
    assert np.all(np.isfinite(p1_preds)), "Non-finite values detected in P1 predictions"
    assert not np.any(np.isnan(p1_preds)), "NaN values detected in P1 predictions"

    p1_cont = evaluate_continuous(p1_y_test, p1_preds)
    p1_rank = evaluate_ranking(p1_y_test, p1_preds, p1_y_bin_15_test, p1_batch_ids_test)

    p1_results = {
        "crop_medians": p1_baseline.crop_medians,
        "global_median": p1_baseline.global_median,
        "continuous": p1_cont,
        "ranking": p1_rank,
    }

    # =========================================================================
    # PROTOCOL P2: 5-Fold Grouped Out-of-Fold (Blocked by Chamber Clusters)
    # =========================================================================
    logger.info("Evaluating Protocol P2: 5-Fold Grouped Out-of-Fold...")
    gkf = GroupKFold(n_splits=5)
    p2_folds = list(gkf.split(eval_df, y_loss, groups))

    oof_preds = np.full(len(eval_df), np.nan)
    oof_assignment_counts = np.zeros(len(eval_df), dtype=int)
    fold_metrics = []

    for fold_num, (train_idx, val_idx) in enumerate(p2_folds, start=1):
        assert len(val_idx) == 360, f"Fold {fold_num} val_idx count {len(val_idx)} != 360"
        train_c = set(groups[train_idx])
        val_c = set(groups[val_idx])
        overlap = len(train_c.intersection(val_c))
        assert overlap == 0, f"Fold {fold_num} cluster overlap detected: {overlap}"

        fold_train_records = [
            CropMedianTrainingRecord(
                crop_type=canonical_inputs[batch_ids[i]].batch.crop_type,
                loss_fraction_pct=float(y_loss[i]),
            )
            for i in train_idx
        ]
        fold_baseline = fit_crop_median_baseline(fold_train_records)

        fold_val_preds = np.array([
            predict_loss_fraction_pct(fold_baseline, canonical_inputs[batch_ids[i]])
            for i in val_idx
        ])
        oof_preds[val_idx] = fold_val_preds
        oof_assignment_counts[val_idx] += 1

        val_crops = [canonical_inputs[batch_ids[i]].batch.crop_type.strip() for i in val_idx]
        unseen_fallbacks = int(sum(c not in fold_baseline.crop_medians for c in val_crops))

        f_cont = evaluate_continuous(y_loss[val_idx], fold_val_preds)
        fold_metrics.append({
            "fold": fold_num,
            "train_size": len(train_idx),
            "val_size": len(val_idx),
            "train_clusters": len(train_c),
            "val_clusters": len(val_c),
            "cluster_overlap": overlap,
            "unseen_crop_fallback_count": unseen_fallbacks,
            "mae": f_cont["mae"],
            "rmse": f_cont["rmse"],
            "r2": f_cont["r2"],
            "spearman": f_cont["spearman"],
        })

    # Strict exact-once coverage and finiteness assertions for P2 OOF
    assert np.all(oof_assignment_counts == 1), (
        f"OOF exact-once coverage assertion failed: min_count={oof_assignment_counts.min()}, "
        f"max_count={oof_assignment_counts.max()}"
    )
    assert len(oof_preds) == 1800, f"Expected 1800 P2 OOF predictions, got {len(oof_preds)}"
    assert len(set(batch_ids)) == 1800, f"Expected 1800 unique batch IDs, got {len(set(batch_ids))}"
    assert np.all(np.isfinite(oof_preds)), "Non-finite values detected in P2 OOF predictions"
    assert not np.any(np.isnan(oof_preds)), "NaN values detected in P2 OOF predictions"

    p2_cont = evaluate_continuous(y_loss, oof_preds)
    p2_rank = evaluate_ranking(y_loss, oof_preds, y_bin_15, batch_ids)

    p2_results = {
        "continuous": p2_cont,
        "ranking": p2_rank,
        "fold_level_metrics": fold_metrics,
    }

    # =========================================================================
    # PROTOCOL P3: Random Split Diagnostic (NON-DEFENSIBLE)
    # =========================================================================
    logger.info("Evaluating Protocol P3: Random Split Diagnostic (Non-defensible)...")
    rng = np.random.RandomState(RANDOM_SEED)
    p3_perm = rng.permutation(len(eval_df))
    p3_train_idx = p3_perm[:1440]
    p3_test_idx = p3_perm[1440:]

    train_clusters = set(groups[p3_train_idx])
    test_clusters = groups[p3_test_idx]
    shared_cluster_batches = sum(c in train_clusters for c in test_clusters)
    shared_cluster_pct = float(shared_cluster_batches / len(test_clusters) * 100.0)

    p3_train_records = [
        CropMedianTrainingRecord(
            crop_type=canonical_inputs[batch_ids[i]].batch.crop_type,
            loss_fraction_pct=float(y_loss[i]),
        )
        for i in p3_train_idx
    ]
    p3_baseline = fit_crop_median_baseline(p3_train_records)
    p3_preds = np.array([
        predict_loss_fraction_pct(p3_baseline, canonical_inputs[batch_ids[i]])
        for i in p3_test_idx
    ])
    p3_y_test = y_loss[p3_test_idx]
    p3_batch_ids_test = batch_ids[p3_test_idx]
    p3_y_bin_15_test = y_bin_15[p3_test_idx]

    # Explicit count, uniqueness, and finiteness assertions for P3
    assert len(p3_preds) == 360, f"Expected 360 P3 predictions, got {len(p3_preds)}"
    assert len(set(p3_batch_ids_test)) == 360, f"Expected 360 unique P3 test batch IDs, got {len(set(p3_batch_ids_test))}"
    assert np.all(np.isfinite(p3_preds)), "Non-finite values detected in P3 predictions"
    assert not np.any(np.isnan(p3_preds)), "NaN values detected in P3 predictions"

    p3_cont = evaluate_continuous(p3_y_test, p3_preds)
    p3_rank = evaluate_ranking(p3_y_test, p3_preds, p3_y_bin_15_test, p3_batch_ids_test)

    p3_results = {
        "status": "NON-DEFENSIBLE DIAGNOSTIC — NOT A CANDIDATE FINAL EVALUATION PROTOCOL",
        "train_size": len(p3_train_idx),
        "test_size": len(p3_test_idx),
        "test_batches_sharing_train_cluster_pct": shared_cluster_pct,
        "continuous": p3_cont,
        "ranking": p3_rank,
    }

    # =========================================================================
    # REFERENCE PARITY VERIFICATION
    # =========================================================================
    parity_results = verify_reference_parity(p1_results, p2_results, historical_vdr04a)

    # =========================================================================
    # APPLICATION PARITY SPECIFICATION
    # =========================================================================
    app_parity = {
        "raw_reader_module": "app.ingestion.raw_reader",
        "raw_reader_functions": ["read_raw_snapshot"],
        "canonical_mapper_module": "app.ingestion.canonical_mapper",
        "canonical_mapper_functions": ["build_batch_assessment_input"],
        "engine_module": "app.analytics.crop_median_baseline",
        "engine_functions": ["fit_crop_median_baseline", "predict_loss_fraction_pct"],
        "status": "PASS",
    }

    # =========================================================================
    # ASSEMBLE OUTPUT SCHEMA
    # =========================================================================
    git_sha = get_git_sha(repo_root)

    # Provenance file hashes
    app_baseline_file = repo_root / "backend" / "app" / "analytics" / "crop_median_baseline.py"
    app_baseline_sha256 = compute_file_sha256(app_baseline_file)
    eval_script_file = Path(__file__).resolve()
    eval_script_sha256 = compute_file_sha256(eval_script_file)

    return {
        "schema_version": "vdr-06a.v1",
        "metadata": {
            "source_git_sha": git_sha,
            "python_version": sys.version,
            "numpy_version": np.__version__,
            "pandas_version": pd.__version__,
            "scipy_version": scipy.__version__,
            "sklearn_version": sklearn.__version__,
            "pydantic_version": pydantic.__version__,
            "random_seed": RANDOM_SEED,
            "batch_count": len(eval_df),
            "cluster_count": n_clusters,
            "batches_in_multi_clusters": multi_count,
            "dataset_hashes": integrity_meta["hashes"],
            "application_baseline_file_sha256": app_baseline_sha256,
            "evaluation_script_sha256": eval_script_sha256,
        },
        "structural_verification": {
            "batches_count": integrity_meta["counts"]["batches"],
            "storage_sessions_count": integrity_meta["counts"]["storage_sessions"],
            "facilities_count": integrity_meta["counts"]["facilities"],
            "storage_zones_count": integrity_meta["counts"]["storage_zones"],
            "quality_checks_count": integrity_meta["counts"]["quality_checks"],
            "shipments_count": integrity_meta["counts"]["shipments"],
            "historical_quality_outcomes_count": integrity_meta["counts"]["historical_quality_outcomes"],
            "canonical_inputs_built": len(canonical_inputs),
            "canonical_inputs_errors": 0,
            "raw_snapshot_diagnostics": {
                "blocking_issues_count": len(snapshot.diagnostics.issues),
                "has_errors": snapshot.diagnostics.has_errors(),
                "status": "PASS" if snapshot.diagnostics.is_valid() else "FAIL",
            },
            "target_leakage_check": {
                "outcome_fields_in_canonical_input": False,
                "status": "PASS",
            },
        },
        "prediction_input_fields": {
            "application_object": "BatchAssessmentInput",
            "outcome_fields_present": False,
            "status": "PASS",
        },
        "prediction_coverage": {
            "p1": {
                "train_count": len(p1_train_idx),
                "test_count": len(p1_test_idx),
                "prediction_count": len(p1_preds),
                "unique_prediction_ids": len(set(p1_batch_ids_test)),
                "missing_predictions": int(np.isnan(p1_preds).sum()),
                "nan_predictions": int(np.isnan(p1_preds).sum()),
                "infinite_predictions": int((~np.isfinite(p1_preds)).sum() - np.isnan(p1_preds).sum()),
            },
            "p2": {
                "oof_prediction_count": len(oof_preds),
                "unique_oof_prediction_ids": len(set(batch_ids)),
                "min_oof_assignment_count": int(oof_assignment_counts.min()),
                "max_oof_assignment_count": int(oof_assignment_counts.max()),
                "all_canonical_batch_ids_covered_once": bool(
                    int(oof_assignment_counts.min()) == 1 and int(oof_assignment_counts.max()) == 1
                ),
                "missing_predictions": int(np.isnan(oof_preds).sum()),
                "nan_predictions": int(np.isnan(oof_preds).sum()),
                "infinite_predictions": int((~np.isfinite(oof_preds)).sum() - np.isnan(oof_preds).sum()),
            },
            "p3": {
                "train_count": len(p3_train_idx),
                "test_count": len(p3_test_idx),
                "prediction_count": len(p3_preds),
                "unique_prediction_ids": len(set(p3_batch_ids_test)),
                "missing_predictions": int(np.isnan(p3_preds).sum()),
                "nan_predictions": int(np.isnan(p3_preds).sum()),
                "infinite_predictions": int((~np.isfinite(p3_preds)).sum() - np.isnan(p3_preds).sum()),
            },
        },
        "split_definitions": {
            "P1_inter_season": {
                "train_season": "Season 2024 (2024-05-25 to 2025-04-11, 900 batches)",
                "test_season": "Season 2025 (2025-05-25 to 2026-04-03, 900 batches)",
                "train_count": 900,
                "test_count": 900,
                "hiatus_days": 43.97,
            },
            "P2_grouped_oof": {
                "protocol": "5-fold GroupKFold blocked by 157 chamber-time clusters",
                "total_batches": 1800,
                "fold_sizes": [len(val_idx) for _, val_idx in p2_folds],
                "cluster_leakage_folds": [0 for _ in p2_folds],
            },
            "P3_random_diagnostic": {
                "protocol": "Non-defensible 80/20 random split (seed 42)",
                "train_batches": 1440,
                "test_batches": 360,
                "cluster_leakage_pct": shared_cluster_pct,
                "status": "NON-DEFENSIBLE DIAGNOSTIC — NOT A CANDIDATE FINAL EVALUATION PROTOCOL",
            },
        },
        "evaluation_results": {
            "p1_inter_season": p1_results,
            "p2_grouped_oof": p2_results,
            "p3_random_diagnostic": p3_results,
        },
        "dataset_integrity": dataset_integrity,
        "reference_parity": parity_results,
        "application_parity": app_parity,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VDR-06A Deterministic Baseline Evaluation Harness & Application Parity"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="sponsor_pack/data",
        help="Path to sponsor data directory",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="docs/data_recon/06a_baseline_evaluation_results.json",
        help="Path to output JSON results file",
    )
    parser.add_argument(
        "--historical-vdr04a",
        type=str,
        default="docs/data_recon/04_dispatch_predictability_results.json",
        help="Path to historical VDR-04A results artifact",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output_path = Path(args.output)
    historical_path = Path(args.historical_vdr04a)

    results = run_evaluation(data_dir, historical_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info(f"VDR-06A results successfully written to {output_path}")


if __name__ == "__main__":
    main()
