from enum import (
    Enum,
)

from pydantic import (
    BaseModel,
    field_validator,
)

from psk_tmd.common.text_utils import (
    normalize_whitespace,
)


# ---------------------------------------------------------------------------
# NORMALIZED LICENSE TYPE
# ---------------------------------------------------------------------------
class NormalizedLicenseType(
    str,
    Enum,
):
    CC0 = "cc0"

    CC_BY = "cc_by"

    CC_BY_SA = "cc_by_sa"

    CC_BY_ND = "cc_by_nd"

    CC_BY_NC = "cc_by_nc"

    CC_BY_NC_SA = "cc_by_nc_sa"

    CC_BY_NC_ND = "cc_by_nc_nd"

    PUBLIC_DOMAIN = "public_domain"

    OTHER = "other"

    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# NORMALIZED LICENSE
# ---------------------------------------------------------------------------
class NormalizedLicense(
    BaseModel
):
    raw_value: str | None

    license_type: NormalizedLicenseType

    version: str | None = None

    normalized_name: str | None = None

    @field_validator(
        "raw_value",
        "version",
        "normalized_name",
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

        return (
            normalized
            or None
        )


# ---------------------------------------------------------------------------
# NORMALIZE LICENSE TOKEN
# ---------------------------------------------------------------------------
def normalize_license_token(
    value: str,
) -> str:
    normalized = (
        value
        .strip()
        .lower()
        .replace(
            "_",
            "-",
        )
    )

    normalized = (
        normalized
        .replace(
            "creative commons",
            "cc",
        )
        .replace(
            "attribution",
            "by",
        )
        .replace(
            "noncommercial",
            "nc",
        )
        .replace(
            "non-commercial",
            "nc",
        )
        .replace(
            "noderivatives",
            "nd",
        )
        .replace(
            "no derivatives",
            "nd",
        )
        .replace(
            "sharealike",
            "sa",
        )
        .replace(
            "share alike",
            "sa",
        )
    )

    for character in (
        "/",
        ":",
        "(",
        ")",
        ",",
        ";",
    ):
        normalized = (
            normalized.replace(
                character,
                " ",
            )
        )

    normalized = (
        "-".join(
            normalized.split()
        )
    )

    while "--" in normalized:
        normalized = (
            normalized.replace(
                "--",
                "-",
            )
        )

    return normalized


# ---------------------------------------------------------------------------
# EXTRACT LICENSE VERSION
# ---------------------------------------------------------------------------
def extract_license_version(
    token: str,
) -> str | None:
    parts = (
        token.split(
            "-"
        )
    )

    for part in parts:
        if not part:
            continue

        if (
            part[
                0
            ].isdigit()
            and all(
                (
                    character.isdigit()
                    or character == "."
                )
                for character
                in part
            )
        ):
            return part

    return None


# ---------------------------------------------------------------------------
# CLASSIFY NORMALIZED LICENSE
# ---------------------------------------------------------------------------
def classify_normalized_license(
    token: str,
) -> NormalizedLicenseType:
    compact = (
        token.replace(
            "-",
            ""
        )
    )

    if (
        compact.startswith(
            "cc0"
        )
        or "publicdomainzero"
        in compact
    ):
        return (
            NormalizedLicenseType.CC0
        )

    if (
        "publicdomain"
        in compact
    ):
        return (
            NormalizedLicenseType.PUBLIC_DOMAIN
        )

    if (
        "ccbyncnd"
        in compact
    ):
        return (
            NormalizedLicenseType.CC_BY_NC_ND
        )

    if (
        "ccbyncsa"
        in compact
    ):
        return (
            NormalizedLicenseType.CC_BY_NC_SA
        )

    if (
        "ccbync"
        in compact
    ):
        return (
            NormalizedLicenseType.CC_BY_NC
        )

    if (
        "ccbynd"
        in compact
    ):
        return (
            NormalizedLicenseType.CC_BY_ND
        )

    if (
        "ccbysa"
        in compact
    ):
        return (
            NormalizedLicenseType.CC_BY_SA
        )

    if (
        "ccby"
        in compact
    ):
        return (
            NormalizedLicenseType.CC_BY
        )

    if (
        compact
        in {
            "",
            "unknown",
            "none",
            "null",
            "unspecified",
        }
    ):
        return (
            NormalizedLicenseType.UNKNOWN
        )

    return (
        NormalizedLicenseType.OTHER
    )


# ---------------------------------------------------------------------------
# BUILD NORMALIZED LICENSE NAME
# ---------------------------------------------------------------------------
def build_normalized_license_name(
    license_type: NormalizedLicenseType,
    version: str | None,
) -> str | None:
    base_names = {
        NormalizedLicenseType.CC0: (
            "CC0"
        ),
        NormalizedLicenseType.CC_BY: (
            "CC BY"
        ),
        NormalizedLicenseType.CC_BY_SA: (
            "CC BY-SA"
        ),
        NormalizedLicenseType.CC_BY_ND: (
            "CC BY-ND"
        ),
        NormalizedLicenseType.CC_BY_NC: (
            "CC BY-NC"
        ),
        NormalizedLicenseType.CC_BY_NC_SA: (
            "CC BY-NC-SA"
        ),
        NormalizedLicenseType.CC_BY_NC_ND: (
            "CC BY-NC-ND"
        ),
        NormalizedLicenseType.PUBLIC_DOMAIN: (
            "Public Domain"
        ),
    }

    base_name = (
        base_names.get(
            license_type
        )
    )

    if base_name is None:
        return None

    if (
        version is not None
        and license_type
        not in {
            NormalizedLicenseType.CC0,
            NormalizedLicenseType.PUBLIC_DOMAIN,
        }
    ):
        return (
            f"{base_name} "
            f"{version}"
        )

    return base_name


# ---------------------------------------------------------------------------
# NORMALIZE LICENSE
# ---------------------------------------------------------------------------
def normalize_license(
    value: str | None,
) -> NormalizedLicense:
    if value is None:
        return NormalizedLicense(
            raw_value=None,
            license_type=(
                NormalizedLicenseType.UNKNOWN
            ),
        )

    normalized_text = (
        normalize_whitespace(
            value
        )
    )

    if not normalized_text:
        return NormalizedLicense(
            raw_value=None,
            license_type=(
                NormalizedLicenseType.UNKNOWN
            ),
        )

    token = (
        normalize_license_token(
            normalized_text
        )
    )

    license_type = (
        classify_normalized_license(
            token
        )
    )

    version = (
        extract_license_version(
            token
        )
    )

    normalized_name = (
        build_normalized_license_name(
            license_type,
            version,
        )
    )

    return NormalizedLicense(
        raw_value=(
            normalized_text
        ),
        license_type=(
            license_type
        ),
        version=(
            version
        ),
        normalized_name=(
            normalized_name
        ),
    )

