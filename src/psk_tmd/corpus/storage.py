import json

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from psk_tmd.common.models import (
    ExperimentalSample,
    ExtractionRecord,
    MechanismAssessment,
    MechanismEvidence,
    PaperRecord,
    PhotocatalyticTest,
    SynthesisStep,
)


ModelT = TypeVar("ModelT", bound=BaseModel)


# ---------------------------------------------------------------------------
# PILOT TABLE DEFINITIONS
# ---------------------------------------------------------------------------
PILOT_TABLE_MODELS: dict[str, type[BaseModel]] = {
    "papers.json": PaperRecord,
    "samples.json": ExperimentalSample,
    "synthesis_steps.json": SynthesisStep,
    "mechanism_assessments.json": MechanismAssessment,
    "mechanism_evidence.json": MechanismEvidence,
    "photocatalytic_tests.json": PhotocatalyticTest,
    "extraction_records.json": ExtractionRecord,
}


# ---------------------------------------------------------------------------
# PILOT TABLE ID FIELDS
# ---------------------------------------------------------------------------
PILOT_TABLE_ID_FIELDS: dict[str, str] = {
    "papers": "paper_id",
    "samples": "sample_id",
    "synthesis_steps": "synthesis_step_id",
    "mechanism_assessments": "mechanism_assessment_id",
    "mechanism_evidence": "evidence_id",
    "photocatalytic_tests": "test_id",
    "extraction_records": "extraction_id",
}


# ---------------------------------------------------------------------------
# SAVE MODELS
# ---------------------------------------------------------------------------
def save_model_list(
        models: list[ModelT],
        path: str | Path,
    ) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = [model.model_dump(mode="json") for model in models]

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


# ---------------------------------------------------------------------------
# LOAD MODELS
# ---------------------------------------------------------------------------
def load_model_list(
        path: str | Path,
        model_class: type[ModelT],
    ) -> list[ModelT]:
    input_path = Path(path)

    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON list in {input_path}, "
            f"but found {type(data).__name__}."
        )

    return [
        model_class.model_validate(record)
        for record in data
    ]


# ---------------------------------------------------------------------------
# VALIDATE PILOT DIRECTORY
# ---------------------------------------------------------------------------
def validate_pilot_directory(
        directory: str | Path,
    ) -> dict[str, int]:
    pilot_directory = Path(directory)

    if not pilot_directory.exists():
        raise FileNotFoundError(
            f"Pilot directory does not exist: {pilot_directory}"
        )

    if not pilot_directory.is_dir():
        raise NotADirectoryError(
            f"Pilot path is not a directory: {pilot_directory}"
        )

    record_counts: dict[str, int] = {}

    for filename, model_class in PILOT_TABLE_MODELS.items():
        file_path = pilot_directory / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Required pilot table is missing: {file_path}"
            )

        records = load_model_list(
            path=file_path,
            model_class=model_class,
        )

        record_counts[filename] = len(records)

    return record_counts


# ---------------------------------------------------------------------------
# LOAD PILOT TABLES
# ---------------------------------------------------------------------------
def load_pilot_tables(
        directory: str | Path,
    ) -> dict[str, list[BaseModel]]:
    pilot_directory = Path(directory)

    tables: dict[str, list[BaseModel]] = {}

    for filename, model_class in PILOT_TABLE_MODELS.items():
        table_name = Path(filename).stem

        tables[table_name] = load_model_list(
            path=pilot_directory / filename,
            model_class=model_class,
        )

    return tables


# ---------------------------------------------------------------------------
# RECORD IDS
# ---------------------------------------------------------------------------
def get_record_ids(
        records: list[BaseModel],
        id_field: str,
    ) -> set[str]:
    return {
        getattr(record, id_field)
        for record in records
    }


# ---------------------------------------------------------------------------
# REQUIRE FOREIGN KEY
# ---------------------------------------------------------------------------
def require_foreign_key(
        value: str,
        valid_ids: set[str],
        *,
        table_name: str,
        record_id: str,
        field_name: str,
    ) -> None:
    if value not in valid_ids:
        raise ValueError(
            f"Invalid foreign key in {table_name}: "
            f"{record_id}.{field_name}={value!r} "
            f"does not reference an existing record."
        )


# ---------------------------------------------------------------------------
# VALIDATE PILOT RELATIONSHIPS
# ---------------------------------------------------------------------------
def validate_pilot_relationships(
        directory: str | Path,
    ) -> None:
    tables = load_pilot_tables(directory)

    paper_ids = get_record_ids(
        tables["papers"],
        "paper_id",
    )

    sample_ids = get_record_ids(
        tables["samples"],
        "sample_id",
    )

    mechanism_assessment_ids = get_record_ids(
        tables["mechanism_assessments"],
        "mechanism_assessment_id",
    )

    for sample in tables["samples"]:
        require_foreign_key(
            sample.paper_id,
            paper_ids,
            table_name="samples",
            record_id=sample.sample_id,
            field_name="paper_id",
        )

    for step in tables["synthesis_steps"]:
        require_foreign_key(
            step.sample_id,
            sample_ids,
            table_name="synthesis_steps",
            record_id=step.synthesis_step_id,
            field_name="sample_id",
        )

    for assessment in tables["mechanism_assessments"]:
        require_foreign_key(
            assessment.sample_id,
            sample_ids,
            table_name="mechanism_assessments",
            record_id=assessment.mechanism_assessment_id,
            field_name="sample_id",
        )

    for evidence in tables["mechanism_evidence"]:
        require_foreign_key(
            evidence.mechanism_assessment_id,
            mechanism_assessment_ids,
            table_name="mechanism_evidence",
            record_id=evidence.evidence_id,
            field_name="mechanism_assessment_id",
        )

    for test in tables["photocatalytic_tests"]:
        require_foreign_key(
            test.sample_id,
            sample_ids,
            table_name="photocatalytic_tests",
            record_id=test.test_id,
            field_name="sample_id",
        )

    for extraction in tables["extraction_records"]:
        require_foreign_key(
            extraction.paper_id,
            paper_ids,
            table_name="extraction_records",
            record_id=extraction.extraction_id,
            field_name="paper_id",
        )

        if extraction.target_table is None:
            continue

        if extraction.target_record_id is None:
            raise ValueError(
                f"{extraction.extraction_id} has target_table "
                f"but no target_record_id."
            )

        if extraction.target_table not in PILOT_TABLE_ID_FIELDS:
            raise ValueError(
                f"{extraction.extraction_id} references unknown "
                f"target_table {extraction.target_table!r}."
            )

        target_records = tables[extraction.target_table]

        target_id_field = PILOT_TABLE_ID_FIELDS[
            extraction.target_table
        ]

        target_ids = get_record_ids(
            target_records,
            target_id_field,
        )

        require_foreign_key(
            extraction.target_record_id,
            target_ids,
            table_name="extraction_records",
            record_id=extraction.extraction_id,
            field_name="target_record_id",
        )

