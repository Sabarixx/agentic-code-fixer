from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
import uvicorn
import sys
import uuid
from pathlib import Path

# Ensure root is in sys.path so 'ui' and 'agent' packages are discoverable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.pipeline_bridge import run_custom_fix
from agent.prompts.duck_debugger_prompt import DUCK_SYSTEM_PROMPT, format_duck_prompt, SocraticResponse
from agent.nodes.custom_debugger import get_llm
from tools.sandbox_runner import detect_language

app = FastAPI(title="Agentic Code Fixer API")

# Enable CORS for the web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory session store for Duck Debugger
# { session_id: {"history": [], "level": 1, "language": "python"} }
duck_sessions: Dict[str, Any] = {}

class RepairRequest(BaseModel):
    code: str
    tests: Optional[str] = ""
    expected_behavior: Optional[str] = ""
    error_message: Optional[str] = ""
    user_tests: Optional[str] = ""
    lang: Optional[str] = None
    language: Optional[str] = None

class DuckChatRequest(BaseModel):
    session_id: Optional[str] = None
    code: str
    tests: Optional[str] = ""
    user_message: str
    language: Optional[str] = None
    lang: Optional[str] = None

@app.post("/repair")
async def repair_code(request: RepairRequest):
    try:
        # Detect exact language from code syntax, falling back to client hint
        input_hint = request.language or request.lang or ""
        target_lang = detect_language(request.code, hint=input_hint)

        # run_custom_fix is a generator that yields the stages of the debugging pipeline
        results = list(run_custom_fix(
            code=request.code,
            language=target_lang,
            expected_behavior=request.expected_behavior or "",
            error_message=request.error_message or "",
            user_tests=request.user_tests or request.tests or ""
        ))

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/duck_chat")
async def duck_chat(request: DuckChatRequest):
    try:
        # Detect exact language from code syntax
        input_hint = request.language or request.lang or ""
        target_lang = detect_language(request.code, hint=input_hint)

        # 1. Session Management
        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in duck_sessions:
            duck_sessions[session_id] = {
                "history": [],
                "level": 1,
                "language": target_lang
            }

        session = duck_sessions[session_id]
        session["language"] = target_lang

        # 2. Frustration Detection & Level Advancement
        frustration_keywords = ["stupid", "just tell me", "give up", "i dont get it", "im stuck"]
        is_frustrated = any(kw in request.user_message.lower() for kw in frustration_keywords)

        # Advance level if frustrated OR if they've had 2 turns at this level
        turn_count = len([m for m in session["history"] if m["role"] == "user"])
        if is_frustrated or (turn_count > 0 and turn_count % 2 == 0):
            session["level"] = min(3, session["level"] + 1)

        # 3. Prompt Formatting
        user_prompt = format_duck_prompt(
            code=request.code,
            tests=request.tests,
            user_message=request.user_message,
            history=session["history"],
            level=session["level"],
            language=target_lang
        )

        # 4. LLM Invocation (Structured)
        llm = get_llm()
        structured_llm = llm.with_structured_output(SocraticResponse)

        messages = [
            ("system", DUCK_SYSTEM_PROMPT),
            ("human", user_prompt),
        ]

        response: SocraticResponse = structured_llm.invoke(messages)

        # 5. Update Session History
        session["history"].append({"role": "user", "content": request.user_message})
        session["history"].append({"role": "assistant", "content": response.response_text})

        return {
            "session_id": session_id,
            "response": response.response_text,
            "level": response.current_level,
            "is_solution_unlocked": response.is_solution_unlocked,
            "critic_monologue": response.critic_monologue
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static web UI files so root "/" serves index.html and web assets directly
WEB_DIR = ROOT / "web"
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

if __name__ == "__main__":
    # Run server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
