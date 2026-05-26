"""
brain/orchestrator.py
Core agent loop: Intent -> Route -> Prompt -> Execute Tools -> Respond
"""
import json
from ollama import Client, chat

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


class JaneOrchestrator:
    def __init__(self, config: dict):
        self.config = config
        self.client = Client(host=config.get("ollama", {}).get("base_url", "http://localhost:11434"))

        # Subsystems
        self.intent = IntentClassifier()
        self.router = ModelRouter(config)
        self.persona = PersonalityEngine(config)
        self.short_memory = ShortTermMemory(
            filepath=config.get("memory", {}).get("short_term", {}).get("filepath"),
            buffer_size=config.get("memory", {}).get("short_term", {}).get("buffer_size", 20),
        )
        self.long_memory = LongTermMemory(config)
        self.project_state = ProjectState(
            filepath=config.get("memory", {}).get("project_state", {}).get("filepath")
        )
        from teacher.teaching_loop import init_teaching_tools
        init_teaching_tools(config, self.long_memory)
        self.tools = ToolRegistry(config)

    def process(self, user_input: str) -> str:
        """Main processing loop for a user message."""
        logger.info(f"User Input: {user_input}")

        # 1. Retrieve context
        relevant_docs = self.long_memory.format_for_prompt(user_input)
        project_ctx = self.project_state.format_for_prompt()
        short_ctx = self.short_memory.format_for_prompt(n=10)

        # 2. Classify intent
        intent = self.intent.classify(user_input)
        logger.info(f"Intent: {intent.category} (conf: {intent.confidence:.2f})")

        # 3. Route to model
        model_name = self.router.get_model(intent.category)
        logger.info(f"Routing to model: {model_name}")

        # 4. Build system prompt
        system_prompt = self.persona.build_prompt(
            tool_descriptions=self.tools.get_descriptions_text(),
            short_memory=short_ctx,
            long_memory=relevant_docs,
            project_context=project_ctx,
            intent_category=intent.category,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

        # 5. Call LLM (Tool loop)
        tool_defs = self.tools.get_definitions()
        
        try:
            # First pass
            response = self.client.chat(
                model=model_name,
                messages=messages,
                tools=tool_defs,
            )
            
            # Handle tool calls if any
            while response.message.tool_calls:
                messages.append(response.message)
                
                for tool_call in response.message.tool_calls:
                    t_name = tool_call.function.name
                    t_args = tool_call.function.arguments
                    logger.info(f"Tool Call: {t_name}({t_args})")
                    
                    # Execute tool (with approval if needed)
                    result_str = self.tools.execute(t_name, t_args, approval_fn=require_approval)
                    logger.info(f"Tool Result: {result_str[:100]}...")
                    
                    messages.append({
                        "role": "tool",
                        "content": result_str,
                        "name": t_name
                    })
                
                # Call LLM again with tool results
                response = self.client.chat(
                    model=model_name,
                    messages=messages,
                    tools=tool_defs,
                )
                
            final_text = response.message.content
            
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            final_text = f"My apologies, I encountered a disturbance in my mental palace: {e}"

        # 7. Update memories
        self.short_memory.add(user_input, final_text)
        self.long_memory.add_interaction(user_input, final_text)

        logger.info("Processing complete.")
        return final_text
