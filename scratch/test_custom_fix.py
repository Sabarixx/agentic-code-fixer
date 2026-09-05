import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from agent.nodes.custom_debugger import run_custom_debugging_pipeline

load_dotenv()

code = "print(sabarish)"
print("Testing custom debugging pipeline on:", code)
for step in run_custom_debugging_pipeline(code=code):
    print("STEP:", step["stage"])
    if step["stage"] == "done":
        print("FINAL STATUS:", step.get("status"))
        print("CORRECTED CODE:\n", step.get("corrected_code"))
        print("CHANGELOG:", step.get("changelog"))
