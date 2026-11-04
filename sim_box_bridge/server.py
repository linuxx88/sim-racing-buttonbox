"""
Serveur de diffusion HTTP et télémétrie temps réel SSE (Server-Sent Events) pour Sim Box Bridge.
Diffuse les trames de télémétrie unifiées (AMS2, Assetto Corsa) sur '/telemetry' à 30 Hz (30 fps).
"""

import asyncio
import http
import json
from typing import AsyncGenerator, Optional
import websockets

try:
    from telemetry_manager import get_telemetry_manager, TelemetryManager
except ImportError:
    from sim_box_bridge.telemetry_manager import get_telemetry_manager, TelemetryManager

DEFAULT_FPS = 30


async def telemetry_stream(manager: Optional[TelemetryManager] = None, fps: int = DEFAULT_FPS) -> AsyncGenerator[str, None]:
    """
    Générateur asynchrone SSE produisant des trames de télémétrie cadencées à `fps` images par seconde.
    """
    if manager is None:
        manager = get_telemetry_manager()
    interval = 1.0 / float(fps)
    while True:
        data = manager.read()
        payload = f"data: {json.dumps(data)}\n\n"
        yield payload
        await asyncio.sleep(interval)


async def handle_sse_telemetry(connection, request, manager: Optional[TelemetryManager] = None, fps: int = DEFAULT_FPS):
    """
    Traite la requête HTTP GET /telemetry en injectant les en-têtes SSE
    et en diffusant le flux text/event-stream à 30 Hz.
    """
    if manager is None:
        manager = get_telemetry_manager()

    transport = connection.transport
    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/event-stream; charset=utf-8\r\n"
        "Cache-Control: no-cache, no-transform\r\n"
        "Connection: keep-alive\r\n"
        "Access-Control-Allow-Origin: *\r\n\r\n"
    )
    transport.write(headers.encode("utf-8"))

    interval = 1.0 / float(fps)
    try:
        while not transport.is_closing():
            data = manager.read()
            frame = f"data: {json.dumps(data)}\n\n"
            transport.write(frame.encode("utf-8"))
            await asyncio.sleep(interval)
    except Exception:
        pass
    finally:
        if not transport.is_closing():
            transport.close()

    # Termine la négociation sans déclencher d'exception WebSocket
    return connection.respond(http.HTTPStatus.OK, "")
