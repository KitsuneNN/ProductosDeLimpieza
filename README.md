# 🧼 ProductosDeLimpieza

Sistema web de **catálogo e inventario** para un local de productos de limpieza.

El cliente escanea un **QR**, entra al catálogo, arma un carrito y envía una **solicitud**.
El administrador recibe un **aviso sonoro**, cobra en efectivo y al presionar **"Pagado"**
el stock se descuenta automáticamente y se refleja al instante en los celulares.

> **Regla de oro:** el cliente nunca ve números de stock — solo etiquetas
> (`Disponible` / `Pocas unidades` / `Sin stock`) calculadas contra un
> **umbral configurable por el administrador**.

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend (UI) | Next.js 16 (App Router) + TypeScript + Tailwind CSS — mobile-first |
| Backend (API) | FastAPI (Python 3.13) + Uvicorn — REST + WebSockets |
| Base de datos | PostgreSQL + SQLAlchemy 2.x + Alembic |
| Auth | JWT (email + password), roles `cliente` / `admin` |
| Imágenes | Cloudinary (fallback local) |
| Testing | pytest · Vitest · Playwright |

## Estructura

```
backend/   → API FastAPI: models, schemas, services, ws, alembic, tests
frontend/  → Next.js 16: /cliente/* (mobile-first), /admin/*, types espejo
e2e/       → Playwright (flujo de oro)
docs/      → ERD, contrato API, eventos WS, manuales
```

## Documentación clave

- 📋 [Plan maestro](CHEF_MASTER_PLAN.md) — equipo de agentes y 17 tareas
- 📐 [ERD](docs/ERD.md) — modelo de datos
- 🔌 [Contrato API](docs/API_CONTRACT.md) — endpoints REST
- 📡 [Eventos WS](docs/WS_EVENTS.md) — tiempo real (aviso sonoro, stock en vivo)
- 🗂️ [Checklist de tareas](planificacion/task.md)
- 📖 [Bitácora global](GLOBAL_WALKTHROUGH.md)

## Estado

🟡 **Fase:** CRÍTICA (infraestructura base) · ARQ-T1 ✅ · ARQ-T2 en revisión

## Contribuir (protocolo del equipo)

1. Cada agente declara **File Claims** antes de tocar archivos (`claims/active_claims.yaml`).
2. Types TS ↔ schemas Pydantic van **siempre espejados** — correr
   `cd backend && .venv/bin/python scripts/verify_contract.py`.
3. Commits en Conventional Commits, ramas `chef-master/<tarea>`, nada directo a `main`.
4. Secretos solo en `.env` (ver `.env.example` cuando exista).
