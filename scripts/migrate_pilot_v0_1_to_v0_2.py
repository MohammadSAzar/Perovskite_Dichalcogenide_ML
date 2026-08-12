import json
import shutil

from pathlib import Path

from psk_tmd.common.models import (
    DisagreementRecord,
    ExperimentalSample,
    ExtractionRecord,
    MechanismAssessment,
    MechanismEvidence,
    PaperRecord,
    PhotocatalyticTest,
    SampleSeries,
    SynthesisRecord,
)
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

BACKUP_DIR = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "pilot_v0_1_backup"
)


# ---------------------------------------------------------------------------
# JSON UTILITIES
# ---------------------------------------------------------------------------
def load_json(filename: str) -> list[dict]:
    path = PILOT_DIR / filename

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected JSON list in {path}."
        )

    return data


def save_json(
    filename: str,
    data: list[dict],
) -> None:
    path = PILOT_DIR / filename

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


# ---------------------------------------------------------------------------
# BACKUP V0.1 PILOT
# ---------------------------------------------------------------------------
def backup_v0_1_pilot() -> None:
    source_files = [
        "papers.json",
        "samples.json",
        "synthesis_steps.json",
        "mechanism_assessments.json",
        "mechanism_evidence.json",
        "photocatalytic_tests.json",
        "extraction_records.json",
    ]

    if BACKUP_DIR.exists():
        raise FileExistsError(
            f"Backup directory already exists: {BACKUP_DIR}"
        )

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=False,
    )

    for filename in source_files:
        source = PILOT_DIR / filename
        destination = BACKUP_DIR / filename

        shutil.copy2(
            source,
            destination,
        )


# ---------------------------------------------------------------------------
# MIGRATE SAMPLE SERIES
# ---------------------------------------------------------------------------
def create_sample_series() -> list[dict]:
    series = [
        SampleSeries(
            sample_series_id="SER-0001",
            paper_id="PPR-0001",
            pair_id="PAIR-0001",
            series_name_reported="MoS2/PbTiO3 loading series",
        ),
        SampleSeries(
            sample_series_id="SER-0002",
            paper_id="PPR-0002",
            pair_id="PAIR-0002",
            series_name_reported="MoS2/LaNiO3 loading series",
        ),
        SampleSeries(
            sample_series_id="SER-0003",
            paper_id="PPR-0003",
            pair_id="PAIR-0003",
            series_name_reported="MoS2/CaTiO3 loading series",
        ),
        SampleSeries(
            sample_series_id="SER-0004",
            paper_id="PPR-0004",
            pair_id="PAIR-0004",
            series_name_reported="CaTiO3/WS2 loading series",
        ),
    ]

    return [
        record.model_dump(mode="json")
        for record in series
    ]


# ---------------------------------------------------------------------------
# MIGRATE SAMPLES
# ---------------------------------------------------------------------------
def migrate_samples(
    records: list[dict],
) -> list[dict]:
    pair_to_series = {
        "PAIR-0001": "SER-0001",
        "PAIR-0002": "SER-0002",
        "PAIR-0003": "SER-0003",
        "PAIR-0004": "SER-0004",
    }

    migrated = []

    for record in records:
        pair_id = record.get("pair_id")

        if pair_id not in pair_to_series:
            raise ValueError(
                f"No sample-series mapping for pair_id "
                f"{pair_id!r}."
            )

        record["sample_series_id"] = (
            pair_to_series[pair_id]
        )

        validated = ExperimentalSample.model_validate(
            record
        )

        migrated.append(
            validated.model_dump(mode="json")
        )

    return migrated


# ---------------------------------------------------------------------------
# MIGRATE SYNTHESIS
# ---------------------------------------------------------------------------
def migrate_synthesis(
    samples: list[dict],
) -> list[dict]:
    synthesis_by_pair = {
        "PAIR-0001": {
            "topology": "psk_first_two_stage",
            "method_reported": "in-situ hydrothermal",
        },
        "PAIR-0002": {
            "topology": "psk_first_two_stage",
            "method_reported": "in-situ hydrothermal",
        },
        "PAIR-0003": {
            "topology": "tmd_first_two_stage",
            "method_reported": "hydrothermal",
        },
        "PAIR-0004": {
            "topology": "three_stage",
            "method_reported": (
                "ultrasonication, stirring and "
                "modified heating"
            ),
        },
    }

    migrated = []

    for index, sample in enumerate(
        samples,
        start=1,
    ):
        pair_id = sample["pair_id"]

        if pair_id not in synthesis_by_pair:
            raise ValueError(
                f"No synthesis mapping for pair_id "
                f"{pair_id!r}."
            )

        synthesis_data = synthesis_by_pair[pair_id]

        record = SynthesisRecord(
            synthesis_id=f"SYN-{index:04d}",
            sample_id=sample["sample_id"],
            topology=synthesis_data["topology"],
            method_reported=(
                synthesis_data["method_reported"]
            ),
        )

        migrated.append(
            record.model_dump(mode="json")
        )

    return migrated


# ---------------------------------------------------------------------------
# MIGRATE MECHANISM ASSESSMENTS
# ---------------------------------------------------------------------------
def migrate_mechanism_assessments(
    records: list[dict],
) -> list[dict]:
    assessment_to_series = {
        "MEA-0001": "SER-0001",
        "MEA-0002": "SER-0002",
        "MEA-0003": "SER-0003",
        "MEA-0004": "SER-0004",
    }

    migrated = []

    for record in records:
        assessment_id = record[
            "mechanism_assessment_id"
        ]

        if (
            "confidence" in record
            and "assessment_confidence"
            not in record
        ):
            record["assessment_confidence"] = (
                record.pop("confidence")
            )

        record["applies_to_series_id"] = (
            assessment_to_series[assessment_id]
        )

        validated = MechanismAssessment.model_validate(
            record
        )

        migrated.append(
            validated.model_dump(mode="json")
        )

    return migrated


# ---------------------------------------------------------------------------
# MIGRATE MECHANISM EVIDENCE
# ---------------------------------------------------------------------------
def migrate_mechanism_evidence(
    records: list[dict],
) -> list[dict]:
    migrated = []

    for record in records:
        if (
            "strength" in record
            and "evidence_strength"
            not in record
        ):
            record["evidence_strength"] = (
                record.pop("strength")
            )

        validated = MechanismEvidence.model_validate(
            record
        )

        migrated.append(
            validated.model_dump(mode="json")
        )

    return migrated


# ---------------------------------------------------------------------------
# MIGRATE PHOTOCATALYTIC TESTS
# ---------------------------------------------------------------------------
def migrate_photocatalytic_tests(
    records: list[dict],
) -> list[dict]:
    concentration_values = {
        "TST-0001": (10.0, "mg/L"),
        "TST-0008": (10.0, "mg/L"),
    }

    dark_equilibration = {
        "TST-0001": 30.0,
        "TST-0008": 30.0,
        "TST-0009": 30.0,
    }

    wavelength_min = {
        "TST-0002": 420.0,
        "TST-0003": 420.0,
        "TST-0004": 420.0,
        "TST-0005": 420.0,
        "TST-0006": 420.0,
        "TST-0009": 400.0,
    }

    migrated = []

    removed_fields = {
        "light_intensity",
        "hydrogen_amount_umol",
        "hydrogen_rate_reported_value",
        "hydrogen_rate_reported_unit",
        "hydrogen_rate_standardized_umol_g_h",
        "sth_percent",
        "apparent_quantum_yield_percent",
    }

    for record in records:
        test_id = record["test_id"]

        old_light_intensity = record.get(
            "light_intensity"
        )

        for field in removed_fields:
            record.pop(
                field,
                None,
            )

        record[
            "initial_target_concentration_value"
        ] = None
        record[
            "initial_target_concentration_unit"
        ] = None

        if test_id in concentration_values:
            value, unit = concentration_values[test_id]

            record[
                "initial_target_concentration_value"
            ] = value
            record[
                "initial_target_concentration_unit"
            ] = unit

        record["wavelength_min_nm"] = (
            wavelength_min.get(test_id)
        )
        record["wavelength_max_nm"] = None

        record["light_intensity_value"] = None
        record["light_intensity_unit"] = None

        if (
            test_id == "TST-0001"
            and old_light_intensity
            == "30000 Lux"
        ):
            record["light_intensity_value"] = 30000.0
            record["light_intensity_unit"] = "lux"

        record["dark_equilibration_time_min"] = (
            dark_equilibration.get(test_id)
        )

        record["first_cycle_performance"] = None
        record["last_cycle_performance"] = None

        validated = PhotocatalyticTest.model_validate(
            record
        )

        migrated.append(
            validated.model_dump(mode="json")
        )

    return migrated


# ---------------------------------------------------------------------------
# MIGRATE EXTRACTION RECORDS
# ---------------------------------------------------------------------------
def migrate_extraction_records(
    records: list[dict],
) -> list[dict]:
    provenance_operations = {
        "EXT-0001": "semantic_normalization",
        "EXT-0002": "unit_normalization",
        "EXT-0003": "ontology_mapping",
        "EXT-0004": "semantic_normalization",
        "EXT-0005": "semantic_normalization",
        "EXT-0006": "semantic_normalization",
        "EXT-0007": "direct_extraction",
        "EXT-0008": "ontology_mapping",
        "EXT-0009": "direct_extraction",
        "EXT-0010": "direct_extraction",
        "EXT-0011": "derived_calculation",
        "EXT-0012": "semantic_normalization",
        "EXT-0013": "direct_extraction",
        "EXT-0014": "semantic_normalization",
        "EXT-0015": "ontology_mapping",
        "EXT-0016": "ontology_mapping",
        "EXT-0017": "direct_extraction",
        "EXT-0018": "direct_extraction",
        "EXT-0019": "semantic_normalization",
        "EXT-0020": "unit_normalization",
        "EXT-0021": "direct_extraction",
        "EXT-0022": "semantic_normalization",
        "EXT-0023": "ontology_mapping",
        "EXT-0024": "ontology_mapping",
        "EXT-0025": "direct_extraction",
        "EXT-0026": "unit_normalization",
        "EXT-0027": "semantic_normalization",
        "EXT-0028": "conflict_resolution",
    }

    target_updates = {
        "EXT-0010": (
            "photocatalytic_tests",
            "TST-0004",
            "performance_metric_value",
        ),
        "EXT-0017": (
            "photocatalytic_tests",
            "TST-0007",
            "performance_metric_value",
        ),
    }

    detached_records = {
        "EXT-0007",
        "EXT-0011",
    }

    migrated = []

    for record in records:
        extraction_id = record["extraction_id"]

        record["provenance_operation"] = (
            provenance_operations[extraction_id]
        )

        if extraction_id in target_updates:
            (
                target_table,
                target_record_id,
                target_field,
            ) = target_updates[extraction_id]

            record["target_table"] = target_table
            record["target_record_id"] = (
                target_record_id
            )
            record["target_field"] = target_field

        if extraction_id in detached_records:
            record["target_table"] = None
            record["target_record_id"] = None
            record["target_field"] = None

        validated = ExtractionRecord.model_validate(
            record
        )

        migrated.append(
            validated.model_dump(mode="json")
        )

    return migrated


# ---------------------------------------------------------------------------
# CREATE DISAGREEMENT RECORDS
# ---------------------------------------------------------------------------
def create_disagreement_records() -> list[dict]:
    records = [
        DisagreementRecord(
            disagreement_id="DSG-0001",
            disagreement_type="within_paper",
            status="curator_resolved",
            paper_ids=["PPR-0004"],
            target_table="photocatalytic_tests",
            target_record_ids=["TST-0009"],
            target_field="performance_metric_value",
            reported_values=[
                "more than 96%",
                "91.12%",
            ],
            selected_value="91.12%",
            description=(
                "The abstract reports more than 96% EE2 "
                "removal, while the detailed results report "
                "91.12%."
            ),
            resolution_notes=(
                "The detailed results value of 91.12% is "
                "used in the structured photocatalytic-test "
                "record."
            ),
        ),
        DisagreementRecord(
            disagreement_id="DSG-0002",
            disagreement_type="within_paper",
            status="curator_resolved",
            paper_ids=["PPR-0004"],
            target_table="samples",
            target_record_ids=[
                "SMP-0014",
                "SMP-0015",
                "SMP-0016",
            ],
            target_field=(
                "heterostructure."
                "component_ratio_reported"
            ),
            reported_values=[
                "1:1 CaTiO3/WS2 mixing ratio",
                (
                    "10 wt%, 20 wt%, and 30 wt% "
                    "CaTiO3 sample series"
                ),
            ],
            selected_value=(
                "10 wt%, 20 wt%, and 30 wt% "
                "CaTiO3 sample labels"
            ),
            description=(
                "The synthesis section contains a 1:1 "
                "mixing statement that conflicts with the "
                "reported 10/20/30 wt% sample series."
            ),
            resolution_notes=(
                "The explicit sample labels and later "
                "performance/mechanism discussion are used "
                "for normalized compositions."
            ),
        ),
        DisagreementRecord(
            disagreement_id="DSG-0003",
            disagreement_type="within_paper",
            status="source_error",
            paper_ids=["PPR-0004"],
            target_table="mechanism_assessments",
            target_record_ids=["MEA-0004"],
            target_field="mechanism_reported",
            reported_values=[
                "direct Z-scheme CaTiO3/WS2 heterostructure",
                "LaNiO3/g-C3N4",
            ],
            selected_value=(
                "direct Z-scheme CaTiO3/WS2 "
                "heterostructure"
            ),
            description=(
                "The abstract contains an unrelated "
                "LaNiO3/g-C3N4 phrase inconsistent with "
                "the CaTiO3/WS2 study."
            ),
            resolution_notes=(
                "The unrelated phrase is treated as a "
                "source-text error and is not propagated "
                "into the normalized mechanism label."
            ),
        ),
    ]

    return [
        record.model_dump(mode="json")
        for record in records
    ]


# ---------------------------------------------------------------------------
# VALIDATE PAPERS
# ---------------------------------------------------------------------------
def validate_papers(
    records: list[dict],
) -> list[dict]:
    return [
        PaperRecord.model_validate(
            record
        ).model_dump(mode="json")
        for record in records
    ]


# ---------------------------------------------------------------------------
# MAIN MIGRATION
# ---------------------------------------------------------------------------
def main() -> None:
    if not PILOT_DIR.exists():
        raise FileNotFoundError(
            f"Pilot directory not found: {PILOT_DIR}"
        )

    backup_v0_1_pilot()

    papers = load_json("papers.json")
    samples = load_json("samples.json")
    mechanism_assessments = load_json(
        "mechanism_assessments.json"
    )
    mechanism_evidence = load_json(
        "mechanism_evidence.json"
    )
    photocatalytic_tests = load_json(
        "photocatalytic_tests.json"
    )
    extraction_records = load_json(
        "extraction_records.json"
    )

    migrated_papers = validate_papers(
        papers
    )

    sample_series = create_sample_series()

    migrated_samples = migrate_samples(
        samples
    )

    synthesis_records = migrate_synthesis(
        migrated_samples
    )

    migrated_assessments = (
        migrate_mechanism_assessments(
            mechanism_assessments
        )
    )

    migrated_evidence = (
        migrate_mechanism_evidence(
            mechanism_evidence
        )
    )

    migrated_tests = (
        migrate_photocatalytic_tests(
            photocatalytic_tests
        )
    )

    migrated_extractions = (
        migrate_extraction_records(
            extraction_records
        )
    )

    disagreement_records = (
        create_disagreement_records()
    )

    save_json(
        "papers.json",
        migrated_papers,
    )
    save_json(
        "sample_series.json",
        sample_series,
    )
    save_json(
        "samples.json",
        migrated_samples,
    )
    save_json(
        "synthesis_records.json",
        synthesis_records,
    )
    save_json(
        "mechanism_assessments.json",
        migrated_assessments,
    )
    save_json(
        "mechanism_evidence.json",
        migrated_evidence,
    )
    save_json(
        "photocatalytic_tests.json",
        migrated_tests,
    )
    save_json(
        "extraction_records.json",
        migrated_extractions,
    )
    save_json(
        "disagreement_records.json",
        disagreement_records,
    )

    old_synthesis_path = (
        PILOT_DIR
        / "synthesis_steps.json"
    )

    old_synthesis_path.unlink()

    counts = validate_pilot_directory(
        PILOT_DIR
    )

    validate_pilot_relationships(
        PILOT_DIR
    )

    print("Migration completed successfully.")
    print()
    print("Pilot table counts:")

    for filename, count in counts.items():
        print(
            f"  {filename}: {count}"
        )

    print()
    print(
        f"v0.1 backup: {BACKUP_DIR}"
    )


if __name__ == "__main__":
    main()


