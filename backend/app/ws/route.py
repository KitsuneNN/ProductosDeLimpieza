# -*- coding: utf-8 -*-
"""Endpoint WebSocket /ws?token=<jwt> (B-T6).

Los navegadores no pueden enviar headers en WebSocket, por eso el token viaja
como query param. Cierre con código 4401 = token inválido/expirado.
"""
import json

import jwt as pyjwt
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.ws.manager import _serializador, manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, token: str | None = Query(default=None)
) -> None:
    if not token:
        await websocket.close(code=4401)
        return
    try:
        payload = decode_access_token(token)
    except pyjwt.InvalidTokenError:
        await websocket.close(code=4401)
        return
    rol = payload.get("rol", "cliente")
    await websocket.accept()
    await manager.conectar(websocket, rol)
    # Confirmación de conexión (permite al frontend mostrar estado "EN VIVO")
    await websocket.send_text(
        json.dumps(
            {"evento": "conexion.establecida", "datos": {"rol": rol}},
            default=_serializador,
            ensure_ascii=False,
        )
    )
    try:
        while True:
            # Canal unidireccional: el MVP no procesa mensajes del cliente.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.desconectar(websocket, rol)
