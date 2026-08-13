# ADR-001 — Stack tecnológico del sistema

- **Fecha:** 2026-08-13
- **Estado:** 🟡 PROPUESTO — pendiente de confirmación final del dueño del proyecto
- **Decisor:** Chef Master 👨‍🍳 + confirmación del usuario

## Contexto
Proyecto desde cero (repo vacío): sistema web de catálogo e inventario para un local de
productos de limpieza. Mobile-first para clientes, panel admin responsive, tiempo real
(aviso sonoro + sincronización de stock), transacciones seguras de inventario.
La IA central del proyecto propuso un stack marcado como RECOMENDACIÓN; este ADR lo
formaliza para aprobación.

## Decisión
| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS | Rápido, CSR ideal para UX tipo app, bundle liviano para gama media |
| UI | Componentes estilo shadcn/ui adaptados (botones ≥44px, alto contraste) | Usabilidad táctil y con guantes (requisito 9.8) |
| Backend | FastAPI (Python 3.12) + Uvicorn | Alto rendimiento, WebSockets nativos para tiempo real |
| DB | PostgreSQL + SQLAlchemy 2.x (async) + Alembic | Transacciones ACID seguras para inventario |
| Hosting DB | Neon o Railway | Postgres administrado, plan gratuito para arrancar |
| Auth | JWT (email+password, bcrypt) | Roles cliente/admin; sin servicios externos |
| Tiempo real | WebSocket (broadcast de eventos) + fallback polling 10s | Aviso sonoro instantáneo; resiliencia ante proxies |
| Imágenes | Cloudinary (upload + URLs optimizadas). **Fallback MVP:** storage local del backend | Optimización para gama media; sin bloqueo si no hay cuenta |
| Testing | pytest (backend, lógica stock ≥80%) + Vitest (componentes) + Playwright (E2E) | La lógica crítica vive en Python; E2E cubre el flujo de oro |
| CI/CD | GitHub Actions → Vercel (frontend) / Render (backend) | Deploy simple, WS soportado en Render |
| Gestor | pnpm (frontend) / pip + venv (backend) | Rápido y determinista |

## Decisiones que se apartan (levemente) de la recomendación original
1. **pytest para la lógica de negocio** (la recomendación decía Vitest): la lógica de
   stock vive en el backend Python, por lo que se testea donde se ejecuta. Vitest se usa
   para componentes React.
2. **Fallback local para imágenes**: el MVP no debe bloquearse si la cuenta de Cloudinary
   no está lista; la integración se diseña tras una interfaz `ImagesService` intercambiable.

## Consecuencias
- El backend es la única fuente de verdad de stock y etiquetas (el frontend nunca calcula).
- El contrato API/WS debe quedar congelado en `docs/API_CONTRACT.md` antes de que
  Frontend y Backend trabajen en paralelo (Regla 5).
- Se requieren cuentas (gratuitas) en: GitHub Actions (incluida), Vercel, Render,
  Neon/Railway, Cloudinary (opcional en MVP).

## Pendiente de confirmación
- [ ] Stack general aprobado por el dueño
- [ ] Cloudinary: ¿cuenta existente o fallback local primero?
- [ ] Cuentas de deploy (Vercel/Render/Neon): ¿existentes o se preparan en fase final?
