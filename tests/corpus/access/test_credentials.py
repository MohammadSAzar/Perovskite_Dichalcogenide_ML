import pytest

from psk_tmd.corpus.access.credentials import (
    ELSEVIER_API_KEY_ENV,
    check_elsevier_api_key,
    get_elsevier_api_key,
    read_environment_secret,
)


# ---------------------------------------------------------------------------
# MISSING ENVIRONMENT SECRET
# ---------------------------------------------------------------------------
def test_missing_environment_secret(
    monkeypatch,
):
    monkeypatch.delenv(
        "TEST_SECRET",
        raising=False,
    )

    assert (
        read_environment_secret(
            "TEST_SECRET"
        )
        is None
    )


# ---------------------------------------------------------------------------
# EMPTY ENVIRONMENT SECRET
# ---------------------------------------------------------------------------
def test_empty_environment_secret(
    monkeypatch,
):
    monkeypatch.setenv(
        "TEST_SECRET",
        "   ",
    )

    assert (
        read_environment_secret(
            "TEST_SECRET"
        )
        is None
    )


# ---------------------------------------------------------------------------
# ENVIRONMENT SECRET IS NORMALIZED
# ---------------------------------------------------------------------------
def test_environment_secret_is_normalized(
    monkeypatch,
):
    monkeypatch.setenv(
        "TEST_SECRET",
        "  secret-value  ",
    )

    assert (
        read_environment_secret(
            "TEST_SECRET"
        )
        == "secret-value"
    )


# ---------------------------------------------------------------------------
# ELSEVIER KEY NOT CONFIGURED
# ---------------------------------------------------------------------------
def test_elsevier_key_not_configured(
    monkeypatch,
):
    monkeypatch.delenv(
        ELSEVIER_API_KEY_ENV,
        raising=False,
    )

    result = (
        check_elsevier_api_key()
    )

    assert (
        result.configured
        is False
    )

    assert (
        result.environment_variable
        == ELSEVIER_API_KEY_ENV
    )


# ---------------------------------------------------------------------------
# ELSEVIER KEY CONFIGURED
# ---------------------------------------------------------------------------
def test_elsevier_key_configured(
    monkeypatch,
):
    monkeypatch.setenv(
        ELSEVIER_API_KEY_ENV,
        "dummy-test-key",
    )

    result = (
        check_elsevier_api_key()
    )

    assert (
        result.configured
        is True
    )


# ---------------------------------------------------------------------------
# GET ELSEVIER API KEY
# ---------------------------------------------------------------------------
def test_get_elsevier_api_key(
    monkeypatch,
):
    monkeypatch.setenv(
        ELSEVIER_API_KEY_ENV,
        "dummy-test-key",
    )

    assert (
        get_elsevier_api_key()
        == "dummy-test-key"
    )


# ---------------------------------------------------------------------------
# MISSING ELSEVIER API KEY RAISES
# ---------------------------------------------------------------------------
def test_missing_elsevier_api_key_raises(
    monkeypatch,
):
    monkeypatch.delenv(
        ELSEVIER_API_KEY_ENV,
        raising=False,
    )

    with pytest.raises(
        RuntimeError,
    ):
        get_elsevier_api_key()


