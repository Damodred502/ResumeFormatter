import os
import json
from docxtpl import DocxTemplate




def load_template(file):
    if not os.path.exists(file):
        raise FileNotFoundError(f"{file} not found in root directory.")

    return DocxTemplate(file)

def load_context(file):
    if not os.path.exists(file):
        raise FileNotFoundError(f"{file} not found in root directory.")
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def render_template(template, context):
    template.render(context)

def delete_old_output(file):
    if os.path.exists(file):
        os.remove(file)
        print(f"Deleted old file: {file}")

def save_output(template, output_file):
    template.save(output_file)
    print(f"New file saved as: {output_file}")

def create_updated_template():
    TEMPLATE_FILE = "Template.docx"
    OUTPUT_FILE = "updated_template.docx"
    CONTEXT_FILE = "openai_response1.json"
    
    delete_old_output(OUTPUT_FILE)
    context = load_context(CONTEXT_FILE)
    doc = load_template(TEMPLATE_FILE)
    render_template(doc, context)
    save_output(doc, OUTPUT_FILE)

