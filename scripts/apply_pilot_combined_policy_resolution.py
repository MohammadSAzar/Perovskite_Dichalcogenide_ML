import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.combined_policy import (
    build_combined_policy_resolution,
)
from psk_tmd.corpus.access.policy import (
    TDMPolicyAssessment,
)
from psk_tmd.corpus.access.policy_evidence import (
    PolicyEvidenceRecord,
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

PROVIDER_IDENTIFICATIONS_PATH = (
    INPUT_DIR
    / "provider_identifications.json"
)

LICENSE_POLICY_PATH = (
    INPUT_DIR
    / "license_policy_assessments.json"
)

PROVIDER_POLICY_EVIDENCE_PATH = (
    INPUT_DIR
    / "provider_policy_evidence.json"
)

OUTPUT_PATH = (
    INPUT_DIR
    / "combined_policy_resolutions.json"
)

SUMMARY_PATH = (
    INPUT_DIR
    / "combined_policy_resolution_summary.json"
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
# INDEX LICENSE ASSESSMENTS
# ---------------------------------------------------------------------------
def index_license_assessments(
    records: list[
        dict
    ],
) -> dict[
    str,
    TDMPolicyAssessment,
]:
    index = {}

    for record in records:
        access_id = (
            record[
                "access_id"
            ]
        )

        if access_id in index:
            raise ValueError(
                "Duplicate license policy "
                "assessment for "
                f"{access_id}."
            )

        assessment_payload = {
            "policy_id": (
                record[
                    "policy_id"
                ]
            ),
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
            "tdm_status": (
                record[
                    "tdm_status"
                ]
            ),
            "ai_use_status": (
                record[
                    "ai_use_status"
                ]
            ),
            "basis_type": (
                record[
                    "basis_type"
                ]
            ),
            "license_name": (
                record.get(
                    "normalized_license_name"
                )
                or record.get(
                    "raw_license"
                )
            ),
            "policy_url": (
                record.get(
                    "policy_url"
                )
            ),
            "basis_text": (
                record.get(
                    "basis_text"
                )
            ),
            "automated_access_permitted": (
                record.get(
                    "automated_access_permitted"
                )
            ),
            "local_copy_permitted": (
                record.get(
                    "local_copy_permitted"
                )
            ),
            "redistribution_permitted": (
                record.get(
                    "redistribution_permitted"
                )
            ),
            "notes": (
                record.get(
                    "notes"
                )
            ),
        }

        index[
            access_id
        ] = (
            TDMPolicyAssessment.model_validate(
                assessment_payload
            )
        )

    return index


# ---------------------------------------------------------------------------
# GROUP PROVIDER EVIDENCE
# ---------------------------------------------------------------------------
def group_provider_evidence(
    records: list[
        dict
    ],
) -> dict[
    str,
    list[
        PolicyEvidenceRecord
    ],
]:
    grouped = {}

    for record in records:
        evidence = (
            PolicyEvidenceRecord.model_validate(
                record
            )
        )

        grouped.setdefault(
            evidence.provider_key,
            [],
        ).append(
            evidence
        )

    return grouped


# ---------------------------------------------------------------------------
# BUILD COMBINED RECORD
# ---------------------------------------------------------------------------
def build_combined_record(
    provider_record: dict,
    *,
    license_assessment: (
        TDMPolicyAssessment
        | None
    ),
    provider_evidence: list[
        PolicyEvidenceRecord
    ],
) -> dict:
    resolution = (
        build_combined_policy_resolution(
            access_id=(
                provider_record[
                    "access_id"
                ]
            ),
            candidate_id=(
                provider_record[
                    "candidate_id"
                ]
            ),
            provider_key=(
                provider_record.get(
                    "provider_key"
                )
            ),
            license_assessment=(
                license_assessment
            ),
            provider_evidence_records=(
                provider_evidence
            ),
        )
    )

    return {
        "access_id": (
            resolution.access_id
        ),
        "candidate_id": (
            resolution.candidate_id
        ),
        "doi": (
            provider_record.get(
                "doi"
            )
        ),
        "publisher": (
            provider_record.get(
                "publisher"
            )
        ),
        "provider_key": (
            resolution.provider_key
        ),
        "provider_name": (
            provider_record.get(
                "provider_name"
            )
        ),
        "provider_type": (
            provider_record.get(
                "provider_type"
            )
        ),
        "proposed_route": (
            provider_record.get(
                "proposed_route"
            )
        ),
        "requested_url": (
            provider_record.get(
                "requested_url"
            )
        ),
        "final_url": (
            provider_record.get(
                "final_url"
            )
        ),
        "url_verification_success": (
            provider_record.get(
                "url_verification_success"
            )
        ),
        "appears_pdf": (
            provider_record.get(
                "appears_pdf"
            )
        ),
        "appears_html": (
            provider_record.get(
                "appears_html"
            )
        ),
        "tdm_status": (
            resolution.tdm_status.value
        ),
        "automated_access_status": (
            resolution
            .automated_access_status
            .value
        ),
        "local_copy_status": (
            resolution
            .local_copy_status
            .value
        ),
        "redistribution_status": (
            resolution
            .redistribution_status
            .value
        ),
        "ai_use_status": (
            resolution.ai_use_status.value
        ),
        "license_policy_id": (
            resolution.license_policy_id
        ),
        "provider_evidence_ids": (
            resolution
            .provider_evidence_ids
        ),
        "conditions": (
            resolution.conditions
        ),
        "reason": (
            resolution.reason
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
    provider_records = (
        load_json(
            PROVIDER_IDENTIFICATIONS_PATH
        )
    )

    license_records = (
        load_json(
            LICENSE_POLICY_PATH
        )
    )

    provider_evidence_records = (
        load_json(
            PROVIDER_POLICY_EVIDENCE_PATH
        )
    )

    license_index = (
        index_license_assessments(
            license_records
        )
    )

    provider_evidence_index = (
        group_provider_evidence(
            provider_evidence_records
        )
    )

    combined_records = []

    for provider_record in sorted(
        provider_records,
        key=lambda record: (
            record[
                "access_id"
            ]
        ),
    ):
        access_id = (
            provider_record[
                "access_id"
            ]
        )

        provider_key = (
            provider_record.get(
                "provider_key"
            )
        )

        license_assessment = (
            license_index.get(
                access_id
            )
        )

        provider_evidence = (
            provider_evidence_index.get(
                provider_key,
                [],
            )
            if provider_key
            is not None
            else []
        )

        combined_records.append(
            build_combined_record(
                provider_record,
                license_assessment=(
                    license_assessment
                ),
                provider_evidence=(
                    provider_evidence
                ),
            )
        )

    summary = {
        "provider_record_count": (
            len(
                provider_records
            )
        ),
        "license_assessment_count": (
            len(
                license_records
            )
        ),
        "provider_policy_evidence_count": (
            len(
                provider_evidence_records
            )
        ),
        "combined_resolution_count": (
            len(
                combined_records
            )
        ),
        "tdm_status_counts": (
            count_values(
                combined_records,
                "tdm_status",
            )
        ),
        "automated_access_status_counts": (
            count_values(
                combined_records,
                "automated_access_status",
            )
        ),
        "local_copy_status_counts": (
            count_values(
                combined_records,
                "local_copy_status",
            )
        ),
        "redistribution_status_counts": (
            count_values(
                combined_records,
                "redistribution_status",
            )
        ),
        "ai_use_status_counts": (
            count_values(
                combined_records,
                "ai_use_status",
            )
        ),
    }

    save_json(
        OUTPUT_PATH,
        combined_records,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT COMBINED POLICY RESOLUTION"
    )

    print(
        "=" * 120
    )

    print(
        f"provider_records="
        f"{len(provider_records)}"
    )

    print(
        f"license_assessments="
        f"{len(license_records)}"
    )

    print(
        f"provider_policy_evidence="
        f"{len(provider_evidence_records)}"
    )

    print(
        f"combined_resolutions="
        f"{len(combined_records)}"
    )

    print()

    status_fields = (
        (
            "TDM STATUS COUNTS",
            "tdm_status",
        ),
        (
            "AUTOMATED ACCESS STATUS COUNTS",
            "automated_access_status",
        ),
        (
            "LOCAL COPY STATUS COUNTS",
            "local_copy_status",
        ),
        (
            "REDISTRIBUTION STATUS COUNTS",
            "redistribution_status",
        ),
        (
            "AI USE STATUS COUNTS",
            "ai_use_status",
        ),
    )

    for (
        title,
        field,
    ) in status_fields:
        print(
            title
        )

        print(
            "-" * 120
        )

        counts = (
            count_values(
                combined_records,
                field,
            )
        )

        for (
            status,
            count,
        ) in counts.items():
            print(
                f"{status:<25} "
                f"{count}"
            )

        print()

    print(
        "COMBINED RESOLUTIONS"
    )

    print(
        "-" * 180
    )

    for record in combined_records:
        print(
            f"{record['access_id']:<12} "
            f"{record['candidate_id']:<12} "
            f"provider="
            f"{str(record['provider_key'] or '-'):<18} "
            f"TDM="
            f"{record['tdm_status']:<15}"
        )

        print(
            f"{'':12}"
            f"automated="
            f"{record['automated_access_status']:<15} "
            f"local_copy="
            f"{record['local_copy_status']:<15} "
            f"redistribution="
            f"{record['redistribution_status']:<15} "
            f"AI="
            f"{record['ai_use_status']}"
        )

        print(
            f"{'':12}"
            f"license_policy="
            f"{record['license_policy_id'] or '-'}"
        )

        print(
            f"{'':12}"
            f"provider_evidence="
            f"{record['provider_evidence_ids']}"
        )

        print(
            f"{'':12}"
            f"verified="
            f"{record['url_verification_success']} "
            f"pdf="
            f"{record['appears_pdf']} "
            f"html="
            f"{record['appears_html']}"
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

