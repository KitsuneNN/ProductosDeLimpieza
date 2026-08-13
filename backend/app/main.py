# -*- coding: utf-8 -*-
"""Punto de entrada de la API FastAPI (B-T1).

Desarrollo:
    cd backend
    .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Documentación interactiva: http://localhost:8000/docs
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.services.checkout import StockInsuficienteError

app = FastAPI(
    title="ProductosDeLimpieza API",
    description=(
        "Catálogo e inventario para local de limpieza. "
        "QR → catálogo → solicitud → aviso sonoro → 'Pagado' → descuento de stock en vivo."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# WebSocket en /ws (fuera del prefijo /api, según docs/WS_EVENTS.md)
from app.ws import route as ws_route  # noqa: E402

app.include_router(ws_route.router)

# Imágenes locales (fallback sin Cloudinary): /uploads/<archivo>
DIR_UPLOADS = Path("uploads")
DIR_UPLOADS.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=DIR_UPLOADS), name="uploads")


@app.exception_handler(StockInsuficienteError)
async def _stock_insuficiente_handler(request, exc: StockInsuficienteError) -> JSONResponse:
    """409 con la lista de faltantes (sin descuentos parciales)."""
    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
            "faltantes": [f.model_dump(mode="json") for f in exc.faltantes],
        },
    )

_PAGINA_ESTADO = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ProductosDeLimpieza API</title>
<style>
  body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
         background:#f0f6fb; color:#123; margin:0; padding:24px; }
  .card { max-width:640px; margin:0 auto; background:#fff; border-radius:16px;
          box-shadow:0 6px 24px rgba(10,60,120,.10); padding:28px; }
  h1 { margin:0 0 4px; font-size:22px; color:#0b3d6b; }
  .sub { color:#5a6b7d; font-size:13px; margin-bottom:20px; }
  .badge { display:inline-flex; align-items:center; gap:8px; padding:10px 16px;
           border-radius:999px; font-weight:600; font-size:14px; }
  .ok { background:#e5f7ec; color:#0d6b3c; border:1px solid #b7e4c7; }
  .down { background:#fdeaea; color:#a11; border:1px solid #f3c1c1; }
  .dot { width:10px; height:10px; border-radius:50%; background:#17a34a; }
  .down .dot { background:#d33; }
  table { width:100%; border-collapse:collapse; margin:18px 0; font-size:14px; }
  th, td { text-align:left; padding:9px 10px; border-bottom:1px solid #e8eef4; }
  th { color:#3b5c7d; font-size:12px; text-transform:uppercase; letter-spacing:.4px; }
  code { background:#eef4fa; padding:2px 7px; border-radius:6px; font-size:12.5px; color:#0b3d6b; }
  a { color:#0b6bcb; }
  .foot { color:#8a99aa; font-size:12px; margin-top:14px; }
</style>
</head>
<body>
<div class="card">
  <h1>🧼 ProductosDeLimpieza API</h1>
  <div class="sub">Catálogo e inventario para local de limpieza · v""" + app.version + """</div>

  <div id="estado" class="badge down"><span class="dot"></span>Verificando…</div>

  <table>
    <tr><th>Recurso</th><th>Descripción</th></tr>
    <tr><td><code>GET /api/health</code></td><td>Salud de la API y su base de datos</td></tr>
    <tr><td><code>/docs</code></td><td>Documentación interactiva (Swagger)</td></tr>
    <tr><td><code>/api/auth/*</code></td><td>Registro y login de clientes (JWT)</td></tr>
    <tr><td><code>/api/catalogo</code></td><td>Catálogo para clientes (solo etiquetas de stock)</td></tr>
    <tr><td><code>/api/admin/*</code></td><td>Panel del administrador (productos, pagos, config)</td></tr>
  </table>

  <p><a href="/docs">Abrir Swagger UI →</a></p>
  <p class="foot">Este es el backend FastAPI. El frontend Next.js (catálogo y panel admin) se conectará aquí en la próxima fase.</p>
</div>
<script>
  fetch('/api/health')
    .then(function(r){ return r.ok ? r.json() : Promise.reject(); })
    .then(function(d){
      var e = document.getElementById('estado');
      e.className = 'badge ok';
      e.innerHTML = '<span class="dot"></span> API y base de datos: OK';
    })
    .catch(function(){
      var e = document.getElementById('estado');
      e.className = 'badge down';
      e.innerHTML = '<span class="dot"></span> Base de datos no disponible';
    });
</script>
</body>
</html>
"""


@app.get("/", tags=["sistema"], response_class=HTMLResponse)
async def raiz() -> HTMLResponse:
    """Página de estado del API (para el preview y visitas humanas)."""
    return HTMLResponse(_PAGINA_ESTADO)
