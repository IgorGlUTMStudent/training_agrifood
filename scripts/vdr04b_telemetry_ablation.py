"""VDR-04B: Telemetry Marginal Value Ablation under Planned Logistics.

Authoritative reproduction and ablation runner for VDR-04B evidence package.
Strictly adheres to ADR 0002 cutoff at T_assess = T_dispatch.
Zero usage of forbidden arrival QC, post-dispatch transit fields,
future telemetry, or target outcomes in feature matrices.

Evaluates the 2x2 ablation design:
                     no logistics        + logistics
  no telemetry            C                  C+L
  + telemetry            C+T                C+T+L

Primary comparison: C+T+L versus C+L (telemetry marginal value under planned logistics).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, ndcg_score, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vdr04b")

# Fixed random seed for complete analytical determinism
RANDOM_SEED = 42

# Explicit Forbidden Column Denylist according to ADR 0002
FORBIDDEN_COLUMNS = {
    # Post-dispatch transit realizations in shipments.csv
    "actual_departure_datetime",
    "actual_arrival_datetime",
    "actual_delay_minutes",
    "cold_chain_incident",
    "transit_temp_mean_c",
    # Destination inspection checks
    "arrival_firmness_kg_cm2",
    "arrival_sugar_brix",
    "arrival_defect_pct",
    "arrival_check_datetime",
    # Historical commercial outcomes (strictly evaluation-only)
    "quality_status",
    "loss_fraction_pct",
    "quality_score",
    "economic_loss_eur",
    # Context-only identifiers (forbidden from direct feature use)
    "batch_id",
    "storage_session_id",
    "facility_id",
    "zone_id",
    "shipment_id",
    "reading_id",
    "check_id",
    "facility_name",
    "zone_name",
}


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA256 hex digest of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_integrity(data_dir: Path) -> Dict[str, Any]:
    """Verify core cardinalities, snapshot invariants, and relational integrity."""
    logger.info("Executing pre-analysis integrity gate...")

    files = {
        "batches": data_dir / "batches.csv",
        "storage_sessions": data_dir / "storage_sessions.csv",
        "facilities": data_dir / "facilities.csv",
        "storage_zones": data_dir / "storage_zones.csv",
        "quality_checks": data_dir / "quality_checks.csv",
        "shipments": data_dir / "shipments.csv",
        "historical_quality_outcomes": data_dir / "historical_quality_outcomes.csv",
        "sensor_readings": data_dir / "sensor_readings.csv",
    }

    hashes = {}
    for name, path in files.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing required dataset file: {path}")
        hashes[name] = compute_file_sha256(path)

    # Load tables for cardinality checks
    batches_df = pd.read_csv(files["batches"])
    sessions_df = pd.read_csv(files["storage_sessions"])
    facilities_df = pd.read_csv(files["facilities"])
    zones_df = pd.read_csv(files["storage_zones"])
    qc_df = pd.read_csv(files["quality_checks"])
    shipments_df = pd.read_csv(files["shipments"])
    outcomes_df = pd.read_csv(files["historical_quality_outcomes"])

    # 1. Primary Key Uniqueness
    assert batches_df["batch_id"].is_unique, "batches.batch_id PK is not unique"
    assert sessions_df["storage_session_id"].is_unique, "storage_sessions.storage_session_id PK is not unique"
    assert facilities_df["facility_id"].is_unique, "facilities.facility_id PK is not unique"
    assert zones_df["zone_id"].is_unique, "storage_zones.zone_id PK is not unique"
    assert qc_df["check_id"].is_unique, "quality_checks.check_id PK is not unique"
    assert shipments_df["shipment_id"].is_unique, "shipments.shipment_id PK is not unique"
    assert outcomes_df["batch_id"].is_unique, "historical_quality_outcomes.batch_id PK is not unique"

    # 2. Strict 1:1 Batch Grain Relationships
    assert sessions_df["batch_id"].is_unique, "storage_sessions does not have 1:1 batch_id"
    assert shipments_df["batch_id"].is_unique, "shipments does not have 1:1 batch_id"
    assert outcomes_df["batch_id"].is_unique, "historical_quality_outcomes does not have 1:1 batch_id"

    # 3. Core Cardinality Assertions
    assert len(batches_df) == 1800, f"Expected 1800 batches, got {len(batches_df)}"
    assert len(sessions_df) == 1800, f"Expected 1800 sessions, got {len(sessions_df)}"
    assert len(shipments_df) == 1800, f"Expected 1800 shipments, got {len(shipments_df)}"
    assert len(outcomes_df) == 1800, f"Expected 1800 outcomes, got {len(outcomes_df)}"
    assert len(qc_df) == 5400, f"Expected 5400 quality checks, got {len(qc_df)}"
    assert len(facilities_df) == 10, f"Expected 10 facilities, got {len(facilities_df)}"
    assert len(zones_df) == 25, f"Expected 25 zones, got {len(zones_df)}"

    # 4. Strict Quality Check Invariant: Exactly one harvest, one pre_dispatch, and one arrival check per batch
    qc_batch_stages = qc_df.groupby(["batch_id", "stage"]).size()
    assert (qc_batch_stages == 1).all(), "Quality check stage per batch is not exactly 1"
    assert len(qc_batch_stages) == 1800 * 3, f"Expected 5400 distinct batch-stage pairs, got {len(qc_batch_stages)}"

    logger.info("Integrity checks passed successfully.")
    return {
        "dataset_hashes": hashes,
        "counts": {
            "batches": len(batches_df),
            "storage_sessions": len(sessions_df),
            "shipments": len(shipments_df),
            "historical_quality_outcomes": len(outcomes_df),
            "quality_checks": len(qc_df),
            "facilities": len(facilities_df),
            "storage_zones": len(zones_df),
        },
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


def compute_telemetry_aggregates(
    sensors_df: pd.DataFrame,
    sessions_df: pd.DataFrame,
    zones_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Compute leakage-safe telemetry aggregates and comprehensive diagnostics."""
    logger.info("Computing leakage-safe batch telemetry aggregates...")
    sensors = sensors_df.copy()
    sensors["timestamp"] = pd.to_datetime(sensors["timestamp"])
    total_readings = len(sensors)
    assert total_readings == 669665, f"Expected 669665 sensor readings, got {total_readings}"

    sessions = sessions_df.copy()
    sessions["entry_datetime"] = pd.to_datetime(sessions["entry_datetime"])
    sessions["dispatch_datetime"] = pd.to_datetime(sessions["dispatch_datetime"])
    sessions = sessions.merge(
        zones_df[["zone_id", "target_temperature_c", "target_relative_humidity_pct"]],
        on="zone_id",
        validate="many_to_one",
    )

    # Pre-index sensor readings by zone
    sensors_by_zone = {zid: group.sort_values("timestamp") for zid, group in sensors.groupby("zone_id")}

    records = []
    numeric_channels = [
        "air_temperature_c",
        "produce_surface_temperature_c",
        "relative_humidity_pct",
        "dew_point_c",
        "co2_ppm",
        "o2_pct",
    ]
    binary_channels = ["condensation_flag", "cooling_on", "defrost_on"]

    for _, row in sessions.iterrows():
        z_df = sensors_by_zone[row["zone_id"]]
        ts = z_df["timestamp"].values
        t_entry = np.datetime64(row["entry_datetime"])
        t_disp = np.datetime64(row["dispatch_datetime"])

        idx_start = np.searchsorted(ts, t_entry, side="left")
        idx_end = np.searchsorted(ts, t_disp, side="right")
        sub = z_df.iloc[idx_start:idx_end]
        n_sub = len(sub)

        feat: Dict[str, Any] = {"batch_id": row["batch_id"], "telemetry_reading_count": n_sub}
        if n_sub == 0:
            records.append(feat)
            continue

        # Strict leakage verification
        assert sub["timestamp"].min() >= row["entry_datetime"], "Temporal leak: reading before entry"
        assert sub["timestamp"].max() <= row["dispatch_datetime"], "Temporal leak: reading after dispatch"

        t_target = row["target_temperature_c"]
        rh_target = row["target_relative_humidity_pct"]

        # Numeric channels
        for col in numeric_channels:
            vals = sub[col].dropna()
            feat[f"{col}_missing_frac"] = 1.0 - (len(vals) / n_sub)
            if len(vals) > 0:
                feat[f"{col}_mean"] = float(vals.mean())
                feat[f"{col}_std"] = float(vals.std()) if len(vals) > 1 else 0.0
                feat[f"{col}_min"] = float(vals.min())
                feat[f"{col}_max"] = float(vals.max())
                feat[f"{col}_p10"] = float(np.percentile(vals, 10))
                feat[f"{col}_p90"] = float(np.percentile(vals, 90))
                feat[f"{col}_first"] = float(vals.iloc[0])
                feat[f"{col}_last"] = float(vals.iloc[-1])
                dur_days = (ts[idx_end - 1] - ts[idx_start]) / np.timedelta64(1, "D")
                feat[f"{col}_slope_per_day"] = float((vals.iloc[-1] - vals.iloc[0]) / max(dur_days, 1e-3))
            else:
                feat[f"{col}_mean"] = np.nan
                feat[f"{col}_std"] = np.nan
                feat[f"{col}_min"] = np.nan
                feat[f"{col}_max"] = np.nan
                feat[f"{col}_p10"] = np.nan
                feat[f"{col}_p90"] = np.nan
                feat[f"{col}_first"] = np.nan
                feat[f"{col}_last"] = np.nan
                feat[f"{col}_slope_per_day"] = np.nan

        # Setpoint deviations
        air_vals = sub["air_temperature_c"].dropna()
        if len(air_vals) > 0:
            diff_air = air_vals - t_target
            feat["air_temp_signed_dev_mean"] = float(diff_air.mean())
            feat["air_temp_abs_dev_mean"] = float(diff_air.abs().mean())
            feat["air_temp_abs_dev_max"] = float(diff_air.abs().max())
            feat["air_temp_frac_above_target"] = float((diff_air > 0).mean())
            feat["air_temp_frac_below_target"] = float((diff_air < 0).mean())

        rh_vals = sub["relative_humidity_pct"].dropna()
        if len(rh_vals) > 0:
            diff_rh = rh_vals - rh_target
            feat["rh_signed_dev_mean"] = float(diff_rh.mean())
            feat["rh_abs_dev_mean"] = float(diff_rh.abs().mean())
            feat["rh_abs_dev_max"] = float(diff_rh.abs().max())
            feat["rh_frac_above_target"] = float((diff_rh > 0).mean())
            feat["rh_frac_below_target"] = float((diff_rh < 0).mean())

        # Binary channels
        for col in binary_channels:
            b_vals = sub[col].astype(bool)
            feat[f"{col}_frac_true"] = float(b_vals.mean())
            feat[f"{col}_transitions"] = int((b_vals.values[:-1] != b_vals.values[1:]).sum()) if len(b_vals) > 1 else 0

        records.append(feat)

    telemetry_df = pd.DataFrame(records)
    logger.info(f"Generated telemetry features for {len(telemetry_df)} batches.")
    return telemetry_df, {"total_sensor_readings": total_readings}


def build_canonical_frame(
    data_dir: Path,
    telemetry_df: pd.DataFrame,
    clusters: Dict[str, int],
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame], Dict[str, np.ndarray]]:
    """Build unified canonical modeling frame keyed strictly by batch_id.

    Constructs the 2x2 ablation matrices:
      C       (Context, 37 features)
      C+T     (Context + Telemetry, 114 features)
      C+L     (Context + Planned Logistics, 41 features)
      C+T+L   (Context + Telemetry + Planned Logistics, 118 features)
    """
    logger.info("Building unified canonical modeling frame keyed by batch_id...")

    batches_df = pd.read_csv(data_dir / "batches.csv")
    sessions_df = pd.read_csv(data_dir / "storage_sessions.csv")
    facilities_df = pd.read_csv(data_dir / "facilities.csv")
    zones_df = pd.read_csv(data_dir / "storage_zones.csv")
    qc_df = pd.read_csv(data_dir / "quality_checks.csv")
    shipments_df = pd.read_csv(data_dir / "shipments.csv")
    outcomes_df = pd.read_csv(data_dir / "historical_quality_outcomes.csv")

    # Order canonically by batch_id
    base_df = batches_df.sort_values("batch_id").reset_index(drop=True)

    # Validate 1:1 joins
    base_df = base_df.merge(sessions_df, on="batch_id", validate="one_to_one")
    base_df = base_df.merge(zones_df, on="zone_id", validate="many_to_one")
    base_df = base_df.merge(facilities_df, on="facility_id", validate="many_to_one")
    base_df = base_df.merge(shipments_df, on="batch_id", validate="one_to_one")
    base_df = base_df.merge(outcomes_df, on="batch_id", validate="one_to_one")
    base_df = base_df.merge(telemetry_df, on="batch_id", validate="one_to_one")

    # Map cluster_id by batch_id
    base_df["chamber_cluster_id"] = base_df["batch_id"].map(clusters)

    # QC stage extraction (strictly pre-dispatch)
    qc_h = (
        qc_df[qc_df["stage"] == "harvest"]
        .set_index("batch_id")[["firmness_kg_cm2", "sugar_brix", "defect_pct"]]
        .rename(columns=lambda c: f"harvest_{c}")
    )
    qc_pd = (
        qc_df[qc_df["stage"] == "pre_dispatch"]
        .set_index("batch_id")[["firmness_kg_cm2", "sugar_brix", "defect_pct"]]
        .rename(columns=lambda c: f"pre_dispatch_{c}")
    )
    qc_wide = qc_h.join(qc_pd)
    qc_wide["delta_firmness"] = qc_wide["pre_dispatch_firmness_kg_cm2"] - qc_wide["harvest_firmness_kg_cm2"]
    qc_wide["delta_sugar_brix"] = qc_wide["pre_dispatch_sugar_brix"] - qc_wide["harvest_sugar_brix"]
    qc_wide["delta_defect_pct"] = qc_wide["pre_dispatch_defect_pct"] - qc_wide["harvest_defect_pct"]

    base_df = base_df.merge(qc_wide, on="batch_id", validate="one_to_one")

    # Final frame assertions
    assert len(base_df) == 1800, f"Expected 1800 rows in canonical modeling frame, got {len(base_df)}"
    assert base_df["batch_id"].is_unique, "batch_id is not unique in canonical modeling frame"
    assert base_df["loss_fraction_pct"].notna().all(), "Missing target outcome in canonical frame"
    assert base_df["chamber_cluster_id"].notna().all(), "Missing cluster ID in canonical frame"

    # Derived calendar features
    base_df["harvest_datetime"] = pd.to_datetime(base_df["harvest_datetime"])
    base_df["harvest_month"] = base_df["harvest_datetime"].dt.month
    base_df["harvest_hour"] = base_df["harvest_datetime"].dt.hour
    base_df["field_precooled"] = base_df["field_precooled"].astype(float)

    base_df["entry_datetime"] = pd.to_datetime(base_df["entry_datetime"])
    base_df["dispatch_datetime"] = pd.to_datetime(base_df["dispatch_datetime"])
    base_df["entry_month"] = base_df["entry_datetime"].dt.month
    base_df["dispatch_month"] = base_df["dispatch_datetime"].dt.month
    base_df["dispatch_hour"] = base_df["dispatch_datetime"].dt.hour
    base_df["has_controlled_atmosphere"] = base_df["has_controlled_atmosphere"].astype(float)

    # 1. Context feature definitions (C / F1)
    c_num_cols = [
        "harvest_weight_kg",
        "initial_quality_score",
        "harvest_temperature_c",
        "field_precooled",
        "harvest_month",
        "harvest_hour",
        "bin_stack_tier",
        "storage_duration_days",
        "entry_month",
        "dispatch_month",
        "dispatch_hour",
        "capacity_tonnes",
        "commissioned_year",
        "has_controlled_atmosphere",
        "nominal_capacity_tonnes",
        "target_temperature_c",
        "target_relative_humidity_pct",
        "defrost_cycle_frequency_per_day",
        "harvest_firmness_kg_cm2",
        "harvest_sugar_brix",
        "harvest_defect_pct",
        "pre_dispatch_firmness_kg_cm2",
        "pre_dispatch_sugar_brix",
        "pre_dispatch_defect_pct",
        "delta_firmness",
        "delta_sugar_brix",
        "delta_defect_pct",
    ]
    c_cat_cols = [
        "crop_type",
        "variety",
        "origin_region",
        "harvest_conditions",
        "cooling_system_type",
        "insulation_quality",
        "zone_type",
        "facility_type",
        "region",
        "district",
    ]
    assert len(c_num_cols) == 27, f"Expected 27 numeric context columns, got {len(c_num_cols)}"
    assert len(c_cat_cols) == 10, f"Expected 10 categorical context columns, got {len(c_cat_cols)}"
    c_cols = c_num_cols + c_cat_cols
    assert len(c_cols) == 37, f"Expected 37 context columns, got {len(c_cols)}"

    # 2. Telemetry columns (T)
    telemetry_feature_cols = [c for c in telemetry_df.columns if c != "batch_id"]
    assert len(telemetry_feature_cols) == 77, f"Expected 77 telemetry columns, got {len(telemetry_feature_cols)}"

    # 3. Planned logistics columns (L)
    logistics_cols = ["destination_market", "destination_region", "vehicle_type", "planned_duration_hours"]
    assert len(logistics_cols) == 4, f"Expected 4 planned logistics columns, got {len(logistics_cols)}"

    # Construct the 4 feature matrices
    X_c = base_df[c_cols].copy()
    X_c_t = base_df[c_cols + telemetry_feature_cols].copy()
    X_c_l = base_df[c_cols + logistics_cols].copy()
    X_c_t_l = base_df[c_cols + telemetry_feature_cols + logistics_cols].copy()

    # Exact feature counts
    assert X_c.shape[1] == 37, f"C must have 37 columns, got {X_c.shape[1]}"
    assert X_c_t.shape[1] == 114, f"C+T must have 114 columns, got {X_c_t.shape[1]}"
    assert X_c_l.shape[1] == 41, f"C+L must have 41 columns, got {X_c_l.shape[1]}"
    assert X_c_t_l.shape[1] == 118, f"C+T+L must have 118 columns, got {X_c_t_l.shape[1]}"

    # Invariant assertions:
    # 1. C+L must contain zero telemetry columns
    c_l_telemetry = set(X_c_l.columns).intersection(set(telemetry_feature_cols))
    assert len(c_l_telemetry) == 0, f"C+L must have zero telemetry columns, found: {c_l_telemetry}"

    # 2. C+T+L and C+L must differ ONLY by the telemetry family
    diff_ctl_cl = set(X_c_t_l.columns) - set(X_c_l.columns)
    assert diff_ctl_cl == set(telemetry_feature_cols), "C+T+L and C+L must differ ONLY by telemetry columns"

    # 3. C+T and C must differ ONLY by the telemetry family
    diff_ct_c = set(X_c_t.columns) - set(X_c.columns)
    assert diff_ct_c == set(telemetry_feature_cols), "C+T and C must differ ONLY by telemetry columns"

    # 4. C+T+L and C+T must differ ONLY by the logistics family
    diff_ctl_ct = set(X_c_t_l.columns) - set(X_c_t.columns)
    assert diff_ctl_ct == set(logistics_cols), "C+T+L and C+T must differ ONLY by logistics columns"

    # 5. C+L and C must differ ONLY by the logistics family
    diff_cl_c = set(X_c_l.columns) - set(X_c.columns)
    assert diff_cl_c == set(logistics_cols), "C+L and C must differ ONLY by logistics columns"

    feature_matrices = {
        "C": X_c,
        "C+T": X_c_t,
        "C+L": X_c_l,
        "C+T+L": X_c_t_l,
    }

    # Strict denylist check
    for f_name, f_mat in feature_matrices.items():
        bad_cols = set(f_mat.columns).intersection(FORBIDDEN_COLUMNS)
        assert len(bad_cols) == 0, f"FORBIDDEN column leak in {f_name}: {bad_cols}"
        assert len(f_mat) == 1800, f"Length mismatch in {f_name}: {len(f_mat)}"

    # Targets (strictly aligned with base_df)
    y_dict = {
        "loss_fraction_pct": base_df["loss_fraction_pct"].values,
        "loss_ge_15": (base_df["loss_fraction_pct"] >= 15.0).astype(int).values,
    }

    logger.info("Canonical modeling frame successfully verified and aligned.")
    return base_df, feature_matrices, y_dict


def build_pipeline(X: pd.DataFrame, model_type: str) -> Pipeline:
    """Build preprocessing and model pipeline with fixed hyperparameters."""
    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()

    transformers = []
    if num_cols:
        transformers.append(
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                num_cols,
            )
        )
    if cat_cols:
        transformers.append(
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                cat_cols,
            )
        )

    preprocessor = ColumnTransformer(transformers=transformers)

    if model_type == "linear":
        model = Ridge(alpha=1.0, random_state=RANDOM_SEED)
    elif model_type == "nonlinear":
        model = HistGradientBoostingRegressor(max_iter=100, max_leaf_nodes=31, random_state=RANDOM_SEED)
    else:
        raise ValueError(f"Unknown model_type {model_type}")

    return Pipeline([("prep", preprocessor), ("model", model)])


def evaluate_continuous(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute continuous regression diagnostic metrics."""
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
    """Compute ranking and top-k retrieval metrics with deterministic label-independent tie-breaking."""
    # Spearman rank correlation
    sp = float(spearmanr(y_true, y_pred).statistic) if len(np.unique(y_pred)) > 1 else 0.0

    # NDCG with continuous loss relevance
    ndcg_10 = float(ndcg_score([y_true], [y_pred], k=10))
    ndcg_50 = float(ndcg_score([y_true], [y_pred], k=50))

    # Deterministic label-independent tie policy: sort by (predicted_score DESC, batch_id ASC)
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


def compute_metrics_package(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_binary_15: np.ndarray,
    batch_ids: np.ndarray,
) -> Dict[str, Any]:
    """Combine continuous and ranking metrics into canonical package."""
    cont = evaluate_continuous(y_true, y_pred)
    rank = evaluate_ranking(y_true, y_pred, y_binary_15, batch_ids)
    return {
        "continuous": cont,
        "ranking": rank,
    }


def compute_pairwise_deltas(
    metrics_a: Dict[str, Any],
    metrics_b: Dict[str, Any],
) -> Dict[str, Any]:
    """Compute pairwise deltas: (metrics_b - metrics_a).

    E.g., (C+T+L) minus (C+L): metrics_b=C+T+L, metrics_a=C+L.
    """
    cont_deltas = {}
    for k in metrics_a["continuous"]:
        cont_deltas[k] = float(metrics_b["continuous"][k] - metrics_a["continuous"][k])

    rank_deltas = {}
    for k in [
        "spearman",
        "ndcg_10",
        "ndcg_50",
        "precision_at_10",
        "precision_at_50",
        "recall_at_10",
        "recall_at_50",
    ]:
        rank_deltas[k] = float(metrics_b["ranking"][k] - metrics_a["ranking"][k])

    return {
        "continuous_deltas": cont_deltas,
        "ranking_deltas": rank_deltas,
    }


def evaluate_clipping_diagnostic(
    y_true: np.ndarray,
    y_raw_pred: np.ndarray,
    y_binary_15: np.ndarray,
    batch_ids: np.ndarray,
) -> Dict[str, Any]:
    """Evaluate diagnostic comparing raw predictions to clipped runtime risk score.

    Runtime score: risk.score = clip(predicted_loss_fraction_pct, 0, 100) / 100
    Ranking order: risk.score DESC, batch_id ASC.
    """
    pred_clipped = np.clip(y_raw_pred, 0.0, 100.0)
    risk_score = pred_clipped / 100.0

    n_below_0 = int(np.sum(y_raw_pred < 0.0))
    n_above_100 = int(np.sum(y_raw_pred > 100.0))
    n_outside_bounds = n_below_0 + n_above_100

    n_unique_raw = int(len(np.unique(y_raw_pred)))
    n_unique_clipped = int(len(np.unique(risk_score)))
    ties_introduced = n_unique_raw - n_unique_clipped

    batch_ints = [int(b.split("-")[1]) for b in batch_ids]

    raw_order = sorted(range(len(y_raw_pred)), key=lambda i: (-y_raw_pred[i], batch_ints[i]))
    clipped_order = sorted(range(len(risk_score)), key=lambda i: (-risk_score[i], batch_ints[i]))

    # Rank correlation between raw order and clipped order
    raw_ranks = np.empty_like(raw_order)
    clipped_ranks = np.empty_like(clipped_order)
    raw_ranks[raw_order] = np.arange(len(raw_order))
    clipped_ranks[clipped_order] = np.arange(len(clipped_order))
    rank_spearman = float(spearmanr(raw_ranks, clipped_ranks).statistic)

    rank_positions_changed = int(np.sum(raw_ranks != clipped_ranks))

    top_10_raw = set(raw_order[:10])
    top_10_clipped = set(clipped_order[:10])
    top_10_overlap = int(len(top_10_raw.intersection(top_10_clipped)))

    top_50_raw = set(raw_order[:50])
    top_50_clipped = set(clipped_order[:50])
    top_50_overlap = int(len(top_50_raw.intersection(top_50_clipped)))

    clipped_ranking_metrics = evaluate_ranking(y_true, risk_score, y_binary_15, batch_ids)

    return {
        "n_predictions_below_0": n_below_0,
        "n_predictions_above_100": n_above_100,
        "n_predictions_outside_bounds": n_outside_bounds,
        "unique_raw_predictions": n_unique_raw,
        "unique_clipped_scores": n_unique_clipped,
        "ties_introduced_by_clipping": ties_introduced,
        "rank_spearman_raw_vs_clipped": rank_spearman,
        "rank_positions_changed": rank_positions_changed,
        "top_10_overlap_count": top_10_overlap,
        "top_50_overlap_count": top_50_overlap,
        "clipped_ranking_metrics": clipped_ranking_metrics,
        "tie_breaker": "risk.score DESC, batch_id ASC",
    }


def run_vdr04b_ablation(
    feature_matrices: Dict[str, pd.DataFrame],
    y_dict: Dict[str, np.ndarray],
    ctx_df: pd.DataFrame,
) -> Dict[str, Any]:
    """Execute complete VDR-04B ablation suite under P1 and P2."""
    batch_ids = ctx_df["batch_id"].values
    y_loss = y_dict["loss_fraction_pct"]
    y_bin15 = y_dict["loss_ge_15"]
    crops = ctx_df["crop_type"].values
    groups = ctx_df["chamber_cluster_id"].values

    # Protocol P1: Forward Inter-Season Holdout
    s2024_mask = ctx_df["dispatch_datetime"] < pd.Timestamp("2025-05-01")
    p1_train_idx = np.where(s2024_mask)[0]
    p1_test_idx = np.where(~s2024_mask)[0]
    assert len(p1_train_idx) == 900 and len(p1_test_idx) == 900

    # Protocol P2: 5-Fold Chamber-Time Grouped OOF
    gkf = GroupKFold(n_splits=5)
    p2_folds = list(gkf.split(ctx_df, y_loss, groups))

    # =========================================================================
    # 1. BASELINE (Fit strictly training-only)
    # =========================================================================
    # P1 Baseline
    gm_p1 = float(np.median(y_loss[p1_train_idx]))
    cm_dict_p1 = {c: float(np.median(y_loss[p1_train_idx][crops[p1_train_idx] == c])) for c in set(crops[p1_train_idx])}
    pred_cm_p1 = np.array([cm_dict_p1.get(c, gm_p1) for c in crops[p1_test_idx]])
    p1_baseline_metrics = compute_metrics_package(
        y_loss[p1_test_idx], pred_cm_p1, y_bin15[p1_test_idx], batch_ids[p1_test_idx]
    )

    # P2 Baseline (OOF)
    pred_p2_cm = np.zeros(len(ctx_df))
    p2_fold_baselines = []
    for f_idx, (tr_idx, val_idx) in enumerate(p2_folds, start=1):
        gm_f = float(np.median(y_loss[tr_idx]))
        cm_d = {c: float(np.median(y_loss[tr_idx][crops[tr_idx] == c])) for c in set(crops[tr_idx])}
        fold_pred_base = np.array([cm_d.get(c, gm_f) for c in crops[val_idx]])
        pred_p2_cm[val_idx] = fold_pred_base
        p2_fold_baselines.append(
            {
                "fold": f_idx,
                "metrics": compute_metrics_package(
                    y_loss[val_idx], fold_pred_base, y_bin15[val_idx], batch_ids[val_idx]
                ),
            }
        )
    p2_baseline_metrics = compute_metrics_package(y_loss, pred_p2_cm, y_bin15, batch_ids)

    baselines = {
        "p1_crop_median": p1_baseline_metrics,
        "p2_crop_median_oof": p2_baseline_metrics,
        "p2_fold_baselines": p2_fold_baselines,
    }

    # =========================================================================
    # 2. EXPERIMENT RUNNER FOR P1 AND P2
    # =========================================================================
    families = ["C", "C+T", "C+L", "C+T+L"]
    models = ["linear", "nonlinear"]

    p1_results: Dict[str, Any] = {}
    p1_clipping_diagnostics: Dict[str, Any] = {}
    p2_oof_results: Dict[str, Any] = {}
    p2_fold_results: Dict[str, Any] = {}
    p2_clipping_diagnostics: Dict[str, Any] = {}

    # P1 Forward Inter-Season
    logger.info("Executing Protocol P1 across all 4 families...")
    for fam in families:
        X = feature_matrices[fam]
        p1_results[fam] = {}
        p1_clipping_diagnostics[fam] = {}

        for m_type in models:
            pipe = build_pipeline(X, m_type)
            pipe.fit(X.iloc[p1_train_idx], y_loss[p1_train_idx])
            pred_p1 = pipe.predict(X.iloc[p1_test_idx])

            p1_results[fam][m_type] = compute_metrics_package(
                y_loss[p1_test_idx], pred_p1, y_bin15[p1_test_idx], batch_ids[p1_test_idx]
            )
            p1_clipping_diagnostics[fam][m_type] = evaluate_clipping_diagnostic(
                y_loss[p1_test_idx], pred_p1, y_bin15[p1_test_idx], batch_ids[p1_test_idx]
            )

    # P2 Chamber-Time Grouped OOF
    logger.info("Executing Protocol P2 across all 4 families...")
    for fam in families:
        X = feature_matrices[fam]
        p2_oof_results[fam] = {}
        p2_fold_results[fam] = {}
        p2_clipping_diagnostics[fam] = {}

        for m_type in models:
            oof_preds = np.zeros(len(ctx_df))
            fold_evals = []

            for fold_idx, (tr_idx, val_idx) in enumerate(p2_folds, start=1):
                pipe = build_pipeline(X, m_type)
                pipe.fit(X.iloc[tr_idx], y_loss[tr_idx])
                fold_pred = pipe.predict(X.iloc[val_idx])
                oof_preds[val_idx] = fold_pred

                fold_metrics = compute_metrics_package(
                    y_loss[val_idx], fold_pred, y_bin15[val_idx], batch_ids[val_idx]
                )
                fold_evals.append(
                    {
                        "fold": fold_idx,
                        "val_size": len(val_idx),
                        "metrics": fold_metrics,
                    }
                )

            p2_fold_results[fam][m_type] = fold_evals
            p2_oof_results[fam][m_type] = compute_metrics_package(
                y_loss, oof_preds, y_bin15, batch_ids
            )
            p2_clipping_diagnostics[fam][m_type] = evaluate_clipping_diagnostic(
                y_loss, oof_preds, y_bin15, batch_ids
            )

    # =========================================================================
    # 3. PAIRWISE COMPARISONS AND DELTAS
    # =========================================================================
    # Pairs to compute:
    # 1. C+T minus C (telemetry without logistics)
    # 2. C+L minus C (logistics without telemetry)
    # 3. C+T+L minus C+T (logistics with telemetry)
    # 4. C+T+L minus C+L (telemetry with logistics — PRIMARY ABLATION)

    pairwise_p1: Dict[str, Any] = {}
    pairwise_p2_oof: Dict[str, Any] = {}
    pairwise_p2_folds: Dict[str, Any] = {}

    delta_pairs = [
        ("telemetry_without_logistics", "C", "C+T"),
        ("logistics_without_telemetry", "C", "C+L"),
        ("logistics_with_telemetry", "C+T", "C+T+L"),
        ("telemetry_with_logistics__PRIMARY", "C+L", "C+T+L"),
    ]

    for label, base_fam, target_fam in delta_pairs:
        pairwise_p1[label] = {}
        pairwise_p2_oof[label] = {}
        pairwise_p2_folds[label] = {}

        for m_type in models:
            pairwise_p1[label][m_type] = compute_pairwise_deltas(
                p1_results[base_fam][m_type], p1_results[target_fam][m_type]
            )
            pairwise_p2_oof[label][m_type] = compute_pairwise_deltas(
                p2_oof_results[base_fam][m_type], p2_oof_results[target_fam][m_type]
            )

            # Fold-level deltas
            fold_deltas = []
            for f_idx in range(5):
                f_base = p2_fold_results[base_fam][m_type][f_idx]["metrics"]
                f_target = p2_fold_results[target_fam][m_type][f_idx]["metrics"]
                fold_deltas.append(
                    {
                        "fold": f_idx + 1,
                        "deltas": compute_pairwise_deltas(f_base, f_target),
                    }
                )
            pairwise_p2_folds[label][m_type] = fold_deltas

    return {
        "baselines": baselines,
        "p1_inter_season": p1_results,
        "p2_grouped_oof": p2_oof_results,
        "p2_fold_level_results": p2_fold_results,
        "pairwise_deltas": {
            "p1_inter_season": pairwise_p1,
            "p2_grouped_oof": pairwise_p2_oof,
            "p2_folds": pairwise_p2_folds,
        },
        "clipping_diagnostics": {
            "p1_inter_season": p1_clipping_diagnostics,
            "p2_grouped_oof": p2_clipping_diagnostics,
        },
    }


def compare_vdr04a_replication(
    reproduced: Dict[str, Any],
    historical_path: Path,
) -> Dict[str, Any]:
    """Verify replication of overlapping families against historical VDR-04A evidence."""
    if not historical_path.exists():
        logger.warning(f"Historical VDR-04A file {historical_path} not found; skipping reproduction comparison.")
        return {"status": "historical_file_not_found"}

    with open(historical_path, "r", encoding="utf-8") as f:
        hist_data = json.load(f)

    hist_p1 = hist_data["benchmark_results"]["p1_inter_season"]
    hist_p2 = hist_data["benchmark_results"]["p2_grouped_oof"]

    rep_p1 = reproduced["p1_inter_season"]
    rep_p2 = reproduced["p2_grouped_oof"]

    # Mapping from VDR-04B family to VDR-04A family
    fam_map = {
        "C": "F1",
        "C+T": "F2",
        "C+T+L": "F3",
    }

    comparison: Dict[str, Any] = {"p1": {}, "p2": {}, "max_absolute_difference": 0.0}
    max_diff = 0.0

    for b_fam, a_fam in fam_map.items():
        comparison["p1"][b_fam] = {}
        comparison["p2"][b_fam] = {}

        for m_type in ["linear", "nonlinear"]:
            comparison["p1"][b_fam][m_type] = {}
            comparison["p2"][b_fam][m_type] = {}

            # P1 continuous
            hist_cont_p1 = hist_p1[a_fam][m_type]["regression_loss"]
            rep_cont_p1 = rep_p1[b_fam][m_type]["continuous"]
            for m in ["mae", "rmse", "r2", "spearman"]:
                h_val = hist_cont_p1[m]
                r_val = rep_cont_p1[m]
                diff = abs(h_val - r_val)
                max_diff = max(max_diff, diff)
                comparison["p1"][b_fam][m_type][f"cont_{m}"] = {
                    "historical": h_val,
                    "reproduced": r_val,
                    "diff": diff,
                }

            # P1 ranking
            hist_rank_p1 = hist_p1[a_fam][m_type]["ranking"]
            rep_rank_p1 = rep_p1[b_fam][m_type]["ranking"]
            for m in ["ndcg_10", "ndcg_50", "precision_at_10", "precision_at_50", "recall_at_10", "recall_at_50"]:
                h_val = hist_rank_p1[m]
                r_val = rep_rank_p1[m]
                diff = abs(h_val - r_val)
                max_diff = max(max_diff, diff)
                comparison["p1"][b_fam][m_type][f"rank_{m}"] = {
                    "historical": h_val,
                    "reproduced": r_val,
                    "diff": diff,
                }

            # P2 continuous
            hist_cont_p2 = hist_p2[a_fam][m_type]["regression_loss"]
            rep_cont_p2 = rep_p2[b_fam][m_type]["continuous"]
            for m in ["mae", "rmse", "r2", "spearman"]:
                h_val = hist_cont_p2[m]
                r_val = rep_cont_p2[m]
                diff = abs(h_val - r_val)
                max_diff = max(max_diff, diff)
                comparison["p2"][b_fam][m_type][f"cont_{m}"] = {
                    "historical": h_val,
                    "reproduced": r_val,
                    "diff": diff,
                }

            # P2 ranking
            hist_rank_p2 = hist_p2[a_fam][m_type]["ranking"]
            rep_rank_p2 = rep_p2[b_fam][m_type]["ranking"]
            for m in ["ndcg_10", "ndcg_50", "precision_at_10", "precision_at_50", "recall_at_10", "recall_at_50"]:
                h_val = hist_rank_p2[m]
                r_val = rep_rank_p2[m]
                diff = abs(h_val - r_val)
                max_diff = max(max_diff, diff)
                comparison["p2"][b_fam][m_type][f"rank_{m}"] = {
                    "historical": h_val,
                    "reproduced": r_val,
                    "diff": diff,
                }

    comparison["max_absolute_difference"] = max_diff
    comparison["parity_status"] = "EXACT_OR_NUMERICALLY_EQUIVALENT" if max_diff < 1e-6 else "DIVERGENCE_DETECTED"
    logger.info(f"VDR-04A Replication Check: max diff = {max_diff:.8e}, status = {comparison['parity_status']}")
    return comparison


def main() -> None:
    parser = argparse.ArgumentParser(description="VDR-04B Telemetry Marginal Value Ablation Benchmark")
    parser.add_argument("--data-dir", type=str, default="sponsor_pack/data", help="Path to sponsor data directory")
    parser.add_argument(
        "--output",
        type=str,
        default="docs/data_recon/04b_telemetry_ablation_results.json",
        help="Path to output JSON results",
    )
    parser.add_argument(
        "--historical-vdr04a",
        type=str,
        default="docs/data_recon/04_dispatch_predictability_results.json",
        help="Path to historical VDR-04A JSON results",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output_path = Path(args.output)
    hist_path = Path(args.historical_vdr04a)

    # 1. Integrity Gate
    integrity_meta = verify_integrity(data_dir)

    # 2. Reconstruct Chamber-Time Clusters
    sessions_df = pd.read_csv(data_dir / "storage_sessions.csv")
    clusters, n_clusters, multi_count = reconstruct_chamber_clusters(sessions_df)

    # 3. Telemetry Aggregation
    sensors_df = pd.read_csv(data_dir / "sensor_readings.csv")
    zones_df = pd.read_csv(data_dir / "storage_zones.csv")
    telemetry_df, tele_meta = compute_telemetry_aggregates(sensors_df, sessions_df, zones_df)

    # 4. Assemble Unified Canonical Modeling Frame (Guaranteed 1:1 Batch Alignment)
    canonical_df, feature_matrices, y_dict = build_canonical_frame(data_dir, telemetry_df, clusters)

    # 5. Run Complete VDR-04B Ablation Benchmark
    ablation_results = run_vdr04b_ablation(feature_matrices, y_dict, canonical_df)

    # 6. Compare Replication against historical VDR-04A
    replication_comparison = compare_vdr04a_replication(ablation_results, hist_path)

    # 7. Build Final JSON Artifact with full schema metadata
    output_data = {
        "schema_version": "vdr-04b.v1",
        "metadata": {
            "source_git_sha": "0c31f947386233badc9122c9cd374fd0c38c1140",
            "task_branch": "victor/vdr-04b-telemetry-ablation",
            "python_version": sys.version,
            "numpy_version": np.__version__,
            "pandas_version": pd.__version__,
            "sklearn_version": sklearn.__version__,
            "scipy_version": sys.modules["scipy"].__version__,
            "random_seed": RANDOM_SEED,
            "cluster_count": n_clusters,
            "batches_in_multi_clusters": multi_count,
            "dataset_hashes": integrity_meta["dataset_hashes"],
        },
        "experiment_design": {
            "primary_question": "Does pre-dispatch telemetry provide material incremental predictive/ranking value once planned logistics are already present?",
            "primary_comparison": "C+T+L versus C+L",
            "design_matrix": {
                "no_logistics_no_telemetry": "C",
                "no_logistics_plus_telemetry": "C+T",
                "plus_logistics_no_telemetry": "C+L",
                "plus_logistics_plus_telemetry": "C+T+L",
            },
            "feature_counts": {
                "C": int(feature_matrices["C"].shape[1]),
                "C+T": int(feature_matrices["C+T"].shape[1]),
                "C+L": int(feature_matrices["C+L"].shape[1]),
                "C+T+L": int(feature_matrices["C+T+L"].shape[1]),
            },
            "planned_logistics_boundary": [
                "destination_market",
                "destination_region",
                "vehicle_type",
                "planned_duration_hours",
            ],
        },
        "feature_family_columns": {
            "C": list(feature_matrices["C"].columns),
            "C+T": list(feature_matrices["C+T"].columns),
            "C+L": list(feature_matrices["C+L"].columns),
            "C+T+L": list(feature_matrices["C+T+L"].columns),
        },
        "split_definitions": {
            "P1_inter_season": {
                "train_season": "Season 2024 (2024-05-25 to 2025-04-11, 900 batches)",
                "test_season": "Season 2025 (2025-05-25 to 2026-04-03, 900 batches)",
                "hiatus_days": 43.97,
            },
            "P2_grouped_oof": {
                "protocol": "5-fold GroupKFold blocked by 157 chamber-time clusters",
                "total_batches": 1800,
                "fold_sizes": [360, 360, 360, 360, 360],
            },
        },
        "model_definitions": {
            "linear_regression": {
                "class": "Ridge",
                "parameters": {"alpha": 1.0, "random_state": RANDOM_SEED},
            },
            "nonlinear_regression": {
                "class": "HistGradientBoostingRegressor",
                "parameters": {"max_iter": 100, "max_leaf_nodes": 31, "random_state": RANDOM_SEED},
            },
            "baseline": {
                "p1": "crop-conditioned training median loss_fraction_pct, fallback to global training median",
                "p2": "per-fold crop-conditioned training median loss_fraction_pct, fallback to global training median of fold",
            },
            "preprocessing": {
                "numeric": "SimpleImputer(strategy='median') + StandardScaler()",
                "categorical": "OneHotEncoder(handle_unknown='ignore', sparse_output=False)",
                "fitting_rule": "Fitted strictly on training partition/fold only",
            },
        },
        "target_definition": {
            "offline_supervised_target": "loss_fraction_pct",
            "evaluation_threshold_for_precision_recall": "loss_fraction_pct >= 15.0%",
            "ndcg_relevance": "continuous loss_fraction_pct",
        },
        "vdr04a_replication_comparison": replication_comparison,
        "ablation_results": ablation_results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    logger.info(f"VDR-04B ablation complete. Results saved to {output_path}")


if __name__ == "__main__":
    main()
