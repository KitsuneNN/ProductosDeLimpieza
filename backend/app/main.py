# -*- coding: utf-8 -*-
"""Punto de entrada de la API FastAPI (B-T1).

Desarrollo:
    cd backend
    .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Documentación interactiva: http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

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


@app.get("/", tags=["sistema"])
async def raiz() -> dict:
    return {
        "app": "ProductosDeLimpieza API",
        "version": app.version,
        "docs": "/docs",
        "health": "/api/health",
    }
