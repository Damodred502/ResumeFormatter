# app/loaders.py
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.orm_models import LibraryVersion, Section, Bullet
from app.resume_model import LibraryVersionModel, SectionModel, BulletModel, LibraryBundle

def get_active_library_version(session) -> LibraryVersion:
    q = (
        select(LibraryVersion)
        .where(LibraryVersion.is_active == True)
        .order_by(LibraryVersion.id.desc())
        .limit(1)
    )
    lv = session.execute(q).scalars().first()
    if not lv:
        raise RuntimeError("No active LibraryVersion found.")
    return lv

def load_library_bundle(session) -> LibraryBundle:
    lv = get_active_library_version(session)

    q_sections = (
        select(Section)
        .where(Section.library_version_id == lv.id)
        .options(selectinload(Section.bullets))
        .order_by(Section.order, Section.code)
    )
    sections_orm: List[Section] = session.execute(q_sections).scalars().all()

    sections = []
    for s in sections_orm:
        # Filter active bullets, then order by rank NULLS LAST, then id
        active_bullets = [b for b in s.bullets if b.is_active]
        active_bullets.sort(key=lambda b: ((b.rank is None), b.rank if b.rank is not None else 10**9, b.id))

        sections.append(
            SectionModel(
                id=s.id,
                library_version_id=s.library_version_id,
                code=s.code,
                organization=s.organization,
                title=s.title,
                introduction=s.introduction,
                order=s.order,
                bullets=[
                    BulletModel(
                        id=b.id,
                        section_id=b.section_id,
                        text=b.text,
                        source_key=b.source_key,
                        rank=b.rank,
                        is_active=b.is_active,
                    ) for b in active_bullets
                ],
            )
        )

    return LibraryBundle(
        library_version=LibraryVersionModel(
            id=lv.id, version_label=lv.version_label, is_active=lv.is_active
        ),
        sections=sections,
    )
