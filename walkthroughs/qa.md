# WALKTHROUGH — ⚡ QA

## [2026-08-13] - QA-T1: Suite pytest del backend (parcial — Vitest y Playwright pendientes)
### ✅ Implementado
- Archivos: `backend/tests/` (conftest, test_auth, test_availability, test_requests_service, test_checkout, test_images, test_api_flows)
- Cobertura de `app/services`: **95%** (checkout 100%, requests 100%, availability 95%, images 85%)
- Casos clave: flujo de oro por API, 409 doble pago, 409 con faltantes (sin descuento parcial), 403 por rol, catálogo sin stock numérico, umbral configurable, máquina de estados, validaciones (password corta, email duplicado), imágenes (formato/vacío/tamaño)

### 🧪 Verificación
- Ruta/comando: `cd backend && .venv/bin/python -m pytest -q` → **28 passed** (exit 0)
- Batería E2E en vivo contra PostgreSQL + WebSockets reales: **11/11 checks** (login, registro, catálogo sin números, WS solicitud.creada→admin, WS stock.actualizado→cliente, doble pago 409, 403, faltantes, umbral)
- Bugs reales encontrados y corregidos por la verificación:
  1. `email-validator` rechazaba el dominio `.local` del admin sembrado (imposible iniciar sesión) → admin@limpieza.com
  2. Broadcast WS con `Decimal` sin serializar → serializador central en el manager

### ⏳ Estado
✅ APPROVED parcial (QA-T1). Pendientes: QA-T2 (Vitest) y QA-T3 (Playwright E2E) — FASE NORMAL/FINAL.
