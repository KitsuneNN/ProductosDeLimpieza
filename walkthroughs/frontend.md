# WALKTHROUGH — 🎨 Frontend

## [2026-08-13] - Fix crítico: preview en blanco (allowedDevOrigins)
### ✅ Implementado
- `next.config.ts`: `allowedDevOrigins: ["*.e2b.app", "*.e2b.dev"]` — Next 16 bloqueaba (403) los chunks JS y HMR cuando el Origin era el host del preview
- `layout.tsx`: eliminado `maximumScale: 1` (a11y: permite zoom)
- `lib/ws.ts`: eliminado fallback muerto a `ws://localhost:8000`; ahora solo ruta relativa `/ws` (rewrite) + `NEXT_PUBLIC_WS_URL` opcional
- `package.json`: script `typecheck` (Next 16 no corre tsc en build)
- `scripts/iniciar_dev.sh`: arranque reproducible del entorno completo (PG + migraciones + seed + admin + verificadores)

### 🧪 Verificación
- Reproducción exacta: chunk con `Origin: https://3000-…e2b.app` → **403 antes / 200 después**
- HMR con handshake WS + Origin preview → aceptado (conexión abierta)
- WS de la app vía proxy Next → `conexion.establecida` OK
- E2E mini vía proxy (health/login/categorías) → 200 · `tsc --noEmit` → 0 errores · pytest 28 ✅

### ⏳ Estado
ESPERANDO_APROBACIÓN_CHEF

## [2026-08-13] - F-T1 + F-T2 + F-T3 + F-T4: Next.js 16 completo
### ✅ Implementado
- Scaffold: Next.js 16.3.0 (App Router + Turbopack) + TypeScript + Tailwind v4 + pnpm-style (npm)
- `next.config.ts` con rewrites: `/api/*`, `/uploads/*` y `/ws` → FastAPI (verificado en vivo)
- Librerías: `lib/api.ts` (cliente HTTP tipado + ApiError con faltantes), `lib/auth.ts` (sesión), `lib/cart.ts` (carrito persistente), `lib/sonido.ts` (aviso Web Audio), `lib/ws.ts` (WS con reintentos + estados)
- Componentes: `ui.tsx` (botones ≥44px, badges, a11y) y `ProductoCard.tsx`
- **Cliente (mobile-first):** landing con QR · login · registro · catálogo (categorías, búsqueda, etiquetas en vivo por WS + polling) · detalle con cantidad · carrito con envío de solicitud · mis pedidos en vivo
- **Admin:** dashboard con aviso sonoro + banner de nuevo pedido + estado "EN VIVO" · CRUD productos con foto (subida Cloudinary/local) · pedidos con filtros · detalle con "Marcar como PAGADO" (maneja 409 con faltantes) · umbral configurable · QR imprimible/descargable
- Guard de sesión por rol en ambos layouts (cliente y admin)

### 🧪 Verificación
- Ruta/comando: `cd frontend && npm run build` → **exit 0** (16 rutas generadas)
- `next dev --hostname 0.0.0.0 --port 3000` → 200 en `/`, `/cliente/login`, `/admin/dashboard`
- Rewrite `/api/health` → FastAPI: 200 `{"status":"ok"}` ✅
- WS a través del proxy de Next (`ws://127.0.0.1:3000/ws`): `conexion.establecida` ✅
- Bug corregido durante el build (Debug Protocol): `??` mezclado con `||` en catálogo → paréntesis → rebuild exit 0

### ⏳ Estado
ESPERANDO_APROBACIÓN_CHEF
