"""VDR-05: Planned Logistics Signal Decomposition & Proxy Robustness Audit.

Authoritative reproduction and logistics signal decomposition runner for VDR-05 evidence package.
Strictly adheres to ADR 0002 cutoff at T_assess = T_dispatch.
Zero usage of forbidden arrival QC, post-dispatch transit fields,
future telemetry, or target outcomes in predictive feature matrices.

Evaluates the exact 10 predictive feature families:
1. C                                      (37 cols)
2. C + destination_market                 (38 cols)
3. C + destination_region                 (38 cols)
4. C + vehicle_type                       (38 cols)
5. C + planned_duration_hours             (38 cols)
6. C + L                                  (41 cols)
7. C + L without destination_market       (40 cols)
8. C + L without destination_region       (40 cols)
9. C + L without vehicle_type             (40 cols)
10. C + L without planned_duration_hours   (40 cols)

Performs comprehensive proxy/confounding diagnostics:
- Categorical Normalized Mutual Information (NMI) against 11 diagnostic variables
- Eta-squared (eta^2) for planned_duration_hours against 11 diagnostic variables
- Internal logistics redundancy (NMI and eta^2)
- Compact contingency evidence
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import platform
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    ndcg_score,
    normalized_mutual_info_score,
    r2_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vdr05")

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

# Authoritative set of 77 sensor telemetry column names from VDR-04B
TELEMETRY_COLUMNS_77 = {
    "air_temp_abs_dev_max", "air_temp_abs_dev_mean", "air_temp_frac_above_target",
    "air_temp_frac_below_target", "air_temp_signed_dev_mean", "air_temperature_c_first",
    "air_temperature_c_last", "air_temperature_c_max", "air_temperature_c_mean",
    "air_temperature_c_min", "air_temperature_c_missing_frac", "air_temperature_c_p10",
    "air_temperature_c_p90", "air_temperature_c_slope_per_day", "air_temperature_c_std",
    "co2_ppm_first", "co2_ppm_last", "co2_ppm_max", "co2_ppm_mean", "co2_ppm_min",
    "co2_ppm_missing_frac", "co2_ppm_p10", "co2_ppm_p90", "co2_ppm_slope_per_day",
    "co2_ppm_std", "condensation_flag_frac_true", "condensation_flag_transitions",
    "cooling_on_frac_true", "cooling_on_transitions", "defrost_on_frac_true",
    "defrost_on_transitions", "dew_point_c_first", "dew_point_c_last", "dew_point_c_max",
    "dew_point_c_mean", "dew_point_c_min", "dew_point_c_missing_frac", "dew_point_c_p10",
    "dew_point_c_p90", "dew_point_c_slope_per_day", "dew_point_c_std", "o2_pct_first",
    "o2_pct_last", "o2_pct_max", "o2_pct_mean", "o2_pct_min", "o2_pct_missing_frac",
    "o2_pct_p10", "o2_pct_p90", "o2_pct_slope_per_day", "o2_pct_std",
    "produce_surface_temperature_c_first", "produce_surface_temperature_c_last",
    "produce_surface_temperature_c_max", "produce_surface_temperature_c_mean",
    "produce_surface_temperature_c_min", "produce_surface_temperature_c_missing_frac",
    "produce_surface_temperature_c_p10", "produce_surface_temperature_c_p90",
    "produce_surface_temperature_c_slope_per_day", "produce_surface_temperature_c_std",
    "relative_humidity_pct_first", "relative_humidity_pct_last", "relative_humidity_pct_max",
    "relative_humidity_pct_mean", "relative_humidity_pct_min",
    "relative_humidity_pct_missing_frac", "relative_humidity_pct_p10",
    "relative_humidity_pct_p90", "relative_humidity_pct_slope_per_day",
    "relative_humidity_pct_std", "rh_abs_dev_max", "rh_abs_dev_mean",
    "rh_frac_above_target", "rh_frac_below_target", "rh_signed_dev_mean",
    "telemetry_reading_count",
}

# Accepted 64-character SHA256 hashes from committed VDR-04B snapshot (04b_telemetry_ablation_results.json)
EXPECTED_DATASET_HASHES: Dict[str, str] = {
    "batches": "bbaf3cb4064ccdefed5eaca0b3fe7d6303bd918b1abc09a8c27cb20309d6072b",
    "storage_sessions": "f38a99dfeb808eaab3b3d91d0494d303649131ee2d5de9a6efa0da99fdf9e04f",
    "facilities": "148de414dcff6d601d327ce17414d8b9e04aaa38c6bc0ecbb769be32d6f3a960",
    "storage_zones": "e2c4b7170c47ab0896ed962c588256e3407d84d30afa758372a704d8085c4ee4",
    "quality_checks": "95ccf7d6d898249f6bf444a874817be74b7ce4338b3099f3bf8687f22fa9b627",
    "shipments": "bfad682700f58936ca383868febd09181bd810e81bd3287fa28d16d204ea9796",
    "historical_quality_outcomes": "567334f44f41b980c67de496736c077dc1d980b4cb02c14ee355597087732606",
    "sensor_readings": "6b27adaf43a6646d32cccddc95872bfed03a6220075d9508ccc54be5bdf9edbb",
}

# Pre-validate all configured expected hashes are valid 64-character lowercase hexadecimal strings
_HEX_64_PATTERN = re.compile(r"^[0-9a-f]{64}$")
for _ds_name, _exp_hash in EXPECTED_DATASET_HASHES.items():
    if not _HEX_64_PATTERN.match(_exp_hash):
        raise ValueError(
            f"Configured expected hash for {_ds_name} is not a valid 64-character lowercase hex SHA256 string: '{_exp_hash}'"
        )


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA256 hex digest of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_eta_squared(
    df: pd.DataFrame,
    cat_col: str,
    num_col: str,
) -> Dict[str, Any]:
    """Compute eta-squared (proportion of variance explained) for num_col grouped by cat_col.

    If total sum of squares <= 0.0, returns eta_squared=None with reason='zero_total_variance'.
    """
    n_rows = len(df)
    n_groups = int(df[cat_col].nunique())
    y = df[num_col].values.astype(float)
    y_mean = float(np.mean(y))
    ss_total = float(np.sum((y - y_mean) ** 2))

    if ss_total <= 0.0:
        return {
            "eta_squared": None,
            "reason": "zero_total_variance",
            "n_rows": n_rows,
            "n_groups": n_groups,
        }

    groups = df.groupby(cat_col, observed=False)[num_col]
    ss_between = float(sum(len(g) * (g.mean() - y_mean) ** 2 for _, g in groups))
    eta2 = float(ss_between / ss_total)
    return {
        "eta_squared": eta2,
        "reason": None,
        "n_rows": n_rows,
        "n_groups": n_groups,
    }


def eta2_sort_key(record: Dict[str, Any]) -> Tuple[int, float, str]:
    """Deterministic sort key for eta^2 records that safely handles None."""
    val = record.get("eta_squared")
    name = str(record.get("diagnostic_field", record.get("grouping_field", "")))
    if val is not None:
        return (0, -float(val), name)
    return (1, 0.0, name)


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
        actual_hash = compute_file_sha256(path)
        expected_hash = EXPECTED_DATASET_HASHES.get(name)
        if expected_hash is None:
            raise KeyError(f"No expected hash configured for dataset: {name}")
        if actual_hash != expected_hash:
            raise ValueError(
                f"Dataset integrity mismatch for {name}:\n"
                f"expected={expected_hash}\n"
                f"actual={actual_hash}"
            )
        hashes[name] = actual_hash

    # Load tables for cardinality checks
    batches_df = pd.read_csv(files["batches"])
    sessions_df = pd.read_csv(files["storage_sessions"])
    facilities_df = pd.read_csv(files["facilities"])
    zones_df = pd.read_csv(files["storage_zones"])
    qc_df = pd.read_csv(files["quality_checks"])
    shipments_df = pd.read_csv(files["shipments"])
    outcomes_df = pd.read_csv(files["historical_quality_outcomes"])
    sensors_df_len = sum(1 for _ in open(files["sensor_readings"], "rb")) - 1

    # 1. Primary Key Uniqueness
    assert batches_df["batch_id"].is_unique, "batches.batch_id PK is not unique"
    assert sessions_df["storage_session_id"].is_unique, "storage_sessions.storage_session_id PK is not unique"
    assert facilities_df["facility_id"].is_unique, "facilities.facility_id PK is not unique"
    assert zones_df["zone_id"].is_unique, "storage_zones.zone_id PK is not unique"
    assert shipments_df["shipment_id"].is_unique, "shipments.shipment_id PK is not unique"

    # 2. Strict Exact Cardinalities
    assert len(batches_df) == 1800, f"Expected 1800 batches, got {len(batches_df)}"
    assert len(sessions_df) == 1800, f"Expected 1800 storage_sessions, got {len(sessions_df)}"
    assert len(shipments_df) == 1800, f"Expected 1800 shipments, got {len(shipments_df)}"
    assert len(outcomes_df) == 1800, f"Expected 1800 outcomes, got {len(outcomes_df)}"
    assert len(qc_df) == 5400, f"Expected 5400 QC checks, got {len(qc_df)}"
    assert len(facilities_df) == 10, f"Expected 10 facilities, got {len(facilities_df)}"
    assert len(zones_df) == 25, f"Expected 25 storage zones, got {len(zones_df)}"
    assert sensors_df_len == 669665, f"Expected 669665 sensor readings, got {sensors_df_len}"

    logger.info("Integrity checks passed successfully.")
    return {
        "dataset_hashes": hashes,
        "dataset_integrity_verification": {
            "status": "ALL_PASSED",
            "verified_count": len(hashes),
            "expected_hashes": EXPECTED_DATASET_HASHES,
        },
        "row_counts": {
            "batches": len(batches_df),
            "storage_sessions": len(sessions_df),
            "shipments": len(shipments_df),
            "historical_quality_outcomes": len(outcomes_df),
            "quality_checks": len(qc_df),
            "facilities": len(facilities_df),
            "storage_zones": len(zones_df),
            "sensor_readings": sensors_df_len,
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


def build_canonical_frame(
    data_dir: Path,
    clusters: Dict[str, int],
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame], Dict[str, np.ndarray]]:
    """Build unified canonical modeling frame keyed strictly by batch_id.

    Constructs the exact 10 feature families:
      1. C                                      (37 cols)
      2. C + destination_market                 (38 cols)
      3. C + destination_region                 (38 cols)
      4. C + vehicle_type                       (38 cols)
      5. C + planned_duration_hours             (38 cols)
      6. C + L                                  (41 cols)
      7. C + L without destination_market       (40 cols)
      8. C + L without destination_region       (40 cols)
      9. C + L without vehicle_type             (40 cols)
      10. C + L without planned_duration_hours   (40 cols)
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

    # Validate 1:1 and relational joins
    base_df = base_df.merge(sessions_df, on="batch_id", validate="one_to_one")
    base_df = base_df.merge(zones_df, on="zone_id", validate="many_to_one")
    base_df = base_df.merge(facilities_df, on="facility_id", validate="many_to_one")
    base_df = base_df.merge(shipments_df, on="batch_id", validate="one_to_one")
    base_df = base_df.merge(outcomes_df, on="batch_id", validate="one_to_one")

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

    # Derived operational season (P1 season membership)
    base_df["operational_season"] = np.where(
        base_df["dispatch_datetime"] < pd.Timestamp("2025-05-01"),
        "Season 2024",
        "Season 2025",
    )

    # 1. Context feature definitions (C / F1) - exactly 37 columns
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

    # 2. Planned logistics columns (L)
    M = "destination_market"
    R = "destination_region"
    V = "vehicle_type"
    D = "planned_duration_hours"
    logistics_cols = [M, R, V, D]

    # Construct the exact 10 feature matrices
    feature_matrices: Dict[str, pd.DataFrame] = {
        "C": base_df[c_cols].copy(),
        "C + destination_market": base_df[c_cols + [M]].copy(),
        "C + destination_region": base_df[c_cols + [R]].copy(),
        "C + vehicle_type": base_df[c_cols + [V]].copy(),
        "C + planned_duration_hours": base_df[c_cols + [D]].copy(),
        "C + L": base_df[c_cols + logistics_cols].copy(),
        "C + L without destination_market": base_df[c_cols + [R, V, D]].copy(),
        "C + L without destination_region": base_df[c_cols + [M, V, D]].copy(),
        "C + L without vehicle_type": base_df[c_cols + [M, R, D]].copy(),
        "C + L without planned_duration_hours": base_df[c_cols + [M, R, V]].copy(),
    }

    # Assert exact column counts
    expected_counts = {
        "C": 37,
        "C + destination_market": 38,
        "C + destination_region": 38,
        "C + vehicle_type": 38,
        "C + planned_duration_hours": 38,
        "C + L": 41,
        "C + L without destination_market": 40,
        "C + L without destination_region": 40,
        "C + L without vehicle_type": 40,
        "C + L without planned_duration_hours": 40,
    }
    for name, exp_count in expected_counts.items():
        actual = feature_matrices[name].shape[1]
        assert actual == exp_count, f"{name} expected {exp_count} columns, got {actual}"

    # Strict isolation assertions across all 10 matrices:
    for name, mat in feature_matrices.items():
        cols = set(mat.columns)
        # 1. No forbidden columns
        forbidden_present = cols.intersection(FORBIDDEN_COLUMNS)
        assert len(forbidden_present) == 0, f"Forbidden columns present in {name}: {forbidden_present}"
        # 2. No telemetry columns
        telemetry_present = cols.intersection(TELEMETRY_COLUMNS_77)
        assert len(telemetry_present) == 0, f"Telemetry features found in predictive matrix {name}: {telemetry_present}"
        # 3. No diagnostic IDs
        for ident in ["facility_id", "zone_id", "batch_id", "storage_session_id", "shipment_id"]:
            assert ident not in cols, f"Identifier {ident} leaked into predictive matrix {name}"

    # Target outcomes
    y_dict = {
        "loss_fraction_pct": base_df["loss_fraction_pct"].values,
        "loss_ge_15": (base_df["loss_fraction_pct"].values >= 15.0).astype(int),
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


def classify_delta_direction(metric_name: str, delta: float, tol: float = 1e-9) -> str:
    """Classify delta direction as favorable, neutral, or adverse.

    Lower is better: MAE, RMSE
    Higher is better: R², Spearman, NDCG, Precision, Recall
    """
    if metric_name in ["mae", "rmse"]:
        if delta < -tol:
            return "favorable"
        elif delta > tol:
            return "adverse"
        else:
            return "neutral"
    else:
        if delta > tol:
            return "favorable"
        elif delta < -tol:
            return "adverse"
        else:
            return "neutral"


def compute_directional_deltas(
    ref_metrics: Dict[str, Any],
    target_metrics: Dict[str, Any],
) -> Dict[str, Any]:
    """Compute pairwise deltas: (target_metrics - ref_metrics) with explicit directional classification."""
    cont_deltas = {}
    for k in ref_metrics["continuous"]:
        val = float(target_metrics["continuous"][k] - ref_metrics["continuous"][k])
        cont_deltas[k] = {
            "delta": val,
            "direction": classify_delta_direction(k, val),
        }

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
        val = float(target_metrics["ranking"][k] - ref_metrics["ranking"][k])
        rank_deltas[k] = {
            "delta": val,
            "direction": classify_delta_direction(k, val),
        }

    return {
        "continuous_deltas": cont_deltas,
        "ranking_deltas": rank_deltas,
    }


def run_predictive_benchmarks(
    feature_matrices: Dict[str, pd.DataFrame],
    y_dict: Dict[str, np.ndarray],
    ctx_df: pd.DataFrame,
) -> Dict[str, Any]:
    """Execute complete 10-family predictive benchmark under P1 and P2."""
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
    families = list(feature_matrices.keys())
    models = ["linear", "nonlinear"]

    p1_results: Dict[str, Any] = {}
    p2_oof_results: Dict[str, Any] = {}
    p2_fold_results: Dict[str, Any] = {}

    logger.info(f"Executing Protocol P1 across all {len(families)} families...")
    for fam in families:
        p1_results[fam] = {}
        X = feature_matrices[fam]
        X_train, X_test = X.iloc[p1_train_idx], X.iloc[p1_test_idx]
        y_train, y_test = y_loss[p1_train_idx], y_loss[p1_test_idx]
        y_bin_test = y_bin15[p1_test_idx]
        b_test = batch_ids[p1_test_idx]

        for m_type in models:
            pipe = build_pipeline(X, m_type)
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_test)
            p1_results[fam][m_type] = compute_metrics_package(y_test, preds, y_bin_test, b_test)

    logger.info(f"Executing Protocol P2 across all {len(families)} families...")
    for fam in families:
        p2_oof_results[fam] = {}
        p2_fold_results[fam] = {}
        X = feature_matrices[fam]

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

    # =========================================================================
    # 3. PAIRWISE COMPARISONS AND DIRECTIONAL DELTAS
    # =========================================================================
    # A. Single-field additions: C -> C + Li
    single_field_pairs = [
        ("destination_market", "C", "C + destination_market"),
        ("destination_region", "C", "C + destination_region"),
        ("vehicle_type", "C", "C + vehicle_type"),
        ("planned_duration_hours", "C", "C + planned_duration_hours"),
    ]

    # B. Leave-one-out contributions: C + (L - Li) -> C + L
    loo_pairs = [
        ("destination_market", "C + L without destination_market", "C + L"),
        ("destination_region", "C + L without destination_region", "C + L"),
        ("vehicle_type", "C + L without vehicle_type", "C + L"),
        ("planned_duration_hours", "C + L without planned_duration_hours", "C + L"),
    ]

    # C. Full-family anchor: C -> C + L
    anchor_pair = [("full_logistics_family", "C", "C + L")]

    def compute_pair_set(pairs_list):
        p1_deltas = {}
        p2_oof_deltas = {}
        p2_fold_deltas = {}

        for label, ref_fam, tgt_fam in pairs_list:
            p1_deltas[label] = {}
            p2_oof_deltas[label] = {}
            p2_fold_deltas[label] = {}

            for m_type in models:
                p1_deltas[label][m_type] = compute_directional_deltas(
                    p1_results[ref_fam][m_type], p1_results[tgt_fam][m_type]
                )
                p2_oof_deltas[label][m_type] = compute_directional_deltas(
                    p2_oof_results[ref_fam][m_type], p2_oof_results[tgt_fam][m_type]
                )

                fold_d = []
                for f_idx in range(5):
                    f_ref = p2_fold_results[ref_fam][m_type][f_idx]["metrics"]
                    f_tgt = p2_fold_results[tgt_fam][m_type][f_idx]["metrics"]
                    fold_d.append(
                        {
                            "fold": f_idx + 1,
                            "deltas": compute_directional_deltas(f_ref, f_tgt),
                        }
                    )
                p2_fold_deltas[label][m_type] = fold_d

        return {
            "p1_inter_season": p1_deltas,
            "p2_grouped_oof": p2_oof_deltas,
            "p2_folds": p2_fold_deltas,
        }

    pairwise_deltas = {
        "single_field_additions": compute_pair_set(single_field_pairs),
        "leave_one_out_contributions": compute_pair_set(loo_pairs),
        "full_family_anchor": compute_pair_set(anchor_pair),
    }

    return {
        "baselines": baselines,
        "p1_inter_season": p1_results,
        "p2_grouped_oof": p2_oof_results,
        "p2_fold_level_results": p2_fold_results,
        "pairwise_deltas": pairwise_deltas,
    }


def compare_vdr04b_reproduction(
    reproduced: Dict[str, Any],
    historical_path: Path,
) -> Dict[str, Any]:
    """Verify replication of baseline, C, and C+L against historical VDR-04B evidence."""
    if not historical_path.exists():
        raise FileNotFoundError(
            f"Mandatory historical VDR-04B reference file not found at '{historical_path}'. "
            "VDR-05 requires historical reproduction verification before proceeding."
        )

    with open(historical_path, "r", encoding="utf-8") as f:
        hist_data = json.load(f)

    hist_ab = hist_data["ablation_results"]
    hist_p1 = hist_ab["p1_inter_season"]
    hist_p2 = hist_ab["p2_grouped_oof"]
    hist_base = hist_ab["baselines"]

    rep_p1 = reproduced["p1_inter_season"]
    rep_p2 = reproduced["p2_grouped_oof"]
    rep_base = reproduced["baselines"]

    comparison: Dict[str, Any] = {
        "baselines": {},
        "p1": {},
        "p2": {},
        "max_absolute_difference": 0.0,
    }
    max_diff = 0.0

    # 1. Baseline comparisons
    # P1 Baseline
    comparison["baselines"]["p1_crop_median"] = {}
    for m in ["mae", "rmse", "r2", "spearman"]:
        h_val = hist_base["p1_crop_median"]["continuous"][m]
        r_val = rep_base["p1_crop_median"]["continuous"][m]
        diff = abs(h_val - r_val)
        max_diff = max(max_diff, diff)
        comparison["baselines"]["p1_crop_median"][f"cont_{m}"] = {
            "historical": h_val,
            "reproduced": r_val,
            "diff": diff,
        }
    for m in ["ndcg_10", "ndcg_50", "precision_at_10", "precision_at_50", "recall_at_10", "recall_at_50"]:
        h_val = hist_base["p1_crop_median"]["ranking"][m]
        r_val = rep_base["p1_crop_median"]["ranking"][m]
        diff = abs(h_val - r_val)
        max_diff = max(max_diff, diff)
        comparison["baselines"]["p1_crop_median"][f"rank_{m}"] = {
            "historical": h_val,
            "reproduced": r_val,
            "diff": diff,
        }

    # P2 Baseline
    comparison["baselines"]["p2_crop_median_oof"] = {}
    for m in ["mae", "rmse", "r2", "spearman"]:
        h_val = hist_base["p2_crop_median_oof"]["continuous"][m]
        r_val = rep_base["p2_crop_median_oof"]["continuous"][m]
        diff = abs(h_val - r_val)
        max_diff = max(max_diff, diff)
        comparison["baselines"]["p2_crop_median_oof"][f"cont_{m}"] = {
            "historical": h_val,
            "reproduced": r_val,
            "diff": diff,
        }
    for m in ["ndcg_10", "ndcg_50", "precision_at_10", "precision_at_50", "recall_at_10", "recall_at_50"]:
        h_val = hist_base["p2_crop_median_oof"]["ranking"][m]
        r_val = rep_base["p2_crop_median_oof"]["ranking"][m]
        diff = abs(h_val - r_val)
        max_diff = max(max_diff, diff)
        comparison["baselines"]["p2_crop_median_oof"][f"rank_{m}"] = {
            "historical": h_val,
            "reproduced": r_val,
            "diff": diff,
        }

    # 2. C and C+L comparisons
    overlapping_families = [("C", "C"), ("C + L", "C+L")]
    for fam_05, fam_04b in overlapping_families:
        comparison["p1"][fam_05] = {}
        comparison["p2"][fam_05] = {}

        for m_type in ["linear", "nonlinear"]:
            comparison["p1"][fam_05][m_type] = {}
            comparison["p2"][fam_05][m_type] = {}

            # P1 continuous
            for m in ["mae", "rmse", "r2", "spearman"]:
                h_val = hist_p1[fam_04b][m_type]["continuous"][m]
                r_val = rep_p1[fam_05][m_type]["continuous"][m]
                diff = abs(h_val - r_val)
                max_diff = max(max_diff, diff)
                comparison["p1"][fam_05][m_type][f"cont_{m}"] = {
                    "historical": h_val,
                    "reproduced": r_val,
                    "diff": diff,
                }

            # P1 ranking
            for m in ["ndcg_10", "ndcg_50", "precision_at_10", "precision_at_50", "recall_at_10", "recall_at_50"]:
                h_val = hist_p1[fam_04b][m_type]["ranking"][m]
                r_val = rep_p1[fam_05][m_type]["ranking"][m]
                diff = abs(h_val - r_val)
                max_diff = max(max_diff, diff)
                comparison["p1"][fam_05][m_type][f"rank_{m}"] = {
                    "historical": h_val,
                    "reproduced": r_val,
                    "diff": diff,
                }

            # P2 continuous
            for m in ["mae", "rmse", "r2", "spearman"]:
                h_val = hist_p2[fam_04b][m_type]["continuous"][m]
                r_val = rep_p2[fam_05][m_type]["continuous"][m]
                diff = abs(h_val - r_val)
                max_diff = max(max_diff, diff)
                comparison["p2"][fam_05][m_type][f"cont_{m}"] = {
                    "historical": h_val,
                    "reproduced": r_val,
                    "diff": diff,
                }

            # P2 ranking
            for m in ["ndcg_10", "ndcg_50", "precision_at_10", "precision_at_50", "recall_at_10", "recall_at_50"]:
                h_val = hist_p2[fam_04b][m_type]["ranking"][m]
                r_val = rep_p2[fam_05][m_type]["ranking"][m]
                diff = abs(h_val - r_val)
                max_diff = max(max_diff, diff)
                comparison["p2"][fam_05][m_type][f"rank_{m}"] = {
                    "historical": h_val,
                    "reproduced": r_val,
                    "diff": diff,
                }

    comparison["max_absolute_difference"] = float(max_diff)
    comparison["parity_status"] = (
        "EXACT_OR_NUMERICALLY_EQUIVALENT" if max_diff < 1e-6 else "DISCREPANCY_DETECTED"
    )
    logger.info(
        f"VDR-04B Replication Check: max diff = {max_diff:.8e}, status = {comparison['parity_status']}"
    )
    assert max_diff < 1e-6, f"VDR-04B replication failed with max diff {max_diff}"
    return comparison


def compute_proxy_diagnostics(base_df: pd.DataFrame) -> Dict[str, Any]:
    """Compute descriptive categorical NMI and duration eta^2 diagnostics."""
    logger.info("Computing proxy and confounding diagnostics...")

    # Required diagnostic variables (at least 11)
    diagnostic_variables = [
        "crop_type",
        "variety",
        "origin_region",
        "harvest_conditions",
        "facility_id",
        "zone_id",
        "facility_type",
        "region",
        "district",
        "zone_type",
        "operational_season",
    ]

    # Verify presence
    for col in diagnostic_variables:
        assert col in base_df.columns, f"Missing diagnostic variable: {col}"

    logistics_categorical = ["destination_market", "destination_region", "vehicle_type"]
    duration_col = "planned_duration_hours"

    n_rows = len(base_df)

    # 1. Categorical NMI against all diagnostic variables
    nmi_records = []
    for log_field in logistics_categorical:
        card_log = int(base_df[log_field].nunique())
        for diag_field in diagnostic_variables:
            card_diag = int(base_df[diag_field].nunique())
            nmi = float(
                normalized_mutual_info_score(
                    base_df[log_field], base_df[diag_field], average_method="arithmetic"
                )
            )
            nmi_records.append(
                {
                    "logistics_field": log_field,
                    "diagnostic_field": diag_field,
                    "nmi": nmi,
                    "n_rows": n_rows,
                    "cardinality_logistics": card_log,
                    "cardinality_diagnostic": card_diag,
                }
            )

    # 2. Planned duration hours eta^2 against diagnostic variables
    eta2_records = []
    for diag_field in diagnostic_variables:
        res = compute_eta_squared(base_df, diag_field, duration_col)
        eta2_records.append(
            {
                "diagnostic_field": diag_field,
                "eta_squared": res["eta_squared"],
                "reason": res["reason"],
                "n_rows": res["n_rows"],
                "number_of_groups": res["n_groups"],
            }
        )

    # 3. Internal logistics redundancy
    internal_nmi = [
        {
            "field_1": "destination_market",
            "field_2": "destination_region",
            "nmi": float(
                normalized_mutual_info_score(
                    base_df["destination_market"],
                    base_df["destination_region"],
                    average_method="arithmetic",
                )
            ),
        },
        {
            "field_1": "destination_market",
            "field_2": "vehicle_type",
            "nmi": float(
                normalized_mutual_info_score(
                    base_df["destination_market"],
                    base_df["vehicle_type"],
                    average_method="arithmetic",
                )
            ),
        },
        {
            "field_1": "destination_region",
            "field_2": "vehicle_type",
            "nmi": float(
                normalized_mutual_info_score(
                    base_df["destination_region"],
                    base_df["vehicle_type"],
                    average_method="arithmetic",
                )
            ),
        },
    ]

    internal_duration_eta2 = []
    for log_cat in logistics_categorical:
        res = compute_eta_squared(base_df, log_cat, duration_col)
        internal_duration_eta2.append(
            {
                "grouping_field": log_cat,
                "eta_squared": res["eta_squared"],
                "reason": res["reason"],
                "n_groups": res["n_groups"],
            }
        )

    # 4. Compact contingency evidence
    # Market to region, duration, vehicle summary
    market_summary = []
    for (m, r), g in base_df.groupby(["destination_market", "destination_region"], observed=False):
        market_summary.append(
            {
                "destination_market": str(m),
                "destination_region": str(r),
                "planned_duration_hours": float(g["planned_duration_hours"].iloc[0]),
                "batch_count": int(len(g)),
                "vehicle_type_distribution": {
                    str(k): int(v) for k, v in g["vehicle_type"].value_counts().items()
                },
            }
        )

    # Vehicle type by destination region
    veh_by_region = []
    for (r, v), g in base_df.groupby(["destination_region", "vehicle_type"], observed=False):
        veh_by_region.append(
            {
                "destination_region": str(r),
                "vehicle_type": str(v),
                "batch_count": int(len(g)),
                "mean_duration_hours": float(g["planned_duration_hours"].mean()),
            }
        )

    # Sort NMI and eta2 records descriptively
    nmi_sorted = sorted(nmi_records, key=lambda x: x["nmi"], reverse=True)
    eta2_sorted = sorted(eta2_records, key=eta2_sort_key)

    return {
        "categorical_nmi": nmi_records,
        "categorical_nmi_sorted": nmi_sorted,
        "duration_eta_squared": eta2_records,
        "duration_eta_squared_sorted": eta2_sorted,
        "internal_logistics_associations": {
            "categorical_nmi": internal_nmi,
            "duration_eta_squared": internal_duration_eta2,
        },
        "compact_contingency_evidence": {
            "market_to_region_duration_vehicle": market_summary,
            "vehicle_by_region": veh_by_region,
        },
    }


def main() -> None:
    """Main execution function for VDR-05."""
    parser = argparse.ArgumentParser(
        description="VDR-05: Planned Logistics Signal Decomposition & Proxy Robustness Audit"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("sponsor_pack/data"),
        help="Path to directory containing input CSV tables",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/data_recon/05_planned_logistics_signal_audit_results.json"),
        help="Path to output JSON results artifact",
    )
    parser.add_argument(
        "--historical-vdr04b",
        type=Path,
        default=Path("docs/data_recon/04b_telemetry_ablation_results.json"),
        help="Path to committed VDR-04B results JSON for mandatory reproduction gate",
    )
    args = parser.parse_args()

    # Step 1: Pre-analysis integrity gate
    integrity_info = verify_integrity(args.data_dir)

    # Step 2: Reconstruct 157 chamber clusters
    sessions_df = pd.read_csv(args.data_dir / "storage_sessions.csv")
    clusters, cluster_count, multi_cluster_batches = reconstruct_chamber_clusters(sessions_df)

    # Step 3: Canonical modeling frame and feature matrices
    base_df, feature_matrices, y_dict = build_canonical_frame(args.data_dir, clusters)

    # Step 4: Run predictive benchmarks across all 10 feature families
    bench_results = run_predictive_benchmarks(feature_matrices, y_dict, base_df)

    # Step 5: Mandatory VDR-04B reproduction gate
    vdr04b_repro = compare_vdr04b_reproduction(bench_results, args.historical_vdr04b)

    # Step 6: Proxy and confounding diagnostics
    proxy_diag = compute_proxy_diagnostics(base_df)

    # Build final serializable output dictionary
    output_data = {
        "schema_version": "vdr-05.v1",
        "metadata": {
            "source_git_sha": "6d0e4a50c36937f01b769a16a99bfa03af458c66",
            "task_branch": "victor/vdr-05-logistics-signal-audit",
            "environment": {
                "OS": platform.platform(),
                "Python": sys.version,
                "NumPy": np.__version__,
                "Pandas": pd.__version__,
                "scikit-learn": sklearn.__version__,
                "SciPy": getattr(sys.modules.get("scipy"), "__version__", "unknown"),
            },
            "random_seed": RANDOM_SEED,
            "cluster_count": cluster_count,
            "batches_in_multi_clusters": multi_cluster_batches,
            "dataset_hashes": integrity_info["dataset_hashes"],
            "dataset_integrity_verification": integrity_info["dataset_integrity_verification"],
            "dataset_row_counts": integrity_info["row_counts"],
        },
        "experiment_design": {
            "objective": "Determine which of the four accepted planned-logistics fields account for the predictive/ranking association observed in VDR-04B, how redundant those fields are with one another, and how strongly they are descriptively associated with crop/site/season identity proxies.",
            "logistics_fields": [
                "destination_market",
                "destination_region",
                "vehicle_type",
                "planned_duration_hours",
            ],
            "feature_families": {name: list(mat.columns) for name, mat in feature_matrices.items()},
            "feature_counts": {name: mat.shape[1] for name, mat in feature_matrices.items()},
        },
        "split_definitions": {
            "P1_inter_season": {
                "train_season": "Season 2024 (dispatch_datetime < 2025-05-01, 900 batches)",
                "test_season": "Season 2025 (dispatch_datetime >= 2025-05-01, 900 batches)",
                "total_batches": 1800,
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
        "diagnostic_column_boundary": {
            "diagnostic_only_fields": [
                "facility_id",
                "zone_id",
                "batch_id",
                "storage_session_id",
                "shipment_id",
                "operational_season",
            ],
            "facility_id_predictive": False,
            "zone_id_predictive": False,
            "batch_id_predictive": False,
            "telemetry_predictive": False,
            "arrival_qc_predictive": False,
            "realized_transit_predictive": False,
            "target_outcomes_predictive": False,
        },
        "vdr04b_reproduction": vdr04b_repro,
        "predictive_results": {
            "baselines": bench_results["baselines"],
            "p1_inter_season": bench_results["p1_inter_season"],
            "p2_grouped_oof": bench_results["p2_grouped_oof"],
            "p2_fold_level_evidence": bench_results["p2_fold_level_results"],
        },
        "pairwise_deltas": bench_results["pairwise_deltas"],
        "proxy_diagnostics": proxy_diag,
    }

    # Ensure parent output dir exists
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"VDR-05 audit complete. Results saved to {args.output}")


if __name__ == "__main__":
    main()
