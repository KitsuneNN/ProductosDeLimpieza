# -*- coding: utf-8 -*-
"""Agregador central de routers (B-T1)."""
from fastapi import APIRouter

from app.api import health

api_router = APIRouter()
api_router.include_router(health.router)
