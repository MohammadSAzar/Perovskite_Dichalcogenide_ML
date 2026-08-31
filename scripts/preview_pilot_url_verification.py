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
# INPUT CONFIGURATION
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

SMOKE_TEST_ACCESS_IDS = (
    "ACC-000021",
    "ACC-000024",
    "ACC-000003",
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
# SELECT SMOKE TEST ITEMS
# ---------------------------------------------------------------------------
def select_smoke_test_items(
    payloads: list[
        dict
    ],
) -> list[
    dict
]:
    payloads_by_id = {
        payload[
            "access_id"
        ]: payload
        for payload in payloads
    }

    selected = []

    for access_id in SMOKE_TEST_ACCESS_IDS:
        payload = (
            payloads_by_id.get(
                access_id
            )
        )

        if payload is None:
            raise ValueError(
                "Smoke-test access ID "
                "was not found: "
                f"{access_id}"
            )

        selected.append(
            payload
        )

    return selected


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    payloads = (
        load_json(
            INPUT_PATH
        )
    )

    test_items = (
        select_smoke_test_items(
            payloads
        )
    )

    successful = 0

    failed = 0

    print(
        "PILOT URL VERIFICATION LIVE PREVIEW"
    )
    print(
        "=" * 160
    )

    print(
        f"input_file="
        f"{INPUT_PATH.relative_to(PROJECT_ROOT)}"
    )

    print(
        f"selected_records="
        f"{len(test_items)}"
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

    for item in test_items:
        source_url = (
            item.get(
                "source_url"
            )
        )

        print(
            "-" * 160
        )

        print(
            f"{item['access_id']:<12} "
            f"{item['candidate_id']:<12} "
            f"type="
            f"{item['location_type']:<12} "
            f"route="
            f"{item['proposed_route']:<22}"
        )

        print(
            f"{'':12}"
            f"DOI="
            f"{item.get('doi') or '-'}"
        )

        print(
            f"{'':12}"
            f"requested_url="
            f"{source_url or '-'}"
        )

        if not source_url:
            failed += 1

            print(
                f"{'':12}"
                f"VERIFICATION SKIPPED: "
                f"No source URL."
            )

            continue

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

        if result.success:
            successful += 1

        else:
            failed += 1

        print(
            f"{'':12}"
            f"success="
            f"{result.success}"
        )

        print(
            f"{'':12}"
            f"status_code="
            f"{result.status_code}"
        )

        print(
            f"{'':12}"
            f"final_url="
            f"{result.final_url or '-'}"
        )

        print(
            f"{'':12}"
            f"content_type="
            f"{result.content_type or '-'}"
        )

        print(
            f"{'':12}"
            f"content_length="
            f"{result.content_length}"
        )

        print(
            f"{'':12}"
            f"appears_pdf="
            f"{result.appears_pdf}"
        )

        print(
            f"{'':12}"
            f"appears_html="
            f"{result.appears_html}"
        )

        if not result.success:
            print(
                f"{'':12}"
                f"error_type="
                f"{result.error_type or '-'}"
            )

            print(
                f"{'':12}"
                f"error_message="
                f"{result.error_message or '-'}"
            )

    print(
        "-" * 160
    )

    print()

    print(
        "SMOKE TEST SUMMARY"
    )
    print(
        "-" * 120
    )

    print(
        f"attempted_records="
        f"{len(test_items)}"
    )

    print(
        f"successful_records="
        f"{successful}"
    )

    print(
        f"failed_records="
        f"{failed}"
    )


if __name__ == "__main__":
    main()

