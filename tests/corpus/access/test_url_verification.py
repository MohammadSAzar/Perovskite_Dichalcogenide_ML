from email.message import (
    Message,
)

from psk_tmd.corpus.access.url_verification import (
    detect_html,
    detect_pdf,
    normalize_content_type,
    parse_content_length,
    verify_url,
)


# ---------------------------------------------------------------------------
# FAKE RESPONSE
# ---------------------------------------------------------------------------
class FakeResponse:
    def __init__(
        self,
        *,
        status: int = 200,
        final_url: str = (
            "https://example.org/article.pdf"
        ),
        content_type: str | None = (
            "application/pdf"
        ),
        content_length: str | None = (
            "12345"
        ),
        body: bytes = (
            b"%PDF-1.7 test"
        ),
    ):
        self.status = (
            status
        )

        self._final_url = (
            final_url
        )

        self._body = (
            body
        )

        self.headers = (
            Message()
        )

        if content_type is not None:
            self.headers[
                "Content-Type"
            ] = (
                content_type
            )

        if content_length is not None:
            self.headers[
                "Content-Length"
            ] = (
                content_length
            )

    def __enter__(
        self,
    ):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False

    def geturl(
        self,
    ) -> str:
        return (
            self._final_url
        )

    def read(
        self,
        size: int = -1,
    ) -> bytes:
        if size < 0:
            return (
                self._body
            )

        return (
            self._body[
                :size
            ]
        )


# ---------------------------------------------------------------------------
# NORMALIZE CONTENT TYPE
# ---------------------------------------------------------------------------
def test_normalize_content_type():
    assert (
        normalize_content_type(
            "Application/PDF; charset=binary"
        )
        == "application/pdf"
    )

    assert (
        normalize_content_type(
            None
        )
        is None
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
            "not-a-number"
        )
        is None
    )

    assert (
        parse_content_length(
            None
        )
        is None
    )


# ---------------------------------------------------------------------------
# DETECT PDF FROM CONTENT TYPE
# ---------------------------------------------------------------------------
def test_detect_pdf_from_content_type():
    assert (
        detect_pdf(
            content_type=(
                "application/pdf"
            ),
            content_prefix=b"",
        )
        is True
    )


# ---------------------------------------------------------------------------
# DETECT PDF FROM MAGIC BYTES
# ---------------------------------------------------------------------------
def test_detect_pdf_from_magic_bytes():
    assert (
        detect_pdf(
            content_type=(
                "application/octet-stream"
            ),
            content_prefix=(
                b"%PDF-1.7 example"
            ),
        )
        is True
    )


# ---------------------------------------------------------------------------
# DETECT HTML FROM CONTENT TYPE
# ---------------------------------------------------------------------------
def test_detect_html_from_content_type():
    assert (
        detect_html(
            content_type="text/html",
            content_prefix=b"",
        )
        is True
    )


# ---------------------------------------------------------------------------
# DETECT HTML FROM CONTENT
# ---------------------------------------------------------------------------
def test_detect_html_from_content():
    assert (
        detect_html(
            content_type=(
                "application/octet-stream"
            ),
            content_prefix=(
                b"<!DOCTYPE html>"
                b"<html></html>"
            ),
        )
        is True
    )


# ---------------------------------------------------------------------------
# VERIFY PDF URL
# ---------------------------------------------------------------------------
def test_verify_pdf_url(
    monkeypatch,
):
    def fake_urlopen(
        request,
        timeout,
        context=None,
    ):
        return FakeResponse()

    monkeypatch.setattr(
        (
            "psk_tmd.corpus.access."
            "url_verification.urlopen"
        ),
        fake_urlopen,
    )

    result = (
        verify_url(
            "https://example.org/article.pdf"
        )
    )

    assert (
        result.success
        is True
    )

    assert (
        result.status_code
        == 200
    )

    assert (
        result.final_url
        == "https://example.org/article.pdf"
    )

    assert (
        result.content_type
        == "application/pdf"
    )

    assert (
        result.content_length
        == 12345
    )

    assert (
        result.appears_pdf
        is True
    )

    assert (
        result.appears_html
        is False
    )


# ---------------------------------------------------------------------------
# VERIFY HTML URL
# ---------------------------------------------------------------------------
def test_verify_html_url(
    monkeypatch,
):
    def fake_urlopen(
        request,
        timeout,
        context=None,
    ):
        return FakeResponse(
            final_url=(
                "https://example.org/article"
            ),
            content_type=(
                "text/html; charset=utf-8"
            ),
            content_length="5000",
            body=(
                b"<!doctype html>"
                b"<html></html>"
            ),
        )

    monkeypatch.setattr(
        (
            "psk_tmd.corpus.access."
            "url_verification.urlopen"
        ),
        fake_urlopen,
    )

    result = (
        verify_url(
            "https://doi.org/10.1000/example"
        )
    )

    assert (
        result.success
        is True
    )

    assert (
        result.final_url
        == "https://example.org/article"
    )

    assert (
        result.content_type
        == "text/html"
    )

    assert (
        result.appears_pdf
        is False
    )

    assert (
        result.appears_html
        is True
    )


# ---------------------------------------------------------------------------
# REDIRECT FINAL URL IS PRESERVED
# ---------------------------------------------------------------------------
def test_redirect_final_url_is_preserved(
    monkeypatch,
):
    def fake_urlopen(
        request,
        timeout,
        context=None,
    ):
        return FakeResponse(
            final_url=(
                "https://publisher.example/"
                "final.pdf"
            )
        )

    monkeypatch.setattr(
        (
            "psk_tmd.corpus.access."
            "url_verification.urlopen"
        ),
        fake_urlopen,
    )

    result = (
        verify_url(
            "https://doi.org/10.1000/example"
        )
    )

    assert (
        result.requested_url
        == "https://doi.org/10.1000/example"
    )

    assert (
        result.final_url
        == (
            "https://publisher.example/"
            "final.pdf"
        )
    )


# ---------------------------------------------------------------------------
# NETWORK ERROR IS CAPTURED
# ---------------------------------------------------------------------------
def test_network_error_is_captured(
    monkeypatch,
):
    def fake_urlopen(
        request,
        timeout,
        context=None,
    ):
        raise RuntimeError(
            "Test network failure"
        )

    monkeypatch.setattr(
        (
            "psk_tmd.corpus.access."
            "url_verification.urlopen"
        ),
        fake_urlopen,
    )

    result = (
        verify_url(
            "https://example.org/article"
        )
    )

    assert (
        result.success
        is False
    )

    assert (
        result.error_type
        == "RuntimeError"
    )

    assert (
        result.error_message
        == "Test network failure"
    )


# ---------------------------------------------------------------------------
# INVALID TIMEOUT
# ---------------------------------------------------------------------------
def test_invalid_timeout():
    try:
        verify_url(
            "https://example.org",
            timeout=0,
        )

    except ValueError as exc:
        assert (
            "greater than zero"
            in str(
                exc
            )
        )

    else:
        raise AssertionError(
            "Expected ValueError."
        )


# ---------------------------------------------------------------------------
# INVALID PREFIX SIZE
# ---------------------------------------------------------------------------
def test_invalid_prefix_size():
    try:
        verify_url(
            "https://example.org",
            prefix_bytes=0,
        )

    except ValueError as exc:
        assert (
            "at least 1"
            in str(
                exc
            )
        )

    else:
        raise AssertionError(
            "Expected ValueError."
        )

# ---------------------------------------------------------------------------
# BUILD SSL CONTEXT
# ---------------------------------------------------------------------------
def test_build_ssl_context():
    from ssl import (
        SSLContext,
    )

    from psk_tmd.corpus.access.url_verification import (
        build_ssl_context,
    )

    context = (
        build_ssl_context()
    )

    assert isinstance(
        context,
        SSLContext,
    )

    assert (
        context.verify_mode
        != 0
    )

    assert (
        context.check_hostname
        is True
    )

