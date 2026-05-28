"""
brain/orchestrator.py
Core agent loop: Intent → Route → Prompt → Tool Loop → Respond
"""
import json
from ollama import Client

from utils.logger import get_logger
from utils.security import require_approval
from brain.intent_classifier import IntentClassifier
from brain.model_router import ModelRouter
from brain.personality_engine import PersonalityEngine
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.project_state import ProjectState
from tools.tool_registry import ToolRegistry

logger = get_logger("Orchestrator")

MAX_TOOL_ITERATIONS = 6  # Safety limit to prevent infinite loops


class JaneOrchestrator:
    def __init__(self, config: dict):
        self.config = config
        self.client = Client(host=config.get("ollama", {}).get("base_url", "http://localhost:11434"))

        # Subsystems
        self.intent = IntentClassifier()
        self.router = ModelRouter(config)
        self.persona = PersonalityEngine(config)
        self.short_memory = ShortTermMemory(
            filepath=config.get("memory", {}).get("short_term", {}).get("filepath", "data/short_term.json"),
            buffer_size=config.get("memory", {}).get("short_term", {}).get("buffer_size", 20),
        )
        self.long_memory = LongTermMemory(config)
        self.project_state = ProjectState(
            filepath=config.get("memory", {}).get("project_state", {}).get("filepath", "data/project_state.json")
        )

        from teacher.teaching_loop import init_teaching_tools
        init_teaching_tools(config, self.long_memory)

        self.tools = ToolRegistry(config)
        logger.info("JaneOrchestrator initialized successfully.")

    def process(self, user_input: str) -> str:
        """Main processing loop for a user message. Returns Jane's response."""
        stripped = user_input.strip()
        logger.info(f"User Input: {stripped}")

        # ── 1. Retrieve context ────────────────────────────────────────────
        relevant_docs = self.long_memory.format_for_prompt(stripped)
        project_ctx = self.project_state.format_for_prompt()
        short_ctx = self.short_memory.format_for_prompt(n=8)

        # ── 2. Classify intent ────────────────────────────────────────────
        intent = self.intent.classify(stripped)
        logger.info(f"Intent: {intent.category} (conf: {intent.confidence:.2f}) | keywords: {intent.keywords[:3]}")

        # ── 3. Route to model ──────────────────────────────────────────────
        model_name = self.router.get_model(intent.category)
        logger.info(f"Model: {model_name}")

        # ── 4. Build system prompt ─────────────────────────────────────────
        system_prompt = self.persona.build_prompt(
            tool_descriptions=self.tools.get_descriptions_text(),
            short_memory=short_ctx,
            long_memory=relevant_docs,
            project_context=project_ctx,
            intent_category=intent.category,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": stripped},
        ]

        # ── 5. LLM + tool loop ─────────────────────────────────────────────
        tool_defs = self.tools.get_definitions()
        iterations = 0
        final_text = ""

        try:
            response = self.client.chat(
                model=model_name,
                messages=messages,
                tools=tool_defs,
            )

            while response.message.tool_calls and iterations < MAX_TOOL_ITERATIONS:
                iterations += 1
                messages.append(response.message)

                for tool_call in response.message.tool_calls:
                    t_name = tool_call.function.name
                    t_args = tool_call.function.arguments or {}

                    # Ensure args is a dict
                    if isinstance(t_args, str):
                        try:
                            t_args = json.loads(t_args)
                        except json.JSONDecodeError:
                            t_args = {}

                    logger.info(f"Tool Call [{iterations}]: {t_name}({t_args})")

                    result_str = self.tools.execute(t_name, t_args, approval_fn=require_approval)
                    logger.info(f"Tool Result: {result_str[:120]}...")

                    messages.append({
                        "role": "tool",
                        "content": result_str,
                        "name": t_name,
                    })

                response = self.client.chat(
                    model=model_name,
                    messages=messages,
                    tools=tool_defs,
                )

            if iterations >= MAX_TOOL_ITERATIONS:
                logger.warning("Tool loop hit iteration limit — forcing final response.")

            final_text = response.message.content or ""

        except Exception as e:
            logger.error(f"LLM Error: {e}", exc_info=True)
            final_text = (
                f"*settles back in chair*\n\n"
                f"My apologies — I encountered a disturbance in my mental palace. "
                f"The error reads: `{e}`. "
                f"Check that Ollama is running and the model is pulled."
            )

        # ── 6. Persist to memory ───────────────────────────────────────────
        self.short_memory.add(stripped, final_text)
        self.long_memory.add_interaction(stripped, final_text)

        logger.info("Processing complete.")
        return final_text
