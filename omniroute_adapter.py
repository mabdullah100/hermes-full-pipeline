"""
Hermes <-> OmniRoute Gateway Adapter
Bridges Hermes Agent with the active OmniRoute AI Gateway on the laptop (or remote VPS).
Automatically discovers, inspects, and routes queries through OmniRoute's free models.
"""

import os
import json
import logging
import urllib.request
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("OmniRouteAdapter")

DEFAULT_OMNIROUTE_URL = os.environ.get("OMNIROUTE_BASE_URL", "http://127.0.0.1:20128/v1")
DEFAULT_OMNIROUTE_KEY = os.environ.get("OMNIROUTE_API_KEY", "sk-cfdb375eb158eba9-a065cc-001dea1c")


class OmniRouteClient:
    def __init__(self, base_url: str = DEFAULT_OMNIROUTE_URL, api_key: str = DEFAULT_OMNIROUTE_KEY):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def is_online(self) -> bool:
        """Check if OmniRoute server is reachable."""
        try:
            req = urllib.request.Request(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """Fetch all available models from OmniRoute."""
        try:
            req = urllib.request.Request(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to query OmniRoute models: {e}")
            return []

    def get_free_models(self) -> List[str]:
        """Return free and auto model identifiers."""
        models = self.list_models()
        free_ids = []
        for m in models:
            mid = m.get("id", "")
            if any(k in mid.lower() for k in ["free", "auto", "fast", "cheap"]):
                free_ids.append(mid)
        return free_ids

    def complete(self, prompt: str, model: str = "auto/best-fast", system: Optional[str] = None) -> Optional[str]:
        """Send chat completion to OmniRoute."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3
        }

        try:
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"OmniRoute request to {model} failed: {e}")
            return None


if __name__ == "__main__":
    client = OmniRouteClient()
    online = client.is_online()
    print(f"OmniRoute online at {client.base_url}: {online}")
    if online:
        free = client.get_free_models()
        print(f"Found {len(free)} free/auto model routes in OmniRoute:")
        for f in free[:10]:
            print(f"  - {f}")
