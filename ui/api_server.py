from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any
import uvicorn
import sys
from pathlib import Path

# Ensure root is in sys.path so 'ui' and 'agent' packages are discoverable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.pipeline_bridge import run_custom_fix

app = FastAPI(title="Agentic Code Fixer API")

# Enable CORS for the web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RepairRequest(BaseModel):
    code: str
    tests: Optional[str] = ""
    expected_behavior: Optional[str] = ""
    error_message: Optional[str] = ""
    user_tests: Optional[str] = ""

@app.post("/repair")
async def repair_code(request: RepairRequest):
    try:
        # Check if code looks like TypeScript/JS and warn (since we only have Python sandbox)
        if "function" in request.code and "def " not in request.code:
             # We still try to run it through the LLM, as the LLM can "fix" it
             # but the sandbox will likely fail.
             pass

        # run_custom_fix is a generator that yields the stages of the debugging pipeline
        results = list(run_custom_fix(
            code=request.code,
            expected_behavior=request.expected_behavior,
            error_message=request.error_message,
            user_tests=request.user_tests or request.tests
        ))

        return results
    except Exception as e:
        # If it's a syntax error from AST, it's likely a language mismatch
        if "SyntaxError" in str(e) or "unexpected token" in str(e).lower():
            raise HTTPException(status_code=400, detail=f"Language mismatch: The agent is currently optimized for Python. Detected potentially non-Python code. Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
