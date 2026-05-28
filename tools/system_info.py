"""
tools/system_info.py
Hardware and OS status — Jarvis-style system awareness.
"""
import platform
import datetime


def get_system_info() -> dict:
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/" if platform.system() != "Windows" else "C:\\")
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        net = psutil.net_io_counters()

        return {
            "os": f"{platform.system()} {platform.version()}",
            "hostname": platform.node(),
            "python": platform.python_version(),
            "cpu": {
                "cores": psutil.cpu_count(logical=False),
                "threads": psutil.cpu_count(logical=True),
                "usage_percent": cpu_percent,
                "freq_mhz": round(psutil.cpu_freq().current) if psutil.cpu_freq() else "N/A",
            },
            "memory": {
                "total_gb": round(mem.total / 1e9, 1),
                "used_gb": round(mem.used / 1e9, 1),
                "percent": mem.percent,
            },
            "disk": {
                "total_gb": round(disk.total / 1e9, 1),
                "used_gb": round(disk.used / 1e9, 1),
                "percent": disk.percent,
            },
            "uptime": str(uptime).split(".")[0],
            "network": {
                "bytes_sent_mb": round(net.bytes_sent / 1e6, 1),
                "bytes_recv_mb": round(net.bytes_recv / 1e6, 1),
            },
        }
    except ImportError:
        return {
            "os": f"{platform.system()} {platform.version()}",
            "hostname": platform.node(),
            "python": platform.python_version(),
            "note": "Install psutil for full hardware info.",
        }


def format_system_info(info: dict) -> str:
    lines = [
        f"🖥  OS: {info.get('os', 'Unknown')}",
        f"🏠  Host: {info.get('hostname', 'Unknown')}",
    ]
    if "cpu" in info:
        cpu = info["cpu"]
        lines.append(f"⚙️  CPU: {cpu['cores']} cores / {cpu['threads']} threads @ {cpu['freq_mhz']} MHz — {cpu['usage_percent']}% usage")
    if "memory" in info:
        mem = info["memory"]
        lines.append(f"🧠  RAM: {mem['used_gb']} / {mem['total_gb']} GB ({mem['percent']}%)")
    if "disk" in info:
        disk = info["disk"]
        lines.append(f"💾  Disk: {disk['used_gb']} / {disk['total_gb']} GB ({disk['percent']}%)")
    if "uptime" in info:
        lines.append(f"⏱️  Uptime: {info['uptime']}")
    if "network" in info:
        net = info["network"]
        lines.append(f"🌐  Network: ↑{net['bytes_sent_mb']} MB / ↓{net['bytes_recv_mb']} MB")
    if "note" in info:
        lines.append(f"ℹ️  {info['note']}")
    return "\n".join(lines)
