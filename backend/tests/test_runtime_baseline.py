"""RBS-01 contract tests using small synthetic resources; real smoke is separate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.analytics import crop_median_baseline
from app.analytics.crop_median_baseline import CropMedianBaseline
from app.ingestion.diagnostics import DiagnosticIssue
from app.ingestion.raw_reader import RawSnapshot, RawTable
from app.main import create_app
from app.runtime import artifact, context
from app.runtime.artifact import SOURCE_HASHES, membership_sha256
from app.services.demo_assessment import build_demo_assessment
from test_ingestion_canonical import _make_synthetic_snapshot

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("artifact_generator", ROOT / "scripts/generate_baseline_artifact.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


@pytest.fixture(autouse=True)
def clear_runtime_environment(monkeypatch):
    monkeypatch.delenv("SMART_HARVEST_DATA_DIR", raising=False)
    monkeypatch.delenv("SMART_HARVEST_BASELINE_ARTIFACT", raising=False)


@pytest.fixture
def cohort():
    rows = {"batches": [], "storage_sessions": [], "historical_quality_outcomes": []}
    for i in range(1800):
        batch_id = f"B-{i:04d}"
        rows["batches"].append({"batch_id": batch_id, "crop_type": "apples" if i % 2 else "pears"})
        rows["storage_sessions"].append({
            "batch_id": batch_id,
            "dispatch_datetime": "2025-04-30 23:59:59" if i < 900 else "2025-05-01 00:00:00",
        })
        rows["historical_quality_outcomes"].append({
            "batch_id": batch_id, "loss_fraction_pct": str(i if i < 900 else 99999),
        })
    return RawSnapshot(Path("synthetic"), {
        name: RawTable(name, Path(name + ".csv"), list(values[0]), values)
        for name, values in rows.items()
    })


@pytest.fixture
def artifact_payload(cohort):
    training, _ = artifact.partition_membership(cohort)
    return {
        "format_version": "baseline-artifact.v1",
        "algorithm_family": artifact.FAMILY,
        "engine_version": artifact.ENGINE_VERSION,
        "source_dataset_id": artifact.DATASET_ID,
        "training_partition": {"predicate": "dispatch_datetime < 2025-05-01", "batch_count": 900},
        "source_table_hashes": dict(SOURCE_HASHES),
        "training_membership_sha256": membership_sha256(training),
        "crop_medians": {"apples": 450.0, "pears": 449.0},
        "global_median": 449.5,
    }


def configure(monkeypatch, tmp_path, payload):
    path = tmp_path / "artifact.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setenv("SMART_HARVEST_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("SMART_HARVEST_BASELINE_ARTIFACT", str(path))
    return path


def assert_degraded(application, expected="unavailable"):
    with TestClient(application) as client:
        assert client.get("/api/v1/health").json() == {
            "status": "ok", "service": "smart-harvest", "analytics": expected,
        }
        assert application.state.analytics_runtime.context is None
        demo = client.get("/api/v1/demo/assessment")
        assert demo.status_code == 200
        actual = demo.json()
        expected_demo = build_demo_assessment().model_dump(mode="json")
        del actual["provenance"]["generated_at"], expected_demo["provenance"]["generated_at"]
        assert actual == expected_demo
        real = client.get("/api/v1/assessments/anything")
        assert real.status_code == 503
        assert real.headers["cache-control"] == "no-store"


def test_unconfigured_startup():
    assert_degraded(create_app(), "not_configured")


@pytest.mark.parametrize("data,model", [("missing", None), (None, "missing"), ("", ""), (" ", " ")])
def test_incomplete_configuration(monkeypatch, data, model):
    if data is not None:
        monkeypatch.setenv("SMART_HARVEST_DATA_DIR", data)
    if model is not None:
        monkeypatch.setenv("SMART_HARVEST_BASELINE_ARTIFACT", model)
    assert_degraded(create_app())


@pytest.mark.parametrize("missing", ["dataset", "artifact"])
def test_missing_resources(monkeypatch, tmp_path, artifact_payload, missing):
    path = configure(monkeypatch, tmp_path, artifact_payload)
    if missing == "artifact":
        path.unlink()
    assert_degraded(create_app())


def test_malformed_json(monkeypatch, tmp_path, artifact_payload):
    path = configure(monkeypatch, tmp_path, artifact_payload)
    path.write_text("{broken", encoding="utf-8")
    assert_degraded(create_app())


@pytest.mark.parametrize("key,value", [
    ("format_version", "unknown"), ("algorithm_family", "other"),
    ("engine_version", "other"), ("source_dataset_id", "other"),
    ("source_table_hashes", {}), ("training_membership_sha256", "bad"),
    ("training_membership_sha256", "0" * 64),
    ("training_partition", {"predicate": "all", "batch_count": 1800}),
    ("crop_medians", {}), ("crop_medians", {"": 1.0}),
    ("crop_medians", {" apples ": 1.0}), ("crop_medians", {"apples": float("inf")}),
    ("crop_medians", {"apples": True}), ("crop_medians", {"apples": "1.0"}),
    ("crop_medians", {"apples": 1.0}),
    ("global_median", float("nan")), ("global_median", float("-inf")),
    ("global_median", True), ("global_median", "11.0"),
])
def test_invalid_artifact_fails_closed(monkeypatch, tmp_path, artifact_payload, cohort, key, value):
    artifact_payload[key] = value
    configure(monkeypatch, tmp_path, artifact_payload)
    monkeypatch.setattr(context, "load_pinned_snapshot", lambda _: cohort)
    assert_degraded(create_app())


def test_valid_loader_never_fits(monkeypatch, tmp_path, artifact_payload, cohort):
    configure(monkeypatch, tmp_path, artifact_payload)
    reader = Mock(return_value=cohort)
    monkeypatch.setattr(context, "load_pinned_snapshot", reader)
    fit = Mock(side_effect=AssertionError("Runtime must not fit"))
    monkeypatch.setattr(crop_median_baseline, "fit_crop_median_baseline", fit)
    app = create_app()
    reader.assert_not_called()  # Creating/importing the app does not load resources.
    with TestClient(app) as client:
        assert client.get("/api/v1/health").json()["analytics"] == "ready"
        runtime = app.state.analytics_runtime.context
        assert runtime.baseline.global_median == 449.5
        assert len(runtime.training_ids) == len(runtime.held_out_ids) == 900
        assert client.get("/api/v1/assessments/unknown").status_code == 404
        assert client.get("/api/v1/assessments/B-0000").status_code == 409
        assert app.state.analytics_runtime.context is runtime
    reader.assert_called_once()
    fit.assert_not_called()
    assert app.state.analytics_runtime.context is None


def test_source_hashing_and_rejection(monkeypatch, tmp_path):
    for name in SOURCE_HASHES:
        (tmp_path / artifact.TABLE_MANIFEST[name].filename).write_bytes(name.encode())
    hashes = artifact.source_hashes(tmp_path)
    assert hashes == {name: hashlib.sha256(name.encode()).hexdigest() for name in SOURCE_HASHES}
    reader = Mock(side_effect=AssertionError("Must reject before reading"))
    monkeypatch.setattr(artifact, "read_raw_snapshot", reader)
    with pytest.raises(ValueError, match="hash mismatch"):
        artifact.load_pinned_snapshot(tmp_path)
    reader.assert_not_called()


@pytest.mark.parametrize("failure", ["hash", "diagnostics", "changed_during_load"])
def test_snapshot_failure_degrades_startup(monkeypatch, tmp_path, artifact_payload, cohort, failure):
    configure(monkeypatch, tmp_path, artifact_payload)
    if failure == "diagnostics":
        cohort.diagnostics.issues.append(DiagnosticIssue("BAD", "bad", "batches", "synthetic"))
    hashes = Mock(side_effect=[{}] if failure == "hash" else [SOURCE_HASHES, {} if failure == "changed_during_load" else SOURCE_HASHES])
    monkeypatch.setattr(artifact, "source_hashes", hashes)
    monkeypatch.setattr(artifact, "read_raw_snapshot", lambda _: cohort)
    assert_degraded(create_app())


def test_partition_boundary_and_fingerprint(cohort):
    training, held_out = artifact.partition_membership(cohort)
    assert "B-0899" in training
    assert "B-0900" in held_out
    assert not training & held_out
    assert membership_sha256(training) == hashlib.sha256(
        "\n".join(f"B-{i:04d}" for i in range(900)).encode()
    ).hexdigest()


@pytest.mark.parametrize("failure", ["count", "duplicate_batch", "duplicate_session", "missing_session", "date"])
def test_invalid_membership(cohort, failure):
    if failure == "count":
        cohort["storage_sessions"].rows[0]["dispatch_datetime"] = "2025-05-01"
    elif failure == "duplicate_batch":
        cohort["batches"].rows.append(cohort["batches"].rows[0])
    elif failure == "duplicate_session":
        cohort["storage_sessions"].rows.append(cohort["storage_sessions"].rows[0])
    elif failure == "missing_session":
        cohort["storage_sessions"].rows.pop()
    else:
        cohort["storage_sessions"].rows[0]["dispatch_datetime"] = "bad"
    with pytest.raises(ValueError):
        artifact.partition_membership(cohort)


def test_generator_fits_training_only(monkeypatch, cohort):
    monkeypatch.setattr(generator, "load_pinned_snapshot", lambda _: cohort)
    fitter = Mock(wraps=crop_median_baseline.fit_crop_median_baseline)
    monkeypatch.setattr(generator, "fit_crop_median_baseline", fitter)
    result = generator.generate_artifact(Path("synthetic"))
    assert result.crop_medians == {"apples": 450.0, "pears": 449.0}
    assert result.global_median == 449.5
    assert len(fitter.call_args.args[0]) == 900
    # Held-out outcomes are never interpreted or fitted.
    for row in cohort["historical_quality_outcomes"].rows[900:]:
        row["loss_fraction_pct"] = "not a number"
    assert generator.generate_artifact(Path("synthetic")) == result


@pytest.mark.parametrize("failure", ["missing", "duplicate", "nan", "infinity"])
def test_generator_rejects_bad_training_outcome(monkeypatch, cohort, failure):
    monkeypatch.setattr(generator, "load_pinned_snapshot", lambda _: cohort)
    rows = cohort["historical_quality_outcomes"].rows
    if failure == "missing":
        rows.pop(0)
    elif failure == "duplicate":
        rows.append(rows[0])
    else:
        rows[0]["loss_fraction_pct"] = "nan" if failure == "nan" else "inf"
    with pytest.raises(ValueError):
        generator.generate_artifact(Path("synthetic"))


def test_generator_refuses_unpinned_source(tmp_path):
    with pytest.raises((OSError, ValueError)):
        generator.generate_artifact(tmp_path)


@pytest.mark.parametrize("protected", ["sponsor_pack/data/new.json", "docs/data_recon/new.json"])
def test_generator_protects_source_and_evidence(monkeypatch, protected):
    monkeypatch.setattr("sys.argv", ["generator", "--data-dir", str(ROOT / "sponsor_pack/data"), "--output", str(ROOT / protected)])
    with pytest.raises(SystemExit) as error:
        generator.main()
    assert error.value.code == 2


@pytest.fixture
def ready_context():
    snapshot = _make_synthetic_snapshot()
    # Shift the existing valid mapper fixture into the held-out season.
    for table in snapshot.tables.values():
        for row in table.rows:
            for key, value in row.items():
                if isinstance(value, str) and value.startswith("2024-"):
                    row[key] = "2025-" + value[5:]
    return context.AnalyticsRuntimeContext(
        snapshot, CropMedianBaseline({"apples": 6.44}, 11.085),
        frozenset({"TRAINING"}), frozenset({"BAT-SYN-001"}),
    )


def test_real_route_mapping_provenance_determinism_and_errors(monkeypatch, ready_context):
    import app.main as main

    monkeypatch.setattr(main, "initialize_runtime", lambda: context.AnalyticsRuntimeState("ready", ready_context))
    monkeypatch.setattr(crop_median_baseline, "fit_crop_median_baseline", Mock(side_effect=AssertionError("No request fit")))
    with TestClient(create_app()) as client:
        before = datetime.now(timezone.utc)
        first = client.get("/api/v1/assessments/BAT-SYN-001")
        second = client.get("/api/v1/assessments/BAT-SYN-001")
        assert first.status_code == second.status_code == 200
        assert first.headers["cache-control"] == "no-store"
        payload = first.json()
        assert payload["batch_id"] == "BAT-SYN-001"
        assert payload["status"] == "assessed"
        assert payload["risk"] == {"score": 0.0644, "band": None}
        assert payload["deterioration_horizon"] is None
        assert payload["factors"] == []
        assert payload["recommendation"] is None
        assert payload["reliability"] == {"level": "unavailable", "confidence_score": None, "reason_codes": [], "missing_requirements": []}
        provenance = payload["provenance"]
        timestamp = datetime.fromisoformat(provenance["generated_at"].replace("Z", "+00:00"))
        assert before <= timestamp <= datetime.now(timezone.utc)
        assert provenance == {
            "contract_version": "1.0.0", "engine_tier": "deterministic_baseline",
            "engine_version": artifact.ENGINE_VERSION, "source_dataset_id": artifact.DATASET_ID,
            "simulation": True, "notice": artifact.NOTICE, "generated_at": provenance["generated_at"],
        }
        other = second.json()
        del payload["provenance"]["generated_at"], other["provenance"]["generated_at"]
        assert payload == other
        for batch, status in [("unknown", 404), ("TRAINING", 409)]:
            response = client.get(f"/api/v1/assessments/{batch}")
            assert response.status_code == status
            assert response.headers["cache-control"] == "no-store"
        rejected = client.post("/api/v1/assessments/BAT-SYN-001")
        assert rejected.status_code == 405
        assert rejected.headers["cache-control"] == "no-store"
        # A real mapper failure must be an HTTP failure, not insufficient_data.
        ready_context.snapshot["batches"].rows[0]["harvest_weight_kg"] = "malformed"
        response = client.get("/api/v1/assessments/BAT-SYN-001")
        assert response.status_code == 500
        assert response.json() == {"detail": "Assessment could not be completed"}
        assert response.headers["cache-control"] == "no-store"


def test_unexpected_internal_failure(monkeypatch, ready_context):
    import app.api.routes as routes

    app = create_app()
    app.dependency_overrides[context.get_runtime] = lambda: ready_context
    monkeypatch.setattr(routes, "build_baseline_assessment", Mock(side_effect=RuntimeError("private detail")))
    with TestClient(app) as client:
        response = client.get("/api/v1/assessments/BAT-SYN-001")
        assert response.status_code == 500
        assert "private detail" not in response.text
        assert response.headers["cache-control"] == "no-store"
