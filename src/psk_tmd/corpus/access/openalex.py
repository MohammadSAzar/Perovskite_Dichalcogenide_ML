import json

from datetime import (
    date,
)
from urllib.parse import (
    quote,
    urlencode,
)
from urllib.request import (
    Request,
    urlopen,
)

from psk_tmd.corpus.access.evidence import (
    AccessEvidenceRecord,
    AccessEvidenceSource,
    AccessEvidenceType,
)
from psk_tmd.corpus.access.models import (
    AccessRecord,
)


# ---------------------------------------------------------------------------
# OPENALEX CONFIGURATION
# ---------------------------------------------------------------------------
OPENALEX_API_URL = (
    "https://api.openalex.org/works"
)

OPENALEX_USER_AGENT = (
    "psk-tmd-ml/0.1"
)


# ---------------------------------------------------------------------------
# BUILD OPENALEX DOI URL
# ---------------------------------------------------------------------------
def build_openalex_doi_url(
    doi: str,
    *,
    api_key: str | None = None,
) -> str:
    normalized_doi = (
        doi
        .strip()
        .lower()
    )

    work_id = (
        "https://doi.org/"
        f"{normalized_doi}"
    )

    url = (
        f"{OPENALEX_API_URL}/"
        f"{quote(work_id, safe='')}"
    )

    if api_key:
        query = urlencode(
            {
                "api_key": api_key,
            }
        )

        url = (
            f"{url}?{query}"
        )

    return url


# ---------------------------------------------------------------------------
# FETCH OPENALEX WORK
# ---------------------------------------------------------------------------
def fetch_openalex_work(
    doi: str,
    *,
    api_key: str | None = None,
    timeout: float = 30.0,
) -> dict:
    if timeout <= 0:
        raise ValueError(
            "OpenAlex timeout "
            "must be greater than zero."
        )

    url = (
        build_openalex_doi_url(
            doi,
            api_key=api_key,
        )
    )

    request = Request(
        url,
        headers={
            "User-Agent": (
                OPENALEX_USER_AGENT
            ),
            "Accept": (
                "application/json"
            ),
        },
    )

    with urlopen(
        request,
        timeout=timeout,
    ) as response:
        payload = (
            response.read()
        )

    return json.loads(
        payload.decode(
            "utf-8"
        )
    )


# ---------------------------------------------------------------------------
# GET OPEN ACCESS
# ---------------------------------------------------------------------------
def get_open_access(
    work: dict,
) -> dict:
    value = work.get(
        "open_access"
    )

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


# ---------------------------------------------------------------------------
# GET BEST OA LOCATION
# ---------------------------------------------------------------------------
def get_best_oa_location(
    work: dict,
) -> dict:
    value = work.get(
        "best_oa_location"
    )

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


# ---------------------------------------------------------------------------
# GET LOCATION SOURCE NAME
# ---------------------------------------------------------------------------
def get_location_source_name(
    location: dict,
) -> str | None:
    source = location.get(
        "source"
    )

    if not isinstance(
        source,
        dict,
    ):
        return None

    value = source.get(
        "display_name"
    )

    if not isinstance(
        value,
        str,
    ):
        return None

    normalized = (
        value.strip()
    )

    return (
        normalized
        or None
    )


# ---------------------------------------------------------------------------
# GET LOCATION URL
# ---------------------------------------------------------------------------
def get_location_url(
    location: dict,
) -> str | None:
    pdf_url = location.get(
        "pdf_url"
    )

    if (
        isinstance(
            pdf_url,
            str,
        )
        and pdf_url.strip()
    ):
        return pdf_url.strip()

    landing_page_url = location.get(
        "landing_page_url"
    )

    if (
        isinstance(
            landing_page_url,
            str,
        )
        and landing_page_url.strip()
    ):
        return (
            landing_page_url.strip()
        )

    return None


# ---------------------------------------------------------------------------
# BUILD OA STATUS EVIDENCE
# ---------------------------------------------------------------------------
def build_oa_status_evidence(
    access_record: AccessRecord,
    work: dict,
    *,
    evidence_id: str,
    observed_date: date,
) -> AccessEvidenceRecord:
    open_access = (
        get_open_access(
            work
        )
    )

    is_oa = open_access.get(
        "is_oa"
    )

    oa_status = open_access.get(
        "oa_status"
    )

    if is_oa is True:
        value = (
            str(
                oa_status
                or "open"
            )
        )

    elif is_oa is False:
        value = "closed"

    else:
        value = "unknown"

    return AccessEvidenceRecord(
        evidence_id=(
            evidence_id
        ),
        access_id=(
            access_record.access_id
        ),
        candidate_id=(
            access_record.candidate_id
        ),
        evidence_type=(
            AccessEvidenceType.OA_STATUS
        ),
        source=(
            AccessEvidenceSource.OPENALEX
        ),
        source_name="OpenAlex",
        source_url=(
            work.get(
                "id"
            )
        ),
        value=value,
        basis=(
            "OpenAlex open_access "
            "metadata for the DOI."
        ),
        observed_date=(
            observed_date
        ),
    )


# ---------------------------------------------------------------------------
# BUILD LOCATION EVIDENCE
# ---------------------------------------------------------------------------
def build_location_evidence(
    access_record: AccessRecord,
    work: dict,
    *,
    evidence_id: str,
    observed_date: date,
) -> AccessEvidenceRecord | None:
    location = (
        get_best_oa_location(
            work
        )
    )

    if not location:
        return None

    source_url = (
        get_location_url(
            location
        )
    )

    if source_url is None:
        return None

    return AccessEvidenceRecord(
        evidence_id=(
            evidence_id
        ),
        access_id=(
            access_record.access_id
        ),
        candidate_id=(
            access_record.candidate_id
        ),
        evidence_type=(
            AccessEvidenceType.FULL_TEXT_LOCATION
        ),
        source=(
            AccessEvidenceSource.OPENALEX
        ),
        source_name=(
            get_location_source_name(
                location
            )
            or "OpenAlex"
        ),
        source_url=(
            source_url
        ),
        value=(
            "oa_location"
        ),
        basis=(
            "OpenAlex best_oa_location "
            "metadata identifies an "
            "open-access location."
        ),
        observed_date=(
            observed_date
        ),
    )


# ---------------------------------------------------------------------------
# BUILD LICENSE EVIDENCE
# ---------------------------------------------------------------------------
def build_license_evidence(
    access_record: AccessRecord,
    work: dict,
    *,
    evidence_id: str,
    observed_date: date,
) -> AccessEvidenceRecord | None:
    location = (
        get_best_oa_location(
            work
        )
    )

    license_value = (
        location.get(
            "license"
        )
    )

    if not (
        isinstance(
            license_value,
            str,
        )
        and license_value.strip()
    ):
        return None

    return AccessEvidenceRecord(
        evidence_id=(
            evidence_id
        ),
        access_id=(
            access_record.access_id
        ),
        candidate_id=(
            access_record.candidate_id
        ),
        evidence_type=(
            AccessEvidenceType.LICENSE
        ),
        source=(
            AccessEvidenceSource.OPENALEX
        ),
        source_name="OpenAlex",
        source_url=(
            get_location_url(
                location
            )
        ),
        value=(
            license_value.strip()
        ),
        basis=(
            "License value reported by "
            "OpenAlex for best_oa_location."
        ),
        observed_date=(
            observed_date
        ),
    )


# ---------------------------------------------------------------------------
# BUILD VERSION EVIDENCE
# ---------------------------------------------------------------------------
def build_version_evidence(
    access_record: AccessRecord,
    work: dict,
    *,
    evidence_id: str,
    observed_date: date,
) -> AccessEvidenceRecord | None:
    location = (
        get_best_oa_location(
            work
        )
    )

    version = location.get(
        "version"
    )

    if not (
        isinstance(
            version,
            str,
        )
        and version.strip()
    ):
        return None

    return AccessEvidenceRecord(
        evidence_id=(
            evidence_id
        ),
        access_id=(
            access_record.access_id
        ),
        candidate_id=(
            access_record.candidate_id
        ),
        evidence_type=(
            AccessEvidenceType.VERSION
        ),
        source=(
            AccessEvidenceSource.OPENALEX
        ),
        source_name="OpenAlex",
        source_url=(
            get_location_url(
                location
            )
        ),
        value=(
            version.strip()
        ),
        basis=(
            "Version reported by "
            "OpenAlex for best_oa_location."
        ),
        observed_date=(
            observed_date
        ),
    )


# ---------------------------------------------------------------------------
# BUILD OPENALEX ACCESS EVIDENCE
# ---------------------------------------------------------------------------
def build_openalex_access_evidence(
    access_record: AccessRecord,
    work: dict,
    *,
    start_index: int,
    observed_date: date,
) -> list[
    AccessEvidenceRecord
]:
    if start_index < 1:
        raise ValueError(
            "Access evidence start_index "
            "must be at least 1."
        )

    evidence_records = []

    next_index = (
        start_index
    )

    oa_evidence = (
        build_oa_status_evidence(
            access_record,
            work,
            evidence_id=(
                f"AEV-"
                f"{next_index:06d}"
            ),
            observed_date=(
                observed_date
            ),
        )
    )

    evidence_records.append(
        oa_evidence
    )

    next_index += 1

    optional_builders = (
        build_location_evidence,
        build_license_evidence,
        build_version_evidence,
    )

    for builder in optional_builders:
        evidence = builder(
            access_record,
            work,
            evidence_id=(
                f"AEV-"
                f"{next_index:06d}"
            ),
            observed_date=(
                observed_date
            ),
        )

        if evidence is None:
            continue

        evidence_records.append(
            evidence
        )

        next_index += 1

    return evidence_records


# ---------------------------------------------------------------------------
# RESOLVE OPENALEX EVIDENCE
# ---------------------------------------------------------------------------
def resolve_openalex_evidence(
    access_record: AccessRecord,
    *,
    start_index: int,
    observed_date: date,
    api_key: str | None = None,
    timeout: float = 30.0,
) -> list[
    AccessEvidenceRecord
]:
    if access_record.doi is None:
        raise ValueError(
            "OpenAlex access lookup "
            "requires a DOI."
        )

    work = (
        fetch_openalex_work(
            access_record.doi,
            api_key=api_key,
            timeout=timeout,
        )
    )

    return (
        build_openalex_access_evidence(
            access_record,
            work,
            start_index=(
                start_index
            ),
            observed_date=(
                observed_date
            ),
        )
    )


