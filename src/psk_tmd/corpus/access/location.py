from enum import (
    Enum,
)
from urllib.parse import (
    urlparse,
)

from pydantic import (
    BaseModel,
    field_validator,
)

from psk_tmd.common.text_utils import (
    normalize_whitespace,
)


# ---------------------------------------------------------------------------
# ACCESS LOCATION TYPE
# ---------------------------------------------------------------------------
class AccessLocationType(
    str,
    Enum,
):
    PUBLISHER = "publisher"
    REPOSITORY = "repository"
    DOI = "doi"
    OTHER = "other"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# ACCESS LOCATION CLASSIFICATION
# ---------------------------------------------------------------------------
class AccessLocationClassification(
    BaseModel
):
    location_type: AccessLocationType

    url: str | None = None

    hostname: str | None = None

    reason: str

    @field_validator(
        "url",
        "hostname",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = (
            normalize_whitespace(
                value
            )
        )

        if not normalized:
            return None

        return normalized

    @field_validator(
        "reason",
    )
    @classmethod
    def validate_reason(
        cls,
        value: str,
    ) -> str:
        normalized = (
            normalize_whitespace(
                value
            )
        )

        if not normalized:
            raise ValueError(
                "Location classification "
                "reason must not be empty."
            )

        return normalized


# ---------------------------------------------------------------------------
# REPOSITORY HOSTNAMES
# ---------------------------------------------------------------------------
REPOSITORY_HOSTNAMES = {
    "arxiv.org",
    "www.arxiv.org",
    "europepmc.org",
    "www.europepmc.org",
    "pmc.ncbi.nlm.nih.gov",
}


# ---------------------------------------------------------------------------
# PUBLISHER HOSTNAME SUFFIXES
# ---------------------------------------------------------------------------
PUBLISHER_HOSTNAME_SUFFIXES = (
    "cell.com",
    "elsevier.com",
    "sciencedirect.com",
    "nature.com",
    "springer.com",
    "springerlink.com",
    "mdpi.com",
    "wiley.com",
    "onlinelibrary.wiley.com",
    "tandfonline.com",
    "rsc.org",
    "pubs.rsc.org",
)


# ---------------------------------------------------------------------------
# NORMALIZE HOSTNAME
# ---------------------------------------------------------------------------
def normalize_hostname(
    hostname: str | None,
) -> str | None:
    if hostname is None:
        return None

    normalized = (
        hostname
        .strip()
        .lower()
    )

    return (
        normalized
        or None
    )


# ---------------------------------------------------------------------------
# IS PUBLISHER HOSTNAME
# ---------------------------------------------------------------------------
def is_publisher_hostname(
    hostname: str,
) -> bool:
    normalized = (
        normalize_hostname(
            hostname
        )
    )

    if normalized is None:
        return False

    return any(
        (
            normalized
            == suffix
            or normalized.endswith(
                f".{suffix}"
            )
        )
        for suffix in (
            PUBLISHER_HOSTNAME_SUFFIXES
        )
    )


# ---------------------------------------------------------------------------
# CLASSIFY ACCESS LOCATION
# ---------------------------------------------------------------------------
def classify_access_location(
    url: str | None,
) -> AccessLocationClassification:
    if url is None:
        return AccessLocationClassification(
            location_type=(
                AccessLocationType.UNKNOWN
            ),
            reason=(
                "No access location URL "
                "was provided."
            ),
        )

    normalized_url = (
        normalize_whitespace(
            url
        )
    )

    if not normalized_url:
        return AccessLocationClassification(
            location_type=(
                AccessLocationType.UNKNOWN
            ),
            reason=(
                "Access location URL "
                "was empty."
            ),
        )

    parsed = (
        urlparse(
            normalized_url
        )
    )

    hostname = (
        normalize_hostname(
            parsed.hostname
        )
    )

    if hostname is None:
        return AccessLocationClassification(
            location_type=(
                AccessLocationType.UNKNOWN
            ),
            url=(
                normalized_url
            ),
            reason=(
                "Access location URL "
                "did not contain a hostname."
            ),
        )

    if (
        hostname
        in {
            "doi.org",
            "www.doi.org",
            "dx.doi.org",
        }
    ):
        return AccessLocationClassification(
            location_type=(
                AccessLocationType.DOI
            ),
            url=(
                normalized_url
            ),
            hostname=(
                hostname
            ),
            reason=(
                "The reported access location "
                "is a DOI resolver rather than "
                "a direct publisher or repository "
                "location."
            ),
        )

    if (
        hostname
        in REPOSITORY_HOSTNAMES
    ):
        return AccessLocationClassification(
            location_type=(
                AccessLocationType.REPOSITORY
            ),
            url=(
                normalized_url
            ),
            hostname=(
                hostname
            ),
            reason=(
                "The reported access location "
                "is hosted by a recognized "
                "repository."
            ),
        )

    if (
        is_publisher_hostname(
            hostname
        )
    ):
        return AccessLocationClassification(
            location_type=(
                AccessLocationType.PUBLISHER
            ),
            url=(
                normalized_url
            ),
            hostname=(
                hostname
            ),
            reason=(
                "The reported access location "
                "is hosted on a recognized "
                "publisher domain."
            ),
        )

    return AccessLocationClassification(
        location_type=(
            AccessLocationType.OTHER
        ),
        url=(
            normalized_url
        ),
        hostname=(
            hostname
        ),
        reason=(
            "The reported access location "
            "is neither a recognized DOI "
            "resolver, repository, nor "
            "publisher domain."
        ),
    )


