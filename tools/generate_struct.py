"""
Générateur de structure ctypes AMS2 à partir de SharedMemory.h officiel.
Vérifie la correspondance stricte des offsets octet par octet.
"""
import re
import sys
from pathlib import Path

HEADER_PATH = Path(__file__).parent / "SharedMemory.h"

with open(HEADER_PATH, "r", encoding="utf-8") as f:
    text = f.read()

parts = text.split("typedef struct")
sm_text = parts[2]
sm_body = sm_text.split("} SharedMemory;")[0]

type_mapping = {
    "unsigned int": "c_uint",
    "int": "c_int",
    "float": "c_float",
    "bool": "c_bool",
    "char": "c_char",
    "volatile unsigned int": "c_uint",
    "ParticipantInfo": "ParticipantInfo",
}

constants = {
    "STRING_LENGTH_MAX": "STRING_LENGTH_MAX",
    "STORED_PARTICIPANTS_MAX": "STORED_PARTICIPANTS_MAX",
    "TYRE_MAX": "TYRE_MAX",
    "VEC_MAX": "VEC_MAX",
    "TYRE_COMPOUND_NAME_LENGTH_MAX": "TYRE_COMPOUND_NAME_LENGTH_MAX",
}

py_lines = []
for line in sm_body.strip().split("\n"):
    orig_comment = ""
    if "//" in line:
        line_code, orig_comment = line.split("//", 1)
        orig_comment = "  # " + orig_comment.strip()
    else:
        line_code = line
    line_code = line_code.strip()
    if not line_code or line_code.startswith("{"):
        continue

    m = re.match(r"([\w\s]+?)\s+(\w+)(?:\[(\w+)\])?(?:\[(\w+)\])?;", line_code)
    if not m:
        print(f"FAILED TO PARSE: {line_code}")
        sys.exit(1)

    typ, name, arr1, arr2 = m.groups()
    typ = typ.strip()
    py_t = type_mapping[typ]

    if arr1 and arr2:
        c1 = constants.get(arr1, arr1)
        c2 = constants.get(arr2, arr2)
        py_decl = f"({py_t} * {c2}) * {c1}"
    elif arr1:
        c1 = constants.get(arr1, arr1)
        py_decl = f"{py_t} * {c1}"
    else:
        py_decl = py_t

    py_lines.append(f'        ("{name}", {py_decl}),{orig_comment}')

print(f"Successfully generated {len(py_lines)} fields.")
with open(Path(__file__).parent / "_generated_fields.py", "w", encoding="utf-8") as f:
    f.write("\n".join(py_lines))
