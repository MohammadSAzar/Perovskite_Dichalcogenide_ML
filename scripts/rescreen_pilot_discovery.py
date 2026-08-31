import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)
from psk_tmd.corpus.discovery.screening import (
    screen_discovery_record,
)
from psk_tmd.corpus.discovery.selection import (
    select_discovery_candidates,
)


# ---------------------------------------------------------------------------
# INPUT / OUTPUT CONFIGURATION
# ---------------------------------------------------------------------------
PILOT_DIR = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "discovery"
    / "pilot_v0_1"
)

INPUT_PATH = (
    PILOT_DIR
    / "screened_discovery_candidates.json"
)

OUTPUT_PATH = (
    PILOT_DIR
    / "screened_discovery_candidates_rescreened.json"
)

SUMMARY_PATH = (
    PILOT_DIR
    / "rescreen_summary.json"
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
# BUILD DISCOVERY RECORD
# ---------------------------------------------------------------------------
def build_discovery_record(
    payload: dict,
) -> DiscoveryRecord:
    return DiscoveryRecord.model_validate(
        payload
    )


# ---------------------------------------------------------------------------
# SERIALIZE SCREENING RESULT
# ---------------------------------------------------------------------------
def serialize_screening_result(
    screening,
) -> dict:
    return {
        "status": (
            screening.status.value
        ),
        "has_perovskite_signal": (
            screening.has_perovskite_signal
        ),
        "has_oxide_perovskite_signal": (
            screening.has_oxide_perovskite_signal
        ),
        "has_halide_perovskite_signal": (
            screening.has_halide_perovskite_signal
        ),
        "has_tmd_signal": (
            screening.has_tmd_signal
        ),
        "has_photo_signal": (
            screening.has_photo_signal
        ),
        "matched_perovskite_terms": list(
            screening.matched_perovskite_terms
        ),
        "matched_abo3_formulas": list(
            screening.matched_abo3_formulas
        ),
        "matched_known_perovskite_formulas": list(
            screening
            .matched_known_perovskite_formulas
        ),
        "matched_oxide_perovskite_terms": list(
            screening
            .matched_oxide_perovskite_terms
        ),
        "matched_halide_perovskite_terms": list(
            screening
            .matched_halide_perovskite_terms
        ),
        "matched_halide_perovskite_formulas": list(
            screening
            .matched_halide_perovskite_formulas
        ),
        "matched_tmd_terms": list(
            screening.matched_tmd_terms
        ),
        "matched_photo_terms": list(
            screening.matched_photo_terms
        ),
        "reason": (
            screening.reason
        ),
    }


# ---------------------------------------------------------------------------
# BUILD SCREENED ITEM
# ---------------------------------------------------------------------------
def build_screened_item(
    candidate_payload: dict,
):
    record = (
        build_discovery_record(
            candidate_payload[
                "record"
            ]
        )
    )

    screening = (
        screen_discovery_record(
            record
        )
    )

    return (
        candidate_payload,
        screening,
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    candidate_payloads = (
        load_json(
            INPUT_PATH
        )
    )

    screened_items = [
        build_screened_item(
            candidate_payload
        )
        for candidate_payload
        in candidate_payloads
    ]

    rewritten_payloads = []

    selection_input = []

    for (
        candidate_payload,
        screening,
    ) in screened_items:
        updated_payload = dict(
            candidate_payload
        )

        updated_payload[
            "screening"
        ] = (
            serialize_screening_result(
                screening
            )
        )

        rewritten_payloads.append(
            updated_payload
        )

        selection_input.append(
            (
                candidate_payload[
                    "candidate_id"
                ],
                screening,
            )
        )

    accepted = [
        item
        for item in selection_input
        if (
            item[1].status.value
            == "pass"
        )
    ]

    review = [
        item
        for item in selection_input
        if (
            item[1].status.value
            == "review"
        )
    ]

    rejected = [
        item
        for item in selection_input
        if (
            item[1].status.value
            == "reject"
        )
    ]

    old_status_counts = {
        "pass": 0,
        "review": 0,
        "reject": 0,
    }

    transition_counts = {}

    for (
        candidate_payload,
        screening,
    ) in screened_items:
        old_status = (
            candidate_payload
            .get(
                "screening",
                {},
            )
            .get(
                "status",
                "unknown",
            )
        )

        new_status = (
            screening.status.value
        )

        if old_status in old_status_counts:
            old_status_counts[
                old_status
            ] += 1

        transition_key = (
            f"{old_status}"
            f"->{new_status}"
        )

        transition_counts[
            transition_key
        ] = (
            transition_counts.get(
                transition_key,
                0,
            )
            + 1
        )

    summary = {
        "input_candidate_count": (
            len(
                candidate_payloads
            )
        ),
        "old_status_counts": (
            old_status_counts
        ),
        "new_status_counts": {
            "pass": (
                len(
                    accepted
                )
            ),
            "review": (
                len(
                    review
                )
            ),
            "reject": (
                len(
                    rejected
                )
            ),
        },
        "actionable_count": (
            len(
                accepted
            )
            + len(
                review
            )
        ),
        "transition_counts": (
            dict(
                sorted(
                    transition_counts.items()
                )
            )
        ),
    }

    save_json(
        OUTPUT_PATH,
        rewritten_payloads,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT DISCOVERY RESCREEN"
    )
    print(
        "=" * 100
    )

    print(
        f"input_candidates="
        f"{len(candidate_payloads)}"
    )

    print()

    print(
        "OLD COUNTS"
    )
    print(
        "-" * 100
    )

    print(
        f"pass="
        f"{old_status_counts['pass']}"
    )

    print(
        f"review="
        f"{old_status_counts['review']}"
    )

    print(
        f"reject="
        f"{old_status_counts['reject']}"
    )

    print()

    print(
        "NEW COUNTS"
    )
    print(
        "-" * 100
    )

    print(
        f"pass="
        f"{len(accepted)}"
    )

    print(
        f"review="
        f"{len(review)}"
    )

    print(
        f"reject="
        f"{len(rejected)}"
    )

    print(
        f"actionable="
        f"{len(accepted) + len(review)}"
    )

    print()

    print(
        "STATUS TRANSITIONS"
    )
    print(
        "-" * 100
    )

    for (
        transition,
        count,
    ) in sorted(
        transition_counts.items()
    ):
        print(
            f"{transition:<20} "
            f"{count}"
        )

    print()

    print(
        "CHANGED CANDIDATES"
    )
    print(
        "-" * 140
    )

    changed_count = 0

    for (
        candidate_payload,
        screening,
    ) in screened_items:
        old_status = (
            candidate_payload[
                "screening"
            ][
                "status"
            ]
        )

        new_status = (
            screening.status.value
        )

        if (
            old_status
            == new_status
        ):
            continue

        changed_count += 1

        record = (
            candidate_payload[
                "record"
            ]
        )

        print(
            f"{candidate_payload['candidate_id']:<12} "
            f"{old_status.upper():<7} "
            f"-> "
            f"{new_status.upper():<7} "
            f"{record.get('doi') or '-':<35} "
            f"{record.get('title', '')[:65]}"
        )

        print(
            f"{'':12} "
            f"ABO3="
            f"{screening.matched_abo3_formulas}"
        )

        print(
            f"{'':12} "
            f"known="
            f"{screening.matched_known_perovskite_formulas}"
        )

        print(
            f"{'':12} "
            f"reason="
            f"{screening.reason}"
        )

    if changed_count == 0:
        print(
            "None"
        )

    print(
        "-" * 140
    )

    print()

    print(
        "SAVED FILES"
    )
    print(
        "-" * 100
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

