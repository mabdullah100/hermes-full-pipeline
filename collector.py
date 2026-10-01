"""
Hermes Content Pipeline - Stage 1: Collector
Collects content from declared RSS feeds, news sources, or web endpoints.
Uses built-in standard libraries (urllib / xml.etree) and httpx for zero-extra-dependency reliability.
"""

import sys
import json
import logging
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import re
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HermesCollector")

HEADERS = {
    "User-Agent": "HermesAgent/2026.9 (Autonomous Content Pipeline; https://hermes-agent.nousresearch.com)"
}


def clean_html_tags(raw_html: str) -> str:
    """Strip HTML markup and collapse whitespace."""
    if not raw_html:
        return ""
    clean = re.sub(r"<[^>]+>", " ", raw_html)
    clean = re.sub(r"&[a-zA-Z0-9#]+;", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def parse_rss_or_atom(xml_content: bytes, source_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse RSS 2.0 or Atom XML content into normalized dictionaries."""
    items = []
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        logger.warning(f"Failed to parse XML for {source_info.get('name')}: {e}")
        return items

    # Check RSS 2.0 channel -> item
    channel = root.find("channel")
    if channel is not None:
        for entry in channel.findall("item"):
            title = entry.findtext("title", default="").strip()
            link = entry.findtext("link", default="").strip()
            desc = entry.findtext("description", default="").strip()
            pub_date = entry.findtext("pubDate", default="")

            if not link or not title:
                continue

            items.append({
                "source": source_info.get("name", "RSS Feed"),
                "category": source_info.get("category", "General"),
                "title": title,
                "url": link,
                "raw_summary": clean_html_tags(desc),
                "published_at": pub_date,
                "collected_at": datetime.now(timezone.utc).isoformat()
            })
        return items

    # Check Atom feed -> entry (with namespace handling)
    namespaces = {"atom": "http://www.w3.org/2005/Atom"}
    # Handle both with and without namespace
    atom_entries = root.findall("atom:entry", namespaces) or root.findall("entry")
    for entry in atom_entries:
        title = entry.findtext("atom:title", namespaces=namespaces, default="") or entry.findtext("title", default="")
        desc = (entry.findtext("atom:summary", namespaces=namespaces, default="") or
                entry.findtext("summary", default="") or
                entry.findtext("atom:content", namespaces=namespaces, default="") or
                entry.findtext("content", default=""))
        
        # Link in atom can be an attribute
        link_elem = entry.find("atom:link", namespaces=namespaces) or entry.find("link")
        link = ""
        if link_elem is not None:
            link = link_elem.get("href", "").strip() or link_elem.text or ""
        
        pub_date = (entry.findtext("atom:published", namespaces=namespaces, default="") or
                    entry.findtext("atom:updated", namespaces=namespaces, default="") or
                    entry.findtext("published", default="") or
                    entry.findtext("updated", default=""))

        if not link or not title:
            continue

        items.append({
            "source": source_info.get("name", "Atom Feed"),
            "category": source_info.get("category", "General"),
            "title": title.strip(),
            "url": link,
            "raw_summary": clean_html_tags(desc),
            "published_at": pub_date.strip(),
            "collected_at": datetime.now(timezone.utc).isoformat()
        })

    return items


def fetch_source(source: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Fetch and parse a single content source."""
    url = source.get("url")
    name = source.get("name", url)
    logger.info(f"Collecting from '{name}' -> {url}")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            items = parse_rss_or_atom(content, source)
            logger.info(f"Fetched {len(items)} items from '{name}'")
            return items
    except Exception as e:
        logger.error(f"Error fetching '{name}': {e}")
        return []


def collect_all(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Run collection across all declared sources."""
    all_items = []
    for src in sources:
        items = fetch_source(src)
        all_items.extend(items)
    logger.info(f"Total collected items across {len(sources)} sources: {len(all_items)}")
    return all_items


if __name__ == "__main__":
    test_source = {
        "name": "Hacker News AI",
        "url": "https://hnrss.org/newest?q=AI+OR+LLM&points=30",
        "category": "Tech"
    }
    results = fetch_source(test_source)
    print(f"Sample output ({len(results)} items collected):")
    if results:
        print(json.dumps(results[0], indent=2))
