import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from ui.pipeline_bridge import run_custom_fix

load_dotenv()

print("=== 1. TESTING TYPESCRIPT CUSTOM REPAIR ===")
ts_code = """function getUserName(user: User) {
  return user.profile.name.toUpperCase();
}"""
ts_tests = """it("returns a user's display name", () => {
  expect(getUserName({ profile: { name: "Ada" } })).toBe("ADA");
  expect(getUserName({ profile: null })).toBe("");
});"""

for step in run_custom_fix(code=ts_code, language="typescript", user_tests=ts_tests):
    stage = step.get("stage")
    print(f"TS STEP: {stage}")
    if stage == "fixing":
        print("Candidate:\n", step.get("corrected_code"))
    elif stage == "testing":
        print("Test Result:", step.get("test_results"))
    elif stage == "done":
        print("Final Status:", step.get("status"))
        print("Final Code:\n", step.get("corrected_code"))
