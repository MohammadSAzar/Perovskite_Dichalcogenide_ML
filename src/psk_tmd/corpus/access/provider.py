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
# PROVIDER TYPE
# ---------------------------------------------------------------------------
class ProviderType(
    str,
    Enum,
):
    PUBLISHER = "publisher"

    REPOSITORY = "repository"

    OTHER = "other"

    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# PROVIDER IDENTIFICATION
# ---------------------------------------------------------------------------
class ProviderIdentification(
    BaseModel
):
    provider_key: str | None

    provider_name: str | None

    provider_type: ProviderType

    matched_from: str | None = None

    reason: str

    @field_validator(
        "provider_key",
        "provider_name",
        "matched_from",
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
                "Provider identification "
                "reason must not be empty."
            )

        return normalized


# ---------------------------------------------------------------------------
# PROVIDER NAME ALIASES
# ---------------------------------------------------------------------------
PROVIDER_NAME_ALIASES = {
    "elsevier": {
        "elsevier",
        "elsevier bv",
        "elsevier b.v.",
    },
    "springer_nature": {
        "nature portfolio",
        "springer nature",
        "springer science and business media llc",
        "springer science+business media",
    },
    "mdpi": {
        "mdpi",
        "mdpi ag",
        "multidisciplinary digital publishing institute",
    },
    "wiley": {
        "wiley",
        "john wiley & sons",
        "john wiley and sons",
    },
    "rsc": {
        "royal society of chemistry",
        "rsc",
    },
    "taylor_francis": {
        "taylor & francis",
        "taylor and francis",
    },
    "arxiv": {
        "arxiv",
    },
}


# ---------------------------------------------------------------------------
# PROVIDER DISPLAY NAMES
# ---------------------------------------------------------------------------
PROVIDER_DISPLAY_NAMES = {
    "elsevier": "Elsevier",
    "springer_nature": "Springer Nature",
    "mdpi": "MDPI",
    "wiley": "Wiley",
    "rsc": "Royal Society of Chemistry",
    "taylor_francis": "Taylor & Francis",
    "arxiv": "arXiv",
}


# ---------------------------------------------------------------------------
# PROVIDER TYPES
# ---------------------------------------------------------------------------
PROVIDER_TYPES = {
    "elsevier": ProviderType.PUBLISHER,
    "springer_nature": ProviderType.PUBLISHER,
    "mdpi": ProviderType.PUBLISHER,
    "wiley": ProviderType.PUBLISHER,
    "rsc": ProviderType.PUBLISHER,
    "taylor_francis": ProviderType.PUBLISHER,
    "arxiv": ProviderType.REPOSITORY,
}


# ---------------------------------------------------------------------------
# HOSTNAME PROVIDER RULES
# ---------------------------------------------------------------------------
HOSTNAME_PROVIDER_RULES = (
    (
        "elsevier",
        (
            "elsevier.com",
            "sciencedirect.com",
            "cell.com",
        ),
    ),
    (
        "springer_nature",
        (
            "nature.com",
            "springer.com",
            "springerlink.com",
        ),
    ),
    (
        "mdpi",
        (
            "mdpi.com",
        ),
    ),
    (
        "wiley",
        (
            "wiley.com",
            "onlinelibrary.wiley.com",
        ),
    ),
    (
        "rsc",
        (
            "rsc.org",
            "pubs.rsc.org",
        ),
    ),
    (
        "taylor_francis",
        (
            "tandfonline.com",
        ),
    ),
    (
        "arxiv",
        (
            "arxiv.org",
        ),
    ),
)


# ---------------------------------------------------------------------------
# NORMALIZE PROVIDER TEXT
# ---------------------------------------------------------------------------
def normalize_provider_text(
    value: str,
) -> str:
    normalized = (
        normalize_whitespace(
            value
        )
        .strip()
        .lower()
    )

    return normalized


# ---------------------------------------------------------------------------
# NORMALIZE HOSTNAME
# ---------------------------------------------------------------------------
def normalize_provider_hostname(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    normalized = (
        value
        .strip()
        .lower()
    )

    return (
        normalized
        or None
    )


# ---------------------------------------------------------------------------
# MATCH PROVIDER FROM NAME
# ---------------------------------------------------------------------------
def match_provider_from_name(
    publisher: str | None,
) -> str | None:
    if publisher is None:
        return None

    normalized = (
        normalize_provider_text(
            publisher
        )
    )

    if not normalized:
        return None

    for (
        provider_key,
        aliases,
    ) in PROVIDER_NAME_ALIASES.items():
        if normalized in aliases:
            return provider_key

    return None


# ---------------------------------------------------------------------------
# MATCH PROVIDER FROM HOSTNAME
# ---------------------------------------------------------------------------
def match_provider_from_hostname(
    hostname: str | None,
) -> str | None:
    normalized = (
        normalize_provider_hostname(
            hostname
        )
    )

    if normalized is None:
        return None

    for (
        provider_key,
        suffixes,
    ) in HOSTNAME_PROVIDER_RULES:
        for suffix in suffixes:
            if (
                normalized
                == suffix
                or normalized.endswith(
                    f".{suffix}"
                )
            ):
                return provider_key

    return None


# ---------------------------------------------------------------------------
# GET HOSTNAME FROM URL
# ---------------------------------------------------------------------------
def get_provider_hostname(
    url: str | None,
) -> str | None:
    if url is None:
        return None

    normalized = (
        normalize_whitespace(
            url
        )
    )

    if not normalized:
        return None

    parsed = (
        urlparse(
            normalized
        )
    )

    return (
        normalize_provider_hostname(
            parsed.hostname
        )
    )


# ---------------------------------------------------------------------------
# BUILD PROVIDER IDENTIFICATION
# ---------------------------------------------------------------------------
def build_provider_identification(
    provider_key: str,
    *,
    matched_from: str,
    reason: str,
) -> ProviderIdentification:
    return ProviderIdentification(
        provider_key=(
            provider_key
        ),
        provider_name=(
            PROVIDER_DISPLAY_NAMES[
                provider_key
            ]
        ),
        provider_type=(
            PROVIDER_TYPES[
                provider_key
            ]
        ),
        matched_from=(
            matched_from
        ),
        reason=(
            reason
        ),
    )


# ---------------------------------------------------------------------------
# IDENTIFY PROVIDER
# ---------------------------------------------------------------------------
def identify_provider(
    *,
    publisher: str | None = None,
    url: str | None = None,
) -> ProviderIdentification:
    hostname = (
        get_provider_hostname(
            url
        )
    )

    hostname_match = (
        match_provider_from_hostname(
            hostname
        )
    )

    if hostname_match is not None:
        return (
            build_provider_identification(
                hostname_match,
                matched_from=(
                    f"hostname:{hostname}"
                ),
                reason=(
                    "Provider was identified "
                    "from the access-location "
                    "hostname."
                ),
            )
        )

    publisher_match = (
        match_provider_from_name(
            publisher
        )
    )

    if publisher_match is not None:
        return (
            build_provider_identification(
                publisher_match,
                matched_from=(
                    f"publisher:{publisher}"
                ),
                reason=(
                    "Provider was identified "
                    "from the normalized "
                    "publisher name."
                ),
            )
        )

    if (
        publisher is not None
        or hostname is not None
    ):
        return ProviderIdentification(
            provider_key=None,
            provider_name=(
                publisher
            ),
            provider_type=(
                ProviderType.OTHER
            ),
            matched_from=(
                (
                    f"hostname:{hostname}"
                    if hostname is not None
                    else f"publisher:{publisher}"
                )
            ),
            reason=(
                "The publisher or hostname "
                "did not match a known "
                "provider rule."
            ),
        )

    return ProviderIdentification(
        provider_key=None,
        provider_name=None,
        provider_type=(
            ProviderType.UNKNOWN
        ),
        reason=(
            "No publisher name or URL "
            "was available for provider "
            "identification."
        ),
    )

