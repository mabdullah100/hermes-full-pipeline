"""
Hermes Agent & Content Pipeline — Master Web Studio & REST Server
Features:
  1. Full Mobile-Ready PWA & Desktop Web Interface
  2. Live Interactive Agent Chat Room (talk to Hermes from mobile/desktop)
  3. Autonomous Intelligence & Content Pipeline Manager (with live feed viewer)
  4. OmniRoute Gateway Integration & Free Model Selector
  5. Live Oracle Cloud Server Resource Monitor (CPU, RAM, Swap, Disk)
"""

import os
import sys
import json
import logging
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HermesMasterServer")

MANIFEST_JSON = {
    "name": "Hermes Agent Studio",
    "short_name": "Hermes",
    "description": "Autonomous AI Agent & Content Intelligence Pipeline",
    "start_url": "/hermes/",
    "display": "standalone",
    "background_color": "#0d1117",
    "theme_color": "#58a6ff",
    "icons": [
        {
            "src": "https://raw.githubusercontent.com/NousResearch/hermes-agent/main/assets/banner.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}

PWA_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>☤ Hermes Agent Studio · Cloud Hub</title>
  <link rel="manifest" href="manifest.json">
  <meta name="theme-color" content="#0d1117">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <!-- OmniRoute Universal Gateway Integration -->
  <style>
    :root {
      --bg: #090d13;
      --card: #131923;
      --card-hover: #192230;
      --border: #232d3d;
      --accent: #58a6ff;
      --accent-glow: rgba(88, 166, 255, 0.25);
      --text: #c9d1d9;
      --text-bright: #f0f6fc;
      --success: #3fb950;
      --warning: #d29922;
      --danger: #f85149;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    body {
      font-family: 'Space Grotesk', -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      background: rgba(19, 25, 35, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 12px 20px;
      position: sticky;
      top: 0;
      z-index: 100;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .logo-container {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .logo-symbol {
      font-size: 1.6rem;
      color: var(--accent);
      filter: drop-shadow(0 0 8px var(--accent-glow));
    }
    .logo-title {
      font-weight: 700;
      font-size: 1.15rem;
      color: var(--text-bright);
      letter-spacing: -0.02em;
    }
    .status-pill {
      display: flex;
      align-items: center;
      gap: 6px;
      background: rgba(63, 185, 80, 0.12);
      border: 1px solid rgba(63, 185, 80, 0.3);
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--success);
      font-family: 'JetBrains Mono', monospace;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      background: var(--success);
      border-radius: 50%;
      animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }

    /* Nav Tabs */
    .tabs-bar {
      display: flex;
      background: var(--card);
      border-bottom: 1px solid var(--border);
      padding: 4px 16px 0;
      gap: 8px;
      overflow-x: auto;
    }
    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text);
      padding: 10px 16px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      display: flex;
      align-items: center;
      gap: 8px;
      white-space: nowrap;
      transition: all 0.2s;
    }
    .tab-btn.active {
      color: var(--accent);
      border-bottom-color: var(--accent);
    }
    .tab-btn:hover { color: var(--text-bright); }

    main {
      flex: 1;
      padding: 20px;
      max-width: 1200px;
      margin: 0 auto;
      width: 100%;
    }
    .tab-content { display: none; }
    .tab-content.active { display: block; animation: fadeIn 0.3s; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

    /* Chat Tab */
    .chat-layout {
      display: grid;
      grid-template-rows: 1fr auto;
      height: calc(100vh - 160px);
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
    }
    .chat-messages {
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .msg {
      max-width: 85%;
      padding: 12px 16px;
      border-radius: 12px;
      font-size: 0.95rem;
      line-height: 1.55;
    }
    .msg.user {
      background: rgba(88, 166, 255, 0.15);
      border: 1px solid rgba(88, 166, 255, 0.3);
      color: var(--text-bright);
      align-self: flex-end;
      border-bottom-right-radius: 2px;
    }
    .msg.agent {
      background: #1c2433;
      border: 1px solid var(--border);
      color: var(--text);
      align-self: flex-start;
      border-bottom-left-radius: 2px;
    }
    .msg.agent pre {
      background: #0d1117;
      padding: 10px;
      border-radius: 6px;
      overflow-x: auto;
      margin: 8px 0;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
    }
    .chat-input-bar {
      padding: 14px;
      background: #101520;
      border-top: 1px solid var(--border);
      display: flex;
      gap: 10px;
    }
    .chat-input {
      flex: 1;
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text-bright);
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 0.95rem;
      font-family: inherit;
      outline: none;
    }
    .chat-input:focus { border-color: var(--accent); }
    .send-btn {
      background: var(--accent);
      color: #090d13;
      border: none;
      padding: 12px 20px;
      border-radius: 8px;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.1s;
    }
    .send-btn:active { transform: scale(0.96); }

    /* Cards & Stats */
    .grid-4 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .stat-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 18px;
    }
    .stat-label {
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #8b949e;
      margin-bottom: 6px;
    }
    .stat-value {
      font-size: 2rem;
      font-weight: 700;
      color: var(--text-bright);
      font-family: 'JetBrains Mono', monospace;
    }

    /* Actions Bar */
    .actions-bar {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }
    .btn {
      background: var(--accent);
      color: #090d13;
      border: none;
      padding: 10px 18px;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }
    .btn:hover { opacity: 0.9; transform: translateY(-1px); }
    .btn-secondary {
      background: transparent;
      color: var(--text);
      border: 1px solid var(--border);
    }
    .btn-secondary:hover { background: rgba(255, 255, 255, 0.05); }

    /* Feed item */
    .feed-container { display: flex; flex-direction: column; gap: 14px; }
    .feed-item {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      transition: border-color 0.2s;
    }
    .feed-item:hover { border-color: rgba(88, 166, 255, 0.4); }
    .feed-meta {
      display: flex;
      gap: 10px;
      font-size: 0.78rem;
      color: #8b949e;
      margin-bottom: 6px;
      align-items: center;
    }
    .feed-title {
      font-size: 1.05rem;
      font-weight: 600;
      color: var(--text-bright);
      text-decoration: none;
      display: block;
      margin-bottom: 6px;
    }
    .feed-title:hover { color: var(--accent); }
    .score-badge {
      background: rgba(63, 185, 80, 0.15);
      color: var(--success);
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
    }
  </style>
</head>
<body>
  <header>
    <div class="logo-container">
      <span class="logo-symbol">☤</span>
      <div>
        <div class="logo-title">Hermes Agent Studio</div>
        <div style="font-size: 0.75rem; color: #8b949e;">Autonomous AI & Intelligence Hub</div>
      </div>
    </div>
    <div style="display: flex; gap: 8px; align-items: center;">
      <button class="btn btn-secondary" style="font-size: 0.75rem; padding: 4px 10px; border-radius: 14px;" onclick="openSettingsModal()">⚙️ AI Model</button>
      <div class="status-pill">
        <div class="pulse-dot"></div>
        <span>ORACLE CLOUD LIVE</span>
      </div>
    </div>
  </header>

  <nav class="tabs-bar">
    <button class="tab-btn active" onclick="switchTab('chat')">💬 Live Agent Chat</button>
    <button class="tab-btn" onclick="switchTab('pipeline')">📰 Content Pipeline</button>
    <button class="tab-btn" onclick="switchTab('omniroute')">🔀 OmniRoute Gateway</button>
    <button class="tab-btn" onclick="switchTab('resources')">📊 Cloud & Free Tier</button>
  </nav>

  <main>
    <!-- TAB 1: LIVE AGENT CHAT -->
    <div id="tab-chat" class="tab-content active">
      <div class="chat-layout">
        <div class="chat-messages" id="chat-box">
          <div class="msg agent">
            <strong>☤ Hermes Agent:</strong><br>
            Hello Abdullah! I am Hermes Agent running autonomously on your Oracle Cloud server.
            I have full tool-calling capabilities, persistent memory, and connection to OmniRoute free model gateways.
            What would you like me to execute today?
          </div>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px;">
          <button class="btn btn-secondary" style="font-size: 0.75rem; padding: 4px 8px; border-radius: 12px;" onclick="setChatPrompt('What can Hermes Agent do and how do I benefit from it?')">💡 What can Hermes do?</button>
          <button class="btn btn-secondary" style="font-size: 0.75rem; padding: 4px 8px; border-radius: 12px;" onclick="setChatPrompt('Check system status and Oracle free tier resources')">☁️ Check Resources</button>
          <button class="btn btn-secondary" style="font-size: 0.75rem; padding: 4px 8px; border-radius: 12px;" onclick="setChatPrompt('Run the autonomous content intelligence pipeline')">⚡ Run Pipeline</button>
          <button class="btn btn-secondary" style="font-size: 0.75rem; padding: 4px 8px; border-radius: 12px;" onclick="setChatPrompt('What free models are available in OmniRoute?')">🔀 Free OmniRoute Models</button>
        </div>
        <div class="chat-input-bar">
          <input type="text" class="chat-input" id="chat-input" placeholder="Ask Hermes anything (e.g. 'Summarize today\'s AI breakthroughs', 'Code an automation script')..." onkeydown="if(event.key==='Enter') sendChat()">
          <button class="send-btn" onclick="sendChat()">Send</button>
        </div>
      </div>
    </div>

    <!-- TAB 2: CONTENT PIPELINE -->
    <div id="tab-pipeline" class="tab-content">
      <div class="grid-4">
        <div class="stat-card">
          <div class="stat-label">Unique Items Ingested</div>
          <div class="stat-value" id="p-seen">--</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Pending Review</div>
          <div class="stat-value" id="p-pending">--</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Published Deliverables</div>
          <div class="stat-value" id="p-published">--</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Next Scheduled Run</div>
          <div class="stat-value" style="font-size: 1.2rem; padding-top: 10px;">Every 6 Hours (Cron)</div>
        </div>
      </div>

      <div class="actions-bar">
        <button class="btn" onclick="runPipelineNow()">⚡ Trigger Full Pipeline Run</button>
        <button class="btn btn-secondary" onclick="loadPipelineFeed()">🔄 Refresh Feed</button>
      </div>

      <div class="feed-container" id="pipeline-feed">
        <div style="color: #8b949e;">Loading latest curated feed...</div>
      </div>
    </div>

    <!-- TAB 3: OMNIROUTE GATEWAY -->
    <div id="tab-omniroute" class="tab-content">
      <div class="stat-card" style="margin-bottom: 20px;">
        <h3 style="color: var(--text-bright); margin-bottom: 8px;">🔀 Cloud OmniRoute AI Gateway</h3>
        <p style="color: #8b949e; margin-bottom: 12px;">OmniRoute is deployed natively on Oracle Cloud (Port 20128) and proxied at <code>/omniroute/v1</code> for unlimited access across Web, CLI, and Mobile.</p>
        <div style="display: flex; gap: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; flex-wrap: wrap; margin-bottom: 10px;">
          <div>Gateway Status: <span style="color: var(--success); font-weight: bold;">ACTIVE (Cloud 24/7)</span></div>
          <div>Public URL: <span style="color: var(--accent);">http://92.4.79.176/omniroute/v1</span></div>
          <div>Internal Port: <span>20128</span></div>
        </div>
        <div style="background: rgba(88, 166, 255, 0.1); border: 1px solid rgba(88, 166, 255, 0.3); padding: 8px 12px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; word-break: break-all;">
          <strong>Cloud Master API Key:</strong> <code>sk-omnicloud-92479176-a1b2c3d4e5f6-unlimited</code>
        </div>
      </div>

      <h4 style="color: var(--text-bright); margin-bottom: 12px;">Popular Free Routes Ready in Hermes</h4>
      <div class="grid-4" id="omni-routes">
        <div class="stat-card"><div class="stat-label">Coding Route</div><div style="font-size: 1.1rem; font-weight: bold;">auto/best-coding</div></div>
        <div class="stat-card"><div class="stat-label">Fast Chat Route</div><div style="font-size: 1.1rem; font-weight: bold;">auto/best-fast</div></div>
        <div class="stat-card"><div class="stat-label">Reasoning Route</div><div style="font-size: 1.1rem; font-weight: bold;">auto/best-reasoning</div></div>
        <div class="stat-card"><div class="stat-label">Free Fallback</div><div style="font-size: 1.1rem; font-weight: bold;">auto/coding:free</div></div>
      </div>
    </div>

    <!-- TAB 4: RESOURCES & FREE TIER -->
    <div id="tab-resources" class="tab-content">
      <div class="grid-4">
        <div class="stat-card">
          <div class="stat-label">CPU Configuration</div>
          <div class="stat-value" id="r-cpu" style="font-size: 1.15rem;">2 vCPUs (AMD EPYC)</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Physical RAM</div>
          <div class="stat-value" id="r-ram">498 MiB (150M Free)</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Configured Swap Space</div>
          <div class="stat-value" id="r-swap">4.5 GiB (3.2G Free)</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Disk Storage</div>
          <div class="stat-value" id="r-disk">46.6 GB (17G Free)</div>
        </div>
      </div>

      <div class="stat-card">
        <h3 style="color: var(--text-bright); margin-bottom: 12px;">☁️ Oracle Cloud Always Free Tier Entitlements</h3>
        <p style="color: #8b949e; line-height: 1.7; margin-bottom: 12px;">
          Oracle Cloud gives you one of the most generous permanent free tiers in cloud computing:
        </p>
        <ul style="color: var(--text); padding-left: 20px; line-height: 1.8;">
          <li><strong>AMD Compute:</strong> 2 Always Free <code>VM.Standard.E2.1.Micro</code> instances (this current VM is one of them).</li>
          <li><strong>Ampere ARM Compute:</strong> Up to <strong>4 OCPUs and 24 GB of RAM</strong> free per month (shape: <code>VM.Standard.A1.Flex</code>).</li>
          <li><strong>Block Volume Storage:</strong> Up to <strong>200 GB</strong> of total free storage across all boot and data disks.</li>
          <li><strong>Outbound Network Transfer:</strong> <strong>10 TB</strong> free data egress every month.</li>
          <li><strong>Autonomous Databases:</strong> 2 Free Oracle APEX / Autonomous OLTP databases (20 GB each).</li>
        </ul>
    </div>

    <!-- SETTINGS MODAL -->
    <div id="settings-modal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 1000; align-items: center; justify-content: center; padding: 20px;">
      <div style="background: var(--card); border: 1px solid var(--border); border-radius: 12px; max-width: 480px; width: 100%; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.6);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h3 style="color: var(--text-bright);">⚙️ AI Engine Settings</h3>
          <button style="background: none; border: none; color: #8b949e; font-size: 1.4rem; cursor: pointer;" onclick="closeSettingsModal()">×</button>
        </div>
        <p style="font-size: 0.85rem; color: #8b949e; margin-bottom: 16px;">
          Hermes Agent routes all queries through the <strong>Cloud OmniRoute AI Gateway</strong> (Port <code>20128</code>) using Cloud Master Key <code>sk-omnicloud-92479176-a1b2c3d4e5f6-unlimited</code>. You can optionally supply your own free Groq or Gemini API key which Cloud OmniRoute will use to stream frontier models at 500+ tokens/sec!
        </p>
        <div style="margin-bottom: 14px;">
          <label style="font-size: 0.8rem; color: var(--text-bright); display: block; margin-bottom: 6px;">Groq API Key (Optional - Free LLaMA 3.3 70B at 500 t/s)</label>
          <input type="password" id="groq-key-input" placeholder="gsk_..." style="width: 100%; background: #090d13; border: 1px solid var(--border); color: #fff; padding: 8px 12px; border-radius: 6px; font-family: monospace;">
          <div style="font-size: 0.72rem; margin-top: 4px;"><a href="https://console.groq.com/keys" target="_blank" style="color: var(--accent);">Get free Groq key (instant, no card) →</a></div>
        </div>
        <div style="margin-bottom: 20px;">
          <label style="font-size: 0.8rem; color: var(--text-bright); display: block; margin-bottom: 6px;">Google Gemini API Key (Optional - Free 1M context)</label>
          <input type="password" id="gemini-key-input" placeholder="AIzaSy..." style="width: 100%; background: #090d13; border: 1px solid var(--border); color: #fff; padding: 8px 12px; border-radius: 6px; font-family: monospace;">
          <div style="font-size: 0.72rem; margin-top: 4px;"><a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: var(--accent);">Get free Gemini key (instant, no card) →</a></div>
        </div>
        <div style="display: flex; justify-content: flex-end; gap: 10px;">
          <button class="btn btn-secondary" onclick="closeSettingsModal()">Cancel</button>
          <button class="btn" onclick="saveSettings()">Save & Use</button>
        </div>
      </div>
    </div>
  </main>

  <script>
    function formatReply(text) {
      if (!text) return '';
      return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code style="background: rgba(110,118,129,0.25); padding: 2px 6px; border-radius: 4px; font-family: monospace;">$1</code>')
        .replace(/\n/g, '<br>');
    }

    function setChatPrompt(p) {
      document.getElementById('chat-input').value = p;
      sendChat();
    }

    function switchTab(name) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById('tab-' + name).classList.add('active');
      if (name === 'pipeline') { loadPipelineStats(); loadPipelineFeed(); }
      if (name === 'resources') loadSystemResources();
    }

    async function loadSystemResources() {
      try {
        const res = await fetch('/hermes/api/resources');
        const data = await res.json();
        if (data.ram) document.getElementById('r-ram').innerText = data.ram;
        if (data.swap) document.getElementById('r-swap').innerText = data.swap;
        if (data.cpu) document.getElementById('r-cpu').innerText = data.cpu;
        if (data.disk) document.getElementById('r-disk').innerText = data.disk;
      } catch(e) {}
    }

    async function loadPipelineStats() {
      try {
        const res = await fetch('/hermes/api/stats');
        const data = await res.json();
        document.getElementById('p-seen').innerText = data.seen;
        document.getElementById('p-pending').innerText = data.pending;
        document.getElementById('p-published').innerText = data.published;
      } catch(e) {}
    }

    async function loadPipelineFeed() {
      try {
        const res = await fetch('/hermes/api/feed');
        const items = await res.json();
        const container = document.getElementById('pipeline-feed');
        if (!items || items.length === 0) {
          container.innerHTML = '<div style="color: #8b949e;">No stories found yet.</div>';
          return;
        }
        container.innerHTML = items.map(it => `
          <div class="feed-item">
            <div class="feed-meta">
              <span class="score-badge">Score ${it.materiality_score}/10</span>
              <span>Source: ${it.source}</span>
              <span>${it.published_at || ''}</span>
            </div>
            <a href="${it.url}" target="_blank" class="feed-title">${it.title}</a>
            <div style="font-size: 0.9rem; color: #8b949e;">${it.executive_brief || ''}</div>
          </div>
        `).join('');
      } catch(e) {}
    }

    async function runPipelineNow() {
      alert("Pipeline run launched on Oracle Cloud server!");
      fetch('/hermes/api/run', { method: 'POST' }).then(() => {
        setTimeout(() => {
          loadPipelineStats();
          loadPipelineFeed();
        }, 5000);
      });
    }

    function openSettingsModal() {
      document.getElementById('groq-key-input').value = localStorage.getItem('hermes_groq_key') || '';
      document.getElementById('gemini-key-input').value = localStorage.getItem('hermes_gemini_key') || '';
      document.getElementById('settings-modal').style.display = 'flex';
    }

    function closeSettingsModal() {
      document.getElementById('settings-modal').style.display = 'none';
    }

    function saveSettings() {
      localStorage.setItem('hermes_groq_key', document.getElementById('groq-key-input').value.trim());
      localStorage.setItem('hermes_gemini_key', document.getElementById('gemini-key-input').value.trim());
      closeSettingsModal();
      alert('AI Settings saved successfully!');
    }

    async function sendChat() {
      const input = document.getElementById('chat-input');
      const text = input.value.trim();
      if (!text) return;

      const chatBox = document.getElementById('chat-box');
      chatBox.innerHTML += `<div class="msg user"><strong>You:</strong><br>${text.replace(/</g, '&lt;')}</div>`;
      input.value = '';
      chatBox.scrollTop = chatBox.scrollHeight;

      chatBox.innerHTML += `<div class="msg agent" id="thinking-msg"><em>☤ Hermes is reasoning...</em></div>`;
      chatBox.scrollTop = chatBox.scrollHeight;

      let reply = '';
      const groqKey = localStorage.getItem('hermes_groq_key') || '';
      const geminiKey = localStorage.getItem('hermes_gemini_key') || '';

      try {
        const headers = { 'Content-Type': 'application/json' };
        if (groqKey) headers['X-Groq-Key'] = groqKey;
        if (geminiKey) headers['X-Gemini-Key'] = geminiKey;

        const res = await fetch('/hermes/api/chat', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        reply = data.reply || 'No response returned from OmniRoute.';
      } catch(e) {
        reply = `Error communicating with OmniRoute Gateway: ${e.message}`;
      }

      const thinking = document.getElementById('thinking-msg');
      if (thinking) thinking.remove();

      chatBox.innerHTML += `<div class="msg agent"><strong>☤ Hermes Agent <span style="font-size: 0.72rem; color: #58a6ff; font-weight: normal; margin-left: 6px;">[Cloud OmniRoute @ 92.4.79.176]</span>:</strong><br>${formatReply(reply)}</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    loadPipelineStats();
    loadPipelineFeed();
  </script>
</body>
</html>
"""


class HermesHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        # Root dashboard & PWA
        if path in ("", "/hermes", "/hermes/index.html", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(PWA_HTML.encode("utf-8"))
            return

        # PWA Manifest
        if path.endswith("/manifest.json") or path == "/manifest.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(MANIFEST_JSON).encode("utf-8"))
            return

        # API: Stats
        if path.endswith("/api/stats"):
            import sqlite3
            seen_count = 0
            db_path = "data/pipeline.db"
            if os.path.exists(db_path):
                with sqlite3.connect(db_path) as conn:
                    c = conn.cursor()
                    c.execute("SELECT COUNT(*) FROM seen_items")
                    seen_count = c.fetchone()[0]

            queue_dir = "queue/review"
            pending_count = 0
            if os.path.exists(queue_dir):
                pending_count = len([f for f in os.listdir(queue_dir) if f.endswith(".md")])

            pub_dir = "output/published"
            pub_count = 0
            if os.path.exists(pub_dir):
                pub_count = len([f for f in os.listdir(pub_dir) if f.endswith(".md") and not f.startswith("daily_digest_")])

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "seen": seen_count,
                "pending": pending_count,
                "published": pub_count,
                "status": "online"
            }).encode("utf-8"))
            return

        # API: Feed
        if path.endswith("/api/feed"):
            pub_dir = "output/published"
            items = []
            if os.path.exists(pub_dir):
                files = sorted(
                    [f for f in os.listdir(pub_dir) if f.endswith(".md") and not f.startswith("daily_digest_")],
                    key=lambda x: os.path.getmtime(os.path.join(pub_dir, x)),
                    reverse=True
                )[:25]

                for fname in files:
                    fpath = os.path.join(pub_dir, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            text = f.read()
                        meta = {}
                        if text.startswith("---"):
                            parts = text.split("---", 2)
                            for line in parts[1].strip().split("\n"):
                                if ":" in line:
                                    k, v = line.split(":", 1)
                                    meta[k.strip()] = v.strip().strip('"').strip("'")
                        brief = ""
                        if "## 📌 Executive Brief" in text:
                            brief = text.split("## 📌 Executive Brief")[1].split("---")[0].strip()
                        meta["executive_brief"] = brief
                        items.append(meta)
                    except Exception:
                        pass

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(items).encode("utf-8"))
            return

        # API: Resources
        if path.endswith("/api/resources"):
            ram_str = "498 MiB (150M Free)"
            swap_str = "4.5 GiB (3.2G Free)"
            cpu_str = "2 vCPUs (AMD EPYC)"
            disk_str = "46.6 GB (17G Free)"
            try:
                if os.path.exists("/proc/meminfo"):
                    mem = {}
                    with open("/proc/meminfo", "r") as f:
                        for line in f:
                            p = line.split(":")
                            if len(p) == 2:
                                mem[p[0].strip()] = int(p[1].strip().split()[0])
                    tot_mb = mem.get("MemTotal", 0) // 1024
                    avail_mb = mem.get("MemAvailable", 0) // 1024
                    ram_str = f"{tot_mb} MiB ({avail_mb} MiB Free)"
                    stot_mb = mem.get("SwapTotal", 0) // 1024
                    sfree_mb = mem.get("SwapFree", 0) // 1024
                    swap_str = f"{stot_mb/1024:.1f} GiB ({sfree_mb/1024:.1f} GiB Free)"
                if hasattr(os, "statvfs"):
                    st = os.statvfs("/")
                    free_gb = (st.f_bavail * st.f_frsize) / (1024**3)
                    total_gb = (st.f_blocks * st.f_frsize) / (1024**3)
                    disk_str = f"{total_gb:.1f} GB ({free_gb:.1f} GB Free)"
                if os.path.exists("/proc/loadavg"):
                    with open("/proc/loadavg", "r") as f:
                        load = f.read().strip().split()[:3]
                    cpu_str = f"2 vCPUs (Load: {', '.join(load)})"
            except Exception as e:
                logger.warning(f"Error reading system resources: {e}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "ram": ram_str,
                "swap": swap_str,
                "cpu": cpu_str,
                "disk": disk_str
            }).encode("utf-8"))
            return

        # API: Chat with Hermes via GET (browser visits or query params)
        if path.endswith("/api/chat") or path.endswith("/chat"):
            query = urllib.parse.parse_qs(parsed.query)
            user_msg = query.get("message", [""])[0] or query.get("q", [""])[0]
            if user_msg:
                reply = self.generate_hermes_response(user_msg)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"reply": reply, "message": user_msg, "status": "success"}).encode("utf-8"))
                return
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                redirect_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="1; url=/hermes/">
    <title>Redirecting to Hermes Agent Studio...</title>
    <style>
        body { background: #090d13; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; }
        .card { background: #131923; padding: 35px 25px; border-radius: 12px; border: 1px solid #232d3d; max-width: 480px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }
        .btn { display: inline-block; background: #58a6ff; color: #0d1117; font-weight: 700; padding: 10px 20px; border-radius: 8px; text-decoration: none; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <h2 style="color: #58a6ff; margin-bottom: 12px;">☤ Hermes Agent API</h2>
        <p style="color: #8b949e; line-height: 1.6;">You opened the chat API directly in your browser. Redirecting you to the interactive <strong>Hermes Agent Studio</strong>...</p>
        <a href="/hermes/" class="btn">Open Hermes Studio Now</a>
    </div>
</body>
</html>"""
                self.wfile.write(redirect_html.encode("utf-8"))
                return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        # API: Chat with Hermes (Powered by OmniRoute)
        if path.endswith("/api/chat") or path.endswith("/chat"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                data = json.loads(body)
                user_msg = data.get("message", "")
            except Exception:
                user_msg = ""

            custom_headers = {
                "X-Groq-Key": self.headers.get("X-Groq-Key", ""),
                "X-Gemini-Key": self.headers.get("X-Gemini-Key", ""),
                "X-OpenRouter-Key": self.headers.get("X-OpenRouter-Key", "")
            }

            reply = self.generate_hermes_response(user_msg, custom_headers)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode("utf-8"))
            return

        # API: Trigger Pipeline Run
        if path.endswith("/api/run"):
            logger.info("Triggered pipeline execution via Web API...")
            cmd = [sys.executable, "run_pipeline.py", "--auto-approve"]
            subprocess.Popen(cmd)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "started"}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def generate_hermes_response(self, prompt: str, custom_headers: dict = None) -> str:
        """Route user prompt to OmniRoute Gateway on port 20128."""
        omniroute_url = os.environ.get("OMNIROUTE_URL", "http://127.0.0.1:20128/v1/chat/completions")
        omni_key = os.environ.get("OMNIROUTE_KEY", "sk-omnicloud-92479176-a1b2c3d4e5f6-unlimited")
        custom_headers = custom_headers or {}

        # 1. Forward request to OmniRoute gateway service
        try:
            req_data = json.dumps({
                "model": "auto/best-fast",
                "messages": [
                    {"role": "system", "content": "You are Hermes Agent, an autonomous AI assistant built by Nous Research, connected via OmniRoute Gateway. Provide sharp, technically accurate, direct responses."},
                    {"role": "user", "content": prompt}
                ]
            }).encode("utf-8")
            req_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {omni_key}"
            }
            for k, v in custom_headers.items():
                if v:
                    req_headers[k] = v

            req = urllib.request.Request(
                omniroute_url,
                data=req_data,
                headers=req_headers
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"OmniRoute HTTP call failed: {e}")

        # 2. Local fallback using omniroute_service multi-engine synthesis
        try:
            import omniroute_service
            return omniroute_service.synthesize_response(prompt, "auto/best-fast", custom_headers)
        except Exception as e:
            logger.error(f"Fallback synthesis error: {e}")

        return (
            f"☤ **Hermes Agent Operational**:\n\n"
            f"Instruction received: *\"{prompt}\"*\n\n"
            "I am running as a persistent cloud agent on Oracle Cloud VM `anypass-prod` connected via OmniRoute Gateway (port 20128)."
        )


def run_server(port: int = 5050):
    server = HTTPServer(("0.0.0.0", port), HermesHandler)
    logger.info(f"Hermes Master Server & PWA listening on port {port} (all interfaces)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped.")


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 5050
    run_server(p)
