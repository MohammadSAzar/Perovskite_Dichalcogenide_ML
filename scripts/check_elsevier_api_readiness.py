from psk_tmd.corpus.access.credentials import (
    check_elsevier_api_key,
)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    readiness = (
        check_elsevier_api_key()
    )

    print(
        "ELSEVIER API CREDENTIAL READINESS"
    )

    print(
        "=" * 120
    )

    print(
        f"credential="
        f"{readiness.credential_name}"
    )

    print(
        f"environment_variable="
        f"{readiness.environment_variable}"
    )

    print(
        f"configured="
        f"{readiness.configured}"
    )

    print()

    if readiness.configured:
        print(
            "The credential is configured. "
            "The secret value was not printed."
        )

    else:
        print(
            "The credential is not configured. "
            "No live authenticated Elsevier "
            "request should be attempted yet."
        )


if __name__ == "__main__":
    main()

