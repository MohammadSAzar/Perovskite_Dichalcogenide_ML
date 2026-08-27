import json

from datetime import date
from pathlib import Path
from urllib.request import urlopen

from psk_tmd.corpus.electronegativity import (
    build_electronegativity_reference_payload, parse_pubchem_periodic_table,
)


# ---------------------------------------------------------------------------
# PUBCHEM SOURCE
# ---------------------------------------------------------------------------
PUBCHEM_PERIODIC_TABLE_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/"
    "rest/pug/periodictable/JSON"
)


# ---------------------------------------------------------------------------
# FETCH PUBCHEM PAYLOAD
# ---------------------------------------------------------------------------
def fetch_pubchem_payload() -> dict:
    with urlopen(
        PUBCHEM_PERIODIC_TABLE_URL,
        timeout=30,
    ) as response:
        payload = json.load(
            response
        )

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(
            "PubChem response must be "
            "a JSON object."
        )

    return payload


# ---------------------------------------------------------------------------
# BUILD OUTPUT PAYLOAD
# ---------------------------------------------------------------------------
def build_output_payload(
    payload: dict,
) -> dict:
    retrieval_date = (
        date.today()
    )

    records = (
        parse_pubchem_periodic_table(
            payload,
            source_reference=(
                PUBCHEM_PERIODIC_TABLE_URL
            ),
        )
    )

    return {
        "source_name": (
            "PubChem Periodic Table"
        ),
        "source_url": (
            PUBCHEM_PERIODIC_TABLE_URL
        ),
        "retrieval_date": (
            retrieval_date.isoformat()
        ),
        "method": (
            "absolute electronegativity "
            "derived as (IE + EA) / 2"
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
    output_payload: dict,
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
            output_payload,
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
        "pubchem_absolute_"
        "electronegativity.json"
    )

    payload = fetch_pubchem_payload()

    output_payload = (
        build_electronegativity_reference_payload(
            payload,
            source_url=(
                PUBCHEM_PERIODIC_TABLE_URL
            ),
            retrieval_date=(
                date.today().isoformat()
            ),
        )
    )

    write_output(
        output_path=output_path,
        output_payload=(
            output_payload
        ),
    )

    records = (
        output_payload[
            "records"
        ]
    )

    available_count = sum(
        1
        for record in records
        if (
            record[
                "absolute_electronegativity_ev"
            ]
            is not None
        )
    )

    unavailable_count = (
        len(records)
        - available_count
    )

    print(
        "PUBCHEM ELECTRONEGATIVITY "
        "REFERENCE"
    )
    print(
        "-" * 70
    )
    print(
        f"Elements: {len(records)}"
    )
    print(
        "Absolute electronegativity "
        f"available: {available_count}"
    )
    print(
        "Absolute electronegativity "
        f"unavailable: {unavailable_count}"
    )
    print(
        f"Output: {output_path}"
    )


if __name__ == "__main__":
    main()

