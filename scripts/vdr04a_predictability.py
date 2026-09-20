"""VDR-04A: Dispatch-Time Predictability & Ranking Feasibility Benchmark.

Authoritative reproduction script for VDR-04A evidence package.
Strictly adheres to ADR 0002 cutoff at T_assess = T_dispatch.
Zero usage of forbidden arrival QC, post-dispatch transit fields,
future telemetry, or target outcomes in feature matrices.
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
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    ndcg_score,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vdr04a")

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

    # 1. Per-zone diagnostics
    zone_diagnostics = {}
    for zid, group in sensors.groupby("zone_id"):
        z_target = zones_df.loc[zones_df["zone_id"] == zid, "target_temperature_c"].values[0]
        group = group.sort_values("timestamp")
        temp_residual = group["air_temperature_c"] - z_target
        autocorr = temp_residual.autocorr(lag=1)
        zone_diagnostics[zid] = {
            "reading_count": int(len(group)),
            "air_temp_residual_mean": float(temp_residual.mean()),
            "air_temp_residual_std": float(temp_residual.std()),
            "air_temp_autocorr_lag1": float(autocorr) if not pd.isna(autocorr) else None,
            "cooling_duty_fraction": float(group["cooling_on"].mean()),
            "defrost_duty_fraction": float(group["defrost_on"].mean()),
            "condensation_duty_fraction": float(group["condensation_flag"].mean()),
            "surface_temp_missing_frac": float(group["produce_surface_temperature_c"].isna().mean()),
            "co2_missing_frac": float(group["co2_ppm"].isna().mean()),
            "o2_missing_frac": float(group["o2_pct"].isna().mean()),
        }

    # 2. Separate CA Room Gas-Channel Analysis
    ca_zones = zones_df.loc[zones_df["zone_type"] == "Controlled Atmosphere (CA)", "zone_id"].tolist()
    ca_sensors = sensors[sensors["zone_id"].isin(ca_zones)]
    ca_gas_diagnostics = {
        "ca_room_count": len(ca_zones),
        "ca_zone_ids": ca_zones,
        "co2_ppm": {
            "total_readings": int(len(ca_sensors)),
            "missing_fraction": float(ca_sensors["co2_ppm"].isna().mean()),
            "mean": float(ca_sensors["co2_ppm"].mean()),
            "std": float(ca_sensors["co2_ppm"].std()),
            "min": float(ca_sensors["co2_ppm"].min()),
            "max": float(ca_sensors["co2_ppm"].max()),
        },
        "o2_pct": {
            "total_readings": int(len(ca_sensors)),
            "missing_fraction": float(ca_sensors["o2_pct"].isna().mean()),
            "mean": float(ca_sensors["o2_pct"].mean()),
            "std": float(ca_sensors["o2_pct"].std()),
            "min": float(ca_sensors["o2_pct"].min()),
            "max": float(ca_sensors["o2_pct"].max()),
        },
        "non_ca_representation_rule": "Absent in non-CA rooms represented strictly as explicit null, never zero.",
    }

    # 3. Extract per-batch features
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

    # 4. Batch-Level Telemetry Variability & Association with Storage Duration
    merged_tele_dur = telemetry_df.merge(
        sessions_df[["batch_id", "storage_duration_days"]],
        on="batch_id",
        validate="one_to_one",
    )
    major_channels = [
        "air_temperature_c_mean",
        "air_temperature_c_std",
        "relative_humidity_pct_mean",
        "cooling_on_frac_true",
        "defrost_on_frac_true",
        "condensation_flag_frac_true",
        "air_temp_abs_dev_mean",
    ]
    batch_telemetry_summary = {}
    for col in major_channels:
        series = merged_tele_dur[col].dropna()
        corr_dur = float(pearsonr(series, merged_tele_dur.loc[series.index, "storage_duration_days"])[0])
        batch_telemetry_summary[col] = {
            "mean": float(series.mean()),
            "std": float(series.std()),
            "min": float(series.min()),
            "max": float(series.max()),
            "pearson_r_with_storage_duration_days": corr_dur,
        }

    return telemetry_df, {
        "zone_diagnostics": zone_diagnostics,
        "ca_gas_diagnostics": ca_gas_diagnostics,
        "batch_telemetry_variability_and_duration_association": batch_telemetry_summary,
        "total_sensor_readings": total_readings,
    }


def build_canonical_frame(
    data_dir: Path,
    telemetry_df: pd.DataFrame,
    clusters: Dict[str, int],
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame], Dict[str, np.ndarray]]:
    """Build unified canonical modeling frame keyed strictly by batch_id.

    Guarantees that X, y, dates, crops, and groups refer to the exact same batch on every row.
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

    # Feature definitions
    f0_cols = ["crop_type"]
    X_f0 = base_df[f0_cols].copy()

    f1_num_cols = [
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
    f1_cat_cols = [
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
    X_f1 = base_df[f1_num_cols + f1_cat_cols].copy()

    # Telemetry columns
    telemetry_feature_cols = [c for c in telemetry_df.columns if c != "batch_id"]
    X_f2 = base_df[f1_num_cols + f1_cat_cols + telemetry_feature_cols].copy()

    # Planned logistics columns
    logistics_cols = ["destination_market", "destination_region", "vehicle_type", "planned_duration_hours"]
    X_f3 = base_df[f1_num_cols + f1_cat_cols + telemetry_feature_cols + logistics_cols].copy()

    feature_matrices = {"F0": X_f0, "F1": X_f1, "F2": X_f2, "F3": X_f3}

    # Strict denylist check
    for f_name, f_mat in feature_matrices.items():
        bad_cols = set(f_mat.columns).intersection(FORBIDDEN_COLUMNS)
        assert len(bad_cols) == 0, f"FORBIDDEN column leak in {f_name}: {bad_cols}"
        assert len(f_mat) == 1800, f"Length mismatch in {f_name}: {len(f_mat)}"

    # Targets (strictly aligned with base_df)
    y_dict = {
        "loss_fraction_pct": base_df["loss_fraction_pct"].values,
        "quality_status": base_df["quality_status"].values,
        "loss_ge_5": (base_df["loss_fraction_pct"] >= 5.0).astype(int).values,
        "loss_ge_15": (base_df["loss_fraction_pct"] >= 15.0).astype(int).values,
        "loss_ge_35": (base_df["loss_fraction_pct"] >= 35.0).astype(int).values,
    }

    logger.info("Canonical modeling frame successfully verified and aligned.")
    return base_df, feature_matrices, y_dict


def build_pipeline(X: pd.DataFrame, model_type: str, task: str) -> Pipeline:
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

    if task == "regression":
        if model_type == "linear":
            model = Ridge(alpha=1.0, random_state=RANDOM_SEED)
        elif model_type == "nonlinear":
            model = HistGradientBoostingRegressor(max_iter=100, max_leaf_nodes=31, random_state=RANDOM_SEED)
        else:
            raise ValueError(f"Unknown model_type {model_type}")
    elif task == "multiclass":
        if model_type == "linear":
            model = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
        elif model_type == "nonlinear":
            model = HistGradientBoostingClassifier(max_iter=100, max_leaf_nodes=31, random_state=RANDOM_SEED)
        else:
            raise ValueError(f"Unknown model_type {model_type}")
    elif task == "binary":
        if model_type == "linear":
            model = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)
        elif model_type == "nonlinear":
            model = HistGradientBoostingClassifier(max_iter=100, max_leaf_nodes=31, random_state=RANDOM_SEED)
        else:
            raise ValueError(f"Unknown model_type {model_type}")
    else:
        raise ValueError(f"Unknown task {task}")

    return Pipeline([("prep", preprocessor), ("model", model)])


def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute standard regression metrics."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    sp = float(spearmanr(y_true, y_pred).statistic) if len(np.unique(y_pred)) > 1 else 0.0
    return {"mae": mae, "rmse": rmse, "r2": r2, "spearman": sp}


def evaluate_multiclass(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """Compute 4-class status evaluation metrics."""
    labels = ["optimal", "degraded", "severe_degradation", "lost"]
    acc = float(accuracy_score(y_true, y_pred))
    bal_acc = float(balanced_accuracy_score(y_true, y_pred))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()
    return {
        "accuracy": acc,
        "balanced_accuracy": bal_acc,
        "macro_f1": f1_macro,
        "confusion_matrix": cm,
    }


def evaluate_binary(y_true: np.ndarray, y_proba: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """Compute binary severity metrics without artificial metric substitution."""
    pos_count = int(np.sum(y_true == 1))
    neg_count = int(np.sum(y_true == 0))

    if pos_count == 0 or neg_count == 0:
        return {
            "roc_auc": None,
            "pr_auc": None,
            "brier_score": float(brier_score_loss(y_true, y_proba)),
            "balanced_accuracy": None,
            "limitation": "Single class in validation set; ROC-AUC and Balanced Accuracy undefined.",
            "pos_count": pos_count,
            "neg_count": neg_count,
        }

    return {
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "brier_score": float(brier_score_loss(y_true, y_proba)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "limitation": None,
        "pos_count": pos_count,
        "neg_count": neg_count,
    }


def evaluate_ranking(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_binary_15: np.ndarray,
    batch_ids: np.ndarray,
) -> Dict[str, Any]:
    """Compute ranking and top-k retrieval metrics with deterministic label-independent tie-breaking."""
    # Spearman correlation
    sp = float(spearmanr(y_true, y_pred).statistic) if len(np.unique(y_pred)) > 1 else 0.0
    # NDCG
    ndcg_10 = float(ndcg_score([y_true], [y_pred], k=10))
    ndcg_50 = float(ndcg_score([y_true], [y_pred], k=50))

    # Deterministic label-independent tie policy: sort by (predicted_score DESC, batch_id ASC)
    # Extracts numerical ID for stable secondary sorting
    batch_ints = [int(b.split("-")[1]) for b in batch_ids]
    # Primary sort: y_pred descending; Secondary sort: batch_int ascending
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


def run_benchmark(
    feature_matrices: Dict[str, pd.DataFrame],
    y_dict: Dict[str, np.ndarray],
    ctx_df: pd.DataFrame,
) -> Dict[str, Any]:
    """Execute complete benchmark under Protocol P1 and Protocol P2."""
    logger.info("Executing benchmark suite...")

    batch_ids = ctx_df["batch_id"].values
    y_loss = y_dict["loss_fraction_pct"]
    y_status = y_dict["quality_status"]
    crops = ctx_df["crop_type"].values
    groups = ctx_df["chamber_cluster_id"].values

    # Protocol P1 Splits
    s2024_mask = ctx_df["dispatch_datetime"] < pd.Timestamp("2025-05-01")
    p1_train_idx = np.where(s2024_mask)[0]
    p1_test_idx = np.where(~s2024_mask)[0]
    assert len(p1_train_idx) == 900 and len(p1_test_idx) == 900

    # Protocol P2 Splits
    gkf = GroupKFold(n_splits=5)
    p2_folds = list(gkf.split(ctx_df, y_loss, groups))

    results: Dict[str, Any] = {
        "p1_inter_season": {},
        "p2_grouped_oof": {},
        "p2_fold_level_results": {},
        "baselines": {"p1": {}, "p2": {}},
    }

    # =========================================================================
    # 1. BASELINES (P1 & P2)
    # =========================================================================
    # P1 Continuous Baselines
    gm_p1 = float(np.median(y_loss[p1_train_idx]))
    cm_dict_p1 = {c: float(np.median(y_loss[p1_train_idx][crops[p1_train_idx] == c])) for c in set(crops[p1_train_idx])}
    pred_cm_p1 = np.array([cm_dict_p1.get(c, gm_p1) for c in crops[p1_test_idx]])

    results["baselines"]["p1"]["global_median_loss"] = evaluate_regression(y_loss[p1_test_idx], np.full(len(p1_test_idx), gm_p1))
    results["baselines"]["p1"]["crop_median_loss"] = evaluate_regression(y_loss[p1_test_idx], pred_cm_p1)
    results["baselines"]["p1"]["crop_median_ranking"] = evaluate_ranking(
        y_loss[p1_test_idx], pred_cm_p1, y_dict["loss_ge_15"][p1_test_idx], batch_ids[p1_test_idx]
    )

    # P1 Multiclass Baselines
    from collections import Counter
    maj_stat_p1 = Counter(y_status[p1_train_idx]).most_common(1)[0][0]
    c_stat_p1 = {c: Counter(y_status[p1_train_idx][crops[p1_train_idx] == c]).most_common(1)[0][0] for c in set(crops[p1_train_idx])}
    pred_c_stat_p1 = np.array([c_stat_p1.get(c, maj_stat_p1) for c in crops[p1_test_idx]])
    results["baselines"]["p1"]["global_majority_status"] = evaluate_multiclass(y_status[p1_test_idx], np.full(len(p1_test_idx), maj_stat_p1))
    results["baselines"]["p1"]["crop_majority_status"] = evaluate_multiclass(y_status[p1_test_idx], pred_c_stat_p1)

    # P1 Binary Baselines
    for thresh_name, y_bin in [
        ("loss_ge_5", y_dict["loss_ge_5"]),
        ("loss_ge_15", y_dict["loss_ge_15"]),
        ("loss_ge_35", y_dict["loss_ge_35"]),
    ]:
        p_glob = float(np.mean(y_bin[p1_train_idx]))
        c_prev = {c: float(np.mean(y_bin[p1_train_idx][crops[p1_train_idx] == c])) for c in set(crops[p1_train_idx])}
        proba_crop = np.array([c_prev.get(c, p_glob) for c in crops[p1_test_idx]])
        pred_crop = (proba_crop >= 0.5).astype(int)

        results["baselines"]["p1"][f"{thresh_name}_global_prevalence"] = evaluate_binary(
            y_bin[p1_test_idx], np.full(len(p1_test_idx), p_glob), (np.full(len(p1_test_idx), p_glob) >= 0.5).astype(int)
        )
        results["baselines"]["p1"][f"{thresh_name}_crop_prevalence"] = evaluate_binary(
            y_bin[p1_test_idx], proba_crop, pred_crop
        )

    # P2 Baselines (Grouped OOF)
    pred_p2_gm = np.zeros(len(ctx_df))
    pred_p2_cm = np.zeros(len(ctx_df))
    pred_p2_s_maj = np.empty(len(ctx_df), dtype=object)
    pred_p2_s_crop = np.empty(len(ctx_df), dtype=object)
    pred_p2_bin_crop = {t: np.zeros(len(ctx_df)) for t in ["loss_ge_5", "loss_ge_15", "loss_ge_35"]}
    pred_p2_bin_glob = {t: np.zeros(len(ctx_df)) for t in ["loss_ge_5", "loss_ge_15", "loss_ge_35"]}

    for train_idx, val_idx in p2_folds:
        gm = float(np.median(y_loss[train_idx]))
        pred_p2_gm[val_idx] = gm
        cm_d = {c: float(np.median(y_loss[train_idx][crops[train_idx] == c])) for c in set(crops[train_idx])}
        pred_p2_cm[val_idx] = [cm_d.get(c, gm) for c in crops[val_idx]]

        s_m = Counter(y_status[train_idx]).most_common(1)[0][0]
        pred_p2_s_maj[val_idx] = s_m
        s_c_d = {c: Counter(y_status[train_idx][crops[train_idx] == c]).most_common(1)[0][0] for c in set(crops[train_idx])}
        pred_p2_s_crop[val_idx] = [s_c_d.get(c, s_m) for c in crops[val_idx]]

        for thresh_name, y_bin in [
            ("loss_ge_5", y_dict["loss_ge_5"]),
            ("loss_ge_15", y_dict["loss_ge_15"]),
            ("loss_ge_35", y_dict["loss_ge_35"]),
        ]:
            p_g = float(np.mean(y_bin[train_idx]))
            pred_p2_bin_glob[thresh_name][val_idx] = p_g
            c_p_d = {c: float(np.mean(y_bin[train_idx][crops[train_idx] == c])) for c in set(crops[train_idx])}
            pred_p2_bin_crop[thresh_name][val_idx] = [c_p_d.get(c, p_g) for c in crops[val_idx]]

    results["baselines"]["p2"]["global_median_loss"] = evaluate_regression(y_loss, pred_p2_gm)
    results["baselines"]["p2"]["crop_median_loss"] = evaluate_regression(y_loss, pred_p2_cm)
    results["baselines"]["p2"]["crop_median_ranking"] = evaluate_ranking(
        y_loss, pred_p2_cm, y_dict["loss_ge_15"], batch_ids
    )
    results["baselines"]["p2"]["global_majority_status"] = evaluate_multiclass(y_status, pred_p2_s_maj)
    results["baselines"]["p2"]["crop_majority_status"] = evaluate_multiclass(y_status, pred_p2_s_crop)

    for thresh_name, y_bin in [
        ("loss_ge_5", y_dict["loss_ge_5"]),
        ("loss_ge_15", y_dict["loss_ge_15"]),
        ("loss_ge_35", y_dict["loss_ge_35"]),
    ]:
        p_g_arr = pred_p2_bin_glob[thresh_name]
        p_c_arr = pred_p2_bin_crop[thresh_name]
        results["baselines"]["p2"][f"{thresh_name}_global_prevalence"] = evaluate_binary(
            y_bin, p_g_arr, (p_g_arr >= 0.5).astype(int)
        )
        results["baselines"]["p2"][f"{thresh_name}_crop_prevalence"] = evaluate_binary(
            y_bin, p_c_arr, (p_c_arr >= 0.5).astype(int)
        )

    # =========================================================================
    # 2. BENCHMARK SUITE ACROSS F0, F1, F2, F3
    # =========================================================================
    families = ["F0", "F1", "F2", "F3"]
    models = ["linear", "nonlinear"]

    # Protocol P1 Loop
    logger.info("Running Protocol P1 (Forward Inter-Season)...")
    for fam in families:
        X = feature_matrices[fam]
        results["p1_inter_season"][fam] = {}

        for m_type in models:
            results["p1_inter_season"][fam][m_type] = {}

            # Regression
            pipe_reg = build_pipeline(X, m_type, "regression")
            pipe_reg.fit(X.iloc[p1_train_idx], y_loss[p1_train_idx])
            pred_reg = pipe_reg.predict(X.iloc[p1_test_idx])
            results["p1_inter_season"][fam][m_type]["regression_loss"] = evaluate_regression(y_loss[p1_test_idx], pred_reg)

            # Ranking
            results["p1_inter_season"][fam][m_type]["ranking"] = evaluate_ranking(
                y_loss[p1_test_idx], pred_reg, y_dict["loss_ge_15"][p1_test_idx], batch_ids[p1_test_idx]
            )

            # Multiclass
            pipe_cls = build_pipeline(X, m_type, "multiclass")
            pipe_cls.fit(X.iloc[p1_train_idx], y_status[p1_train_idx])
            pred_cls = pipe_cls.predict(X.iloc[p1_test_idx])
            results["p1_inter_season"][fam][m_type]["multiclass_status"] = evaluate_multiclass(y_status[p1_test_idx], pred_cls)

            # Binary
            for thresh_name, y_bin in [
                ("loss_ge_5", y_dict["loss_ge_5"]),
                ("loss_ge_15", y_dict["loss_ge_15"]),
                ("loss_ge_35", y_dict["loss_ge_35"]),
            ]:
                pipe_bin = build_pipeline(X, m_type, "binary")
                pipe_bin.fit(X.iloc[p1_train_idx], y_bin[p1_train_idx])
                proba_bin = pipe_bin.predict_proba(X.iloc[p1_test_idx])[:, 1]
                pred_bin = (proba_bin >= 0.5).astype(int)
                results["p1_inter_season"][fam][m_type][thresh_name] = evaluate_binary(
                    y_bin[p1_test_idx], proba_bin, pred_bin
                )

    # Protocol P2 Loop (Grouped OOF)
    logger.info("Running Protocol P2 (Chamber-Time Grouped OOF)...")
    for fam in families:
        X = feature_matrices[fam]
        results["p2_grouped_oof"][fam] = {}
        results["p2_fold_level_results"][fam] = {}

        for m_type in models:
            results["p2_grouped_oof"][fam][m_type] = {}
            results["p2_fold_level_results"][fam][m_type] = []

            oof_pred_reg = np.zeros(len(ctx_df))
            oof_pred_cls = np.empty(len(ctx_df), dtype=object)
            oof_proba_bin = {
                "loss_ge_5": np.zeros(len(ctx_df)),
                "loss_ge_15": np.zeros(len(ctx_df)),
                "loss_ge_35": np.zeros(len(ctx_df)),
            }
            oof_pred_bin = {
                "loss_ge_5": np.zeros(len(ctx_df)),
                "loss_ge_15": np.zeros(len(ctx_df)),
                "loss_ge_35": np.zeros(len(ctx_df)),
            }

            for fold_idx, (train_idx, val_idx) in enumerate(p2_folds, start=1):
                # Regression
                pipe_reg = build_pipeline(X, m_type, "regression")
                pipe_reg.fit(X.iloc[train_idx], y_loss[train_idx])
                fold_pred_reg = pipe_reg.predict(X.iloc[val_idx])
                oof_pred_reg[val_idx] = fold_pred_reg
                fold_reg_eval = evaluate_regression(y_loss[val_idx], fold_pred_reg)

                # Multiclass
                pipe_cls = build_pipeline(X, m_type, "multiclass")
                pipe_cls.fit(X.iloc[train_idx], y_status[train_idx])
                fold_pred_cls = pipe_cls.predict(X.iloc[val_idx])
                oof_pred_cls[val_idx] = fold_pred_cls
                fold_cls_eval = evaluate_multiclass(y_status[val_idx], fold_pred_cls)

                # Binary
                fold_bin_evals = {}
                for thresh_name, y_bin in [
                    ("loss_ge_5", y_dict["loss_ge_5"]),
                    ("loss_ge_15", y_dict["loss_ge_15"]),
                    ("loss_ge_35", y_dict["loss_ge_35"]),
                ]:
                    train_classes = np.unique(y_bin[train_idx])
                    if len(train_classes) < 2:
                        # Cannot fit classifier if training has only 1 class
                        fold_bin_evals[thresh_name] = {
                            "roc_auc": None,
                            "pr_auc": None,
                            "brier_score": None,
                            "balanced_accuracy": None,
                            "limitation": f"Training partition has only class {train_classes[0]}; model not fitted.",
                        }
                    else:
                        pipe_bin = build_pipeline(X, m_type, "binary")
                        pipe_bin.fit(X.iloc[train_idx], y_bin[train_idx])
                        probs = pipe_bin.predict_proba(X.iloc[val_idx])
                        p1_prob = probs[:, 1] if probs.shape[1] == 2 else probs[:, 0]
                        p_pred = (p1_prob >= 0.5).astype(int)
                        oof_proba_bin[thresh_name][val_idx] = p1_prob
                        oof_pred_bin[thresh_name][val_idx] = p_pred
                        fold_bin_evals[thresh_name] = evaluate_binary(y_bin[val_idx], p1_prob, p_pred)

                results["p2_fold_level_results"][fam][m_type].append(
                    {
                        "fold": fold_idx,
                        "val_size": len(val_idx),
                        "regression_loss": fold_reg_eval,
                        "multiclass_status": fold_cls_eval,
                        "binary_severity": fold_bin_evals,
                    }
                )

            results["p2_grouped_oof"][fam][m_type]["regression_loss"] = evaluate_regression(y_loss, oof_pred_reg)
            results["p2_grouped_oof"][fam][m_type]["ranking"] = evaluate_ranking(
                y_loss, oof_pred_reg, y_dict["loss_ge_15"], batch_ids
            )
            results["p2_grouped_oof"][fam][m_type]["multiclass_status"] = evaluate_multiclass(y_status, oof_pred_cls)

            for thresh_name, y_bin in [
                ("loss_ge_5", y_dict["loss_ge_5"]),
                ("loss_ge_15", y_dict["loss_ge_15"]),
                ("loss_ge_35", y_dict["loss_ge_35"]),
            ]:
                results["p2_grouped_oof"][fam][m_type][thresh_name] = evaluate_binary(
                    y_bin, oof_proba_bin[thresh_name], oof_pred_bin[thresh_name]
                )

    # 3. Telemetry Truncation Sensitivity (Season 2025 Test Partition)
    logger.info("Evaluating telemetry truncation sensitivity...")
    disp_2026_test_mask = ctx_df.iloc[p1_test_idx]["dispatch_datetime"] >= pd.Timestamp("2026-01-01")
    non_truncated_test_subidx = np.where(~disp_2026_test_mask)[0]
    truncated_test_subidx = np.where(disp_2026_test_mask)[0]

    truncation_results = {}
    for fam in ["F1", "F2", "F3"]:
        pipe = build_pipeline(feature_matrices[fam], "nonlinear", "regression")
        pipe.fit(feature_matrices[fam].iloc[p1_train_idx], y_loss[p1_train_idx])
        preds = pipe.predict(feature_matrices[fam].iloc[p1_test_idx])

        truncation_results[fam] = {
            "all_900_batches": evaluate_regression(y_loss[p1_test_idx], preds),
            "non_truncated_696_batches": evaluate_regression(
                y_loss[p1_test_idx][non_truncated_test_subidx], preds[non_truncated_test_subidx]
            ),
            "truncated_204_batches": evaluate_regression(
                y_loss[p1_test_idx][truncated_test_subidx], preds[truncated_test_subidx]
            ),
        }
    results["truncation_sensitivity"] = truncation_results

    # 4. Site Proxy Sensitivity
    logger.info("Evaluating site-proxy sensitivity...")
    proxy_cols_to_drop = ["district", "region", "facility_type", "commissioned_year", "capacity_tonnes"]
    X_f1_no_proxy = feature_matrices["F1"].drop(columns=proxy_cols_to_drop)
    pipe_f1_no_proxy = build_pipeline(X_f1_no_proxy, "nonlinear", "regression")
    pipe_f1_no_proxy.fit(X_f1_no_proxy.iloc[p1_train_idx], y_loss[p1_train_idx])
    pred_no_proxy_p1 = pipe_f1_no_proxy.predict(X_f1_no_proxy.iloc[p1_test_idx])

    results["proxy_sensitivity"] = {
        "f1_with_proxies_mae": results["p1_inter_season"]["F1"]["nonlinear"]["regression_loss"]["mae"],
        "f1_without_proxies_mae": float(mean_absolute_error(y_loss[p1_test_idx], pred_no_proxy_p1)),
        "f1_with_proxies_r2": results["p1_inter_season"]["F1"]["nonlinear"]["regression_loss"]["r2"],
        "f1_without_proxies_r2": float(r2_score(y_loss[p1_test_idx], pred_no_proxy_p1)),
        "dropped_features": proxy_cols_to_drop,
    }

    # 5. Within-Crop Telemetry Increment Test (Apples and Plums)
    logger.info("Evaluating within-crop telemetry lift...")
    within_crop_results = {}
    for crop in ["apples", "plums"]:
        crop_mask = crops == crop
        crop_indices = np.where(crop_mask)[0]
        crop_p1_train = np.intersect1d(crop_indices, p1_train_idx)
        crop_p1_test = np.intersect1d(crop_indices, p1_test_idx)

        c_median = float(np.median(y_loss[crop_p1_train]))
        c_base_pred = np.full(len(crop_p1_test), c_median)
        base_eval = evaluate_regression(y_loss[crop_p1_test], c_base_pred)

        pipe_f1 = build_pipeline(feature_matrices["F1"], "nonlinear", "regression")
        pipe_f1.fit(feature_matrices["F1"].iloc[crop_p1_train], y_loss[crop_p1_train])
        f1_pred = pipe_f1.predict(feature_matrices["F1"].iloc[crop_p1_test])
        f1_eval = evaluate_regression(y_loss[crop_p1_test], f1_pred)

        pipe_f2 = build_pipeline(feature_matrices["F2"], "nonlinear", "regression")
        pipe_f2.fit(feature_matrices["F2"].iloc[crop_p1_train], y_loss[crop_p1_train])
        f2_pred = pipe_f2.predict(feature_matrices["F2"].iloc[crop_p1_test])
        f2_eval = evaluate_regression(y_loss[crop_p1_test], f2_pred)

        within_crop_results[crop] = {
            "n_train": int(len(crop_p1_train)),
            "n_test": int(len(crop_p1_test)),
            "crop_median_baseline": base_eval,
            "f1_non_telemetry": f1_eval,
            "f2_telemetry": f2_eval,
            "telemetry_lift_mae": float(f1_eval["mae"] - f2_eval["mae"]),
            "telemetry_lift_r2": float(f2_eval["r2"] - f1_eval["r2"]),
        }
    results["within_crop_telemetry_test"] = within_crop_results

    # 6. Subgroup Performance across All Crops under P1 (HistGradientBoosting on F3)
    logger.info("Computing subgroup performance by crop...")
    f3_pipe = build_pipeline(feature_matrices["F3"], "nonlinear", "regression")
    f3_pipe.fit(feature_matrices["F3"].iloc[p1_train_idx], y_loss[p1_train_idx])
    f3_preds = f3_pipe.predict(feature_matrices["F3"].iloc[p1_test_idx])

    subgroup_crop = {}
    for c in sorted(list(set(crops))):
        c_sub = np.where(crops[p1_test_idx] == c)[0]
        if len(c_sub) > 0:
            subgroup_crop[c] = {
                "count": int(len(c_sub)),
                "mae": float(mean_absolute_error(y_loss[p1_test_idx][c_sub], f3_preds[c_sub])),
                "rmse": float(np.sqrt(mean_squared_error(y_loss[p1_test_idx][c_sub], f3_preds[c_sub]))),
                "r2": float(r2_score(y_loss[p1_test_idx][c_sub], f3_preds[c_sub])) if len(c_sub) > 1 else 0.0,
            }
    results["subgroup_by_crop"] = subgroup_crop

    # 7. Protocol P3: Random Split Diagnostic (Non-defensible)
    logger.info("Running non-defensible Protocol P3 random split diagnostic...")
    rng = np.random.RandomState(RANDOM_SEED)
    p3_perm = rng.permutation(len(ctx_df))
    p3_train_idx = p3_perm[:1440]
    p3_test_idx = p3_perm[1440:]

    train_clusters = set(groups[p3_train_idx])
    test_clusters = groups[p3_test_idx]
    shared_cluster_batches = sum(c in train_clusters for c in test_clusters)
    shared_cluster_pct = float(shared_cluster_batches / len(test_clusters) * 100.0)

    pipe_p3 = build_pipeline(feature_matrices["F3"], "nonlinear", "regression")
    pipe_p3.fit(feature_matrices["F3"].iloc[p3_train_idx], y_loss[p3_train_idx])
    pred_p3 = pipe_p3.predict(feature_matrices["F3"].iloc[p3_test_idx])
    results["p3_random_split_diagnostic"] = {
        "status": "NON-DEFENSIBLE DIAGNOSTIC — NOT A CANDIDATE FINAL EVALUATION PROTOCOL",
        "train_size": len(p3_train_idx),
        "test_size": len(p3_test_idx),
        "test_batches_sharing_train_cluster_pct": shared_cluster_pct,
        "f3_nonlinear_regression": evaluate_regression(y_loss[p3_test_idx], pred_p3),
    }

    # 8. Post-Dispatch Transit Leakage Diagnostic (Verification Only, Never in Features)
    r_cold_chain = float(pearsonr(ctx_df["cold_chain_incident"].astype(float), y_loss)[0])
    r_transit_temp = float(pearsonr(ctx_df["transit_temp_mean_c"], y_loss)[0])
    results["post_dispatch_transit_leakage_diagnostic"] = {
        "cold_chain_incident_pearson_r": r_cold_chain,
        "transit_temp_mean_c_pearson_r": r_transit_temp,
        "note": "Evaluation-only diagnostic confirming VDR-02 transit leakage severity; strictly excluded from model feature matrices.",
    }

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="VDR-04A Dispatch-Time Predictability Benchmark")
    parser.add_argument("--data-dir", type=str, default="sponsor_pack/data", help="Path to sponsor data directory")
    parser.add_argument(
        "--output",
        type=str,
        default="docs/data_recon/04_dispatch_predictability_results.json",
        help="Path to output JSON results",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output_path = Path(args.output)

    # 1. Integrity Gate
    integrity_meta = verify_integrity(data_dir)

    # 2. Reconstruct Chamber-Time Clusters
    sessions_df = pd.read_csv(data_dir / "storage_sessions.csv")
    clusters, n_clusters, multi_count = reconstruct_chamber_clusters(sessions_df)

    # 3. Telemetry Aggregation & Diagnostics
    sensors_df = pd.read_csv(data_dir / "sensor_readings.csv")
    zones_df = pd.read_csv(data_dir / "storage_zones.csv")
    telemetry_df, tele_meta = compute_telemetry_aggregates(sensors_df, sessions_df, zones_df)

    # 4. Assemble Unified Canonical Modeling Frame (Guaranteed 1:1 Batch Alignment)
    canonical_df, feature_matrices, y_dict = build_canonical_frame(data_dir, telemetry_df, clusters)

    # 5. Run Benchmark
    benchmark_results = run_benchmark(feature_matrices, y_dict, canonical_df)

    # 6. Build Final JSON Artifact with full schema metadata
    output_data = {
        "schema_version": "vdr-04a.v1",
        "metadata": {
            "source_git_sha": "70ab2a3ce6f060f9b2b43fcb7fb4ecd284426fdd",
            "python_version": sys.version,
            "numpy_version": np.__version__,
            "pandas_version": pd.__version__,
            "sklearn_version": sklearn.__version__,
            "random_seed": RANDOM_SEED,
            "cluster_count": n_clusters,
            "batches_in_multi_clusters": multi_count,
            "dataset_hashes": integrity_meta["dataset_hashes"],
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
            "P3_random_diagnostic": {
                "protocol": "Non-defensible 80/20 random split (seed 42)",
                "train_batches": 1440,
                "test_batches": 360,
                "cluster_leakage_pct": 94.44,
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
            "linear_classification": {
                "class": "LogisticRegression",
                "parameters": {"max_iter": 1000, "random_state": RANDOM_SEED},
            },
            "nonlinear_classification": {
                "class": "HistGradientBoostingClassifier",
                "parameters": {"max_iter": 100, "max_leaf_nodes": 31, "random_state": RANDOM_SEED},
            },
            "preprocessing": {
                "numeric": "SimpleImputer(strategy='median') + StandardScaler()",
                "categorical": "OneHotEncoder(handle_unknown='ignore', sparse_output=False)",
            },
        },
        "target_probes": {
            "continuous_loss": "loss_fraction_pct (regression)",
            "multiclass_status": "quality_status (4-class ordinal: optimal, degraded, severe_degradation, lost)",
            "binary_severity_5": "loss_fraction_pct >= 5.0% (degraded+ threshold)",
            "binary_severity_15": "loss_fraction_pct >= 15.0% (severe degradation+ threshold)",
            "binary_severity_35": "loss_fraction_pct >= 35.0% (lost threshold)",
            "ranking": "batch risk ordering by predicted loss evaluated against severe degradation (>= 15%)",
        },
        "feature_family_columns": {
            "F0": list(feature_matrices["F0"].columns),
            "F1": list(feature_matrices["F1"].columns),
            "F2": list(feature_matrices["F2"].columns),
            "F3": list(feature_matrices["F3"].columns),
        },
        "telemetry_diagnostics": tele_meta,
        "benchmark_results": benchmark_results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    logger.info(f"VDR-04A benchmark complete. Results saved to {output_path}")


if __name__ == "__main__":
    main()
