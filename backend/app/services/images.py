# -*- coding: utf-8 -*-
"""Almacenamiento de imágenes de productos (B-T3).

- Si Cloudinary está configurado (env) → sube y devuelve URL optimizada.
- Si no → fallback local en `uploads/` servido por FastAPI en `/uploads`.
"""
import asyncio
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

DIR_UPLOADS = Path("uploads")
EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp"}
TAMANO_MAXIMO = 5 * 1024 * 1024  # 5 MB


class ImagesService:
    """Interfaz intercambiable de almacenamiento (Cloudinary o local)."""

    async def guardar(self, archivo: UploadFile) -> str:
        """Guarda la imagen y devuelve su URL pública."""
        if not archivo.filename:
            raise HTTPException(status_code=400, detail="Archivo sin nombre")
        extension = Path(archivo.filename).suffix.lower()
        if extension not in EXTENSIONES_PERMITIDAS:
            raise HTTPException(
                status_code=400,
                detail="Formato no permitido (usar jpg, png o webp)",
            )
        contenido = await archivo.read()
        if len(contenido) == 0:
            raise HTTPException(status_code=400, detail="Archivo vacío")
        if len(contenido) > TAMANO_MAXIMO:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Imagen demasiado grande (máximo 5 MB)",
            )
        if settings.cloudinary_configurado:
            return await asyncio.to_thread(self._subir_cloudinary, contenido)
        return self._guardar_local(contenido, extension)

    # ------------------------------------------------------------------ local
    def _guardar_local(self, contenido: bytes, extension: str) -> str:
        DIR_UPLOADS.mkdir(parents=True, exist_ok=True)
        nombre = f"{uuid4().hex}{extension}"
        (DIR_UPLOADS / nombre).write_bytes(contenido)
        return f"/uploads/{nombre}"

    # -------------------------------------------------------------- cloudinary
    def _subir_cloudinary(self, contenido: bytes) -> str:
        import cloudinary.uploader  # import perezoso: solo si está configurado

        resultado = cloudinary.uploader.upload(
            contenido,
            resource_type="image",
            folder="productos_limpieza",
        )
        return resultado.get("secure_url", "")


images_service = ImagesService()
