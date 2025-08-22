# app/loaders.py
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.orm_models import LibraryVersion, Section, Bullet, JobDescriptionEval
from app.resume_model import LibraryVersionModel, SectionModel, BulletModel, LibraryBundle, JobDescriptionEvalDTO
import pprint



#---BPLib Loader------ pulls most recent active full BP library
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

#---JD Loader------ pulls most recent evaluated jd

def load_jd_evaluation(session, eval_id: int | None = None) -> JobDescriptionEval:
    if eval_id is not None:
        stmt = select(JobDescriptionEval).where(JobDescriptionEval.id == eval_id)
        evaluation = session.execute(stmt).scalars().first()
        if evaluation is None:
            raise ValueError(f"Job Description with id = {eval_id} not found")
    else:
        stmt = select(JobDescriptionEval).order_by(JobDescriptionEval.id.desc()).limit(1)
        evaluation = session.execute(stmt).scalars().first()
        if evaluation is None:
            raise ValueError("No JobDescriptionEval records exist yet")
    
    return evaluation





if __name__ == "__main__":
    from app.db import SessionLocal

    with SessionLocal() as session:
        bundle = load_library_bundle(session)

    try:
        print(bundle.model_dump_json(indent=2))
    except AttributeError:
        pass