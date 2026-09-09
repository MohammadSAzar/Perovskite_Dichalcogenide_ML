import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.provider import (
    identify_provider,
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

ROUTE_PROPOSALS_PATH = (
    INPUT_DIR
    / "acquisition_route_proposals.json"
)

URL_VERIFICATION_PATH = (
    INPUT_DIR
    / "url_verification_results.json"
)

OUTPUT_PATH = (
    INPUT_DIR
    / "provider_identifications.json"
)

SUMMARY_PATH = (
    INPUT_DIR
    / "provider_identification_summary.json"
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
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# INDEX RECORDS BY ACCESS ID
# ---------------------------------------------------------------------------
def index_by_access_id(
    records: list[dict],
) -> dict[str, dict]:
    index = {}

    for record in records:
        access_id = (
            record.get(
                "access_id"
            )
        )

        if not access_id:
            raise ValueError(
                "Record is missing access_id."
            )

        if access_id in index:
            raise ValueError(
                "Duplicate access_id: "
                f"{access_id}"
            )

        index[
            access_id
        ] = record

    return index


# ---------------------------------------------------------------------------
# SELECT PROVIDER URL
# ---------------------------------------------------------------------------
def select_provider_url(
    verification: dict,
) -> str | None:
    final_url = (
        verification.get(
            "final_url"
        )
    )

    if final_url:
        return final_url

    requested_url = (
        verification.get(
            "requested_url"
        )
    )

    if requested_url:
        return requested_url

    return None


# ---------------------------------------------------------------------------
# BUILD PROVIDER RECORD
# ---------------------------------------------------------------------------
def build_provider_record(
    route_record: dict,
    verification_record: dict,
) -> dict:
    access_id = (
        route_record[
            "access_id"
        ]
    )

    candidate_id = (
        route_record.get(
            "candidate_id"
        )
        or verification_record.get(
            "candidate_id"
        )
    )

    publisher = (
        route_record.get(
            "publisher"
        )
        or verification_record.get(
            "publisher"
        )
    )

    provider_url = (
        select_provider_url(
            verification_record
        )
    )

    identification = (
        identify_provider(
            publisher=(
                publisher
            ),
            url=(
                provider_url
            ),
        )
    )

    return {
        "access_id": (
            access_id
        ),
        "candidate_id": (
            candidate_id
        ),
        "doi": (
            route_record.get(
                "doi"
            )
            or verification_record.get(
                "doi"
            )
        ),
        "publisher": (
            publisher
        ),
        "requested_url": (
            verification_record.get(
                "requested_url"
            )
        ),
        "final_url": (
            verification_record.get(
                "final_url"
            )
        ),
        "provider_url": (
            provider_url
        ),
        "url_verification_success": (
            verification_record.get(
                "success"
            )
        ),
        "url_status_code": (
            verification_record.get(
                "status_code"
            )
        ),
        "appears_pdf": (
            verification_record.get(
                "appears_pdf",
                False,
            )
        ),
        "appears_html": (
            verification_record.get(
                "appears_html",
                False,
            )
        ),
        "proposed_route": (
            route_record.get(
                "proposed_route"
            )
        ),
        "original_location_type": (
            route_record.get(
                "location_type"
            )
        ),
        "provider_key": (
            identification.provider_key
        ),
        "provider_name": (
            identification.provider_name
        ),
        "provider_type": (
            identification.provider_type.value
        ),
        "matched_from": (
            identification.matched_from
        ),
        "reason": (
            identification.reason
        ),
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    route_records = (
        load_json(
            ROUTE_PROPOSALS_PATH
        )
    )

    verification_records = (
        load_json(
            URL_VERIFICATION_PATH
        )
    )

    route_index = (
        index_by_access_id(
            route_records
        )
    )

    verification_index = (
        index_by_access_id(
            verification_records
        )
    )

    route_ids = set(
        route_index
    )

    verification_ids = set(
        verification_index
    )

    if (
        route_ids
        != verification_ids
    ):
        missing_verification = (
            sorted(
                route_ids
                - verification_ids
            )
        )

        missing_routes = (
            sorted(
                verification_ids
                - route_ids
            )
        )

        raise ValueError(
            "Access-ID mismatch between "
            "route proposals and URL "
            "verification results. "
            f"missing_verification="
            f"{missing_verification}, "
            f"missing_routes="
            f"{missing_routes}"
        )

    provider_records = []

    for access_id in sorted(
        route_index
    ):
        provider_records.append(
            build_provider_record(
                route_index[
                    access_id
                ],
                verification_index[
                    access_id
                ],
            )
        )

    provider_counts = {}

    provider_type_counts = {}

    matched_from_counts = {
        "hostname": 0,
        "publisher": 0,
        "none": 0,
    }

    unidentified = []

    for record in provider_records:
        provider_key = (
            record[
                "provider_key"
            ]
            or "unidentified"
        )

        provider_counts[
            provider_key
        ] = (
            provider_counts.get(
                provider_key,
                0,
            )
            + 1
        )

        provider_type = (
            record[
                "provider_type"
            ]
        )

        provider_type_counts[
            provider_type
        ] = (
            provider_type_counts.get(
                provider_type,
                0,
            )
            + 1
        )

        matched_from = (
            record[
                "matched_from"
            ]
        )

        if (
            matched_from
            and matched_from.startswith(
                "hostname:"
            )
        ):
            matched_from_counts[
                "hostname"
            ] += 1

        elif (
            matched_from
            and matched_from.startswith(
                "publisher:"
            )
        ):
            matched_from_counts[
                "publisher"
            ] += 1

        else:
            matched_from_counts[
                "none"
            ] += 1

        if (
            record[
                "provider_key"
            ]
            is None
        ):
            unidentified.append(
                record[
                    "access_id"
                ]
            )

    summary = {
        "input_route_records": (
            len(
                route_records
            )
        ),
        "input_verification_records": (
            len(
                verification_records
            )
        ),
        "provider_identification_count": (
            len(
                provider_records
            )
        ),
        "provider_counts": (
            dict(
                sorted(
                    provider_counts.items()
                )
            )
        ),
        "provider_type_counts": (
            dict(
                sorted(
                    provider_type_counts.items()
                )
            )
        ),
        "matched_from_counts": (
            matched_from_counts
        ),
        "unidentified_access_ids": (
            unidentified
        ),
    }

    save_json(
        OUTPUT_PATH,
        provider_records,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT PROVIDER IDENTIFICATION"
    )

    print(
        "=" * 120
    )

    print(
        f"route_records="
        f"{len(route_records)}"
    )

    print(
        f"verification_records="
        f"{len(verification_records)}"
    )

    print(
        f"provider_records="
        f"{len(provider_records)}"
    )

    print()

    print(
        "PROVIDER COUNTS"
    )

    print(
        "-" * 120
    )

    for (
        provider_key,
        count,
    ) in sorted(
        provider_counts.items()
    ):
        print(
            f"{provider_key:<25} "
            f"{count}"
        )

    print()

    print(
        "PROVIDER TYPE COUNTS"
    )

    print(
        "-" * 120
    )

    for (
        provider_type,
        count,
    ) in sorted(
        provider_type_counts.items()
    ):
        print(
            f"{provider_type:<25} "
            f"{count}"
        )

    print()

    print(
        "MATCH SOURCE COUNTS"
    )

    print(
        "-" * 120
    )

    for (
        source,
        count,
    ) in matched_from_counts.items():
        print(
            f"{source:<25} "
            f"{count}"
        )

    print()

    print(
        "IDENTIFICATIONS"
    )

    print(
        "-" * 180
    )

    for record in provider_records:
        print(
            f"{record['access_id']:<12} "
            f"{record['candidate_id'] or '-':<12} "
            f"provider="
            f"{str(record['provider_key'] or '-'):<18} "
            f"type="
            f"{record['provider_type']:<12} "
            f"route="
            f"{str(record['proposed_route'] or '-')}"
        )

        print(
            f"{'':12}"
            f"publisher="
            f"{record['publisher'] or '-'}"
        )

        print(
            f"{'':12}"
            f"matched_from="
            f"{record['matched_from'] or '-'}"
        )

        print(
            f"{'':12}"
            f"requested="
            f"{record['requested_url'] or '-'}"
        )

        print(
            f"{'':12}"
            f"final="
            f"{record['final_url'] or '-'}"
        )

        print(
            f"{'':12}"
            f"verified="
            f"{record['url_verification_success']} "
            f"status="
            f"{record['url_status_code']} "
            f"pdf="
            f"{record['appears_pdf']} "
            f"html="
            f"{record['appears_html']}"
        )

        print(
            "-" * 180
        )

    print()

    if unidentified:
        print(
            "UNIDENTIFIED ACCESS IDS"
        )

        print(
            "-" * 120
        )

        for access_id in unidentified:
            print(
                access_id
            )

        print()

    print(
        "SAVED FILES"
    )

    print(
        "-" * 120
    )

    print(
        OUTPUT_PATH.relative_to(
            PROJECT_ROOT
        )
    )

    print(
        SUMMARY_PATH.relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()

