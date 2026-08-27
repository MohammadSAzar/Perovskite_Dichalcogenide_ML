import pytest

from psk_tmd.common.constants import (
    BandClaimContext,
)
from psk_tmd.corpus.band_claim_context import (
    classify_band_claim_context,
)


# ---------------------------------------------------------------------------
# CURRENT WORK THIS STUDY
# ---------------------------------------------------------------------------
def test_current_work_this_study():
    text = (
        "In this study, the band gap "
        "was determined to be 2.35 eV."
    )

    result = (
        classify_band_claim_context(
            text
        )
    )

    assert (
        result
        == BandClaimContext.CURRENT_WORK
    )


# ---------------------------------------------------------------------------
# CURRENT WORK WE DETERMINED
# ---------------------------------------------------------------------------
def test_current_work_we_determined():
    text = (
        "We determined the band gap "
        "of CaTiO3 to be 3.20 eV."
    )

    result = (
        classify_band_claim_context(
            text
        )
    )

    assert (
        result
        == BandClaimContext.CURRENT_WORK
    )


# ---------------------------------------------------------------------------
# CURRENT WORK OUR RESULTS
# ---------------------------------------------------------------------------
def test_current_work_our_results():
    text = (
        "Our results indicate a "
        "direct band gap of 2.10 eV."
    )

    result = (
        classify_band_claim_context(
            text
        )
    )

    assert (
        result
        == BandClaimContext.CURRENT_WORK
    )


# ---------------------------------------------------------------------------
# PRIOR LITERATURE PREVIOUSLY REPORTED
# ---------------------------------------------------------------------------
def test_prior_literature_previously_reported():
    text = (
        "The band gap was previously "
        "reported as 2.15 eV."
    )

    result = (
        classify_band_claim_context(
            text
        )
    )

    assert (
        result
        == (
            BandClaimContext
            .PRIOR_LITERATURE
        )
    )


# ---------------------------------------------------------------------------
# PRIOR LITERATURE PREVIOUS STUDIES
# ---------------------------------------------------------------------------
def test_prior_literature_previous_studies():
    text = (
        "Previous studies reported "
        "a band gap of 2.20 eV."
    )

    result = (
        classify_band_claim_context(
            text
        )
    )

    assert (
        result
        == (
            BandClaimContext
            .PRIOR_LITERATURE
        )
    )


# ---------------------------------------------------------------------------
# PRIOR LITERATURE REPORTED BY
# ---------------------------------------------------------------------------
def test_prior_literature_reported_by():
    text = (
        "A value of 2.30 eV was "
        "reported by Zhang."
    )

    result = (
        classify_band_claim_context(
            text
        )
    )

    assert (
        result
        == (
            BandClaimContext
            .PRIOR_LITERATURE
        )
    )


# ---------------------------------------------------------------------------
# AMBIGUOUS WITHOUT CONTEXT
# ---------------------------------------------------------------------------
def test_ambiguous_without_context():
    text = (
        "The band gap is 2.40 eV."
    )

    result = (
        classify_band_claim_context(
            text
        )
    )

    assert (
        result
        == BandClaimContext.AMBIGUOUS
    )


# ---------------------------------------------------------------------------
# AMBIGUOUS CONFLICTING CONTEXT
# ---------------------------------------------------------------------------
def test_ambiguous_conflicting_context():
    text = (
        "Previous studies reported "
        "2.10 eV, while in this study "
        "we measured 2.35 eV."
    )

    result = (
        classify_band_claim_context(
            text
        )
    )

    assert (
        result
        == BandClaimContext.AMBIGUOUS
    )


# ---------------------------------------------------------------------------
# EMPTY TEXT IS AMBIGUOUS
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text",
    [
        "",
        " ",
        "\n",
    ],
)
def test_empty_text_is_ambiguous(
    text: str,
):
    result = (
        classify_band_claim_context(
            text
        )
    )

    assert (
        result
        == BandClaimContext.AMBIGUOUS
    )

