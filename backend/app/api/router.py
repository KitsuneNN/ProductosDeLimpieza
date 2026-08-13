# -*- coding: utf-8 -*-
"""Agregador central de routers."""
from fastapi import APIRouter

from app.api import auth, catalogo, config_admin, health, products_admin, requests

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(catalogo.router)
api_router.include_router(requests.router_cliente)
api_router.include_router(requests.router_admin)
api_router.include_router(products_admin.router)
api_router.include_router(config_admin.router)
