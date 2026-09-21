"""Deterministic crop-median baseline analytics engine (IGR-04A).

Implements the accepted ADR 0003 D2, D5 crop-conditioned median baseline:
- Fitting computes per-crop median loss_fraction_pct and global training median.
- Inference consumes only batch_input.batch.crop_type from BatchAssessmentInput.
- Unseen crops fall back to the global training median.
- Risk score is computed by clipping predicted loss to [0, 100] and dividing by 100.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Sequence

from app.domain.batch import BatchAssessmentInput


@dataclass(frozen=True)
class CropMedianTrainingRecord:
    """A single training observation for fitting the crop median baseline."""

    crop_type: str
    loss_fraction_pct: float

    def __post_init__(self) -> None:
        if not isinstance(self.crop_type, str) or not self.crop_type.strip():
            raise ValueError(
                f"crop_type must be a non-empty string, got: {self.crop_type!r}"
            )
        if not isinstance(self.loss_fraction_pct, (int, float)) or not math.isfinite(
            self.loss_fraction_pct
        ):
            raise ValueError(
                f"loss_fraction_pct must be a finite number, got: {self.loss_fraction_pct!r}"
            )


@dataclass(frozen=True)
class CropMedianBaseline:
    """Fitted baseline holding deterministic per-crop medians and global median."""

    crop_medians: dict[str, float]
    global_median: float


def fit_crop_median_baseline(
    training_records: Sequence[CropMedianTrainingRecord],
) -> CropMedianBaseline:
    """Fit crop-median baseline on an explicit caller-supplied training collection.

    Validation rules:
    - Empty collection raises ValueError (no fabricated defaults).
    - NaN / +/-inf raises ValueError (no silent inclusion).
    - Empty/invalid crop identifier raises ValueError (no hidden fallback bucket).
    - Fits medians deterministically using Python standard library statistics.median.
    """
    if not isinstance(training_records, Sequence) or isinstance(
        training_records, (str, bytes)
    ):
        raise TypeError(
            f"training_records must be a Sequence of CropMedianTrainingRecord, got: {type(training_records).__name__}"
        )

    if len(training_records) == 0:
        raise ValueError("training_records collection must not be empty.")

    by_crop: dict[str, list[float]] = {}
    all_losses: list[float] = []

    for idx, r in enumerate(training_records):
        if not isinstance(r, CropMedianTrainingRecord):
            raise TypeError(
                f"Record at index {idx} must be a CropMedianTrainingRecord, got: {type(r).__name__}"
            )
        # Verify invariants in case attributes were bypassed
        if not isinstance(r.crop_type, str) or not r.crop_type.strip():
            raise ValueError(
                f"Record at index {idx} has invalid crop_type: {r.crop_type!r}"
            )
        if not isinstance(r.loss_fraction_pct, (int, float)) or not math.isfinite(
            r.loss_fraction_pct
        ):
            raise ValueError(
                f"Record at index {idx} has non-finite loss_fraction_pct: {r.loss_fraction_pct!r}"
            )

        crop_key = r.crop_type.strip()
        loss_val = float(r.loss_fraction_pct)
        by_crop.setdefault(crop_key, []).append(loss_val)
        all_losses.append(loss_val)

    # Sort keys for strictly deterministic dictionary ordering
    crop_medians: dict[str, float] = {
        crop: float(statistics.median(by_crop[crop]))
        for crop in sorted(by_crop.keys())
    }
    global_median = float(statistics.median(all_losses))

    return CropMedianBaseline(
        crop_medians=crop_medians,
        global_median=global_median,
    )


def predict_loss_fraction_pct(
    baseline: CropMedianBaseline,
    batch_input: BatchAssessmentInput,
) -> float:
    """Predict loss fraction percentage using ONLY batch_input.batch.crop_type.

    If crop_type was observed during training, returns the crop-specific median.
    If crop_type was not observed during training, returns the global training median.
    """
    if not isinstance(baseline, CropMedianBaseline):
        raise TypeError(
            f"baseline must be an instance of CropMedianBaseline, got: {type(baseline).__name__}"
        )
    if not isinstance(batch_input, BatchAssessmentInput):
        raise TypeError(
            f"batch_input must be an instance of BatchAssessmentInput, got: {type(batch_input).__name__}"
        )

    crop = batch_input.batch.crop_type.strip()
    if crop in baseline.crop_medians:
        return baseline.crop_medians[crop]
    return baseline.global_median


def predict_risk_score(
    baseline: CropMedianBaseline,
    batch_input: BatchAssessmentInput,
) -> float:
    """Compute risk score from predicted loss fraction percentage.

    Per ADR 0003 D2:
    risk_score = clip(predicted_loss_fraction_pct, 0, 100) / 100
    """
    predicted_loss = predict_loss_fraction_pct(baseline, batch_input)
    clipped = max(0.0, min(100.0, predicted_loss))
    return clipped / 100.0
