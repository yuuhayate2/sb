# KUNI SB GENERATOR - FULL FIXED VERSION

import json
import os
import random
import string
import threading
import hashlib

from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = "https://ukwltgxtfikrpsqfihi.supabase.co"
SUPABASE_KEY = "sb_publishable_NhI5Z-LriMN_huWOV14AtA_YtmDZeQ3"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

current_license = None

state = {
    "running": False,
    "created": 0,
    "active": 0,
    "failed": 0,
    "target": 0,
    "stop": False
}

def get_hwid(ip):
    return hashlib.sha256(ip.encode()).hexdigest()

@app.route("/verify-key", methods=["POST"])
def verify_key():

    global current_license

    data = request.json
    key = data.get("key")

    hwid = get_hwid(request.remote_addr)

    url = f"{SUPABASE_URL}/rest/v1/licenses"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    params = {
        "license_key": f"eq.{key}"
    }

    res = requests.get(url, headers=headers, params=params)
    data = res.json()

    if not data:
        return jsonify({"valid": False})

    license = data[0]

    if license["status"] != "active":
        return jsonify({"valid": False})

    if license["hwid"] and license["hwid"] != hwid:
        return jsonify({"valid": False})

    if not license["hwid"]:
        requests.patch(
            url,
            headers=headers,
            params={"license_key": f"eq.{key}"},
            json={"hwid": hwid}
        )

    current_license = license

    return jsonify({"valid": True})

def rand_username():
    return "Kuni" + "".join(random.choices(string.ascii_letters + string.digits, k=10))

def rand_password():
    return "".join(random.choices(string.ascii_letters + string.digits, k=14))

def create_account(slot):

    global current_license

    if current_license:
        if current_license["accounts_used"] >= current_license["accounts_limit"]:
            return

    username = rand_username()
    password = rand_password()

    try:
        state["created"] += 1

        requests.patch(
            f"{SUPABASE_URL}/rest/v1/licenses",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            params={
                "license_key": f"eq.{current_license['license_key']}"
            },
            json={
                "accounts_used": current_license["accounts_used"] + 1
            }
        )

    except:
        state["failed"] += 1

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>KUNI GENERATOR</title>
</head>

<body style="background:#080c10;color:white;font-family:monospace">

<h1>KUNI GENERATOR</h1>

<input id="key" placeholder="Enter License Key">

<button onclick="login()">Login</button>

<br><br>

<button onclick="start()">Start Generator</button>

<script>

async function login(){

const key = document.getElementById("key").value

const res = await fetch("/verify-key",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({key})
})

const data = await res.json()

if(data.valid){
alert("Login Success")
}else{
alert("Invalid Key")
}

}

function start(){

fetch("/start",{
method:"POST"
})

}

</script>

</body>
</html>
"""

@app.route("/")
def index():
    return HTML

@app.route("/start", methods=["POST"])
def start():

    for i in range(10):
        create_account(i)

    return "started"

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
