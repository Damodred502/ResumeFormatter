import os
import json
import sys
import demjson3
import re
from openai import OpenAI


def load_file(file_path:str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} was not found")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    
def load_json(file_path:str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
    
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


def try_parse_json(content_str:str) -> dict:
    cleaned = clean_gpt_wrapping(content_str)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("Standard JSON parsing failed.  Trying GPT repair...")
        try:
            return json.loads(clean_gpt_wrapping(fix_json_with_gpt(cleaned)))
        except Exception:
            print("GPT repair failed.  Trying demjson3 fallback...")
            try:
                return demjson3.decode(cleaned)
            except demjson3.JSONDecodeError as e:
                print("demjson3 also failed to parse the response.")
                raise ValueError("Unable to parse response as valid JSON.")

# Make a OpenAI with the malformed json and return a restructured version
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

def clean_gpt_wrapping(text: str) -> str:
    """Remove common GPT formatting like ```json ... ``` or backticks."""
    # Remove ```json and ```
    text = re.sub(r"^```json\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"```$", "", text.strip())
    # Remove stray backticks
    return text.replace("`", "")