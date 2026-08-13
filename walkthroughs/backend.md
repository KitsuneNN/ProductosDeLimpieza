# WALKTHROUGH — 🔧 Backend

## [2026-08-13] - B-T1: Scaffold FastAPI + conexión DB + healthcheck
### ✅ Implementado
- Archivos: `backend/app/main.py`, `backend/app/core/config.py` (Settings pydantic-settings, .env, CORS), `backend/app/db/session.py` (motor async + get_db), `backend/app/api/health.py` (ping a BD), `backend/app/api/router.py`, `backend/requirements.txt`, `backend/.env.example`
- CORS configurable por `CORS_ORIGINS`; URL async por `DATABASE_URL` (sqlite dev / postgresql+asyncpg prod)
- Alembic `env.py` ahora convierte URLs async→sync para migraciones (sqlite+aiosqlite→sqlite, postgresql+asyncpg→postgresql+psycopg)

### 🧪 Verificación
- Ruta/comando: `cd backend && DATABASE_URL=postgresql+asyncpg://... .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Pasos:
  1. Migración `alembic upgrade head` sobre **PostgreSQL 17 real**: OK
  2. Seed ×2 sobre PostgreSQL: 6 categorías, umbral=5, idempotente
  3. Constraint de negocio probado: INSERT stock=-1 → **rechazado por la BD** (ck_productos_stock_no_negativo)
  4. `GET /` → 200 app info · `GET /api/health` → 200 `{"status":"ok"}` (ping real a PG) · `/docs` → 200 · 404 uniforme `{"detail":"Not Found"}`
- Resultado: exit 0 ✅

### ⏳ Estado
ESPERANDO_APROBACIÓN_CHEF
