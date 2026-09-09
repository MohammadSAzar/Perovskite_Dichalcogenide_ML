import json

from datetime import (
    date,
)
from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.policy_evidence import (
    PolicyDecision,
    PolicyEvidenceRecord,
    PolicyProviderType,
    PolicyScope,
)


# ---------------------------------------------------------------------------
# OUTPUT CONFIGURATION
# ---------------------------------------------------------------------------
OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "provider_policy_evidence.json"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "provider_policy_evidence_summary.json"
)


# ---------------------------------------------------------------------------
# OBSERVATION DATE
# ---------------------------------------------------------------------------
OBSERVED_DATE = (
    date(
        2026,
        9,
        9,
    )
)


# ---------------------------------------------------------------------------
# BUILD ELSEVIER EVIDENCE
# ---------------------------------------------------------------------------
def build_elsevier_evidence(
) -> list[
    PolicyEvidenceRecord
]:
    return [
        PolicyEvidenceRecord(
            evidence_id="PEV-000001",
            provider_key="elsevier",
            provider_name="Elsevier",
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
            source_url=(
                "https://www.elsevier.com/"
                "about/policies-and-standards/"
                "text-and-data-mining"
            ),
            observed_date=(
                OBSERVED_DATE
            ),
            basis_text=(
                "Elsevier permits researchers "
                "at subscribing academic "
                "institutions to text and data "
                "mine subscribed ScienceDirect "
                "full-text content for "
                "non-commercial research."
            ),
            conditions=(
                "Subscription access and "
                "non-commercial research "
                "conditions apply. Elsevier's "
                "API is the supported route "
                "for bulk TDM access."
            ),
        ),
        PolicyEvidenceRecord(
            evidence_id="PEV-000002",
            provider_key="elsevier",
            provider_name="Elsevier",
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.AUTOMATED_ACCESS
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
            source_url=(
                "https://www.elsevier.com/"
                "about/policies-and-standards/"
                "text-and-data-mining/license"
            ),
            observed_date=(
                OBSERVED_DATE
            ),
            basis_text=(
                "Elsevier provides automated "
                "TDM access through its API "
                "and states that robots, "
                "spiders, screen-scraping, "
                "and other automated "
                "downloading of Elsevier web "
                "sites are not permitted "
                "under the TDM agreement."
            ),
            conditions=(
                "Use the authorized API route "
                "rather than crawling or "
                "screen-scraping publisher "
                "web pages."
            ),
        ),
        PolicyEvidenceRecord(
            evidence_id="PEV-000003",
            provider_key="elsevier",
            provider_name="Elsevier",
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.LOCAL_COPY
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
            source_url=(
                "https://dev.elsevier.com/"
                "tdm_service.html"
            ),
            observed_date=(
                OBSERVED_DATE
            ),
            basis_text=(
                "Elsevier's TDM provisions "
                "allow a TDM dataset to be "
                "used internally for academic "
                "research, subject to the "
                "applicable TDM terms."
            ),
            conditions=(
                "The licensed dataset is "
                "subject to retention and "
                "use restrictions under "
                "Elsevier's TDM provisions."
            ),
        ),
    ]


# ---------------------------------------------------------------------------
# BUILD MDPI EVIDENCE
# ---------------------------------------------------------------------------
def build_mdpi_evidence(
) -> list[
    PolicyEvidenceRecord
]:
    return [
        PolicyEvidenceRecord(
            evidence_id="PEV-000004",
            provider_key="mdpi",
            provider_name="MDPI",
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.PERMITTED
            ),
            source_url=(
                "https://www.mdpi.com/"
                "about/openaccess"
            ),
            observed_date=(
                OBSERVED_DATE
            ),
            basis_text=(
                "MDPI states that its journal "
                "articles are open access and "
                "may be reused by text-mining "
                "applications free of charge, "
                "provided the source and "
                "original publisher are "
                "properly credited."
            ),
            conditions=(
                "Attribution and the applicable "
                "CC BY license conditions "
                "must be followed."
            ),
        ),
        PolicyEvidenceRecord(
            evidence_id="PEV-000005",
            provider_key="mdpi",
            provider_name="MDPI",
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.LOCAL_COPY
            ),
            decision=(
                PolicyDecision.PERMITTED
            ),
            source_url=(
                "https://www.mdpi.com/"
                "about/termsofuse"
            ),
            observed_date=(
                OBSERVED_DATE
            ),
            basis_text=(
                "MDPI states that articles "
                "are generally distributed "
                "under the Creative Commons "
                "Attribution license, which "
                "permits broad reuse with "
                "appropriate credit."
            ),
            conditions=(
                "Third-party material embedded "
                "within an article may have "
                "different reuse rights."
            ),
        ),
        PolicyEvidenceRecord(
            evidence_id="PEV-000006",
            provider_key="mdpi",
            provider_name="MDPI",
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.AUTOMATED_ACCESS
            ),
            decision=(
                PolicyDecision.UNCLEAR
            ),
            source_url=(
                "https://www.mdpi.com/"
                "about/termsofuse"
            ),
            observed_date=(
                OBSERVED_DATE
            ),
            basis_text=(
                "MDPI's open-access policy "
                "clearly supports text-mining "
                "reuse, but the reviewed Terms "
                "of Use do not provide a clear "
                "provider-level authorization "
                "for unrestricted automated "
                "HTTP retrieval."
            ),
            conditions=(
                "Use a supported API or other "
                "explicitly permitted route "
                "when available. Do not infer "
                "automated retrieval permission "
                "from CC BY alone."
            ),
        ),
    ]


# ---------------------------------------------------------------------------
# BUILD SPRINGER NATURE EVIDENCE
# ---------------------------------------------------------------------------
def build_springer_nature_evidence(
) -> list[
    PolicyEvidenceRecord
]:
    return [
        PolicyEvidenceRecord(
            evidence_id="PEV-000007",
            provider_key=(
                "springer_nature"
            ),
            provider_name=(
                "Springer Nature"
            ),
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
            source_url=(
                "https://www.springernature.com/"
                "de/researchers/"
                "text-and-data-mining"
            ),
            observed_date=(
                OBSERVED_DATE
            ),
            basis_text=(
                "Springer Nature grants "
                "researchers at subscribing "
                "academic institutions TDM "
                "rights for subscribed journals "
                "and books for non-commercial "
                "research."
            ),
            conditions=(
                "Institutional license and "
                "non-commercial research "
                "conditions apply for "
                "subscription content."
            ),
        ),
        PolicyEvidenceRecord(
            evidence_id="PEV-000008",
            provider_key=(
                "springer_nature"
            ),
            provider_name=(
                "Springer Nature"
            ),
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.AUTOMATED_ACCESS
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
            source_url=(
                "https://www.springernature.com/"
                "de/researchers/"
                "text-and-data-mining"
            ),
            observed_date=(
                OBSERVED_DATE
            ),
            basis_text=(
                "Springer Nature permits "
                "researchers to download "
                "content for TDM through "
                "supported platform and API "
                "routes, subject to reasonable "
                "request limits."
            ),
            conditions=(
                "Direct platform downloads "
                "should be limited to a "
                "reasonable rate; Springer "
                "Nature currently describes "
                "approximately one request per "
                "second for individual "
                "researcher downloads."
            ),
        ),
        PolicyEvidenceRecord(
            evidence_id="PEV-000009",
            provider_key=(
                "springer_nature"
            ),
            provider_name=(
                "Springer Nature"
            ),
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.LOCAL_COPY
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
            source_url=(
                "https://www.springernature.com/"
                "de/researchers/"
                "text-and-data-mining"
            ),
            observed_date=(
                OBSERVED_DATE
            ),
            basis_text=(
                "Springer Nature permits "
                "downloaded TDM content to be "
                "stored securely for the "
                "duration of the TDM project."
            ),
            conditions=(
                "Content should be stored on "
                "a secure internal server, "
                "protected from third-party "
                "access, and retained only "
                "for the duration of the "
                "TDM project."
            ),
        ),
    ]


# ---------------------------------------------------------------------------
# BUILD ARXIV EVIDENCE
# ---------------------------------------------------------------------------
def build_arxiv_evidence(
) -> list[
    PolicyEvidenceRecord
]:
    return [
        PolicyEvidenceRecord(
            evidence_id="PEV-000010",
            provider_key="arxiv",
            provider_name="arXiv",
            provider_type=(
                PolicyProviderType.REPOSITORY
            ),
            scope=(
                PolicyScope.AUTOMATED_ACCESS
            ),
            decision=(
                PolicyDecision.UNCLEAR
            ),
            source_url=(
                "https://arxiv.org/"
            ),
            observed_date=(
                OBSERVED_DATE
            ),
            basis_text=(
                "The pilot verified that the "
                "specific arXiv PDF endpoint "
                "is technically reachable, "
                "but no sufficiently specific "
                "current authoritative "
                "automated-access policy was "
                "resolved in this policy pass."
            ),
            conditions=(
                "Do not generalize one "
                "successful PDF request into "
                "permission for bulk automated "
                "retrieval."
            ),
        ),
    ]


# ---------------------------------------------------------------------------
# BUILD ALL POLICY EVIDENCE
# ---------------------------------------------------------------------------
def build_policy_evidence(
) -> list[
    PolicyEvidenceRecord
]:
    return (
        build_elsevier_evidence()
        + build_mdpi_evidence()
        + build_springer_nature_evidence()
        + build_arxiv_evidence()
    )


# ---------------------------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------------------------
def save_json(
    path: Path,
    payload,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    evidence_records = (
        build_policy_evidence()
    )

    payloads = [
        record.model_dump(
            mode="json"
        )
        for record
        in evidence_records
    ]

    provider_counts = {}

    scope_counts = {}

    decision_counts = {}

    for record in evidence_records:
        provider_counts[
            record.provider_key
        ] = (
            provider_counts.get(
                record.provider_key,
                0,
            )
            + 1
        )

        scope_counts[
            record.scope.value
        ] = (
            scope_counts.get(
                record.scope.value,
                0,
            )
            + 1
        )

        decision_counts[
            record.decision.value
        ] = (
            decision_counts.get(
                record.decision.value,
                0,
            )
            + 1
        )

    summary = {
        "evidence_count": (
            len(
                evidence_records
            )
        ),
        "provider_counts": (
            dict(
                sorted(
                    provider_counts.items()
                )
            )
        ),
        "scope_counts": (
            dict(
                sorted(
                    scope_counts.items()
                )
            )
        ),
        "decision_counts": (
            dict(
                sorted(
                    decision_counts.items()
                )
            )
        ),
    }

    save_json(
        OUTPUT_PATH,
        payloads,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT PROVIDER POLICY EVIDENCE"
    )

    print(
        "=" * 120
    )

    print(
        f"evidence_records="
        f"{len(evidence_records)}"
    )

    print()

    print(
        "PROVIDER COUNTS"
    )

    print(
        "-" * 120
    )

    for (
        provider,
        count,
    ) in sorted(
        provider_counts.items()
    ):
        print(
            f"{provider:<25} "
            f"{count}"
        )

    print()

    print(
        "SCOPE COUNTS"
    )

    print(
        "-" * 120
    )

    for (
        scope,
        count,
    ) in sorted(
        scope_counts.items()
    ):
        print(
            f"{scope:<25} "
            f"{count}"
        )

    print()

    print(
        "DECISION COUNTS"
    )

    print(
        "-" * 120
    )

    for (
        decision,
        count,
    ) in sorted(
        decision_counts.items()
    ):
        print(
            f"{decision:<25} "
            f"{count}"
        )

    print()

    print(
        "POLICY EVIDENCE"
    )

    print(
        "-" * 180
    )

    for record in evidence_records:
        print(
            f"{record.evidence_id:<12} "
            f"{record.provider_key:<20} "
            f"scope="
            f"{record.scope.value:<20} "
            f"decision="
            f"{record.decision.value}"
        )

        print(
            f"{'':12}"
            f"url="
            f"{record.source_url}"
        )

        print(
            f"{'':12}"
            f"conditions="
            f"{record.conditions or '-'}"
        )

        print(
            "-" * 180
        )

    print()

    print(
        "SAVED FILES"
    )

    print(
        "-" * 120
    )

    print(
        OUTPUT_PATH.relative_to(
            PROJECT_ROOT
        )
    )

    print(
        SUMMARY_PATH.relative_to(
            PROJECT_ROOT
        )
    )


if __name__ == "__main__":
    main()


