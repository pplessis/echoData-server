"""
mcp_v100.py
-----------
Endpoints Flask exposant le serveur MCP EchoData via transport SSE.

Architecture :
  GET  /v100/mcp/sse               → Ouvre une connexion SSE longue
  POST /v100/mcp/messages          → Endpoint où le client MCP POSTe les messages

Le serveur MCP (mcp_server) tourne dans un thread dédié avec son propre event
loop asyncio, afin de rester compatible avec le runtime WSGI Flask sans migrer
vers ASGI.

Limitation Vercel serverless :
  Le SSE nécessite une session mémoire partagée entre GET et POST.
  En local / `vercel dev` → ✅ parfaitement fonctionnel.
  En prod Vercel serverless → ⚠️ peut être instable si GET et POST atterrissent
  sur des instances différentes (stateless).
"""

import asyncio
import json
import queue
import threading
import time
import uuid
from typing import Dict, Any

import anyio
from flask import Blueprint, jsonify, request, Response

from ..services.service_mcp import mcp_server

mcp_v100 = Blueprint("mcp_v100", __name__)

# ------------------------------------------------------------------
# Sessions MCP : stockage en mémoire
# ------------------------------------------------------------------
# Structure par session :
#   {
#       "tx": anyio.streams.memory.MemoryObjectSendStream,
#       "loop": asyncio.AbstractEventLoop,
#       "created_at": float (timestamp)
#   }
_sessions: Dict[str, Any] = {}
_sessions_lock = threading.Lock()


def _cleanup_old_sessions(timeout: float = 3600.0):
    """Supprime les sessions inactives depuis plus de `timeout` secondes."""
    now = time.time()
    with _sessions_lock:
        stale = [
            sid for sid, s in _sessions.items()
            if now - s.get("created_at", 0) > timeout
        ]
        for sid in stale:
            del _sessions[sid]
            if stale:
                # log via print simple car on est hors contexte Flask request
                print(f"[MCP] Cleaned stale session {sid}")


# ------------------------------------------------------------------
# Route SSE : connexion longue vers le client MCP
# ------------------------------------------------------------------

@mcp_v100.route("/mcp/sse", methods=["GET"])
def mcp_sse():
    """
    Établit une connexion SSE et démarre une session MCP dédiée.
    Le client MCP doit ensuite effectuer des POST sur /mcp/messages
    avec le query-param `session_id` retourné ici.
    """
    _cleanup_old_sessions()

    session_id = str(uuid.uuid4())
    ready_event = threading.Event()
    msg_queue: queue.Queue = queue.Queue()

    def run_mcp_session():
        """Thread dédié : héberge l'event loop asyncio + le serveur MCP."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Streams anyio : client -> serveur et serveur -> client
        client_rx, client_tx = anyio.create_memory_object_stream(0)
        server_rx, server_tx = anyio.create_memory_object_stream(0)

        with _sessions_lock:
            _sessions[session_id] = {
                "tx": client_tx,
                "loop": loop,
                "created_at": time.time(),
            }

        # Prévient le thread principal que la session est prête
        ready_event.set()

        async def mcp_main():
            """Lance le serveur MCP et pump les messages vers la queue sync."""
            async with anyio.create_task_group() as tg:
                tg.start_soon(
                    mcp_server.run,
                    client_rx,
                    server_tx,
                    mcp_server.create_initialization_options(),
                )
                async for message in server_rx:
                    msg_queue.put(message)

        loop.run_until_complete(mcp_main())

    # Démarre le thread MCP
    thread = threading.Thread(target=run_mcp_session, daemon=True)
    thread.start()

    # Attend que la session soit initialisée (timeout 5s)
    if not ready_event.wait(timeout=5):
        return jsonify({"error": "MCP session failed to start within 5s"}), 500

    def generate_sse():
        """Générateur Flask (sync) : consomme la queue et yield les events SSE."""
        while True:
            message = msg_queue.get()
            yield f"event: message\ndata: {json.dumps(message)}\n\n"

    return Response(generate_sse(), mimetype="text/event-stream")


# ------------------------------------------------------------------
# Route POST : injection de messages dans la session MCP
# ------------------------------------------------------------------

@mcp_v100.route("/mcp/messages", methods=["POST"])
def mcp_messages():
    """
    Reçoit un message JSON-RPC du client MCP et l'injecte dans la session
    identifiée par `session_id`.
    """
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id query parameter"}), 400

    with _sessions_lock:
        session = _sessions.get(session_id)

    if not session:
        return jsonify({"error": "Session not found or expired"}), 404

    message = request.get_json()
    if message is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    tx = session["tx"]
    loop = session["loop"]

    # Exécute tx.send() dans le event loop distant du thread MCP
    future = asyncio.run_coroutine_threadsafe(tx.send(message), loop)
    try:
        future.result(timeout=5)
        return "", 202
    except Exception as e:
        return jsonify({"error": f"Failed to forward message: {e}"}), 500
