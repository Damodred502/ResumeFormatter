

# app/orm_models.py
import json
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator, Text
from sqlalchemy import String, Integer, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from datetime import datetime, UTC
from typing import List, Optional


class JsonList(TypeDecorator):
    impl = Text
    cache_ok = True
    def process_bind_param(self, value, dialect):
        return json.dumps(value or [])
    def process_result_value(self, value, dialect):
        return json.loads(value or "[]")


class Base(DeclarativeBase):
    pass


#---BpLib Tables-------------------------------------
class LibraryVersion(Base):
    __tablename__ = "library_version"
    id: Mapped[int] = mapped_column("library_version_id", Integer, primary_key=True, autoincrement=True)
    version_label: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, nullable=False)

    sections: Mapped[list["Section"]] = relationship(back_populates="library_version", cascade="all, delete-orphan")

class Section(Base):
    __tablename__ = "section"
    id: Mapped[int] = mapped_column("section_id", Integer, primary_key=True, autoincrement=True)
    library_version_id: Mapped[int] = mapped_column(ForeignKey("library_version.library_version_id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(1), nullable=False)  # 'A'..'Z'
    organization: Mapped[str] = mapped_column(Text, nullable = False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    introduction: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int | None] = mapped_column("order_index", Integer)

    library_version: Mapped["LibraryVersion"] = relationship(back_populates="sections")
    bullets: Mapped[list["Bullet"]] = relationship(back_populates="section", cascade="all, delete-orphan")

class Bullet(Base):
    __tablename__ = "bullet"
    id: Mapped[int] = mapped_column("bullet_id", Integer, primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("section.section_id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_key: Mapped[str | None] = mapped_column(String(64))
    rank: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, nullable=False)

    section: Mapped["Section"] = relationship(back_populates="bullets")

#---Decision Set BPLib Tables-------------------------------
class BPDecisionSet(Base):
    __tablename__ = "bp_decision_sets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Link to the central transaction row (same table you already use)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("jd_transactions.id", ondelete="CASCADE"), nullable=False
    )

    # Optional: link to the library version used for selection (safer by id)
    library_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("library_version.library_version_id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False
    )

    transaction: Mapped["JDEvaluationTransaction"] = relationship()
    sections: Mapped[list["BPDecisionSection"]] = relationship(
        back_populates="decision_set", cascade="all, delete-orphan"
    )


class BPDecisionSection(Base):
    __tablename__ = "bp_decision_sections"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    decision_set_id: Mapped[int] = mapped_column(
        ForeignKey("bp_decision_sets.id", ondelete="CASCADE"), nullable=False
    )

    # Mirror structure you present to the LLM
    code: Mapped[str] = mapped_column(String(4), nullable=False)   # 'A','B','C', etc.
    organization: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    introduction: Mapped[str] = mapped_column(Text, nullable=False)

    decision_set: Mapped["BPDecisionSet"] = relationship(back_populates="sections")
    bullets: Mapped[list["BPDecisionBullet"]] = relationship(
        back_populates="section", cascade="all, delete-orphan"
    )

    __table_args__ = (
        # optional: keep each section code unique per decision set
        UniqueConstraint("decision_set_id", "code", name="uq_decset_code"),
    )


class BPDecisionBullet(Base):
    __tablename__ = "bp_decision_bullets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    decision_section_id: Mapped[int] = mapped_column(
        ForeignKey("bp_decision_sections.id", ondelete="CASCADE"), nullable=False
    )

    # If this bullet came from your library, keep the FK for traceability
    source_bullet_id: Mapped[int | None] = mapped_column(
        ForeignKey("bullet.bullet_id", ondelete="SET NULL"), nullable=True
    )

    # Always store a snapshot to freeze history
    text_snapshot: Mapped[str] = mapped_column(Text, nullable=False)

    # Rank from the model output (required for your downstream rendering)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    section: Mapped["BPDecisionSection"] = relationship(back_populates="bullets")



#---Transaction Table(s)-----------------------
class JDEvaluationTransaction(Base):
    __tablename__ = "jd_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Basic run metadata
    started_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at_utc: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="completed", nullable=False)  # e.g., "running", "completed", "error"
    process_name: Mapped[str] = mapped_column(String(50), default="jd_evaluator", nullable=False)
    input_payload: Mapped[str | None] = mapped_column(Text, nullable=True)   # JSON string sent to the agent
    output_payload: Mapped[str | None] = mapped_column(Text, nullable=True)  # raw model JSON returned

    # Optional diagnostics / context
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "gpt-4o"
    env: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)         # e.g., "production", "development"
    source_filename: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Many-> One FK to evaluations
    jd_evaluation_id:Mapped[int] = mapped_column(
        ForeignKey("jd_evaluations.id", ondelete="CASCADE"), 
        nullable=False,
    )
    
    evaluation: Mapped["JobDescriptionEval"] = relationship(back_populates="transactions")





#---Job Description Evaluation Table -----------------------------------
class JobDescriptionEval(Base):
    __tablename__ = "jd_evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    
    #unique hash for dedupe
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True, unique=True)

    #---Parsed Fields
    job_title: Mapped[str] = mapped_column(String(200), nullable=False)
    company: Mapped[str] = mapped_column(String(200), nullable=False)

    jd_text: Mapped[str] = mapped_column(Text, nullable=False)
    jd_summary: Mapped[str] = mapped_column(Text, nullable=False)

    jd_keywords: Mapped[List[str]] = mapped_column(JsonList, nullable=False)
    jd_skills: Mapped[List[str]] = mapped_column(JsonList, nullable=False)
    jd_tasks: Mapped[List[str]] = mapped_column(JsonList, nullable=False)
    jd_technologies: Mapped[List[str]] = mapped_column(JsonList, nullable=False)

    created_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # One -> Many backref to transaction
    transactions: Mapped[list["JDEvaluationTransaction"]] = relationship(
        back_populates="evaluation",
        cascade="all, delete-orphan",
        passive_deletes=True,
        single_parent=True
        )

