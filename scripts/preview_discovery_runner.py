from collections import (
    Counter,
)

from psk_tmd.corpus.discovery.candidates import (
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
    run_discovery_plan,
)
from psk_tmd.corpus.discovery.screening import (
    screen_discovery_record,
)
from psk_tmd.corpus.discovery.selection import (
    select_discovery_candidates,
)


# ---------------------------------------------------------------------------
# FORMAT OA STATUS
# ---------------------------------------------------------------------------
def format_oa_status(
    value: bool | None,
) -> str:
    if value is True:
        return "OA"

    if value is False:
        return "CLOSED"

    return "UNKNOWN"


# ---------------------------------------------------------------------------
# PRINT SCREENED CANDIDATE DETAILS
# ---------------------------------------------------------------------------
def print_screened_candidate_details(
    candidate,
    screening,
) -> None:
    record = candidate.record

    print(
        f"{candidate.candidate_id:<12} "
        f"{screening.status.value.upper():<7} "
        f"hits={candidate.hit_count:<2} "
        f"queries={len(candidate.query_ids):<2} "
        f"sources={','.join(candidate.sources):<20} "
        f"{record.doi or '-':<35} "
        f"{record.title[:65]}"
    )

    print(
        f"{'':12} "
        f"PSK terms="
        f"{screening.matched_perovskite_terms}"
    )

    print(
        f"{'':12} "
        f"PSK formulas="
        f"{screening.matched_perovskite_formulas}"
    )

    print(
        f"{'':12} "
        f"oxide terms="
        f"{screening.matched_oxide_perovskite_terms}"
    )

    print(
        f"{'':12} "
        f"halide terms="
        f"{screening.matched_halide_perovskite_terms}"
    )

    print(
        f"{'':12} "
        f"halide formulas="
        f"{screening.matched_halide_perovskite_formulas}"
    )

    print(
        f"{'':12} "
        f"TMD terms="
        f"{screening.matched_tmd_terms}"
    )

    print(
        f"{'':12} "
        f"PHOTO terms="
        f"{screening.matched_photo_terms}"
    )

    print(
        f"{'':12} "
        f"reason="
        f"{screening.reason}"
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

    full_plan = (
        build_execution_plan(
            pilot_queries
        )
    )

    test_plan = full_plan[
        :3
    ]

    result = (
        run_discovery_plan(
            test_plan,
            result_limit=5,
            delay_seconds=1.0,
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

    passed_candidates = (
        selection.accepted
    )

    review_candidates = (
        selection.review
    )

    rejected_candidates = (
        selection.rejected
    )

    actionable_candidates = (
        selection.actionable
    )

    source_counts = Counter(
        hit.source
        for hit in result.hits
    )

    query_counts = Counter(
        hit.query_id
        for hit in result.hits
    )

    print(
        "DISCOVERY RUNNER LIVE PREVIEW"
    )
    print(
        "=" * 150
    )

    print(
        f"selected_queries="
        f"{len(test_plan)}"
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

    print()

    print(
        "METADATA SCREENING"
    )
    print(
        "-" * 150
    )

    for (
        candidate,
        screening,
    ) in screened_candidates:
        record = candidate.record

        signal_text = (
            f"PSK="
            f"{int(screening.has_perovskite_signal)} "
            f"OXIDE="
            f"{int(screening.has_oxide_perovskite_signal)} "
            f"HALIDE="
            f"{int(screening.has_halide_perovskite_signal)} "
            f"TMD="
            f"{int(screening.has_tmd_signal)} "
            f"PHOTO="
            f"{int(screening.has_photo_signal)}"
        )

        print(
            f"{candidate.candidate_id:<12} "
            f"{screening.status.value.upper():<7} "
            f"{signal_text:<38} "
            f"hits={candidate.hit_count:<2} "
            f"{record.doi or '-':<35} "
            f"{record.title[:50]}"
        )

        print(
            f"{'':12} "
            f"reason="
            f"{screening.reason}"
        )

    print(
        "-" * 150
    )

    print(
        f"screened_candidates="
        f"{len(screened_candidates)}"
    )

    print(
        f"screen_passed="
        f"{len(passed_candidates)}"
    )

    print(
        f"screen_review="
        f"{len(review_candidates)}"
    )

    print(
        f"screen_rejected="
        f"{len(rejected_candidates)}"
    )

    print(
        f"screen_actionable="
        f"{len(actionable_candidates)}"
    )

    print()

    print(
        "PASSED CANDIDATES"
    )
    print(
        "-" * 150
    )

    if not passed_candidates:
        print(
            "None"
        )

    for (
        candidate,
        screening,
    ) in passed_candidates:
        print_screened_candidate_details(
            candidate,
            screening,
        )

    print(
        "-" * 150
    )

    print()

    print(
        "REVIEW CANDIDATES"
    )
    print(
        "-" * 150
    )

    if not review_candidates:
        print(
            "None"
        )

    for (
        candidate,
        screening,
    ) in review_candidates:
        print_screened_candidate_details(
            candidate,
            screening,
        )

    print(
        "-" * 150
    )

    print()

    print(
        "ACTIONABLE CANDIDATES"
    )
    print(
        "-" * 150
    )

    if not actionable_candidates:
        print(
            "None"
        )

    for (
        candidate,
        screening,
    ) in actionable_candidates:
        record = candidate.record

        print(
            f"{candidate.candidate_id:<12} "
            f"{screening.status.value.upper():<7} "
            f"hits={candidate.hit_count:<2} "
            f"queries={len(candidate.query_ids):<2} "
            f"sources={','.join(candidate.sources):<20} "
            f"{record.doi or '-':<35} "
            f"{record.title[:65]}"
        )

    print(
        "-" * 150
    )

    print()

    print(
        "UNIQUE DISCOVERY CANDIDATES"
    )
    print(
        "-" * 150
    )

    for candidate in candidates:
        record = candidate.record

        print(
            f"{candidate.candidate_id:<12} "
            f"hits={candidate.hit_count:<2} "
            f"queries={len(candidate.query_ids):<2} "
            f"sources={','.join(candidate.sources):<20} "
            f"{record.doi or '-':<35} "
            f"{record.title[:60]}"
        )

    print(
        "-" * 150
    )

    print()

    print(
        "SOURCE COUNTS"
    )
    print(
        "-" * 150
    )

    for (
        source,
        count,
    ) in sorted(
        source_counts.items()
    ):
        print(
            f"{source:<15} "
            f"{count}"
        )

    print()

    print(
        "QUERY COUNTS"
    )
    print(
        "-" * 150
    )

    for item in test_plan:
        print(
            f"{item.query_id:<12} "
            f"{query_counts.get(item.query_id, 0):>3} "
            f"{item.query_text}"
        )

    print()

    print(
        "RAW DISCOVERY HITS"
    )
    print(
        "-" * 150
    )

    for hit in result.hits:
        record = hit.record

        oa_text = (
            format_oa_status(
                record.is_open_access
            )
        )

        print(
            f"{hit.query_id:<12} "
            f"{hit.source:<10} "
            f"rank={hit.source_rank:<2} "
            f"{record.year!s:<6} "
            f"{oa_text:<8} "
            f"{record.doi or '-':<35} "
            f"{record.title[:55]}"
        )

    print(
        "-" * 150
    )


if __name__ == "__main__":
    main()

