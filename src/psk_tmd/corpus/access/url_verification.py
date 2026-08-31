import ssl

from pydantic import (
    BaseModel,
    field_validator,
)
from urllib.request import (
    Request,
    urlopen,
)

from psk_tmd.common.text_utils import (
    normalize_whitespace,
)


# ---------------------------------------------------------------------------
# URL VERIFICATION RESULT
# ---------------------------------------------------------------------------
class URLVerificationResult(
    BaseModel
):
    requested_url: str

    success: bool

    status_code: int | None = None

    final_url: str | None = None

    content_type: str | None = None

    content_length: int | None = None

    appears_pdf: bool = False

    appears_html: bool = False

    error_type: str | None = None

    error_message: str | None = None

    @field_validator(
        "requested_url",
    )
    @classmethod
    def validate_requested_url(
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
                "requested_url "
                "must not be empty."
            )

        return normalized

    @field_validator(
        "final_url",
        "content_type",
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

    @field_validator(
        "content_length",
    )
    @classmethod
    def validate_content_length(
        cls,
        value: int | None,
    ) -> int | None:
        if (
            value is not None
            and value < 0
        ):
            raise ValueError(
                "content_length "
                "must not be negative."
            )

        return value


# ---------------------------------------------------------------------------
# VERIFIER CONFIGURATION
# ---------------------------------------------------------------------------
DEFAULT_USER_AGENT = (
    "psk-tmd-ml/0.1"
)

DEFAULT_PREFIX_BYTES = 8192


# ---------------------------------------------------------------------------
# BUILD SSL CONTEXT
# ---------------------------------------------------------------------------
def build_ssl_context() -> ssl.SSLContext:
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
            maxsplit=1,
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
        parsed = int(
            value.strip()
        )

    except (
        TypeError,
        ValueError,
    ):
        return None

    if parsed < 0:
        return None

    return parsed


# ---------------------------------------------------------------------------
# DETECT PDF
# ---------------------------------------------------------------------------
def detect_pdf(
    *,
    content_type: str | None,
    content_prefix: bytes,
) -> bool:
    if (
        content_type
        == "application/pdf"
    ):
        return True

    return (
        content_prefix
        .lstrip()
        .startswith(
            b"%PDF-"
        )
    )


# ---------------------------------------------------------------------------
# DETECT HTML
# ---------------------------------------------------------------------------
def detect_html(
    *,
    content_type: str | None,
    content_prefix: bytes,
) -> bool:
    if (
        content_type
        in {
            "text/html",
            "application/xhtml+xml",
        }
    ):
        return True

    normalized_prefix = (
        content_prefix[
            :1024
        ]
        .lstrip()
        .lower()
    )

    return (
        normalized_prefix.startswith(
            b"<!doctype html"
        )
        or normalized_prefix.startswith(
            b"<html"
        )
    )


# ---------------------------------------------------------------------------
# VERIFY URL
# ---------------------------------------------------------------------------
def verify_url(
    url: str,
    *,
    timeout: float = 30.0,
    prefix_bytes: int = DEFAULT_PREFIX_BYTES,
    user_agent: str = DEFAULT_USER_AGENT,
) -> URLVerificationResult:
    normalized_url = (
        normalize_whitespace(
            url
        )
    )

    if not normalized_url:
        raise ValueError(
            "URL must not be empty."
        )

    if timeout <= 0:
        raise ValueError(
            "timeout must be "
            "greater than zero."
        )

    if prefix_bytes < 1:
        raise ValueError(
            "prefix_bytes must be "
            "at least 1."
        )

    request = Request(
        normalized_url,
        headers={
            "User-Agent": (
                user_agent
            ),
            "Accept": (
                "application/pdf,"
                "text/html,"
                "application/xhtml+xml,"
                "*/*;q=0.8"
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
            timeout=timeout,
            context=ssl_context,
        ) as response:
            status_code = getattr(
                response,
                "status",
                None,
            )

            final_url = (
                response.geturl()
            )

            raw_content_type = (
                response.headers.get(
                    "Content-Type"
                )
            )

            content_type = (
                normalize_content_type(
                    raw_content_type
                )
            )

            content_length = (
                parse_content_length(
                    response.headers.get(
                        "Content-Length"
                    )
                )
            )

            content_prefix = (
                response.read(
                    prefix_bytes
                )
            )

    except Exception as exc:
        return URLVerificationResult(
            requested_url=(
                normalized_url
            ),
            success=False,
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

    appears_pdf = (
        detect_pdf(
            content_type=(
                content_type
            ),
            content_prefix=(
                content_prefix
            ),
        )
    )

    appears_html = (
        detect_html(
            content_type=(
                content_type
            ),
            content_prefix=(
                content_prefix
            ),
        )
    )

    return URLVerificationResult(
        requested_url=(
            normalized_url
        ),
        success=True,
        status_code=(
            status_code
        ),
        final_url=(
            final_url
        ),
        content_type=(
            content_type
        ),
        content_length=(
            content_length
        ),
        appears_pdf=(
            appears_pdf
        ),
        appears_html=(
            appears_html
        ),
    )

