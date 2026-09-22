"""Controlled offline Season-2024 fit; never imported by application startup."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.analytics.crop_median_baseline import CropMedianTrainingRecord, fit_crop_median_baseline
from app.runtime.artifact import (
    BaselineArtifact, DATASET_ID, ENGINE_VERSION, FAMILY, SOURCE_HASHES,
    load_pinned_snapshot, membership_sha256, partition_membership,
)


def generate_artifact(data_dir: Path) -> BaselineArtifact:
    snapshot = load_pinned_snapshot(data_dir)
    training, _ = partition_membership(snapshot)
    outcomes: dict[str, list[dict[str, str]]] = {}
    for row in snapshot["historical_quality_outcomes"].rows:
        outcomes.setdefault(row["batch_id"], []).append(row)
    records = []
    for batch in snapshot["batches"].rows:
        if batch["batch_id"] not in training:
            continue
        matches = outcomes.get(batch["batch_id"], [])
        if len(matches) != 1:
            raise ValueError("Expected exactly one historical outcome per training batch")
        records.append(CropMedianTrainingRecord(
            crop_type=batch["crop_type"],
            loss_fraction_pct=float(matches[0]["loss_fraction_pct"]),
        ))
    baseline = fit_crop_median_baseline(records)
    return BaselineArtifact(
        format_version="baseline-artifact.v1",
        algorithm_family=FAMILY,
        engine_version=ENGINE_VERSION,
        source_dataset_id=DATASET_ID,
        training_partition={"predicate": "dispatch_datetime < 2025-05-01", "batch_count": 900},
        source_table_hashes=dict(SOURCE_HASHES),
        training_membership_sha256=membership_sha256(training),
        crop_medians=baseline.crop_medians,
        global_median=baseline.global_median,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    repo = Path(__file__).resolve().parents[1]
    protected = (args.data_dir.resolve(), repo / "sponsor_pack", repo / "docs" / "data_recon")
    if any(output.is_relative_to(directory) for directory in protected):
        parser.error("Output must not overwrite source data or research evidence")
    artifact = generate_artifact(args.data_dir)
    content = json.dumps(artifact.model_dump(), sort_keys=True, indent=2, allow_nan=False) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(content.encode("utf-8"))
    print(f"Generated {output}; training=900; held-out=900")


if __name__ == "__main__":
    main()
