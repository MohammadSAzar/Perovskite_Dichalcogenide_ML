import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.acquisition_decision import (
    resolve_acquisition_decision,
)
from psk_tmd.corpus.access.combined_policy import (
    CombinedPolicyResolution,
)
from psk_tmd.corpus.access.models import (
    AcquisitionRoute,
)


# ---------------------------------------------------------------------------
# INPUT / OUTPUT CONFIGURATION
# ---------------------------------------------------------------------------
INPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
)

COMBINED_POLICY_PATH = (
    INPUT_DIR
    / "combined_policy_resolutions.json"
)

OUTPUT_PATH = (
    INPUT_DIR
    / "acquisition_decisions.json"
)

SUMMARY_PATH = (
    INPUT_DIR
    / "acquisition_decision_summary.json"
)


# ---------------------------------------------------------------------------
# LOAD JSON
# ---------------------------------------------------------------------------
def load_json(
    path: Path,
):
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
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
# BUILD POLICY MODEL
# ---------------------------------------------------------------------------
def build_policy_model(
    record: dict,
) -> CombinedPolicyResolution:
    return (
        CombinedPolicyResolution.model_validate(
            {
                "access_id": (
                    record[
                        "access_id"
                    ]
                ),
                "candidate_id": (
                    record[
                        "candidate_id"
                    ]
                ),
                "provider_key": (
                    record.get(
                        "provider_key"
                    )
                ),
                "tdm_status": (
                    record[
                        "tdm_status"
                    ]
                ),
                "automated_access_status": (
                    record[
                        "automated_access_status"
                    ]
                ),
                "local_copy_status": (
                    record[
                        "local_copy_status"
                    ]
                ),
                "redistribution_status": (
                    record[
                        "redistribution_status"
                    ]
                ),
                "ai_use_status": (
                    record[
                        "ai_use_status"
                    ]
                ),
                "license_policy_id": (
                    record.get(
                        "license_policy_id"
                    )
                ),
                "provider_evidence_ids": (
                    record.get(
                        "provider_evidence_ids",
                        [],
                    )
                ),
                "conditions": (
                    record.get(
                        "conditions",
                        [],
                    )
                ),
                "reason": (
                    record[
                        "reason"
                    ]
                ),
            }
        )
    )


# ---------------------------------------------------------------------------
# SELECT SOURCE URL
# ---------------------------------------------------------------------------
def select_source_url(
    record: dict,
) -> str | None:
    final_url = (
        record.get(
            "final_url"
        )
    )

    if final_url:
        return final_url

    requested_url = (
        record.get(
            "requested_url"
        )
    )

    if requested_url:
        return requested_url

    return None


# ---------------------------------------------------------------------------
# BUILD DECISION RECORD
# ---------------------------------------------------------------------------
def build_decision_record(
    record: dict,
) -> dict:
    policy = (
        build_policy_model(
            record
        )
    )

    route = (
        AcquisitionRoute(
            record[
                "proposed_route"
            ]
        )
    )

    source_url = (
        select_source_url(
            record
        )
    )

    decision = (
        resolve_acquisition_decision(
            access_id=(
                record[
                    "access_id"
                ]
            ),
            candidate_id=(
                record[
                    "candidate_id"
                ]
            ),
            route=(
                route
            ),
            source_url=(
                source_url
            ),
            url_verified=bool(
                record.get(
                    "url_verification_success",
                    False,
                )
            ),
            appears_pdf=bool(
                record.get(
                    "appears_pdf",
                    False,
                )
            ),
            policy=(
                policy
            ),
        )
    )

    return {
        "access_id": (
            decision.access_id
        ),
        "candidate_id": (
            decision.candidate_id
        ),
        "doi": (
            record.get(
                "doi"
            )
        ),
        "publisher": (
            record.get(
                "publisher"
            )
        ),
        "provider_key": (
            record.get(
                "provider_key"
            )
        ),
        "decision": (
            decision.decision.value
        ),
        "route": (
            decision.route.value
        ),
        "source_url": (
            decision.source_url
        ),
        "url_verification_success": (
            record.get(
                "url_verification_success"
            )
        ),
        "appears_pdf": (
            record.get(
                "appears_pdf"
            )
        ),
        "appears_html": (
            record.get(
                "appears_html"
            )
        ),
        "tdm_status": (
            record[
                "tdm_status"
            ]
        ),
        "automated_access_status": (
            record[
                "automated_access_status"
            ]
        ),
        "local_copy_status": (
            record[
                "local_copy_status"
            ]
        ),
        "redistribution_status": (
            record[
                "redistribution_status"
            ]
        ),
        "ai_use_status": (
            record[
                "ai_use_status"
            ]
        ),
        "license_policy_id": (
            record.get(
                "license_policy_id"
            )
        ),
        "provider_evidence_ids": (
            record.get(
                "provider_evidence_ids",
                [],
            )
        ),
        "conditions": (
            record.get(
                "conditions",
                [],
            )
        ),
        "reason": (
            decision.reason
        ),
    }


# ---------------------------------------------------------------------------
# COUNT VALUES
# ---------------------------------------------------------------------------
def count_values(
    records: list[
        dict
    ],
    field: str,
) -> dict[
    str,
    int
]:
    counts = {}

    for record in records:
        value = (
            record[
                field
            ]
        )

        counts[
            value
        ] = (
            counts.get(
                value,
                0,
            )
            + 1
        )

    return dict(
        sorted(
            counts.items()
        )
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    combined_records = (
        load_json(
            COMBINED_POLICY_PATH
        )
    )

    decision_records = [
        build_decision_record(
            record
        )
        for record
        in sorted(
            combined_records,
            key=lambda item: (
                item[
                    "access_id"
                ]
            ),
        )
    ]

    auto_acquire_ids = [
        record[
            "access_id"
        ]
        for record
        in decision_records
        if (
            record[
                "decision"
            ]
            == "auto_acquire"
        )
    ]

    manual_review_ids = [
        record[
            "access_id"
        ]
        for record
        in decision_records
        if (
            record[
                "decision"
            ]
            == "manual_review"
        )
    ]

    metadata_only_ids = [
        record[
            "access_id"
        ]
        for record
        in decision_records
        if (
            record[
                "decision"
            ]
            == "metadata_only"
        )
    ]

    summary = {
        "input_record_count": (
            len(
                combined_records
            )
        ),
        "decision_record_count": (
            len(
                decision_records
            )
        ),
        "decision_counts": (
            count_values(
                decision_records,
                "decision",
            )
        ),
        "route_counts": (
            count_values(
                decision_records,
                "route",
            )
        ),
        "provider_counts": (
            count_values(
                decision_records,
                "provider_key",
            )
        ),
        "auto_acquire_access_ids": (
            auto_acquire_ids
        ),
        "manual_review_access_ids": (
            manual_review_ids
        ),
        "metadata_only_access_ids": (
            metadata_only_ids
        ),
    }

    save_json(
        OUTPUT_PATH,
        decision_records,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT ACQUISITION DECISIONS"
    )

    print(
        "=" * 120
    )

    print(
        f"input_records="
        f"{len(combined_records)}"
    )

    print(
        f"decisions="
        f"{len(decision_records)}"
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
    ) in count_values(
        decision_records,
        "decision",
    ).items():
        print(
            f"{decision:<25} "
            f"{count}"
        )

    print()

    print(
        "ROUTE COUNTS"
    )

    print(
        "-" * 120
    )

    for (
        route,
        count,
    ) in count_values(
        decision_records,
        "route",
    ).items():
        print(
            f"{route:<25} "
            f"{count}"
        )

    print()

    print(
        "DECISIONS"
    )

    print(
        "-" * 180
    )

    for record in decision_records:
        print(
            f"{record['access_id']:<12} "
            f"{record['candidate_id']:<12} "
            f"decision="
            f"{record['decision']:<16} "
            f"provider="
            f"{str(record['provider_key'] or '-'):<18}"
        )

        print(
            f"{'':12}"
            f"route="
            f"{record['route']:<22} "
            f"verified="
            f"{record['url_verification_success']} "
            f"pdf="
            f"{record['appears_pdf']} "
            f"html="
            f"{record['appears_html']}"
        )

        print(
            f"{'':12}"
            f"TDM="
            f"{record['tdm_status']:<15} "
            f"automated="
            f"{record['automated_access_status']:<15} "
            f"local_copy="
            f"{record['local_copy_status']}"
        )

        print(
            f"{'':12}"
            f"source="
            f"{record['source_url'] or '-'}"
        )

        print(
            f"{'':12}"
            f"reason="
            f"{record['reason']}"
        )

        print(
            "-" * 180
        )

    print()

    print(
        "AUTO ACQUIRE IDS"
    )

    print(
        "-" * 120
    )

    if auto_acquire_ids:
        for access_id in auto_acquire_ids:
            print(
                access_id
            )

    else:
        print(
            "none"
        )

    print()

    print(
        "MANUAL REVIEW IDS"
    )

    print(
        "-" * 120
    )

    if manual_review_ids:
        for access_id in manual_review_ids:
            print(
                access_id
            )

    else:
        print(
            "none"
        )

    print()

    print(
        "METADATA ONLY IDS"
    )

    print(
        "-" * 120
    )

    if metadata_only_ids:
        for access_id in metadata_only_ids:
            print(
                access_id
            )

    else:
        print(
            "none"
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

