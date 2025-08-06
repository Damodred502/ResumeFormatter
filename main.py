import os
import sys
import json
import demjson3
import re
from openai import OpenAI
from dotenv import load_dotenv
import certifi
from template_writer import create_updated_template


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
    jd_text = load_job_description(jd_file)
    bp_lib = load_bulletpoint_library("./bulletpoint_library.json")

    # INSERT YOUR PROMPT HERE
    prompt = f"""
        You are a resume assistant helping tailor bullet points for a specific job application.
        You will be provided with: A job description (text).
        A JSON object called library containing pre-written resume bullet points organized into sections "A", "B", and "C". Each section includes multiple key-value pairs, where the key is a unique identifier (e.g., "a_bp_1") and the value is the bullet point text.
        Instructions:
        Analyze the job description carefully simulating an ATS system.
        Redraft the introduction to align more closely with the job description infering skills and experiance from all provided bullet points in bulletpoint_library.json and output it in G.introduction.  Include the mention of veteran status.  Where possible, demonstrate 
        Select the best  aligned skills from the skills inventory, not to exceed 15 values, and output it into a comma seperated list in G.si.
        Select:
        The 14 best-aligned bullet points from Section A
        The 6 best-aligned bullet points from Section B
        The 2 best-aligned bullet points from Section C
        Choose bullet points that best match the job’s responsibilities, required skills, and desired experience while trying to minimize redundancy and show a bredth of experiance.  Bullet points should be ordered from most to least realavent. Prioritize exact keyword matches optimized for a stict ATS system.
        Output Format:
        Return a single JSON object structured as follows:
        {{
        "G":{{
        "introduction": "[your response]",
        "si":"[your response]",
        }}
        "A": {{
        "a_bp_1": "[bullet text]",
        "a_bp_2": "[bullet text]",
        ...
        }},
        "B": {{
        "b_bp_1": "[bullet text]",
        ...
        }},
        "C": {{
        "c_bp_1": "[bullet text]",
        ...
        }}
        }}
        All Keys must be sequential, 1-N.
        Do not include explanations, comments, or any other text.
        Your entire response must be valid JSON and must begin and end with curly braces.

    {jd_text}
    {bp_lib}
    """
    
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
