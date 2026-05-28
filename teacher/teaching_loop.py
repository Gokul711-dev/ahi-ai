"""
teacher/teaching_loop.py
Teaching engine tools — curriculum generation via LLM.
"""
from teacher.curriculum_builder import CurriculumBuilder

_builder = None
_long_memory = None


def init_teaching_tools(config: dict, long_memory):
    global _builder, _long_memory
    _builder = CurriculumBuilder(config)
    _long_memory = long_memory


def start_curriculum(topic: str) -> str:
    if not _builder:
        return "[Error] Teaching tools not initialized."
    existing = _builder.load_roadmap(topic)
    if existing:
        phases = [p["name"] for p in existing.get("phases", [])]
        return f"Loaded existing roadmap for '{topic}'. Phases: {phases}"
    roadmap = _builder.build_roadmap(topic)
    if "error" in roadmap:
        return f"Failed to build roadmap: {roadmap['error']}"
    phases = [p["name"] for p in roadmap.get("phases", [])]
    return f"Created new roadmap for '{topic}'. Phases: {phases}"


def get_curriculum(topic: str) -> str:
    if not _builder:
        return "[Error] Teaching tools not initialized."
    roadmap = _builder.load_roadmap(topic)
    if not roadmap:
        return f"No saved roadmap found for '{topic}'. Use start_curriculum first."
    import json
    return json.dumps(roadmap, indent=2)


def record_weak_point(concept: str) -> str:
    if not _long_memory:
        return "[Error] Long-term memory not initialized."
    text = f"USER WEAK POINT: {concept}"
    _long_memory.add_document(text, metadata={"type": "weak_point"})
    return f"Recorded '{concept}' as a weak point for future spaced repetition."
