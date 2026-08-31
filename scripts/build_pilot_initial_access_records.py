import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.builders import (
    build_initial_access_records,
)
from psk_tmd.corpus.discovery.candidates import (
    DiscoveryCandidate,
    DiscoverySourceRank,
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
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "discovery"
    / "pilot_v0_1"
    / "screened_discovery_candidates_association_qc.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "initial_access_records.json"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "initial_access_summary.json"
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
# BUILD DISCOVERY RECORD
# ---------------------------------------------------------------------------
def build_discovery_record(
    payload: dict,
) -> DiscoveryRecord:
    return DiscoveryRecord.model_validate(
        payload
    )


# ---------------------------------------------------------------------------
# BUILD SOURCE RANKS
# ---------------------------------------------------------------------------
def build_source_ranks(
    payload: list[
        dict
    ],
) -> tuple[
    DiscoverySourceRank,
    ...
]:
    return tuple(
        DiscoverySourceRank(
            source=(
                item[
                    "source"
                ]
            ),
            best_rank=(
                item[
                    "best_rank"
                ]
            ),
        )
        for item in payload
    )


# ---------------------------------------------------------------------------
# BUILD DISCOVERY CANDIDATE
# ---------------------------------------------------------------------------
def build_discovery_candidate(
    payload: dict,
) -> DiscoveryCandidate:
    return DiscoveryCandidate(
        candidate_id=(
            payload[
                "candidate_id"
            ]
        ),
        group_key=(
            payload[
                "group_key"
            ]
        ),
        record=(
            build_discovery_record(
                payload[
                    "record"
                ]
            )
        ),
        hit_count=(
            payload[
                "hit_count"
            ]
        ),
        query_ids=tuple(
            payload.get(
                "query_ids",
                [],
            )
        ),
        query_texts=tuple(
            payload.get(
                "query_texts",
                [],
            )
        ),
        families=tuple(
            payload.get(
                "families",
                [],
            )
        ),
        sources=tuple(
            payload.get(
                "sources",
                [],
            )
        ),
        source_ranks=(
            build_source_ranks(
                payload.get(
                    "source_ranks",
                    [],
                )
            )
        ),
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
# BUILD ACTIONABLE CANDIDATES
# ---------------------------------------------------------------------------
def build_actionable_candidates(
    payloads: list[
        dict
    ],
):
    actionable = []

    for payload in payloads:
        screening_payload = (
            payload[
                "screening"
            ]
        )

        status = (
            DiscoveryScreeningStatus(
                screening_payload[
                    "status"
                ]
            )
        )

        if (
            status
            == DiscoveryScreeningStatus.REJECT
        ):
            continue

        candidate = (
            build_discovery_candidate(
                payload
            )
        )

        screening = (
            build_screening_result(
                discovery_id=(
                    candidate.record.discovery_id
                ),
                payload=(
                    screening_payload
                ),
            )
        )

        actionable.append(
            (
                candidate,
                screening,
            )
        )

    return actionable


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    candidate_payloads = (
        load_json(
            INPUT_PATH
        )
    )

    actionable_candidates = (
        build_actionable_candidates(
            candidate_payloads
        )
    )

    access_records = (
        build_initial_access_records(
            actionable_candidates
        )
    )

    output_payload = [
        record.model_dump(
            mode="json"
        )
        for record in access_records
    ]

    pass_count = sum(
        1
        for (
            _,
            screening,
        ) in actionable_candidates
        if (
            screening.status
            == DiscoveryScreeningStatus.PASS
        )
    )

    review_count = sum(
        1
        for (
            _,
            screening,
        ) in actionable_candidates
        if (
            screening.status
            == DiscoveryScreeningStatus.REVIEW
        )
    )

    summary = {
        "input_candidate_count": (
            len(
                candidate_payloads
            )
        ),
        "actionable_candidate_count": (
            len(
                actionable_candidates
            )
        ),
        "pass_count": (
            pass_count
        ),
        "review_count": (
            review_count
        ),
        "access_record_count": (
            len(
                access_records
            )
        ),
    }

    save_json(
        OUTPUT_PATH,
        output_payload,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT INITIAL ACCESS RECORD BUILD"
    )
    print(
        "=" * 100
    )

    print(
        f"input_candidates="
        f"{len(candidate_payloads)}"
    )

    print(
        f"actionable_candidates="
        f"{len(actionable_candidates)}"
    )

    print(
        f"pass="
        f"{pass_count}"
    )

    print(
        f"review="
        f"{review_count}"
    )

    print(
        f"access_records="
        f"{len(access_records)}"
    )

    print()

    print(
        "INITIAL ACCESS QUEUE"
    )
    print(
        "-" * 140
    )

    for access_record in access_records:
        print(
            f"{access_record.access_id:<12} "
            f"{access_record.candidate_id:<12} "
            f"OA={str(access_record.is_open_access):<5} "
            f"{access_record.doi or '-':<35} "
            f"{access_record.publisher or '-'}"
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

