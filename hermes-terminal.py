"""
Hermes Agent — Interactive Terminal Client (CLI)
Connects directly to the live Cloud OmniRoute Gateway on Oracle Cloud.
"""

import sys
import json
import urllib.request

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CLOUD_OMNI_URL = "http://92.4.79.176/omniroute/v1/chat/completions"
CLOUD_MASTER_KEY = "sk-omnicloud-92479176-a1b2c3d4e5f6-unlimited"

def chat_loop():
    print("=" * 65)
    print("  ☤ HERMES AGENT TERMINAL · CLOUD OMNIROUTE (Nous Research)")
    print(f"  Gateway: {CLOUD_OMNI_URL}")
    print(f"  API Key: {CLOUD_MASTER_KEY[:18]}...")
    print("  Type 'exit' or 'quit' to end session.")
    print("=" * 65)
    print("\n[Hermes Agent]: Online via Cloud OmniRoute. How can I assist you?\n")

    while True:
        try:
            prompt = input("You > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ("exit", "quit"):
                print("\nGoodbye!")
                break

            req_data = json.dumps({
                "model": "auto/best-fast",
                "messages": [
                    {"role": "system", "content": "You are Hermes Agent, an expert AI created by Nous Research."},
                    {"role": "user", "content": prompt}
                ]
            }).encode("utf-8")

            req = urllib.request.Request(
                CLOUD_OMNI_URL,
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {CLOUD_MASTER_KEY}"
                }
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data["choices"][0]["message"]["content"]
                print(f"\n[Hermes Agent]:\n{reply}\n")
        except KeyboardInterrupt:
            print("\nSession interrupted.")
            break
        except Exception as e:
            print(f"\n[Error]: {e}\n")

if __name__ == "__main__":
    chat_loop()
