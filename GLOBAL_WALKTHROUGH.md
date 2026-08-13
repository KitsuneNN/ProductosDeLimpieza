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
| 2026-08-13 | ARQ-T1: modelo de datos, migración, seed y ERD | ✅ APPROVED (auditoría: DDL congelado + paridad verificada) |
| 2026-08-13 | ARQ-T2: schemas Pydantic + types TS + contrato API/WS | ✅ APPROVED (30 pares espejo + 4 eventos WS + tsc strict OK) |
| 2026-08-13 | B-T1: scaffold FastAPI + PostgreSQL + healthcheck | 🟩 ESPERANDO_APROBACIÓN (servidor vivo, /api/health 200) |

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
1. Aprobación del dueño de B-T1.
2. En paralelo: B-T2 (auth JWT) y F-T1 (scaffold Next.js).
3. Cambio de rama default en GitHub Settings (acción manual del dueño, pendiente).

## 📐 Auditoría 2026-08-13 — segunda ronda (inspección profunda)
Correcciones aplicadas y verificadas:
- **Paridad modelos ↔ migración**: `rol`, `estado`, `stock_actual`, `orden`, `total` pasaron a `server_default` (antes el `create_all` divergía de Alembic). Nuevo verificador permanente: `backend/scripts/verify_migration_parity.py` → espejo exacto (6 tablas, 33 columnas).
- **ERD**: tipos Mermaid válidos (se eliminaron `decimal(12,2)` y la fila `uk` sin tipo).
- **Schemas faltantes** referenciados por el contrato: `HealthResponse`, `ProductosAdminResponse`, `ConfiguracionesResponse` (Pydantic + TS).
- **Tipos de eventos WS**: nuevo `frontend/src/types/ws.ts` con los 4 eventos; el `verify_contract.py` ahora los exige.
- **.gitignore**: `.env.*` (excepto `.env.example`), `*.db`, `uploads/`.
- **bcrypt**: `LoginRequest.password` limitado a 72 bytes.
- **TypeScript**: `tsc --noEmit --strict` sobre todos los types → 0 errores.
- **PostgreSQL 17 real instalado en el sandbox** (BD `limpieza`): migración + seed + constraint de stock negativo verificados contra el motor de producción; el API server corre contra PostgreSQL real.
