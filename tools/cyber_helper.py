"""
tools/cyber_helper.py
Ethical hacking educational tools — read-only, explanatory, approval-gated.
"""
import os
import json
import socket
import subprocess
import shutil
from pathlib import Path
from typing import Optional

# ── Port database ───────────────────────────────────────────────────────────
WELL_KNOWN_PORTS = {
    20: "FTP Data Transfer",
    21: "FTP Control",
    22: "SSH (Secure Shell)",
    23: "Telnet (insecure — avoid)",
    25: "SMTP (email sending)",
    53: "DNS (Domain Name System)",
    80: "HTTP (unencrypted web)",
    110: "POP3 (email retrieval)",
    143: "IMAP (email)",
    443: "HTTPS (encrypted web)",
    445: "SMB (Windows file sharing)",
    3306: "MySQL",
    3389: "RDP (Remote Desktop)",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP Alternate / Proxy",
    8443: "HTTPS Alternate",
    27017: "MongoDB",
}

# ── Attack explanations ─────────────────────────────────────────────────────
ATTACK_EXPLANATIONS = {
    "sql injection": (
        "SQL Injection inserts malicious SQL code into input fields, tricking the database into executing "
        "unintended commands. Example: entering `' OR '1'='1` in a login field bypasses authentication. "
        "Defence: parameterized queries / prepared statements. Never trust user input."
    ),
    "xss": (
        "Cross-Site Scripting (XSS) injects malicious JavaScript into web pages viewed by others. "
        "Types: Stored (persisted in DB), Reflected (via URL), DOM-based. "
        "Defence: sanitize/encode all user input, use Content-Security-Policy headers."
    ),
    "phishing": (
        "Phishing tricks users into revealing credentials via fake login pages or emails. "
        "Spear phishing targets specific individuals. Whaling targets executives. "
        "Defence: MFA, email filtering, user awareness training."
    ),
    "mitm": (
        "Man-in-the-Middle attacks intercept communication between two parties without either knowing. "
        "Common vectors: ARP spoofing on LANs, rogue Wi-Fi hotspots. "
        "Defence: HTTPS/TLS everywhere, certificate pinning, VPNs."
    ),
    "ddos": (
        "Distributed Denial of Service floods a target with traffic from many sources, overwhelming it. "
        "Types: volumetric (bandwidth flood), protocol (SYN flood), application layer (HTTP flood). "
        "Defence: rate limiting, CDN, anycast routing, WAF."
    ),
    "brute force": (
        "Brute force attacks systematically try all possible passwords or keys. "
        "Dictionary attacks use common passwords. Credential stuffing reuses leaked credentials. "
        "Defence: account lockout policies, MFA, long passphrases, breach monitoring."
    ),
    "social engineering": (
        "Social engineering manipulates people rather than systems. "
        "Techniques: pretexting (fabricating scenarios), baiting (USB drops), vishing (voice phishing), "
        "tailgating (physical access). "
        "Defence: security awareness training, verification procedures, zero-trust culture."
    ),
    "ransomware": (
        "Ransomware encrypts victim files and demands payment for decryption keys. "
        "Often delivered via phishing emails or unpatched vulnerabilities. "
        "Defence: offline backups, endpoint detection, patch management, least-privilege access."
    ),
    "privilege escalation": (
        "Privilege escalation exploits vulnerabilities or misconfigurations to gain higher-level permissions. "
        "Vertical: gaining admin/root. Horizontal: accessing another user's data. "
        "Defence: principle of least privilege, patch management, proper SUID/GUID controls."
    ),
}


def explain_port(port_number: int) -> str:
    service = WELL_KNOWN_PORTS.get(port_number)
    if service:
        return f"**Port {port_number}**: {service}"
    return f"Port {port_number} is not a well-known port. It may be used by custom applications or services."


def explain_attack(attack_name: str) -> str:
    key = attack_name.lower().strip()
    for attack_key, explanation in ATTACK_EXPLANATIONS.items():
        if attack_key in key or key in attack_key:
            return f"**{attack_name.upper()}**\n{explanation}"
    return (
        f"I don't have a pre-built card for '{attack_name}', "
        f"but I can explain it conversationally. Ask me directly!"
    )


def dns_lookup(domain: str, record_type: str = "A") -> str:
    try:
        if record_type.upper() == "A":
            addr = socket.gethostbyname(domain)
            return f"**{domain}** → `{addr}` (A record)"
        else:
            return f"DNS lookup for {record_type} records requires dnspython. Run: `pip install dnspython`"
    except socket.gaierror as e:
        return f"DNS lookup failed for {domain}: {e}"


def whois_lookup(domain: str) -> str:
    try:
        import whois
        w = whois.whois(domain)
        lines = [f"**WHOIS: {domain}**"]
        if w.registrar:
            lines.append(f"Registrar: {w.registrar}")
        if w.creation_date:
            lines.append(f"Created: {w.creation_date}")
        if w.expiration_date:
            lines.append(f"Expires: {w.expiration_date}")
        if w.name_servers:
            ns = w.name_servers if isinstance(w.name_servers, list) else [w.name_servers]
            lines.append(f"Name Servers: {', '.join(str(n) for n in ns[:3])}")
        return "\n".join(lines)
    except ImportError:
        return "python-whois not installed. Run: `pip install python-whois`"
    except Exception as e:
        return f"WHOIS lookup failed: {e}"


# ── Nmap ─────────────────────────────────────────────────────────────────────
_NMAP_EXECUTABLE: Optional[str] = None
_NMAP_PATH_FILE = Path("data/nmap_path.json")

# Auto-discover from PATH
_discovered = shutil.which("nmap")
if _discovered:
    _NMAP_EXECUTABLE = _discovered

# Load persisted custom path
if _NMAP_PATH_FILE.is_file():
    try:
        with open(_NMAP_PATH_FILE, "r", encoding="utf-8") as f:
            _data = json.load(f)
            _path = _data.get("path")
            if _path and os.path.isfile(_path) and os.access(_path, os.X_OK):
                _NMAP_EXECUTABLE = _path
    except Exception:
        pass


def set_nmap_path(path: str) -> str:
    global _NMAP_EXECUTABLE
    if not path:
        return "[Error] No path provided."
    candidate = path
    if os.path.isdir(path):
        candidate = os.path.join(path, "nmap.exe")
    if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
        _NMAP_EXECUTABLE = candidate
        _NMAP_PATH_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(_NMAP_PATH_FILE, "w", encoding="utf-8") as f:
                json.dump({"path": candidate}, f)
        except Exception as e:
            return f"[Error] Could not save config: {e}"
        return f"Nmap executable set to: `{candidate}`"
    return f"[Error] Not found or not executable: `{candidate}`"


ALLOWED_TARGETS = {"localhost", "127.0.0.1", "scanme.nmap.org"}


def run_nmap_scan(target: str, scan_type: str = "-sS") -> str:
    """Run Nmap against a whitelisted target. Falls back to simulation if Nmap absent."""
    if target not in ALLOWED_TARGETS:
        return (
            f"[Security Block] `{target}` is not in the educational whitelist.\n"
            f"Allowed: {sorted(ALLOWED_TARGETS)}\n\n"
            f"For ethical hacking labs, only scan systems you own or have explicit permission to test."
        )

    if _NMAP_EXECUTABLE:
        cmd = [_NMAP_EXECUTABLE, scan_type, target]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            output = result.stdout.strip() or result.stderr.strip()
            return f"**Nmap Scan — {target}**\n```\n{output}\n```"
        except subprocess.TimeoutExpired:
            return "[Timeout] Nmap scan exceeded 60 seconds."
        except Exception as e:
            return f"[Error] Failed to run Nmap: {e}"

    # Simulation fallback
    return f"""\
**[Simulation Mode]** Nmap not found — showing what a `{scan_type}` scan of `{target}` would look like:

```
Starting Nmap 7.93 ( https://nmap.org )
Nmap scan report for {target}
Host is up (0.042s latency).
Not shown: 996 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
9929/tcp open  nping-echo

Nmap done: 1 IP address (1 host up) scanned in 1.42 seconds
```
Install Nmap from https://nmap.org for live scanning."""


def craft_packet(protocol: str, target: str) -> str:
    """Demonstrate Scapy packet crafting. Does NOT transmit."""
    try:
        from scapy.all import IP, TCP, ICMP, UDP

        protocol = protocol.upper()
        if protocol == "TCP_SYN":
            pkt = IP(dst=target) / TCP(dport=80, flags="S")
            desc = "TCP SYN Packet (half-open scan probe)"
        elif protocol == "ICMP":
            pkt = IP(dst=target) / ICMP()
            desc = "ICMP Echo Request (ping)"
        elif protocol == "UDP":
            pkt = IP(dst=target) / UDP(dport=53)
            desc = "UDP Packet (DNS port)"
        else:
            return f"Protocol '{protocol}' not supported. Use: TCP_SYN, ICMP, or UDP."

        output = f"**--- {desc} ---**\n```\n"
        output += pkt.show(dump=True)
        output += "\n```\n*(Packet crafted but NOT sent)*"
        return output
    except ImportError:
        return "Scapy is not installed. Run: `pip install scapy`"
    except Exception as e:
        return f"[Error] Packet crafting failed: {e}"


def analyze_pcap(filepath: str) -> str:
    """Analyze a PCAP file and summarize its contents."""
    if not Path(filepath).exists():
        return f"[Error] File not found: {filepath}"
    try:
        from scapy.all import rdpcap, IP, TCP, UDP
        packets = rdpcap(filepath, count=100)
        stats = {"total": len(packets), "tcp": 0, "udp": 0, "icmp": 0, "other": 0}
        ips: set = set()

        for pkt in packets:
            if IP in pkt:
                ips.add(pkt[IP].src)
                ips.add(pkt[IP].dst)
            if TCP in pkt:
                stats["tcp"] += 1
            elif UDP in pkt:
                stats["udp"] += 1
            elif pkt.haslayer("ICMP"):
                stats["icmp"] += 1
            else:
                stats["other"] += 1

        return (
            f"**PCAP Analysis: `{filepath}`**\n"
            f"Packets read: {stats['total']} (capped at 100 for preview)\n"
            f"TCP: {stats['tcp']} | UDP: {stats['udp']} | ICMP: {stats['icmp']} | Other: {stats['other']}\n"
            f"Unique IPs seen: {len(ips)}"
        )
    except ImportError:
        return "Scapy not installed. Run: `pip install scapy`"
    except Exception as e:
        return f"[Error] PCAP analysis failed: {e}"
