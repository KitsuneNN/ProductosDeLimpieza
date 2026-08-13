# ADR-001 — Stack tecnológico del sistema

- **Fecha:** 2026-08-13 (v2)
- **Estado:** ✅ ACEPTADO por el dueño del proyecto
- **Decisor:** Dueño del proyecto + Chef Master 👨‍🍳

## Contexto
Proyecto desde cero (repo vacío): sistema web de catálogo e inventario para un local de
productos de limpieza. Mobile-first para clientes, panel admin responsive, tiempo real
(aviso sonoro + sincronización de stock), transacciones seguras de inventario.
La IA central propuso un stack inicial; el dueño ajustó el framework frontend: **Next.js
en lugar de Vite**, manteniendo FastAPI como API.

## Decisión
| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| Frontend (UI) | **Next.js 16 (App Router)** + TypeScript + Tailwind CSS | Elegido por el dueño (en reemplazo de Vite). Capa de interfaz mobile-first, componentes cliente (CSR tras login). Verificado: v16.3.0 en npm |
| UI kit | Componentes estilo shadcn/ui adaptados (botones ≥44px, alto contraste) | Usabilidad táctil y con guantes (requisito 9.8) |
| Backend (API) | **FastAPI (Python 3.13)** + Uvicorn | Alta velocidad, WebSockets nativos para tiempo real (aviso sonoro, sincronización de stock) |
| Comunicación | REST (JSON) + **WebSocket** (`solicitud.creada`, `solicitud.pagada`, `stock.actualizado`) + fallback polling | Cliente Next.js consume la API de FastAPI directamente; proxy `/api` en dev via rewrites |
| DB | PostgreSQL + SQLAlchemy 2.x (async) + Alembic | Transacciones ACID seguras para inventario |
| Hosting DB | Neon o Railway (a definir en FASE FINAL; desarrollo local primero) | Postgres administrado; aún sin cuentas creadas |
| Auth | JWT (email+password, bcrypt) | Roles cliente/admin; sin servicios externos |
| Imágenes | Cloudinary (cuenta existente) + fallback local del backend | Optimización para gama media; sin bloqueo |
| Testing | pytest (backend, lógica stock ≥80%) + Vitest (componentes) + Playwright (E2E) | La lógica crítica vive en Python |
| CI/CD | GitHub Actions → Vercel (Next.js) / Render (FastAPI) — FASE FINAL | Sin cuentas de deploy aún; desarrollo local primero |
| Gestor | pnpm (frontend) / pip + venv (backend) | Determinista y simple |

## Decisiones del dueño registradas en esta sesión
1. **Next.js en lugar de Vite** (revoca la recomendación original de la IA central).
2. **Arquitectura B: Next.js como UI + FastAPI como API** — se conserva Python para
   negocio y tiempo real; Next.js NO implementa endpoints de negocio (solo proxy de dev).
3. **Cloudinary:** cuenta existente — credenciales se solicitan al llegar a B-T3.
4. **Deploy:** sin cuentas todavía → desarrollo 100% local; FASE FINAL prepara
   Vercel/Render/Neon.

## Consecuencias
- Dos codebases coordinadas por un **contrato API/WS congelado** (`docs/API_CONTRACT.md`,
  `docs/WS_EVENTS.md`) antes del trabajo en paralelo (Regla 5).
- CORS: FastAPI debe aceptar el origen de Next.js en dev (localhost:3000) y prod.
- El backend es la única fuente de verdad de stock y etiquetas (el frontend nunca calcula).
- Next.js se usa con componentes cliente en las zonas autenticadas; la landing "/" puede
  ser estática (SEO no crítico: app tras login).

## Estado
- [x] Stack general aprobado por el dueño
- [x] Cloudinary: cuenta existente
- [x] Deploy: sin cuentas — local primero, preparar en FASE FINAL
