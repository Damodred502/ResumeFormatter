# app/persist_bp.py (new helper)

from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, UTC
import json

from app.orm_models import (
    JobDescriptionEval,
    JDEvaluationTransaction,
    LibraryVersion,
    Bullet,
    BPDecisionSet,
    BPDecisionSection,
    BPDecisionBullet,
)
from app.resume_model import LibraryBundle  # your Pydantic output model


def persist_bp_result(
    session: Session,
    *,
    jd_evaluation_id: int,
    bundle: LibraryBundle,
    model_name: str,
    env: str,
    prompt_version: Optional[str],
    agent_input_json: str | None = None,
    raw_output_json: str | None = None,
) -> int:
    """
    Persists a bp_selector run:
      - Creates a row in jd_transactions with process_name='bp_selector'
      - Creates a BPDecisionSet + BPDecisionSections + BPDecisionBullets
    Returns: decision_set_id
    """

    started = datetime.now(UTC).replace(tzinfo=None)

    # 1) Create transaction
    txn = JDEvaluationTransaction(
        started_at_utc=started,
        completed_at_utc=None,
        status="running",
        model_name=model_name,
        env=env,
        prompt_version=prompt_version,
        error_message=None,
        jd_evaluation_id=jd_evaluation_id,
        process_name="bp_selector",
        input_payload=agent_input_json,
        output_payload=raw_output_json,
    )
    session.add(txn)
    session.flush()  # get txn.id

    # 2) Resolve library_version_id by label (if present)
    lib_version_id = None
    lbl = (bundle.library_version.version_label if bundle.library_version else None)
    if lbl:
        lib_v = session.execute(
            select(LibraryVersion).where(LibraryVersion.version_label == lbl)
        ).scalars().first()
        if lib_v:
            lib_version_id = lib_v.id

    # 3) Decision set
    dec_set = BPDecisionSet(
        transaction_id=txn.id,
        library_version_id=lib_version_id,
    )
    session.add(dec_set)
    session.flush()  # dec_set.id

    # 4) Sections + bullets
    for s in bundle.sections or []:
        dec_sec = BPDecisionSection(
            decision_set_id=dec_set.id,
            code=s.code,
            organization=s.organization,
            title=s.title,
            introduction=s.introduction,
        )
        session.add(dec_sec)
        session.flush()

        # bullets
        for b in s.bullets or []:
            # Try to resolve source bullet id (if your output included "id")
            source_id = getattr(b, "id", None)
            # It’s okay if bullet id isn’t resolvable—keep it NULL and snapshot text
            if source_id is not None:
                exists = session.execute(
                    select(Bullet.id).where(Bullet.id == source_id)
                ).scalar_one_or_none()
                if exists is None:
                    source_id = None

            dec_b = BPDecisionBullet(
                decision_section_id=dec_sec.id,
                source_bullet_id=source_id,
                text_snapshot=b.text,
                rank=b.rank if hasattr(b, "rank") else None,
            )
            session.add(dec_b)

    # 5) finalize transaction
    txn.completed_at_utc = datetime.now(UTC).replace(tzinfo=None)
    txn.status = "completed"

    session.commit()
    return dec_set.id
