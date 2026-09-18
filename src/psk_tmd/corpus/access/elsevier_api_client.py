import ssl

from urllib.error import (
    HTTPError,
    URLError,
)
from urllib.request import (
    Request,
    urlopen,
)

from pydantic import (
    BaseModel,
    field_validator,
)

from psk_tmd.common.text_utils import (
    normalize_whitespace,
)
from psk_tmd.corpus.access.credentials import (
    get_elsevier_api_key,
)
from psk_tmd.corpus.access.elsevier_api import (
    ElsevierArticleAPIRequest,
)


# ---------------------------------------------------------------------------
# CLIENT CONFIGURATION
# ---------------------------------------------------------------------------
DEFAULT_TIMEOUT_SECONDS = 30

DEFAULT_PREFIX_BYTES = 8192


# ---------------------------------------------------------------------------
# ELSEVIER API RESPONSE
# ---------------------------------------------------------------------------
class ElsevierAPIResponse(
    BaseModel
):
    success: bool

    status_code: int | None = None

    content_type: str | None = None

    content_length: int | None = None

    appears_xml: bool = False

    appears_full_text: bool = False

    entitlement_outcome: str

    error_type: str | None = None

    error_message: str | None = None

    @field_validator(
        "content_type",
        "entitlement_outcome",
        "error_type",
        "error_message",
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
# BUILD SSL CONTEXT
# ---------------------------------------------------------------------------
def build_ssl_context(
) -> ssl.SSLContext:
    try:
        import certifi

    except ImportError:
        return (
            ssl.create_default_context()
        )

    return (
        ssl.create_default_context(
            cafile=(
                certifi.where()
            )
        )
    )


# ---------------------------------------------------------------------------
# NORMALIZE CONTENT TYPE
# ---------------------------------------------------------------------------
def normalize_content_type(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    normalized = (
        value
        .split(
            ";",
            1,
        )[
            0
        ]
        .strip()
        .lower()
    )

    return (
        normalized
        or None
    )


# ---------------------------------------------------------------------------
# PARSE CONTENT LENGTH
# ---------------------------------------------------------------------------
def parse_content_length(
    value: str | None,
) -> int | None:
    if value is None:
        return None

    try:
        return int(
            value
        )

    except ValueError:
        return None


# ---------------------------------------------------------------------------
# DETECT XML
# ---------------------------------------------------------------------------
def detect_xml(
    *,
    content_type: str | None,
    prefix: bytes,
) -> bool:
    if (
        content_type
        in {
            "text/xml",
            "application/xml",
        }
    ):
        return True

    stripped = (
        prefix.lstrip()
    )

    return (
        stripped.startswith(
            b"<?xml"
        )
    )


# ---------------------------------------------------------------------------
# DETECT FULL TEXT
# ---------------------------------------------------------------------------
def detect_full_text(
    prefix: bytes,
) -> bool:
    lowered = (
        prefix.lower()
    )

    markers = (
        b"<xocs:doc",
        b"<ce:sections",
        b"<ce:section",
        b"<body",
    )

    return any(
        marker in lowered
        for marker
        in markers
    )


# ---------------------------------------------------------------------------
# CLASSIFY ENTITLEMENT
# ---------------------------------------------------------------------------
def classify_entitlement(
    *,
    success: bool,
    status_code: int | None,
    appears_full_text: bool,
    response_prefix: bytes,
) -> str:
    if (
        success
        and appears_full_text
    ):
        return (
            "full_text_available"
        )

    lowered = (
        response_prefix.lower()
    )

    if (
        b"not entitled"
        in lowered
        or b"entitlement"
        in lowered
        or b"authorization"
        in lowered
    ):
        return (
            "entitlement_restricted"
        )

    if (
        status_code
        == 401
    ):
        return (
            "authentication_failed"
        )

    if (
        status_code
        == 403
    ):
        return (
            "authorization_or_entitlement_restricted"
        )

    if success:
        return (
            "response_received_full_text_unconfirmed"
        )

    return (
        "request_failed"
    )


# ---------------------------------------------------------------------------
# FETCH ELSEVIER ARTICLE
# ---------------------------------------------------------------------------
def fetch_elsevier_article(
    request_spec: ElsevierArticleAPIRequest,
    *,
    timeout: int = (
        DEFAULT_TIMEOUT_SECONDS
    ),
    prefix_bytes: int = (
        DEFAULT_PREFIX_BYTES
    ),
) -> ElsevierAPIResponse:
    api_key = (
        get_elsevier_api_key()
    )

    request = Request(
        request_spec.endpoint_url,
        headers={
            "Accept": (
                request_spec.accept
            ),
            request_spec.api_key_header: (
                api_key
            ),
            "User-Agent": (
                "psk-tmd-ml/0.1"
            ),
        },
        method="GET",
    )

    ssl_context = (
        build_ssl_context()
    )

    try:
        with urlopen(
            request,
            timeout=(
                timeout
            ),
            context=(
                ssl_context
            ),
        ) as response:
            status_code = (
                response.status
            )

            content_type = (
                normalize_content_type(
                    response.headers.get(
                        "Content-Type"
                    )
                )
            )

            content_length = (
                parse_content_length(
                    response.headers.get(
                        "Content-Length"
                    )
                )
            )

            prefix = (
                response.read(
                    prefix_bytes
                )
            )

            appears_xml = (
                detect_xml(
                    content_type=(
                        content_type
                    ),
                    prefix=(
                        prefix
                    ),
                )
            )

            appears_full_text = (
                detect_full_text(
                    prefix
                )
            )

            entitlement_outcome = (
                classify_entitlement(
                    success=True,
                    status_code=(
                        status_code
                    ),
                    appears_full_text=(
                        appears_full_text
                    ),
                    response_prefix=(
                        prefix
                    ),
                )
            )

            return ElsevierAPIResponse(
                success=True,
                status_code=(
                    status_code
                ),
                content_type=(
                    content_type
                ),
                content_length=(
                    content_length
                ),
                appears_xml=(
                    appears_xml
                ),
                appears_full_text=(
                    appears_full_text
                ),
                entitlement_outcome=(
                    entitlement_outcome
                ),
            )

    except HTTPError as exc:
        try:
            prefix = (
                exc.read(
                    prefix_bytes
                )
            )

        except Exception:
            prefix = b""

        return ElsevierAPIResponse(
            success=False,
            status_code=(
                exc.code
            ),
            content_type=(
                normalize_content_type(
                    exc.headers.get(
                        "Content-Type"
                    )
                    if exc.headers
                    else None
                )
            ),
            appears_xml=(
                detect_xml(
                    content_type=(
                        normalize_content_type(
                            exc.headers.get(
                                "Content-Type"
                            )
                            if exc.headers
                            else None
                        )
                    ),
                    prefix=(
                        prefix
                    ),
                )
            ),
            appears_full_text=False,
            entitlement_outcome=(
                classify_entitlement(
                    success=False,
                    status_code=(
                        exc.code
                    ),
                    appears_full_text=False,
                    response_prefix=(
                        prefix
                    ),
                )
            ),
            error_type=(
                "HTTPError"
            ),
            error_message=(
                f"HTTP Error "
                f"{exc.code}: "
                f"{exc.reason}"
            ),
        )

    except URLError as exc:
        return ElsevierAPIResponse(
            success=False,
            entitlement_outcome=(
                "request_failed"
            ),
            error_type=(
                "URLError"
            ),
            error_message=(
                str(
                    exc.reason
                )
            ),
        )

    except Exception as exc:
        return ElsevierAPIResponse(
            success=False,
            entitlement_outcome=(
                "request_failed"
            ),
            error_type=(
                type(
                    exc
                ).__name__
            ),
            error_message=(
                str(
                    exc
                )
            ),
        )

