from urllib.parse import (
    quote,
    urlencode,
)

from pydantic import (
    BaseModel,
    field_validator,
)

from psk_tmd.common.text_utils import (
    normalize_whitespace,
)


# ---------------------------------------------------------------------------
# API CONFIGURATION
# ---------------------------------------------------------------------------
ELSEVIER_API_BASE_URL = (
    "https://api.elsevier.com"
)

ELSEVIER_ARTICLE_DOI_PATH = (
    "/content/article/doi/{doi}"
)

ELSEVIER_API_KEY_HEADER = (
    "X-ELS-APIKey"
)

ELSEVIER_DEFAULT_ACCEPT = (
    "text/xml"
)


# ---------------------------------------------------------------------------
# ELSEVIER ARTICLE API REQUEST
# ---------------------------------------------------------------------------
class ElsevierArticleAPIRequest(
    BaseModel
):
    doi: str

    endpoint_url: str

    accept: str = (
        ELSEVIER_DEFAULT_ACCEPT
    )

    view: str = "FULL"

    requires_api_key: bool = True

    api_key_header: str = (
        ELSEVIER_API_KEY_HEADER
    )

    requires_entitlement_check: bool = True

    @field_validator(
        "doi",
        "endpoint_url",
        "accept",
        "view",
        "api_key_header",
    )
    @classmethod
    def validate_required_text(
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
                "Required Elsevier API "
                "request field must not "
                "be empty."
            )

        return normalized


# ---------------------------------------------------------------------------
# NORMALIZE DOI
# ---------------------------------------------------------------------------
def normalize_elsevier_doi(
    doi: str,
) -> str:
    normalized = (
        normalize_whitespace(
            doi
        )
        .strip()
    )

    lowered = (
        normalized.lower()
    )

    prefixes = (
        "https://doi.org/",
        "http://doi.org/",
        "doi:",
    )

    for prefix in prefixes:
        if lowered.startswith(
            prefix
        ):
            normalized = (
                normalized[
                    len(
                        prefix
                    ):
                ]
                .strip()
            )

            break

    if not normalized:
        raise ValueError(
            "DOI must not be empty."
        )

    return normalized


# ---------------------------------------------------------------------------
# BUILD ARTICLE DOI ENDPOINT
# ---------------------------------------------------------------------------
def build_elsevier_article_doi_endpoint(
    doi: str,
) -> str:
    normalized_doi = (
        normalize_elsevier_doi(
            doi
        )
    )

    encoded_doi = (
        quote(
            normalized_doi,
            safe="",
        )
    )

    path = (
        ELSEVIER_ARTICLE_DOI_PATH.format(
            doi=encoded_doi
        )
    )

    return (
        f"{ELSEVIER_API_BASE_URL}"
        f"{path}"
    )


# ---------------------------------------------------------------------------
# BUILD FULL-TEXT REQUEST URL
# ---------------------------------------------------------------------------
def build_elsevier_full_text_url(
    doi: str,
) -> str:
    endpoint = (
        build_elsevier_article_doi_endpoint(
            doi
        )
    )

    query = (
        urlencode(
            {
                "view": "FULL",
            }
        )
    )

    return (
        f"{endpoint}?{query}"
    )


# ---------------------------------------------------------------------------
# BUILD ARTICLE API REQUEST
# ---------------------------------------------------------------------------
def build_elsevier_article_api_request(
    doi: str,
) -> ElsevierArticleAPIRequest:
    normalized_doi = (
        normalize_elsevier_doi(
            doi
        )
    )

    return ElsevierArticleAPIRequest(
        doi=(
            normalized_doi
        ),
        endpoint_url=(
            build_elsevier_full_text_url(
                normalized_doi
            )
        ),
        accept=(
            ELSEVIER_DEFAULT_ACCEPT
        ),
        view="FULL",
        requires_api_key=True,
        api_key_header=(
            ELSEVIER_API_KEY_HEADER
        ),
        requires_entitlement_check=True,
    )

