# proxy_util.py
import random, re
from pathlib import Path

PROXIES_FILE = Path(__file__).parent / "proxies.txt"

def load_proxies():
    if not PROXIES_FILE.exists(): return []
    return [l.strip() for l in PROXIES_FILE.read_text().splitlines() if l.strip() and not l.startswith("#")]

def get_random_proxy(proxies):
    if not proxies: return None
    return parse_proxy(random.choice(proxies))

def parse_proxy(raw):
    raw = raw.strip()
    if re.match(r'^(https?|socks5)://', raw):
        m = re.match(r'^((?:https?|socks5)://)(?:([^:@]+):([^@]+)@)?(.+)$', raw)
        if m:
            scheme, user, passwd, hostport = m.groups()
            r = {"server": f"{scheme}{hostport}"}
            if user: r["username"] = user; r["password"] = passwd or ""
            return r
        return {"server": raw}
    if "@" in raw:
        creds, hostport = raw.rsplit("@", 1)
        user, passwd = creds.split(":", 1) if ":" in creds else (creds, "")
        return {"server": f"http://{hostport}", "username": user, "password": passwd}
    parts = raw.split(":")
    if len(parts) == 4:
        host, port, user, passwd = parts
        return {"server": f"http://{host}:{port}", "username": user, "password": passwd}
    if len(parts) == 2: return {"server": f"http://{raw}"}
    return {"server": f"http://{raw}"}

def proxy_to_requests(proxy):
    if not proxy: return None
    server = proxy.get("server", "")
    user   = proxy.get("username", "")
    pw     = proxy.get("password", "")
    url    = re.sub(r'://', f'://{user}:{pw}@', server) if user else server
    return {"http": url, "https": url}

def proxy_display(proxy):
    if not proxy: return "none"
    server = proxy.get("server", "")
    user   = proxy.get("username", "")
    return f"{user}@{server}" if user else server
