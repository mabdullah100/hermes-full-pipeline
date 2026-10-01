"""
Hermes Content Pipeline - Stage 6: Publishing & Delivery Engine
Publishes approved items to structured Markdown archives, daily HTML digests, and webhooks (Telegram/Discord).
"""

import os
import json
import logging
import urllib.request
from datetime import datetime, timezone
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HermesPublisher")


class ContentPublisher:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pub_cfg = config.get("publishing", {})
        self.output_dir = self.pub_cfg.get("output_directory", "output/published")
        os.makedirs(self.output_dir, exist_ok=True)

    def publish_file(self, queue_item: Dict[str, Any]) -> str:
        """Copy and finalize approved item into published archive."""
        source_path = queue_item.get("filepath", "")
        item_id = queue_item.get("id", "item")
        dest_path = os.path.join(self.output_dir, f"{item_id}.md")

        if os.path.exists(source_path):
            with open(source_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Update status to published
            content = content.replace('status: "approved"', 'status: "published"')
            content = content.replace('status: "pending_review"', 'status: "published"')
            content = content.replace('**Status**: `approved`', '**Status**: `published`')
            content += f"\n\n*Published at: {datetime.now(timezone.utc).isoformat()}*\n"

            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Published to archive: {dest_path}")
            return dest_path
        return ""

    def generate_digest(self, published_items: List[Dict[str, Any]]) -> str:
        """Create a unified daily briefing markdown document aggregating all published items."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        digest_path = os.path.join(self.output_dir, f"daily_digest_{today}.md")

        md = [
            f"# ☤ Hermes Daily Intelligence Digest — {today}",
            f"**Curated automatically by Hermes Content Pipeline (Nous Research)**\n",
            f"Total qualified stories: {len(published_items)}\n",
            "---"
        ]

        for idx, it in enumerate(published_items, start=1):
            title = it.get("title", "Untitled")
            source = it.get("source", "Unknown")
            url = it.get("url", "#")
            score = it.get("materiality_score", "N/A")
            md.append(f"\n### {idx}. [{title}]({url})")
            md.append(f"**Source:** {source} | **Materiality Score:** `{score}/10`\n")

            # Read summary if available
            path = it.get("filepath")
            if path and os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                if "## 📌 Executive Brief" in text:
                    brief = text.split("## 📌 Executive Brief")[1].split("---")[0].strip()
                    md.append(f"> {brief}\n")

        full_digest = "\n".join(md)
        with open(digest_path, "w", encoding="utf-8") as f:
            f.write(full_digest)

        logger.info(f"Daily digest created: {digest_path}")
        return digest_path

    def send_telegram(self, text: str) -> bool:
        """Send message via Telegram bot if credentials are configured."""
        tg_cfg = self.pub_cfg.get("telegram", {})
        if not tg_cfg.get("enabled", False):
            return False

        token = os.environ.get(tg_cfg.get("bot_token_env", "TELEGRAM_BOT_TOKEN"), "")
        chat_id = os.environ.get(tg_cfg.get("chat_id_env", "TELEGRAM_CHAT_ID"), "")

        if not token or not chat_id:
            logger.debug("Telegram credentials not set; skipping webhook.")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Failed to post to Telegram: {e}")
            return False

    def publish_approved(self, approved_items: List[Dict[str, Any]]) -> List[str]:
        """Publish all approved items."""
        published_paths = []
        for it in approved_items:
            path = self.publish_file(it)
            if path:
                published_paths.append(path)

        if published_items := approved_items:
            if self.pub_cfg.get("generate_daily_digest", True):
                self.generate_digest(published_items)

        logger.info(f"Publishing complete: {len(published_paths)} items published.")
        return published_paths


if __name__ == "__main__":
    with open("config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)
    pub = ContentPublisher(cfg)
    mock_items = [{
        "id": "mock_test_123",
        "title": "Hermes Agent Pipeline Launch",
        "source": "Nous Research",
        "url": "https://hermes-agent.nousresearch.com",
        "materiality_score": "9",
        "filepath": "queue/review/hermes_agent_autonomous_pipeli_f3565075.md"
    }]
    pub.publish_approved(mock_items)
