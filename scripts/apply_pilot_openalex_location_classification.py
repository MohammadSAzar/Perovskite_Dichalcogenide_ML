import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.location import (
    AccessLocationType,
    classify_access_location,
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
    / "openalex_access_review_queue.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
)

CLASSIFICATION_PATH = (
    OUTPUT_DIR
    / "openalex_location_classifications.json"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "openalex_location_classification_summary.json"
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
# BUILD CLASSIFICATION RECORD
# ---------------------------------------------------------------------------
def build_classification_record(
    review_item: dict,
) -> dict:
    location_url = (
        review_item.get(
            "openalex_full_text_location"
        )
    )

    classification = (
        classify_access_location(
            location_url
        )
    )

    return {
        "access_id": (
            review_item[
                "access_id"
            ]
        ),
        "candidate_id": (
            review_item[
                "candidate_id"
            ]
        ),
        "doi": (
            review_item.get(
                "doi"
            )
        ),
        "publisher": (
            review_item.get(
                "publisher"
            )
        ),
        "openalex_oa_status": (
            review_item.get(
                "openalex_oa_status"
            )
        ),
        "openalex_license": (
            review_item.get(
                "openalex_license"
            )
        ),
        "openalex_version": (
            review_item.get(
                "openalex_version"
            )
        ),
        "location_type": (
            classification
            .location_type
            .value
        ),
        "location_url": (
            classification.url
        ),
        "hostname": (
            classification.hostname
        ),
        "classification_reason": (
            classification.reason
        ),
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    review_items = (
        load_json(
            INPUT_PATH
        )
    )

    classifications = [
        build_classification_record(
            review_item
        )
        for review_item
        in review_items
    ]

    type_counts = {}

    for classification in classifications:
        location_type = (
            classification[
                "location_type"
            ]
        )

        type_counts[
            location_type
        ] = (
            type_counts.get(
                location_type,
                0,
            )
            + 1
        )

    summary = {
        "input_review_count": (
            len(
                review_items
            )
        ),
        "classification_count": (
            len(
                classifications
            )
        ),
        "location_type_counts": (
            dict(
                sorted(
                    type_counts.items()
                )
            )
        ),
    }

    save_json(
        CLASSIFICATION_PATH,
        classifications,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT OPENALEX LOCATION CLASSIFICATION"
    )
    print(
        "=" * 120
    )

    print(
        f"input_review_records="
        f"{len(review_items)}"
    )

    print(
        f"classifications="
        f"{len(classifications)}"
    )

    print()

    print(
        "LOCATION TYPE COUNTS"
    )
    print(
        "-" * 120
    )

    for (
        location_type,
        count,
    ) in sorted(
        type_counts.items()
    ):
        print(
            f"{location_type:<25} "
            f"{count}"
        )

    print()

    print(
        "CLASSIFICATIONS"
    )
    print(
        "-" * 180
    )

    if not classifications:
        print(
            "None"
        )

    for item in classifications:
        print(
            f"{item['access_id']:<12} "
            f"{item['candidate_id']:<12} "
            f"{item['location_type']:<12} "
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
            f"host="
            f"{item['hostname'] or '-'}"
        )

        print(
            f"{'':12}"
            f"url="
            f"{item['location_url'] or '-'}"
        )

        print(
            f"{'':12}"
            f"reason="
            f"{item['classification_reason']}"
        )

        print(
            "-" * 180
        )

    print()

    print(
        "SANITY CHECK"
    )
    print(
        "-" * 120
    )

    expected_types = {
        AccessLocationType.DOI.value,
        AccessLocationType.PUBLISHER.value,
        AccessLocationType.REPOSITORY.value,
        AccessLocationType.OTHER.value,
        AccessLocationType.UNKNOWN.value,
    }

    unexpected_types = sorted(
        set(
            type_counts
        )
        - expected_types
    )

    if unexpected_types:
        print(
            "Unexpected location types: "
            f"{unexpected_types}"
        )

    else:
        print(
            "All location types are valid."
        )

    print()

    print(
        "SAVED FILES"
    )
    print(
        "-" * 120
    )

    print(
        CLASSIFICATION_PATH.relative_to(
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

