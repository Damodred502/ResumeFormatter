import os
import sys
import json
import demjson3
import re
from openai import OpenAI
from dotenv import load_dotenv
import certifi
from template_writer import create_updated_template
from utils import load_file


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




def load_job_description(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Job description file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def load_bulletpoint_library(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Bulletpoint Library file not found at {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

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

def fix_json_with_gpt(malformed_json: str) -> str:
    fix_prompt = f"""
        The following string is intended to be valid JSON but contains formatting issues.
        Fix it so that it is a valid JSON object. Return only the corrected JSON.

        Input:
        {malformed_json}
        """
    response = client.chat.completions.create(
        model = model,
        messages= [{"role":"user", "content": fix_prompt}],
        temperature=0
    )
    return response.choices[0].message.content

def try_parse_json(content_str:str) -> dict:
    cleaned = clean_gpt_wrapping(content_str)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("Standard JSON parsing failed.  Trying GPT repair...")
        try:
            repaired = fix_json_with_gpt(cleaned)
            cleaned_repaired = clean_gpt_wrapping(repaired)
            return json.loads(repaired)
        except Exception:
            print("GPT repair failed.  Trying demjson3 fallback...")
            try:
                return demjson3.decode(cleaned)
            except demjson3.JSONDecodeError as e:
                print("demjson3 also failed to parse the response.")
                raise ValueError("Unable to parse response as valid JSON.")

def clean_gpt_wrapping(text: str) -> str:
    """Remove common GPT formatting like ```json ... ``` or backticks."""
    # Remove ```json and ```
    text = re.sub(r"^```json\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"```$", "", text.strip())
    # Remove stray backticks
    return text.replace("`", "")


def main(filename="job_description.txt"):

    
    
    jd_file = sys.argv[1] if len(sys.argv) == 2 else filename
    jd_text = load_file(jd_file)
    bp_lib = load_file("./bulletpoint_library.json")

    # INSERT YOUR PROMPT HERE

    
    print("Calling OpenAI...")
    raw_result = call_openai_api(prompt)

    print("Validating and parsing JSON...")
    parsed_json = try_parse_json(raw_result)

    delete_old_output()
    
    print("Saving Valid Json")
    save_response(parsed_json)
    
    print("Creating Updated Template")
    create_updated_template()

if __name__ == "__main__":
        main()
