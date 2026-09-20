"""Validation evidence script for IGR-03 across all 1,800 real sponsor batches.

Validates:
- All 1800 batches in sponsor_pack/data map deterministically to BatchAssessmentInput.
- Strict 5-step lifecycle chronology check:
    T_harvest < T_harvest_qc < T_entry < T_pre_dispatch_qc < T_dispatch.
- Assessment anchor clock invariant:
    assessment_context.assessment_timestamp == storage_sessions.dispatch_datetime.
- Fast, low-memory sequential execution (objects validated and discarded).
- Exception classification (CHRONOLOGY_VIOLATION, CARDINALITY, MALFORMED, OTHER).
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
import sys

# Ensure backend app package is importable
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "backend"))

from app.ingestion.canonical_mapper import (
    BatchNotFoundError,
    CanonicalMappingError,
    CanonicalValidationError,
    CardinalityError,
    build_batch_assessment_input,
)
from app.ingestion.raw_reader import read_raw_snapshot


def main() -> None:
    data_dir = repo_root / "sponsor_pack" / "data"
    print(f"Loading raw snapshot from: {data_dir}")
    snapshot = read_raw_snapshot(data_dir)

    batch_ids = snapshot["batches"].get_column_values("batch_id")
    total_batches = len(batch_ids)
    print(f"Total batches in snapshot: {total_batches}")

    session_dispatches = {
        r["batch_id"]: datetime.fromisoformat(r["dispatch_datetime"])
        for r in snapshot["storage_sessions"].rows
    }

    successful_count = 0
    failed_count = 0
    failure_categories: Counter[str] = Counter()
    failures_by_category: dict[str, list[str]] = {}

    for idx, batch_id in enumerate(batch_ids, start=1):
        try:
            canonical_input = build_batch_assessment_input(snapshot, batch_id)

            # Invariant check: assessment_timestamp == dispatch_datetime
            expected_dispatch = session_dispatches.get(batch_id)
            actual_timestamp = canonical_input.assessment_context.assessment_timestamp
            if actual_timestamp != expected_dispatch:
                raise ValueError(
                    f"Anchor clock mismatch for batch '{batch_id}': "
                    f"actual {actual_timestamp} != expected {expected_dispatch}"
                )

            successful_count += 1

            # Explicitly discard object to prevent memory accumulation
            del canonical_input

        except CanonicalValidationError as e:
            failed_count += 1
            msg = str(e)
            if "Chronological sequence violation" in msg:
                cat = "CHRONOLOGY_VIOLATION"
            else:
                cat = "MALFORMED"
            failure_categories[cat] += 1
            failures_by_category.setdefault(cat, []).append(f"{batch_id}: {msg}")

        except CardinalityError as e:
            failed_count += 1
            cat = "CARDINALITY"
            failure_categories[cat] += 1
            failures_by_category.setdefault(cat, []).append(f"{batch_id}: {e}")

        except BatchNotFoundError as e:
            failed_count += 1
            cat = "BATCH_NOT_FOUND"
            failure_categories[cat] += 1
            failures_by_category.setdefault(cat, []).append(f"{batch_id}: {e}")

        except Exception as e:
            failed_count += 1
            cat = "OTHER"
            failure_categories[cat] += 1
            failures_by_category.setdefault(cat, []).append(
                f"{batch_id}: {type(e).__name__}: {e}"
            )

    print("\n--- Validation Summary ---")
    print(f"Total: {total_batches}")
    print(f"Mapped successfully: {successful_count}")
    print(f"Failed: {failed_count}")
    if failure_categories:
        print("Failure breakdown by category:")
        for cat, count in sorted(failure_categories.items()):
            print(f"  - {cat}: {count}")
    else:
        print("Failure breakdown by category: None")


if __name__ == "__main__":
    main()
