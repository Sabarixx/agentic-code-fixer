"""File writer tool for persisting generated agent code implementations."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = ROOT / "generated"


def write_code_to_file(
    spec_id: str,
    attempt_n: int,
    code: str,
    output_dir: Path | None = None,
) -> Path:
    """Write generated python code string to generated/{spec_id}_attempt_{attempt_n}.py."""
    target_dir = output_dir or GENERATED_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{spec_id}_attempt_{attempt_n}.py"
    filepath = target_dir / filename
    filepath.write_text(code, encoding="utf-8")
    return filepath
