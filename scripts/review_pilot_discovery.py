import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)


# ---------------------------------------------------------------------------
# INPUT CONFIGURATION
# ---------------------------------------------------------------------------
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "discovery"
    / "pilot_v0_1"
    / "screened_discovery_candidates.json"
)


# ---------------------------------------------------------------------------
# LOAD JSON
# ---------------------------------------------------------------------------
def load_json(
    path: Path,
) -> list[dict]:
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


# ---------------------------------------------------------------------------
# GET SCREENING STATUS
# ---------------------------------------------------------------------------
def get_screening_status(
    candidate: dict,
) -> str:
    screening = candidate.get(
        "screening",
        {},
    )

    return str(
        screening.get(
            "status",
            ""
        )
    ).lower()


# ---------------------------------------------------------------------------
# GET RECORD
# ---------------------------------------------------------------------------
def get_record(
    candidate: dict,
) -> dict:
    return candidate.get(
        "record",
        {},
    )


# ---------------------------------------------------------------------------
# GET SCREENING
# ---------------------------------------------------------------------------
def get_screening(
    candidate: dict,
) -> dict:
    return candidate.get(
        "screening",
        {},
    )


# ---------------------------------------------------------------------------
# PRINT CANDIDATE
# ---------------------------------------------------------------------------
def print_candidate(
    candidate: dict,
) -> None:
    record = (
        get_record(
            candidate
        )
    )

    screening = (
        get_screening(
            candidate
        )
    )

    candidate_id = (
        candidate.get(
            "candidate_id",
            "-"
        )
    )

    status = (
        screening.get(
            "status",
            "-"
        )
    )

    year = (
        record.get(
            "year"
        )
    )

    doi = (
        record.get(
            "doi"
        )
        or "-"
    )

    title = (
        record.get(
            "title"
        )
        or "-"
    )

    hit_count = (
        candidate.get(
            "hit_count",
            0,
        )
    )

    query_ids = (
        candidate.get(
            "query_ids",
            [],
        )
    )

    sources = (
        candidate.get(
            "sources",
            [],
        )
    )

    psk_formulas = (
        screening.get(
            "matched_perovskite_formulas",
            [],
        )
    )

    oxide_terms = (
        screening.get(
            "matched_oxide_perovskite_terms",
            [],
        )
    )

    halide_terms = (
        screening.get(
            "matched_halide_perovskite_terms",
            [],
        )
    )

    halide_formulas = (
        screening.get(
            "matched_halide_perovskite_formulas",
            [],
        )
    )

    tmd_terms = (
        screening.get(
            "matched_tmd_terms",
            [],
        )
    )

    photo_terms = (
        screening.get(
            "matched_photo_terms",
            [],
        )
    )

    reason = (
        screening.get(
            "reason",
            "-"
        )
    )

    print(
        f"{candidate_id:<12} "
        f"{status.upper():<7} "
        f"{year!s:<6} "
        f"hits={hit_count:<3} "
        f"queries={len(query_ids):<3} "
        f"sources={','.join(sources):<20}"
    )

    print(
        f"{'':12} "
        f"DOI={doi}"
    )

    print(
        f"{'':12} "
        f"title={title}"
    )

    print(
        f"{'':12} "
        f"PSK formulas="
        f"{tuple(psk_formulas)}"
    )

    print(
        f"{'':12} "
        f"oxide terms="
        f"{tuple(oxide_terms)}"
    )

    print(
        f"{'':12} "
        f"halide terms="
        f"{tuple(halide_terms)}"
    )

    print(
        f"{'':12} "
        f"halide formulas="
        f"{tuple(halide_formulas)}"
    )

    print(
        f"{'':12} "
        f"TMD terms="
        f"{tuple(tmd_terms)}"
    )

    print(
        f"{'':12} "
        f"PHOTO terms="
        f"{tuple(photo_terms)}"
    )

    print(
        f"{'':12} "
        f"reason="
        f"{reason}"
    )

    print(
        "-" * 150
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    candidates = (
        load_json(
            INPUT_PATH
        )
    )

    passed_candidates = [
        candidate
        for candidate in candidates
        if (
            get_screening_status(
                candidate
            )
            == "pass"
        )
    ]

    review_candidates = [
        candidate
        for candidate in candidates
        if (
            get_screening_status(
                candidate
            )
            == "review"
        )
    ]

    rejected_candidates = [
        candidate
        for candidate in candidates
        if (
            get_screening_status(
                candidate
            )
            == "reject"
        )
    ]

    actionable_candidates = (
        passed_candidates
        + review_candidates
    )

    print(
        "PILOT DISCOVERY QC REVIEW"
    )
    print(
        "=" * 150
    )

    print(
        f"input_file="
        f"{INPUT_PATH.relative_to(PROJECT_ROOT)}"
    )

    print(
        f"total_candidates="
        f"{len(candidates)}"
    )

    print(
        f"pass="
        f"{len(passed_candidates)}"
    )

    print(
        f"review="
        f"{len(review_candidates)}"
    )

    print(
        f"reject="
        f"{len(rejected_candidates)}"
    )

    print(
        f"actionable="
        f"{len(actionable_candidates)}"
    )

    print()

    print(
        "PASS CANDIDATES"
    )
    print(
        "=" * 150
    )

    if not passed_candidates:
        print(
            "None"
        )

    for candidate in passed_candidates:
        print_candidate(
            candidate
        )

    print()

    print(
        "REVIEW CANDIDATES"
    )
    print(
        "=" * 150
    )

    if not review_candidates:
        print(
            "None"
        )

    for candidate in review_candidates:
        print_candidate(
            candidate
        )

    print()

    print(
        "ACTIONABLE CHEMISTRY SUMMARY"
    )
    print(
        "=" * 150
    )

    formula_counts: dict[
        str,
        int,
    ] = {}

    tmd_counts: dict[
        str,
        int,
    ] = {}

    for candidate in actionable_candidates:
        screening = (
            get_screening(
                candidate
            )
        )

        for formula in screening.get(
            "matched_perovskite_formulas",
            [],
        ):
            formula_counts[
                formula
            ] = (
                formula_counts.get(
                    formula,
                    0,
                )
                + 1
            )

        for tmd in screening.get(
            "matched_tmd_terms",
            [],
        ):
            tmd_counts[
                tmd
            ] = (
                tmd_counts.get(
                    tmd,
                    0,
                )
                + 1
            )

    print(
        "PSK FORMULA COUNTS"
    )
    print(
        "-" * 80
    )

    if not formula_counts:
        print(
            "None"
        )

    for (
        formula,
        count,
    ) in sorted(
        formula_counts.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    ):
        print(
            f"{formula:<25} "
            f"{count}"
        )

    print()

    print(
        "TMD TERM COUNTS"
    )
    print(
        "-" * 80
    )

    if not tmd_counts:
        print(
            "None"
        )

    for (
        tmd,
        count,
    ) in sorted(
        tmd_counts.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    ):
        print(
            f"{tmd:<25} "
            f"{count}"
        )


if __name__ == "__main__":
    main()

