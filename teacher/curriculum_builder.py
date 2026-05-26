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
        self.client = Client(host=self.config.get("ollama", {}).get("base_url", "http://localhost:11434"))
        self.model = self.config.get("ollama", {}).get("models", {}).get("general", "llama3.1:latest")
        self.storage_dir = Path("data/curricula")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def build_roadmap(self, topic: str) -> dict:
        """Ask LLM to generate a structured JSON roadmap for a topic."""
        prompt = f"""
You are an expert educator. Create a comprehensive learning roadmap for the topic: "{topic}".
Break it down into 3 phases: Beginner, Intermediate, Advanced.
Return ONLY valid JSON in this exact structure:
{{
  "topic": "{topic}",
  "phases": [
    {{
      "name": "Beginner",
      "modules": [
        {{"title": "Module 1", "description": "What to learn here"}},
        {{"title": "Module 2", "description": "What to learn here"}}
      ]
    }}
  ]
}}
Do not include markdown blocks or any other text. Just the JSON object.
"""
        try:
            response = self.client.generate(model=self.model, prompt=prompt)
            text = response.response.strip()
            # Try to strip markdown if the model ignored instructions
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
            
            data = json.loads(text.strip())
            data["created_at"] = time.time()
            data["progress"] = {}  # To track completion
            
            # Save to disk
            safe_name = "".join([c if c.isalnum() else "_" for c in topic]).strip("_")
            filepath = self.storage_dir / f"{safe_name}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            return data
        except Exception as e:
            return {"error": str(e), "topic": topic}

    def load_roadmap(self, topic: str) -> dict:
        safe_name = "".join([c if c.isalnum() else "_" for c in topic]).strip("_")
        filepath = self.storage_dir / f"{safe_name}.json"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
