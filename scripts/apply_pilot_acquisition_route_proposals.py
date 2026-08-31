import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.location import (
    AccessLocationClassification,
    AccessLocationType,
)
from psk_tmd.corpus.access.route_proposal import (
    propose_acquisition_route,
)


# ---------------------------------------------------------------------------
# INPUT / OUTPUT CONFIGURATION
# ---------------------------------------------------------------------------
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
    / "openalex_location_classifications.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
)

PROPOSALS_PATH = (
    OUTPUT_DIR
    / "acquisition_route_proposals.json"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "acquisition_route_proposal_summary.json"
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
# BUILD LOCATION CLASSIFICATION
# ---------------------------------------------------------------------------
def build_location_classification(
    payload: dict,
) -> AccessLocationClassification:
    return AccessLocationClassification(
        location_type=(
            AccessLocationType(
                payload[
                    "location_type"
                ]
            )
        ),
        url=(
            payload.get(
                "location_url"
            )
        ),
        hostname=(
            payload.get(
                "hostname"
            )
        ),
        reason=(
            payload[
                "classification_reason"
            ]
        ),
    )


# ---------------------------------------------------------------------------
# BUILD ROUTE PROPOSAL RECORD
# ---------------------------------------------------------------------------
def build_route_proposal_record(
    payload: dict,
) -> dict:
    classification = (
        build_location_classification(
            payload
        )
    )

    proposal = (
        propose_acquisition_route(
            access_id=(
                payload[
                    "access_id"
                ]
            ),
            candidate_id=(
                payload[
                    "candidate_id"
                ]
            ),
            classification=(
                classification
            ),
        )
    )

    return {
        "access_id": (
            proposal.access_id
        ),
        "candidate_id": (
            proposal.candidate_id
        ),
        "doi": (
            payload.get(
                "doi"
            )
        ),
        "publisher": (
            payload.get(
                "publisher"
            )
        ),
        "openalex_oa_status": (
            payload.get(
                "openalex_oa_status"
            )
        ),
        "openalex_license": (
            payload.get(
                "openalex_license"
            )
        ),
        "openalex_version": (
            payload.get(
                "openalex_version"
            )
        ),
        "location_type": (
            proposal.location_type.value
        ),
        "source_url": (
            proposal.source_url
        ),
        "proposed_route": (
            proposal.proposed_route.value
        ),
        "reason": (
            proposal.reason
        ),
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    classification_payloads = (
        load_json(
            INPUT_PATH
        )
    )

    proposals = [
        build_route_proposal_record(
            payload
        )
        for payload
        in classification_payloads
    ]

    route_counts = {}

    location_type_counts = {}

    for proposal in proposals:
        route = (
            proposal[
                "proposed_route"
            ]
        )

        location_type = (
            proposal[
                "location_type"
            ]
        )

        route_counts[
            route
        ] = (
            route_counts.get(
                route,
                0,
            )
            + 1
        )

        location_type_counts[
            location_type
        ] = (
            location_type_counts.get(
                location_type,
                0,
            )
            + 1
        )

    summary = {
        "input_classification_count": (
            len(
                classification_payloads
            )
        ),
        "proposal_count": (
            len(
                proposals
            )
        ),
        "location_type_counts": (
            dict(
                sorted(
                    location_type_counts.items()
                )
            )
        ),
        "route_counts": (
            dict(
                sorted(
                    route_counts.items()
                )
            )
        ),
    }

    save_json(
        PROPOSALS_PATH,
        proposals,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT ACQUISITION ROUTE PROPOSALS"
    )
    print(
        "=" * 120
    )

    print(
        f"input_classifications="
        f"{len(classification_payloads)}"
    )

    print(
        f"proposals="
        f"{len(proposals)}"
    )

    print()

    print(
        "ROUTE COUNTS"
    )
    print(
        "-" * 120
    )

    for (
        route,
        count,
    ) in sorted(
        route_counts.items()
    ):
        print(
            f"{route:<25} "
            f"{count}"
        )

    print()

    print(
        "ROUTE PROPOSALS"
    )
    print(
        "-" * 180
    )

    if not proposals:
        print(
            "None"
        )

    for item in proposals:
        print(
            f"{item['access_id']:<12} "
            f"{item['candidate_id']:<12} "
            f"{item['location_type']:<12} "
            f"{item['proposed_route']:<22} "
            f"{item['doi'] or '-'}"
        )

        print(
            f"{'':12}"
            f"OA="
            f"{item['openalex_oa_status'] or '-'} "
            f"license="
            f"{item['openalex_license'] or '-'} "
            f"version="
            f"{item['openalex_version'] or '-'}"
        )

        print(
            f"{'':12}"
            f"url="
            f"{item['source_url'] or '-'}"
        )

        print(
            f"{'':12}"
            f"reason="
            f"{item['reason']}"
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
        PROPOSALS_PATH.relative_to(
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

