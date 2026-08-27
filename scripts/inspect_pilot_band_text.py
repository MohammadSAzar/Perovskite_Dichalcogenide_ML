import sys
import re

from pathlib import Path

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.pdf_text import (
    extract_pdf_text,
)


# ---------------------------------------------------------------------------
# PILOT FILES
# ---------------------------------------------------------------------------
PILOT_FILES = [
    (
        "Mao 2019",
        PROJECT_ROOT
        / "data"
        / "raw"
        / "literature"
        / "2019.Mao.pdf",
    ),
    (
        "Jiang 2020",
        PROJECT_ROOT
        / "data"
        / "raw"
        / "literature"
        / "2020.Jiang.pdf",
    ),
    (
        "Rashki 2022",
        PROJECT_ROOT
        / "data"
        / "raw"
        / "literature"
        / "2022.Rashki.pdf",
    ),
    (
        "Qin 2023",
        PROJECT_ROOT
        / "data"
        / "raw"
        / "literature"
        / "2023.Qin.pdf",
    ),
]


# ---------------------------------------------------------------------------
# SEARCH PATTERNS
# ---------------------------------------------------------------------------
SEARCH_PATTERNS = [
    re.compile(
        r"band",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bEg\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"E\s*g",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bCB\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bVB\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"conduction",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"valence",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\beV\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"NHE",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"Ag\s*/\s*AgCl",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"Tauc",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"Mott",
        flags=re.IGNORECASE,
    ),
]


# ---------------------------------------------------------------------------
# IS RELEVANT LINE
# ---------------------------------------------------------------------------
def is_relevant_line(
    line: str,
) -> bool:
    return any(
        pattern.search(
            line
        )
        is not None
        for pattern in SEARCH_PATTERNS
    )


# ---------------------------------------------------------------------------
# CLEAN LINE
# ---------------------------------------------------------------------------
def clean_line(
    line: str,
    *,
    max_length: int = 240,
) -> str:
    clean = " ".join(
        line.split()
    )

    if len(
        clean
    ) <= max_length:
        return clean

    return (
        clean[
            :max_length - 3
        ]
        + "..."
    )


# ---------------------------------------------------------------------------
# CONFIGURE UTF-8 OUTPUT
# ---------------------------------------------------------------------------
def configure_utf8_output() -> None:
    sys.stdout.reconfigure(
        encoding="utf-8",
        errors="replace",
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    configure_utf8_output()

    for (
        paper_name,
        path,
    ) in PILOT_FILES:
        document = (
            extract_pdf_text(
                path
            )
        )

        print()
        print(
            "=" * 100
        )
        print(
            paper_name
        )
        print(
            "=" * 100
        )
        print(
            f"Characters: "
            f"{len(document.full_text)}"
        )
        print(
            f"Pages: "
            f"{document.page_count}"
        )
        print()

        relevant_lines = []

        for line in (
            document.full_text
            .splitlines()
        ):
            if is_relevant_line(
                line
            ):
                clean = (
                    clean_line(
                        line
                    )
                )

                if clean:
                    relevant_lines.append(
                        clean
                    )

        print(
            f"Relevant lines: "
            f"{len(relevant_lines)}"
        )
        print(
            "-" * 100
        )

        for line in (
            relevant_lines[
                :80
            ]
        ):
            print(
                line
            )


if __name__ == "__main__":
    main()

