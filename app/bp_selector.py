import os
import json
import asyncio
from dotenv import load_dotenv

from agents import Agent, Runner

from app.persist_bp import persist_bp_result
from app.db import SessionLocal
from app.loaders import load_library_bundle, load_jd_evaluation
from app.orm_models import JobDescriptionEval
from app.resume_model import JobDescriptionEvalDTO, LibraryBundle
from datetime import datetime
from pprint import pprint

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
env = os.getenv("ENV", "production").lower()
model = "gpt-4o-mini" if env == "development" else "gpt-4o"


def evaluation_to_json_selected(eval_orm : JobDescriptionEval  ) -> str:
    dto = JobDescriptionEvalDTO.model_validate(eval_orm)
    return dto.model_dump_json(
        include={
            "job_title",
            "company",
            "jd_text",
            "jd_keywords",
            "jd_skills",
            "jd_tasks",
            "jd_technologies",
        },
        indent=2
    )

def library_bundle_to_json_selected(bundle: LibraryBundle) -> str:
    return bundle.model_dump_json(
          include={
                "library_version": {"version_label"},
                "sections": {
                    "__all__": {
                        "code": True,
                        "organization": True,
                        "title": True,
                        "introduction": True,
                        "bullets": {"__all__": {"id","text"}
                        },
                    }
                },
            },
        exclude_none=True,
        indent=2,
    )

def log_runner_result(result, filename = "runner_log.json"):
        timestamp = datetime.utcnow().isoformat()
        content = result.model_dump_json(indent=2)
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"\n--- Log at {timestamp} UTC ---\n")
            f.write(content)
            f.write("\n")


async def get_bp_eval(session) -> LibraryBundle:
    jd_eval = load_jd_evaluation(session)
    jd_json = evaluation_to_json_selected(jd_eval)
    jd_lib_json = library_bundle_to_json_selected(load_library_bundle(session))

    agent_input = json.dumps(
        {
        "job_description" : json.loads(jd_json),
        "library_bundle" : json.loads(jd_lib_json)
        },
        indent=2
    )
    result = await Runner.run(bp_selector, agent_input)
    out = result.final_output
    log_runner_result(out)
    persist_bp_result(
        session,
        jd_evaluation_id=jd_eval.id,
        bundle=out,
        model_name=model,
        env=env,
        prompt_version= "v1"
        )
    return out
    


#---Agents------------------------------

bp_selector = Agent(
    name = "Bulletpoint Selector",
    model = model,
    instructions=
        """
        You are simulating a job seeker who wants to obtain a new position.

        INPUT:
        - `job_description`: JSON containing a job description and a preliminary analysis (keywords, skills, tasks, technologies).
        - `library_bundle`: JSON with a curated list of prior-experience bullet points grouped by sections.
        Each `section` represents a past role/experience; sections 2, 3, and 4 contain larger bullet pools.

        TASK:
        1) Analyze how well the extracted items match the actual job description. Adjust the analysis mentally as needed.
        2) For each section, rewrite `introduction` to align with the job description.  Make sure section.id matches the input id.
        3)“For each section, copy the existing organization value from the input and never output an empty string.  The organization for section 1 is "Information”
        4) Select and return WITH A RANK:
        - 12 best-aligned bullets from section 2
        - 6 best-aligned bullets from section 3
        - 2 best-aligned bullets from section 4
        4) Follow the `LibraryBundle` schema for output. Return ONLY valid `LibraryBundle` content.

        NOTES:
        - Use the bullet `id` and `text` already provided in `library_bundle`.
        - Preserve other fields as needed by the `LibraryBundle` schema.
        """.strip(),
    output_type=LibraryBundle
)






if __name__ == "__main__":
    with SessionLocal() as session:
        returned_library_bundle = asyncio.run(get_bp_eval(session))
        print(returned_library_bundle.model_dump_json(indent=2))