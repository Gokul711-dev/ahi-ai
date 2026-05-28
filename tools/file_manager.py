"""
tools/file_manager.py
Filesystem read/write/list operations.
"""
from pathlib import Path


def read_file(path: str) -> str:
    try:
        p = Path(path)
        if not p.exists():
            return f"[Error] File not found: {path}"
        if not p.is_file():
            return f"[Error] Path is not a file: {path}"
        return p.read_text(encoding="utf-8")
    except Exception as e:
        return f"[Error] {e}"


def write_file(path: str, content: str) -> str:
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"[OK] Written {len(content)} characters to {path}"
    except Exception as e:
        return f"[Error] {e}"


def list_directory(path: str = ".") -> str:
    try:
        p = Path(path)
        if not p.exists():
            return f"[Error] Path not found: {path}"
        items = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        lines = [f"📁 {path}/"]
        for item in items:
            if item.is_dir():
                lines.append(f"  📂 {item.name}/")
            else:
                size = item.stat().st_size
                lines.append(f"  📄 {item.name} ({size:,} bytes)")
        return "\n".join(lines)
    except Exception as e:
        return f"[Error] {e}"


def append_to_file(path: str, content: str) -> str:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"[OK] Appended {len(content)} characters to {path}"
    except Exception as e:
        return f"[Error] {e}"
