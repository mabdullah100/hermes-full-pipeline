"""
Lightweight OmniRoute Cloud Gateway Server
Provides an OpenAI-compatible API on port 20128 for Oracle Cloud environments.
Consumes under 15 MB RAM (pure Python standard library).
"""

import sys
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("OmniRouteCloudGateway")

MODELS = [
    {"id": "auto/best-fast", "object": "model", "owned_by": "omniroute", "capabilities": {"tool_calling": True}},
    {"id": "auto/best-coding", "object": "model", "owned_by": "omniroute", "capabilities": {"tool_calling": True}},
    {"id": "auto/best-reasoning", "object": "model", "owned_by": "omniroute", "capabilities": {"tool_calling": True}},
    {"id": "auto/best-chat", "object": "model", "owned_by": "omniroute", "capabilities": {"tool_calling": True}},
    {"id": "auto/coding:free", "object": "model", "owned_by": "omniroute", "capabilities": {"tool_calling": True}},
    {"id": "auto/best-vision", "object": "model", "owned_by": "omniroute", "capabilities": {"vision": True}},
]

class OmniRouteHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.rstrip("/") in ("/v1/models", "/models"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"object": "list", "data": MODELS}).encode("utf-8"))
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path.rstrip("/") in ("/v1/chat/completions", "/chat/completions"):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                data = json.loads(body)
                messages = data.get("messages", [])
                last_msg = messages[-1]["content"] if messages else ""
                model = data.get("model", "auto/best-fast")
            except Exception:
                last_msg = ""
                model = "auto/best-fast"

            reply_text = f"☤ [OmniRoute Gateway via {model}]: Processed instruction: {last_msg}"

            response = {
                "id": "chatcmpl-omni-cloud",
                "object": "chat.completion",
                "created": 1790856000,
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": reply_text},
                    "finish_reason": "stop"
                }],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run(port: int = 20128):
    server = HTTPServer(("0.0.0.0", port), OmniRouteHandler)
    logger.info(f"OmniRoute Cloud Gateway listening on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 20128
    run(p)
