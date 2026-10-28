"""
service_mcp.py
--------------
Définition du serveur MCP (Model Context Protocol) EchoData.
Exposes les données et services existants via des outils (tools) MCP,
appelés directement sans requête HTTP interne.

API SDK MCP Python 1.26 :
  - @mcp_server.list_tools()  → retourne la liste des outils disponibles
  - @mcp_server.call_tool()   → exécute un outil par son nom et arguments
"""

import json
from typing import Literal

from mcp.server import Server
from mcp.types import Tool, TextContent

from ..config import Config, logger
from .service_events_day import service_events_day
from .service_oracle import Service_Oracle
from .service_music import service_music
from ..models.dataClasses_Horoscope import Sign, Horoscope20

# ------------------------------------------------------------------
# Initialise le serveur MCP (une seule instance globale, thread-safe)
# ------------------------------------------------------------------
mcp_server = Server("EchoData")

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _resolve_db(category: Literal["international", "daysoff", "saints"]) -> str:
    """Retourne le chemin JSON correspondant à la catégorie."""
    mapping = {
        "international": Config.DATABASE_JSON_EVENTS,
        "daysoff": Config.DATABASE_JSON_DAYOFF,
        "saints": Config.DATABASE_JSON_SAINTS,
    }
    return mapping.get(category, Config.DATABASE_JSON_EVENTS)


def _serialize_events(events):
    """Convertit une liste d'EventDay en dict JSON-safe."""
    return [{"name": ev.getName, "date": ev.getDate} for ev in events]


# ------------------------------------------------------------------
# Schémas JSON des outils (pour découverte auto par les clients MCP)
# ------------------------------------------------------------------

TOOLS_SCHEMA = [
    Tool(
        name="echodata_get_events_today",
        description="Retourne les événements du jour (journées internationales, jours fériés ou saints).",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["international", "daysoff", "saints"],
                    "description": "Type d'événement",
                    "default": "international",
                }
            },
        },
    ),
    Tool(
        name="echodata_get_events_by_date",
        description="Retourne les événements pour une date précise (format YYYY-MM-DD).",
        inputSchema={
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date au format YYYY-MM-DD",
                },
                "category": {
                    "type": "string",
                    "enum": ["international", "daysoff", "saints"],
                    "description": "Type d'événement",
                    "default": "international",
                },
            },
            "required": ["date"],
        },
    ),
    Tool(
        name="echodata_get_events_current_month",
        description="Retourne tous les événements du mois en cours.",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["international", "daysoff", "saints"],
                    "description": "Type d'événement",
                    "default": "international",
                }
            },
        },
    ),
    Tool(
        name="echodata_get_random_event",
        description="Retourne un événement aléatoire.",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["international", "daysoff", "saints"],
                    "description": "Type d'événement",
                    "default": "international",
                }
            },
        },
    ),
    Tool(
        name="echodata_get_horoscope",
        description="Retourne l'horoscope du jour pour un signe astrologique.",
        inputSchema={
            "type": "object",
            "properties": {
                "sign": {
                    "type": "string",
                    "description": "Signe astrologique (ex: aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces)",
                }
            },
            "required": ["sign"],
        },
    ),
    Tool(
        name="echodata_get_random_music_track",
        description="Retourne un morceau musical aléatoire depuis la base music.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


# ------------------------------------------------------------------
# Handler : list_tools
# ------------------------------------------------------------------

@mcp_server.list_tools()
async def handle_list_tools():
    """Retourne la liste des outils MCP disponibles."""
    return TOOLS_SCHEMA


# ------------------------------------------------------------------
# Handler : call_tool
# ------------------------------------------------------------------

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None):
    """
    Exécute l'outil demandé avec les arguments fournis.

    Args:
        name: Nom de l'outil MCP.
        arguments: Dictionnaire des paramètres (peut être None).

    Returns:
        Liste de TextContent avec le résultat JSON.
    """
    if arguments is None:
        arguments = {}

    # --------------------------------------------------------------
    # 1. echodata_get_events_today
    # --------------------------------------------------------------
    if name == "echodata_get_events_today":
        category = arguments.get("category", "international")
        try:
            db_path = _resolve_db(category)
            service = service_events_day(db_path)
            events = service.get_events_today()
            payload = {
                "category": category,
                "count": len(events),
                "events": _serialize_events(events),
            }
            return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]
        except Exception as e:
            logger.error(f"MCP tool {name} error: {e}")
            return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]

    # --------------------------------------------------------------
    # 2. echodata_get_events_by_date
    # --------------------------------------------------------------
    if name == "echodata_get_events_by_date":
        date_str = arguments.get("date")
        category = arguments.get("category", "international")
        try:
            db_path = _resolve_db(category)
            service = service_events_day(db_path)
            events = service.get_events_by_date(date_str)
            payload = {
                "date": date_str,
                "category": category,
                "count": len(events),
                "events": _serialize_events(events),
            }
            return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]
        except Exception as e:
            logger.error(f"MCP tool {name} error: {e}")
            return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]

    # --------------------------------------------------------------
    # 3. echodata_get_events_current_month
    # --------------------------------------------------------------
    if name == "echodata_get_events_current_month":
        category = arguments.get("category", "international")
        try:
            db_path = _resolve_db(category)
            service = service_events_day(db_path)
            events = service.get_events_current_month()
            payload = {
                "category": category,
                "count": len(events),
                "events": _serialize_events(events),
            }
            return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]
        except Exception as e:
            logger.error(f"MCP tool {name} error: {e}")
            return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]

    # --------------------------------------------------------------
    # 4. echodata_get_random_event
    # --------------------------------------------------------------
    if name == "echodata_get_random_event":
        category = arguments.get("category", "international")
        try:
            db_path = _resolve_db(category)
            service = service_events_day(db_path)
            events = service.get_events_random()
            payload = {
                "category": category,
                "count": len(events),
                "events": _serialize_events(events),
            }
            return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]
        except Exception as e:
            logger.error(f"MCP tool {name} error: {e}")
            return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]

    # --------------------------------------------------------------
    # 5. echodata_get_horoscope
    # --------------------------------------------------------------
    if name == "echodata_get_horoscope":
        sign_text = arguments.get("sign", "")
        try:
            sign_enum = Sign(sign_text.upper())
            service = Service_Oracle(sign_enum)
            horoscope = service.loadData(sign_enum, Horoscope20)
            service.Horoscope = horoscope
            payload = {
                "sign": service.Horoscope.sign,
                "date": service.Horoscope.date.strftime("%Y-%m-%d"),
                "sections": service.Horoscope.sections,
            }
            return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]
        except Exception as e:
            logger.error(f"MCP tool {name} error: {e}")
            return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]

    # --------------------------------------------------------------
    # 6. echodata_get_random_music_track
    # --------------------------------------------------------------
    if name == "echodata_get_random_music_track":
        try:
            track = service_music.loadRandomTrack(enrich=True)
            return [TextContent(type="text", text=json.dumps(track, ensure_ascii=False))]
        except Exception as e:
            logger.error(f"MCP tool {name} error: {e}")
            return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]

    # --------------------------------------------------------------
    # Outil inconnu
    # --------------------------------------------------------------
    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False))]
