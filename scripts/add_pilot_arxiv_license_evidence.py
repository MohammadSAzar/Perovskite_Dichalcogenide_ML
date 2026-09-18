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


# ---------------------------------------------------------------------------
# INPUT / OUTPUT CONFIGURATION
# ---------------------------------------------------------------------------
INPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
)

INPUT_PATH = (
    INPUT_DIR
    / "openalex_access_evidence.json"
)

OUTPUT_PATH = (
    INPUT_DIR
    / "access_evidence_with_arxiv_license.json"
)


# ---------------------------------------------------------------------------
# TARGET RECORD
# ---------------------------------------------------------------------------
TARGET_ACCESS_ID = (
    "ACC-000021"
)

TARGET_CANDIDATE_ID = (
    "CND-000143"
)

ARXIV_ABS_URL = (
    "https://arxiv.org/abs/2111.03139"
)

LICENSE_VALUE = (
    "CC BY 4.0"
)


# ---------------------------------------------------------------------------
# LOAD JSON
# ---------------------------------------------------------------------------
def load_json(
    path: Path,
):
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


# ---------------------------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------------------------
def save_json(
    path: Path,
    payload,
) -> None:
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# BUILD NEXT EVIDENCE ID
# ---------------------------------------------------------------------------
def build_next_evidence_id(
    records: list[
        dict
    ],
) -> str:
    numbers = []

    for record in records:
        evidence_id = (
            record.get(
                "evidence_id",
                "",
            )
        )

        if not evidence_id.startswith(
            "AEV-"
        ):
            continue

        suffix = (
            evidence_id.removeprefix(
                "AEV-"
            )
        )

        if suffix.isdigit():
            numbers.append(
                int(
                    suffix
                )
            )

    if not numbers:
        return (
            "AEV-000001"
        )

    return (
        f"AEV-{max(numbers) + 1:06d}"
    )


# ---------------------------------------------------------------------------
# CHECK EXISTING LICENSE EVIDENCE
# ---------------------------------------------------------------------------
def has_existing_license_evidence(
    records: list[
        dict
    ],
) -> bool:
    return any(
        (
            record.get(
                "access_id"
            )
            == TARGET_ACCESS_ID
            and record.get(
                "evidence_type"
            )
            == "license"
        )
        for record
        in records
    )


# ---------------------------------------------------------------------------
# BUILD ARXIV LICENSE EVIDENCE
# ---------------------------------------------------------------------------
def build_arxiv_license_evidence(
    records: list[
        dict
    ],
) -> dict:
    return {
        "evidence_id": (
            build_next_evidence_id(
                records
            )
        ),
        "access_id": (
            TARGET_ACCESS_ID
        ),
        "candidate_id": (
            TARGET_CANDIDATE_ID
        ),
        "evidence_type": (
            "license"
        ),
        "source": (
            "repository"
        ),
        "source_name": (
            "arXiv"
        ),
        "source_url": (
            ARXIV_ABS_URL
        ),
        "value": (
            LICENSE_VALUE
        ),
        "basis": (
            "Article-specific license "
            "displayed on the arXiv "
            "abstract page."
        ),
        "observed_date": (
            date.today().isoformat()
        ),
        "notes": (
            "CC BY 4.0 applies to the "
            "arXiv version associated "
            "with this access record."
        ),
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    records = (
        load_json(
            INPUT_PATH
        )
    )

    if (
        has_existing_license_evidence(
            records
        )
    ):
        raise ValueError(
            "License evidence already "
            "exists for "
            f"{TARGET_ACCESS_ID}."
        )

    license_record = (
        build_arxiv_license_evidence(
            records
        )
    )

    updated_records = [
        *records,
        license_record,
    ]

    save_json(
        OUTPUT_PATH,
        updated_records,
    )

    print(
        "PILOT ARXIV LICENSE EVIDENCE"
    )

    print(
        "=" * 120
    )

    print(
        f"input_records="
        f"{len(records)}"
    )

    print(
        f"output_records="
        f"{len(updated_records)}"
    )

    print(
        f"evidence_id="
        f"{license_record['evidence_id']}"
    )

    print(
        f"access_id="
        f"{license_record['access_id']}"
    )

    print(
        f"candidate_id="
        f"{license_record['candidate_id']}"
    )

    print(
        f"license="
        f"{license_record['value']}"
    )

    print(
        f"source="
        f"{license_record['source']}"
    )

    print(
        f"source_url="
        f"{license_record['source_url']}"
    )

    print()

    print(
        "SAVED FILE"
    )

    print(
        "-" * 120
    )

    print(
        OUTPUT_PATH.relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()

