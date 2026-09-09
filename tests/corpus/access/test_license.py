from psk_tmd.corpus.access.license import (
    NormalizedLicenseType,
    build_normalized_license_name,
    classify_normalized_license,
    extract_license_version,
    normalize_license,
    normalize_license_token,
)


# ---------------------------------------------------------------------------
# NORMALIZE LICENSE TOKEN
# ---------------------------------------------------------------------------
def test_normalize_license_token():
    assert (
        normalize_license_token(
            "CC BY-NC-ND 4.0"
        )
        == "cc-by-nc-nd-4.0"
    )


# ---------------------------------------------------------------------------
# CREATIVE COMMONS WORDING
# ---------------------------------------------------------------------------
def test_creative_commons_wording():
    token = (
        normalize_license_token(
            "Creative Commons Attribution 4.0"
        )
    )

    assert (
        classify_normalized_license(
            token
        )
        == NormalizedLicenseType.CC_BY
    )


# ---------------------------------------------------------------------------
# EXTRACT LICENSE VERSION
# ---------------------------------------------------------------------------
def test_extract_license_version():
    assert (
        extract_license_version(
            "cc-by-4.0"
        )
        == "4.0"
    )

    assert (
        extract_license_version(
            "cc-by"
        )
        is None
    )


# ---------------------------------------------------------------------------
# NORMALIZE CC BY
# ---------------------------------------------------------------------------
def test_normalize_cc_by():
    result = (
        normalize_license(
            "CC BY 4.0"
        )
    )

    assert (
        result.license_type
        == NormalizedLicenseType.CC_BY
    )

    assert (
        result.version
        == "4.0"
    )

    assert (
        result.normalized_name
        == "CC BY 4.0"
    )


# ---------------------------------------------------------------------------
# NORMALIZE OPENALEX CC BY
# ---------------------------------------------------------------------------
def test_normalize_openalex_cc_by():
    result = (
        normalize_license(
            "cc-by"
        )
    )

    assert (
        result.license_type
        == NormalizedLicenseType.CC_BY
    )

    assert (
        result.version
        is None
    )

    assert (
        result.normalized_name
        == "CC BY"
    )


# ---------------------------------------------------------------------------
# NORMALIZE CC BY NC ND
# ---------------------------------------------------------------------------
def test_normalize_cc_by_nc_nd():
    result = (
        normalize_license(
            "cc-by-nc-nd"
        )
    )

    assert (
        result.license_type
        == NormalizedLicenseType.CC_BY_NC_ND
    )

    assert (
        result.normalized_name
        == "CC BY-NC-ND"
    )


# ---------------------------------------------------------------------------
# NORMALIZE CC BY NC SA
# ---------------------------------------------------------------------------
def test_normalize_cc_by_nc_sa():
    result = (
        normalize_license(
            "CC BY-NC-SA 4.0"
        )
    )

    assert (
        result.license_type
        == NormalizedLicenseType.CC_BY_NC_SA
    )

    assert (
        result.version
        == "4.0"
    )


# ---------------------------------------------------------------------------
# NORMALIZE CC0
# ---------------------------------------------------------------------------
def test_normalize_cc0():
    result = (
        normalize_license(
            "CC0 1.0"
        )
    )

    assert (
        result.license_type
        == NormalizedLicenseType.CC0
    )

    assert (
        result.normalized_name
        == "CC0"
    )


# ---------------------------------------------------------------------------
# NORMALIZE PUBLIC DOMAIN
# ---------------------------------------------------------------------------
def test_normalize_public_domain():
    result = (
        normalize_license(
            "Public Domain"
        )
    )

    assert (
        result.license_type
        == NormalizedLicenseType.PUBLIC_DOMAIN
    )


# ---------------------------------------------------------------------------
# NORMALIZE UNKNOWN
# ---------------------------------------------------------------------------
def test_normalize_unknown():
    result = (
        normalize_license(
            None
        )
    )

    assert (
        result.license_type
        == NormalizedLicenseType.UNKNOWN
    )


# ---------------------------------------------------------------------------
# NORMALIZE OTHER LICENSE
# ---------------------------------------------------------------------------
def test_normalize_other_license():
    result = (
        normalize_license(
            "Example Custom License"
        )
    )

    assert (
        result.license_type
        == NormalizedLicenseType.OTHER
    )

    assert (
        result.normalized_name
        is None
    )


# ---------------------------------------------------------------------------
# BUILD NORMALIZED NAME
# ---------------------------------------------------------------------------
def test_build_normalized_name():
    assert (
        build_normalized_license_name(
            NormalizedLicenseType.CC_BY,
            "4.0",
        )
        == "CC BY 4.0"
    )


