from Utils/utils.py import load_file


def build_resume_prompt(job_description: str, bulletpoint_library: str) -> str:
    return f"""
        You are a resume assistant helping tailor bullet points for a specific job application.
        You will be provided with: A job description (text).
        A JSON object called library containing pre-written resume bullet points organized into sections "A", "B", and "C". Each section includes multiple key-value pairs, where the key is a unique identifier (e.g., "a_bp_1") and the value is the bullet point text.
        Instructions:
        Analyze the job description carefully simulating an ATS system.
        Redraft the introduction to align more closely with the job description infering skills and experiance from all provided bullet points in bulletpoint_library.json and output it in G.introduction.  Include the mention of veteran status.  Where possible, demonstrate 
        Select the best  aligned skills from the skills inventory, not to exceed 15 values, and output it into a comma seperated list in G.si.
        Select:
        The 10 best-aligned bullet points from Section A
        The 5 best-aligned bullet points from Section B
        The 2 best-aligned bullet points from Section C
        Choose bullet points that best match the job’s responsibilities, required skills, and desired experience while trying to minimize redundancy and show a bredth of experiance.  Bullet points should be ordered from most to least realavent.
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