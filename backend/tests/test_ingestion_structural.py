"""Tests for raw dataset loading and structural diagnostics (IGR-02).

Validates:
1. Supplied snapshot loads with exact row counts across all 8 tables.
2. Candidate primary key uniqueness on the supplied snapshot.
3. Direct foreign key referential integrity on the supplied snapshot.
4. Negative case: missing file detection without silent failure.
5. Negative case: bad/duplicate/mismatched headers detection.
6. Negative case: duplicate candidate primary key detection.
7. Negative case: broken foreign key (orphan) detection.
8. Raw value preservation: strings, empty values, and formatting are untouched.
"""

from pathlib import Path
import pytest

from app.ingestion.diagnostics import DiagnosticIssue, StructuralDiagnostics
from app.ingestion.raw_reader import (
    RawSnapshot,
    RawTable,
    read_raw_snapshot,
    read_raw_table,
)
from app.ingestion.structural_manifest import TABLE_MANIFEST, TableSpec


DATA_DIR = Path("sponsor_pack/data")


def test_supplied_snapshot_loads() -> None:
    """Test 1: Supplied snapshot loads and asserts exact row counts for all 8 tables."""
    snapshot = read_raw_snapshot(DATA_DIR)

    assert len(snapshot.tables) == 8
    assert snapshot.diagnostics.is_valid(), f"Unexpected issues: {snapshot.diagnostics.issues}"

    # Verify exact VDR-01 accepted counts
    expected_counts = {
        "facilities": 10,
        "storage_zones": 25,
        "batches": 1800,
        "storage_sessions": 1800,
        "sensor_readings": 669665,
        "quality_checks": 5400,
        "shipments": 1800,
        "historical_quality_outcomes": 1800,
    }

    for table_name, expected_count in expected_counts.items():
        assert table_name in snapshot.tables
        actual_count = snapshot[table_name].row_count
        assert actual_count == expected_count, (
            f"Row count mismatch for {table_name}: actual {actual_count} != expected {expected_count}"
        )


def test_candidate_pk_uniqueness_on_supplied_snapshot() -> None:
    """Test 2: Candidate PK uniqueness on supplied snapshot (0 duplicates)."""
    snapshot = read_raw_snapshot(DATA_DIR)

    for table_name, spec in TABLE_MANIFEST.items():
        diag = snapshot.diagnostics.table_stats[table_name]
        assert diag.duplicate_pk_count == 0, (
            f"Table {table_name} has duplicate PKs: {diag.duplicate_pks}"
        )
        assert len(diag.duplicate_pks) == 0

        # Independent confirmation: unique values set length equals row count
        pk_values = snapshot[table_name].get_column_values(spec.pk_column)
        assert len(set(pk_values)) == spec.expected_row_count


def test_direct_fk_integrity_on_supplied_snapshot() -> None:
    """Test 3: Direct FK integrity on supplied snapshot (0 orphans for allowed relations)."""
    snapshot = read_raw_snapshot(DATA_DIR)

    for table_name, diag in snapshot.diagnostics.table_stats.items():
        for rel_key, orphans in diag.orphan_fks.items():
            assert len(orphans) == 0, (
                f"FK relationship {table_name}.{rel_key} has {len(orphans)} orphans: {orphans[:5]}"
            )

    orphan_issues = snapshot.diagnostics.get_issues_by_code("ORPHAN_FK")
    assert len(orphan_issues) == 0


def test_missing_file_negative_case(tmp_path: Path) -> None:
    """Test 4: Missing file negative case (omit 1 CSV, assert explicit diagnostic/failure)."""
    # Create a minimal directory with only 1 table present instead of 8
    facilities_csv = tmp_path / "facilities.csv"
    facilities_csv.write_text(
        "facility_id,facility_name,region,district,facility_type,capacity_tonnes,commissioned_year,has_controlled_atmosphere\n"
        "FAC-001,Test Cold,North,Bălți,Commercial Cold Store,4500,2018,True\n",
        encoding="utf-8",
    )

    snapshot = read_raw_snapshot(tmp_path, check_vdr01_counts=False)

    assert snapshot.diagnostics.has_errors()
    assert "storage_zones" in snapshot.diagnostics.missing_tables
    assert "batches" in snapshot.diagnostics.missing_tables

    missing_issues = snapshot.diagnostics.get_issues_by_code("MISSING_FILE")
    assert len(missing_issues) == 7  # 7 out of 8 files missing
    missing_tables = {i.table_name for i in missing_issues}
    assert "storage_zones" in missing_tables


def test_bad_header_negative_case(tmp_path: Path) -> None:
    """Test 5: Bad header negative case (missing/wrong/duplicate header, assert explicit detection)."""
    # Case A: Missing header
    bad_headers_csv = tmp_path / "facilities.csv"
    bad_headers_csv.write_text(
        "facility_id,facility_name,region\n"  # Missing other 5 columns
        "FAC-001,Test Cold,North\n",
        encoding="utf-8",
    )

    _, issues = read_raw_table(bad_headers_csv, "facilities", spec=TABLE_MANIFEST["facilities"])
    mismatch_issues = [i for i in issues if i.code == "HEADER_MISMATCH"]
    assert len(mismatch_issues) == 1
    assert "district" in mismatch_issues[0].details["missing_headers"]

    # Case B: Duplicate header
    dup_header_csv = tmp_path / "dup_headers.csv"
    dup_header_csv.write_text(
        "col_a,col_b,col_a\n"
        "1,2,3\n",
        encoding="utf-8",
    )
    _, dup_issues = read_raw_table(dup_header_csv, "test_table")
    dup_header_issues = [i for i in dup_issues if i.code == "DUPLICATE_HEADER"]
    assert len(dup_header_issues) == 1
    assert "col_a" in dup_header_issues[0].details["duplicate_headers"]


def test_duplicate_pk_negative_case(tmp_path: Path) -> None:
    """Test 6: Duplicate PK negative case (CSV with duplicate PK, assert detection)."""
    batches_csv = tmp_path / "batches.csv"
    batches_csv.write_text(
        "batch_id,crop_type,variety,origin_region,harvest_datetime,harvest_weight_kg,initial_quality_score,harvest_temperature_c,harvest_conditions,field_precooled\n"
        "BAT-000001,plums,Stanley,South,2024-08-06 12:15:00,9026.1,89.4,20.7,Optimal Dry,True\n"
        "BAT-000001,apples,Gala,North,2024-08-07 10:00:00,5000.0,92.0,18.0,Optimal Dry,False\n",
        encoding="utf-8",
    )

    custom_manifest = {"batches": TABLE_MANIFEST["batches"]}
    snapshot = read_raw_snapshot(tmp_path, manifest=custom_manifest, check_vdr01_counts=False)

    assert snapshot.diagnostics.has_errors()
    pk_issues = snapshot.diagnostics.get_issues_by_code("DUPLICATE_PK")
    assert len(pk_issues) == 1
    assert pk_issues[0].table_name == "batches"
    assert "BAT-000001" in pk_issues[0].details["duplicate_keys"]
    assert snapshot.diagnostics.table_stats["batches"].duplicate_pk_count == 1


def test_broken_fk_negative_case(tmp_path: Path) -> None:
    """Test 7: Broken FK negative case (child record referencing missing parent FK, assert orphan detection)."""
    facilities_csv = tmp_path / "facilities.csv"
    facilities_csv.write_text(
        "facility_id,facility_name,region,district,facility_type,capacity_tonnes,commissioned_year,has_controlled_atmosphere\n"
        "FAC-001,NordFrigo Hub,North,Bălți,Commercial Cold Store,4500,2018,True\n",
        encoding="utf-8",
    )

    storage_zones_csv = tmp_path / "storage_zones.csv"
    storage_zones_csv.write_text(
        "zone_id,facility_id,zone_name,zone_type,nominal_capacity_tonnes,target_temperature_c,target_relative_humidity_pct,cooling_system_type,insulation_quality,defrost_cycle_frequency_per_day\n"
        "ZONE-001,FAC-001,Chamber 1 (CA),Controlled Atmosphere (CA),120,0.5,94.0,Propane Chiller,Premium,1\n"
        "ZONE-002,FAC-999,Chamber 2 (Std),Standard Cold Room,100,2.0,90.0,R134a DX,High,2\n",  # FAC-999 is an orphan!
        encoding="utf-8",
    )

    custom_manifest = {
        "facilities": TABLE_MANIFEST["facilities"],
        "storage_zones": TABLE_MANIFEST["storage_zones"],
    }
    snapshot = read_raw_snapshot(tmp_path, manifest=custom_manifest, check_vdr01_counts=False)

    assert snapshot.diagnostics.has_errors()
    orphan_issues = snapshot.diagnostics.get_issues_by_code("ORPHAN_FK")
    assert len(orphan_issues) == 1
    assert orphan_issues[0].table_name == "storage_zones"
    assert "FAC-999" in orphan_issues[0].details["sample_orphans"]


def test_raw_preservation(tmp_path: Path) -> None:
    """Test 8: Raw preservation (empty fields, unusual text, formatting read as-is, not repaired/dropped)."""
    test_csv = tmp_path / "raw_test.csv"
    test_content = (
        "id,text_with_spaces,empty_val,unicode_text,numeric_string,bool_string\n"
        '1,  untrimmed text  ,,"Bălți / Chișinău №1 & 100% (-0.4°C)",+00123.400,True\n'
        '2,normal,,another line,0045,False\n'
    )
    test_csv.write_text(test_content, encoding="utf-8")

    table, issues = read_raw_table(test_csv, "raw_test")
    assert table is not None
    assert len(issues) == 0
    assert table.row_count == 2

    row0 = table.rows[0]
    # Assert string values are preserved exactly:
    assert row0["text_with_spaces"] == "  untrimmed text  "  # NOT stripped
    assert row0["empty_val"] == ""                          # NOT converted to None or NaN
    assert row0["unicode_text"] == "Bălți / Chișinău №1 & 100% (-0.4°C)"  # Unicode intact
    assert row0["numeric_string"] == "+00123.400"           # NOT coerced to 123.4
    assert row0["bool_string"] == "True"                    # NOT coerced to boolean True

    row1 = table.rows[1]
    assert row1["empty_val"] == ""
    assert row1["numeric_string"] == "0045"
    assert row1["bool_string"] == "False"
