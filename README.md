# 🧼 ProductosDeLimpieza

Sistema web de **catálogo e inventario** para un local de productos de limpieza.

El cliente escanea un **QR**, entra al catálogo, arma un carrito y envía una **solicitud**.
El administrador recibe un **aviso sonoro**, cobra en efectivo y al presionar **"Pagado"**
el stock se descuenta automáticamente y se refleja al instante en los celulares.

> **Regla de oro:** el cliente nunca ve números de stock — solo etiquetas
> (`Disponible` / `¡Pocas unidades!` / `Sin stock`) calculadas contra un
> **umbral configurable por el administrador**.

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend (UI) | Next.js 16 (App Router) + TypeScript + Tailwind CSS v4 — mobile-first |
| Backend (API) | FastAPI (Python 3.13) + Uvicorn — REST + WebSockets |
| Base de datos | PostgreSQL + SQLAlchemy 2.x (async) + Alembic |
| Auth | JWT (email + password, bcrypt), roles `cliente` / `admin` |
| Tiempo real | WebSocket (`solicitud.creada`, `solicitud.pagada`, `stock.actualizado`) + polling de respaldo |
| Imágenes | Cloudinary (cuenta existente) con fallback local `/uploads` |
| Testing | pytest (28 tests, services 95%) · Vitest y Playwright pendientes |

## Estructura

```
backend/    → API FastAPI: models, schemas, services, ws, alembic, tests
frontend/   → Next.js 16: /cliente/* (mobile-first), /admin/*, types espejo
e2e/        → Playwright (pendiente, QA-T3)
docs/       → ERD, contrato API, eventos WS, manuales
plantilla/  → contratos de agentes (Chef)
```

## 🚀 Cómo correrlo en local

### Requisitos
- Python 3.13 + PostgreSQL (o SQLite para dev rápido)
- Node 20+

### Backend (puerto 8000)
```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env            # completar DATABASE_URL y JWT_SECRET
.venv/bin/python -m alembic upgrade head     # migraciones
.venv/bin/python -c "from app.db.seed import seed; from sqlalchemy import create_engine; from sqlalchemy.orm import sessionmaker; seed(sessionmaker(bind=create_engine('postgresql+psycopg://...'))())"  # o vía API
ADMIN_EMAIL=admin@limpieza.com ADMIN_PASSWORD=TuClave .venv/bin/python -m app.db.seed_admin
.venv/bin/uvicorn app.main:app --reload
```

### Frontend (puerto 3000)
```bash
cd frontend
npm install
npm run dev       # proxea /api y /ws al backend vía rewrites
```

### Tests
```bash
cd backend && .venv/bin/python -m pytest -q --cov=app.services
.venv/bin/python scripts/verify_contract.py        # Regla 5: Pydantic ↔ TS
.venv/bin/python scripts/verify_migration_parity.py # migración ↔ modelos
```

## Documentación clave
- 📋 [Plan maestro](CHEF_MASTER_PLAN.md) · 🗂️ [Checklist](planificacion/task.md)
- 📐 [ERD](docs/ERD.md) · 🔌 [Contrato API](docs/API_CONTRACT.md) · 📡 [Eventos WS](docs/WS_EVENTS.md)
- 📖 [Bitácora global](GLOBAL_WALKTHROUGH.md)

## Estado
🟢 **MVP funcional end-to-end** (API + frontend completos). Restan: Vitest, Playwright E2E,
CI/CD y deploy (Vercel/Render/Neon) — FASE FINAL.
