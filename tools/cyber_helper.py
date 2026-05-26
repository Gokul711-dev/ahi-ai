"""
tools/cyber_helper.py
Ethical hacking educational tools — read-only, explainatory, approval-gated.
"""
import socket
import json
from typing import Optional
from pathlib import Path


# Educational port database
WELL_KNOWN_PORTS = {
    20: "FTP Data Transfer",
    21: "FTP Control",
    22: "SSH (Secure Shell)",
    23: "Telnet (insecure, avoid)",
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

ATTACK_EXPLANATIONS = {
    "sql injection": (
        "SQL Injection is when an attacker inserts malicious SQL code into an input field, "
        "tricking the database into executing unintended commands. Example: entering ' OR '1'='1 "
        "in a login field. Defence: use parameterized queries / prepared statements."
    ),
    "xss": (
        "Cross-Site Scripting (XSS) injects malicious JavaScript into web pages viewed by others. "
        "Types: Stored (persisted in DB), Reflected (via URL), DOM-based. "
        "Defence: sanitize input, use Content Security Policy headers."
    ),
    "phishing": (
        "Phishing tricks users into revealing credentials via fake login pages or emails. "
        "Spear phishing targets specific individuals. Defence: MFA, email filtering, user training."
    ),
    "mitm": (
        "Man-in-the-Middle (MITM) attacks intercept communication between two parties. "
        "Common vectors: ARP spoofing on LANs, rogue Wi-Fi hotspots. "
        "Defence: HTTPS/TLS, certificate pinning, VPNs."
    ),
    "ddos": (
        "Distributed Denial of Service floods a target with traffic from many sources, "
        "overwhelming it. Types: volumetric, protocol, application layer. "
        "Defence: rate limiting, CDN, anycast, WAF."
    ),
    "brute force": (
        "Brute force attacks systematically try all possible passwords or keys. "
        "Dictionary attacks use common passwords. Defence: account lockout, MFA, long passwords."
    ),
}


def explain_port(port_number: int) -> str:
    """Explain what a port is used for."""
    service = WELL_KNOWN_PORTS.get(port_number)
    if service:
        return f"Port {port_number}: {service}"
    return f"Port {port_number} is not a well-known port. It may be used by custom applications."


def explain_attack(attack_name: str) -> str:
    """Return an educational explanation of a cyber attack type."""
    key = attack_name.lower().strip()
    for attack_key, explanation in ATTACK_EXPLANATIONS.items():
        if attack_key in key or key in attack_key:
            return f"**{attack_name.upper()}**\n{explanation}"
    return f"I don't have a pre-built explanation for '{attack_name}' yet. Ask me to explain it conversationally!"


def dns_lookup(domain: str, record_type: str = "A") -> str:
    """Perform a DNS lookup for educational purposes."""
    try:
        import socket
        if record_type.upper() == "A":
            addr = socket.gethostbyname(domain)
            return f"{domain} → {addr} (A record)"
        else:
            return f"DNS lookup for {record_type} records requires dnspython. Install with: pip install dnspython"
    except socket.gaierror as e:
        return f"DNS lookup failed for {domain}: {e}"


def whois_lookup(domain: str) -> str:
    """Retrieve WHOIS information for a domain."""
    try:
        import whois
        w = whois.whois(domain)
        lines = [f"WHOIS: {domain}"]
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
        return "python-whois not installed. Run: pip install python-whois"
    except Exception as e:
        return f"WHOIS lookup failed: {e}"


import os
import subprocess
import shutil

# Global variable to store custom Nmap executable path (e.g., "D:\\nmap\\nmap.exe")
_NMAP_EXECUTABLE = None
_NMAP_PATH_FILE = Path('data/nmap_path.json')

# Attempt to locate nmap in system PATH if not already configured
if _NMAP_EXECUTABLE is None:
    nmap_path = shutil.which("nmap")
    if nmap_path:
        _NMAP_EXECUTABLE = nmap_path
        # Persist discovered path for future runs
        _NMAP_PATH_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(_NMAP_PATH_FILE, "w", encoding="utf-8") as f:
                json.dump({"path": _NMAP_EXECUTABLE}, f)
        except Exception:
            pass

# Load stored Nmap path if the config file exists
if _NMAP_PATH_FILE.is_file():
    try:
        with open(_NMAP_PATH_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            path = data.get('path')
            if path and os.path.isfile(path) and os.access(path, os.X_OK):
                _NMAP_EXECUTABLE = path
    except Exception:
        # Silently ignore errors; fallback to simulation
        pass

def set_nmap_path(path: str):
    """Configure the absolute path to the Nmap executable.
    Accepts either a directory containing nmap.exe or the full path to the binary.
    Returns a status string indicating success or error.
    """
    global _NMAP_EXECUTABLE
    if not path:
        return "[Error] No path provided for Nmap executable."
    # If a directory is provided, append nmap.exe
    candidate = path
    if os.path.isdir(path):
        candidate = os.path.join(path, "nmap.exe")
    if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
        _NMAP_EXECUTABLE = candidate
        # Persist to JSON file
        _NMAP_PATH_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(_NMAP_PATH_FILE, 'w', encoding='utf-8') as f:
                json.dump({"path": candidate}, f)
        except Exception as e:
            return f"[Error] Unable to write config file: {e}"
        return f"Nmap executable set to: {candidate}"
    else:
        return f"[Error] Nmap executable not found or not executable at: {candidate}"

def run_nmap_scan(target: str, scan_type: str = "-sS") -> str:
    """
    Run an Nmap scan against a target.
    If a custom Nmap executable is configured, it is used via subprocess.
    Otherwise, falls back to simulation mode.
    Requires approval.
    """
    # Very strict whitelist for safety during Phase 2
    allowed_targets = ["localhost", "127.0.0.1", "scanme.nmap.org"]
    if target not in allowed_targets:
        return f"[Security Block] Target '{target}' is not in the allowed educational whitelist ({allowed_targets})."

    # Use configured executable if available
    if _NMAP_EXECUTABLE:
        # Build command line: nmap <scan_type> <target>
        cmd = [_NMAP_EXECUTABLE, scan_type, target]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout.strip() or result.stderr.strip()
            return f"Nmap Scan Results for {target}:\n{output}"
        except Exception as e:
            return f"[Error] Failed to execute Nmap: {e}"
    # Fallback to simulation (previous behavior)
    sim_output = f"""
+[SIMULATION MODE] Nmap is not installed or a custom path was not provided.
 Here is what a {scan_type} scan against {target} would look like:
 
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
"""
    return sim_output.strip()


def craft_packet(protocol: str, target: str) -> str:
    """
    Demonstrate packet crafting with Scapy without actually sending the packet.
    """
    try:
        from scapy.all import IP, TCP, ICMP, UDP
        
        protocol = protocol.upper()
        if protocol == "TCP_SYN":
            pkt = IP(dst=target)/TCP(dport=80, flags="S")
            desc = "TCP SYN Packet (Used in half-open scanning)"
        elif protocol == "ICMP":
            pkt = IP(dst=target)/ICMP()
            desc = "ICMP Echo Request (Used in ping)"
        elif protocol == "UDP":
            pkt = IP(dst=target)/UDP(dport=53)
            desc = "UDP Packet (Targeting DNS)"
        else:
            return f"Protocol '{protocol}' simulation not supported. Try TCP_SYN, ICMP, or UDP."
            
        output = f"--- {desc} ---\n"
        output += pkt.show(dump=True)
        return output
    except ImportError:
        return "[Error] Scapy is not installed. Run: pip install scapy"
    except Exception as e:
        return f"[Error] Failed to craft packet: {e}"


def analyze_pcap(filepath: str) -> str:
    """
    Analyze a provided PCAP file using Scapy and summarize its contents.
    """
    from pathlib import Path
    if not Path(filepath).exists():
        return f"[Error] File not found: {filepath}"
        
    try:
        from scapy.all import rdpcap, IP, TCP, UDP
        packets = rdpcap(filepath, count=100) # Limit for safety
        
        stats = {"total_read": len(packets), "tcp": 0, "udp": 0, "icmp": 0, "other": 0}
        ips = set()
        
        for pkt in packets:
            if IP in pkt:
                ips.add(pkt[IP].src)
                ips.add(pkt[IP].dst)
            if TCP in pkt: stats["tcp"] += 1
            elif UDP in pkt: stats["udp"] += 1
            elif pkt.haslayer("ICMP"): stats["icmp"] += 1
            else: stats["other"] += 1
            
        summary = (
            f"PCAP Analysis: {filepath}\n"
            f"Read {stats['total_read']} packets (capped at 100 for preview).\n"
            f"Protocol Breakdown: {stats['tcp']} TCP, {stats['udp']} UDP, {stats['icmp']} ICMP.\n"
            f"Unique IP Addresses seen: {len(ips)}\n"
        )
        return summary
    except ImportError:
        return "[Error] Scapy is not installed. Run: pip install scapy"
    except Exception as e:
        return f"[Error] Failed to analyze PCAP: {e}"

