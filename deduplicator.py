"""
Hermes Content Pipeline - Stage 2: Deduplication Engine
Handles URL canonicalization, persistent SQLite tracking, and semantic title similarity matching.
Prevents processing or paying tokens for duplicate stories across feeds or time.
"""

import sqlite3
import hashlib
import re
import urllib.parse
from datetime import datetime, timezone
import logging
from typing import List, Dict, Any, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HermesDeduplicator")

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "fbclid", "gclid", "mc_cid", "mc_eid", "source"
}


class Deduplicator:
    def __init__(self, db_path: str = "data/pipeline.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database for tracking processed content."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seen_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url_hash TEXT UNIQUE NOT NULL,
                    canonical_url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    title_fingerprint TEXT NOT NULL,
                    source TEXT,
                    first_seen_at TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_seen_url ON seen_items(url_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_seen_fingerprint ON seen_items(title_fingerprint)")
            conn.commit()

    @staticmethod
    def canonicalize_url(raw_url: str) -> str:
        """Strip tracking parameters and normalize URL."""
        if not raw_url:
            return ""
        parsed = urllib.parse.urlparse(raw_url.strip())
        query_dict = urllib.parse.parse_qs(parsed.query)
        cleaned_query = {k: v for k, v in query_dict.items() if k.lower() not in TRACKING_PARAMS}
        new_query = urllib.parse.urlencode(cleaned_query, doseq=True)
        path = parsed.path.rstrip("/")
        normalized = urllib.parse.urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            "",
            new_query,
            ""
        ))
        return normalized

    @staticmethod
    def url_hash(canonical_url: str) -> str:
        """Compute SHA256 hash of canonical URL."""
        return hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()

    @staticmethod
    def title_fingerprint(title: str) -> str:
        """Generate a normalized word set fingerprint for fuzzy title matching."""
        if not title:
            return ""
        # Lowercase, keep alphanumeric, remove common stopwords
        words = re.findall(r"\b[a-zA-Z0-9]{3,}\b", title.lower())
        stopwords = {"the", "and", "for", "with", "that", "this", "from", "are", "was", "has", "have", "you", "new"}
        filtered = sorted(set(w for w in words if w not in stopwords))
        return " ".join(filtered)

    @staticmethod
    def jaccard_similarity(set_a: set, set_b: set) -> float:
        """Calculate Jaccard similarity between two token sets."""
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        return float(intersection) / float(union) if union > 0 else 0.0

    def is_duplicate(self, item: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if item is a duplicate by URL hash or title similarity."""
        canonical_url = self.canonicalize_url(item.get("url", ""))
        uhash = self.url_hash(canonical_url)
        fingerprint = self.title_fingerprint(item.get("title", ""))
        tokens_current = set(fingerprint.split())

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 1. Exact URL match
            cursor.execute("SELECT id, title FROM seen_items WHERE url_hash = ?", (uhash,))
            row = cursor.fetchone()
            if row:
                return True, f"Exact URL duplicate (ID: {row[0]}, Title: '{row[1]}')"

            # 2. Semantic title similarity against recent entries
            cursor.execute("SELECT id, title, title_fingerprint FROM seen_items ORDER BY id DESC LIMIT 500")
            recent_rows = cursor.fetchall()
            for rid, rtitle, rfp in recent_rows:
                tokens_seen = set(rfp.split())
                similarity = self.jaccard_similarity(tokens_current, tokens_seen)
                if similarity >= 0.70:
                    return True, f"High title similarity ({similarity:.2f}) with ID {rid}: '{rtitle}'"

        return False, ""

    def mark_seen(self, item: Dict[str, Any]):
        """Persist item to database so it won't be processed again."""
        canonical_url = self.canonicalize_url(item.get("url", ""))
        uhash = self.url_hash(canonical_url)
        fingerprint = self.title_fingerprint(item.get("title", ""))
        now = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO seen_items 
                    (url_hash, canonical_url, title, title_fingerprint, source, first_seen_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (uhash, canonical_url, item.get("title", ""), fingerprint, item.get("source", ""), now))
                conn.commit()
            except Exception as e:
                logger.error(f"Error persisting item to deduplication DB: {e}")

    def deduplicate(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out duplicate items from a list of collected items."""
        unique_items = []
        for item in items:
            dup, reason = self.is_duplicate(item)
            if dup:
                logger.debug(f"Skipping duplicate: '{item.get('title')}' -> {reason}")
                continue
            unique_items.append(item)
            self.mark_seen(item)

        logger.info(f"Deduplication complete: {len(unique_items)} unique items kept out of {len(items)} collected.")
        return unique_items


if __name__ == "__main__":
    dedup = Deduplicator("data/test_pipeline.db")
    item1 = {
        "title": "Nous Research Releases Hermes Agent v2026",
        "url": "https://example.com/hermes-agent?utm_source=twitter&ref=123",
        "source": "TechNews"
    }
    item2 = {
        "title": "Nous Research Releases Hermes Agent v2026 Update",
        "url": "https://anothersite.com/hermes-agent-release",
        "source": "AnotherNews"
    }
    item3 = {
        "title": "Completely Unrelated Story About Quantum Computing",
        "url": "https://example.com/quantum",
        "source": "PhysicsNews"
    }

    filtered = dedup.deduplicate([item1, item2, item3])
    print(f"Kept {len(filtered)} items.")
    for it in filtered:
        print(" -", it["title"])
