from dataclasses import (
    dataclass,
)


# ---------------------------------------------------------------------------
# QUERY DEFINITION
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DiscoveryQuery:
    query_id: str

    family: str

    perovskite_term: str

    tmd_term: str

    photo_term: str

    query_text: str


# ---------------------------------------------------------------------------
# QUERY VOCABULARY
# ---------------------------------------------------------------------------
GENERIC_PEROVSKITE_TERMS = (
    "perovskite",
    "perovskite oxide",
    "ABO3",
)

SEED_PEROVSKITE_TERMS = (
    "CaTiO3",
    "SrTiO3",
    "BaTiO3",
    "PbTiO3",
    "LaFeO3",
    "LaCoO3",
    "LaNiO3",
    "BiFeO3",
)

TMD_TERMS = (
    "MoS2",
    "WS2",
    "MoSe2",
    "WSe2",
    "MoTe2",
    "WTe2",
    "transition metal dichalcogenide",
)

PHOTO_TERMS = (
    "photocatalysis",
    "photocatalytic",
    "photoelectrocatalysis",
    "photoelectrochemical",
    "hydrogen evolution",
    "CO2 reduction",
    "pollutant degradation",
    "visible light",
)


# ---------------------------------------------------------------------------
# NORMALIZE QUERY TEXT
# ---------------------------------------------------------------------------
def normalize_query_text(
    value: str,
) -> str:
    return " ".join(
        value.split()
    )


# ---------------------------------------------------------------------------
# BUILD QUERY TEXT
# ---------------------------------------------------------------------------
def build_query_text(
    perovskite_term: str,
    tmd_term: str,
    photo_term: str,
) -> str:
    values = (
        perovskite_term,
        tmd_term,
        photo_term,
    )

    normalized_values = [
        normalize_query_text(
            value
        )
        for value in values
        if normalize_query_text(
            value
        )
    ]

    if len(
        normalized_values
    ) != 3:
        raise ValueError(
            "Discovery query terms must "
            "all be non-empty."
        )

    return " ".join(
        normalized_values
    )


# ---------------------------------------------------------------------------
# BUILD QUERY FAMILY
# ---------------------------------------------------------------------------
def build_query_family(
    *,
    family: str,
    perovskite_terms: tuple[
        str,
        ...
    ],
    tmd_terms: tuple[
        str,
        ...
    ],
    photo_terms: tuple[
        str,
        ...
    ],
    start_index: int = 1,
) -> list[
    DiscoveryQuery
]:
    if not family.strip():
        raise ValueError(
            "Discovery query family "
            "must not be empty."
        )

    if start_index < 1:
        raise ValueError(
            "Discovery query start_index "
            "must be at least 1."
        )

    queries: list[
        DiscoveryQuery
    ] = []

    next_index = start_index

    seen_query_texts: set[
        str
    ] = set()

    for perovskite_term in perovskite_terms:
        for tmd_term in tmd_terms:
            for photo_term in photo_terms:
                query_text = (
                    build_query_text(
                        perovskite_term,
                        tmd_term,
                        photo_term,
                    )
                )

                deduplication_key = (
                    query_text.casefold()
                )

                if (
                    deduplication_key
                    in seen_query_texts
                ):
                    continue

                seen_query_texts.add(
                    deduplication_key
                )

                queries.append(
                    DiscoveryQuery(
                        query_id=(
                            f"QRY-"
                            f"{next_index:06d}"
                        ),
                        family=(
                            family.strip()
                        ),
                        perovskite_term=(
                            normalize_query_text(
                                perovskite_term
                            )
                        ),
                        tmd_term=(
                            normalize_query_text(
                                tmd_term
                            )
                        ),
                        photo_term=(
                            normalize_query_text(
                                photo_term
                            )
                        ),
                        query_text=(
                            query_text
                        ),
                    )
                )

                next_index += 1

    return queries


# ---------------------------------------------------------------------------
# BUILD DEFAULT DISCOVERY QUERIES
# ---------------------------------------------------------------------------
def build_default_discovery_queries(
) -> list[
    DiscoveryQuery
]:
    queries: list[
        DiscoveryQuery
    ] = []

    generic_queries = (
        build_query_family(
            family=(
                "generic_perovskite"
            ),
            perovskite_terms=(
                GENERIC_PEROVSKITE_TERMS
            ),
            tmd_terms=(
                TMD_TERMS
            ),
            photo_terms=(
                PHOTO_TERMS
            ),
            start_index=1,
        )
    )

    queries.extend(
        generic_queries
    )

    seed_queries = (
        build_query_family(
            family=(
                "seed_perovskite"
            ),
            perovskite_terms=(
                SEED_PEROVSKITE_TERMS
            ),
            tmd_terms=(
                TMD_TERMS
            ),
            photo_terms=(
                PHOTO_TERMS
            ),
            start_index=(
                len(
                    queries
                )
                + 1
            ),
        )
    )

    queries.extend(
        seed_queries
    )

    return queries


