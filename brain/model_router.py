"""
brain/model_router.py
Routes requests to the best local model based on intent category.
"""


class ModelRouter:
    def __init__(self, config: dict = None):
        self.config = config or {}
        models = self.config.get("ollama", {}).get("models", {})
        self.general_model = models.get("general", "llama3.1:latest")
        self.code_model = models.get("code", "qwen2.5-coder:7b")

        # Intent → model mapping
        self._routing_map = {
            "coding": self.code_model,
            "cyber": self.code_model,  # technical; coder model handles it well
        }

    def get_model(self, intent_category: str) -> str:
        """Return the best model for a given intent category."""
        return self._routing_map.get(intent_category, self.general_model)
