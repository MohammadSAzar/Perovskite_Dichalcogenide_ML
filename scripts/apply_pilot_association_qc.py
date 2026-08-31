import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.discovery.association import (
    detect_title_association,
    resolve_association_status,
)
from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)
from psk_tmd.corpus.discovery.screening import (
    DiscoveryScreeningResult,
    DiscoveryScreeningStatus,
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
    / "screened_discovery_candidates_rescreened.json"
)

OUTPUT_PATH = (
    PILOT_DIR
    / "screened_discovery_candidates_association_qc.json"
)

SUMMARY_PATH = (
    PILOT_DIR
    / "association_qc_summary.json"
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
# BUILD SCREENING RESULT
# ---------------------------------------------------------------------------
def build_screening_result(
    *,
    discovery_id: str,
    payload: dict,
) -> DiscoveryScreeningResult:
    return DiscoveryScreeningResult(
        discovery_id=(
            discovery_id
        ),
        status=(
            DiscoveryScreeningStatus(
                payload[
                    "status"
                ]
            )
        ),
        has_perovskite_signal=(
            payload[
                "has_perovskite_signal"
            ]
        ),
        has_oxide_perovskite_signal=(
            payload[
                "has_oxide_perovskite_signal"
            ]
        ),
        has_halide_perovskite_signal=(
            payload[
                "has_halide_perovskite_signal"
            ]
        ),
        has_tmd_signal=(
            payload[
                "has_tmd_signal"
            ]
        ),
        has_photo_signal=(
            payload[
                "has_photo_signal"
            ]
        ),
        matched_perovskite_terms=tuple(
            payload.get(
                "matched_perovskite_terms",
                [],
            )
        ),
        matched_abo3_formulas=tuple(
            payload.get(
                "matched_abo3_formulas",
                [],
            )
        ),
        matched_known_perovskite_formulas=tuple(
            payload.get(
                "matched_known_perovskite_formulas",
                [],
            )
        ),
        matched_oxide_perovskite_terms=tuple(
            payload.get(
                "matched_oxide_perovskite_terms",
                [],
            )
        ),
        matched_halide_perovskite_terms=tuple(
            payload.get(
                "matched_halide_perovskite_terms",
                [],
            )
        ),
        matched_halide_perovskite_formulas=tuple(
            payload.get(
                "matched_halide_perovskite_formulas",
                [],
            )
        ),
        matched_tmd_terms=tuple(
            payload.get(
                "matched_tmd_terms",
                [],
            )
        ),
        matched_photo_terms=tuple(
            payload.get(
                "matched_photo_terms",
                [],
            )
        ),
        reason=(
            payload.get(
                "reason",
                "",
            )
        ),
    )


# ---------------------------------------------------------------------------
# SERIALIZE ASSOCIATION
# ---------------------------------------------------------------------------
def serialize_association(
    association,
) -> dict:
    return {
        "has_title_perovskite_signal": (
            association
            .has_title_perovskite_signal
        ),
        "has_title_known_perovskite_formula": (
            association
            .has_title_known_perovskite_formula
        ),
        "has_title_tmd_signal": (
            association
            .has_title_tmd_signal
        ),
        "has_title_pair_signal": (
            association
            .has_title_pair_signal
        ),
        "matched_title_perovskite_terms": list(
            association
            .matched_title_perovskite_terms
        ),
        "matched_title_abo3_formulas": list(
            association
            .matched_title_abo3_formulas
        ),
        "matched_title_known_perovskite_formulas": list(
            association
            .matched_title_known_perovskite_formulas
        ),
        "matched_title_tmd_terms": list(
            association
            .matched_title_tmd_terms
        ),
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    candidate_payloads = (
        load_json(
            INPUT_PATH
        )
    )

    updated_payloads = []

    old_counts = {
        "pass": 0,
        "review": 0,
        "reject": 0,
    }

    new_counts = {
        "pass": 0,
        "review": 0,
        "reject": 0,
    }

    transition_counts = {}

    changed_candidates = []

    for candidate_payload in candidate_payloads:
        record = (
            build_discovery_record(
                candidate_payload[
                    "record"
                ]
            )
        )

        screening = (
            build_screening_result(
                discovery_id=(
                    record.discovery_id
                ),
                payload=(
                    candidate_payload[
                        "screening"
                    ]
                ),
            )
        )

        association = (
            detect_title_association(
                record
            )
        )

        new_status, association_reason = (
            resolve_association_status(
                screening,
                association,
            )
        )

        old_status = (
            screening.status.value
        )

        new_status_value = (
            new_status.value
        )

        old_counts[
            old_status
        ] += 1

        new_counts[
            new_status_value
        ] += 1

        transition_key = (
            f"{old_status}"
            f"->{new_status_value}"
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

        updated_payload = dict(
            candidate_payload
        )

        updated_screening = dict(
            candidate_payload[
                "screening"
            ]
        )

        updated_screening[
            "status"
        ] = (
            new_status_value
        )

        updated_screening[
            "reason"
        ] = (
            association_reason
        )

        updated_payload[
            "screening"
        ] = (
            updated_screening
        )

        updated_payload[
            "association"
        ] = (
            serialize_association(
                association
            )
        )

        updated_payloads.append(
            updated_payload
        )

        if (
            old_status
            != new_status_value
        ):
            changed_candidates.append(
                (
                    candidate_payload,
                    association,
                    new_status_value,
                    association_reason,
                )
            )

    summary = {
        "input_candidate_count": (
            len(
                candidate_payloads
            )
        ),
        "old_status_counts": (
            old_counts
        ),
        "new_status_counts": (
            new_counts
        ),
        "actionable_count": (
            new_counts[
                "pass"
            ]
            + new_counts[
                "review"
            ]
        ),
        "transition_counts": (
            dict(
                sorted(
                    transition_counts.items()
                )
            )
        ),
        "changed_candidate_count": (
            len(
                changed_candidates
            )
        ),
    }

    save_json(
        OUTPUT_PATH,
        updated_payloads,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT DISCOVERY ASSOCIATION QC"
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
        f"{old_counts['pass']}"
    )

    print(
        f"review="
        f"{old_counts['review']}"
    )

    print(
        f"reject="
        f"{old_counts['reject']}"
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
        f"{new_counts['pass']}"
    )

    print(
        f"review="
        f"{new_counts['review']}"
    )

    print(
        f"reject="
        f"{new_counts['reject']}"
    )

    print(
        f"actionable="
        f"{new_counts['pass'] + new_counts['review']}"
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
        "-" * 150
    )

    if not changed_candidates:
        print(
            "None"
        )

    for (
        candidate_payload,
        association,
        new_status,
        association_reason,
    ) in changed_candidates:
        record_payload = (
            candidate_payload[
                "record"
            ]
        )

        old_status = (
            candidate_payload[
                "screening"
            ][
                "status"
            ]
        )

        print(
            f"{candidate_payload['candidate_id']:<12} "
            f"{old_status.upper():<7} "
            f"-> "
            f"{new_status.upper():<7} "
            f"{record_payload.get('doi') or '-':<35}"
        )

        print(
            f"{'':12} "
            f"title="
            f"{record_payload.get('title', '')}"
        )

        print(
            f"{'':12} "
            f"title PSK="
            f"{association.matched_title_known_perovskite_formulas}"
        )

        print(
            f"{'':12} "
            f"title TMD="
            f"{association.matched_title_tmd_terms}"
        )

        print(
            f"{'':12} "
            f"title pair="
            f"{association.has_title_pair_signal}"
        )

        print(
            f"{'':12} "
            f"reason="
            f"{association_reason}"
        )

        print(
            "-" * 150
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

