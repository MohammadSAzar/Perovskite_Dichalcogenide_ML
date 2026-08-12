import json

from pathlib import Path

from psk_tmd.corpus.storage import (
    validate_pilot_directory,
    validate_pilot_relationships,
)


# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

PILOT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "corpus"
    / "pilot"
)


# ---------------------------------------------------------------------------
# LOAD JSON
# ---------------------------------------------------------------------------
def load_json(filename: str) -> list[dict]:
    path = PILOT_DIR / filename

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    counts = validate_pilot_directory(PILOT_DIR)
    validate_pilot_relationships(PILOT_DIR)

    print("=== TABLE COUNTS ===")

    for filename, count in counts.items():
        print(f"{filename}: {count}")

    print()

    sample_series = load_json("sample_series.json")
    samples = load_json("samples.json")
    synthesis = load_json("synthesis_records.json")
    assessments = load_json("mechanism_assessments.json")
    evidence = load_json("mechanism_evidence.json")
    tests = load_json("photocatalytic_tests.json")
    extractions = load_json("extraction_records.json")
    disagreements = load_json("disagreement_records.json")

    print("=== SAMPLE SERIES ===")

    for record in sample_series:
        print(
            record["sample_series_id"],
            record["paper_id"],
            record["pair_id"],
        )

    print()

    print("=== SAMPLE SERIES MEMBERSHIP ===")

    for sample in samples:
        print(
            sample["sample_id"],
            sample["sample_series_id"],
            sample["pair_id"],
        )

    print()

    print("=== SYNTHESIS RECORDS ===")

    for record in synthesis:
        print(
            record["synthesis_id"],
            record["sample_id"],
            record["topology"],
            record["method_reported"],
        )

    print()

    print("=== MECHANISM ASSESSMENTS ===")

    for record in assessments:
        print(
            record["mechanism_assessment_id"],
            record["sample_id"],
            record["applies_to_series_id"],
            record["mechanism_normalized"],
            record["charge_transfer_class"],
        )

    print()

    print("=== EVIDENCE STRENGTH CHECK ===")

    missing_strength = [
        record["evidence_id"]
        for record in evidence
        if "evidence_strength" not in record
    ]

    print("Missing evidence_strength:", missing_strength)

    print()

    print("=== PHOTOCATALYTIC CHECKS ===")

    for test_id in [
        "TST-0001",
        "TST-0004",
        "TST-0007",
        "TST-0008",
        "TST-0009",
    ]:
        record = next(
            item
            for item in tests
            if item["test_id"] == test_id
        )

        print(
            test_id,
            {
                "initial_concentration": (
                    record[
                        "initial_target_concentration_value"
                    ],
                    record[
                        "initial_target_concentration_unit"
                    ],
                ),
                "wavelength_min_nm": (
                    record["wavelength_min_nm"]
                ),
                "light_intensity": (
                    record["light_intensity_value"],
                    record["light_intensity_unit"],
                ),
                "dark_equilibration_min": (
                    record[
                        "dark_equilibration_time_min"
                    ]
                ),
                "metric": (
                    record["performance_metric_name"],
                    record["performance_metric_value"],
                    record["performance_metric_unit"],
                ),
                "cycles": record["cycles"],
            },
        )

    print()

    print("=== EXTRACTION CHECKS ===")

    for extraction_id in [
        "EXT-0007",
        "EXT-0010",
        "EXT-0011",
        "EXT-0017",
        "EXT-0028",
    ]:
        record = next(
            item
            for item in extractions
            if item["extraction_id"] == extraction_id
        )

        print(
            extraction_id,
            record["provenance_operation"],
            record["target_table"],
            record["target_record_id"],
            record["target_field"],
        )

    print()

    print("=== DISAGREEMENTS ===")

    for record in disagreements:
        print(
            record["disagreement_id"],
            record["disagreement_type"],
            record["status"],
            record["target_table"],
            record["target_record_ids"],
            record["selected_value"],
        )

    print()

    print("=== OBSOLETE FILE CHECK ===")

    obsolete_path = PILOT_DIR / "synthesis_steps.json"

    print(
        "synthesis_steps.json exists:",
        obsolete_path.exists(),
    )

    print()
    print("Pilot v0.2 inspection completed.")


if __name__ == "__main__":
    main()


