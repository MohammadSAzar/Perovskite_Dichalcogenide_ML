import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.url_verification import (
    verify_url,
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
    / "acquisition_route_proposals.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
)

RESULTS_PATH = (
    OUTPUT_DIR
    / "url_verification_results.json"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "url_verification_summary.json"
)

TIMEOUT_SECONDS = 30.0

PREFIX_BYTES = 8192


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
# BUILD RESULT RECORD
# ---------------------------------------------------------------------------
def build_result_record(
    item: dict,
) -> dict:
    source_url = (
        item.get(
            "source_url"
        )
    )

    if not source_url:
        return {
            "access_id": (
                item[
                    "access_id"
                ]
            ),
            "candidate_id": (
                item[
                    "candidate_id"
                ]
            ),
            "doi": (
                item.get(
                    "doi"
                )
            ),
            "publisher": (
                item.get(
                    "publisher"
                )
            ),
            "location_type": (
                item.get(
                    "location_type"
                )
            ),
            "proposed_route": (
                item.get(
                    "proposed_route"
                )
            ),
            "requested_url": None,
            "success": False,
            "status_code": None,
            "final_url": None,
            "content_type": None,
            "content_length": None,
            "appears_pdf": False,
            "appears_html": False,
            "error_type": (
                "MissingURL"
            ),
            "error_message": (
                "No source URL was available."
            ),
        }

    result = (
        verify_url(
            source_url,
            timeout=(
                TIMEOUT_SECONDS
            ),
            prefix_bytes=(
                PREFIX_BYTES
            ),
        )
    )

    return {
        "access_id": (
            item[
                "access_id"
            ]
        ),
        "candidate_id": (
            item[
                "candidate_id"
            ]
        ),
        "doi": (
            item.get(
                "doi"
            )
        ),
        "publisher": (
            item.get(
                "publisher"
            )
        ),
        "location_type": (
            item.get(
                "location_type"
            )
        ),
        "proposed_route": (
            item.get(
                "proposed_route"
            )
        ),
        "requested_url": (
            result.requested_url
        ),
        "success": (
            result.success
        ),
        "status_code": (
            result.status_code
        ),
        "final_url": (
            result.final_url
        ),
        "content_type": (
            result.content_type
        ),
        "content_length": (
            result.content_length
        ),
        "appears_pdf": (
            result.appears_pdf
        ),
        "appears_html": (
            result.appears_html
        ),
        "error_type": (
            result.error_type
        ),
        "error_message": (
            result.error_message
        ),
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    items = (
        load_json(
            INPUT_PATH
        )
    )

    results = []

    print(
        "PILOT URL VERIFICATION"
    )
    print(
        "=" * 120
    )

    print(
        f"input_records="
        f"{len(items)}"
    )

    print(
        f"timeout_seconds="
        f"{TIMEOUT_SECONDS}"
    )

    print(
        f"prefix_bytes="
        f"{PREFIX_BYTES}"
    )

    print()

    for item in items:
        print(
            f"Verifying "
            f"{item['access_id']} "
            f"{item.get('doi') or '-'}"
        )

        result_record = (
            build_result_record(
                item
            )
        )

        results.append(
            result_record
        )

    successful_count = sum(
        1
        for result in results
        if (
            result[
                "success"
            ]
        )
    )

    failed_count = (
        len(
            results
        )
        - successful_count
    )

    pdf_count = sum(
        1
        for result in results
        if (
            result[
                "appears_pdf"
            ]
        )
    )

    html_count = sum(
        1
        for result in results
        if (
            result[
                "appears_html"
            ]
        )
    )

    other_content_count = sum(
        1
        for result in results
        if (
            result[
                "success"
            ]
            and not result[
                "appears_pdf"
            ]
            and not result[
                "appears_html"
            ]
        )
    )

    redirected_count = sum(
        1
        for result in results
        if (
            result[
                "success"
            ]
            and result[
                "requested_url"
            ]
            and result[
                "final_url"
            ]
            and (
                result[
                    "requested_url"
                ]
                != result[
                    "final_url"
                ]
            )
        )
    )

    summary = {
        "input_record_count": (
            len(
                items
            )
        ),
        "successful_count": (
            successful_count
        ),
        "failed_count": (
            failed_count
        ),
        "pdf_count": (
            pdf_count
        ),
        "html_count": (
            html_count
        ),
        "other_content_count": (
            other_content_count
        ),
        "redirected_count": (
            redirected_count
        ),
    }

    save_json(
        RESULTS_PATH,
        results,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print()

    print(
        "RUN SUMMARY"
    )
    print(
        "-" * 120
    )

    print(
        f"input_records="
        f"{len(items)}"
    )

    print(
        f"successful="
        f"{successful_count}"
    )

    print(
        f"failed="
        f"{failed_count}"
    )

    print(
        f"pdf="
        f"{pdf_count}"
    )

    print(
        f"html="
        f"{html_count}"
    )

    print(
        f"other_content="
        f"{other_content_count}"
    )

    print(
        f"redirected="
        f"{redirected_count}"
    )

    print()

    print(
        "VERIFICATION RESULTS"
    )
    print(
        "-" * 180
    )

    for result in results:
        print(
            f"{result['access_id']:<12} "
            f"{str(result['success']):<6} "
            f"status="
            f"{str(result['status_code']):<5} "
            f"pdf="
            f"{str(result['appears_pdf']):<5} "
            f"html="
            f"{str(result['appears_html']):<5} "
            f"{result['doi'] or '-'}"
        )

        print(
            f"{'':12}"
            f"type="
            f"{result['location_type'] or '-'} "
            f"route="
            f"{result['proposed_route'] or '-'}"
        )

        print(
            f"{'':12}"
            f"content_type="
            f"{result['content_type'] or '-'} "
            f"length="
            f"{result['content_length']}"
        )

        print(
            f"{'':12}"
            f"requested="
            f"{result['requested_url'] or '-'}"
        )

        print(
            f"{'':12}"
            f"final="
            f"{result['final_url'] or '-'}"
        )

        if not result[
            "success"
        ]:
            print(
                f"{'':12}"
                f"error="
                f"{result['error_type'] or '-'}: "
                f"{result['error_message'] or '-'}"
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
        RESULTS_PATH.relative_to(
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

