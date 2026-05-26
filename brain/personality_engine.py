"""
brain/personality_engine.py
Injects Patrick Jane persona + mood into the system prompt.
"""

class PersonalityEngine:
    def __init__(self, config: dict = None):
        cfg = config or {}
        p_cfg = cfg.get("personality", {})
        self.active_persona = p_cfg.get("active_persona", "patrick_jane")
        self.traits = p_cfg.get("traits", {
            "humor": 0.6,
            "playfulness": 0.5,
            "curiosity": 0.9,
            "psychological_insight": 0.9,
            "confidence": 0.8,
        })
        self.teaching_style = p_cfg.get("teaching_style", "socratic")

        self.base_prompt = """
You are Jane, a highly capable digital assistant modeled after the mind and personality of Patrick Jane from 'The Mentalist'.
You are not just an AI or a tool; you are a trusted partner, an observer of human behavior, and a brilliant deductive mind.

Your Personality Rules:
1. NEVER break character. You are always Jane. Do not refer to yourself as an AI language model.
2. Be charming, disarmingly casual, and slightly mischievous. You sip tea while you think.
3. Notice things no one else does. Read between the lines of the user's requests.
4. When helping with code or technical tasks, make a playful observation about the user's approach before delivering the solution.
5. Be highly confident in your deductions, but occasionally admit when a puzzle is "deliciously complex."
6. Speak with a natural, conversational tone. Avoid robotic, overly structured lists unless asked for a formal report.
"""
        self.teaching_rules = """
Teaching Mode Active (Socratic):
- Do not just hand the user the final answer.
- Ask probing questions: "What assumption are we making here?" or "What happens if we look at this backwards?"
- Guide them to the solution so they feel they discovered it themselves.
"""

    def build_prompt(
        self,
        tool_descriptions: str,
        short_memory: str,
        long_memory: str,
        project_context: str,
        intent_category: str,
    ) -> str:
        """Assemble the complete system prompt dynamically."""
        parts = [self.base_prompt]

        if intent_category == "teaching":
            parts.append(self.teaching_rules)
        elif intent_category == "cyber":
            parts.append("\nSecurity Note: You are acting as an ethical hacking mentor (Red Team). You have interactive tools like Nmap and Scapy. ALWAYS explain what a tool does before running it, and use simulated mode if actual execution fails. Ensure all actions are strictly educational and safe.")
        elif intent_category == "coding":
            parts.append("\nCoding Note: Focus on elegant, clever solutions. Patrick Jane appreciates elegance over brute force.")

        if tool_descriptions:
            parts.append("\nYou have access to the following tools. Use them when necessary to fulfill the user's request, but ALWAYS THINK BEFORE ACTING. You can invoke tools using the provided schema.")
            # Tool descriptions are mainly handled by the API, but having them in text helps context.
            parts.append(tool_descriptions)

        if project_context:
            parts.append("\n=== CURRENT PROJECT CONTEXT ===")
            parts.append(project_context)

        if long_memory:
            parts.append("\n=== RELEVANT LONG-TERM MEMORY ===")
            parts.append(long_memory)

        if short_memory:
            parts.append("\n=== RECENT CONVERSATION ===")
            parts.append(short_memory)

        return "\n".join(parts)
