import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.elsevier_api import (
    build_elsevier_article_api_request,
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

ROUTE_REFINEMENTS_PATH = (
    INPUT_DIR
    / "route_refinements.json"
)

OUTPUT_PATH = (
    INPUT_DIR
    / "elsevier_api_requests.json"
)

SUMMARY_PATH = (
    INPUT_DIR
    / "elsevier_api_request_summary.json"
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
# SELECT ELSEVIER API RECORDS
# ---------------------------------------------------------------------------
def select_elsevier_api_records(
    records: list[
        dict
    ],
) -> list[
    dict
]:
    return [
        record
        for record
        in records
        if (
            record.get(
                "provider_key"
            )
            == "elsevier"
            and record.get(
                "refined_route"
            )
            == "official_api"
        )
    ]


# ---------------------------------------------------------------------------
# BUILD API REQUEST RECORD
# ---------------------------------------------------------------------------
def build_api_request_record(
    route_record: dict,
) -> dict:
    doi = (
        route_record.get(
            "doi"
        )
    )

    if not doi:
        raise ValueError(
            "Elsevier API route requires "
            "a DOI. "
            f"access_id="
            f"{route_record.get('access_id')}"
        )

    request = (
        build_elsevier_article_api_request(
            doi
        )
    )

    return {
        "access_id": (
            route_record[
                "access_id"
            ]
        ),
        "candidate_id": (
            route_record[
                "candidate_id"
            ]
        ),
        "doi": (
            request.doi
        ),
        "provider_key": (
            route_record[
                "provider_key"
            ]
        ),
        "route": (
            route_record[
                "refined_route"
            ]
        ),
        "endpoint_url": (
            request.endpoint_url
        ),
        "accept": (
            request.accept
        ),
        "view": (
            request.view
        ),
        "requires_api_key": (
            request.requires_api_key
        ),
        "api_key_header": (
            request.api_key_header
        ),
        "requires_entitlement_check": (
            request
            .requires_entitlement_check
        ),
        "credential_status": (
            "not_evaluated"
        ),
        "entitlement_status": (
            "not_evaluated"
        ),
        "stable_source_url": (
            route_record.get(
                "stable_source_url"
            )
        ),
        "observed_final_url": (
            route_record.get(
                "observed_final_url"
            )
        ),
        "notes": (
            "Request specification only. "
            "No API key is stored and no "
            "network request has been made."
        ),
    }


# ---------------------------------------------------------------------------
# COUNT VALUES
# ---------------------------------------------------------------------------
def count_values(
    records: list[
        dict
    ],
    field: str,
) -> dict[
    str,
    int
]:
    counts = {}

    for record in records:
        value = (
            record[
                field
            ]
        )

        counts[
            value
        ] = (
            counts.get(
                value,
                0,
            )
            + 1
        )

    return dict(
        sorted(
            counts.items()
        )
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    route_records = (
        load_json(
            ROUTE_REFINEMENTS_PATH
        )
    )

    elsevier_records = (
        select_elsevier_api_records(
            route_records
        )
    )

    api_request_records = [
        build_api_request_record(
            record
        )
        for record
        in sorted(
            elsevier_records,
            key=lambda item: (
                item[
                    "access_id"
                ]
            ),
        )
    ]

    summary = {
        "input_route_record_count": (
            len(
                route_records
            )
        ),
        "elsevier_api_route_count": (
            len(
                elsevier_records
            )
        ),
        "api_request_count": (
            len(
                api_request_records
            )
        ),
        "accept_counts": (
            count_values(
                api_request_records,
                "accept",
            )
        ),
        "credential_status_counts": (
            count_values(
                api_request_records,
                "credential_status",
            )
        ),
        "entitlement_status_counts": (
            count_values(
                api_request_records,
                "entitlement_status",
            )
        ),
        "access_ids": [
            record[
                "access_id"
            ]
            for record
            in api_request_records
        ],
    }

    save_json(
        OUTPUT_PATH,
        api_request_records,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT ELSEVIER API REQUESTS"
    )

    print(
        "=" * 120
    )

    print(
        f"input_route_records="
        f"{len(route_records)}"
    )

    print(
        f"elsevier_api_routes="
        f"{len(elsevier_records)}"
    )

    print(
        f"api_requests="
        f"{len(api_request_records)}"
    )

    print()

    print(
        "REQUESTS"
    )

    print(
        "-" * 180
    )

    for record in api_request_records:
        print(
            f"{record['access_id']:<12} "
            f"{record['candidate_id']:<12} "
            f"doi="
            f"{record['doi']}"
        )

        print(
            f"{'':12}"
            f"endpoint="
            f"{record['endpoint_url']}"
        )

        print(
            f"{'':12}"
            f"accept="
            f"{record['accept']} "
            f"view="
            f"{record['view']}"
        )

        print(
            f"{'':12}"
            f"requires_api_key="
            f"{record['requires_api_key']} "
            f"header="
            f"{record['api_key_header']}"
        )

        print(
            f"{'':12}"
            f"credential_status="
            f"{record['credential_status']} "
            f"entitlement_status="
            f"{record['entitlement_status']}"
        )

        print(
            "-" * 180
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

