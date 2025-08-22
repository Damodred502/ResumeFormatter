from typing import List,Optional, Annotated, TypeAlias
from pydantic import BaseModel, Field, field_validator, constr, ConfigDict
from datetime import datetime

SectionCode: TypeAlias = constr(strip_whitespace=True, pattern=r"^[A-Z]$")

class BulletModel(BaseModel):
    id: Optional[int] = None
    section_id: Optional[int] = None
    text: str
    source_key: Optional[str] = None
    rank: Optional[int] = None
    is_active: bool = True

class SectionModel(BaseModel):
    id: Optional[int] = None
    library_version_id: Optional[int] = None
    code: SectionCode
    organization: str
    title: str
    introduction: str
    order: Optional[int] = None
    bullets: List[BulletModel] = Field(default_factory=list)

    @field_validator("organization", "title", "introduction")
    @staticmethod
    def _trim_nonempty(v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("field cannot be empty")
        return v

class LibraryVersionModel(BaseModel):
    id: Optional[int] = None
    version_label: str
    is_active: bool = True

class LibraryBundle(BaseModel):
    """What you will feed to the LLM: one library version + its sections/bullets."""
    library_version: LibraryVersionModel
    sections: List[SectionModel]

    model_config = {"from_attributes": True}  # enable ORM→Pydantic via attribute access


class JobDescriptionEvalDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_hash: str
    job_title: str
    company: str
    jd_text: str
    jd_summary: str
    jd_keywords: List[str]
    jd_skills: List[str]
    jd_tasks: List[str]
    jd_technologies: List[str]
    created_at_utc: datetime