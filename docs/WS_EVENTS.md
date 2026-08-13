# WS EVENTS — Contrato de WebSocket (ARQ-T2)

**Autor:** 📐 Arquitecto · **Estado:** ESPERANDO_APROBACIÓN_CHEF
**Implementación prevista:** B-T6 (`backend/app/ws/manager.py`) · **Consumo:** F-T2/F-T3

## Conexión

| Tema | Valor |
|------|-------|
| Endpoint | `ws://localhost:8000/ws?token=<access_token>` (dev) / `wss://...` (prod) |
| Auth | Token JWT en query param (los navegadores no mandan headers en WS) |
| Cierre | Código 4401 = token inválido/expirado → el cliente re-loguea |
| Reintentos | Backoff exponencial (1s → 2s → 4s → máx 15s) + **fallback polling** cada 10s |

## Eventos (servidor → cliente)

Todos los mensajes tienen la forma `{"evento": "...", "datos": {...}}`.

| Evento | Destinatarios | Cuándo | `datos` |
|--------|---------------|--------|---------|
| `solicitud.creada` | **Solo admins** | Un cliente crea una solicitud pendiente | `{solicitud_id, usuario: {id, nombre}, total, creado_en, resumen: [{producto_id, nombre, cantidad}]}` |
| `solicitud.pagada` | Todos (broadcast) | El admin presiona "Pagado" | `{solicitud_id, usuario_id, pagada_en}` |
| `solicitud.cancelada` | Todos (broadcast) | Una solicitud pendiente se cancela | `{solicitud_id, usuario_id, por: "cliente" | "admin"}` |
| `stock.actualizado` | **Solo clientes** | Cambió el stock de 1+ productos (pago, edición admin) | `{productos: [{producto_id, disponibilidad}]}` — **nunca números** |

### Reglas de oro del canal
- `stock.actualizado` transporta SOLO etiquetas (`disponible|pocas|sin_stock`), jamás stock numérico.
- `solicitud.creada` es el disparador del **aviso sonoro** en la PC del admin (requisito 19.3).

### Ejemplos de payload
```json
{"evento": "solicitud.creada", "datos": {
  "solicitud_id": 12,
  "usuario": {"id": 7, "nombre": "María González"},
  "total": 3850.0,
  "creado_en": "2026-08-13T18:04:11Z",
  "resumen": [{"producto_id": 4, "nombre": "Lavandina 1L", "cantidad": 2}]
}}

{"evento": "stock.actualizado", "datos": {
  "productos": [{"producto_id": 4, "disponibilidad": "pocas"}]
}}
```

## Fallback polling (si el WS no conecta)
- Clientes: `GET /api/catalogo?page=1&page_size=20` cada 10s para refrescar etiquetas.
- Admin: `GET /api/admin/solicitudes?estado=pendiente` cada 10s (detecta solicitudes nuevas sin WS).

## Eventos cliente → servidor
Ninguno en el MVP. El canal es unidireccional (broadcast). El cliente solo recibe;
cualquier mensaje entrante del cliente se ignora con `{"evento":"error","datos":{"detail":"..."}}`.
