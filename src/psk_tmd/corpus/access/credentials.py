import os

from pydantic import (
    BaseModel,
)


# ---------------------------------------------------------------------------
# CREDENTIAL CONFIGURATION
# ---------------------------------------------------------------------------
ELSEVIER_API_KEY_ENV = (
    "ELSEVIER_API_KEY"
)


# ---------------------------------------------------------------------------
# CREDENTIAL READINESS
# ---------------------------------------------------------------------------
class CredentialReadiness(
    BaseModel
):
    credential_name: str

    environment_variable: str

    configured: bool


# ---------------------------------------------------------------------------
# READ ENVIRONMENT SECRET
# ---------------------------------------------------------------------------
def read_environment_secret(
    environment_variable: str,
) -> str | None:
    value = (
        os.getenv(
            environment_variable
        )
    )

    if value is None:
        return None

    normalized = (
        value.strip()
    )

    return (
        normalized
        or None
    )


# ---------------------------------------------------------------------------
# CHECK ELSEVIER API KEY
# ---------------------------------------------------------------------------
def check_elsevier_api_key(
) -> CredentialReadiness:
    api_key = (
        read_environment_secret(
            ELSEVIER_API_KEY_ENV
        )
    )

    return CredentialReadiness(
        credential_name=(
            "Elsevier API key"
        ),
        environment_variable=(
            ELSEVIER_API_KEY_ENV
        ),
        configured=(
            api_key is not None
        ),
    )


# ---------------------------------------------------------------------------
# GET ELSEVIER API KEY
# ---------------------------------------------------------------------------
def get_elsevier_api_key(
) -> str:
    api_key = (
        read_environment_secret(
            ELSEVIER_API_KEY_ENV
        )
    )

    if api_key is None:
        raise RuntimeError(
            "Elsevier API key is not "
            "configured. Set the "
            f"{ELSEVIER_API_KEY_ENV} "
            "environment variable."
        )

    return api_key

