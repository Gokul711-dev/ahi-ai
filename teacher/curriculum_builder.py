"""
teacher/curriculum_builder.py
Generates learning roadmaps using the LLM.
"""
import json
import time
from pathlib import Path
from ollama import Client


class CurriculumBuilder:
    def __init__(self, config: dict = None):
        self.config = config or {}
        ollama_cfg = self.config.get("ollama", {})
        self.client = Client(host=ollama_cfg.get("base_url", "http://localhost:11434"))
        self.model = ollama_cfg.get("models", {}).get("general", "llama3.1:latest")
        self.storage_dir = Path("data/curricula")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def build_roadmap(self, topic: str) -> dict:
        """Ask the LLM to generate a structured JSON learning roadmap."""
        prompt = f"""You are an expert educator. Create a comprehensive learning roadmap for: "{topic}".
Break it into 3 phases: Beginner, Intermediate, Advanced.
Return ONLY valid JSON in this exact structure, no markdown, no extra text:
{{
  "topic": "{topic}",
  "phases": [
    {{
      "name": "Beginner",
      "modules": [
        {{"title": "Module 1", "description": "What to learn here"}},
        {{"title": "Module 2", "description": "What to learn here"}}
      ]
    }},
    {{
      "name": "Intermediate",
      "modules": [
        {{"title": "Module 1", "description": "What to learn here"}}
      ]
    }},
    {{
      "name": "Advanced",
      "modules": [
        {{"title": "Module 1", "description": "What to learn here"}}
      ]
    }}
  ]
}}"""
        try:
            response = self.client.generate(model=self.model, prompt=prompt)
            text = response.response.strip()
            # Strip markdown fences if model ignored instructions
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

            data = json.loads(text.strip())
            data["created_at"] = time.time()
            data["progress"] = {}

            safe_name = "".join(c if c.isalnum() else "_" for c in topic).strip("_")
            filepath = self.storage_dir / f"{safe_name}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return data
        except Exception as e:
            return {"error": str(e), "topic": topic}

    def load_roadmap(self, topic: str) -> dict | None:
        safe_name = "".join(c if c.isalnum() else "_" for c in topic).strip("_")
        filepath = self.storage_dir / f"{safe_name}.json"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
