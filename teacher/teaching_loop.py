"""
teacher/teaching_loop.py
Exposes teaching engine tools for the LLM.
"""
from teacher.curriculum_builder import CurriculumBuilder

# Global instances for tools to use
_builder = None
_long_memory = None

def init_teaching_tools(config: dict, long_memory):
    global _builder, _long_memory
    _builder = CurriculumBuilder(config)
    _long_memory = long_memory

def start_curriculum(topic: str) -> str:
    """Generate a learning roadmap for a topic."""
    if not _builder:
        return "[Error] Teaching tools not initialized."
    
    existing = _builder.load_roadmap(topic)
    if existing:
        return f"Loaded existing roadmap for {topic}. Phases: {[p['name'] for p in existing.get('phases', [])]}"
        
    roadmap = _builder.build_roadmap(topic)
    if "error" in roadmap:
        return f"Failed to build roadmap: {roadmap['error']}"
        
    return f"Created new roadmap for {topic}. Phases: {[p['name'] for p in roadmap.get('phases', [])]}"

def get_curriculum(topic: str) -> str:
    """View the current roadmap for a topic."""
    if not _builder:
        return "[Error] Teaching tools not initialized."
    roadmap = _builder.load_roadmap(topic)
    if not roadmap:
        return f"No roadmap found for {topic}."
    
    import json
    return json.dumps(roadmap, indent=2)

def record_weak_point(concept: str) -> str:
    """Record a user's weak point into long-term memory for spaced repetition."""
    if not _long_memory:
        return "[Error] Long term memory not initialized."
    
    # We store it with a specific tag
    text = f"USER WEAK POINT: {concept}"
    _long_memory.add_document(text, metadata={"type": "weak_point"})
    return f"Recorded '{concept}' as a weak point for future review."
