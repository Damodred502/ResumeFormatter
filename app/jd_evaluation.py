from __future__ import annotations
import os
import re, hashlib, unicodedata
import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv
from typing import Optional, Union, List
from pathlib import Path
from datetime import datetime
from app.db import SessionLocal
from settings import PROJECT_ROOT
from pydantic import BaseModel, Field, ValidationError
from app.orm_models import JDEvaluationTransaction, JobDescriptionEval
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError



# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
env = os.getenv("ENV", "production").lower()
model = "gpt-4o-mini" if env == "development" else "gpt-4o"


#---Data Models----------------------------------
class OutputJDEvaluator(BaseModel):
    job_title: str = Field(..., description="Parsed job title")
    company: str = Field(..., description="Parsed company name")
    jd_text: str = Field(..., description="Original JD text")
    jd_summary: str = Field(..., description="Short summary of the role")
    jd_keywords: List[str] = Field(default_factory=list, description="ATS-friendly keywords")
    jd_skills: List[str] = Field(default_factory=list, description="Ranked list of skills")
    jd_tasks: List[str] = Field(default_factory=list, description="Core tasks/duties")
    jd_technologies: List[str] = Field(default_factory=list, description="Explicit tech mentioned")

#---Agents----------------------------------
jd_evaluator = Agent(
    name = "JD Evaluator",
    model=model,
    instructions=(
        "Your job is to evaluate job descriptions and return a summery of the position and an analysis"
        "Your analysis should include the following sections:"
        "A list of important keywords for ATS compatability"
        "A list of important skills in order of realavance"
        "A list of the critical job tasks and duties"
        "A list of explicitly named technologies desired or required.  Include the names of specifically mentioned products, applications, development environments, or languages"
        "Return only in the schema provided."

        ),
    output_type=OutputJDEvaluator
    )


#---Services----------------------------------

def load_job_description(filename: Union[str, Path] = PROJECT_ROOT/ "job_description.txt") -> str:
    with open(filename, "r", encoding="utf-8") as f:
        jd_text = f.read()
    return jd_text
    
def canonicalize(text: str) -> str:
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    t = unicodedata.normalize("NFKC", t)
    t = "\n".join(line.strip() for line in t.splitlines())
    t = re.sub(r"\n{3,}", "\n\n", t)  # collapse 3+ blank lines to 2
    return t.strip()

def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def evaluate_jd_async(file_path : Union[str, Path]) -> tuple[OutputJDEvaluator, str, str]:
    raw = load_job_description(file_path)
    canonical = canonicalize(raw)
    content_hash = sha256_hex(canonical)
    result = await Runner.run(jd_evaluator, canonical)
    out = result.final_output
    if not isinstance(out, OutputJDEvaluator):
        out = OutputJDEvaluator.model_validate(out)
    if not out.jd_text:
        out.jd_text = canonical
    return (out, canonical, content_hash)

def get_or_create_evaluation(
    session: Session,
    *,
    analysis: OutputJDEvaluator,   # already validated
    canonical_text: str,           # your canonicalized JD
    content_hash: str,             # sha256 of canonical_text
) -> JobDescriptionEval:
    # Fast path
    existing = session.scalar(
        select(JobDescriptionEval).where(JobDescriptionEval.content_hash == content_hash)
    )
    if existing:
        return existing

    # Build payload from Pydantic, override jd_text to canonical form
    payload = analysis.model_dump()          # Pydantic v2; returns Python-native types
    payload["jd_text"] = canonical_text      # ensure what you persist is canonical

    # (Optional safety) filter keys to only ORM columns you actually have
    allowed = set(JobDescriptionEval.__table__.columns.keys()) - {"id", "created_at_utc", "content_hash"}
    payload = {k: v for k, v in payload.items() if k in allowed}

    row = JobDescriptionEval(content_hash=content_hash, **payload)
    session.add(row)
    try:
        session.flush()  # assigns PK; raises IntegrityError if content_hash already exists (unique index)
    except IntegrityError:
        session.rollback()
        row = session.scalar(
            select(JobDescriptionEval).where(JobDescriptionEval.content_hash == content_hash)
        )
        if row is None:
            raise
    return row

def create_transaction(
    session: Session,
    *,
    eval_id: int,
    model_name: Optional[str],
    env: Optional[str],
    source_filename: Optional[str],
    prompt_version: Optional[str],
    status: str = "completed",
    error_message: Optional[str] = None,
) -> JDEvaluationTransaction:
    tx = JDEvaluationTransaction(
        jd_evaluation_id=eval_id,
        status=status,
        model_name=model_name,
        env=env,
        source_filename=source_filename,
        prompt_version=prompt_version,
        error_message=error_message,
        started_at_utc=datetime.utcnow(),
        completed_at_utc=datetime.utcnow(),
    )
    session.add(tx)
    session.flush()
    return tx


async def run_and_persist_jd_evaluation(
    file_path: Union[str, Path] = PROJECT_ROOT / "job_description.txt",
    *,
    prompt_version: Optional[str] = None,
) -> tuple[JDEvaluationTransaction, JobDescriptionEval]:
    file_path = Path(file_path)

    with SessionLocal() as session:
        try:
            analysis, canonical_text, content_hash = await evaluate_jd_async(file_path)

            eval_row = get_or_create_evaluation(
                session,
                analysis=analysis,
                canonical_text=canonical_text,
                content_hash=content_hash,
            )

            tx = create_transaction(
                session,
                eval_id=eval_row.id,
                model_name=model,
                env=env,
                source_filename=str(file_path),
                prompt_version=prompt_version,
                status="completed",
            )

            session.commit()
            # refresh for return
            session.refresh(eval_row)
            session.refresh(tx)
            return tx, eval_row

        except ValidationError as ex:
            # If you want to record error runs as transactions,
            # make jd_evaluation_id nullable OR log to a separate run_log table.
            # With NOT NULL FK, we can only re-raise:
            raise
        except Exception:
            session.rollback()
            raise



if __name__ == "__main__":
    asyncio.run(run_and_persist_jd_evaluation())