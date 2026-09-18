from psk_tmd.corpus.access.elsevier_api_client import (
    classify_entitlement,
    detect_full_text,
    detect_xml,
    normalize_content_type,
    parse_content_length,
)


# ---------------------------------------------------------------------------
# NORMALIZE CONTENT TYPE
# ---------------------------------------------------------------------------
def test_normalize_content_type():
    assert (
        normalize_content_type(
            "text/xml; charset=UTF-8"
        )
        == "text/xml"
    )


# ---------------------------------------------------------------------------
# PARSE CONTENT LENGTH
# ---------------------------------------------------------------------------
def test_parse_content_length():
    assert (
        parse_content_length(
            "12345"
        )
        == 12345
    )

    assert (
        parse_content_length(
            "invalid"
        )
        is None
    )


# ---------------------------------------------------------------------------
# DETECT XML FROM MIME TYPE
# ---------------------------------------------------------------------------
def test_detect_xml_from_mime_type():
    assert (
        detect_xml(
            content_type="text/xml",
            prefix=b"anything",
        )
        is True
    )


# ---------------------------------------------------------------------------
# DETECT XML FROM PREFIX
# ---------------------------------------------------------------------------
def test_detect_xml_from_prefix():
    assert (
        detect_xml(
            content_type="text/plain",
            prefix=(
                b"<?xml version='1.0'?>"
            ),
        )
        is True
    )


# ---------------------------------------------------------------------------
# DETECT FULL TEXT
# ---------------------------------------------------------------------------
def test_detect_full_text():
    assert (
        detect_full_text(
            (
                b"<xocs:doc>"
                b"<ce:sections>"
            )
        )
        is True
    )


# ---------------------------------------------------------------------------
# METADATA IS NOT FULL TEXT
# ---------------------------------------------------------------------------
def test_metadata_is_not_full_text():
    assert (
        detect_full_text(
            (
                b"<coredata>"
                b"<dc:title>Example</dc:title>"
                b"</coredata>"
            )
        )
        is False
    )


# ---------------------------------------------------------------------------
# FULL TEXT ENTITLEMENT
# ---------------------------------------------------------------------------
def test_full_text_entitlement():
    result = (
        classify_entitlement(
            success=True,
            status_code=200,
            appears_full_text=True,
            response_prefix=(
                b"<xocs:doc>"
            ),
        )
    )

    assert (
        result
        == "full_text_available"
    )


# ---------------------------------------------------------------------------
# RESTRICTED ENTITLEMENT MESSAGE
# ---------------------------------------------------------------------------
def test_restricted_entitlement_message():
    result = (
        classify_entitlement(
            success=False,
            status_code=403,
            appears_full_text=False,
            response_prefix=(
                b"User is not entitled "
                b"to access this resource."
            ),
        )
    )

    assert (
        result
        == "entitlement_restricted"
    )


# ---------------------------------------------------------------------------
# HTTP 403 IS AUTHORIZATION OR ENTITLEMENT RESTRICTED
# ---------------------------------------------------------------------------
def test_http_403_is_authorization_or_entitlement_restricted():
    result = (
        classify_entitlement(
            success=False,
            status_code=403,
            appears_full_text=False,
            response_prefix=b"",
        )
    )

    assert (
        result
        == (
            "authorization_or_"
            "entitlement_restricted"
        )
    )


# ---------------------------------------------------------------------------
# HTTP 401 IS AUTHENTICATION FAILURE
# ---------------------------------------------------------------------------
def test_http_401_is_authentication_failure():
    result = (
        classify_entitlement(
            success=False,
            status_code=401,
            appears_full_text=False,
            response_prefix=b"",
        )
    )

    assert (
        result
        == "authentication_failed"
    )


# ---------------------------------------------------------------------------
# SUCCESS WITHOUT FULL TEXT
# ---------------------------------------------------------------------------
def test_success_without_full_text():
    result = (
        classify_entitlement(
            success=True,
            status_code=200,
            appears_full_text=False,
            response_prefix=(
                b"<coredata/>"
            ),
        )
    )

    assert (
        result
        == (
            "response_received_"
            "full_text_unconfirmed"
        )
    )


