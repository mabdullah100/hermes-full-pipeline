"""
Hermes Content Pipeline - Stage 3: AI Filtering & Materiality Scoring
Scores and filters items based on technical significance, novelty, and topic match.
Supports free OpenRouter models, Google Gemini free tier, local Ollama, and heuristic fallback.
"""

import os
import json
import logging
import urllib.request
import re
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HermesFilter")


class AIFilter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_cfg = config.get("llm", {})
        self.filter_cfg = config.get("filter", {})
        self.threshold = self.filter_cfg.get("materiality_threshold", 7)
        self.target_topics = [t.lower() for t in self.filter_cfg.get("target_topics", [])]
        self.negative_keywords = [k.lower() for k in self.filter_cfg.get("negative_keywords", [])]

        # Check API key from env or config
        env_key_var = self.llm_cfg.get("api_key_env", "OPENROUTER_API_KEY")
        self.api_key = os.environ.get(env_key_var, "") or os.environ.get("GEMINI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = self.llm_cfg.get("base_url", "https://openrouter.ai/api/v1")
        self.model = self.llm_cfg.get("model", "meta-llama/llama-3.3-70b-instruct:free")

    def heuristic_score(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligent fallback scoring when no external LLM key is configured."""
        text = f"{item.get('title', '')} {item.get('raw_summary', '')}".lower()

        # Check negative keywords first
        for neg in self.negative_keywords:
            if neg in text:
                return {
                    "materiality_score": 2,
                    "relevance_score": 1,
                    "verdict": "FILTERED",
                    "reason": f"Matched negative keyword: '{neg}'"
                }

        # Check topic matches
        matched_topics = [topic for topic in self.target_topics if topic in text]
        score = 4 + min(len(matched_topics) * 2, 5)

        # Boost for substantive terms
        high_value_terms = ["release", "open-source", "architecture", "breakthrough", "benchmark", "framework", "autonomous", "weights"]
        boost = sum(1 for term in high_value_terms if term in text)
        score = min(score + boost, 10)

        verdict = "PASS" if score >= self.threshold else "FILTERED"
        return {
            "materiality_score": score,
            "relevance_score": score,
            "verdict": verdict,
            "matched_topics": matched_topics,
            "reason": f"Heuristic analysis: matched {len(matched_topics)} topics ({', '.join(matched_topics[:3])})"
        }

    def llm_score(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate item using an LLM endpoint (OpenRouter free model / Gemini / Ollama)."""
        prompt = f"""You are an elite AI technical content curator for Hermes Agent.
Evaluate the following article for an engineering/AI audience.

Title: {item.get('title')}
Source: {item.get('source')}
Summary: {item.get('raw_summary')}

Desired Topics: {', '.join(self.target_topics)}
Threshold: {self.threshold}/10

Respond strictly in valid JSON format:
{{
  "materiality_score": <1-10>,
  "relevance_score": <1-10>,
  "verdict": "<PASS or FILTERED>",
  "reason": "<1 sentence explanation>"
}}"""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://hermes-agent.nousresearch.com",
            "X-Title": "Hermes Content Pipeline"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }

        try:
            req = urllib.request.Request(
                f"{self.base_url.rstrip('/')}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                # Extract json from codeblocks if wrapped
                match = re.search(r"\{.*\}", content, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
        except Exception as e:
            logger.warning(f"LLM scoring request failed ({e}), falling back to heuristic scoring.")

        return self.heuristic_score(item)

    def evaluate_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Score an individual item."""
        if self.api_key:
            score_data = self.llm_score(item)
        else:
            score_data = self.heuristic_score(item)

        item["evaluation"] = score_data
        return item

    def filter_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter a list of items and retain only those passing the materiality threshold."""
        passed = []
        for item in items:
            evaluated = self.evaluate_item(item)
            ev = evaluated.get("evaluation", {})
            if ev.get("verdict") == "PASS" and ev.get("materiality_score", 0) >= self.threshold:
                passed.append(evaluated)
                logger.info(f"[PASS - Score {ev.get('materiality_score')}/10] {item.get('title')}")
            else:
                logger.info(f"[FILTERED - Score {ev.get('materiality_score')}/10] {item.get('title')}")

        logger.info(f"Filtering complete: {len(passed)} items passed threshold out of {len(items)}.")
        return passed


if __name__ == "__main__":
    with open("config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    ai_filter = AIFilter(cfg)
    test_items = [
        {
            "title": "Nous Research Unveils Hermes Agent with Autonomous Self-Evolution",
            "raw_summary": "Open-source agent features persistent memory, skill discovery, and reinforcement learning optimization for developer workflows.",
            "source": "AI Tech"
        },
        {
            "title": "Top 10 Casino Crypto Meme Coins to Buy Tonight",
            "raw_summary": "Get rich quick with these gambling tokens on blockchain.",
            "source": "CryptoDaily"
        }
    ]

    filtered = ai_filter.filter_items(test_items)
    print(f"Passed: {len(filtered)} items.")
