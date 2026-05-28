"""
utils/security.py
Input sanitization and user approval gates.
"""
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm

console = Console()

BLOCKED_PATTERNS = [
    "rm -rf",
    "format c:",
    "del /s /q",
    "shutdown",
    "__import__('os').system",
    "subprocess.call",
]


def sanitize_input(text: str) -> str:
    cleaned = text
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in cleaned.lower():
            cleaned = cleaned.replace(pattern, "[REDACTED]")
    return cleaned


def check_path_permission(path: str, allowed_dirs: list[str] = None) -> bool:
    if allowed_dirs is None:
        allowed_dirs = [".", "knowledge/sources", "data"]
    resolved = Path(path).resolve()
    for allowed in allowed_dirs:
        try:
            resolved.relative_to(Path(allowed).resolve())
            return True
        except ValueError:
            continue
    return False


def require_approval(action_description: str) -> bool:
    """Prompt user for Y/N before a sensitive action."""
    console.print(f"\n[bold yellow]⚠  Approval Required[/bold yellow]")
    console.print(f"[dim]Action:[/dim] {action_description}")
    return Confirm.ask("[bold]Approve?[/bold]")
