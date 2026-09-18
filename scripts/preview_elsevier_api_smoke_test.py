import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.elsevier_api import (
    build_elsevier_article_api_request,
)
from psk_tmd.corpus.access.elsevier_api_client import (
    fetch_elsevier_article,
)


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
    / "elsevier_api_requests.json"
)

SMOKE_ACCESS_ID = (
    "ACC-000003"
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
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    records = (
        load_json(
            INPUT_PATH
        )
    )

    selected = next(
        (
            record
            for record
            in records
            if (
                record[
                    "access_id"
                ]
                == SMOKE_ACCESS_ID
            )
        ),
        None,
    )

    if selected is None:
        raise ValueError(
            "Smoke-test access record "
            "was not found."
        )

    request_spec = (
        build_elsevier_article_api_request(
            selected[
                "doi"
            ]
        )
    )

    result = (
        fetch_elsevier_article(
            request_spec
        )
    )

    print(
        "ELSEVIER API SMOKE TEST"
    )

    print(
        "=" * 120
    )

    print(
        f"access_id="
        f"{selected['access_id']}"
    )

    print(
        f"doi="
        f"{selected['doi']}"
    )

    print(
        f"success="
        f"{result.success}"
    )

    print(
        f"status_code="
        f"{result.status_code}"
    )

    print(
        f"content_type="
        f"{result.content_type}"
    )

    print(
        f"content_length="
        f"{result.content_length}"
    )

    print(
        f"appears_xml="
        f"{result.appears_xml}"
    )

    print(
        f"appears_full_text="
        f"{result.appears_full_text}"
    )

    print(
        f"entitlement_outcome="
        f"{result.entitlement_outcome}"
    )

    if result.error_type:
        print(
            f"error_type="
            f"{result.error_type}"
        )

    if result.error_message:
        print(
            f"error_message="
            f"{result.error_message}"
        )

    print()

    print(
        "API key was not printed "
        "or persisted."
    )


if __name__ == "__main__":
    main()


