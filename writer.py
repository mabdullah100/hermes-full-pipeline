"""
Hermes Content Pipeline - Stage 4: Writing & Synthesis Engine
Generates executive briefs, core insights, social drafts, and markdown deliverables for qualified items.
Supports free OpenRouter models, Gemini API, Ollama local inference, and structured synthesis templates.
"""

import os
import json
import logging
import urllib.request
import re
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HermesWriter")


class ContentWriter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_cfg = config.get("llm", {})
        env_key_var = self.llm_cfg.get("api_key_env", "OPENROUTER_API_KEY")
        self.api_key = os.environ.get(env_key_var, "") or os.environ.get("GEMINI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = self.llm_cfg.get("base_url", "https://openrouter.ai/api/v1")
        self.model = self.llm_cfg.get("model", "meta-llama/llama-3.3-70b-instruct:free")

    def template_synthesize(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """High-clarity template-based synthesis when no external LLM API key is present."""
        title = item.get("title", "")
        source = item.get("source", "Web")
        url = item.get("url", "")
        raw_summary = item.get("raw_summary", "No details available.")

        # Clean executive summary
        summary_clean = raw_summary if len(raw_summary) > 20 else title
        exec_brief = f"**{title}** ({source}): {summary_clean[:300]}..."

        takeaways = [
            f"Key development in {item.get('category', 'AI & Technology')} reported by {source}.",
            "Introduces new tooling, capabilities, or architectural perspectives for automation systems.",
            f"Original documentation and primary source available at: {url}"
        ]

        social_draft = (
            f"🚨 **New in AI & Autonomous Agents**\n\n"
            f"📌 **{title}**\n"
            f"{summary_clean[:220]}...\n\n"
            f"🔗 Read primary source: {url}\n"
            f"#AI #AutonomousAgents #Hermes #MachineLearning"
        )

        return {
            "title": title,
            "executive_brief": exec_brief,
            "takeaways": takeaways,
            "social_draft": social_draft,
            "source_url": url,
            "source_name": source,
            "generated_by": "Hermes Structural Synthesis"
        }

    def llm_synthesize(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tailored multi-format writeups using an LLM."""
        prompt = f"""You are Hermes Writer, the elite technical content writer for Hermes Agent.
Transform the following verified technical news item into structured publishing artifacts:

Title: {item.get('title')}
Source: {item.get('source')}
URL: {item.get('url')}
Raw Content: {item.get('raw_summary')}

Generate valid JSON output with the following exact keys:
{{
  "title": "<Concise punchy title>",
  "executive_brief": "<Bottom Line Up Front: 2-3 clear, insightful sentences>",
  "takeaways": [
    "<Technical takeaway 1>",
    "<Technical takeaway 2>",
    "<Practical impact / developer takeaway 3>"
  ],
  "social_draft": "<Ready-to-post Twitter/X or Telegram broadcast with emojis, key points, and URL>",
  "action_items": "<1 recommendation for developers/builders>"
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
            "temperature": 0.4
        }

        try:
            req = urllib.request.Request(
                f"{self.base_url.rstrip('/')}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                match = re.search(r"\{.*\}", content, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    parsed["source_url"] = item.get("url")
                    parsed["source_name"] = item.get("source")
                    parsed["generated_by"] = f"Hermes LLM ({self.model})"
                    return parsed
        except Exception as e:
            logger.warning(f"LLM synthesis request failed ({e}), falling back to template synthesis.")

        return self.template_synthesize(item)

    def write_draft(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Produce final draft artifacts for an item."""
        if self.api_key:
            draft = self.llm_synthesize(item)
        else:
            draft = self.template_synthesize(item)
        
        item["draft"] = draft
        return item

    def write_all(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and synthesize drafts for all passed items."""
        drafts = []
        for it in items:
            logger.info(f"Writing deliverables for: '{it.get('title')}'")
            drafted = self.write_draft(it)
            drafts.append(drafted)
        return drafts


if __name__ == "__main__":
    with open("config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    writer = ContentWriter(cfg)
    test_item = {
        "title": "Nous Research Releases Hermes Agent Open-Source",
        "source": "Hacker News",
        "url": "https://github.com/NousResearch/hermes-agent",
        "raw_summary": "Hermes Agent is a persistent self-improving agent that supports automated skills, memory, and scheduled cron jobs."
    }

    result = writer.write_draft(test_item)
    print(json.dumps(result["draft"], indent=2))
