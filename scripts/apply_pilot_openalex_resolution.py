import json

from pathlib import (
    Path,
)

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.corpus.access.evidence import (
    AccessEvidenceRecord,
)
from psk_tmd.corpus.access.models import (
    AccessRecord,
    AccessStatus,
)
from psk_tmd.corpus.access.openalex_resolution import (
    propose_openalex_resolution,
)


# ---------------------------------------------------------------------------
# INPUT / OUTPUT CONFIGURATION
# ---------------------------------------------------------------------------
ACCESS_RECORDS_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "access"
    / "pilot_v0_1"
    / "initial_access_records.json"
)

EVIDENCE_PATH = (
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

RESOLUTION_PATH = (
    OUTPUT_DIR
    / "openalex_access_resolutions.json"
)

REVIEW_QUEUE_PATH = (
    OUTPUT_DIR
    / "openalex_access_review_queue.json"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "openalex_resolution_summary.json"
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
# LOAD ACCESS RECORDS
# ---------------------------------------------------------------------------
def load_access_records(
    path: Path,
) -> list[
    AccessRecord
]:
    payloads = (
        load_json(
            path
        )
    )

    return [
        AccessRecord.model_validate(
            payload
        )
        for payload in payloads
    ]


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
# GROUP EVIDENCE BY ACCESS ID
# ---------------------------------------------------------------------------
def group_evidence_by_access_id(
    evidence_records: list[
        AccessEvidenceRecord
    ],
) -> dict[
    str,
    list[
        AccessEvidenceRecord
    ],
]:
    grouped = {}

    for evidence in evidence_records:
        grouped.setdefault(
            evidence.access_id,
            [],
        ).append(
            evidence
        )

    return grouped


# ---------------------------------------------------------------------------
# BUILD ACCESS RECORD LOOKUP
# ---------------------------------------------------------------------------
def build_access_record_lookup(
    access_records: list[
        AccessRecord
    ],
) -> dict[
    str,
    AccessRecord
]:
    lookup = {}

    for access_record in access_records:
        if (
            access_record.access_id
            in lookup
        ):
            raise ValueError(
                "Duplicate access_id "
                "in initial access records: "
                f"{access_record.access_id}"
            )

        lookup[
            access_record.access_id
        ] = (
            access_record
        )

    return lookup


# ---------------------------------------------------------------------------
# VALIDATE EVIDENCE ACCESS IDS
# ---------------------------------------------------------------------------
def validate_evidence_access_ids(
    access_record_lookup: dict[
        str,
        AccessRecord
    ],
    evidence_records: list[
        AccessEvidenceRecord
    ],
) -> None:
    unknown_access_ids = sorted(
        {
            evidence.access_id
            for evidence in evidence_records
            if (
                evidence.access_id
                not in access_record_lookup
            )
        }
    )

    if unknown_access_ids:
        raise ValueError(
            "Evidence references unknown "
            "access IDs: "
            f"{unknown_access_ids}"
        )


# ---------------------------------------------------------------------------
# BUILD REVIEW QUEUE ITEM
# ---------------------------------------------------------------------------
def build_review_queue_item(
    access_record: AccessRecord,
    resolution,
    evidence_records: list[
        AccessEvidenceRecord
    ],
) -> dict:
    oa_status = None
    license_value = None
    full_text_location = None
    version = None

    for evidence in evidence_records:
        evidence_type = (
            evidence.evidence_type.value
        )

        if (
            evidence_type
            == "oa_status"
        ):
            oa_status = (
                evidence.value
            )

        elif (
            evidence_type
            == "license"
        ):
            license_value = (
                evidence.value
            )

        elif (
            evidence_type
            == "full_text_location"
        ):
            full_text_location = (
                evidence.source_url
            )

        elif (
            evidence_type
            == "version"
        ):
            version = (
                evidence.value
            )

    return {
        "access_id": (
            access_record.access_id
        ),
        "candidate_id": (
            access_record.candidate_id
        ),
        "doi": (
            access_record.doi
        ),
        "publisher": (
            access_record.publisher
        ),
        "discovery_is_open_access": (
            access_record.is_open_access
        ),
        "openalex_oa_status": (
            oa_status
        ),
        "openalex_license": (
            license_value
        ),
        "openalex_full_text_location": (
            full_text_location
        ),
        "openalex_version": (
            version
        ),
        "proposed_access_status": (
            resolution
            .proposed_access_status
            .value
        ),
        "proposed_acquisition_route": (
            resolution
            .proposed_acquisition_route
            .value
        ),
        "proposed_tdm_status": (
            resolution
            .proposed_tdm_status
            .value
        ),
        "reason": (
            resolution.reason
        ),
        "evidence_ids": list(
            resolution.evidence_ids
        ),
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    access_records = (
        load_access_records(
            ACCESS_RECORDS_PATH
        )
    )

    evidence_records = (
        load_evidence_records(
            EVIDENCE_PATH
        )
    )

    access_record_lookup = (
        build_access_record_lookup(
            access_records
        )
    )

    validate_evidence_access_ids(
        access_record_lookup,
        evidence_records,
    )

    evidence_by_access_id = (
        group_evidence_by_access_id(
            evidence_records
        )
    )

    resolutions = []

    review_queue = []

    status_counts = {}

    route_counts = {}

    tdm_counts = {}

    no_evidence_count = 0

    for access_record in access_records:
        record_evidence = (
            evidence_by_access_id.get(
                access_record.access_id,
                [],
            )
        )

        if not record_evidence:
            no_evidence_count += 1

        resolution = (
            propose_openalex_resolution(
                access_record,
                record_evidence,
            )
        )

        resolutions.append(
            resolution
        )

        status_value = (
            resolution
            .proposed_access_status
            .value
        )

        route_value = (
            resolution
            .proposed_acquisition_route
            .value
        )

        tdm_value = (
            resolution
            .proposed_tdm_status
            .value
        )

        status_counts[
            status_value
        ] = (
            status_counts.get(
                status_value,
                0,
            )
            + 1
        )

        route_counts[
            route_value
        ] = (
            route_counts.get(
                route_value,
                0,
            )
            + 1
        )

        tdm_counts[
            tdm_value
        ] = (
            tdm_counts.get(
                tdm_value,
                0,
            )
            + 1
        )

        if (
            resolution.proposed_access_status
            == AccessStatus.REQUIRES_REVIEW
        ):
            review_queue.append(
                build_review_queue_item(
                    access_record,
                    resolution,
                    record_evidence,
                )
            )

    resolution_payload = [
        resolution.model_dump(
            mode="json"
        )
        for resolution in resolutions
    ]

    summary = {
        "access_record_count": (
            len(
                access_records
            )
        ),
        "evidence_record_count": (
            len(
                evidence_records
            )
        ),
        "resolution_count": (
            len(
                resolutions
            )
        ),
        "review_queue_count": (
            len(
                review_queue
            )
        ),
        "no_evidence_count": (
            no_evidence_count
        ),
        "status_counts": (
            dict(
                sorted(
                    status_counts.items()
                )
            )
        ),
        "acquisition_route_counts": (
            dict(
                sorted(
                    route_counts.items()
                )
            )
        ),
        "tdm_status_counts": (
            dict(
                sorted(
                    tdm_counts.items()
                )
            )
        ),
    }

    save_json(
        RESOLUTION_PATH,
        resolution_payload,
    )

    save_json(
        REVIEW_QUEUE_PATH,
        review_queue,
    )

    save_json(
        SUMMARY_PATH,
        summary,
    )

    print(
        "PILOT OPENALEX ACCESS RESOLUTION"
    )
    print(
        "=" * 120
    )

    print(
        f"access_records="
        f"{len(access_records)}"
    )

    print(
        f"evidence_records="
        f"{len(evidence_records)}"
    )

    print(
        f"resolutions="
        f"{len(resolutions)}"
    )

    print(
        f"review_queue="
        f"{len(review_queue)}"
    )

    print(
        f"no_evidence="
        f"{no_evidence_count}"
    )

    print()

    print(
        "ACCESS STATUS COUNTS"
    )
    print(
        "-" * 120
    )

    for (
        status,
        count,
    ) in sorted(
        status_counts.items()
    ):
        print(
            f"{status:<25} "
            f"{count}"
        )

    print()

    print(
        "ACQUISITION ROUTE COUNTS"
    )
    print(
        "-" * 120
    )

    for (
        route,
        count,
    ) in sorted(
        route_counts.items()
    ):
        print(
            f"{route:<25} "
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
        tdm_counts.items()
    ):
        print(
            f"{status:<25} "
            f"{count}"
        )

    print()

    print(
        "REVIEW QUEUE"
    )
    print(
        "-" * 180
    )

    if not review_queue:
        print(
            "None"
        )

    for item in review_queue:
        print(
            f"{item['access_id']:<12} "
            f"{item['candidate_id']:<12} "
            f"OA={str(item['openalex_oa_status'] or '-'):<10} "
            f"license={str(item['openalex_license'] or '-'):<15} "
            f"{item['doi'] or '-'}"
        )

        print(
            f"{'':12}"
            f"publisher="
            f"{item['publisher'] or '-'}"
        )

        print(
            f"{'':12}"
            f"version="
            f"{item['openalex_version'] or '-'}"
        )

        print(
            f"{'':12}"
            f"location="
            f"{item['openalex_full_text_location'] or '-'}"
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
        RESOLUTION_PATH.relative_to(
            PROJECT_ROOT
        )
    )

    print(
        REVIEW_QUEUE_PATH.relative_to(
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

