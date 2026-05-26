"""
brain/intent_classifier.py
Fast, rule-based + keyword intent detection.
"""
from dataclasses import dataclass
import re


@dataclass
class Intent:
    category: str
    confidence: float
    keywords: list[str]


class IntentClassifier:
    def __init__(self):
        # Patterns and keywords for each intent category
        self.categories = {
            "coding": {
                "keywords": ["code", "script", "function", "debug", "python", "html", "css", "javascript", "refactor", "error", "bug", "compile"],
                "patterns": [r"write a \w+", r"how to (code|build|program)"],
            },
            "teaching": {
                "keywords": ["teach", "learn", "explain", "understand", "what is", "how does", "tutorial", "guide", "curriculum"],
                "patterns": [r"teach me \w+", r"how does \w+ work"],
            },
            "web_search": {
                "keywords": ["search", "find", "google", "look up", "duckduckgo", "who is", "what is the current", "latest"],
                "patterns": [r"search for \w+", r"look up \w+"],
            },
            "news": {
                "keywords": ["news", "latest news", "headlines", "what's happening", "update me on"],
                "patterns": [r"news about \w+", r"latest on \w+"],
            },
            "cyber": {
                "keywords": ["nmap", "scan", "hack", "cyber", "security", "xss", "sql injection", "whois", "dns", "ip lookup"],
                "patterns": [r"scan \w+", r"what port is \w+"],
            },
            "system_info": {
                "keywords": ["system", "ram", "cpu", "disk", "uptime", "status", "how is my computer"],
                "patterns": [r"system (status|info)", r"how much ram"],
            },
            "project_mgmt": {
                "keywords": ["project", "goal", "status", "what are we working on", "current project"],
                "patterns": [r"(new|start) project", r"set goal to"],
            }
        }

    def classify(self, text: str) -> Intent:
        """Classify user input into an intent category."""
        text = text.lower()
        best_category = "general_chat"
        max_score = 0
        matched_keywords = []

        for category, rules in self.categories.items():
            score = 0
            cat_matches = []

            # Check keywords
            for kw in rules["keywords"]:
                if kw in text:
                    # Exact word match is better than substring
                    if re.search(rf"\b{kw}\b", text):
                        score += 2
                    else:
                        score += 1
                    cat_matches.append(kw)

            # Check regex patterns
            for pattern in rules["patterns"]:
                if re.search(pattern, text):
                    score += 3
                    cat_matches.append(pattern)

            if score > max_score:
                max_score = score
                best_category = category
                matched_keywords = cat_matches

        # Normalize confidence (max out at 1.0)
        confidence = min(max_score / 5.0, 1.0)

        # If confidence is too low, default to general chat
        if confidence < 0.2:
            return Intent(category="general_chat", confidence=1.0, keywords=[])

        return Intent(category=best_category, confidence=confidence, keywords=matched_keywords)
