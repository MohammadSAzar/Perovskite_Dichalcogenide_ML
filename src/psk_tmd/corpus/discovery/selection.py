from dataclasses import (
    dataclass,
)

from psk_tmd.corpus.discovery.candidates import (
    DiscoveryCandidate,
)
from psk_tmd.corpus.discovery.screening import (
    DiscoveryScreeningResult,
    DiscoveryScreeningStatus,
)


# ---------------------------------------------------------------------------
# SCREENED CANDIDATE
# ---------------------------------------------------------------------------
ScreenedCandidate = tuple[
    DiscoveryCandidate,
    DiscoveryScreeningResult,
]


# ---------------------------------------------------------------------------
# CANDIDATE SELECTION
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DiscoveryCandidateSelection:
    accepted: tuple[
        ScreenedCandidate,
        ...
    ]

    review: tuple[
        ScreenedCandidate,
        ...
    ]

    rejected: tuple[
        ScreenedCandidate,
        ...
    ]

    @property
    def actionable(
        self,
    ) -> tuple[
        ScreenedCandidate,
        ...
    ]:
        return (
            self.accepted
            + self.review
        )


# ---------------------------------------------------------------------------
# SELECT DISCOVERY CANDIDATES
# ---------------------------------------------------------------------------
def select_discovery_candidates(
    screened_candidates: list[
        ScreenedCandidate
    ]
    | tuple[
        ScreenedCandidate,
        ...
    ],
) -> DiscoveryCandidateSelection:
    accepted: list[
        ScreenedCandidate
    ] = []

    review: list[
        ScreenedCandidate
    ] = []

    rejected: list[
        ScreenedCandidate
    ] = []

    for (
        candidate,
        screening,
    ) in screened_candidates:
        item = (
            candidate,
            screening,
        )

        if (
            screening.status
            == DiscoveryScreeningStatus.PASS
        ):
            accepted.append(
                item
            )

        elif (
            screening.status
            == DiscoveryScreeningStatus.REVIEW
        ):
            review.append(
                item
            )

        elif (
            screening.status
            == DiscoveryScreeningStatus.REJECT
        ):
            rejected.append(
                item
            )

        else:
            raise ValueError(
                "Unsupported discovery "
                "screening status."
            )

    return DiscoveryCandidateSelection(
        accepted=tuple(
            accepted
        ),
        review=tuple(
            review
        ),
        rejected=tuple(
            rejected
        ),
    )

