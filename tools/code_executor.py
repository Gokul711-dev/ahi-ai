"""
tools/code_executor.py
Safe Python code execution in a subprocess sandbox.
"""
import os
import subprocess
import tempfile
from pathlib import Path

MAX_OUTPUT_CHARS = 2000
DEFAULT_TIMEOUT = 10


def execute_python(code: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """
    Execute Python code in a subprocess and return the output.
    Requires user approval before calling (enforced by ToolRegistry).
    """
    # Write to temp file
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
        # Truncate if too long
        if len(output) > MAX_OUTPUT_CHARS:
            output = output[:MAX_OUTPUT_CHARS] + "\n...[output truncated]"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return f"[Timeout] Code execution exceeded {timeout} seconds."
    except Exception as e:
        return f"[Exception] {e}"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def format_code_for_display(code: str) -> str:
    """Wrap code in a markdown code block for display."""
    return f"```python\n{code}\n```"
