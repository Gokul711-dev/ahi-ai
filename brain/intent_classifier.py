"""
brain/intent_classifier.py
Intent detection using weighted keyword scoring + regex patterns.
Handles ambiguous inputs gracefully and avoids false positives.
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
        # Each category has: keywords (weight 1), strong_keywords (weight 3), patterns (weight 4)
        self.categories = {
            "coding": {
                "keywords": ["code", "script", "function", "debug", "python", "html", "css",
                             "javascript", "refactor", "bug", "compile", "algorithm", "class",
                             "method", "variable", "loop", "array", "json", "api", "import"],
                "strong_keywords": ["write a program", "fix this code", "implement", "chatbot.py",
                                    "create a script", "build a function", ".py", "syntax error"],
                "patterns": [
                    r"write (a |an )?\w+ (in |using )?(python|js|javascript|c\+\+|java)",
                    r"how (do i|to) (code|build|program|implement|create) \w+",
                    r"debug (this|my|the) (code|script|function|program)",
                    r"(create|make|build) (a )?(chatbot|script|program|app|tool)(\.py)?",
                    r"(fix|solve) (this |the )?(error|bug|exception|issue)",
                ],
            },
            "teaching": {
                "keywords": ["teach", "learn", "explain", "understand", "tutorial", "guide",
                             "curriculum", "how does", "what is", "study", "master", "course"],
                "strong_keywords": ["teach me", "how does it work", "explain to me",
                                    "learning roadmap", "beginner guide", "step by step"],
                "patterns": [
                    r"teach (me |us )?\w+",
                    r"how does \w+ work",
                    r"(explain|describe) (how |what |why )?\w+",
                    r"(i want to|help me) (learn|understand|master) \w+",
                    r"(what|why|how) (is|are|does|do) .+\?",
                ],
            },
            "cyber": {
                "keywords": ["nmap", "scan", "hack", "cyber", "security", "xss", "sql injection",
                             "whois", "dns", "ip lookup", "port", "exploit", "vulnerability",
                             "pentest", "firewall", "malware", "phishing", "mitm", "attack"],
                "strong_keywords": ["ethical hacking", "port scan", "network scan", "penetration",
                                    "osint", "packet", "wireshark", "capture", "pcap"],
                "patterns": [
                    r"scan (me|localhost|scanme|\d+\.\d+)",
                    r"what port is \w+",
                    r"(explain|show|teach) .*(attack|exploit|vulnerability)",
                    r"how (does|do) .*(hack|exploit|attack|inject)",
                ],
            },
            "web_search": {
                "keywords": ["search", "find", "google", "look up", "who is", "what happened",
                             "current", "recent", "latest", "today", "news about"],
                "strong_keywords": ["search for", "look it up", "what's the current",
                                    "search the web", "find information on"],
                "patterns": [
                    r"search (for |the )?\w+",
                    r"(look up|find out about) \w+",
                    r"(what|who) (is|are|was|were) (the )?current",
                    r"latest (news|info|update) (on|about) \w+",
                ],
            },
            "news": {
                "keywords": ["news", "headlines", "happening", "update me", "what's new",
                             "breaking", "today", "recently"],
                "strong_keywords": ["latest news", "what's happening", "current events",
                                    "news update", "world news"],
                "patterns": [
                    r"(any |get |show )?(latest |recent )?news",
                    r"what('s| is) happening (in |with |around )?\w*",
                    r"(update me on|tell me about) (what('s| is) happening)",
                ],
            },
            "system_info": {
                "keywords": ["system", "ram", "cpu", "disk", "uptime", "status", "memory",
                             "processor", "storage", "performance", "hardware", "specs"],
                "strong_keywords": ["how is my computer", "system status", "check my system",
                                    "cpu usage", "ram usage", "disk space"],
                "patterns": [
                    r"(how is|check|show) (my )?(computer|system|pc|machine)",
                    r"(how much |what is my )(ram|cpu|disk|memory|storage)",
                    r"system (status|info|specs|performance)",
                ],
            },
            "project_mgmt": {
                "keywords": ["project", "goal", "task", "milestone", "status", "progress",
                             "plan", "roadmap", "working on", "agenda"],
                "strong_keywords": ["start a project", "set my goal", "current project",
                                    "what are we working on", "project status"],
                "patterns": [
                    r"(new|start|create) (a )?project",
                    r"set (my |the )?(goal|objective|target)",
                    r"(what('s| is)|show) (my |the |our )?project",
                ],
            },
            "clear": {
                "keywords": [],
                "strong_keywords": ["CLEAR", "clear memory", "reset memory", "clear chat",
                                    "forget everything", "start fresh"],
                "patterns": [
                    r"^clear$",
                    r"^reset$",
                    r"clear (memory|chat|history|context)",
                ],
            },
        }

    def classify(self, text: str) -> Intent:
        """Classify user input into an intent category with confidence scoring."""
        original = text.strip()
        lower = original.lower()

        best_category = "general_chat"
        max_score = 0.0
        matched_keywords = []

        for category, rules in self.categories.items():
            score = 0.0
            cat_matches = []

            # Keyword matching (weight 1)
            for kw in rules.get("keywords", []):
                if kw.lower() in lower:
                    if re.search(rf"\b{re.escape(kw.lower())}\b", lower):
                        score += 1.5
                    else:
                        score += 0.8
                    cat_matches.append(kw)

            # Strong keyword matching (weight 3)
            for skw in rules.get("strong_keywords", []):
                if skw.lower() in lower:
                    score += 3.0
                    cat_matches.append(skw)

            # Pattern matching (weight 4)
            for pattern in rules.get("patterns", []):
                if re.search(pattern, lower):
                    score += 4.0
                    cat_matches.append(f"pattern:{pattern[:30]}")

            if score > max_score:
                max_score = score
                best_category = category
                matched_keywords = cat_matches

        # Normalize: max meaningful score ~10, normalize to 0-1
        confidence = min(max_score / 10.0, 1.0)

        # Below threshold → general chat
        if confidence < 0.15:
            return Intent(category="general_chat", confidence=1.0, keywords=[])

        return Intent(
            category=best_category,
            confidence=round(confidence, 2),
            keywords=matched_keywords,
        )
