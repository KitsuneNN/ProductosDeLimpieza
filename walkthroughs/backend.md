# WALKTHROUGH — 🔧 Backend

## [2026-08-13] - B-T2..B-T6: API completa
### ✅ Implementado
- **B-T2 Auth:** `core/security.py` (bcrypt + PyJWT), `core/deps.py` (get_current_user / require_admin), `api/auth.py` (registro/login/me), `db/seed_admin.py` (admin idempotente)
- **B-T3 Productos:** `api/products_admin.py` (CRUD admin + estado + imagen), `services/images.py` (Cloudinary con fallback local `/uploads` + validaciones)
- **B-T4 Catálogo:** `api/catalogo.py` (categorías + catálogo paginado/filtros), `services/availability.py` (etiquetas contra umbral)
- **B-T5 Solicitudes:** `api/requests.py` (cliente + admin), `services/requests.py` (crear con snapshot de precios, cancelar con máquina de estados)
- **B-T6 Pago+WS:** `services/checkout.py` (SELECT FOR UPDATE, 409 con faltantes, descuento solo al pagar), `ws/manager.py` + `ws/route.py` (broadcast por rol, serializador Decimal→float), `api/config_admin.py` (umbral configurable con re-etiquetado en vivo)

### 🧪 Verificación
- `pytest -q` → **28 passed** · cobertura services **95%**
- E2E en vivo (PostgreSQL 17 real + WebSockets): **11/11** — ver walkthrough de QA
- Bugs corregidos vía Debug Protocol: dominio `.local` inválido en admin · Decimal en payloads WS
- Migración + seed sobre PostgreSQL verificado; constraint de stock negativo probada contra la BD

### ⏳ Estado
ESPERANDO_APROBACIÓN_CHEF

## [2026-08-13] - B-T1: Scaffold FastAPI + conexión DB + healthcheck
### ⏳ Estado
✅ APPROVED (verificado en turno anterior)
