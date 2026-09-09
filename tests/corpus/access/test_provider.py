from psk_tmd.corpus.access.provider import (
    ProviderType,
    get_provider_hostname,
    identify_provider,
    match_provider_from_hostname,
    match_provider_from_name,
    normalize_provider_hostname,
)


# ---------------------------------------------------------------------------
# MATCH ELSEVIER NAME
# ---------------------------------------------------------------------------
def test_match_elsevier_name():
    assert (
        match_provider_from_name(
            "Elsevier BV"
        )
        == "elsevier"
    )


# ---------------------------------------------------------------------------
# MATCH SPRINGER NATURE NAME
# ---------------------------------------------------------------------------
def test_match_springer_nature_name():
    assert (
        match_provider_from_name(
            "Nature Portfolio"
        )
        == "springer_nature"
    )


# ---------------------------------------------------------------------------
# MATCH MDPI NAME VARIANTS
# ---------------------------------------------------------------------------
def test_match_mdpi_name_variants():
    assert (
        match_provider_from_name(
            "MDPI AG"
        )
        == "mdpi"
    )

    assert (
        match_provider_from_name(
            (
                "Multidisciplinary Digital "
                "Publishing Institute"
            )
        )
        == "mdpi"
    )


# ---------------------------------------------------------------------------
# MATCH WILEY NAME
# ---------------------------------------------------------------------------
def test_match_wiley_name():
    assert (
        match_provider_from_name(
            "Wiley"
        )
        == "wiley"
    )


# ---------------------------------------------------------------------------
# MATCH RSC NAME
# ---------------------------------------------------------------------------
def test_match_rsc_name():
    assert (
        match_provider_from_name(
            "Royal Society of Chemistry"
        )
        == "rsc"
    )


# ---------------------------------------------------------------------------
# MATCH TAYLOR FRANCIS NAME
# ---------------------------------------------------------------------------
def test_match_taylor_francis_name():
    assert (
        match_provider_from_name(
            "Taylor & Francis"
        )
        == "taylor_francis"
    )


# ---------------------------------------------------------------------------
# NORMALIZE HOSTNAME
# ---------------------------------------------------------------------------
def test_normalize_hostname():
    assert (
        normalize_provider_hostname(
            "  WWW.NATURE.COM "
        )
        == "www.nature.com"
    )


# ---------------------------------------------------------------------------
# GET HOSTNAME FROM URL
# ---------------------------------------------------------------------------
def test_get_hostname_from_url():
    assert (
        get_provider_hostname(
            (
                "https://linkinghub.elsevier.com/"
                "retrieve/pii/example"
            )
        )
        == "linkinghub.elsevier.com"
    )


# ---------------------------------------------------------------------------
# MATCH ELSEVIER HOSTNAME
# ---------------------------------------------------------------------------
def test_match_elsevier_hostname():
    assert (
        match_provider_from_hostname(
            "linkinghub.elsevier.com"
        )
        == "elsevier"
    )

    assert (
        match_provider_from_hostname(
            "www.cell.com"
        )
        == "elsevier"
    )


# ---------------------------------------------------------------------------
# MATCH NATURE HOSTNAME
# ---------------------------------------------------------------------------
def test_match_nature_hostname():
    assert (
        match_provider_from_hostname(
            "www.nature.com"
        )
        == "springer_nature"
    )


# ---------------------------------------------------------------------------
# MATCH MDPI HOSTNAME
# ---------------------------------------------------------------------------
def test_match_mdpi_hostname():
    assert (
        match_provider_from_hostname(
            "www.mdpi.com"
        )
        == "mdpi"
    )


# ---------------------------------------------------------------------------
# MATCH ARXIV HOSTNAME
# ---------------------------------------------------------------------------
def test_match_arxiv_hostname():
    assert (
        match_provider_from_hostname(
            "arxiv.org"
        )
        == "arxiv"
    )


# ---------------------------------------------------------------------------
# URL TAKES PRECEDENCE OVER PUBLISHER
# ---------------------------------------------------------------------------
def test_url_takes_precedence_over_publisher():
    result = (
        identify_provider(
            publisher="Elsevier BV",
            url=(
                "https://arxiv.org/"
                "pdf/2111.03139"
            ),
        )
    )

    assert (
        result.provider_key
        == "arxiv"
    )

    assert (
        result.provider_type
        == ProviderType.REPOSITORY
    )


# ---------------------------------------------------------------------------
# IDENTIFY ELSEVIER FROM REDIRECT URL
# ---------------------------------------------------------------------------
def test_identify_elsevier_from_redirect_url():
    result = (
        identify_provider(
            publisher="Elsevier BV",
            url=(
                "https://linkinghub."
                "elsevier.com/retrieve/pii/"
                "S123"
            ),
        )
    )

    assert (
        result.provider_key
        == "elsevier"
    )

    assert (
        result.provider_type
        == ProviderType.PUBLISHER
    )


# ---------------------------------------------------------------------------
# IDENTIFY PROVIDER FROM PUBLISHER FALLBACK
# ---------------------------------------------------------------------------
def test_identify_provider_from_publisher_fallback():
    result = (
        identify_provider(
            publisher="MDPI AG",
            url=(
                "https://doi.org/"
                "10.3390/example"
            ),
        )
    )

    assert (
        result.provider_key
        == "mdpi"
    )

    assert (
        result.provider_type
        == ProviderType.PUBLISHER
    )


# ---------------------------------------------------------------------------
# UNKNOWN PROVIDER
# ---------------------------------------------------------------------------
def test_unknown_provider():
    result = (
        identify_provider(
            publisher=None,
            url=None,
        )
    )

    assert (
        result.provider_key
        is None
    )

    assert (
        result.provider_type
        == ProviderType.UNKNOWN
    )


# ---------------------------------------------------------------------------
# OTHER PROVIDER
# ---------------------------------------------------------------------------
def test_other_provider():
    result = (
        identify_provider(
            publisher=(
                "Example Scientific Press"
            ),
            url=(
                "https://example.org/article"
            ),
        )
    )

    assert (
        result.provider_key
        is None
    )

    assert (
        result.provider_type
        == ProviderType.OTHER
    )


