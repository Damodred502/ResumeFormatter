from typing import List,Optional, Annotated, TypeAlias
from pydantic import BaseModel, Field, field_validator, constr

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
    """What you’ll feed to the LLM: one library version + its sections/bullets."""
    library_version: LibraryVersionModel
    sections: List[SectionModel]

    model_config = {"from_attributes": True}  # enable ORM→Pydantic via attribute access