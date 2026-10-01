"""
Hermes Agent — Interactive Terminal Client (CLI)
Connects directly to the live Oracle Cloud Hermes Agent server.
"""

import sys
import json
import urllib.request

SERVER_URL = "http://92.4.79.176/hermes/api/chat"

def chat_loop():
    print("=" * 60)
    print("  ☤ HERMES AGENT INTERACTIVE TERMINAL (Nous Research)")
    print("  Server: http://92.4.79.176/hermes/")
    print("  Type 'exit' or 'quit' to end session.")
    print("=" * 60)
    print("\n[Hermes Agent]: Online and ready. How can I assist you?\n")

    while True:
        try:
            prompt = input("You > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ("exit", "quit"):
                print("\nGoodbye!")
                break

            req_data = json.dumps({"message": prompt}).encode("utf-8")
            req = urllib.request.Request(
                SERVER_URL,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data.get("reply", "No response.")
                print(f"\n[Hermes Agent]:\n{reply}\n")
        except KeyboardInterrupt:
            print("\nSession interrupted.")
            break
        except Exception as e:
            print(f"\n[Error]: {e}\n")

if __name__ == "__main__":
    chat_loop()
