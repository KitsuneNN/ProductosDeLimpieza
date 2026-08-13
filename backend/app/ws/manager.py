# -*- coding: utf-8 -*-
"""WebSockets — manager de conexiones y broadcast (B-T6)."""
import json
import logging
from datetime import datetime
from decimal import Decimal

from fastapi import WebSocket

logger = logging.getLogger("app.ws")


def _serializador(obj):
    """Codificador JSON para payloads de eventos: Decimal→float, datetime→ISO."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Tipo no serializable en evento WS: {type(obj).__name__}")


class ConnectionManager:
    """Mantiene conexiones por rol y transmite eventos JSON.

    Canales:
    - `admin`    → solo administradores (ej. solicitud.creada → aviso sonoro)
    - `cliente`  → solo clientes
    - broadcast  → todos (ej. solicitud.pagada)
    """

    def __init__(self) -> None:
        self._conexiones: dict[str, set[WebSocket]] = {"admin": set(), "cliente": set()}

    async def conectar(self, websocket: WebSocket, rol: str) -> None:
        canal = rol if rol in self._conexiones else "cliente"
        self._conexiones[canal].add(websocket)

    def desconectar(self, websocket: WebSocket, rol: str) -> None:
        canal = rol if rol in self._conexiones else "cliente"
        self._conexiones[canal].discard(websocket)

    async def enviar_a_rol(self, rol: str, evento: str, datos: dict) -> None:
        mensaje = json.dumps(
            {"evento": evento, "datos": datos},
            default=_serializador,
            ensure_ascii=False,
        )
        for ws in list(self._conexiones.get(rol, set())):
            try:
                await ws.send_text(mensaje)
            except Exception as exc:
                logger.warning(
                    "Error al enviar evento %s a rol %s: %r", evento, rol, exc
                )
                self.desconectar(ws, rol)

    async def broadcast(self, evento: str, datos: dict) -> None:
        for rol in self._conexiones:
            await self.enviar_a_rol(rol, evento, datos)


manager = ConnectionManager()
