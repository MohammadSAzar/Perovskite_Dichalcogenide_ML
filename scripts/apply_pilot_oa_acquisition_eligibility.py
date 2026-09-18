import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.oa_eligibility import (
    resolve_oa_eligibility,
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

LOCATION_PATH = (
    INPUT_DIR
    / "openalex_location_classifications.json"
)

VERIFICATION_PATH = (
    INPUT_DIR
    / "url_verification_results.json"
)

POLICY_PATH = (
    INPUT_DIR
    / "combined_policy_resolutions.json"
)

ROUTE_PATH = (
    INPUT_DIR
    / "route_refinements.json"
)

OUTPUT_PATH = (
    INPUT_DIR
    / "oa_acquisition_eligibility.json"
)

SUMMARY_PATH = (
    INPUT_DIR
    / "oa_acquisition_eligibility_summary.json"
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
# INDEX BY ACCESS ID
# ---------------------------------------------------------------------------
def index_by_access_id(
    records: list[
        dict
    ],
) -> dict[
    str,
    dict
]:
    return {
        record[
            "access_id"
        ]: record
        for record
        in records
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
    location_records = (
        load_json(
            LOCATION_PATH
        )
    )

    verification_records = (
        load_json(
            VERIFICATION_PATH
        )
    )

    policy_records = (
        load_json(
            POLICY_PATH
        )
    )

    route_records = (
        load_json(
            ROUTE_PATH
        )
    )

    locations = (
        index_by_access_id(
            location_records
        )
    )

    verifications = (
        index_by_access_id(
            verification_records
        )
    )

    policies = (
        index_by_access_id(
            policy_records
        )
    )

    routes = (
        index_by_access_id(
            route_records
        )
    )

    access_ids = sorted(
        set(
            locations
        )
        & set(
            policies
        )
        & set(
            routes
        )
    )

    resolutions = []

    for access_id in access_ids:
        location = (
            locations[
                access_id
            ]
        )

        policy = (
            policies[
                access_id
            ]
        )

        route = (
            routes[
                access_id
            ]
        )

        verification = (
            verifications.get(
                access_id
            )
        )

        source_url = (
            route.get(
                "stable_source_url"
            )
            or location.get(
                "source_url"
            )
        )

        result = (
            resolve_oa_eligibility(
                access_id=(
                    access_id
                ),
                candidate_id=(
                    route[
                        "candidate_id"
                    ]
                ),
                location_type=(
                    location[
                        "location_type"
                    ]
                ),
                source_url=(
                    source_url
                ),
                url_verified=(
                    bool(
                        verification
                        and verification.get(
                            "success"
                        )
                    )
                ),
                appears_pdf=(
                    bool(
                        verification
                        and verification.get(
                            "appears_pdf"
                        )
                    )
                ),
                tdm_status=(
                    policy[
                        "tdm_status"
                    ]
                ),
                automated_access_status=(
                    policy[
                        "automated_access_status"
                    ]
                ),
                local_copy_status=(
                    policy[
                        "local_copy_status"
                    ]
                ),
            )
        )

        resolutions.append(
            result.model_dump(
                mode="json"
            )
        )

    summary = {
        "location_record_count": (
            len(
                location_records
            )
        ),
        "verification_record_count": (
            len(
                verification_records
            )
        ),
        "policy_record_count": (
            len(
                policy_records
            )
        ),
        "route_record_count": (
            len(
                route_records
            )
        ),
        "resolved_record_count": (
            len(
                resolutions
            )
        ),
        "eligible_count": (
            sum(
                1
                for record
                in resolutions
                if record[
                    "eligible_for_oa_acquisition"
                ]
            )
        ),
        "acquisition_mode_counts": (
            count_values(
                resolutions,
                "acquisition_mode",
            )
        ),
        "preferred_source_counts": (
            count_values(
                resolutions,
                "preferred_source",
            )
        ),
        "pdf_verified_count": (
            sum(
                1
                for record
                in resolutions
                if record[
                    "pdf_verified"
                ]
            )
        ),
    }

    save_json(
        OUTPUT_PATH,
        resolutions,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT OA ACQUISITION ELIGIBILITY"
    )

    print(
        "=" * 120
    )

    print(
        f"resolved_records="
        f"{len(resolutions)}"
    )

    print(
        f"eligible="
        f"{summary['eligible_count']}"
    )

    print(
        f"pdf_verified="
        f"{summary['pdf_verified_count']}"
    )

    print()

    print(
        "ACQUISITION MODES"
    )

    print(
        "-" * 120
    )

    for (
        mode,
        count,
    ) in (
        summary[
            "acquisition_mode_counts"
        ].items()
    ):
        print(
            f"{mode:<24} "
            f"{count}"
        )

    print()

    print(
        "RECORDS"
    )

    print(
        "-" * 180
    )

    for record in resolutions:
        print(
            f"{record['access_id']:<12} "
            f"{record['candidate_id']:<12} "
            f"mode="
            f"{record['acquisition_mode']:<16} "
            f"source="
            f"{record['preferred_source']:<12} "
            f"pdf="
            f"{record['pdf_verified']}"
        )

        print(
            f"{'':12}"
            f"reason="
            f"{record['reason']}"
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

