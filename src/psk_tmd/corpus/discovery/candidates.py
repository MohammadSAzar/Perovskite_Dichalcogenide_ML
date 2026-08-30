from dataclasses import (
    dataclass,
)

from psk_tmd.corpus.discovery.deduplication import (
    get_discovery_group_key,
    merge_discovery_group,
)
from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)
from psk_tmd.corpus.discovery.runner import (
    DiscoveryHit,
)


# ---------------------------------------------------------------------------
# SOURCE RANK
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DiscoverySourceRank:
    source: str

    best_rank: int


# ---------------------------------------------------------------------------
# DISCOVERY CANDIDATE
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DiscoveryCandidate:
    candidate_id: str

    group_key: str

    record: DiscoveryRecord

    hit_count: int

    query_ids: tuple[
        str,
        ...
    ]

    query_texts: tuple[
        str,
        ...
    ]

    families: tuple[
        str,
        ...
    ]

    sources: tuple[
        str,
        ...
    ]

    source_ranks: tuple[
        DiscoverySourceRank,
        ...
    ]


# ---------------------------------------------------------------------------
# GROUP DISCOVERY HITS
# ---------------------------------------------------------------------------
def group_discovery_hits(
    hits: list[
        DiscoveryHit
    ]
    | tuple[
        DiscoveryHit,
        ...
    ],
) -> dict[
    str,
    list[
        DiscoveryHit
    ],
]:
    grouped: dict[
        str,
        list[
            DiscoveryHit
        ],
    ] = {}

    for hit in hits:
        key = (
            get_discovery_group_key(
                hit.record
            )
        )

        grouped.setdefault(
            key,
            [],
        ).append(
            hit
        )

    return grouped


# ---------------------------------------------------------------------------
# GET UNIQUE VALUES
# ---------------------------------------------------------------------------
def get_unique_values(
    values: list[
        str
    ],
) -> tuple[
    str,
    ...
]:
    return tuple(
        sorted(
            set(
                values
            )
        )
    )


# ---------------------------------------------------------------------------
# BUILD SOURCE RANKS
# ---------------------------------------------------------------------------
def build_source_ranks(
    hits: list[
        DiscoveryHit
    ],
) -> tuple[
    DiscoverySourceRank,
    ...
]:
    best_ranks: dict[
        str,
        int,
    ] = {}

    for hit in hits:
        current = (
            best_ranks.get(
                hit.source
            )
        )

        if (
            current is None
            or hit.source_rank
            < current
        ):
            best_ranks[
                hit.source
            ] = (
                hit.source_rank
            )

    return tuple(
        DiscoverySourceRank(
            source=source,
            best_rank=(
                best_ranks[
                    source
                ]
            ),
        )
        for source in sorted(
            best_ranks
        )
    )


# ---------------------------------------------------------------------------
# BUILD DISCOVERY CANDIDATE
# ---------------------------------------------------------------------------
def build_discovery_candidate(
    hits: list[
        DiscoveryHit
    ],
    *,
    candidate_id: str,
) -> DiscoveryCandidate:
    if not hits:
        raise ValueError(
            "Discovery candidate hits "
            "must not be empty."
        )

    group_keys = {
        get_discovery_group_key(
            hit.record
        )
        for hit in hits
    }

    if len(
        group_keys
    ) != 1:
        raise ValueError(
            "Discovery candidate hits "
            "must belong to one group."
        )

    group_key = next(
        iter(
            group_keys
        )
    )

    records = [
        hit.record
        for hit in hits
    ]

    merged_record = (
        merge_discovery_group(
            records,
            discovery_id=(
                candidate_id
            ),
        )
    )

    return DiscoveryCandidate(
        candidate_id=(
            candidate_id
        ),
        group_key=(
            group_key
        ),
        record=(
            merged_record
        ),
        hit_count=len(
            hits
        ),
        query_ids=(
            get_unique_values(
                [
                    hit.query_id
                    for hit in hits
                ]
            )
        ),
        query_texts=(
            get_unique_values(
                [
                    hit.query_text
                    for hit in hits
                ]
            )
        ),
        families=(
            get_unique_values(
                [
                    hit.family
                    for hit in hits
                ]
            )
        ),
        sources=(
            get_unique_values(
                [
                    hit.source
                    for hit in hits
                ]
            )
        ),
        source_ranks=(
            build_source_ranks(
                hits
            )
        ),
    )


# ---------------------------------------------------------------------------
# BUILD DISCOVERY CANDIDATES
# ---------------------------------------------------------------------------
def build_discovery_candidates(
    hits: list[
        DiscoveryHit
    ]
    | tuple[
        DiscoveryHit,
        ...
    ],
    *,
    start_index: int = 1,
) -> list[
    DiscoveryCandidate
]:
    if start_index < 1:
        raise ValueError(
            "Discovery candidate "
            "start_index must be at least 1."
        )

    grouped = (
        group_discovery_hits(
            hits
        )
    )

    candidates: list[
        DiscoveryCandidate
    ] = []

    next_index = (
        start_index
    )

    for group_key in sorted(
        grouped
    ):
        candidate = (
            build_discovery_candidate(
                grouped[
                    group_key
                ],
                candidate_id=(
                    f"CND-"
                    f"{next_index:06d}"
                ),
            )
        )

        candidates.append(
            candidate
        )

        next_index += 1

    return candidates

