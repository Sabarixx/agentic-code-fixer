"""Pytest test suite for Coder Node and File Writer Tool."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import pytest

from agent.nodes.coder import coder_node, extract_code_block, validate_code_ast
from agent.state import initial_state
from tools.file_writer import write_code_to_file

ROOT = Path(__file__).resolve().parent.parent
SPEC_FILES = sorted((ROOT / "specs").glob("spec_*.json"))


def test_extract_code_block_fenced_python():
    raw = "Here is the solution:\n```python\ndef foo():\n    return 42\n```\nHope this helps!"
    extracted = extract_code_block(raw)
    assert extracted == "def foo():\n    return 42"


def test_extract_code_block_generic_fence():
    raw = "```\ndef bar():\n    pass\n```"
    extracted = extract_code_block(raw)
    assert extracted == "def bar():\n    pass"


def test_extract_code_block_unfenced():
    raw = "def baz():\n    return True"
    extracted = extract_code_block(raw)
    assert extracted == "def baz():\n    return True"


def test_validate_code_ast_valid():
    is_valid, err = validate_code_ast("x = 1 + 2\nprint(x)")
    assert is_valid is True
    assert err == ""


def test_validate_code_ast_invalid():
    is_valid, err = validate_code_ast("def broken_func(:")
    assert is_valid is False
    assert "SyntaxError" in err


def test_file_writer_tool(tmp_path: Path):
    filepath = write_code_to_file("spec_test", 1, "def test_fn(): pass\n", output_dir=tmp_path)
    assert filepath.exists()
    assert filepath.name == "spec_test_attempt_1.py"
    assert filepath.read_text(encoding="utf-8") == "def test_fn(): pass\n"


@pytest.mark.parametrize("spec_path", SPEC_FILES, ids=lambda p: p.stem)
def test_coder_node_generates_valid_code_and_file(spec_path: Path):
    """Test coder_node produces syntactically valid code and writes a file for each spec."""
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec_id = spec.get("id", spec_path.stem)

    dummy_plan = {
        "approach": f"Implement {spec_id} algorithm according to signature.",
        "edge_cases": ["empty input"],
        "complexity_target": "O(N) Time",
    }

    state = initial_state(spec)
    state["plan"] = dummy_plan

    result = coder_node(state)

    assert result["status"] == "coding"
    code = result["code"]
    assert isinstance(code, str) and len(code) > 0

    # Validate AST
    is_valid, ast_err = validate_code_ast(code)
    assert is_valid is True, f"AST validation failed for {spec_id}: {ast_err}"

    # Verify generated file was written
    generated_file = ROOT / "generated" / f"{spec_id}_attempt_{result['iteration_count']}.py"
    assert generated_file.exists(), f"Expected generated file missing: {generated_file}"
