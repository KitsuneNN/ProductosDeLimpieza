# GLOBAL_WALKTHROUGH — Sistema Web Catálogo e Inventario (Local de Limpieza)

## 📌 Estado general
- **Fecha:** 2026-08-13
- **Fase:** 🟡/🟢 FASE ALTA COMPLETADA — frontend funcional en preview; restan QA-T2 (Vitest), QA-T3 (Playwright) y FASE FINAL (deploy/docs)
- **Repo:** github.com/KitsuneNN/ProductosDeLimpieza — rama de trabajo: `chef-master/planificacion`
- **Previews vivos:** API server (:8000) + Frontend Next.js (:3000)

## 🚦 Línea de tiempo
| Fecha | Evento | Estado |
|-------|--------|--------|
| 2026-08-13 | Conexión SSH + clone + verificación de push | ✅ |
| 2026-08-13 | Requisitos recibidos + equipo de 5 agentes aprobado | ✅ |
| 2026-08-13 | ADR-001 ACEPTADO: Next.js 16 (UI) + FastAPI (API) + PostgreSQL + Cloudinary | ✅ |
| 2026-08-13 | ARQ-T1 (modelo de datos) y ARQ-T2 (contratos) | ✅ (2 auditorías) |
| 2026-08-13 | B-T1..B-T6: API completa (auth, productos, catálogo, solicitudes, pago+WS) | ✅ E2E 11/11 |
| 2026-08-13 | F-T1..F-T4: Next.js 16 completo (cliente + admin + QR) | ✅ |
| 2026-08-13 | QA-T1: pytest 28 tests, services 95% | ✅ |
| 2026-08-13 | Fix preview en blanco (allowedDevOrigins) | ✅ |
| 2026-08-13 | Fix catálogo inaccesible: entorno reconstruido + admin puede ver catálogo | ✅ |
| 2026-08-13 | **MERGE a main**: primera entrega completa en la rama principal | ✅ |

## 🧪 Cómo probar el sistema ahora (preview Arena)
1. Abrir el preview **Frontend** (puerto 3000).
2. **Admin:** entrar con `admin@limpieza.com` / `Admin#Limpieza2026` (solo dev) → panel con sonido.
3. **Cliente:** crear cuenta desde "Crear mi cuenta" (o registrar por API) → catálogo con etiquetas → carrito → enviar pedido.
4. Con las dos sesiones abiertas (admin en una pestaña, cliente en otra) se ve el flujo completo en vivo: sonido en el admin + etiquetas que cambian solas en el cliente.
5. Para el sonido: hacer clic una vez en el panel (los navegadores exigen interacción antes de sonar).

## 🔑 Credenciales de desarrollo (SOLO entorno local/sandbox)
- Admin: `admin@limpieza.com` / `Admin#Limpieza2026`
- Generar otro admin: `cd backend && ADMIN_EMAIL=... ADMIN_PASSWORD=... .venv/bin/python -m app.db.seed_admin`
- Base de datos del sandbox: PostgreSQL 17 local (usuario `limpieza`)

## 🧾 Decisiones clave
- ADR-001 aceptado (Next.js 16 UI + FastAPI API + PostgreSQL + Cloudinary con fallback local).
- Flujo Git: ramas `chef-master/<tarea>`; nada directo a `main` sin aprobación.
- Deploy: sin cuentas aún → preparar en FASE FINAL (Vercel/Render/Neon).

## 🐛 Bugs reales encontrados por las etapas de verificación (y corregidos)
1. Migración acoplada al código (DDL congelado + verificador de paridad permanente).
2. `email-validator` rechazaba el dominio `.local` del admin (login imposible) → `.com`.
3. Broadcast WS con `Decimal` sin serializar → serializador central en el manager.
4. Endpoint WS bajo `/api/ws` en vez de `/ws` (contrato) → movido.
5. ERD Mermaid inválido · schemas faltantes del contrato · `.gitignore` débil · paridad modelos/migración.
6. **Página en blanco en el preview**: Next.js 16 bloqueaba los chunks JS y el HMR (403) cuando el `Origin` es el host del preview (`*.e2b.app`) → `allowedDevOrigins` en `next.config.ts` + restart. Verificado: chunks 403→200, HMR con handshake OK, WS vía proxy OK.
7. `viewport.maximumScale=1` (bloqueaba zoom → violación a11y) → eliminado.
8. Fallback WS a `ws://localhost:8000` (muerto en el navegador del usuario) → ruta relativa `/ws` única + `NEXT_PUBLIC_WS_URL` opcional.
9. Next 16 ya no corre `tsc` en `next build` → script `npm run typecheck` agregado (0 errores).
10. **Catálogo "inaccesible"**: el sandbox se reinicia entre turnos → PostgreSQL, `.venv`, `node_modules` y los servidores desaparecen. Solución: `scripts/iniciar_dev.sh` ahora reconstruye TODO (instala PG si falta, migra, siembra, admin, deps front). Además: el admin ya puede recorrer `/cliente/*` (vista cliente) y hay botón "Ver catálogo" en su panel.
11. localStorage blindado (try/catch) en `lib/auth.ts` y `lib/cart.ts` (iframes sandboxeados lanzan SecurityError).
12. Permisos SSH restaurados por el snapshot (0644) → OpenSSH ignoraba la llave; `iniciar_dev.sh` ahora los corrige (chmod 600) y re-registra el remoto git si falta.

## 📂 Convenciones del repo
- Rama default: `main` (⚠️ pendiente cambio en GitHub Settings — la default sigue siendo la rama de test)
- Ramas de trabajo: `chef-master/<tarea>` · Commits Conventional Commits
- Secretos solo en `.env` · Idioma español en UI/docs/comentarios
- Verificadores permanentes: `backend/scripts/verify_contract.py` (Regla 5) y `verify_migration_parity.py`

## ⏳ Próximos pasos
1. Aprobación del dueño del frontend (F-T2/F-T3/F-T4 en preview).
2. QA-T2 (Vitest) + QA-T3 (Playwright E2E).
3. FASE FINAL: cuentas de deploy + CI/CD + manual del admin.
4. Cambio de rama default en GitHub Settings (manual del dueño).
