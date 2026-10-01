"""
Hermes Content & Intelligence Pipeline — Main Orchestrator
Executes the full Hermes pipeline blueprint:
  Stage 1: Content Collection (RSS / Web / APIs)
  Stage 2: Deduplication (URL Hash & Semantic Token Matching)
  Stage 3: AI Filtering & Materiality Scoring
  Stage 4: AI Writing & Synthesis (Briefs, Takeaways, Social Posts)
  Stage 5: Review Queue Staging & Human Approval
  Stage 6: Publishing & Digest Generation (Markdown, HTML, Webhooks)

Usage:
  python run_pipeline.py                  # Run full pipeline with human review
  python run_pipeline.py --auto-approve   # Run autonomous pipeline (auto-publish)
  python run_pipeline.py --review         # Review pending items in terminal
  python run_pipeline.py --stats          # Show pipeline metrics and DB stats
"""

import os
import sys
import json
import argparse
import logging

from collector import collect_all
from deduplicator import Deduplicator
from ai_filter import AIFilter
from writer import ContentWriter
from review_queue import ReviewQueue
from publisher import ContentPublisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HermesPipeline")


def load_config(config_path: str = "config.json") -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def print_banner():
    banner = r"""
 =============================================================
     HERMES AUTONOMOUS CONTENT PIPELINE (Nous Research)
     Collection -> Deduplication -> AI Filter -> Writing -> Publish
 =============================================================
"""
    print(banner)


def run_pipeline(config: dict, auto_approve: bool = False):
    print_banner()
    logger.info("Starting Hermes content pipeline run...")

    # Stage 1: Collection
    logger.info("=== STAGE 1: Content Collection ===")
    sources = config.get("sources", [])
    raw_items = collect_all(sources)
    if not raw_items:
        logger.warning("No items collected from sources. Exiting pipeline.")
        return

    # Stage 2: Deduplication
    logger.info("=== STAGE 2: Deduplication ===")
    dedup = Deduplicator("data/pipeline.db")
    unique_items = dedup.deduplicate(raw_items)
    if not unique_items:
        logger.info("All collected items were already processed in previous runs. Nothing new.")
        return

    # Stage 3: AI Filtering & Materiality Scoring
    logger.info("=== STAGE 3: AI Filtering & Materiality Scoring ===")
    ai_filter = AIFilter(config)
    qualified_items = ai_filter.filter_items(unique_items)
    if not qualified_items:
        logger.info("No items met the materiality score threshold. Pipeline complete.")
        return

    # Stage 4: Writing & Deliverable Synthesis
    logger.info("=== STAGE 4: AI Writing & Synthesis ===")
    writer = ContentWriter(config)
    drafted_items = writer.write_all(qualified_items)

    # Stage 5: Review Queue Staging
    logger.info("=== STAGE 5: Staging to Review Queue ===")
    auto_app = auto_approve or config.get("review", {}).get("auto_approve", False)
    queue = ReviewQueue(
        queue_dir=config.get("review", {}).get("queue_directory", "queue/review"),
        auto_approve=auto_app
    )
    for it in drafted_items:
        queue.stage_item(it)

    # Stage 6: Publishing
    logger.info("=== STAGE 6: Publishing & Delivery ===")
    publisher = ContentPublisher(config)
    if auto_app:
        approved = queue.get_approved_items()
        published_paths = publisher.publish_approved(approved)
        logger.info(f"Autonomous publish finished: {len(published_paths)} articles published.")
    else:
        pending = [it for it in queue.list_queue() if it.get("status") == "pending_review"]
        logger.info(f"{len(pending)} items staged in 'queue/review/' awaiting review.")
        logger.info("Run 'python run_pipeline.py --review' to approve and publish.")


def review_interactive(config: dict):
    queue = ReviewQueue(queue_dir=config.get("review", {}).get("queue_directory", "queue/review"))
    publisher = ContentPublisher(config)

    items = queue.list_queue()
    pending = [it for it in items if it.get("status") == "pending_review"]

    if not pending:
        print("\n✅ No pending items in the review queue. All clear!\n")
        return

    print(f"\n📋 Found {len(pending)} items waiting for review:\n")
    for idx, it in enumerate(pending, start=1):
        print(f"[{idx}] {it.get('title')} ({it.get('source')})")
        print(f"    URL: {it.get('url')}")
        print(f"    Materiality: {it.get('materiality_score')}/10 | ID: {it.get('id')}\n")

    choice = input("Enter item number to approve (or 'all', 'publish-approved', 'q'): ").strip().lower()

    if choice == "q":
        return
    elif choice == "all":
        for it in pending:
            queue.set_status(it.get("id"), "approved")
        print("All pending items approved! Now publishing...")
        approved = queue.get_approved_items()
        publisher.publish_approved(approved)
    elif choice == "publish-approved":
        approved = queue.get_approved_items()
        publisher.publish_approved(approved)
    elif choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(pending):
            selected = pending[num - 1]
            act = input(f"Approve, Reject, or Cancel [a/r/c]: ").strip().lower()
            if act == "a":
                queue.set_status(selected.get("id"), "approved")
                print("Approved! Publishing...")
                publisher.publish_approved([selected])
            elif act == "r":
                queue.set_status(selected.get("id"), "rejected")
                print("Rejected.")


def show_stats(config: dict):
    import sqlite3
    db_path = "data/pipeline.db"
    seen_count = 0
    if os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM seen_items")
            seen_count = c.fetchone()[0]

    queue = ReviewQueue(queue_dir=config.get("review", {}).get("queue_directory", "queue/review"))
    items = queue.list_queue()
    pending = sum(1 for it in items if it.get("status") == "pending_review")
    approved = sum(1 for it in items if it.get("status") == "approved")

    pub_dir = config.get("publishing", {}).get("output_directory", "output/published")
    pub_count = len([f for f in os.listdir(pub_dir) if f.endswith(".md")]) if os.path.exists(pub_dir) else 0

    print("\n📊 Hermes Content Pipeline Metrics:")
    print(f"  • Total Unique Items Seen in History (DB): {seen_count}")
    print(f"  • Pending Review Queue:                    {pending}")
    print(f"  • Approved Ready to Publish:               {approved}")
    print(f"  • Published Articles / Digests:            {pub_count}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hermes Content Pipeline Runner")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve items and publish immediately")
    parser.add_argument("--review", action="store_true", help="Launch interactive review queue")
    parser.add_argument("--stats", action="store_true", help="Display pipeline statistics")
    args = parser.parse_args()

    cfg = load_config()

    if args.stats:
        show_stats(cfg)
    elif args.review:
        review_interactive(cfg)
    else:
        run_pipeline(cfg, auto_approve=args.auto_approve)
