from typing import List,Optional, Annotated
from pydantic import BaseModel, Field, field_validator, constr

class GeneralInfo(BaseModel):
    """Top of resume general information"""
    introduction: str = Field(..., desciption="Narrative intro/summery")
    skills: List[str] = Field(default_factory=list, description="Skills Inventory")

    @field_validator("introduction")
    @staticmethod
    def _trim_intro(v:str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Intoduction cannot be empty")
        return v

class Bullet(BaseModel):
    """A single bullet the section will display."""
    text: str = Field(..., description="Bullet body text (verbatim)")
    # Optional metadata for DB / lineage without leaking into template:
    source_key: Optional[str] = Field(
        default=None, description="Optional link back to library key (e.g., 'a_bp_23')"
    )
    rank: Optional[int] = Field(
        default=None, ge=1, description="Optional priority/order hint for sorting"
    )
    # Optional DB identifiers you can map later:
    id: Optional[int] = Field(default=None, description="DB PK if persisted")
    section_id: Optional[int] = Field(default=None, description="FK to section in DB")


SectionCode = constr(strip_whitespace=True, pattern=r"^[A-Z]$")  #Enforces the section code to be A..Z

class Section(BaseModel):
    """A logical resume section (A..N). We keep a simple code like 'A'and an introduction. Bullets carry the content."""
    
    code: Annotated[str, SectionCode] = Field(..., description="Logical section code (A..Z)")
    introduction: str = Field(..., description="Short intro for this section")
    bullets: List[Bullet] = Field(default_factory=list)
    # Optional DB fields:
    id: Optional[int] = Field(default=None, description="DB PK if persisted")
    order: Optional[int] = Field(default=None, ge=0, description="Explicit ordering if desired")

    @field_validator("introduction")
    @staticmethod
    def _trim_section_intro(v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("section.introduction cannot be empty")
        return v

    @field_validator("bullets")
    @staticmethod
    def _dedupe_bullets(bullets: List[Bullet]) -> List[Bullet]:
        # Gentle guard against exact-duplicate bullet text
        seen = set()
        out: List[Bullet] = []
        for b in bullets:
            key = b.text.strip()
            if key and key not in seen:
                seen.add(key)
                out.append(b)
        return out

class Bullet(BaseModel):
    """A single bullet the section will display."""
    text: str = Field(..., description="Bullet body text (verbatim)")
    # Optional metadata for DB / lineage without leaking into template:
    source_key: Optional[str] = Field(
        default=None, description="Optional link back to library key (e.g., 'a_bp_23')"
    )
    rank: Optional[int] = Field(
        default=None, ge=1, description="Optional priority/order hint for sorting"
    )
    # Optional DB identifiers you can map later:
    id: Optional[int] = Field(default=None, description="DB PK if persisted")
    section_id: Optional[int] = Field(default=None, description="FK to section in DB")