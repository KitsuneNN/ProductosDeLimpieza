# WALKTHROUGH — 📐 Arquitecto

## [2026-08-13] - Auditoría Chef + correcciones de ARQ-T1
### ✅ Implementado
- Migración 0001 reescrita con DDL congelado y autocontenido (sin depender del código)
- `alembic.ini`, `alembic/env.py` (lee DATABASE_URL) y `alembic/script.py.mako` creados
- `seed.py` refactorizado: dialect-agnóstico, idempotente, órdenes 1..6
- `usuario.email`: eliminado `index=True` redundante (unique ya indexa)

### 🧪 Verificación
- Ruta/comando: `cd backend && DATABASE_URL=sqlite:////tmp/arq_test.db .venv/bin/python -m alembic upgrade head` → `downgrade base` → `upgrade head` + seed ×2
- Pasos: 1) upgrade crea 6 tablas 2) downgrade las elimina (rollback) 3) upgrade repetible 4) seed ×2 → 6 categorías, 1 config, umbral=5, órdenes 1..6
- Resultado: exit 0 ✅

### ⏳ Estado
✅ APPROVED (Chef)

## [2026-08-13] - ARQ-T2: Schemas Pydantic + Types TS + Contratos API/WS
### ✅ Implementado
- Archivos: `backend/app/schemas/*.py` (common, auth, categoria, producto, solicitud, configuracion, catalogo), `frontend/src/types/*.ts` (9 archivos espejo), `docs/API_CONTRACT.md`, `docs/WS_EVENTS.md`, `backend/scripts/verify_contract.py`
- 27 schemas/paquetes con espejo TS exacto (snake_case, opcionalidad `?` ⇔ default)
- Wire-format definido y verificado: montos Decimal → número en JSON
- `ProductoClientePublic` SIN `stock_actual` (solo etiqueta `disponibilidad`) — requisito 3.5
- 409 de pago con `faltantes` (FaltantesResponse) — sin descuentos parciales
- 4 eventos WS definidos: solicitud.creada (admin), solicitud.pagada, solicitud.cancelada, stock.actualizado (clientes, solo etiquetas)

### 🧪 Verificación
- Ruta/comando: `cd backend && .venv/bin/python scripts/verify_contract.py`
- Pasos:
  1. 27 pares Pydantic↔TS con campos y opcionalidad idénticos
  2. 4 aliases Literal coincidentes
  3. Wire-format de montos como número
  4. Sanity: registro válido OK; password corta, email inválido y cantidad 0 rechazados
- Resultado: exit 0 ✅
- Bug corregido durante verificación (Debug Protocol): `ModuleNotFoundError: app` en el script → fix `sys.path.insert` → re-verificación exitosa

### ⏳ Estado
ESPERANDO_APROBACIÓN_CHEF

## [2026-08-13] - ARQ-T1: Modelo de datos, migración y estados
### ✅ Implementado
- Archivos: `backend/app/models/*.py`, `backend/alembic/versions/0001_initial.py`, `backend/app/db/seed.py`, `docs/ERD.md`
- 6 tablas con constraints críticos: stock ≥ 0, cantidades > 0, estados y roles con CHECK, FKs RESTRICT, UNIQUE (solicitud_id, producto_id)
- Migración 0001 con rollback — Regla 12
- Seed idempotente: 6 categorías base + `umbral_pocas_unidades=5`
- ERD en Mermaid en `docs/ERD.md`

### 🧪 Verificación
- Ruta/comando: `cd backend && .venv/bin/python -c "..."` (SQLAlchemy mock engine) + verificación REAL posterior (ver entrada de auditoría)
- Bug corregido durante verificación: `String` sin importar en `solicitud.py` → fix mínimo y re-verificación

### ⏳ Estado
✅ APPROVED (Chef)
