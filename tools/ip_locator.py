"""
tools/ip_locator.py
IP geolocation using ip-api.com (free, no key required).
"""
import requests


def locate_ip(ip_address: str) -> dict:
    """Return geolocation data for an IP address."""
    try:
        url = f"http://ip-api.com/json/{ip_address}"
        params = {
            "fields": "status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "fail":
            return {"error": data.get("message", "Lookup failed"), "ip": ip_address}
        return {
            "ip": data.get("query", ip_address),
            "city": data.get("city", "Unknown"),
            "region": data.get("regionName", "Unknown"),
            "country": data.get("country", "Unknown"),
            "zip": data.get("zip", ""),
            "latitude": data.get("lat"),
            "longitude": data.get("lon"),
            "timezone": data.get("timezone", ""),
            "isp": data.get("isp", "Unknown"),
            "org": data.get("org", ""),
        }
    except requests.Timeout:
        return {"error": "Request timed out", "ip": ip_address}
    except Exception as e:
        return {"error": str(e), "ip": ip_address}


def format_location(data: dict) -> str:
    if "error" in data:
        return f"Could not locate {data.get('ip', 'that IP')}: {data['error']}"
    return (
        f"**{data['ip']}** is located in **{data['city']}, {data['region']}, {data['country']}**\n"
        f"Coordinates: {data['latitude']}, {data['longitude']}\n"
        f"Timezone: {data['timezone']}\n"
        f"ISP: {data['isp']}"
    )
