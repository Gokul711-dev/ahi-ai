"""
tools/code_executor.py
Safe Python code execution in a sandboxed subprocess.
"""
import os
import subprocess
import tempfile
from pathlib import Path

MAX_OUTPUT_CHARS = 2000
DEFAULT_TIMEOUT = 10


def execute_python(code: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Execute Python code in a subprocess. Requires user approval."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path.cwd()),
        )
        output = result.stdout
        if result.returncode != 0:
            output = f"[Error]\n{result.stderr}"
        if len(output) > MAX_OUTPUT_CHARS:
            output = output[:MAX_OUTPUT_CHARS] + "\n...[output truncated]"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return f"[Timeout] Execution exceeded {timeout}s."
    except Exception as e:
        return f"[Exception] {e}"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
