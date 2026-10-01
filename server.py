"""
Hermes Content Pipeline - Web Dashboard & REST API Server
A lightweight, zero-dependency HTTP server providing a modern Web UI
and REST API for monitoring, reviewing, and triggering the Hermes Pipeline.
Runs seamlessly on local machines and Oracle Cloud VPS behind Nginx.
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

from collector import collect_all
from deduplicator import Deduplicator
from ai_filter import AIFilter
from writer import ContentWriter
from review_queue import ReviewQueue
from publisher import ContentPublisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HermesServer")

HTML_DASHBOARD = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>☤ Hermes Autonomous Intelligence Pipeline</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --accent: #58a6ff;
      --text: #c9d1d9;
      --text-bright: #f0f6fc;
      --success: #3fb950;
      --warning: #d29922;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Space Grotesk', sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 20px;
      margin-bottom: 24px;
    }
    .logo {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .logo h1 {
      font-size: 1.5rem;
      color: var(--text-bright);
      font-weight: 700;
      letter-spacing: -0.02em;
    }
    .badge {
      background: rgba(56, 139, 253, 0.15);
      color: var(--accent);
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 600;
      border: 1px solid rgba(56, 139, 253, 0.3);
    }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
    }
    .card-title {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #8b949e;
      margin-bottom: 8px;
    }
    .card-val {
      font-size: 2.2rem;
      font-weight: 700;
      color: var(--text-bright);
      font-family: 'JetBrains Mono', monospace;
    }
    .btn {
      background: var(--accent);
      color: #0d1117;
      border: none;
      padding: 10px 18px;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn:hover { opacity: 0.9; transform: translateY(-1px); }
    .btn-outline {
      background: transparent;
      color: var(--accent);
      border: 1px solid var(--accent);
    }
    .btn-outline:hover { background: rgba(56, 139, 253, 0.1); }
    .actions { display: flex; gap: 12px; }
    .section-title {
      font-size: 1.2rem;
      color: var(--text-bright);
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .feed-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .feed-item {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
      transition: border-color 0.2s;
    }
    .feed-item:hover { border-color: #58a6ff55; }
    .item-meta {
      display: flex;
      gap: 12px;
      font-size: 0.8rem;
      color: #8b949e;
      margin-bottom: 6px;
    }
    .item-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--text-bright);
      margin-bottom: 8px;
      text-decoration: none;
      display: block;
    }
    .item-title:hover { color: var(--accent); }
    .item-desc {
      font-size: 0.92rem;
      color: #8b949e;
      line-height: 1.6;
    }
    .score-tag {
      background: rgba(63, 185, 80, 0.15);
      color: var(--success);
      padding: 2px 8px;
      border-radius: 6px;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
    }
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">
      <h1>☤ Hermes Content Pipeline</h1>
      <span class="badge">Nous Research · Live</span>
    </div>
    <div class="actions">
      <button class="btn" onclick="triggerRun()">⚡ Run Pipeline Now</button>
      <button class="btn btn-outline" onclick="location.reload()">🔄 Refresh</button>
    </div>
  </div>

  <div class="stats-grid">
    <div class="card">
      <div class="card-title">Unique Seen (DB)</div>
      <div class="card-val" id="stat-seen">--</div>
    </div>
    <div class="card">
      <div class="card-title">Pending Review</div>
      <div class="card-val" id="stat-pending">--</div>
    </div>
    <div class="card">
      <div class="card-title">Published Stories</div>
      <div class="card-val" id="stat-published">--</div>
    </div>
    <div class="card">
      <div class="card-title">Deployment</div>
      <div class="card-val" style="font-size: 1.4rem; padding-top: 10px;">Oracle Cloud</div>
    </div>
  </div>

  <div class="section-title">
    <span>📰 Latest Published Intelligence</span>
    <span style="font-size: 0.85rem; color: #8b949e;">Autonomously curated & deduplicated</span>
  </div>

  <div class="feed-container" id="feed">
    <div style="color: #8b949e;">Loading latest feed...</div>
  </div>

  <script>
    async function fetchStats() {
      try {
        const res = await fetch('api/stats');
        const data = await res.json();
        document.getElementById('stat-seen').innerText = data.seen;
        document.getElementById('stat-pending').innerText = data.pending;
        document.getElementById('stat-published').innerText = data.published;
      } catch (e) {
        console.error(e);
      }
    }

    async function fetchFeed() {
      try {
        const res = await fetch('api/feed');
        const items = await res.json();
        const container = document.getElementById('feed');
        if (!items || items.length === 0) {
          container.innerHTML = '<div style="color: #8b949e;">No published items found yet. Click Run Pipeline to curate!</div>';
          return;
        }
        container.innerHTML = items.map(it => `
          <div class="feed-item">
            <div class="item-meta">
              <span class="score-tag">Score ${it.materiality_score}/10</span>
              <span>Source: ${it.source}</span>
              <span>${it.published_at || ''}</span>
            </div>
            <a href="${it.url}" target="_blank" class="item-title">${it.title}</a>
            <div class="item-desc">${it.executive_brief || it.summary || ''}</div>
          </div>
        `).join('');
      } catch (e) {
        console.error(e);
      }
    }

    async function triggerRun() {
      alert("Launching autonomous pipeline execution in background...");
      fetch('api/run', { method: 'POST' }).then(() => {
        setTimeout(() => {
          fetchStats();
          fetchFeed();
        }, 5000);
      });
    }

    fetchStats();
    fetchFeed();
  </script>
</body>
</html>
"""


class HermesHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        # Root dashboard
        if path in ("", "/hermes", "/hermes/index.html", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode("utf-8"))
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
            self.end_headers()
            self.wfile.write(json.dumps(items).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path.endswith("/api/run"):
            import subprocess
            logger.info("Triggered pipeline execution via Web API...")
            cmd = [sys.executable, "run_pipeline.py", "--auto-approve"]
            subprocess.Popen(cmd)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "started"}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def run_server(port: int = 5050):
    server = HTTPServer(("0.0.0.0", port), HermesHandler)
    logger.info(f"Hermes Dashboard & API Server listening on port {port} (all interfaces)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped.")


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 5050
    run_server(p)
