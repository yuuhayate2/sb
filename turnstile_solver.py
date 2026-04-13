# turnstile_solver.py — CapSolver Turnstile bypass
import asyncio, os, time, requests
from dotenv import load_dotenv
from playwright.async_api import BrowserContext, Page

load_dotenv()

CAPSOLVER_KEY    = os.getenv("CAPSOLVER_KEY", "")
SB_TURNSTILE_KEY = "0x4AAAAAAADI1KFhXIM1zitP"
SB_SIGNUP_URL    = "https://scriptblox.com/signup"
SB_UPLOAD_URL    = "https://scriptblox.com/script/create"
NO_PROXY         = {"http": None, "https": None}  # bypass proxy for CapSolver


def capsolver_create_task(site_key, page_url):
    try:
        r = requests.post("https://api.capsolver.com/createTask", json={
            "clientKey": CAPSOLVER_KEY,
            "task": {
                "type": "AntiTurnstileTaskProxyLess",
                "websiteURL": page_url,
                "websiteKey": site_key,
                "metadata": {"action": ""}
            }
        }, timeout=30, proxies=NO_PROXY)
        data = r.json()
        if data.get("errorId", 1) == 0:
            return data.get("taskId")
        print(f"[!] CapSolver error: {data.get('errorDescription')}")
        return None
    except Exception as e:
        print(f"[!] CapSolver exception: {e}")
        return None


def capsolver_get_result(task_id, retries=30, interval=2.0):
    for _ in range(retries):
        try:
            r = requests.post("https://api.capsolver.com/getTaskResult", json={
                "clientKey": CAPSOLVER_KEY, "taskId": task_id
            }, timeout=30, proxies=NO_PROXY)
            data = r.json()
            if data.get("status") == "ready":
                return data.get("solution", {}).get("token")
            if data.get("errorId", 0) != 0:
                print(f"[!] CapSolver poll error: {data.get('errorDescription')}")
                return None
        except Exception as e:
            print(f"[!] CapSolver poll exception: {e}")
        time.sleep(interval)
    return None


def solve_turnstile_capsolver(page_url=SB_SIGNUP_URL, site_key=SB_TURNSTILE_KEY):
    print(f"[→] CapSolver: creating task...")
    task_id = capsolver_create_task(site_key, page_url)
    if not task_id: return None
    print(f"[→] CapSolver: waiting... (taskId={task_id[:12]}...)")
    token = capsolver_get_result(task_id)
    if token: print(f"[✓] CapSolver: token received!")
    else: print(f"[✗] CapSolver: failed")
    return token


async def inject_turnstile_callback(ctx: BrowserContext):
    await ctx.add_init_script("""
        window.__turnstileToken = '';
        const _patch = () => {
            if (!window.turnstile || window.__patched) return;
            window.__patched = true;
            const orig = window.turnstile.render.bind(window.turnstile);
            window.turnstile.render = (el, params) => {
                const cb = params.callback;
                params.callback = (token) => {
                    window.__turnstileToken = token;
                    if (cb) cb(token);
                };
                return orig(el, params);
            };
        };
        _patch();
        document.addEventListener('DOMContentLoaded', _patch);
        setTimeout(_patch, 500); setTimeout(_patch, 1500);
    """)

async def get_token_from_page(page: Page):
    for _ in range(150):
        token = await page.evaluate("""() => {
            const inp = document.querySelector('input[name="cf-turnstile-response"]');
            if (inp?.value?.length > 40) return inp.value;
            if (window.__turnstileToken?.length > 40) return window.__turnstileToken;
            return null;
        }""")
        if token: return token
        await asyncio.sleep(0.3)
    return None

async def wait_for_turnstile(page: Page, timeout=45):
    return bool(await get_token_from_page(page))

async def click_and_wait_turnstile(page: Page, selector, timeout=45):
    try:
        await page.click(selector)
        return await wait_for_turnstile(page, timeout)
    except: return True
