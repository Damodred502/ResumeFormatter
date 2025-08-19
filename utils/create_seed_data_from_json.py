import json
import os
from settings import PROJECT_ROOT
from utils.utils import load_json

# ---- Paste your JSON exactly as given into `raw` ----

json_file = PROJECT_ROOT / "bulletpoint_library.json"
output_file = PROJECT_ROOT / "statements.txt"


# ---- Config: how top-level keys map to section variables (sec_a.id, etc.)
SECTION_ID_VAR = {
    "A": "sec_a.id",
    "B": "sec_b.id",
    "C": "sec_c.id",
    "G": "sec_g.id",
}

def escape_text(s: str) -> str:
    """Escape for inclusion inside double-quoted Python/SQL strings."""
    return (
        s.replace("\\", "\\\\")
         .replace('"', '\\"')
         .replace("\r\n", "\\n")
         .replace("\n", "\\n")
    ).strip()

def iter_texts(d):
    """Yield (section_key, text) pairs from the nested dict."""
    for section_key, section_val in d.items():
        if not isinstance(section_val, dict):
            continue
        for _, v in section_val.items():
            if isinstance(v, str):
                txt = v.strip()
                if txt:
                    yield section_key, txt

def main():
    data = load_json(json_file)
    with open(output_file, "w", encoding="utf-8") as out:
        for section_key, text in iter_texts(data):
            sec_var = SECTION_ID_VAR.get(section_key, f"sec_{section_key.lower()}.id")
            line = f'Bullet(section_id={sec_var}, text="{escape_text(text)}"),\n'
            out.write(line)


if __name__ == "__main__":
    main()
    print(f"✅ Wrote SQL-like statements to {output_file}")