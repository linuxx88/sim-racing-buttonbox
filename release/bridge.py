import asyncio
import http
import json
import os
import signal
import sys
import websockets
import websockets.http11
from websockets.http11 import parse_line, parse_headers, d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from injector import get_injector, VALID_TYPES

HOST = "127.0.0.1"
PORT = 5000
HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

injector = get_injector()

# Support HTTP HEAD in addition to GET for websockets handshake parser
@classmethod
def _patched_parse(cls, read_line):
    try:
        request_line = yield from parse_line(read_line)
    except EOFError as exc:
        raise EOFError("connection closed while reading HTTP request line") from exc

    try:
        method, raw_path, protocol = request_line.split(b" ", 2)
    except ValueError:
        raise ValueError(f"invalid HTTP request line: {d(request_line)}") from None
    if protocol != b"HTTP/1.1":
        raise ValueError(f"unsupported protocol; expected HTTP/1.1: {d(request_line)}")
    if method not in (b"GET", b"HEAD"):
        raise ValueError(f"unsupported HTTP method; expected GET/HEAD; got {d(method)}")
    path = raw_path.decode("ascii", "surrogateescape")
    headers = yield from parse_headers(read_line)
    req = cls(path, headers)
    req.method = method.decode()
    return req

websockets.http11.Request.parse = _patched_parse

def load_html() -> str:
    base_dir = getattr(sys, "_MEIPASS", os.path.abspath("."))
    candidates = [
        HTML_PATH,
        os.path.join(base_dir, "index.html"),
        os.path.join(base_dir, "sim_box_bridge", "index.html"),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
    return "<h1>Error loading index.html</h1>"

def process_request(connection, request):
    if "Upgrade" in request.headers:
        return None
    req_path = request.path.split("?")[0]
    if req_path in ("/", "/index.html"):
        content = load_html()
        is_head = getattr(request, "method", "GET") == "HEAD"
        response = connection.respond(http.HTTPStatus.OK, "" if is_head else content)
        del response.headers["Content-Type"]
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        if is_head:
            del response.headers["Content-Length"]
            response.headers["Content-Length"] = str(len(content.encode("utf-8")))
        return response
    return None

async def handler(websocket):
    try:
        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
                if not isinstance(data, dict):
                    print(f"[BRIDGE_WARNING] Non-object payload ignored: {raw_message}", flush=True)
                    continue
                action = data.get("action")
                action_type = data.get("type")
                if not isinstance(action, str) or action_type not in VALID_TYPES:
                    print(f"[BRIDGE_WARNING] Invalid schema: action={action}, type={action_type}", flush=True)
                    continue
                injector.handle(action, action_type)
            except (json.JSONDecodeError, UnicodeDecodeError):
                print(f"[BRIDGE_WARNING] Corrupted JSON frame ignored: {raw_message}", flush=True)
    except websockets.exceptions.ConnectionClosed:
        pass

async def main():
    stop = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except (NotImplementedError, AttributeError):
            pass

    async with websockets.serve(handler, HOST, PORT, process_request=process_request):
        print("SERVER_LISTENING_PORT_5000", flush=True)
        await stop.wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        sys.exit(1)
