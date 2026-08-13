# PLAN MAESTRO — Sistema Web de Catálogo e Inventario para Local de Limpieza

## RESUMEN
Herramienta digital para un local de productos de limpieza: el **cliente escanea un QR**,
entra al catálogo, arma un carrito y envía una **solicitud**; el **administrador** recibe un
**aviso sonoro**, cobra en efectivo y al presionar **"Pagado"** el stock se descuenta
automáticamente y se refleja **al instante** en los celulares de los clientes.

**Regla de oro del dominio:** el cliente NUNCA ve números exactos de stock — solo etiquetas
de disponibilidad ("Disponible", "Pocas unidades", "Sin stock") calculadas contra un
**umbral configurable por el admin**.

## STACK TECNOLÓGICO (ACEPTADO — ver decisiones/ADR-001)
- **Frontend (UI):** Next.js 15 (App Router) + TypeScript + Tailwind CSS — mobile-first absoluto, componentes cliente
- **Backend (API):** FastAPI (Python) + Uvicorn — API REST + WebSockets nativos
- **Comunicación:** REST JSON + WS (`solicitud.creada`, `solicitud.pagada`, `stock.actualizado`) + fallback polling; proxy `/api` en dev
- **Base de datos:** PostgreSQL (Neon/Railway en FASE FINAL) + SQLAlchemy 2.x + Alembic (migraciones)
- **Auth:** JWT (email + password), roles `cliente` / `admin`
- **Imágenes:** Cloudinary (cuenta existente) con fallback local del backend
- **Testing:** pytest (backend) + Vitest (frontend) + Playwright (E2E)
- **CI/CD (FASE FINAL):** GitHub Actions → Vercel (Next.js) / Render (FastAPI) / Neon (DB) — desarrollo local primero

## ESTRUCTURA DEL PROYECTO
```
ProductosDeLimpieza/
├── backend/                        # FastAPI (API + negocio + WS)
│   ├── app/
│   │   ├── api/          # routers REST
│   │   ├── core/         # config, security, auth (JWT)
│   │   ├── db/           # sesión, seed
│   │   ├── models/       # SQLAlchemy          ← 📐 Arquitecto
│   │   ├── schemas/      # Pydantic             ← 📐 Arquitecto
│   │   ├── services/     # lógica de negocio    ← 🔧 Backend
│   │   └── ws/           # websockets broadcast ← 🔧 Backend
│   ├── tests/                                   ← ⚡ QA
│   └── alembic/                                 ← 🔧 Backend (ejecuta migraciones)
├── frontend/                       # Next.js 15 (UI mobile-first)
│   ├── src/
│   │   ├── app/          # App Router: /, /cliente/*, /admin/*  ← 🎨 Frontend
│   │   ├── components/
│   │   ├── types/        # espejo TS de schemas ← 📐 Arquitecto
│   │   ├── hooks/
│   │   ├── lib/          # api client (FastAPI), auth, ws       ← 🎨 Frontend
│   │   └── styles/
│   ├── public/           # sonido de aviso, assets
│   ├── next.config.ts    # rewrites de dev hacia FastAPI
│   └── package.json
├── e2e/                                          ← ⚡ QA
├── docs/                # ERD, contratos, manuales
├── .github/workflows/                            ← 🚀 DevOps
├── plantilla/           # contratos de agentes (Chef)
├── walkthroughs/        # bitácoras de agentes (Chef)
├── planificacion/       # task.md (Chef)
├── decisiones/          # ADRs (Chef)
├── claims/              # file claims (Chef)
├── CHEF_MASTER_PLAN.md
└── GLOBAL_WALKTHROUGH.md
```

## EQUIPO DE AGENTES
| Agente | Rol | Responsabilidad principal |
|--------|-----|---------------------------|
| 📐 Arquitecto | Datos y contratos | Modelo de datos, schemas Pydantic, types TS, contrato API/WS, ERD |
| 🔧 Backend | API y negocio | FastAPI, auth JWT, CRUD, transacciones de stock, WebSockets, seed |
| 🎨 Frontend | UI mobile-first (Next.js) | Pantallas cliente y admin, UX táctil, sonido, a11y, integración API/WS |
| ⚡ QA | Testing | pytest (lógica stock ≥80%), Vitest, Playwright E2E |
| 🚀 DevOps | Deploy y CI/CD | GitHub Actions, Vercel, Render, Neon, secretos, CORS (FASE FINAL) |

## REGLAS DE NEGOCIO CRÍTICAS (fuente de verdad)
1. Stock **nunca negativo** → CHECK en BD + validación transaccional al pagar.
2. Descuento de stock **solo** al presionar "Pagado" (confirmación humana).
3. Cliente ve **solo etiquetas** (`disponible` | `pocas` | `sin_stock`) — jamás números.
4. Umbral de "Pocas unidades" **configurable por admin** (default: 5).
5. Si al pagar falta stock → **409** con detalle de faltantes (no se descuenta parcial).
6. Estados de Solicitud: `pendiente → pagada | cancelada` (cancelación: cliente si pendiente, admin siempre).
7. Aviso sonoro característico en PC del admin ante nueva solicitud.

## TAREAS

### 🔴 FASE CRÍTICA (infraestructura base)

#### 📐 ARQ-T1 — Modelo de datos, migración y estados
- **Archivos:** `backend/app/models/*.py`, `backend/alembic/versions/0001_*.py`, `backend/app/db/seed.py`, `docs/ERD.md`
- **Duración estimada:** 1 día · **Dependencias:** ninguna
- **Instrucciones:**
  1. Tablas: `usuarios` (id, nombre, telefono, email, password_hash, rol, creado_en), `categorias` (id, nombre, orden), `productos` (id, categoria_id, nombre, descripcion, precio, stock_actual, imagen_url, estado activo|pausado), `solicitudes` (id, usuario_id, estado, total, creado_en, pagada_en), `detalle_solicitud` (id, solicitud_id, producto_id, cantidad, precio_unitario), `configuracion` (clave PK, valor)
  2. Constraints: `stock_actual >= 0` (CHECK), FKs con `ON DELETE RESTRICT`, estados con CHECK
  3. Migración Alembic con **rollback** + seed idempotente de categorías (detergentes, lavandinas, desinfectantes, esponjas y trapos, aromatizantes, otros) y configuración por defecto (`umbral_pocas_unidades=5`)
  4. Diagrama ERD en Mermaid en `docs/ERD.md`
- **Criterios:** ✅ migración up/down sin errores · ✅ stock no negativo a nivel BD · ✅ seed idempotente · ✅ Regla 5 (Pydantic ↔ TS espejo exacto, viene en ARQ-T2)

#### 📐 ARQ-T2 — Contrato API + eventos WebSocket + types TS
- **Archivos:** `backend/app/schemas/*.py`, `frontend/src/types/*.ts`, `docs/API_CONTRACT.md`, `docs/WS_EVENTS.md`
- **Duración estimada:** 1 día · **Dependencias:** ARQ-T1
- **Instrucciones:**
  1. Schemas Pydantic v2 de todas las entidades + payloads request/response + errores uniformes `{detail}`
  2. Types TS **idénticos campo a campo** (Regla 5)
  3. Contrato REST completo: endpoints cliente vs admin, códigos de error, paginación
  4. Eventos WS: `solicitud.creada`, `solicitud.pagada`, `stock.actualizado` con payloads de ejemplo
- **Criterios:** ✅ endpoint catálogo cliente **sin** campo de stock numérico · ✅ permisos por rol documentados · ✅ handoff listo para Backend y Frontend

#### 🔧 B-T1 — Scaffold backend + conexión DB
- **Archivos:** `backend/**` (main, config, db, .env.example, requirements, alembic env)
- **Duración estimada:** 1 día · **Dependencias:** ARQ-T1
- **Instrucciones:** 1) FastAPI+Uvicorn por capas 2) SQLAlchemy async + `.env.example` (DATABASE_URL, JWT_SECRET, CLOUDINARY_*) 3) aplicar migración + seed + `GET /api/health`
- **Criterios:** ✅ `uvicorn app.main:app` arranca · ✅ `/api/health` → 200 · ✅ migración aplicada y seed cargado

#### 🔧 B-T2 — Auth JWT + roles
- **Archivos:** `backend/app/core/security.py`, `backend/app/api/auth.py`, dependencias `get_current_user` / `require_admin`
- **Duración estimada:** 1 día · **Dependencias:** B-T1, ARQ-T2
- **Instrucciones:** 1) registro cliente (nombre, teléfono, email, password) + login JWT 2) seed admin inicial documentado 3) guard de rol en rutas admin
- **Criterios:** ✅ bcrypt, nunca texto plano · ✅ token con expiración validada · ✅ ruta admin sin rol → 403

#### 🎨 F-T1 — Scaffold frontend Next.js + rutas + tema
- **Archivos:** `frontend/**` (create-next-app, TS, Tailwind, App Router, api client, rewrites, tema)
- **Duración estimada:** 1 día · **Dependencias:** ARQ-T2 (types)
- **Instrucciones:** 1) create-next-app + TS + Tailwind + ESLint 2) App Router: `/` landing QR, `/cliente/*`, `/admin/*` (componentes cliente) 3) API client tipado con types compartidos + manejo de token 4) rewrites `/api/* → localhost:8000` en dev 5) tema claro, botones ≥44px, alto contraste
- **Criterios:** ✅ `pnpm build` exit 0 · ✅ verificado en 360px · ✅ Regla 13 (focus visible, aria-labels)

### 🟡 FASE ALTA (funcionalidad core)

#### 🔧 B-T3 — CRUD productos + imágenes (admin)
- **Archivos:** `backend/app/api/products.py`, `backend/app/services/images.py`
- **Dependencias:** B-T2 · **Duración estimada:** 1 día
- **Instrucciones:** CRUD admin (crear/editar/pausar/activar/eliminar), upload imagen a Cloudinary (fallback local `/uploads`), listados por categoría
- **Criterios:** ✅ solo admin muta · ✅ URL de imagen optimizada en respuesta · ✅ sin stock numérico en endpoints de cliente

#### 🔧 B-T4 — Catálogo cliente + etiquetas de disponibilidad
- **Archivos:** `backend/app/api/catalog.py`, `backend/app/services/availability.py`
- **Dependencias:** B-T3 · **Duración estimada:** 1 día
- **Instrucciones:** GET catálogo por categoría + búsqueda case-insensitive por nombre; campo derivado `disponibilidad: disponible|pocas|sin_stock` contra umbral de `configuracion`
- **Criterios:** ✅ nunca exponer número · ✅ umbral default 5 · ✅ respuesta <300ms con catálogo típico

#### 🔧 B-T5 — Solicitudes (crear, listar, estados)
- **Archivos:** `backend/app/api/requests.py`, `backend/app/services/requests.py`
- **Dependencias:** B-T4 · **Duración estimada:** 1 día
- **Instrucciones:** crear solicitud con detalles (valida productos activos), listar "mis solicitudes" (cliente) / todas (admin), detalle, cancelar (reglas de estado)
- **Criterios:** ✅ máquina de estados respetada · ✅ totales calculados server-side · ✅ payload validado (cantidades ≥1)

#### 🔧 B-T6 — Pago transaccional + umbrales + broadcast WS
- **Archivos:** `backend/app/services/checkout.py`, `backend/app/ws/manager.py`, `backend/app/api/config.py`
- **Dependencias:** B-T5 · **Duración estimada:** 1-2 días
- **Instrucciones:**
  1. `POST /api/admin/requests/{id}/pagar`: transacción con `SELECT ... FOR UPDATE`, valida stock ≥ cantidades → si falta → **409 con faltantes**
  2. Descuenta stock, marca `pagada` + `pagada_en`
  3. Broadcast WS `solicitud.pagada` + `stock.actualizado`
  4. `GET/PUT /api/admin/config` (umbral_pocas_unidades y demás)
- **Criterios:** ✅ concurrencia segura (2 pagos simultáneos no dejan stock negativo) · ✅ broadcast <1s · ✅ cambio de umbral re-etiqueta en vivo

#### 🎨 F-T2 — Pantallas cliente (mobile-first)
- **Archivos:** `frontend/src/app/cliente/**` (login, registro, catálogo, detalle, carrito, mis solicitudes)
- **Dependencias:** B-T4, B-T5, B-T6 · **Duración estimada:** 2-3 días
- **Instrucciones:** grid de productos con fotos grandes, filtros por categoría, búsqueda, badges de etiquetas (verde/amarillo/gris), carrito persistente (localStorage), envío de solicitud con confirmación
- **Criterios:** ✅ solo etiquetas, nunca números · ✅ catálogo <2s tras login · ✅ táctil (botones ≥44px) · ✅ WS actualiza badges en vivo

#### 🎨 F-T3 — Panel admin + aviso sonoro
- **Archivos:** `frontend/src/app/admin/**` (dashboard, productos CRUD, solicitudes, configuración, QR)
- **Dependencias:** B-T3, B-T6, F-T1 · **Duración estimada:** 2-3 días
- **Instrucciones:** dashboard con solicitudes entrantes destacadas, CRUD productos con upload de foto, detalle de solicitud con botón grande "Pagado" + confirmación, configuración de umbrales, **sonido característico** al recibir `solicitud.creada` (más badge persistente), responsive PC/celular
- **Criterios:** ✅ sonido reproducible sin interacción previa · ✅ botón "Pagado" prominente con confirmación · ✅ Regla 13 en todos los controles

### 🟢 FASE NORMAL (features adicionales)

#### 🎨 F-T4 — QR imprimible
- **Archivos:** frontend admin (componente QR), backend endpoint de configuración de URL pública
- **Dependencias:** F-T3 · **Duración estimada:** 0.5 día
- **Criterios:** ✅ escaneo abre landing → login → catálogo · ✅ imprimible para mostrador

#### ⚡ QA-T1 — Tests backend (pytest)
- **Archivos:** `backend/tests/**` · **Dependencias:** B-T6
- **Criterios:** ✅ cobertura ≥80% en services (stock/checkout/availability) · ✅ casos: descuento, faltantes 409, concurrencia, umbrales, permisos 403

#### ⚡ QA-T2 — Tests frontend (Vitest)
- **Archivos:** `frontend/src/**/*.test.tsx` · **Dependencias:** F-T2, F-T3
- **Criterios:** ✅ badges de disponibilidad, tarjeta producto, carrito (agregar/quitar/total)

### 🔵 FASE FINAL (testing, deploy, docs)

#### ⚡ QA-T3 — E2E Playwright
- **Archivos:** `e2e/**` · **Dependencias:** todo lo anterior
- **Criterios:** ✅ flujo completo: login cliente → carrito → solicitud → (sonido) → admin "Pagado" → badges actualizados en celular

#### 🚀 D-T1 — CI/CD + deploy
- **Archivos:** `.github/workflows/*.yml`, `vercel.json`, `render.yaml`, docs de secretos
- **Criterios:** ✅ pipeline lint+build+test en cada push · ✅ Next.js en Vercel, FastAPI en Render (WS habilitado), DB Neon · ✅ CORS y secretos configurados

#### 🚀 D-T2 — Documentación final
- **Archivos:** `README.md` final, `docs/MANUAL_ADMIN.md`, `docs/ERD.md` actualizado
- **Criterios:** ✅ manual rápido para cargar productos · ✅ diagrama BD · ✅ runbook de deploy

#### 👨‍🍳 CHEF-FINAL — Verificación end-to-end
- Pedido de prueba real: escaneo → solicitud → sonido → "Pagado" → descuento visible en cliente en vivo. Evidencia: screenshots + video. **Aprobación final del Chef.**

## RIESGOS Y MITIGACIONES
| Riesgo | Mitigación |
|--------|------------|
| Desincronización si admin no presiona "Pagado" | Badge persistente + sonido + solicitudes pendientes destacadas en dashboard |
| Concurrencia de stock (2 ventas simultáneas) | Transacción + `SELECT FOR UPDATE` + CHECK en BD |
| Móviles gama media lentos | Imágenes optimizadas (Cloudinary), bundle liviano, catálogo paginado |
| Sonido bloqueado por autoplay | Reproducir tras interacción inicial del admin + fallback visual |
| CORS entre Next.js (dev :3000) y FastAPI (:8000) | CORS configurado en FastAPI + URL base de API en variable de entorno + rewrites en dev |
| Dependencia de cuentas externas (deploy) | Desarrollo local completo; cuentas se preparan en FASE FINAL |

## DEFINICIÓN DE TERMINADO (MVP)
- Flujo de oro completo verificado E2E por el Chef (criterio 2.3 del proyecto).
- Cliente ve solo etiquetas; admin ve números.
- Umbral configurable funcionando en vivo.
- 0 errores de compilación · 0 crashes · tests críticos ≥80% · docs al día.
