import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.models import (
    AcquisitionRoute,
)
from psk_tmd.corpus.access.route_refinement import (
    refine_acquisition_route,
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

ACQUISITION_DECISIONS_PATH = (
    INPUT_DIR
    / "acquisition_decisions.json"
)

PROVIDER_IDENTIFICATIONS_PATH = (
    INPUT_DIR
    / "provider_identifications.json"
)

OUTPUT_PATH = (
    INPUT_DIR
    / "route_refinements.json"
)

SUMMARY_PATH = (
    INPUT_DIR
    / "route_refinement_summary.json"
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
    index = {}

    for record in records:
        access_id = (
            record[
                "access_id"
            ]
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
# BUILD REFINEMENT RECORD
# ---------------------------------------------------------------------------
def build_refinement_record(
    decision_record: dict,
    provider_record: dict,
) -> dict:
    original_route = (
        AcquisitionRoute(
            decision_record[
                "route"
            ]
        )
    )

    result = (
        refine_acquisition_route(
            access_id=(
                decision_record[
                    "access_id"
                ]
            ),
            candidate_id=(
                decision_record[
                    "candidate_id"
                ]
            ),
            provider_key=(
                decision_record.get(
                    "provider_key"
                )
            ),
            original_route=(
                original_route
            ),
            requested_url=(
                provider_record.get(
                    "requested_url"
                )
            ),
            final_url=(
                provider_record.get(
                    "final_url"
                )
            ),
            doi=(
                decision_record.get(
                    "doi"
                )
            ),
        )
    )

    return {
        "access_id": (
            result.access_id
        ),
        "candidate_id": (
            result.candidate_id
        ),
        "doi": (
            result.doi
        ),
        "provider_key": (
            result.provider_key
        ),
        "original_route": (
            result.original_route.value
        ),
        "refined_route": (
            result.refined_route.value
        ),
        "route_changed": (
            result.route_changed
        ),
        "basis": (
            result.basis.value
        ),
        "stable_source_url": (
            result.stable_source_url
        ),
        "observed_final_url": (
            result.observed_final_url
        ),
        "requires_endpoint_resolution": (
            result
            .requires_endpoint_resolution
        ),
        "reason": (
            result.reason
        ),
        "current_decision": (
            decision_record[
                "decision"
            ]
        ),
        "url_verification_success": (
            decision_record.get(
                "url_verification_success"
            )
        ),
        "appears_pdf": (
            decision_record.get(
                "appears_pdf"
            )
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
    decision_records = (
        load_json(
            ACQUISITION_DECISIONS_PATH
        )
    )

    provider_records = (
        load_json(
            PROVIDER_IDENTIFICATIONS_PATH
        )
    )

    decision_index = (
        index_by_access_id(
            decision_records
        )
    )

    provider_index = (
        index_by_access_id(
            provider_records
        )
    )

    decision_ids = set(
        decision_index
    )

    provider_ids = set(
        provider_index
    )

    if (
        decision_ids
        != provider_ids
    ):
        missing_provider = (
            sorted(
                decision_ids
                - provider_ids
            )
        )

        missing_decision = (
            sorted(
                provider_ids
                - decision_ids
            )
        )

        raise ValueError(
            "Access-ID mismatch between "
            "acquisition decisions and "
            "provider identifications. "
            f"missing_provider="
            f"{missing_provider}, "
            f"missing_decision="
            f"{missing_decision}"
        )

    refinement_records = []

    for access_id in sorted(
        decision_index
    ):
        refinement_records.append(
            build_refinement_record(
                decision_index[
                    access_id
                ],
                provider_index[
                    access_id
                ],
            )
        )

    changed_ids = [
        record[
            "access_id"
        ]
        for record
        in refinement_records
        if record[
            "route_changed"
        ]
    ]

    endpoint_resolution_ids = [
        record[
            "access_id"
        ]
        for record
        in refinement_records
        if record[
            "requires_endpoint_resolution"
        ]
    ]

    summary = {
        "input_decision_count": (
            len(
                decision_records
            )
        ),
        "input_provider_count": (
            len(
                provider_records
            )
        ),
        "refinement_count": (
            len(
                refinement_records
            )
        ),
        "original_route_counts": (
            count_values(
                refinement_records,
                "original_route",
            )
        ),
        "refined_route_counts": (
            count_values(
                refinement_records,
                "refined_route",
            )
        ),
        "basis_counts": (
            count_values(
                refinement_records,
                "basis",
            )
        ),
        "route_changed_access_ids": (
            changed_ids
        ),
        "endpoint_resolution_access_ids": (
            endpoint_resolution_ids
        ),
    }

    save_json(
        OUTPUT_PATH,
        refinement_records,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT ROUTE REFINEMENT"
    )

    print(
        "=" * 120
    )

    print(
        f"decision_records="
        f"{len(decision_records)}"
    )

    print(
        f"provider_records="
        f"{len(provider_records)}"
    )

    print(
        f"refinements="
        f"{len(refinement_records)}"
    )

    print()

    print(
        "ORIGINAL ROUTE COUNTS"
    )

    print(
        "-" * 120
    )

    for (
        route,
        count,
    ) in count_values(
        refinement_records,
        "original_route",
    ).items():
        print(
            f"{route:<25} "
            f"{count}"
        )

    print()

    print(
        "REFINED ROUTE COUNTS"
    )

    print(
        "-" * 120
    )

    for (
        route,
        count,
    ) in count_values(
        refinement_records,
        "refined_route",
    ).items():
        print(
            f"{route:<25} "
            f"{count}"
        )

    print()

    print(
        "REFINEMENTS"
    )

    print(
        "-" * 180
    )

    for record in refinement_records:
        print(
            f"{record['access_id']:<12} "
            f"{record['candidate_id']:<12} "
            f"provider="
            f"{str(record['provider_key'] or '-'):<18} "
            f"{record['original_route']:<22} "
            f"-> "
            f"{record['refined_route']:<22}"
        )

        print(
            f"{'':12}"
            f"changed="
            f"{record['route_changed']} "
            f"basis="
            f"{record['basis']} "
            f"endpoint_resolution="
            f"{record['requires_endpoint_resolution']}"
        )

        print(
            f"{'':12}"
            f"stable_source="
            f"{record['stable_source_url'] or '-'}"
        )

        print(
            f"{'':12}"
            f"observed_final="
            f"{record['observed_final_url'] or '-'}"
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
        "ROUTE CHANGED IDS"
    )

    print(
        "-" * 120
    )

    if changed_ids:
        for access_id in changed_ids:
            print(
                access_id
            )

    else:
        print(
            "none"
        )

    print()

    print(
        "ENDPOINT RESOLUTION IDS"
    )

    print(
        "-" * 120
    )

    if endpoint_resolution_ids:
        for access_id in endpoint_resolution_ids:
            print(
                access_id
            )

    else:
        print(
            "none"
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


