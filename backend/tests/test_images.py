# -*- coding: utf-8 -*-
"""Tests del servicio de imágenes (B-T3) — fallback local."""
import io
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile

from app.services.images import ImagesService

service = ImagesService()


async def _archivo(nombre: str, contenido: bytes, tipo: str = "image/png") -> UploadFile:
    return UploadFile(filename=nombre, file=io.BytesIO(contenido))


@pytest.mark.asyncio
async def test_guardar_local_devuelve_url(client):
    upload = await _archivo("foto.png", b"\x89PNG\r\n" + b"0" * 100)
    url = await service.guardar(upload)
    assert url.startswith("/uploads/") and url.endswith(".png")
    assert (Path("uploads") / url.split("/")[-1]).exists()


@pytest.mark.asyncio
async def test_extension_no_permitida_400(client):
    with pytest.raises(HTTPException) as exc:
        await service.guardar(await _archivo("virus.exe", b"MZ..."))
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_archivo_vacio_400(client):
    with pytest.raises(HTTPException) as exc:
        await service.guardar(await _archivo("vacio.png", b""))
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_archivo_demasiado_grande_413(client):
    contenido = b"\x89PNG\r\n" + b"0" * (5 * 1024 * 1024)
    with pytest.raises(HTTPException) as exc:
        await service.guardar(await _archivo("grande.png", contenido))
    assert exc.value.status_code == 413
