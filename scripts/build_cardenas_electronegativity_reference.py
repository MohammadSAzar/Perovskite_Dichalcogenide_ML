import json

from pathlib import Path

from psk_tmd.corpus.cardenas_reference import (
    CARDENAS_METHOD,
    CARDENAS_SOURCE_NAME,
    CARDENAS_SOURCE_REFERENCE,
    build_cardenas_reference,
)


# ---------------------------------------------------------------------------
# BUILD OUTPUT PAYLOAD
# ---------------------------------------------------------------------------
def build_output_payload() -> dict:
    records = (
        build_cardenas_reference()
    )

    return {
        "source_name": (
            CARDENAS_SOURCE_NAME
        ),
        "source_reference": (
            CARDENAS_SOURCE_REFERENCE
        ),
        "method": (
            CARDENAS_METHOD
        ),
        "canonical_for_band_calculation": (
            True
        ),
        "records": [
            record.model_dump(
                mode="json"
            )
            for record in records
        ],
    }


# ---------------------------------------------------------------------------
# WRITE OUTPUT
# ---------------------------------------------------------------------------
def write_output(
    output_path: Path,
    payload: dict,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )

        file.write(
            "\n"
        )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    output_path = Path(
        "data/external/"
        "electronegativity/"
        "cardenas2016_absolute_"
        "electronegativity.json"
    )

    payload = (
        build_output_payload()
    )

    write_output(
        output_path=output_path,
        payload=payload,
    )

    records = payload[
        "records"
    ]

    print(
        "CARDENAS 2016 "
        "ELECTRONEGATIVITY REFERENCE"
    )
    print(
        "-" * 70
    )
    print(
        f"Elements: {len(records)}"
    )
    print(
        "Canonical for standardized "
        "band calculations: yes"
    )
    print(
        f"Output: {output_path}"
    )


if __name__ == "__main__":
    main()

