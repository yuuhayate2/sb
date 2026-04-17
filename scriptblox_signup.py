HTML = r"""<!DOCTYPE html>
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
    --bg: #080b0f;
    --surface: #0d1117;
    --surface2: #161b22;
    --surface3: #1c2330;
    --border: #21262d;
    --border2: #30363d;
    --cyan: #58a6ff;
    --cyan-glow: rgba(88,166,255,0.15);
    --cyan-dim: rgba(88,166,255,0.08);
    --green: #3fb950;
    --green-glow: rgba(63,185,80,0.15);
    --red: #f85149;
    --red-dim: rgba(248,81,73,0.1);
    --gold: #d29922;
    --gold-dim: rgba(210,153,34,0.1);
    --purple: #a371f7;
    --purple-dim: rgba(163,113,247,0.1);
    --text: #c9d1d9;
    --text2: #8b949e;
    --text3: #484f58;
    --mono: 'Space Mono', monospace;
    --sans: 'Syne', sans-serif;
    --radius: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
  }
  html, body { height: 100%; background: var(--bg); color: var(--text); font-family: var(--mono); }
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

  /* ── LICENSE SCREEN ── */
  .lic-wrap {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px 16px;
    background: radial-gradient(ellipse 70% 50% at 50% -10%, rgba(88,166,255,0.08) 0%, transparent 60%), var(--bg);
  }
  .lic-card {
    width: 100%;
    max-width: 500px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 40px 32px 32px;
    position: relative;
    overflow: hidden;
  }
  .lic-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
  }
  .lic-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }
  .lic-icon {
    width: 40px; height: 40px;
    background: var(--cyan-dim);
    border: 1px solid rgba(88,166,255,0.3);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
  }
  .lic-logo {
    font-family: var(--sans);
    font-size: 28px;
    font-weight: 800;
    color: var(--cyan);
    letter-spacing: 4px;
  }
  .lic-sub {
    font-size: 11px;
    letter-spacing: 2px;
    color: var(--text2);
    margin-bottom: 32px;
    padding-left: 52px;
  }
  .lic-label {
    font-size: 11px;
    letter-spacing: 2px;
    color: var(--text2);
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
    transition: border-color .2s, box-shadow .2s;
    margin-bottom: 12px;
  }
  .lic-input:focus { border-color: var(--cyan); box-shadow: 0 0 0 3px var(--cyan-dim); }
  .lic-input::placeholder { color: var(--text3); letter-spacing: 1px; }
  .lic-btn {
    width: 100%;
    padding: 14px;
    background: var(--cyan);
    border: none;
    border-radius: var(--radius);
    color: #0d1117;
    font-family: var(--sans);
    font-weight: 800;
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    cursor: pointer;
    transition: all .2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }
  .lic-btn:hover { filter: brightness(1.1); transform: translateY(-1px); box-shadow: 0 8px 32px var(--cyan-glow); }
  .lic-btn.loading { opacity: .6; pointer-events: none; }
  .lic-err { font-size: 11px; min-height: 20px; margin-top: 10px; text-align: center; letter-spacing: .5px; color: var(--red); }

  /* pricing */
  .price-section { margin-top: 28px; padding-top: 24px; border-top: 1px solid var(--border); }
  .price-title {
    font-size: 10px;
    letter-spacing: 3px;
    color: var(--text3);
    margin-bottom: 14px;
    text-align: center;
    text-transform: uppercase;
  }
  .price-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px; }
  .price-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 10px;
    text-align: center;
    transition: border-color .2s, transform .2s;
    cursor: default;
  }
  .price-card:hover { border-color: var(--border2); transform: translateY(-2px); }
  .price-card.featured { border-color: rgba(88,166,255,0.4); background: rgba(88,166,255,0.05); }
  .price-badge {
    display: inline-block;
    font-size: 9px;
    letter-spacing: 1.5px;
    color: var(--cyan);
    background: var(--cyan-dim);
    border-radius: 20px;
    padding: 2px 8px;
    margin-bottom: 8px;
    text-transform: uppercase;
  }
  .price-name { font-family: var(--sans); font-size: 11px; font-weight: 700; color: var(--text); letter-spacing: 1px; margin-bottom: 4px; }
  .price-limit { font-size: 9px; color: var(--text2); letter-spacing: 1px; margin-bottom: 10px; }
  .price-amt { font-family: var(--sans); font-size: 16px; font-weight: 800; color: var(--text); }
  .price-card.featured .price-amt { color: var(--cyan); }
  .price-php { font-size: 9px; color: var(--text2); margin-top: 2px; }

  /* discord */
  .discord-section { text-align: center; }
  .discord-label { font-size: 10px; color: var(--text2); letter-spacing: 1px; margin-bottom: 10px; }
  .discord-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 12px 24px;
    background: rgba(88,101,242,0.08);
    border: 1px solid rgba(88,101,242,0.35);
    border-radius: var(--radius);
    color: #8a96ff;
    font-family: var(--mono);
    font-size: 12px;
    letter-spacing: 1px;
    text-decoration: none;
    transition: all .2s;
    width: 100%;
  }
  .discord-btn:hover { background: rgba(88,101,242,0.15); color: #fff; transform: translateY(-1px); }
  .lic-footer {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: var(--text3);
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
  }
  .status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); display: inline-block; margin-right: 6px; vertical-align: middle; animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

  /* ── MAIN APP ── */
  .app { min-height: 100vh; max-width: 620px; margin: 0 auto; padding: 20px 16px 60px; display: flex; flex-direction: column; gap: 14px; }

  /* header */
  .hdr {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 0 16px;
    border-bottom: 1px solid var(--border);
  }
  .hdr-icon {
    width: 44px; height: 44px;
    background: var(--cyan-dim);
    border: 1px solid rgba(88,166,255,0.25);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
  }
  .hdr-logo { font-family: var(--sans); font-size: 20px; font-weight: 800; color: var(--cyan); letter-spacing: 3px; }
  .hdr-sub { font-size: 10px; color: var(--text2); letter-spacing: 2px; margin-top: 2px; }
  .hdr-right { margin-left: auto; display: flex; align-items: center; gap: 8px; }
  .ver-badge {
    font-size: 10px;
    color: var(--text2);
    background: var(--surface2);
    padding: 4px 10px;
    border-radius: 20px;
    border: 1px solid var(--border);
    letter-spacing: .5px;
  }
  .plan-badge {
    font-size: 10px;
    letter-spacing: 1px;
    color: var(--gold);
    background: var(--gold-dim);
    border: 1px solid rgba(210,153,34,.3);
    border-radius: 20px;
    padding: 4px 12px;
  }

  /* status bar */
  .status-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 12px;
    color: var(--text2);
    padding: 10px 14px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
  }
  .status-bar .s-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--text3); flex-shrink: 0; }
  .status-bar.running .s-dot { background: var(--gold); animation: pulse 1s infinite; }
  .status-bar.done .s-dot { background: var(--green); }
  .status-bar.stopped .s-dot, .status-bar.limit .s-dot { background: var(--red); }
  .status-bar .s-text { color: var(--text); }
  .status-bar .s-icon { margin-left: auto; font-size: 16px; }

  /* stats grid */
  .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
  .stat {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 12px 12px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: border-color .2s;
  }
  .stat:hover { border-color: var(--border2); }
  .stat-icon { font-size: 18px; display: block; margin-bottom: 6px; }
  .stat-val { font-family: var(--sans); font-size: 28px; font-weight: 800; display: block; line-height: 1; }
  .stat-lbl { font-size: 9px; color: var(--text2); letter-spacing: 2px; margin-top: 6px; display: block; text-transform: uppercase; }
  .stat-bar { position: absolute; bottom: 0; left: 0; right: 0; height: 2px; }
  .s-created .stat-val { color: var(--green); }
  .s-created .stat-bar { background: var(--green); opacity: .6; }
  .s-active .stat-val { color: var(--cyan); }
  .s-active .stat-bar { background: var(--cyan); opacity: .6; }
  .s-failed .stat-val { color: var(--red); }
  .s-failed .stat-bar { background: var(--red); opacity: .6; }
  .s-target .stat-val { color: var(--gold); }
  .s-target .stat-bar { background: var(--gold); opacity: .6; }

  /* limit bar */
  .limit-bar-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 16px;
  }
  .limit-bar-top { display: flex; justify-content: space-between; font-size: 11px; color: var(--text2); margin-bottom: 10px; letter-spacing: 1px; }
  .limit-bar-top .lbl { display: flex; align-items: center; gap: 6px; }
  .limit-bar-track { height: 6px; background: var(--border); border-radius: 6px; overflow: hidden; }
  .limit-bar-fill { height: 100%; background: var(--cyan); border-radius: 6px; transition: width .4s ease; }
  .limit-bar-fill.warn { background: var(--gold); }
  .limit-bar-fill.danger { background: var(--red); }

  /* config card */
  .config-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
  }
  .config-hdr {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    font-size: 11px;
    letter-spacing: 2px;
    color: var(--text2);
    cursor: pointer;
    user-select: none;
    transition: background .15s;
    text-transform: uppercase;
  }
  .config-hdr:hover { background: var(--surface2); }
  .config-hdr-icon { font-size: 14px; }
  .config-toggle { margin-left: auto; font-size: 10px; letter-spacing: 1px; color: var(--text3); }
  .config-body { padding: 16px; display: flex; flex-direction: column; gap: 14px; }

  /* count row */
  .config-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
  .config-field { display: flex; align-items: center; gap: 10px; }
  .config-label { font-size: 10px; letter-spacing: 1.5px; color: var(--text2); white-space: nowrap; text-transform: uppercase; }
  .config-input {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--cyan);
    font-family: var(--mono);
    font-size: 13px;
    padding: 7px 12px;
    width: 80px;
    outline: none;
    transition: border-color .2s;
  }
  .config-input:focus { border-color: var(--cyan); }

  /* panel (proxies) */
  .panel-wrap {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
  }
  .panel-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    letter-spacing: 1.5px;
    color: var(--text2);
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    user-select: none;
    transition: background .15s;
    text-transform: uppercase;
  }
  .panel-label:hover { background: var(--surface2); color: var(--text); }
  .panel-label-icon { font-size: 14px; }
  .panel-badge { margin-left: auto; font-size: 10px; color: var(--text3); }
  .panel-badge.ok { color: var(--green); }
  .panel-inner { display: none; }
  .panel-inner.open { display: block; }
  .panel-textarea {
    width: 100%;
    min-height: 90px;
    padding: 12px 14px;
    resize: vertical;
    background: transparent;
    border: none;
    outline: none;
    color: var(--cyan);
    font-family: var(--mono);
    font-size: 11px;
    line-height: 1.8;
  }
  .panel-textarea::placeholder { color: var(--text3); }
  .panel-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    border-top: 1px solid var(--border);
  }
  .panel-btn {
    padding: 6px 16px;
    background: transparent;
    border: 1px solid var(--cyan);
    border-radius: var(--radius);
    color: var(--cyan);
    font-family: var(--sans);
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 2px;
    cursor: pointer;
    transition: all .15s;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .panel-btn:hover { background: var(--cyan); color: var(--bg); }
  .panel-status { font-size: 10px; color: var(--text2); letter-spacing: 1px; margin-left: auto; }

  /* webhook */
  .webhook-wrap {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    transition: border-color .3s;
  }
  .webhook-wrap.required { border-color: rgba(248,81,73,.5); }
  .webhook-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 14px;
    border-bottom: 1px solid var(--border);
  }
  .webhook-icon { font-size: 14px; flex-shrink: 0; }
  .webhook-lbl { font-size: 10px; letter-spacing: 1.5px; color: var(--text2); white-space: nowrap; flex-shrink: 0; text-transform: uppercase; }
  .webhook-wrap.required .webhook-lbl { color: var(--red); }
  .webhook-input {
    flex: 1;
    padding: 11px 0;
    background: transparent;
    border: none;
    outline: none;
    color: var(--cyan);
    font-family: var(--mono);
    font-size: 11px;
  }
  .webhook-input::placeholder { color: var(--text3); }
  .webhook-req-note { font-size: 9px; padding: 4px 14px 2px; color: var(--red); letter-spacing: 1px; display: none; }
  .webhook-wrap.required .webhook-req-note { display: block; }

  /* warn / limit banners */
  .warn-banner {
    background: var(--gold-dim);
    border: 1px solid rgba(210,153,34,.35);
    border-radius: var(--radius);
    padding: 12px 16px;
    font-size: 11px;
    color: var(--gold);
    display: none;
    align-items: flex-start;
    gap: 10px;
    line-height: 1.6;
  }
  .warn-banner.show { display: flex; }
  .warn-banner .warn-icon { font-size: 16px; flex-shrink: 0; }
  .warn-banner strong { color: var(--text); }
  .limit-banner {
    background: var(--red-dim);
    border: 1px solid rgba(248,81,73,.3);
    border-radius: var(--radius);
    padding: 12px 16px;
    font-size: 11px;
    color: var(--red);
    display: none;
    align-items: center;
    gap: 10px;
  }
  .limit-banner.show { display: flex; }

  /* tutorial */
  .tutorial-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
  }
  .tutorial-hdr {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    font-size: 11px;
    letter-spacing: 1.5px;
    color: var(--text2);
    cursor: pointer;
    user-select: none;
    transition: background .15s;
    text-transform: uppercase;
  }
  .tutorial-hdr:hover { background: var(--surface2); }
  .tutorial-hdr-icon { font-size: 14px; }
  .tutorial-body { display: none; padding: 16px; }
  .tutorial-body.open { display: block; }
  .video-container {
    position: relative;
    width: 100%;
    padding-top: 56.25%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
  }
  .video-el { position: absolute; inset: 0; width: 100%; height: 100%; }

  /* RUN BUTTON */
  .run-btn {
    width: 100%;
    padding: 16px;
    border: none;
    border-radius: var(--radius-lg);
    font-family: var(--sans);
    font-weight: 800;
    font-size: 14px;
    letter-spacing: 3px;
    text-transform: uppercase;
    cursor: pointer;
    transition: all .2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }
  .run-btn.idle {
    background: linear-gradient(135deg, rgba(88,166,255,0.15), rgba(88,166,255,0.05));
    border: 1px solid rgba(88,166,255,0.5);
    color: var(--cyan);
  }
  .run-btn.idle:hover {
    background: var(--cyan);
    color: var(--bg);
    box-shadow: 0 8px 32px var(--cyan-glow);
    transform: translateY(-1px);
  }
  .run-btn.stop {
    background: linear-gradient(135deg, rgba(248,81,73,0.12), rgba(248,81,73,0.05));
    border: 1px solid rgba(248,81,73,.5);
    color: var(--red);
  }
  .run-btn.stop:hover { background: rgba(248,81,73,.08); }
  .run-btn.disabled-btn { opacity: .35; pointer-events: none; border: 1px solid var(--border); color: var(--text2); background: transparent; }

  /* LOG */
  .log-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
  }
  .log-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
    font-size: 11px;
    letter-spacing: 2px;
    color: var(--text2);
    text-transform: uppercase;
  }
  .log-header-icon { font-size: 14px; }
  .log-clear {
    font-size: 10px;
    color: var(--text3);
    background: none;
    border: none;
    cursor: pointer;
    font-family: var(--mono);
    padding: 3px 8px;
    border-radius: 4px;
    margin-left: auto;
    transition: color .2s, background .2s;
    letter-spacing: 1px;
  }
  .log-clear:hover { color: var(--text); background: var(--surface2); }
  .log-box { padding: 12px 16px; height: 240px; overflow-y: auto; font-size: 11px; line-height: 1.9; }
  .log-line { display: flex; gap: 10px; margin-bottom: 1px; }
  .log-ts { color: var(--text3); flex-shrink: 0; }
  .log-tag { flex-shrink: 0; font-size: 9px; letter-spacing: 1px; }
  .ok .log-tag { color: var(--green); }
  .ok .log-msg { color: #56d364; }
  .err .log-tag { color: var(--red); }
  .err .log-msg { color: var(--red); }
  .dim .log-tag { color: var(--text3); }
  .dim .log-msg { color: var(--text2); }
  .inf .log-tag { color: var(--cyan); }
  .inf .log-msg { color: var(--cyan); }

  /* footer */
  .footer { display: flex; justify-content: space-between; font-size: 10px; color: var(--text3); padding-top: 4px; letter-spacing: 1px; }
  .footer a { color: var(--text3); text-decoration: none; transition: color .2s; }
  .footer a:hover { color: var(--red); }

  /* proxy info strip */
  .proxy-strip {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    background: rgba(63,185,80,0.06);
    border-top: 1px solid var(--border);
    font-size: 10px;
    color: var(--text2);
    letter-spacing: 1px;
  }
  .proxy-strip .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); animation: pulse 2s infinite; }
  .proxy-strip.empty .dot { background: var(--text3); animation: none; }
  .proxy-strip.empty { background: transparent; }

  @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
  .animate-in { animation: fadeIn .3s ease forwards; }

  @media (max-width: 480px) {
    .stats { grid-template-columns: repeat(2, 1fr); }
    .lic-card { padding: 32px 20px 24px; }
    .price-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<div id="app"></div>
<script>
let licenseInfo = null;
let sessionToken = null;
let socket = null;
let running = false;
let webhookSet = false;
let cfgOpen = true;
let tutOpen = false;

const ERR_MAP = {
  not_found:     'invalid license key — contact kuni',
  disabled:      'this license has been disabled',
  expired:       'license has expired — contact kuni',
  hwid_mismatch: 'key is bound to another machine',
  limit_reached: 'account limit reached — upgrade your plan',
  rate_limited:  'too many attempts — wait 1 min',
  server_error:  'server error — try again later',
};

function getLsToken() {
  let t = localStorage.getItem('_kuni_lst');
  if (!t) { t = [...crypto.getRandomValues(new Uint8Array(16))].map(b => b.toString(16).padStart(2,'0')).join(''); localStorage.setItem('_kuni_lst', t); }
  return t;
}

async function getCanvasFp() {
  try {
    const c = document.createElement('canvas'), ctx = c.getContext('2d');
    ctx.textBaseline = 'top'; ctx.font = '14px Arial';
    ctx.fillStyle = '#f60'; ctx.fillRect(125, 1, 62, 20);
    ctx.fillStyle = '#069'; ctx.fillText('kuni-fp', 2, 15);
    return c.toDataURL().slice(-64);
  } catch { return ''; }
}

async function sha256Hex(s) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,'0')).join('');
}

async function getDeviceFingerprint() {
  try {
    const raw = [navigator.userAgent, navigator.language, screen.width+'x'+screen.height, screen.colorDepth, new Date().getTimezoneOffset(), navigator.hardwareConcurrency||0, navigator.platform, await getCanvasFp()].join('|');
    return await sha256Hex(raw);
  } catch {
    let id = localStorage.getItem('_did');
    if (!id) { id = Math.random().toString(36).slice(2)+Math.random().toString(36).slice(2); localStorage.setItem('_did', id); }
    return id;
  }
}

async function getExtraFp() {
  return await sha256Hex(navigator.userAgent + navigator.platform);
}

async function authFetch(url, opts) {
  opts = opts || {};
  const headers = Object.assign({'Content-Type': 'application/json'}, opts.headers || {});
  if (sessionToken) headers['X-Session-Token'] = sessionToken;
  return fetch(url, Object.assign({}, opts, {headers}));
}

/* ─────────────────────────────────── LICENSE SCREEN ─── */
function showLicenseScreen() {
  document.getElementById('app').innerHTML = `
    <div class="lic-wrap animate-in">
      <div class="lic-card">
        <div class="lic-brand">
          <div class="lic-icon">🚀</div>
          <div class="lic-logo">KUNI</div>
        </div>
        <div class="lic-sub">Auto SB Gen &nbsp;·&nbsp; v2.6</div>

        <span class="lic-label">🔑 LICENSE KEY</span>
        <input class="lic-input" id="licInput" type="text" placeholder="KUNI-XXXX-XXXX-XXXX" autocomplete="off" spellcheck="false">
        <button class="lic-btn" id="licBtn" onclick="doLogin()">
          <span>⚡</span> Verify License
        </button>
        <div class="lic-err" id="licErr"></div>

        <div class="price-section">
          <div class="price-title">💎 Pricing Plans</div>
          <div class="price-grid">
            <div class="price-card">
              <div class="price-name">BASIC</div>
              <div class="price-limit">100 accounts</div>
              <div class="price-amt">$59.99</div>
              <div class="price-php">≈ ₱3,389 · 30 days</div>
            </div>
            <div class="price-card featured">
              <div class="price-badge">POPULAR</div>
              <div class="price-name">PRO</div>
              <div class="price-limit">500 accounts</div>
              <div class="price-amt">$249.99</div>
              <div class="price-php">≈ ₱14,124 · 30 days</div>
            </div>
            <div class="price-card">
              <div class="price-name">UNLIMITED</div>
              <div class="price-limit">no limit</div>
              <div class="price-amt">$399.99</div>
              <div class="price-php">≈ ₱22,599 · 60 days</div>
            </div>
          </div>
          <div class="discord-section">
            <div class="discord-label">🎮 join our server to purchase</div>
            <a class="discord-btn" href="https://discord.gg/Qvy4BSGJvC" target="_blank">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03z"/></svg>
              Join <strong style="color:#fff">Kuni Server</strong>
            </a>
          </div>
        </div>

        <div class="lic-footer">
          <span><span class="status-dot"></span>kuni tool</span>
          <span>v2.6 · 2025</span>
        </div>
      </div>
    </div>`;
  document.getElementById('licInput').addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); });
}

async function doLogin() {
  const key = document.getElementById('licInput').value.trim();
  const err = document.getElementById('licErr');
  const btn = document.getElementById('licBtn');
  if (!key) { err.style.color='var(--gold)'; err.textContent='⚠ please enter a license key'; return; }
  btn.classList.add('loading'); btn.textContent = '⏳ Verifying...';
  err.style.color='var(--text2)'; err.textContent='🔄 connecting...';
  try {
    const [hwid, fp] = await Promise.all([getDeviceFingerprint(), getExtraFp()]);
    const ls_token = getLsToken();
    const res = await fetch('/verify-key',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key, hwid, ls_token, fp})});
    const data = await res.json();
    if (data.valid) {
      sessionToken = data.session_token;
      localStorage.setItem('license', key);
      localStorage.setItem('session_token', sessionToken);
      if (data.ls_token) localStorage.setItem('_kuni_lst', data.ls_token);
      licenseInfo = data;
      err.style.color='var(--green)'; err.textContent='✅ license valid — loading...';
      setTimeout(showMainApp, 600);
    } else {
      btn.classList.remove('loading'); btn.innerHTML='<span>⚡</span> Verify License';
      err.style.color='var(--red)'; err.textContent = '❌ '+(ERR_MAP[data.error] || 'invalid license — contact kuni');
    }
  } catch {
    btn.classList.remove('loading'); btn.innerHTML='<span>⚡</span> Verify License';
    err.style.color='var(--red)'; err.textContent='❌ server error';
  }
}

/* ─────────────────────────────────── MAIN APP ─── */
function showMainApp() {
  const planLabel = licenseInfo ? licenseInfo.plan : '-';
  const isUnlimited = licenseInfo && licenseInfo.limit >= 9999;

  document.getElementById('app').innerHTML = `
    <div class="app animate-in">
      <!-- Header -->
      <div class="hdr">
        <div class="hdr-icon">🚀</div>
        <div>
          <div class="hdr-logo">KUNI</div>
          <div class="hdr-sub">AUTO SB GEN · SCRIPTBLOX</div>
        </div>
        <div class="hdr-right">
          <span class="plan-badge" id="planBadge">💎 ${planLabel}</span>
          <div class="ver-badge">v2.6</div>
        </div>
      </div>

      <!-- Status -->
      <div class="status-bar idle" id="statusBar">
        <span class="s-dot"></span>
        <span class="s-text" id="statusText">💤 idle — ready to generate</span>
        <span class="s-icon" id="statusIcon">⬛</span>
      </div>

      <!-- Webhook warning -->
      <div class="warn-banner" id="webhookWarn">
        <span class="warn-icon">⚠️</span>
        <div><strong>Discord webhook required.</strong> Set your webhook below before running the generator.</div>
      </div>

      <!-- Stats -->
      <div class="stats">
        <div class="stat s-created">
          <span class="stat-icon">✅</span>
          <span class="stat-val" id="s-created">0</span>
          <span class="stat-lbl">Created</span>
          <div class="stat-bar"></div>
        </div>
        <div class="stat s-active">
          <span class="stat-icon">⚡</span>
          <span class="stat-val" id="s-active">0</span>
          <span class="stat-lbl">Active</span>
          <div class="stat-bar"></div>
        </div>
        <div class="stat s-failed">
          <span class="stat-icon">❌</span>
          <span class="stat-val" id="s-failed">0</span>
          <span class="stat-lbl">Failed</span>
          <div class="stat-bar"></div>
        </div>
        <div class="stat s-target">
          <span class="stat-icon">🎯</span>
          <span class="stat-val" id="s-target">0</span>
          <span class="stat-lbl">Target</span>
          <div class="stat-bar"></div>
        </div>
      </div>

      <!-- Limit bar -->
      ${!isUnlimited ? `
      <div class="limit-bar-wrap">
        <div class="limit-bar-top">
          <span class="lbl">📊 Account Usage</span>
          <span id="limitText" style="color:var(--text)">loading...</span>
        </div>
        <div class="limit-bar-track"><div class="limit-bar-fill" id="limitBar" style="width:0%"></div></div>
      </div>` : ''}

      <!-- Limit banner -->
      <div class="limit-banner" id="limitBanner">
        <span>🚫</span>
        <span>Account limit reached — contact Kuni to upgrade your plan.</span>
      </div>

      <!-- Config -->
      <div class="config-card">
        <div class="config-hdr" onclick="toggleConfig()">
          <span class="config-hdr-icon">⚙️</span>
          <span>Configuration</span>
          <span class="config-toggle" id="cfgToggle">HIDE</span>
        </div>
        <div class="config-body" id="cfgBody">

          <!-- Count + Concurrent -->
          <div class="config-row">
            <div class="config-field">
              <span class="config-label">📦 Count</span>
              <input class="config-input" type="number" id="count" value="10" min="1" max="9999">
            </div>
            <div class="config-field">
              <span class="config-label">🔀 Concurrent</span>
              <input class="config-input" type="number" id="concurrent" value="10" min="1" max="50">
            </div>
          </div>

          <!-- Proxies -->
          <div class="panel-wrap">
            <div class="panel-label" onclick="togglePanel('proxyPanel')">
              <span class="panel-label-icon">🌐</span>
              <span>Proxies (rotating)</span>
              <span class="panel-badge" id="proxyBadge">loading...</span>
            </div>
            <div class="panel-inner" id="proxyPanel">
              <textarea class="panel-textarea" id="proxyTA" placeholder="paste proxies — one per line&#10;user:pass@host:port  or  host:port  or  http://user:pass@host:port&#10;&#10;each account uses a random proxy from this list"></textarea>
              <div class="proxy-strip empty" id="proxyStrip">
                <span class="dot"></span>
                <span id="proxyStripTxt">no proxies loaded</span>
              </div>
              <div class="panel-actions">
                <button class="panel-btn" onclick="saveProxies()">💾 Save Proxies</button>
                <span class="panel-status" id="proxySt"></span>
              </div>
            </div>
          </div>

          <!-- Webhook -->
          <div class="webhook-wrap" id="webhookWrap">
            <div class="webhook-row">
              <span class="webhook-icon">📡</span>
              <span class="webhook-lbl">Webhook <span id="webhookReqMark" style="color:var(--red)">*</span></span>
              <input class="webhook-input" id="webhookInput" type="text" placeholder="https://discord.com/api/webhooks/...">
            </div>
            <div class="webhook-req-note">⚠ Required — accounts are delivered here</div>
            <div class="panel-actions">
              <button class="panel-btn" onclick="saveWebhook()">📡 Save &amp; Test</button>
              <span class="panel-status" id="webhookSt"></span>
            </div>
          </div>

        </div>
      </div>

      <!-- Run Button -->
      <button class="run-btn idle" id="mainBtn" onclick="toggle()">
        <span>🚀</span> Run Generator
      </button>

      <!-- Tutorial -->
      <div class="tutorial-card">
        <div class="tutorial-hdr" onclick="toggleTutorial()">
          <span class="tutorial-hdr-icon">🎬</span>
          <span>How to use your accounts</span>
          <span id="tutToggle" style="margin-left:auto;font-size:9px;letter-spacing:2px;color:var(--text3)">SHOW</span>
        </div>
        <div class="tutorial-body" id="tutBody">
          <div class="video-container">
            <iframe src="https://drive.google.com/file/d/1KgpnvPBwSzS75rAcTzDo8MIunPc9RVtM/preview" class="video-el" frameborder="0" allowfullscreen allow="autoplay" sandbox="allow-scripts allow-same-origin allow-presentation"></iframe>
          </div>
        </div>
      </div>

      <!-- Log -->
      <div class="log-wrap">
        <div class="log-header">
          <span class="log-header-icon">📋</span>
          <span>Log Output</span>
          <button class="log-clear" onclick="clearLog()">🗑 clear</button>
        </div>
        <div class="log-box" id="logBox"></div>
      </div>

      <!-- Footer -->
      <div class="footer">
        <span>🔐 kuni tool · v2.6</span>
        <a href="#" onclick="doLogout();return false;">🚪 logout</a>
      </div>
    </div>`;

  loadSavedConfig();
  updateLimitBar();
  initSocket();
}

function toggleConfig() {
  cfgOpen = !cfgOpen;
  document.getElementById('cfgBody').style.display = cfgOpen ? 'flex' : 'none';
  document.getElementById('cfgToggle').textContent = cfgOpen ? 'HIDE' : 'SHOW';
}
function togglePanel(id) { document.getElementById(id).classList.toggle('open'); }
function toggleTutorial() {
  tutOpen = !tutOpen;
  document.getElementById('tutBody').classList.toggle('open', tutOpen);
  document.getElementById('tutToggle').textContent = tutOpen ? 'HIDE' : 'SHOW';
}

function updateWebhookUI(hasWebhook) {
  webhookSet = hasWebhook;
  const wrap = document.getElementById('webhookWrap');
  const warn = document.getElementById('webhookWarn');
  const mark = document.getElementById('webhookReqMark');
  if (!wrap || !warn) return;
  if (hasWebhook) { wrap.classList.remove('required'); warn.classList.remove('show'); if (mark) mark.style.display='none'; }
  else { wrap.classList.add('required'); warn.classList.add('show'); if (mark) mark.style.display='inline'; }
}

function updateProxyStrip(count) {
  const strip = document.getElementById('proxyStrip');
  const txt = document.getElementById('proxyStripTxt');
  if (!strip || !txt) return;
  if (count > 0) {
    strip.classList.remove('empty');
    txt.textContent = count + ' proxies loaded — rotating per account';
  } else {
    strip.classList.add('empty');
    txt.textContent = 'no proxies loaded — using direct connection';
  }
}

async function loadSavedConfig() {
  try {
    const r = await authFetch('/get-proxies');
    const d = await r.json();
    if (d.ok) {
      const badge = document.getElementById('proxyBadge');
      badge.textContent = d.count > 0 ? d.count+' loaded' : 'none';
      badge.className = 'panel-badge'+(d.count>0?' ok':'');
      updateProxyStrip(d.count);
    }
  } catch {}
  try {
    const r = await authFetch('/get-webhook');
    const d = await r.json();
    if (d.ok) {
      updateWebhookUI(d.has_webhook);
      const st = document.getElementById('webhookSt');
      if (st) {
        if (d.has_webhook) { st.style.color='var(--green)'; st.textContent='✅ connected'; }
        else { st.style.color='var(--red)'; st.textContent='❌ not set'; }
      }
    }
  } catch {}
}

async function saveProxies() {
  const text = document.getElementById('proxyTA').value;
  const st = document.getElementById('proxySt');
  st.style.color='var(--text2)'; st.textContent='⏳ saving...';
  try {
    const r = await authFetch('/set-proxies',{method:'POST',body:JSON.stringify({proxies:text})});
    const d = await r.json();
    if (d.ok) {
      st.style.color='var(--green)'; st.textContent='✅ '+d.count+' proxies saved';
      document.getElementById('proxyTA').value='';
      const b = document.getElementById('proxyBadge');
      b.textContent=d.count+' loaded'; b.className='panel-badge'+(d.count>0?' ok':'');
      updateProxyStrip(d.count);
      setTimeout(()=>togglePanel('proxyPanel'), 900);
    } else { st.style.color='var(--red)'; st.textContent='❌ '+(d.error||'error'); }
  } catch { st.style.color='var(--red)'; st.textContent='❌ request failed'; }
}

async function saveWebhook() {
  const wh = document.getElementById('webhookInput').value.trim();
  const st = document.getElementById('webhookSt');
  st.style.color='var(--text2)'; st.textContent = wh?'⏳ testing...':'⏳ clearing...';
  try {
    const r = await authFetch('/set-webhook',{method:'POST',body:JSON.stringify({webhook:wh})});
    const d = await r.json();
    if (d.ok) {
      if (wh) { st.style.color='var(--green)'; st.textContent = d.tested?'✅ verified — test sent':'✅ saved'; updateWebhookUI(true); }
      else { st.style.color='var(--gold)'; st.textContent='🗑 cleared'; updateWebhookUI(false); }
    } else {
      st.style.color='var(--red)';
      st.textContent = d.error==='invalid_webhook'?'❌ invalid discord url':
                       d.error==='webhook_unreachable'?'❌ test failed — check url':
                       d.error==='not_authenticated'?'❌ session expired — refresh':
                       ('❌ '+(d.error||'error'));
    }
  } catch { st.style.color='var(--red)'; st.textContent='❌ request failed'; }
}

function updateLimitBar() {
  if (!licenseInfo || licenseInfo.limit >= 9999) return;
  const used = licenseInfo.limit - (licenseInfo.accounts_left || 0);
  const limit = licenseInfo.limit;
  const pct = Math.min(100, Math.round(used/limit*100));
  const fill = document.getElementById('limitBar');
  if (fill) { fill.style.width=pct+'%'; fill.className='limit-bar-fill'+(pct>=90?' danger':pct>=70?' warn':''); }
  const txt = document.getElementById('limitText');
  if (txt) txt.textContent = used + ' / ' + limit + ' (' + (100-pct) + '% left)';
}

function showLimitReached(used, limit, reason) {
  const banner = document.getElementById('limitBanner');
  if (banner) {
    banner.classList.add('show');
    banner.innerHTML = '<span>🚫</span><span>'+(reason==='revoked'?'License revoked — contact Kuni':reason==='expired'?'License expired — contact Kuni':'Account limit reached — upgrade to continue.')+'</span>';
  }
  const btn = document.getElementById('mainBtn');
  if (btn) { btn.className='run-btn disabled-btn'; btn.innerHTML='<span>🔒</span> Unavailable'; }
  setStatus('limit', '🚫 '+(reason||'limit reached')+' — '+used+'/'+limit);
}

function setStatus(mode, text) {
  const bar = document.getElementById('statusBar');
  const ico = document.getElementById('statusIcon');
  if (bar) { bar.className='status-bar '+mode; document.getElementById('statusText').textContent=text; }
  if (ico) {
    const iconMap = { idle:'⬛', running:'🟡', done:'🟢', stopped:'🔴', limit:'🔴' };
    ico.textContent = iconMap[mode] || '⬛';
  }
}

function clearLog() { const b=document.getElementById('logBox'); if(b) b.innerHTML=''; }

async function doLogout() {
  try { if (sessionToken) await fetch('/logout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_token:sessionToken})}); } catch {}
  localStorage.removeItem('license'); localStorage.removeItem('session_token');
  sessionToken = null;
  location.reload();
}

function initSocket() {
  socket = io({ auth: { token: sessionToken } });

  socket.on('auth_failed', () => {
    localStorage.removeItem('license'); localStorage.removeItem('session_token');
    sessionToken = null;
    alert('Session expired — please log in again.');
    location.reload();
  });

  window.toggle = function() {
    if (running) { socket.emit('stop'); return; }
    if (!webhookSet) {
      setStatus('stopped', '⚠️ webhook required — set it first');
      const warn = document.getElementById('webhookWarn');
      if (warn) { warn.classList.add('show'); warn.scrollIntoView({behavior:'smooth',block:'center'}); }
      cfgOpen = true;
      document.getElementById('cfgBody').style.display='flex';
      document.getElementById('cfgToggle').textContent='HIDE';
      const inp = document.getElementById('webhookInput');
      if (inp) inp.focus();
      return;
    }
    const count=parseInt(document.getElementById('count').value)||10;
    const concurrent=parseInt(document.getElementById('concurrent').value)||10;
    socket.emit('start',{count,concurrent});
  };

  socket.on('started', d => {
    running = true;
    const btn = document.getElementById('mainBtn');
    btn.className='run-btn stop'; btn.innerHTML='<span>⏹</span> Stop Generator';
    setStatus('running','⚡ running — generating '+d.count+' accounts');
  });

  socket.on('start_blocked', d => {
    running = false;
    setStatus('stopped', '🚫 '+(d.message||'blocked'));
    if (d.reason==='webhook_required') {
      updateWebhookUI(false);
      const warn = document.getElementById('webhookWarn');
      if (warn) warn.scrollIntoView({behavior:'smooth',block:'center'});
    }
  });

  socket.on('stopped', () => {
    running = false;
    const btn = document.getElementById('mainBtn');
    btn.className='run-btn idle'; btn.innerHTML='<span>🚀</span> Run Generator';
    setStatus('stopped','⏹ stopped by user');
  });

  socket.on('done', d => {
    running = false;
    const btn = document.getElementById('mainBtn');
    btn.className='run-btn idle'; btn.innerHTML='<span>🚀</span> Run Generator';
    setStatus('done','✅ done — '+d.created+'/'+d.total+' accounts created');
  });

  socket.on('stats', d => {
    document.getElementById('s-created').textContent=d.created;
    document.getElementById('s-active').textContent=d.active;
    document.getElementById('s-failed').textContent=d.failed;
    document.getElementById('s-target').textContent=d.target;
    if (licenseInfo && licenseInfo.limit < 9999) {
      const used = (licenseInfo.used||0) + d.created;
      const pct  = Math.min(100, Math.round(used/licenseInfo.limit*100));
      const fill = document.getElementById('limitBar');
      if (fill) { fill.style.width=pct+'%'; fill.className='limit-bar-fill'+(pct>=90?' danger':pct>=70?' warn':''); }
      const txt = document.getElementById('limitText');
      if (txt) txt.textContent = used + ' / ' + licenseInfo.limit + ' (' + Math.max(0,100-pct) + '% left)';
    }
  });

  socket.on('log', d => {
    const box=document.getElementById('logBox');
    if (!box) return;
    const line=document.createElement('div');
    const tag = {ok:'✅',err:'❌',dim:'·',inf:'ℹ'}[d.tag||'dim'] || '·';
    line.className='log-line '+(d.tag||'dim');
    const msg=d.msg||'';
    const m=msg.match(/^\[(\d{2}:\d{2}:\d{2})\]\s*(.*)/s);
    if (m) line.innerHTML=`<span class="log-ts">${m[1]}</span><span class="log-tag">${tag}</span><span class="log-msg">${m[2]}</span>`;
    else   line.innerHTML=`<span class="log-tag">${tag}</span><span class="log-msg">${msg}</span>`;
    box.appendChild(line); box.scrollTop=box.scrollHeight;
  });

  socket.on('limit_reached', d => {
    running = false;
    showLimitReached(d.used||0, d.limit||0, d.reason);
  });
}

/* ─── AUTO-LOGIN ─── */
const savedKey = localStorage.getItem('license');
const savedToken = localStorage.getItem('session_token');
if (savedKey && savedToken) {
  (async () => {
    const [hwid, fp] = await Promise.all([getDeviceFingerprint(), getExtraFp()]);
    const ls_token = getLsToken();
    try {
      const r = await fetch('/verify-key',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:savedKey,hwid,ls_token,fp})});
      const d = await r.json();
      if (d.valid) {
        sessionToken = d.session_token;
        localStorage.setItem('session_token', sessionToken);
        licenseInfo = d;
        showMainApp();
      } else {
        localStorage.removeItem('license'); localStorage.removeItem('session_token');
        showLicenseScreen();
      }
    } catch { showLicenseScreen(); }
  })();
} else {
  showLicenseScreen();
}
</script>
</body>
</html>
"""
