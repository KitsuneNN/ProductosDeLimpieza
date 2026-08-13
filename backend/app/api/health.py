# -*- coding: utf-8 -*-
"""Healthcheck con verificación de conectividad a BD (B-T1)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import HealthResponse

router = APIRouter(tags=["sistema"])


@router.get("/health", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Verifica que la API y su base de datos responden."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible",
        )
    return HealthResponse(status="ok")
