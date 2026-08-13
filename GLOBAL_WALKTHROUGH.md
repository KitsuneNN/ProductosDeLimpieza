# GLOBAL_WALKTHROUGH — Sistema Web Catálogo e Inventario (Local de Limpieza)

## 📌 Estado general
- **Fecha:** 2026-08-13
- **Fase:** 🔴 FASE CRÍTICA (infraestructura base)
- **Repo:** github.com/KitsuneNN/ProductosDeLimpieza — rama de trabajo: `chef-master/planificacion`
- **Conexión GitHub:** ✅ SSH deploy key con write access verificada

## 🚦 Línea de tiempo
| Fecha | Evento | Estado |
|-------|--------|--------|
| 2026-08-13 | Conexión SSH + clone + verificación de push | ✅ OK |
| 2026-08-13 | Recepción de requisitos (cuestionario IA central) | ✅ OK |
| 2026-08-13 | Equipo de 5 agentes aprobado por el dueño | ✅ OK |
| 2026-08-13 | ADR-001 ACEPTADO: Next.js 15 (UI) + FastAPI (API) + PostgreSQL + Cloudinary | ✅ OK |
| 2026-08-13 | Deploy: sin cuentas aún → desarrollo local, preparar en FASE FINAL | ✅ OK |
| 2026-08-13 | ARQ-T1: modelo de datos, migración, seed y ERD | ✅ APPROVED (auditoría: migración DDL congelado + test up/down real) |
| 2026-08-13 | ARQ-T2: schemas Pydantic + types TS + contrato API/WS | 🟩 ESPERANDO_APROBACIÓN |

## 🧾 Decisiones clave
- **ADR-001 (ACEPTADO):** Next.js 15 App Router como capa UI (mobile-first) + FastAPI como API y WebSockets + PostgreSQL + Cloudinary (cuenta existente).
- **Flujo Git:** ramas `chef-master/<tarea>`; nada directo a `main` sin aprobación del dueño.
- **Deploy:** sin cuentas por ahora → desarrollo 100% local; FASE FINAL prepara Vercel/Render/Neon.

## 📂 Convenciones del repo
- Rama default: `main` (⚠️ pendiente cambio en GitHub Settings: hoy la default es la rama de test)
- Ramas de trabajo: `chef-master/<tarea>`
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`)
- Secretos: solo en `.env` (referencias en `.env.example`); nunca commitear credenciales
- Idioma de UI, comentarios y docs: español

## ⏳ Próximos pasos
1. Aprobación Chef de ARQ-T2 (contrato API/WS + types TS).
2. En paralelo: B-T1 (scaffold backend), B-T2 (auth), F-T1 (scaffold Next.js).
3. Cambio de rama default en GitHub Settings (acción manual del dueño, pendiente).

## 📐 Auditoría 2026-08-13 (correcciones aplicadas)
- Migración 0001 convertida a DDL congelado autocontenido (independiente del código).
- Maquinaria Alembic completa: `alembic.ini`, `env.py` (DATABASE_URL), `script.py.mako`.
- Seed dialect-agnóstico idempotente con órdenes 1..6.
- Verificación REAL de migración: upgrade → downgrade → upgrade + seed ×2 (exit 0).
- `verify_contract.py` (Regla 5) agregado como verificación permanente del contrato.
- Versiones corregidas en ADR: Next.js 16 (npm: 16.3.0), Python 3.13.
