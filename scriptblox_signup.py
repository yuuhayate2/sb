# scriptblox_signup.py — Kuni Tool · SB Account Generator
# Web UI — deploy on Railway, Render, or run locally
# Open http://localhost:5000 in browser

import asyncio
import json
import os
import random
import re
import string
import threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

import requests
import urllib3
urllib3.disable_warnings()

from dotenv import load_dotenv
from flask import Flask, request, jsonify
import hashlib
from flask_socketio import SocketIO, emit

from turnstile_solver import solve_turnstile_capsolver
from proxy_util import load_proxies, get_random_proxy, proxy_display

load_dotenv()
SUPABASE_URL = "https://ukwltgxtfikrpsqfihi.supabase.co"
SUPABASE_KEY = "sb_publishable_NhI5Z-LriMN_huWOV14AtA_YtmDZeQ3"

license_valid = False
current_key = None

def get_hwid(ip):
    return hashlib.sha256(ip.encode()).hexdigest()

ACCOUNTS_FILE   = Path(__file__).parent / "scriptblox_accounts.txt"
SB_SIGNUP       = "https://scriptblox.com/api/auth/signup"
MW_DOMAIN       = "aula.edu.pl"
MW_BASE         = "https://mailwave.dev"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "")
NO_PROXY        = {"http": None, "https": None}

proxies_list = load_proxies()
file_lock    = threading.Lock()

app      = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

state = {
    "running": False,
    "created": 0,
    "active":  0,
    "failed":  0,
    "target":  0,
    "stop":    False,
}


# ── MailWave ──────────────────────────────────────────────────────────────────

def mw_setup():
    try:
        r = requests.get(f"{MW_BASE}/", proxies=NO_PROXY, timeout=15)
        token = re.search(r'<meta name="csrf-token" content="([^"]+)"', r.text)
        csrf = token.group(1) if token else None
        return dict(r.cookies), csrf
    except:
        return None, None

def mw_get_email(cookies, csrf):
    if not csrf or cookies is None:
        return None, csrf
    for _ in range(20):
        alias = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        try:
            r = requests.post(f"{MW_BASE}/change",
                data={"_token": csrf, "name": alias, "domain": MW_DOMAIN},
                cookies=cookies, proxies=NO_PROXY, timeout=15)
            cookies.update(dict(r.cookies))
            new_csrf = unquote(cookies.get("XSRF-TOKEN", csrf))
            r2 = requests.post(f"{MW_BASE}/get_messages",
                headers={"Content-Type": "application/json", "X-CSRF-TOKEN": new_csrf},
                cookies=cookies, proxies=NO_PROXY, timeout=15)
            data = r2.json()
            mailbox = data.get("mailbox", "")
            if MW_DOMAIN in mailbox:
                return mailbox, new_csrf
        except:
            pass
    return None, csrf


# ── Discord Webhook ───────────────────────────────────────────────────────────

def send_webhook(username, password, email):
    if not DISCORD_WEBHOOK:
        return
    try:
        embed = {
            "title": "🎯 New Account Generated",
            "color": 0x00ffcc,
            "description": f"**{username}** | {email}",
            "fields": [
                {"name": "👤 Username", "value": f"```{username}```", "inline": True},
                {"name": "🔑 Password", "value": f"```{password}```", "inline": True},
                {"name": "📧 Email",    "value": f"```{email}```",    "inline": False},
                {"name": "📅 Created",  "value": datetime.now(timezone.utc).strftime("%b %d, %Y"), "inline": True},
                {"name": "⚡ Status",   "value": "⚠️ Unverified", "inline": True},
            ],
            "footer": {"text": "Kuni SB Generator"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        requests.post(DISCORD_WEBHOOK,
            json={"content": "@everyone", "embeds": [embed]},
            proxies=NO_PROXY, timeout=10)
    except:
        pass


# ── Utils ─────────────────────────────────────────────────────────────────────

def rand_username(): return "Kuni" + "".join(random.choices(string.ascii_letters + string.digits, k=10))
def rand_password():  return "".join(random.choices(string.ascii_letters + string.digits + "!@#$", k=14))

def proxy_to_requests(proxy):
    if not proxy: return None
    server = proxy.get("server", "")
    user   = proxy.get("username", "")
    pw     = proxy.get("password", "")
    if user:
        host = server.replace("http://", "").replace("https://", "")
        return {"http": f"http://{user}:{pw}@{host}", "https": f"http://{user}:{pw}@{host}"}
    return {"http": server, "https": server}

def sb_headers():
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://scriptblox.com",
        "Referer": "https://scriptblox.com/signup",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/143.0.0.0 Safari/537.36",
    }

def log_emit(msg, tag="info"):
    ts = datetime.now().strftime("%H:%M:%S")
    socketio.emit("log", {"msg": f"[{ts}] {msg}", "tag": tag})
    socketio.emit("stats", {
        "created": state["created"],
        "active":  state["active"],
        "failed":  state["failed"],
        "target":  state["target"],
    })


# ── Core ──────────────────────────────────────────────────────────────────────

def create_account(slot):
    if state["stop"]: return

    username  = rand_username()
    password  = rand_password()
    proxy     = get_random_proxy(proxies_list)
    proxy_req = proxy_to_requests(proxy)

    cookies, csrf = mw_setup()
    captcha = solve_turnstile_capsolver()
    email_addr, _ = mw_get_email(cookies, csrf)

    if not email_addr or not captcha:
        state["failed"] += 1
        log_emit(f"[#{slot}] Setup failed", "err")
        return

    log_emit(f"[#{slot}] {email_addr} | Captcha OK", "dim")

    try:
        r = requests.post(SB_SIGNUP, json={
            "email": email_addr, "username": username,
            "password": password, "repeatPassword": password,
            "terms": True, "captcha": captcha,
        }, headers=sb_headers(), proxies=proxy_req, timeout=30, verify=False)
        resp = r.json()
    except Exception as e:
        state["failed"] += 1
        log_emit(f"[#{slot}] Request error", "err")
        return

    if resp.get("error") or (isinstance(resp.get("statusCode"), int) and resp["statusCode"] >= 400):
        state["failed"] += 1
        log_emit(f"[#{slot}] Signup failed: {resp.get('message','')}", "err")
        return

    account = {"username": username, "password": password, "email": email_addr}
    with file_lock:
        with open(ACCOUNTS_FILE, "a") as f:
            f.write(json.dumps(account) + "\n")

    send_webhook(username, password, email_addr)
    state["created"] += 1
    log_emit(f"[#{slot}] {username}", "ok")


def run_generator(count, concurrent):
    sem = threading.Semaphore(concurrent)
    threads = []

    def worker(slot):
        with sem:
            if not state["stop"]:
                state["active"] += 1
                create_account(slot)
                state["active"] -= 1

    for i in range(count):
        if state["stop"]: break
        t = threading.Thread(target=worker, args=(i + 1,), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    state["running"] = False
    log_emit(f"Done! {state['created']}/{count} accounts created.", "ok")
    socketio.emit("done", {"created": state["created"], "total": count})


# ── License Verify Route ──────────────────────────────────────────────────────

@app.route("/verify-key", methods=["POST"])
def verify():
    global license_valid, current_key
    try:
        data = request.json
        key = data.get("key")
        if not key:
            return jsonify({"valid": False})

        hwid = get_hwid(request.remote_addr)
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }

        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/licenses",
            headers=headers,
            params={"license_key": f"eq.{key}", "select": "*"}
        )

        if res.status_code != 200:
            return jsonify({"valid": False})

        result = res.json()
        if not result:
            return jsonify({"valid": False})

        license = result[0]

        if license.get("status") != "active":
            return jsonify({"valid": False})

        expiry_date = license.get("expiry_date")
        if expiry_date:
            expiry = datetime.fromisoformat(expiry_date.replace("Z", ""))
            if datetime.now() > expiry:
                return jsonify({"valid": False})

        if license.get("hwid") and license["hwid"] != hwid:
            return jsonify({"valid": False})

        if not license.get("hwid"):
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/licenses",
                headers=headers,
                params={"license_key": f"eq.{key}"},
                json={"hwid": hwid}
            )

        license_valid = True
        current_key = key
        return jsonify({"valid": True})

    except Exception as e:
        print("VERIFY ERROR:", str(e))
        return jsonify({"valid": False})


# ── HTML ──────────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KUNI · AUTO SB GEN</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --bg:       #080b0f;
    --surface:  #0e1318;
    --surface2: #141c24;
    --border:   #1c2a38;
    --border2:  #253545;
    --cyan:     #00d4ff;
    --cyan-dim: rgba(0,212,255,0.08);
    --cyan-glow:rgba(0,212,255,0.18);
    --green:    #00e87a;
    --red:      #ff3b5c;
    --gold:     #f5c842;
    --text:     #c5d8ea;
    --muted:    #4a6070;
    --muted2:   #2a3a4a;
    --mono:     'Space Mono', monospace;
    --sans:     'Syne', sans-serif;
    --radius:   10px;
    --radius-lg:16px;
  }

  html, body { height: 100%; background: var(--bg); color: var(--text); font-family: var(--mono); }

  /* ── scrollbar ── */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

  /* ══════════════════════════════════════════
     LICENSE SCREEN
  ══════════════════════════════════════════ */
  .lic-wrap {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    background:
      radial-gradient(ellipse 60% 40% at 50% 0%, rgba(0,212,255,0.06) 0%, transparent 70%),
      var(--bg);
  }

  .lic-card {
    width: 100%;
    max-width: 400px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 40px 36px 32px;
    position: relative;
    overflow: hidden;
  }

  .lic-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
  }

  .lic-logo {
    font-family: var(--sans);
    font-size: 36px;
    font-weight: 800;
    color: var(--cyan);
    letter-spacing: 6px;
    margin-bottom: 4px;
  }

  .lic-sub {
    font-size: 10px;
    letter-spacing: 3px;
    color: var(--muted);
    margin-bottom: 36px;
    text-transform: uppercase;
  }

  .lic-label {
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--muted);
    margin-bottom: 8px;
    display: block;
  }

  .lic-input {
    width: 100%;
    padding: 13px 16px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--cyan);
    font-family: var(--mono);
    font-size: 13px;
    letter-spacing: 2px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    margin-bottom: 12px;
  }

  .lic-input:focus {
    border-color: var(--cyan);
    box-shadow: 0 0 0 3px var(--cyan-dim);
  }

  .lic-input::placeholder { color: var(--muted2); letter-spacing: 1px; }

  .lic-btn {
    width: 100%;
    padding: 13px;
    background: var(--cyan);
    border: none;
    border-radius: var(--radius);
    color: var(--bg);
    font-family: var(--sans);
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
  }

  .lic-btn:hover { background: #33dbff; transform: translateY(-1px); box-shadow: 0 8px 24px var(--cyan-glow); }
  .lic-btn:active { transform: translateY(0); }
  .lic-btn.loading { opacity: 0.7; pointer-events: none; }

  .lic-err {
    font-size: 11px;
    min-height: 18px;
    margin-top: 10px;
    text-align: center;
    letter-spacing: 0.5px;
    color: var(--red);
    transition: color 0.2s;
  }

  .lic-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 28px 0 20px;
  }

  .lic-footer {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 1px;
  }

  .lic-dot {
    width: 6px; height: 6px;
    background: var(--muted2);
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
    vertical-align: middle;
    transition: background 0.3s;
  }
  .lic-dot.active { background: var(--green); box-shadow: 0 0 6px var(--green); animation: pulse-dot 1.4s infinite; }

  @keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  /* ══════════════════════════════════════════
     MAIN APP
  ══════════════════════════════════════════ */
  .app {
    min-height: 100vh;
    max-width: 540px;
    margin: 0 auto;
    padding: 20px 16px 40px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  /* header */
  .hdr {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 0 12px;
    border-bottom: 1px solid var(--border);
  }
  .hdr-logo {
    font-family: var(--sans);
    font-size: 22px;
    font-weight: 800;
    color: var(--cyan);
    letter-spacing: 4px;
  }
  .hdr-sub { font-size: 10px; color: var(--muted); letter-spacing: 2px; }
  .hdr-ver { margin-left: auto; font-size: 10px; color: var(--muted2); background: var(--surface2); padding: 3px 8px; border-radius: 4px; border: 1px solid var(--border); }

  /* status bar */
  .status-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    color: var(--muted);
    padding: 6px 0;
  }
  .status-bar .dot {
    width: 6px; height: 6px; border-radius: 50%; background: var(--muted2); flex-shrink: 0;
  }
  .status-bar.idle .dot   { background: var(--muted); }
  .status-bar.running .dot { background: var(--gold); box-shadow: 0 0 6px var(--gold); animation: pulse-dot 1s infinite; }
  .status-bar.done .dot   { background: var(--green); }
  .status-bar.stopped .dot { background: var(--red); }
  .status-text { color: var(--text); }

  /* stats grid */
  .stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }
  .stat {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 8px 10px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }
  .stat::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 0 0 var(--radius) var(--radius);
    opacity: 0.6;
  }
  .stat.s-created::after { background: var(--green); }
  .stat.s-active::after  { background: var(--cyan); }
  .stat.s-failed::after  { background: var(--red); }
  .stat.s-target::after  { background: var(--gold); }

  .stat-val { font-family: var(--sans); font-size: 26px; font-weight: 800; display: block; line-height: 1; }
  .stat-lbl { font-size: 8px; color: var(--muted); letter-spacing: 2px; margin-top: 5px; display: block; }
  .s-created .stat-val { color: var(--green); }
  .s-active  .stat-val { color: var(--cyan); }
  .s-failed  .stat-val { color: var(--red); }
  .s-target  .stat-val { color: var(--gold); }

  /* config row */
  .config-row {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 16px;
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
  }
  .config-field { display: flex; align-items: center; gap: 10px; }
  .config-label { font-size: 10px; letter-spacing: 2px; color: var(--muted); white-space: nowrap; }
  .config-input {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--cyan);
    font-family: var(--mono);
    font-size: 13px;
    padding: 6px 10px;
    width: 72px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .config-input:focus { border-color: var(--cyan); box-shadow: 0 0 0 2px var(--cyan-dim); }
  .proxy-badge {
    margin-left: auto;
    font-size: 10px;
    color: var(--muted);
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 3px 10px;
    white-space: nowrap;
  }

  /* run button */
  .run-btn {
    width: 100%;
    padding: 15px;
    border: none;
    border-radius: var(--radius);
    font-family: var(--sans);
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
  }
  .run-btn.idle {
    background: transparent;
    border: 1px solid var(--cyan);
    color: var(--cyan);
  }
  .run-btn.idle:hover {
    background: var(--cyan);
    color: var(--bg);
    box-shadow: 0 6px 24px var(--cyan-glow);
    transform: translateY(-1px);
  }
  .run-btn.stop {
    background: transparent;
    border: 1px solid var(--red);
    color: var(--red);
  }
  .run-btn.stop:hover { background: rgba(255,59,92,0.08); }
  .run-btn:active { transform: scale(0.99); }

  /* log */
  .log-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    flex: 1;
  }
  .log-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--muted);
  }
  .log-clear {
    font-size: 10px;
    color: var(--muted2);
    background: none;
    border: none;
    cursor: pointer;
    font-family: var(--mono);
    letter-spacing: 1px;
    padding: 2px 6px;
    border-radius: 4px;
    transition: color 0.2s, background 0.2s;
  }
  .log-clear:hover { color: var(--text); background: var(--surface2); }
  .log-box {
    padding: 10px 14px;
    height: 220px;
    overflow-y: auto;
    font-size: 11px;
    line-height: 1.8;
  }
  .log-line { display: flex; gap: 8px; }
  .log-ts { color: var(--muted2); flex-shrink: 0; }
  .ok  .log-msg { color: var(--green); }
  .err .log-msg { color: var(--red); }
  .dim .log-msg { color: var(--muted); }
  .inf .log-msg { color: var(--cyan); }

  /* footer */
  .footer {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: var(--muted2);
    padding-top: 4px;
    letter-spacing: 1px;
  }

  /* ── mobile ── */
  @media (max-width: 480px) {
    .stats { grid-template-columns: repeat(2, 1fr); }
    .config-row { gap: 12px; }
    .proxy-badge { margin-left: 0; width: 100%; text-align: center; }
    .lic-card { padding: 32px 20px 24px; }
    .stat-val { font-size: 22px; }
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .animate-in { animation: fadeIn 0.3s ease forwards; }
</style>
</head>
<body>
<div id="app"></div>

<script>
// ── License Screen ──────────────────────────────────────────────────────────
function showLicenseScreen() {
  document.getElementById('app').innerHTML = `
    <div class="lic-wrap animate-in">
      <div class="lic-card">
        <div class="lic-logo">KUNI</div>
        <div class="lic-sub">Auto SB Gen &nbsp;·&nbsp; v2.3</div>
        <span class="lic-label">LICENSE KEY</span>
        <input class="lic-input" id="licInput" type="text" placeholder="XXXX-XXXX-XXXX-XXXX" autocomplete="off" spellcheck="false" />
        <button class="lic-btn" id="licBtn" onclick="doLogin()">Verify License</button>
        <div class="lic-err" id="licErr"></div>
        <hr class="lic-divider" />
        <div class="lic-footer">
          <span><span class="lic-dot" id="connDot"></span>kuni tool</span>
          <span>unauthorized access prohibited</span>
        </div>
      </div>
    </div>
  `;
  document.getElementById('licInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') doLogin();
  });
}

async function doLogin() {
  const key = document.getElementById('licInput').value.trim();
  const err = document.getElementById('licErr');
  const btn = document.getElementById('licBtn');
  const dot = document.getElementById('connDot');
  if (!key) { err.style.color = '#f5c842'; err.textContent = 'please enter a license key'; return; }
  btn.classList.add('loading');
  btn.textContent = 'Verifying...';
  err.style.color = '#4a6070';
  err.textContent = 'connecting to license server...';
  if (dot) { dot.classList.add('active'); }
  try {
    const res = await fetch('/verify-key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key })
    });
    const data = await res.json();
    if (data.valid) {
      localStorage.setItem('license', key);
      err.style.color = '#00e87a';
      err.textContent = 'license valid — loading...';
      setTimeout(showMainApp, 600);
    } else {
      btn.classList.remove('loading');
      btn.textContent = 'Verify License';
      err.style.color = '#ff3b5c';
      err.textContent = 'invalid license — contact your reseller';
      if (dot) dot.classList.remove('active');
    }
  } catch (e) {
    btn.classList.remove('loading');
    btn.textContent = 'Verify License';
    err.style.color = '#ff3b5c';
    err.textContent = 'server error — try again';
    if (dot) dot.classList.remove('active');
  }
}

// ── Main App ────────────────────────────────────────────────────────────────
function showMainApp() {
  document.getElementById('app').innerHTML = `
    <div class="app animate-in">
      <div class="hdr">
        <div class="hdr-logo">KUNI</div>
        <div class="hdr-sub">AUTO SB GEN</div>
        <div class="hdr-ver">v2.3</div>
      </div>

      <div class="status-bar idle" id="statusBar">
        <span class="dot"></span>
        <span class="status-text" id="statusText">idle — ready</span>
      </div>

      <div class="stats">
        <div class="stat s-created"><span class="stat-val" id="s-created">0</span><span class="stat-lbl">CREATED</span></div>
        <div class="stat s-active"><span class="stat-val" id="s-active">0</span><span class="stat-lbl">ACTIVE</span></div>
        <div class="stat s-failed"><span class="stat-val" id="s-failed">0</span><span class="stat-lbl">FAILED</span></div>
        <div class="stat s-target"><span class="stat-val" id="s-target">0</span><span class="stat-lbl">TARGET</span></div>
      </div>

      <div class="config-row">
        <div class="config-field">
          <span class="config-label">COUNT</span>
          <input class="config-input" type="number" id="count" value="10" min="1" max="9999">
        </div>
        <div class="config-field">
          <span class="config-label">CONCURRENT</span>
          <input class="config-input" type="number" id="concurrent" value="10" min="1" max="50">
        </div>
        <div class="proxy-badge" id="proxyBadge">loading proxies...</div>
      </div>

      <button class="run-btn idle" id="mainBtn" onclick="toggle()">Run Generator</button>

      <div class="log-wrap">
        <div class="log-header">
          <span>LOG OUTPUT</span>
          <button class="log-clear" onclick="clearLog()">clear</button>
        </div>
        <div class="log-box" id="logBox"></div>
      </div>

      <div class="footer">
        <span>by kuni</span>
        <span id="footerStatus">idle</span>
      </div>
    </div>
  `;
  initSocket();
}

function clearLog() {
  document.getElementById('logBox').innerHTML = '';
}

function setStatus(mode, text) {
  const bar = document.getElementById('statusBar');
  bar.className = 'status-bar ' + mode;
  document.getElementById('statusText').textContent = text;
  document.getElementById('footerStatus').textContent = mode;
}

function initSocket() {
  const socket = io();
  let running = false;

  window.toggle = function() {
    if (running) {
      socket.emit('stop');
    } else {
      const count = parseInt(document.getElementById('count').value) || 10;
      const concurrent = parseInt(document.getElementById('concurrent').value) || 10;
      socket.emit('start', { count, concurrent });
    }
  };

  socket.on('connect', () => socket.emit('get_info'));

  socket.on('info', d => {
    document.getElementById('proxyBadge').textContent = d.proxies + ' proxies loaded';
  });

  socket.on('log', d => {
    const box = document.getElementById('logBox');
    const line = document.createElement('div');
    line.className = 'log-line ' + (d.tag || 'dim');
    const msg = d.msg || '';
    const tsMatch = msg.match(/^\[(\d{2}:\d{2}:\d{2})\]\s*(.*)/s);
    if (tsMatch) {
      line.innerHTML = `<span class="log-ts">${tsMatch[1]}</span><span class="log-msg">${tsMatch[2]}</span>`;
    } else {
      line.innerHTML = `<span class="log-msg">${msg}</span>`;
    }
    box.appendChild(line);
    box.scrollTop = box.scrollHeight;
  });

  socket.on('stats', d => {
    document.getElementById('s-created').textContent = d.created;
    document.getElementById('s-active').textContent  = d.active;
    document.getElementById('s-failed').textContent  = d.failed;
    document.getElementById('s-target').textContent  = d.target;
  });

  socket.on('started', d => {
    running = true;
    const btn = document.getElementById('mainBtn');
    btn.className = 'run-btn stop';
    btn.textContent = '■  Stop';
    setStatus('running', 'running — ' + d.count + ' accounts');
  });

  socket.on('stopped', () => {
    running = false;
    const btn = document.getElementById('mainBtn');
    btn.className = 'run-btn idle';
    btn.textContent = 'Run Generator';
    setStatus('stopped', 'stopped');
  });

  socket.on('done', d => {
    running = false;
    const btn = document.getElementById('mainBtn');
    btn.className = 'run-btn idle';
    btn.textContent = 'Run Generator';
    setStatus('done', 'done — ' + d.created + '/' + d.total + ' created');
  });
}

// ── Init ────────────────────────────────────────────────────────────────────
if (localStorage.getItem('license')) {
  showMainApp();
} else {
  showLicenseScreen();
}
</script>
</body>
</html>
"""

# ── Flask Routes + SocketIO Events ────────────────────────────────────────────

@app.route("/")
def index():
    return HTML


@socketio.on("get_info")
def on_info():
    emit("info", {"proxies": len(proxies_list)})


@socketio.on("start")
def on_start(data):
    if not license_valid:
        return
    if state["running"]:
        return
    count      = int(data.get("count", 10))
    concurrent = int(data.get("concurrent", 10))

    state["running"] = True
    state["stop"]    = False
    state["created"] = 0
    state["active"]  = 0
    state["failed"]  = 0
    state["target"]  = count

    emit("started", {"count": count})
    log_emit(f"Starting {count} accounts ({concurrent} concurrent)...", "inf")

    threading.Thread(
        target=run_generator,
        args=(count, concurrent),
        daemon=True
    ).start()


@socketio.on("stop")
def on_stop():
    state["stop"] = True
    emit("stopped")
    log_emit("Stopping...", "inf")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n[KUNI] SB Generator running!")
    print(f"[KUNI] Open http://localhost:{port} in your browser\n")
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
