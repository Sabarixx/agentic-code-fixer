import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from ui.pipeline_bridge import run_custom_fix

load_dotenv()

print("=== TESTING PYTHON BUG: prit('hello') ===")
py_bug = """def say_hello():
    prit("hello")
"""
for step in run_custom_fix(code=py_bug, language="python"):
    stage = step.get("stage")
    print(f"PY STEP: {stage}")
    if stage == "done":
        print("Final Status:", step.get("status"))
        print("Final Code:\n", step.get("corrected_code"))
        print("Changelog:", step.get("changelog"))
