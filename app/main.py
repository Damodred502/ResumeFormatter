import os
import sys
import json
import demjson3
import re
from openai import OpenAI
from dotenv import load_dotenv
import certifi
from app.template_writer import create_updated_template
import utils.utils
from app.loaders import load_library_bundle
from app.db import SessionLocal


# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
env = os.getenv("ENV", "production").lower()

if not api_key:
    raise ValueError("Missing OpenAI API key in .env file")
client = OpenAI(api_key=api_key)

# Select model based on environment
model = "gpt-4o-mini" if env == "development" else "gpt-4o"

def delete_old_output():
    OPENAI_RESPONSE = "./openai_response1.json"
    if os.path.exists(OPENAI_RESPONSE):
        os.remove(OPENAI_RESPONSE)
        print(f"Deleted old file: {OPENAI_RESPONSE}")

def call_openai_api(prompt: str) -> str:
    """Scaffold for OpenAI API call. Insert your full prompt in the message."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

def save_response(content_dict: dict, filename: str = "openai_response1.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(content_dict, f, indent=2)



def main(filename="job_description.txt"):

    jd_file = sys.argv[1] if len(sys.argv) == 2 else filename
    
    with SessionLocal() as session:
        prompt_bundle = load_library_bundle(session)
        print(prompt_bundle.model_dump_json(indent=2))
    
    



if __name__ == "__main__":
        main()
