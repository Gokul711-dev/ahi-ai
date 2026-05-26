"""
tools/tool_registry.py
Central registry that wraps all tools with Ollama function-calling schemas.
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
    run_nmap_scan, craft_packet, analyze_pcap
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
    formatter: Callable = None  # Optional result formatter


class ToolRegistry:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self._tools: dict[str, ToolDefinition] = {}
        self._register_all()

    def _register_all(self):
        tools_cfg = self.config.get("tools", {})

        self._register(ToolDefinition(
            name="web_search",
            description="Search the web using DuckDuckGo. Use for current events, facts, or anything requiring up-to-date information. Input: query string.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "max_results": {"type": "integer", "description": "Number of results to return (default 5)", "default": 5},
                },
                "required": ["query"],
            },
            function=web_search,
            formatter=format_search_results,
            enabled=tools_cfg.get("web_search", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="get_news",
            description="Fetch latest news from RSS feeds. Use when the user asks for current news or latest updates on a topic.",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Optional topic to filter news (e.g., 'AI', 'cybersecurity')"},
                    "max_results": {"type": "integer", "description": "Number of news items to return", "default": 5},
                },
                "required": [],
            },
            function=get_news,
            formatter=format_search_results,
            enabled=tools_cfg.get("web_search", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="locate_ip",
            description="Find geolocation information for an IP address: city, region, country, coordinates, ISP.",
            parameters={
                "type": "object",
                "properties": {
                    "ip_address": {"type": "string", "description": "The IPv4 or IPv6 address to look up"},
                },
                "required": ["ip_address"],
            },
            function=locate_ip,
            formatter=format_location,
            enabled=tools_cfg.get("ip_locator", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="execute_python",
            description="Execute Python code in a safe subprocess and return the output. Use for calculations, demonstrations, or testing snippets.",
            parameters={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The Python code to execute"},
                },
                "required": ["code"],
            },
            function=execute_python,
            requires_approval=True,
            enabled=tools_cfg.get("code_executor", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="read_file",
            description="Read the contents of a file from the filesystem.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to read"},
                },
                "required": ["path"],
            },
            function=read_file,
            enabled=tools_cfg.get("file_manager", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="write_file",
            description="Write content to a file. Use for saving code, notes, or outputs.",
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
            enabled=tools_cfg.get("file_manager", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="list_directory",
            description="List files and subdirectories at a given path.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to list (default: current dir)", "default": "."},
                },
                "required": [],
            },
            function=list_directory,
            enabled=tools_cfg.get("file_manager", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="get_system_info",
            description="Get current hardware and OS status: CPU, RAM, disk, uptime, network stats.",
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
            },
            function=get_system_info,
            formatter=format_system_info,
            enabled=tools_cfg.get("system_info", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="explain_port",
            description="Explain what a network port number is used for (educational).",
            parameters={
                "type": "object",
                "properties": {
                    "port_number": {"type": "integer", "description": "The port number to explain"},
                },
                "required": ["port_number"],
            },
            function=explain_port,
            enabled=tools_cfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="explain_attack",
            description="Get an educational explanation of a cybersecurity attack type (e.g., SQL injection, XSS, MITM).",
            parameters={
                "type": "object",
                "properties": {
                    "attack_name": {"type": "string", "description": "Name of the attack type to explain"},
                },
                "required": ["attack_name"],
            },
            function=explain_attack,
            enabled=tools_cfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="dns_lookup",
            description="Perform a DNS lookup for a domain (educational networking tool).",
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
            enabled=tools_cfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="whois_lookup",
            description="Look up WHOIS registration information for a domain.",
            parameters={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Domain name to look up"},
                },
                "required": ["domain"],
            },
            function=whois_lookup,
            requires_approval=True,
            enabled=tools_cfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="run_nmap_scan",
            description="Run an Nmap scan against a target. Simulated if Nmap is missing. Allowed targets: localhost, 127.0.0.1, scanme.nmap.org",
            parameters={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Target IP or domain to scan"},
                    "scan_type": {"type": "string", "description": "Nmap arguments, e.g., -sS, -A", "default": "-sS"},
                },
                "required": ["target"],
            },
            function=run_nmap_scan,
            requires_approval=True,
            enabled=tools_cfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="craft_packet",
            description="Demonstrate packet crafting with Scapy. Safe and does not actually send the packet.",
            parameters={
                "type": "object",
                "properties": {
                    "protocol": {"type": "string", "description": "Protocol to craft (TCP_SYN, ICMP, UDP)"},
                    "target": {"type": "string", "description": "Target IP or domain"},
                },
                "required": ["protocol", "target"],
            },
            function=craft_packet,
            enabled=tools_cfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="analyze_pcap",
            description="Analyze a PCAP file and summarize its contents (packet counts, protocols, IPs).",
            parameters={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the PCAP file"},
                },
                "required": ["filepath"],
            },
            function=analyze_pcap,
            enabled=tools_cfg.get("cyber_helper", {}).get("enabled", True),
        ))

        self._register(ToolDefinition(
            name="start_curriculum",
            description="Generate or resume a learning roadmap for a topic.",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to learn (e.g., 'Python', 'Networking')"},
                },
                "required": ["topic"],
            },
            function=start_curriculum,
            enabled=True,
        ))

        self._register(ToolDefinition(
            name="get_curriculum",
            description="Get the current learning roadmap structure for a topic.",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to look up"},
                },
                "required": ["topic"],
            },
            function=get_curriculum,
            enabled=True,
        ))

        self._register(ToolDefinition(
            name="record_weak_point",
            description="Record a user's weak point or misunderstanding into long-term memory for future spaced repetition.",
            parameters={
                "type": "object",
                "properties": {
                    "concept": {"type": "string", "description": "The specific concept the user struggled with"},
                },
                "required": ["concept"],
            },
            function=record_weak_point,
            enabled=True,
        ))

    def _register(self, tool: ToolDefinition):
        if tool.enabled:
            self._tools[tool.name] = tool

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
        """Return tool names and descriptions as a readable string for prompt injection."""
        lines = []
        for t in self._tools.values():
            lines.append(f"- **{t.name}**: {t.description}")
        return "\n".join(lines)

    def execute(self, tool_name: str, args: dict, approval_fn=None) -> str:
        """Execute a tool by name with args. Returns result as string."""
        tool = self._tools.get(tool_name)
        if not tool:
            return f"[Error] Unknown tool: {tool_name}"

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
            return f"[Error] Invalid arguments for {tool_name}: {e}"
        except Exception as e:
            return f"[Error] {tool_name} failed: {e}"

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())
