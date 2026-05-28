"""
memory/project_state.py
Tracks active projects and goals across sessions.
"""
import json
import time
from pathlib import Path
from typing import Optional


class ProjectState:
    def __init__(self, filepath: str = "data/project_state.json"):
        self.filepath = Path(filepath)
        self._state = self._load()

    def _load(self) -> dict:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {"active": None, "projects": {}}

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._state, f, indent=2, ensure_ascii=False)

    def set_project(self, name: str, goal: str = "", tech_stack: list = None):
        self._state["active"] = name
        if name not in self._state["projects"]:
            self._state["projects"][name] = {
                "name": name,
                "goal": goal,
                "tech_stack": tech_stack or [],
                "recent_files": [],
                "notes": [],
                "created_at": time.time(),
                "last_active": time.time(),
            }
        else:
            self._state["projects"][name]["last_active"] = time.time()
            if goal:
                self._state["projects"][name]["goal"] = goal
        self._save()

    def get_project(self, name: str = None) -> Optional[dict]:
        key = name or self._state.get("active")
        if not key:
            return None
        return self._state["projects"].get(key)

    def get_active(self) -> Optional[dict]:
        return self.get_project()

    def update_goal(self, goal: str):
        active = self._state.get("active")
        if active and active in self._state["projects"]:
            self._state["projects"][active]["goal"] = goal
            self._save()

    def add_note(self, note: str):
        active = self._state.get("active")
        if active and active in self._state["projects"]:
            self._state["projects"][active]["notes"].append(
                {"text": note, "timestamp": time.time()}
            )
            self._save()

    def add_recent_file(self, filepath: str):
        active = self._state.get("active")
        if active and active in self._state["projects"]:
            files = self._state["projects"][active]["recent_files"]
            if filepath not in files:
                files.insert(0, filepath)
                self._state["projects"][active]["recent_files"] = files[:10]
            self._save()

    def list_projects(self) -> list[dict]:
        return list(self._state["projects"].values())

    def format_for_prompt(self) -> str:
        project = self.get_active()
        if not project:
            return ""
        lines = [
            f"Active Project: {project['name']}",
            f"Goal: {project.get('goal', 'Not set')}",
        ]
        if project.get("tech_stack"):
            lines.append(f"Tech Stack: {', '.join(project['tech_stack'])}")
        if project.get("recent_files"):
            lines.append(f"Recent Files: {', '.join(project['recent_files'][:3])}")
        if project.get("notes"):
            lines.append(f"Last Note: {project['notes'][-1]['text']}")
        return "\n".join(lines)
