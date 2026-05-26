"""
utils/security.py
Input sanitization, path permission checks, and approval gates.
"""
import os
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm

console = Console()

# Patterns that are never allowed in user input passed to shell/exec
BLOCKED_PATTERNS = [
    "rm -rf",
    "format c:",
    "del /s /q",
    "shutdown",
    "__import__('os').system",
    "subprocess.call",
    "eval(",
    "exec(",
]


def sanitize_input(text: str) -> str:
    """Strip dangerous patterns from user text before passing to tools."""
    cleaned = text
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in cleaned.lower():
            cleaned = cleaned.replace(pattern, "[REDACTED]")
    return cleaned


def check_path_permission(path: str, allowed_dirs: list[str] = None) -> bool:
    """Ensure a file path stays within allowed directories."""
    if allowed_dirs is None:
        allowed_dirs = [".", "knowledge/sources", "data"]

    resolved = Path(path).resolve()
    for allowed in allowed_dirs:
        allowed_resolved = Path(allowed).resolve()
        try:
            resolved.relative_to(allowed_resolved)
            return True
        except ValueError:
            continue
    return False


def require_approval(action_description: str) -> bool:
    """Prompt user for explicit Y/N confirmation before a sensitive action."""
    console.print(f"\n[bold yellow]⚠ Approval Required[/bold yellow]")
    console.print(f"[dim]Action:[/dim] {action_description}")
    return Confirm.ask("[bold]Do you approve this action?[/bold]")
