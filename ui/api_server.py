from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
import uvicorn
import sys
import uuid
import json
import asyncio
from pathlib import Path

# Ensure root is in sys.path so 'ui' and 'agent' packages are discoverable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.pipeline_bridge import run_custom_fix
from agent.prompts.duck_debugger_prompt import DUCK_SYSTEM_PROMPT, format_duck_prompt, SocraticResponse
from agent.nodes.custom_debugger import get_llm, are_tests_compatible
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
        raw_tests = request.user_tests or request.tests or ""
        compatible_tests = raw_tests if are_tests_compatible(request.code, raw_tests) else ""

        results = list(run_custom_fix(
            code=request.code,
            language=target_lang,
            expected_behavior=request.expected_behavior or "",
            error_message=request.error_message or "",
            user_tests=compatible_tests,
        ))

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/repair/stream")
async def repair_code_stream(request: RepairRequest):
    """
    Non-blocking Server-Sent Events (SSE) streaming endpoint for autonomous repair.
    Yields intermediate node states (diagnosing, generating_tests, fixing, testing, done)
    incrementally to eliminate UI freezes and sudden code flashes.
    """
    try:
        input_hint = request.language or request.lang or ""
        target_lang = detect_language(request.code, hint=input_hint)

        raw_tests = request.user_tests or request.tests or ""
        compatible_tests = raw_tests if are_tests_compatible(request.code, raw_tests) else ""

        async def event_generator():
            queue: asyncio.Queue = asyncio.Queue()
            loop = asyncio.get_running_loop()

            def worker():
                try:
                    for step in run_custom_fix(
                        code=request.code,
                        language=target_lang,
                        expected_behavior=request.expected_behavior or "",
                        error_message=request.error_message or "",
                        user_tests=compatible_tests,
                    ):
                        loop.call_soon_threadsafe(queue.put_nowait, ("event", step))
                    loop.call_soon_threadsafe(queue.put_nowait, ("done", None))
                except Exception as ex:
                    loop.call_soon_threadsafe(queue.put_nowait, ("error", str(ex)))

            # Execute synchronous generator in worker thread so event loop remains free
            loop.run_in_executor(None, worker)

            while True:
                msg_type, payload = await queue.get()
                if msg_type == "event":
                    yield f"data: {json.dumps(payload)}\n\n"
                elif msg_type == "error":
                    yield f"data: {json.dumps({'stage': 'error', 'error': payload})}\n\n"
                    break
                elif msg_type == "done":
                    yield "data: [DONE]\n\n"
                    break

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*",
            },
        )
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
        compatible_tests = request.tests if are_tests_compatible(request.code, request.tests) else ""
        user_prompt = format_duck_prompt(
            code=request.code,
            tests=compatible_tests,
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

@app.post("/duck_chat/stream")
async def duck_chat_stream(request: DuckChatRequest):
    """
    Non-blocking SSE streaming endpoint for Duck Debugger.
    Streams immediate pondering indicator, internal critic monologue, and response chunks.
    """
    try:
        input_hint = request.language or request.lang or ""
        target_lang = detect_language(request.code, hint=input_hint)

        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in duck_sessions:
            duck_sessions[session_id] = {
                "history": [],
                "level": 1,
                "language": target_lang
            }

        session = duck_sessions[session_id]
        session["language"] = target_lang

        frustration_keywords = ["stupid", "just tell me", "give up", "i dont get it", "im stuck"]
        is_frustrated = any(kw in request.user_message.lower() for kw in frustration_keywords)
        turn_count = len([m for m in session["history"] if m["role"] == "user"])
        if is_frustrated or (turn_count > 0 and turn_count % 2 == 0):
            session["level"] = min(3, session["level"] + 1)

        compatible_tests = request.tests if are_tests_compatible(request.code, request.tests) else ""
        user_prompt = format_duck_prompt(
            code=request.code,
            tests=compatible_tests,
            user_message=request.user_message,
            history=session["history"],
            level=session["level"],
            language=target_lang
        )

        async def duck_event_generator():
            # Immediate feedback so UI knows request is received
            yield f"data: {json.dumps({'stage': 'pondering', 'session_id': session_id, 'level': session['level']})}\n\n"

            loop = asyncio.get_running_loop()

            def invoke_llm():
                llm = get_llm()
                structured_llm = llm.with_structured_output(SocraticResponse)
                messages = [
                    ("system", DUCK_SYSTEM_PROMPT),
                    ("human", user_prompt),
                ]
                return structured_llm.invoke(messages)

            try:
                response: SocraticResponse = await loop.run_in_executor(None, invoke_llm)

                session["history"].append({"role": "user", "content": request.user_message})
                session["history"].append({"role": "assistant", "content": response.response_text})

                if response.critic_monologue:
                    yield f"data: {json.dumps({'stage': 'critic', 'critic_monologue': response.critic_monologue})}\n\n"

                # Stream response tokens/words for smooth incremental rendering
                words = response.response_text.split(" ")
                chunk_size = 2
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i + chunk_size])
                    if i + chunk_size < len(words):
                        chunk += " "
                    yield f"data: {json.dumps({'stage': 'chunk', 'text': chunk})}\n\n"
                    await asyncio.sleep(0.015)

                yield f"data: {json.dumps({'stage': 'done', 'session_id': session_id, 'response': response.response_text, 'level': response.current_level, 'is_solution_unlocked': response.is_solution_unlocked, 'critic_monologue': response.critic_monologue})}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as err:
                yield f"data: {json.dumps({'stage': 'error', 'error': str(err)})}\n\n"

        return StreamingResponse(
            duck_event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static web UI files so root "/" serves index.html and web assets directly
WEB_DIR = ROOT / "web"
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
