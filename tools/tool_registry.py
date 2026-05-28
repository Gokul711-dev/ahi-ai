"""
tools/tool_registry.py
Central registry wrapping all tools with Ollama function-calling schemas.
"""
from typing import Any, Callable
from dataclasses import dataclass, field

from tools.web_search import web_search, get_news, format_search_results
from tools.ip_locator import locate_ip, format_location
from tools.code_executor import execute_python
from tools.file_manager import read_file, write_file, list_directory
from tools.system_info import get_system_info, format_system_info
from tools.cyber_helper import (
    explain_port, explain_attack, dns_lookup, whois_lookup,
    run_nmap_scan, craft_packet, analyze_pcap,
)
from teacher.teaching_loop import start_curriculum, get_curriculum, record_weak_point


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict
    function: Callable
    requires_approval: bool = False
    enabled: bool = True
    formatter: Callable = None


class ToolRegistry:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self._tools: dict[str, ToolDefinition] = {}
        self._register_all()

    def _reg(self, tool: ToolDefinition):
        if tool.enabled:
            self._tools[tool.name] = tool

    def _register_all(self):
        tcfg = self.config.get("tools", {})

        # ── Web search ──────────────────────────────────────────────────────
        self._reg(ToolDefinition(
            name="web_search",
            description="Search the web using DuckDuckGo. Use for current events, facts, or anything needing up-to-date information.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "max_results": {"type": "integer", "description": "Number of results (default 5)", "default": 5},
                },
                "required": ["query"],
            },
            function=web_search,
            formatter=format_search_results,
            enabled=tcfg.get("web_search", {}).get("enabled", True),
        ))

        self._reg(ToolDefinition(
            name="get_news",
            description="Fetch latest news from RSS feeds. Use when the user asks for current news or updates on a topic.",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to filter news (e.g. 'AI', 'cybersecurity')"},
                    "max_results": {"type": "integer", "description": "Number of items to return", "default": 5},
                },
                "required": [],
            },
            function=get_news,
            formatter=format_search_results,
            enabled=tcfg.get("web_search", {}).get("enabled", True),
        ))

        # ── IP locator ──────────────────────────────────────────────────────
        self._reg(ToolDefinition(
            name="locate_ip",
            description="Find geolocation info for an IP address: city, country, ISP, coordinates.",
            parameters={
                "type": "object",
                "properties": {
                    "ip_address": {"type": "string", "description": "IPv4 or IPv6 address to look up"},
                },
                "required": ["ip_address"],
            },
            function=locate_ip,
            formatter=format_location,
            enabled=tcfg.get("ip_locator", {}).get("enabled", True),
        ))

        # ── Code executor ───────────────────────────────────────────────────
        self._reg(ToolDefinition(
            name="execute_python",
            description="Execute Python code in a safe subprocess and return output. Use for calculations, demos, or testing snippets.",
            parameters={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"},
                },
                "required": ["code"],
            },
            function=execute_python,
            requires_approval=True,
            enabled=tcfg.get("code_executor", {}).get("enabled", True),
        ))

        # ── File manager ────────────────────────────────────────────────────
        self._reg(ToolDefinition(
            name="read_file",
            description="Read the contents of a file from the filesystem.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"},
                },
                "required": ["path"],
            },
            function=read_file,
            enabled=tcfg.get("file_manager", {}).get("enabled", True),
        ))

        self._reg(ToolDefinition(
            name="write_file",
            description="Write content to a file. Use for saving code, notes, or generated outputs.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write to"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
            function=write_file,
            requires_approval=True,
            enabled=tcfg.get("file_manager", {}).get("enabled", True),
        ))

        self._reg(ToolDefinition(
            name="list_directory",
            description="List files and subdirectories at a given path.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory to list (default: current dir)", "default": "."},
                },
                "required": [],
            },
            function=list_directory,
            enabled=tcfg.get("file_manager", {}).get("enabled", True),
        ))

        # ── System info ─────────────────────────────────────────────────────
        self._reg(ToolDefinition(
            name="get_system_info",
            description="Get current hardware and OS status: CPU, RAM, disk, uptime, network stats.",
            parameters={"type": "object", "properties": {}, "required": []},
            function=get_system_info,
            formatter=format_system_info,
            enabled=tcfg.get("system_info", {}).get("enabled", True),
        ))

        # ── Cyber tools ─────────────────────────────────────────────────────
        self._reg(ToolDefinition(
            name="explain_port",
            description="Explain what a network port number is used for.",
            parameters={
                "type": "object",
                "properties": {
                    "port_number": {"type": "integer", "description": "Port number to explain"},
                },
                "required": ["port_number"],
            },
            function=explain_port,
            enabled=tcfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._reg(ToolDefinition(
            name="explain_attack",
            description="Get an educational explanation of a cybersecurity attack type (e.g., SQL injection, XSS, MITM, phishing, DDoS).",
            parameters={
                "type": "object",
                "properties": {
                    "attack_name": {"type": "string", "description": "Attack type name"},
                },
                "required": ["attack_name"],
            },
            function=explain_attack,
            enabled=tcfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._reg(ToolDefinition(
            name="dns_lookup",
            description="Perform a DNS lookup for a domain.",
            parameters={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Domain name to look up"},
                    "record_type": {"type": "string", "description": "DNS record type (A, MX, etc.)", "default": "A"},
                },
                "required": ["domain"],
            },
            function=dns_lookup,
            requires_approval=True,
            enabled=tcfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._reg(ToolDefinition(
            name="whois_lookup",
            description="Look up WHOIS registration information for a domain.",
            parameters={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Domain name"},
                },
                "required": ["domain"],
            },
            function=whois_lookup,
            requires_approval=True,
            enabled=tcfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._reg(ToolDefinition(
            name="run_nmap_scan",
            description="Run an Nmap scan against an allowed target (localhost, 127.0.0.1, scanme.nmap.org). Simulates if Nmap not installed.",
            parameters={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Target IP or hostname"},
                    "scan_type": {"type": "string", "description": "Nmap flags (e.g. -sS, -A)", "default": "-sS"},
                },
                "required": ["target"],
            },
            function=run_nmap_scan,
            requires_approval=True,
            enabled=tcfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._reg(ToolDefinition(
            name="craft_packet",
            description="Demonstrate packet crafting with Scapy for educational purposes. Does NOT send the packet.",
            parameters={
                "type": "object",
                "properties": {
                    "protocol": {"type": "string", "description": "Protocol: TCP_SYN, ICMP, or UDP"},
                    "target": {"type": "string", "description": "Target IP or hostname"},
                },
                "required": ["protocol", "target"],
            },
            function=craft_packet,
            enabled=tcfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._reg(ToolDefinition(
            name="analyze_pcap",
            description="Analyze a PCAP file and summarize packet counts, protocols, and IPs.",
            parameters={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the PCAP file"},
                },
                "required": ["filepath"],
            },
            function=analyze_pcap,
            enabled=tcfg.get("cyber_helper", {}).get("enabled", True),
        ))

        # ── Teaching engine ─────────────────────────────────────────────────
        self._reg(ToolDefinition(
            name="start_curriculum",
            description="Generate or resume a structured learning roadmap for any topic.",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to learn (e.g. 'Python', 'Networking')"},
                },
                "required": ["topic"],
            },
            function=start_curriculum,
        ))

        self._reg(ToolDefinition(
            name="get_curriculum",
            description="Retrieve the current learning roadmap structure for a topic.",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to look up"},
                },
                "required": ["topic"],
            },
            function=get_curriculum,
        ))

        self._reg(ToolDefinition(
            name="record_weak_point",
            description="Record a concept the user struggled with into long-term memory for future spaced repetition.",
            parameters={
                "type": "object",
                "properties": {
                    "concept": {"type": "string", "description": "The concept the user found difficult"},
                },
                "required": ["concept"],
            },
            function=record_weak_point,
        ))

    # ── Public API ──────────────────────────────────────────────────────────

    def get_definitions(self) -> list[dict]:
        """Return tool definitions in Ollama function-calling format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._tools.values()
        ]

    def get_descriptions_text(self) -> str:
        """Compact text summary of tools for system prompt injection."""
        return "\n".join(
            f"- **{t.name}**: {t.description}" for t in self._tools.values()
        )

    def execute(self, tool_name: str, args: dict, approval_fn=None) -> str:
        """Execute a tool by name. Returns result as string."""
        tool = self._tools.get(tool_name)
        if not tool:
            return f"[Error] Unknown tool: '{tool_name}'"

        if tool.requires_approval and approval_fn:
            approved = approval_fn(f"{tool_name}({args})")
            if not approved:
                return "[Cancelled] User did not approve this action."

        try:
            result = tool.function(**args)
            if tool.formatter and isinstance(result, (dict, list)):
                return tool.formatter(result)
            return str(result)
        except TypeError as e:
            return f"[Error] Invalid arguments for '{tool_name}': {e}"
        except Exception as e:
            return f"[Error] '{tool_name}' failed: {e}"

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())
