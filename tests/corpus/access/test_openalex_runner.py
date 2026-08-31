from datetime import (
    date,
)

from psk_tmd.corpus.access.evidence import (
    AccessEvidenceRecord,
    AccessEvidenceSource,
    AccessEvidenceType,
)
from psk_tmd.corpus.access.models import (
    AccessRecord,
)
from psk_tmd.corpus.access.openalex_runner import (
    run_openalex_access_lookups,
)


# ---------------------------------------------------------------------------
# MAKE ACCESS RECORD
# ---------------------------------------------------------------------------
def make_access_record(
    access_id: str,
    candidate_id: str,
    doi: str,
) -> AccessRecord:
    return AccessRecord(
        access_id=(
            access_id
        ),
        candidate_id=(
            candidate_id
        ),
        doi=(
            doi
        ),
    )


# ---------------------------------------------------------------------------
# MAKE EVIDENCE
# ---------------------------------------------------------------------------
def make_evidence(
    *,
    evidence_id: str,
    access_id: str,
    candidate_id: str,
) -> AccessEvidenceRecord:
    return AccessEvidenceRecord(
        evidence_id=(
            evidence_id
        ),
        access_id=(
            access_id
        ),
        candidate_id=(
            candidate_id
        ),
        evidence_type=(
            AccessEvidenceType.OA_STATUS
        ),
        source=(
            AccessEvidenceSource.OPENALEX
        ),
        value="gold",
    )


# ---------------------------------------------------------------------------
# ALL CALLS SUCCEED
# ---------------------------------------------------------------------------
def test_all_calls_succeed(
    monkeypatch,
):
    records = [
        make_access_record(
            "ACC-000001",
            "CND-000001",
            "10.1000/one",
        ),
        make_access_record(
            "ACC-000002",
            "CND-000002",
            "10.1000/two",
        ),
    ]

    def fake_resolver(
        access_record,
        *,
        start_index,
        observed_date,
        api_key=None,
        timeout=30.0,
    ):
        return [
            make_evidence(
                evidence_id=(
                    f"AEV-"
                    f"{start_index:06d}"
                ),
                access_id=(
                    access_record.access_id
                ),
                candidate_id=(
                    access_record.candidate_id
                ),
            )
        ]

    monkeypatch.setattr(
        (
            "psk_tmd.corpus.access."
            "openalex_runner."
            "resolve_openalex_evidence"
        ),
        fake_resolver,
    )

    result = (
        run_openalex_access_lookups(
            records,
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
            delay_seconds=0,
        )
    )

    assert (
        result.attempted_calls
        == 2
    )

    assert (
        result.successful_calls
        == 2
    )

    assert (
        result.failed_calls
        == 0
    )

    assert len(
        result.evidence_records
    ) == 2

    assert (
        result.evidence_records[
            0
        ].evidence_id
        == "AEV-000001"
    )

    assert (
        result.evidence_records[
            1
        ].evidence_id
        == "AEV-000002"
    )


# ---------------------------------------------------------------------------
# FAILURE DOES NOT STOP RUN
# ---------------------------------------------------------------------------
def test_failure_does_not_stop_run(
    monkeypatch,
):
    records = [
        make_access_record(
            "ACC-000001",
            "CND-000001",
            "10.1000/one",
        ),
        make_access_record(
            "ACC-000002",
            "CND-000002",
            "10.1000/two",
        ),
    ]

    def fake_resolver(
        access_record,
        *,
        start_index,
        observed_date,
        api_key=None,
        timeout=30.0,
    ):
        if (
            access_record.access_id
            == "ACC-000001"
        ):
            raise RuntimeError(
                "Test failure"
            )

        return [
            make_evidence(
                evidence_id=(
                    f"AEV-"
                    f"{start_index:06d}"
                ),
                access_id=(
                    access_record.access_id
                ),
                candidate_id=(
                    access_record.candidate_id
                ),
            )
        ]

    monkeypatch.setattr(
        (
            "psk_tmd.corpus.access."
            "openalex_runner."
            "resolve_openalex_evidence"
        ),
        fake_resolver,
    )

    result = (
        run_openalex_access_lookups(
            records,
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
            delay_seconds=0,
        )
    )

    assert (
        result.attempted_calls
        == 2
    )

    assert (
        result.successful_calls
        == 1
    )

    assert (
        result.failed_calls
        == 1
    )

    assert len(
        result.evidence_records
    ) == 1

    assert (
        result.call_results[
            0
        ].success
        is False
    )

    assert (
        result.call_results[
            0
        ].error_type
        == "RuntimeError"
    )

    assert (
        result.call_results[
            1
        ].success
        is True
    )


# ---------------------------------------------------------------------------
# INVALID START INDEX
# ---------------------------------------------------------------------------
def test_invalid_start_index():
    try:
        run_openalex_access_lookups(
            [],
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
            start_evidence_index=0,
            delay_seconds=0,
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
# INVALID DELAY
# ---------------------------------------------------------------------------
def test_invalid_delay():
    try:
        run_openalex_access_lookups(
            [],
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
            delay_seconds=-1,
        )

    except ValueError as exc:
        assert (
            "must not be negative"
            in str(
                exc
            )
        )

    else:
        raise AssertionError(
            "Expected ValueError."
        )


# ---------------------------------------------------------------------------
# INVALID TIMEOUT
# ---------------------------------------------------------------------------
def test_invalid_timeout():
    try:
        run_openalex_access_lookups(
            [],
            observed_date=(
                date(
                    2026,
                    8,
                    31,
                )
            ),
            delay_seconds=0,
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

