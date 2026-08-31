import json

from datetime import (
    date,
)
from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.models import (
    AccessRecord,
)
from psk_tmd.corpus.access.openalex import (
    resolve_openalex_evidence,
)


# ---------------------------------------------------------------------------
# INPUT CONFIGURATION
# ---------------------------------------------------------------------------
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
    / "initial_access_records.json"
)

SMOKE_TEST_ACCESS_IDS = (
    "ACC-000003",
    "ACC-000006",
    "ACC-000027",
)

TIMEOUT_SECONDS = 30.0


# ---------------------------------------------------------------------------
# LOAD JSON
# ---------------------------------------------------------------------------
def load_json(
    path: Path,
) -> list[
    dict
]:
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


# ---------------------------------------------------------------------------
# LOAD ACCESS RECORDS
# ---------------------------------------------------------------------------
def load_access_records(
    path: Path,
) -> list[
    AccessRecord
]:
    payloads = (
        load_json(
            path
        )
    )

    return [
        AccessRecord.model_validate(
            payload
        )
        for payload in payloads
    ]


# ---------------------------------------------------------------------------
# SELECT SMOKE TEST RECORDS
# ---------------------------------------------------------------------------
def select_smoke_test_records(
    records: list[
        AccessRecord
    ],
) -> list[
    AccessRecord
]:
    records_by_id = {
        record.access_id: record
        for record in records
    }

    selected = []

    for access_id in SMOKE_TEST_ACCESS_IDS:
        record = (
            records_by_id.get(
                access_id
            )
        )

        if record is None:
            raise ValueError(
                "Smoke-test access record "
                f"was not found: {access_id}"
            )

        selected.append(
            record
        )

    return selected


# ---------------------------------------------------------------------------
# FORMAT DISCOVERY OA
# ---------------------------------------------------------------------------
def format_discovery_oa(
    value: bool | None,
) -> str:
    if value is True:
        return "TRUE"

    if value is False:
        return "FALSE"

    return "UNKNOWN"


# ---------------------------------------------------------------------------
# PRINT EVIDENCE RECORD
# ---------------------------------------------------------------------------
def print_evidence_record(
    evidence,
) -> None:
    print(
        f"    {evidence.evidence_id:<12} "
        f"type={evidence.evidence_type.value:<20} "
        f"source={evidence.source.value:<10} "
        f"value={evidence.value or '-'}"
    )

    print(
        f"{'':16}"
        f"source_name="
        f"{evidence.source_name or '-'}"
    )

    print(
        f"{'':16}"
        f"source_url="
        f"{evidence.source_url or '-'}"
    )

    print(
        f"{'':16}"
        f"basis="
        f"{evidence.basis or '-'}"
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    access_records = (
        load_access_records(
            INPUT_PATH
        )
    )

    test_records = (
        select_smoke_test_records(
            access_records
        )
    )

    observed_date = (
        date.today()
    )

    next_evidence_index = 1

    successful_records = 0

    failed_records = 0

    total_evidence = 0

    print(
        "OPENALEX ACCESS EVIDENCE LIVE PREVIEW"
    )
    print(
        "=" * 150
    )

    print(
        f"input_file="
        f"{INPUT_PATH.relative_to(PROJECT_ROOT)}"
    )

    print(
        f"selected_records="
        f"{len(test_records)}"
    )

    print(
        f"observed_date="
        f"{observed_date.isoformat()}"
    )

    print()

    for access_record in test_records:
        print(
            "-" * 150
        )

        print(
            f"{access_record.access_id:<12} "
            f"{access_record.candidate_id:<12} "
            f"discovery_OA="
            f"{format_discovery_oa(access_record.is_open_access):<8} "
            f"DOI="
            f"{access_record.doi or '-'}"
        )

        print(
            f"{'':12}"
            f"publisher="
            f"{access_record.publisher or '-'}"
        )

        try:
            evidence_records = (
                resolve_openalex_evidence(
                    access_record,
                    start_index=(
                        next_evidence_index
                    ),
                    observed_date=(
                        observed_date
                    ),
                    timeout=(
                        TIMEOUT_SECONDS
                    ),
                )
            )

        except Exception as exc:
            failed_records += 1

            print(
                f"{'':12}"
                f"LOOKUP FAILED: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            continue

        successful_records += 1

        total_evidence += len(
            evidence_records
        )

        print(
            f"{'':12}"
            f"evidence_count="
            f"{len(evidence_records)}"
        )

        if not evidence_records:
            print(
                f"{'':12}"
                f"No OpenAlex evidence returned."
            )

        for evidence in evidence_records:
            print_evidence_record(
                evidence
            )

        if evidence_records:
            next_evidence_index += len(
                evidence_records
            )

    print(
        "-" * 150
    )

    print()

    print(
        "SMOKE TEST SUMMARY"
    )
    print(
        "-" * 100
    )

    print(
        f"attempted_records="
        f"{len(test_records)}"
    )

    print(
        f"successful_records="
        f"{successful_records}"
    )

    print(
        f"failed_records="
        f"{failed_records}"
    )

    print(
        f"total_evidence_records="
        f"{total_evidence}"
    )


if __name__ == "__main__":
    main()

