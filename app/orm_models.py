

# app/orm_models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, DateTime, Boolean, ForeignKey
from datetime import datetime

class Base(DeclarativeBase):
    pass

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
