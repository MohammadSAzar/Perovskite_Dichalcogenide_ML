import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.acquisition_blockers import (
    assess_acquisition_blockers,
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

ACQUISITION_DECISIONS_PATH = (
    INPUT_DIR
    / "acquisition_decisions.json"
)

OUTPUT_PATH = (
    INPUT_DIR
    / "acquisition_blockers.json"
)

SUMMARY_PATH = (
    INPUT_DIR
    / "acquisition_blocker_summary.json"
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
# BUILD BLOCKER RECORD
# ---------------------------------------------------------------------------
def build_blocker_record(
    record: dict,
) -> dict:
    policy = (
        build_policy_model(
            record
        )
    )

    assessment = (
        assess_acquisition_blockers(
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
                AcquisitionRoute(
                    record[
                        "route"
                    ]
                )
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

    blocker_payloads = [
        {
            "blocker_type": (
                blocker
                .blocker_type
                .value
            ),
            "reason": (
                blocker.reason
            ),
        }
        for blocker
        in assessment.blockers
    ]

    return {
        "access_id": (
            assessment.access_id
        ),
        "candidate_id": (
            assessment.candidate_id
        ),
        "doi": (
            record.get(
                "doi"
            )
        ),
        "provider_key": (
            record.get(
                "provider_key"
            )
        ),
        "decision": (
            record[
                "decision"
            ]
        ),
        "route": (
            record[
                "route"
            ]
        ),
        "source_url": (
            record.get(
                "source_url"
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
        "is_blocked": (
            assessment.is_blocked
        ),
        "blocker_count": (
            len(
                assessment.blockers
            )
        ),
        "blockers": (
            blocker_payloads
        ),
    }


# ---------------------------------------------------------------------------
# COUNT BLOCKER TYPES
# ---------------------------------------------------------------------------
def count_blocker_types(
    records: list[
        dict
    ],
) -> dict[
    str,
    int
]:
    counts = {}

    for record in records:
        for blocker in record[
            "blockers"
        ]:
            blocker_type = (
                blocker[
                    "blocker_type"
                ]
            )

            counts[
                blocker_type
            ] = (
                counts.get(
                    blocker_type,
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
# COUNT BLOCKERS BY PROVIDER
# ---------------------------------------------------------------------------
def count_blockers_by_provider(
    records: list[
        dict
    ],
) -> dict[
    str,
    dict[
        str,
        int
    ],
]:
    counts = {}

    for record in records:
        provider_key = (
            record.get(
                "provider_key"
            )
            or "unidentified"
        )

        provider_counts = (
            counts.setdefault(
                provider_key,
                {},
            )
        )

        for blocker in record[
            "blockers"
        ]:
            blocker_type = (
                blocker[
                    "blocker_type"
                ]
            )

            provider_counts[
                blocker_type
            ] = (
                provider_counts.get(
                    blocker_type,
                    0,
                )
                + 1
            )

    return {
        provider: (
            dict(
                sorted(
                    blocker_counts.items()
                )
            )
        )
        for (
            provider,
            blocker_counts,
        )
        in sorted(
            counts.items()
        )
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    decision_records = (
        load_json(
            ACQUISITION_DECISIONS_PATH
        )
    )

    blocker_records = [
        build_blocker_record(
            record
        )
        for record
        in sorted(
            decision_records,
            key=lambda item: (
                item[
                    "access_id"
                ]
            ),
        )
    ]

    blocker_type_counts = (
        count_blocker_types(
            blocker_records
        )
    )

    blocker_counts_by_provider = (
        count_blockers_by_provider(
            blocker_records
        )
    )

    blocked_ids = [
        record[
            "access_id"
        ]
        for record
        in blocker_records
        if record[
            "is_blocked"
        ]
    ]

    ready_ids = [
        record[
            "access_id"
        ]
        for record
        in blocker_records
        if not record[
            "is_blocked"
        ]
    ]

    summary = {
        "input_record_count": (
            len(
                decision_records
            )
        ),
        "blocker_record_count": (
            len(
                blocker_records
            )
        ),
        "blocked_record_count": (
            len(
                blocked_ids
            )
        ),
        "ready_record_count": (
            len(
                ready_ids
            )
        ),
        "blocker_type_counts": (
            blocker_type_counts
        ),
        "blocker_counts_by_provider": (
            blocker_counts_by_provider
        ),
        "blocked_access_ids": (
            blocked_ids
        ),
        "ready_access_ids": (
            ready_ids
        ),
    }

    save_json(
        OUTPUT_PATH,
        blocker_records,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT ACQUISITION BLOCKERS"
    )

    print(
        "=" * 120
    )

    print(
        f"input_records="
        f"{len(decision_records)}"
    )

    print(
        f"blocked="
        f"{len(blocked_ids)}"
    )

    print(
        f"ready="
        f"{len(ready_ids)}"
    )

    print()

    print(
        "BLOCKER TYPE COUNTS"
    )

    print(
        "-" * 120
    )

    for (
        blocker_type,
        count,
    ) in blocker_type_counts.items():
        print(
            f"{blocker_type:<35} "
            f"{count}"
        )

    print()

    print(
        "BLOCKERS BY PROVIDER"
    )

    print(
        "-" * 120
    )

    for (
        provider,
        counts,
    ) in (
        blocker_counts_by_provider.items()
    ):
        print(
            provider
        )

        for (
            blocker_type,
            count,
        ) in counts.items():
            print(
                f"    "
                f"{blocker_type:<31} "
                f"{count}"
            )

    print()

    print(
        "RECORD BLOCKERS"
    )

    print(
        "-" * 180
    )

    for record in blocker_records:
        print(
            f"{record['access_id']:<12} "
            f"{record['candidate_id']:<12} "
            f"provider="
            f"{str(record['provider_key'] or '-'):<18} "
            f"decision="
            f"{record['decision']:<16} "
            f"blockers="
            f"{record['blocker_count']}"
        )

        if record[
            "blockers"
        ]:
            for blocker in record[
                "blockers"
            ]:
                print(
                    f"{'':12}"
                    f"- "
                    f"{blocker['blocker_type']}: "
                    f"{blocker['reason']}"
                )

        else:
            print(
                f"{'':12}"
                f"- none"
            )

        print(
            "-" * 180
        )

    print()

    print(
        "READY ACCESS IDS"
    )

    print(
        "-" * 120
    )

    if ready_ids:
        for access_id in ready_ids:
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

