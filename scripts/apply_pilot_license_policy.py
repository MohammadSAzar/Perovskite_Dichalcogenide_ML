import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.evidence import (
    AccessEvidenceRecord,
    AccessEvidenceType,
)
from psk_tmd.corpus.access.license import (
    normalize_license,
)
from psk_tmd.corpus.access.license_policy import (
    build_license_policy_assessment,
)
from psk_tmd.corpus.access.models import (
    TDMStatus,
)
from psk_tmd.corpus.access.policy import (
    AIUseStatus,
)


# ---------------------------------------------------------------------------
# INPUT / OUTPUT CONFIGURATION
# ---------------------------------------------------------------------------
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
    / "openalex_access_evidence.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
)

ASSESSMENTS_PATH = (
    OUTPUT_DIR
    / "license_policy_assessments.json"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "license_policy_summary.json"
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
# LOAD EVIDENCE RECORDS
# ---------------------------------------------------------------------------
def load_evidence_records(
    path: Path,
) -> list[
    AccessEvidenceRecord
]:
    payloads = (
        load_json(
            path
        )
    )

    return [
        AccessEvidenceRecord.model_validate(
            payload
        )
        for payload in payloads
    ]


# ---------------------------------------------------------------------------
# SELECT LICENSE EVIDENCE
# ---------------------------------------------------------------------------
def select_license_evidence(
    evidence_records: list[
        AccessEvidenceRecord
    ],
) -> list[
    AccessEvidenceRecord
]:
    return [
        evidence
        for evidence
        in evidence_records
        if (
            evidence.evidence_type
            == AccessEvidenceType.LICENSE
        )
    ]


# ---------------------------------------------------------------------------
# BUILD POLICY ID
# ---------------------------------------------------------------------------
def build_policy_id(
    index: int,
) -> str:
    if index < 1:
        raise ValueError(
            "Policy index must be "
            "at least 1."
        )

    return (
        f"POL-"
        f"{index:06d}"
    )


# ---------------------------------------------------------------------------
# BUILD ASSESSMENT RECORD
# ---------------------------------------------------------------------------
def build_assessment_record(
    evidence: AccessEvidenceRecord,
    *,
    policy_id: str,
) -> dict:
    normalized_license = (
        normalize_license(
            evidence.value
        )
    )

    assessment = (
        build_license_policy_assessment(
            policy_id=(
                policy_id
            ),
            access_id=(
                evidence.access_id
            ),
            candidate_id=(
                evidence.candidate_id
            ),
            license_value=(
                normalized_license
            ),
            policy_url=None,
        )
    )

    return {
        "policy_id": (
            assessment.policy_id
        ),
        "access_id": (
            assessment.access_id
        ),
        "candidate_id": (
            assessment.candidate_id
        ),
        "source_evidence_id": (
            evidence.evidence_id
        ),
        "source": (
            evidence.source.value
        ),
        "source_name": (
            evidence.source_name
        ),
        "source_url": (
            evidence.source_url
        ),
        "raw_license": (
            evidence.value
        ),
        "normalized_license_type": (
            normalized_license
            .license_type
            .value
        ),
        "normalized_license_name": (
            normalized_license
            .normalized_name
        ),
        "license_version": (
            normalized_license
            .version
        ),
        "tdm_status": (
            assessment.tdm_status.value
        ),
        "ai_use_status": (
            assessment.ai_use_status.value
        ),
        "basis_type": (
            assessment.basis_type.value
        ),
        "policy_url": (
            assessment.policy_url
        ),
        "basis_text": (
            assessment.basis_text
        ),
        "automated_access_permitted": (
            assessment
            .automated_access_permitted
        ),
        "local_copy_permitted": (
            assessment
            .local_copy_permitted
        ),
        "redistribution_permitted": (
            assessment
            .redistribution_permitted
        ),
        "notes": (
            assessment.notes
        ),
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    evidence_records = (
        load_evidence_records(
            INPUT_PATH
        )
    )

    license_evidence = (
        select_license_evidence(
            evidence_records
        )
    )

    assessment_records = []

    for (
        index,
        evidence,
    ) in enumerate(
        license_evidence,
        start=1,
    ):
        assessment_records.append(
            build_assessment_record(
                evidence,
                policy_id=(
                    build_policy_id(
                        index
                    )
                ),
            )
        )

    license_type_counts = {}

    tdm_status_counts = {}

    ai_use_status_counts = {}

    automated_access_counts = {
        "true": 0,
        "false": 0,
        "unknown": 0,
    }

    local_copy_counts = {
        "true": 0,
        "false": 0,
        "unknown": 0,
    }

    redistribution_counts = {
        "true": 0,
        "false": 0,
        "unknown": 0,
    }

    for record in assessment_records:
        license_type = (
            record[
                "normalized_license_type"
            ]
        )

        license_type_counts[
            license_type
        ] = (
            license_type_counts.get(
                license_type,
                0,
            )
            + 1
        )

        tdm_status = (
            record[
                "tdm_status"
            ]
        )

        tdm_status_counts[
            tdm_status
        ] = (
            tdm_status_counts.get(
                tdm_status,
                0,
            )
            + 1
        )

        ai_use_status = (
            record[
                "ai_use_status"
            ]
        )

        ai_use_status_counts[
            ai_use_status
        ] = (
            ai_use_status_counts.get(
                ai_use_status,
                0,
            )
            + 1
        )

        automated_value = (
            record[
                "automated_access_permitted"
            ]
        )

        if automated_value is True:
            automated_access_counts[
                "true"
            ] += 1

        elif automated_value is False:
            automated_access_counts[
                "false"
            ] += 1

        else:
            automated_access_counts[
                "unknown"
            ] += 1

        local_copy_value = (
            record[
                "local_copy_permitted"
            ]
        )

        if local_copy_value is True:
            local_copy_counts[
                "true"
            ] += 1

        elif local_copy_value is False:
            local_copy_counts[
                "false"
            ] += 1

        else:
            local_copy_counts[
                "unknown"
            ] += 1

        redistribution_value = (
            record[
                "redistribution_permitted"
            ]
        )

        if redistribution_value is True:
            redistribution_counts[
                "true"
            ] += 1

        elif redistribution_value is False:
            redistribution_counts[
                "false"
            ] += 1

        else:
            redistribution_counts[
                "unknown"
            ] += 1

    summary = {
        "input_evidence_count": (
            len(
                evidence_records
            )
        ),
        "license_evidence_count": (
            len(
                license_evidence
            )
        ),
        "assessment_count": (
            len(
                assessment_records
            )
        ),
        "license_type_counts": (
            dict(
                sorted(
                    license_type_counts.items()
                )
            )
        ),
        "tdm_status_counts": (
            dict(
                sorted(
                    tdm_status_counts.items()
                )
            )
        ),
        "ai_use_status_counts": (
            dict(
                sorted(
                    ai_use_status_counts.items()
                )
            )
        ),
        "automated_access_counts": (
            automated_access_counts
        ),
        "local_copy_counts": (
            local_copy_counts
        ),
        "redistribution_counts": (
            redistribution_counts
        ),
    }

    save_json(
        ASSESSMENTS_PATH,
        assessment_records,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT LICENSE POLICY ASSESSMENT"
    )
    print(
        "=" * 120
    )

    print(
        f"input_evidence="
        f"{len(evidence_records)}"
    )

    print(
        f"license_evidence="
        f"{len(license_evidence)}"
    )

    print(
        f"assessments="
        f"{len(assessment_records)}"
    )

    print()

    print(
        "LICENSE TYPE COUNTS"
    )
    print(
        "-" * 120
    )

    for (
        license_type,
        count,
    ) in sorted(
        license_type_counts.items()
    ):
        print(
            f"{license_type:<25} "
            f"{count}"
        )

    print()

    print(
        "TDM STATUS COUNTS"
    )
    print(
        "-" * 120
    )

    for (
        status,
        count,
    ) in sorted(
        tdm_status_counts.items()
    ):
        print(
            f"{status:<25} "
            f"{count}"
        )

    print()

    print(
        "AI USE STATUS COUNTS"
    )
    print(
        "-" * 120
    )

    for (
        status,
        count,
    ) in sorted(
        ai_use_status_counts.items()
    ):
        print(
            f"{status:<25} "
            f"{count}"
        )

    print()

    print(
        "PERMISSION COUNTS"
    )
    print(
        "-" * 120
    )

    print(
        "automated_access="
        f"{automated_access_counts}"
    )

    print(
        "local_copy="
        f"{local_copy_counts}"
    )

    print(
        "redistribution="
        f"{redistribution_counts}"
    )

    print()

    print(
        "ASSESSMENTS"
    )
    print(
        "-" * 180
    )

    for record in assessment_records:
        print(
            f"{record['policy_id']:<12} "
            f"{record['access_id']:<12} "
            f"{record['candidate_id']:<12} "
            f"license="
            f"{str(record['normalized_license_name'] or '-'):<18} "
            f"TDM="
            f"{record['tdm_status']:<15}"
        )

        print(
            f"{'':12}"
            f"raw_license="
            f"{record['raw_license'] or '-'}"
        )

        print(
            f"{'':12}"
            f"AI="
            f"{record['ai_use_status']} "
            f"automated="
            f"{record['automated_access_permitted']} "
            f"local_copy="
            f"{record['local_copy_permitted']} "
            f"redistribution="
            f"{record['redistribution_permitted']}"
        )

        print(
            f"{'':12}"
            f"evidence="
            f"{record['source_evidence_id']} "
            f"source="
            f"{record['source']}"
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
        ASSESSMENTS_PATH.relative_to(
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


