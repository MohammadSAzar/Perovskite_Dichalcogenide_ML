import json

from datetime import (
    datetime,
    timezone,
)
from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.discovery.candidates import (
    DiscoveryCandidate,
    build_discovery_candidates,
)
from psk_tmd.corpus.discovery.execution_plan import (
    build_execution_plan,
    select_pilot_queries,
)
from psk_tmd.corpus.discovery.query_strategy import (
    build_default_discovery_queries,
)
from psk_tmd.corpus.discovery.runner import (
    DiscoveryHit,
    run_discovery_plan,
)
from psk_tmd.corpus.discovery.screening import (
    DiscoveryScreeningResult,
    screen_discovery_record,
)
from psk_tmd.corpus.discovery.selection import (
    select_discovery_candidates,
)


# ---------------------------------------------------------------------------
# OUTPUT CONFIGURATION
# ---------------------------------------------------------------------------
OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "discovery"
    / "pilot_v0_1"
)

RAW_HITS_PATH = (
    OUTPUT_DIR
    / "raw_discovery_hits.json"
)

SCREENED_CANDIDATES_PATH = (
    OUTPUT_DIR
    / "screened_discovery_candidates.json"
)

RUN_SUMMARY_PATH = (
    OUTPUT_DIR
    / "run_summary.json"
)

RESULT_LIMIT = 10

DELAY_SECONDS = 1.0


# ---------------------------------------------------------------------------
# SERIALIZE DISCOVERY HIT
# ---------------------------------------------------------------------------
def serialize_discovery_hit(
    hit: DiscoveryHit,
) -> dict:
    return {
        "query_id": hit.query_id,
        "query_text": hit.query_text,
        "family": hit.family,
        "source": hit.source,
        "source_rank": hit.source_rank,
        "record": (
            hit.record.model_dump(
                mode="json"
            )
        ),
    }


# ---------------------------------------------------------------------------
# SERIALIZE SCREENING RESULT
# ---------------------------------------------------------------------------
def serialize_screening_result(
    screening: DiscoveryScreeningResult,
) -> dict:
    return {
        "status": (
            screening.status.value
        ),
        "has_perovskite_signal": (
            screening
            .has_perovskite_signal
        ),
        "has_oxide_perovskite_signal": (
            screening
            .has_oxide_perovskite_signal
        ),
        "has_halide_perovskite_signal": (
            screening
            .has_halide_perovskite_signal
        ),
        "has_tmd_signal": (
            screening
            .has_tmd_signal
        ),
        "has_photo_signal": (
            screening
            .has_photo_signal
        ),
        "matched_perovskite_terms": list(
            screening
            .matched_perovskite_terms
        ),
        "matched_perovskite_formulas": list(
            screening
            .matched_perovskite_formulas
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
            screening
            .matched_tmd_terms
        ),
        "matched_photo_terms": list(
            screening
            .matched_photo_terms
        ),
        "reason": (
            screening.reason
        ),
    }


# ---------------------------------------------------------------------------
# SERIALIZE DISCOVERY CANDIDATE
# ---------------------------------------------------------------------------
def serialize_discovery_candidate(
    candidate: DiscoveryCandidate,
    screening: DiscoveryScreeningResult,
) -> dict:
    return {
        "candidate_id": (
            candidate.candidate_id
        ),
        "group_key": (
            candidate.group_key
        ),
        "hit_count": (
            candidate.hit_count
        ),
        "query_ids": list(
            candidate.query_ids
        ),
        "query_texts": list(
            candidate.query_texts
        ),
        "families": list(
            candidate.families
        ),
        "sources": list(
            candidate.sources
        ),
        "source_ranks": [
            {
                "source": (
                    source_rank.source
                ),
                "best_rank": (
                    source_rank.best_rank
                ),
            }
            for source_rank
            in candidate.source_ranks
        ],
        "record": (
            candidate.record.model_dump(
                mode="json"
            )
        ),
        "screening": (
            serialize_screening_result(
                screening
            )
        ),
    }


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
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    all_queries = (
        build_default_discovery_queries()
    )

    pilot_queries = (
        select_pilot_queries(
            all_queries
        )
    )

    plan = (
        build_execution_plan(
            pilot_queries
        )
    )

    planned_source_calls = sum(
        len(
            item.sources
        )
        for item in plan
    )

    print(
        "PILOT CORPUS DISCOVERY"
    )
    print(
        "=" * 120
    )

    print(
        f"available_queries="
        f"{len(all_queries)}"
    )

    print(
        f"selected_queries="
        f"{len(plan)}"
    )

    print(
        f"planned_source_calls="
        f"{planned_source_calls}"
    )

    print(
        f"result_limit="
        f"{RESULT_LIMIT}"
    )

    print(
        f"delay_seconds="
        f"{DELAY_SECONDS}"
    )

    print()

    print(
        "Running discovery..."
    )

    result = (
        run_discovery_plan(
            plan,
            result_limit=(
                RESULT_LIMIT
            ),
            delay_seconds=(
                DELAY_SECONDS
            ),
        )
    )

    candidates = (
        build_discovery_candidates(
            result.hits
        )
    )

    screened_candidates = [
        (
            candidate,
            screen_discovery_record(
                candidate.record
            ),
        )
        for candidate in candidates
    ]

    selection = (
        select_discovery_candidates(
            screened_candidates
        )
    )

    raw_hits_payload = [
        serialize_discovery_hit(
            hit
        )
        for hit in result.hits
    ]

    candidates_payload = [
        serialize_discovery_candidate(
            candidate,
            screening,
        )
        for (
            candidate,
            screening,
        ) in screened_candidates
    ]

    generated_at = (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )

    run_summary = {
        "generated_at_utc": (
            generated_at
        ),
        "available_query_count": (
            len(
                all_queries
            )
        ),
        "selected_query_count": (
            len(
                plan
            )
        ),
        "planned_source_calls": (
            planned_source_calls
        ),
        "result_limit": (
            RESULT_LIMIT
        ),
        "delay_seconds": (
            DELAY_SECONDS
        ),
        "attempted_calls": (
            result.attempted_calls
        ),
        "successful_calls": (
            result.successful_calls
        ),
        "failed_calls": (
            result.failed_calls
        ),
        "raw_hit_count": (
            len(
                result.hits
            )
        ),
        "unique_candidate_count": (
            len(
                candidates
            )
        ),
        "screen_pass_count": (
            len(
                selection.accepted
            )
        ),
        "screen_review_count": (
            len(
                selection.review
            )
        ),
        "screen_reject_count": (
            len(
                selection.rejected
            )
        ),
        "actionable_candidate_count": (
            len(
                selection.actionable
            )
        ),
    }

    save_json(
        RAW_HITS_PATH,
        raw_hits_payload,
    )

    save_json(
        SCREENED_CANDIDATES_PATH,
        candidates_payload,
    )

    save_json(
        RUN_SUMMARY_PATH,
        run_summary,
    )

    print()

    print(
        "RUN SUMMARY"
    )
    print(
        "-" * 120
    )

    print(
        f"attempted_calls="
        f"{result.attempted_calls}"
    )

    print(
        f"successful_calls="
        f"{result.successful_calls}"
    )

    print(
        f"failed_calls="
        f"{result.failed_calls}"
    )

    print(
        f"raw_hits="
        f"{len(result.hits)}"
    )

    print(
        f"unique_candidates="
        f"{len(candidates)}"
    )

    print(
        f"screen_pass="
        f"{len(selection.accepted)}"
    )

    print(
        f"screen_review="
        f"{len(selection.review)}"
    )

    print(
        f"screen_reject="
        f"{len(selection.rejected)}"
    )

    print(
        f"actionable="
        f"{len(selection.actionable)}"
    )

    print()

    print(
        "ACTIONABLE CANDIDATES"
    )
    print(
        "-" * 150
    )

    if not selection.actionable:
        print(
            "None"
        )

    for (
        candidate,
        screening,
    ) in selection.actionable:
        record = (
            candidate.record
        )

        print(
            f"{candidate.candidate_id:<12} "
            f"{screening.status.value.upper():<7} "
            f"hits={candidate.hit_count:<3} "
            f"queries={len(candidate.query_ids):<3} "
            f"{record.year!s:<6} "
            f"{record.doi or '-':<35} "
            f"{record.title[:65]}"
        )

    print(
        "-" * 150
    )

    print()

    print(
        "SAVED FILES"
    )
    print(
        "-" * 120
    )

    print(
        RAW_HITS_PATH.relative_to(
            PROJECT_ROOT
        )
    )

    print(
        SCREENED_CANDIDATES_PATH.relative_to(
            PROJECT_ROOT
        )
    )

    print(
        RUN_SUMMARY_PATH.relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()

