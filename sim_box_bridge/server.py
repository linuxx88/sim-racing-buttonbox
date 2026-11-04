"""
Serveur de diffusion HTTP et télémétrie temps réel SSE (Server-Sent Events) pour Sim Box Bridge.
Diffuse les trames de télémétrie Assetto Corsa sur '/telemetry' à 30 Hz (30 fps).
"""

import asyncio
import http
import json
from typing import AsyncGenerator
import websockets

try:
    from telemetry_ac import get_ac_reader, AssettoCorsaReader
except ImportError:
    from sim_box_bridge.telemetry_ac import get_ac_reader, AssettoCorsaReader

DEFAULT_FPS = 30


async def telemetry_stream(reader: AssettoCorsaReader, fps: int = DEFAULT_FPS) -> AsyncGenerator[str, None]:
    """
    Générateur asynchrone SSE produisant des trames de télémétrie cadencées à `fps` images par seconde.
    """
    interval = 1.0 / float(fps)
    while True:
        data = reader.read()
        payload = f"data: {json.dumps(data)}\n\n"
        yield payload
        await asyncio.sleep(interval)


async def handle_sse_telemetry(connection, request, reader: AssettoCorsaReader = None, fps: int = DEFAULT_FPS):
    """
    Traite la requête HTTP GET /telemetry en injectant les en-têtes SSE
    et en diffusant le flux text/event-stream à 30 Hz.
    """
    if reader is None:
        reader = get_ac_reader()

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
            data = reader.read()
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
