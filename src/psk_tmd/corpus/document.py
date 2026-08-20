from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# DOCUMENT BLOCK
# ---------------------------------------------------------------------------
class DocumentBlock(BaseModel):
    block_index: int = Field(ge=1)
    text: str


# ---------------------------------------------------------------------------
# DOCUMENT PAGE
# ---------------------------------------------------------------------------
class DocumentPage(BaseModel):
    page_number: int = Field(ge=1)
    text: str
    blocks: list[DocumentBlock] = Field(
        default_factory=list,
    )


# ---------------------------------------------------------------------------
# DOCUMENT SECTION
# ---------------------------------------------------------------------------
class DocumentSection(BaseModel):
    section_index: int = Field(ge=1)
    title: str | None = None
    text: str


# ---------------------------------------------------------------------------
# DOCUMENT TEXT RESULT
# ---------------------------------------------------------------------------
class DocumentTextResult(BaseModel):
    pages: list[DocumentPage] = Field(default_factory=list)
    sections: list[DocumentSection] = Field(default_factory=list)

    full_text: str

    page_count: int = Field(ge=0)

    source_format: Literal["pdf", "xml"]
    extraction_method: str


