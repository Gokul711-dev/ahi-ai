"""
brain/model_router.py
Selects the best Ollama model based on intent.
"""

class ModelRouter:
    def __init__(self, config: dict = None):
        self.config = config or {}
        models = self.config.get("ollama", {}).get("models", {})
        self.general_model = models.get("general", "llama3.1:latest")
        self.code_model = models.get("code", "qwen2.5-coder:7b")

    def get_model(self, intent_category: str) -> str:
        """Route to the appropriate model based on intent."""
        if intent_category == "coding":
            return self.code_model
        return self.general_model
