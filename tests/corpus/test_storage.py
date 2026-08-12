import json

import pytest

from psk_tmd.common.models import PaperRecord
from psk_tmd.corpus.storage import (
    load_model_list,
    save_model_list,
    validate_pilot_directory,
    validate_pilot_relationships,
)


# ---------------------------------------------------------------------------
# SAVE MODEL LIST
# ---------------------------------------------------------------------------
def test_save_model_list(tmp_path):
    papers = [
        PaperRecord(
            paper_id="PPR-0001",
            title="Test paper",
            authors=["Author A", "Author B"],
            year=2023,
        )
    ]

    output_path = tmp_path / "papers.json"

    save_model_list(
        models=papers,
        path=output_path,
    )

    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["paper_id"] == "PPR-0001"
    assert data[0]["title"] == "Test paper"


# ---------------------------------------------------------------------------
# LOAD MODEL LIST
# ---------------------------------------------------------------------------
def test_load_model_list(tmp_path):
    input_path = tmp_path / "papers.json"

    data = [
        {
            "paper_id": "PPR-0002",
            "title": "Loaded paper",
            "authors": ["Author C"],
            "year": 2022,
        }
    ]

    with input_path.open("w", encoding="utf-8") as file:
        json.dump(data, file)

    papers = load_model_list(
        path=input_path,
        model_class=PaperRecord,
    )

    assert len(papers) == 1
    assert isinstance(papers[0], PaperRecord)
    assert papers[0].paper_id == "PPR-0002"
    assert papers[0].title == "Loaded paper"
    assert papers[0].year == 2022


# ---------------------------------------------------------------------------
# ROUND-TRIP VALIDATION
# ---------------------------------------------------------------------------
def test_round_trip_model_list(tmp_path):
    original_papers = [
        PaperRecord(
            paper_id="PPR-0003",
            doi="10.1234/example",
            title="Round-trip paper",
            authors=["Author D"],
            year=2021,
            journal="Example Journal",
        )
    ]

    output_path = tmp_path / "papers.json"

    save_model_list(
        models=original_papers,
        path=output_path,
    )

    loaded_papers = load_model_list(
        path=output_path,
        model_class=PaperRecord,
    )

    assert loaded_papers == original_papers


# ---------------------------------------------------------------------------
# INVALID JSON ROOT
# ---------------------------------------------------------------------------
def test_load_model_list_rejects_non_list_json(tmp_path):
    input_path = tmp_path / "papers.json"

    data = {
        "paper_id": "PPR-0004",
        "title": "Wrong JSON structure",
        "year": 2020,
    }

    with input_path.open("w", encoding="utf-8") as file:
        json.dump(data, file)

    with pytest.raises(ValueError, match="Expected a JSON list"):
        load_model_list(
            path=input_path,
            model_class=PaperRecord,
        )


# ---------------------------------------------------------------------------
# INVALID MODEL RECORD
# ---------------------------------------------------------------------------
def test_load_model_list_rejects_invalid_record(tmp_path):
    input_path = tmp_path / "papers.json"

    data = [
        {
            "paper_id": "PPR-0005",
            "title": "Invalid paper",
            "year": 1800,
        }
    ]

    with input_path.open("w", encoding="utf-8") as file:
        json.dump(data, file)

    with pytest.raises(Exception):
        load_model_list(
            path=input_path,
            model_class=PaperRecord,
        )


# ---------------------------------------------------------------------------
# PILOT DIRECTORY VALIDATION
# ---------------------------------------------------------------------------
def test_validate_empty_pilot_directory(tmp_path):
    filenames = [
        "papers.json",
        "sample_series.json",
        "samples.json",
        "synthesis_records.json",
        "mechanism_assessments.json",
        "mechanism_evidence.json",
        "photocatalytic_tests.json",
        "extraction_records.json",
        "disagreement_records.json",
    ]

    for filename in filenames:
        file_path = tmp_path / filename

        with file_path.open("w", encoding="utf-8") as file:
            json.dump([], file)

    counts = validate_pilot_directory(tmp_path)

    assert counts == {
        "papers.json": 0,
        "sample_series.json": 0,
        "samples.json": 0,
        "synthesis_records.json": 0,
        "mechanism_assessments.json": 0,
        "mechanism_evidence.json": 0,
        "photocatalytic_tests.json": 0,
        "extraction_records.json": 0,
        "disagreement_records.json": 0,
    }


# ---------------------------------------------------------------------------
# MISSING PILOT TABLE
# ---------------------------------------------------------------------------
def test_validate_pilot_directory_rejects_missing_table(tmp_path):
    filenames = [
        "papers.json",
        "sample_series.json",
        "samples.json",
        "synthesis_records.json",
        "mechanism_assessments.json",
        "mechanism_evidence.json",
        "photocatalytic_tests.json",
        "extraction_records.json",
    ]

    for filename in filenames:
        file_path = tmp_path / filename

        with file_path.open("w", encoding="utf-8") as file:
            json.dump([], file)

    with pytest.raises(
        FileNotFoundError,
        match="Required pilot table is missing",
    ):
        validate_pilot_directory(tmp_path)


# ---------------------------------------------------------------------------
# INVALID PILOT RECORD
# ---------------------------------------------------------------------------
def test_validate_pilot_directory_rejects_invalid_record(tmp_path):
    valid_empty_files = [
        "sample_series.json",
        "samples.json",
        "synthesis_records.json",
        "mechanism_assessments.json",
        "mechanism_evidence.json",
        "photocatalytic_tests.json",
        "extraction_records.json",
        "disagreement_records.json",
    ]

    for filename in valid_empty_files:
        file_path = tmp_path / filename

        with file_path.open("w", encoding="utf-8") as file:
            json.dump([], file)

    invalid_papers = [
        {
            "paper_id": "PPR-0001",
            "title": "Invalid pilot paper",
            "year": 1800,
        }
    ]

    with (tmp_path / "papers.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(invalid_papers, file)

    with pytest.raises(Exception):
        validate_pilot_directory(tmp_path)


# ---------------------------------------------------------------------------
# VALID PILOT RELATIONSHIPS
# ---------------------------------------------------------------------------
def test_validate_pilot_relationships(tmp_path):
    tables = {
        "papers.json": [
            {
                "paper_id": "PPR-0001",
                "title": "Test paper",
                "year": 2023,
            }
        ],
        "sample_series.json": [
            {
                "sample_series_id": "SER-0001",
                "paper_id": "PPR-0001",
                "pair_id": "PAIR-0001",
            }
        ],
        "samples.json": [
            {
                "sample_id": "SMP-0001",
                "paper_id": "PPR-0001",
                "sample_series_id": "SER-0001",
                "psk": {
                    "formula_reported": "CaTiO3",
                },
                "tmd": {
                    "formula_reported": "MoS2",
                },
            }
        ],
        "synthesis_records.json": [
            {
                "synthesis_id": "SYN-0001",
                "sample_id": "SMP-0001",
                "topology": "psk_first_two_stage",
            }
        ],
        "mechanism_assessments.json": [
            {
                "mechanism_assessment_id": "MEA-0001",
                "sample_id": "SMP-0001",
                "applies_to_series_id": "SER-0001",
            }
        ],
        "mechanism_evidence.json": [
            {
                "evidence_id": "EVD-0001",
                "mechanism_assessment_id": "MEA-0001",
            }
        ],
        "photocatalytic_tests.json": [
            {
                "test_id": "TST-0001",
                "sample_id": "SMP-0001",
            }
        ],
        "extraction_records.json": [
            {
                "extraction_id": "EXT-0001",
                "paper_id": "PPR-0001",
                "target_table": "photocatalytic_tests",
                "target_record_id": "TST-0001",
                "target_field": "test_duration_h",
            }
        ],
        "disagreement_records.json": [
            {
                "disagreement_id": "DSG-0001",
                "disagreement_type": "within_paper",
                "paper_ids": ["PPR-0001"],
                "target_table": "photocatalytic_tests",
                "target_record_ids": ["TST-0001"],
                "target_field": "performance_metric_value",
                "reported_values": [
                    "90%",
                    "92%",
                ],
            }
        ],
    }

    for filename, data in tables.items():
        with (tmp_path / filename).open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(data, file)

    validate_pilot_relationships(tmp_path)


# ---------------------------------------------------------------------------
# INVALID SAMPLE PAPER LINK
# ---------------------------------------------------------------------------
def test_validate_pilot_relationships_rejects_missing_paper(tmp_path):
    tables = {
        "papers.json": [],
        "sample_series.json": [],
        "samples.json": [
            {
                "sample_id": "SMP-0001",
                "paper_id": "PPR-9999",
                "psk": {
                    "formula_reported": "CaTiO3",
                },
                "tmd": {
                    "formula_reported": "MoS2",
                },
            }
        ],
        "synthesis_records.json": [],
        "mechanism_assessments.json": [],
        "mechanism_evidence.json": [],
        "photocatalytic_tests.json": [],
        "extraction_records.json": [],
        "disagreement_records.json": [],
    }

    for filename, data in tables.items():
        with (tmp_path / filename).open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(data, file)

    with pytest.raises(
        ValueError,
        match="Invalid foreign key",
    ):
        validate_pilot_relationships(tmp_path)


# ---------------------------------------------------------------------------
# INVALID SAMPLE SERIES LINK
# ---------------------------------------------------------------------------
def test_validate_pilot_relationships_rejects_missing_sample_series(
    tmp_path,
):
    tables = {
        "papers.json": [
            {
                "paper_id": "PPR-0001",
                "title": "Test paper",
                "year": 2023,
            }
        ],
        "sample_series.json": [],
        "samples.json": [
            {
                "sample_id": "SMP-0001",
                "paper_id": "PPR-0001",
                "sample_series_id": "SER-9999",
                "psk": {
                    "formula_reported": "CaTiO3",
                },
                "tmd": {
                    "formula_reported": "MoS2",
                },
            }
        ],
        "synthesis_records.json": [],
        "mechanism_assessments.json": [],
        "mechanism_evidence.json": [],
        "photocatalytic_tests.json": [],
        "extraction_records.json": [],
        "disagreement_records.json": [],
    }

    for filename, data in tables.items():
        with (tmp_path / filename).open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(data, file)

    with pytest.raises(
        ValueError,
        match="Invalid foreign key",
    ):
        validate_pilot_relationships(tmp_path)


# ---------------------------------------------------------------------------
# INVALID MECHANISM SERIES LINK
# ---------------------------------------------------------------------------
def test_validate_pilot_relationships_rejects_bad_mechanism_series(
    tmp_path,
):
    tables = {
        "papers.json": [
            {
                "paper_id": "PPR-0001",
                "title": "Test paper",
                "year": 2023,
            }
        ],
        "sample_series.json": [],
        "samples.json": [
            {
                "sample_id": "SMP-0001",
                "paper_id": "PPR-0001",
                "psk": {
                    "formula_reported": "CaTiO3",
                },
                "tmd": {
                    "formula_reported": "MoS2",
                },
            }
        ],
        "synthesis_records.json": [],
        "mechanism_assessments.json": [
            {
                "mechanism_assessment_id": "MEA-0001",
                "sample_id": "SMP-0001",
                "applies_to_series_id": "SER-9999",
            }
        ],
        "mechanism_evidence.json": [],
        "photocatalytic_tests.json": [],
        "extraction_records.json": [],
        "disagreement_records.json": [],
    }

    for filename, data in tables.items():
        with (tmp_path / filename).open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(data, file)

    with pytest.raises(
        ValueError,
        match="Invalid foreign key",
    ):
        validate_pilot_relationships(tmp_path)


# ---------------------------------------------------------------------------
# INVALID EXTRACTION TARGET
# ---------------------------------------------------------------------------
def test_validate_pilot_relationships_rejects_bad_extraction_target(
    tmp_path,
):
    tables = {
        "papers.json": [
            {
                "paper_id": "PPR-0001",
                "title": "Test paper",
                "year": 2023,
            }
        ],
        "sample_series.json": [],
        "samples.json": [],
        "synthesis_records.json": [],
        "mechanism_assessments.json": [],
        "mechanism_evidence.json": [],
        "photocatalytic_tests.json": [],
        "extraction_records.json": [
            {
                "extraction_id": "EXT-0001",
                "paper_id": "PPR-0001",
                "target_table": "photocatalytic_tests",
                "target_record_id": "TST-9999",
                "target_field": "test_duration_h",
            }
        ],
        "disagreement_records.json": [],
    }

    for filename, data in tables.items():
        with (tmp_path / filename).open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(data, file)

    with pytest.raises(
        ValueError,
        match="Invalid foreign key",
    ):
        validate_pilot_relationships(tmp_path)


# ---------------------------------------------------------------------------
# INVALID DISAGREEMENT TARGET
# ---------------------------------------------------------------------------
def test_validate_pilot_relationships_rejects_bad_disagreement_target(
    tmp_path,
):
    tables = {
        "papers.json": [
            {
                "paper_id": "PPR-0001",
                "title": "Test paper",
                "year": 2023,
            }
        ],
        "sample_series.json": [],
        "samples.json": [],
        "synthesis_records.json": [],
        "mechanism_assessments.json": [],
        "mechanism_evidence.json": [],
        "photocatalytic_tests.json": [],
        "extraction_records.json": [],
        "disagreement_records.json": [
            {
                "disagreement_id": "DSG-0001",
                "disagreement_type": "within_paper",
                "paper_ids": ["PPR-0001"],
                "target_table": "photocatalytic_tests",
                "target_record_ids": ["TST-9999"],
                "reported_values": [
                    "90%",
                    "92%",
                ],
            }
        ],
    }

    for filename, data in tables.items():
        with (tmp_path / filename).open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(data, file)

    with pytest.raises(
        ValueError,
        match="Invalid foreign key",
    ):
        validate_pilot_relationships(tmp_path)

