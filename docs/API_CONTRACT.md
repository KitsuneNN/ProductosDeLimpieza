# API CONTRACT — Contrato REST (ARQ-T2)

**Autor:** 📐 Arquitecto · **Estado:** ESPERANDO_APROBACIÓN_CHEF
**Fuente de verdad de payloads:** `backend/app/schemas/*.py` ↔ `frontend/src/types/*.ts` (espejo exacto, Regla 5 — verificado con `backend/scripts/verify_contract.py`)

## Convenciones generales

| Tema | Regla |
|------|-------|
| Base URL dev | `http://localhost:8000/api` (el frontend Next.js la consume vía rewrites `/api/*`) |
| Formato | JSON. Campos en `snake_case`. |
| Montos | Números (`1250.5`). La precisión `Decimal` se mantiene en el servidor. |
| Fechas | ISO 8601 con timezone (`2026-08-13T18:00:00Z`). |
| Auth | Header `Authorization: Bearer <access_token>` (JWT). |
| Errores | Uniformes: `{"detail": "..."}`. El 409 de pago agrega `faltantes` (ver abajo). |
| Paginación | `?page=1&page_size=20` → respuesta con `items`, `page`, `page_size`, `total`. |
| Roles | `cliente` y `admin`. Rutas `/api/admin/**` requieren `Authorization` de admin (si no: 401/403). |
| Idioma de mensajes | Español. |

## Endpoints públicos

| Método | Ruta | Auth | Descripción | 200 → | Errores |
|--------|------|------|-------------|-------|---------|
| GET | `/api/health` | — | Healthcheck (B-T1) | `{"status":"ok"}` | — |
| POST | `/api/auth/registro` | — | Registro de cliente | `TokenResponse` | 400 datos inválidos · 409 email ya registrado |
| POST | `/api/auth/login` | — | Login | `TokenResponse` | 401 credenciales inválidas |

`RegistroRequest`: `{nombre, telefono, email, password}` (password ≥ 8).
`LoginRequest`: `{email, password}`.
`TokenResponse`: `{access_token, token_type: "bearer", usuario: UsuarioPublic}`.

## Endpoints de cliente (requieren JWT de `cliente` o `admin`)

| Método | Ruta | Descripción | 200 → |
|--------|------|-------------|-------|
| GET | `/api/categorias` | Categorías ordenadas | `CategoriasResponse` |
| GET | `/api/catalogo` | Catálogo paginado. Filtros: `?categoria_id=&busqueda=&page=&page_size=` | `CatalogoResponse` |
| GET | `/api/catalogo/{producto_id}` | Detalle de producto | `ProductoClientePublic` |
| POST | `/api/solicitudes` | Crear solicitud | `SolicitudPublic` (estado `pendiente`) |
| GET | `/api/solicitudes/mias` | Mis solicitudes (`?page=&page_size=`) | `SolicitudesResponse` |
| GET | `/api/solicitudes/{id}` | Detalle (solo si es propia) | `SolicitudPublic` |
| POST | `/api/solicitudes/{id}/cancelar` | Cancelar propia (solo si `pendiente`) | `SolicitudPublic` (estado `cancelada`) |

⚠️ **`ProductoClientePublic` NUNCA incluye `stock_actual`** — solo `disponibilidad`
(`disponible` | `pocas` | `sin_stock`) calculada contra `umbral_pocas_unidades`.
Si el JSON de un endpoint de cliente incluye stock numérico → BUG crítico.

`SolicitudCreate`: `{items: [{producto_id, cantidad}]}` (1–50 ítems, cantidad 1–999).

## Endpoints de administración (requieren JWT de `admin`)

| Método | Ruta | Descripción | 200 → |
|--------|------|-------------|-------|
| GET | `/api/admin/productos` | Todos (incluye pausados y stock). `?categoria_id=&busqueda=&page=&page_size=` | `{items: [ProductoAdminPublic], page, page_size, total}` |
| POST | `/api/admin/productos` | Crear producto | `ProductoAdminPublic` |
| GET | `/api/admin/productos/{id}` | Detalle | `ProductoAdminPublic` |
| PUT | `/api/admin/productos/{id}` | Edición parcial (campos presentes) | `ProductoAdminPublic` |
| PATCH | `/api/admin/productos/{id}/estado` | Activar/pausar `{estado}` | `ProductoAdminPublic` |
| DELETE | `/api/admin/productos/{id}` | Eliminar (409 si tiene historial — FK RESTRICT) | `204` |
| POST | `/api/admin/productos/{id}/imagen` | Upload `multipart/form-data` (campo `archivo`) → Cloudinary con fallback local | `ProductoAdminPublic` (con `imagen_url`) |
| GET | `/api/admin/solicitudes` | Todas. `?estado=&page=&page_size=` | `SolicitudesAdminResponse` |
| GET | `/api/admin/solicitudes/{id}` | Detalle con usuario | `SolicitudAdminPublic` |
| POST | `/api/admin/solicitudes/{id}/pagar` | **Pago: descuenta stock transaccionalmente** | `PagoResponse` |
| POST | `/api/admin/solicitudes/{id}/cancelar` | Cancelar cualquier solicitud pendiente | `SolicitudAdminPublic` |
| GET | `/api/admin/config` | Toda la configuración | `{items: [ConfiguracionPublic]}` |
| GET | `/api/admin/config/umbral-pocas-unidades` | Umbral actual | `UmbralResponse` |
| PUT | `/api/admin/config/umbral-pocas-unidades` | Cambiar umbral `{valor: "3"}` | `UmbralResponse` |

### Pago — `POST /api/admin/solicitudes/{id}/pagar`

- Transacción con `SELECT ... FOR UPDATE`: si algún producto no alcanza → **409**:
```json
{
  "detail": "Stock insuficiente para completar la solicitud",
  "faltantes": [
    {"producto_id": 4, "nombre": "Lavandina 1L", "solicitado": 3, "disponible": 1}
  ]
}
```
- No se descuenta NADA parcial. El admin corrige stock o cancela la solicitud.
- Éxito → `PagoResponse`: `{solicitud_id, estado: "pagada", total, pagada_en, unidades_descontadas}`
  + broadcast WS (`solicitud.pagada`, `stock.actualizado`).
- Pagar una solicitud ya `pagada` → 409; ya `cancelada` → 409.

### Errores estándar
| Código | Caso |
|--------|------|
| 401 | Token ausente/expirado/inválido |
| 403 | Rol insuficiente (ej. cliente en `/api/admin/**`) |
| 404 | Recurso inexistente o no visible para el rol |
| 409 | Conflicto de estado (pagar ya pagada, email duplicado, stock insuficiente) |
| 422 | Payload inválido (validación Pydantic) |

## Ejemplo: flujo de oro en llamadas
1. `POST /api/auth/login` → token
2. `GET /api/catalogo?categoria_id=1&page=1&page_size=20` → items con `disponibilidad`
3. `POST /api/solicitudes` `{items:[{producto_id: 4, cantidad: 2}]}` → solicitud `pendiente`
4. (admin) `POST /api/admin/solicitudes/12/pagar` → `PagoResponse` + WS broadcast
5. `GET /api/catalogo` → el producto 4 ahora refleja la nueva etiqueta
