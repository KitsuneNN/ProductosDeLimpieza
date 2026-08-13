# -*- coding: utf-8 -*-
"""Configuración central (B-T1).

Lee variables de entorno / archivo .env. Fuente única de verdad de
configuración: nadie más lee os.environ directamente.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Base de datos (URL async):
    #   Dev: sqlite+aiosqlite:///./dev.db
    #   Prod: postgresql+asyncpg://usuario:clave@host:5432/limpieza
    database_url: str = "sqlite+aiosqlite:///./dev.db"

    # Auth (usado desde B-T2)
    jwt_secret: str = "cambiar-por-secreto-largo-y-aleatorio"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 1440

    # CORS — orígenes del frontend separados por coma
    cors_origins: str = "http://localhost:3000"

    # Cloudinary (opcional; si vacío → almacenamiento local)
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def cloudinary_configurado(self) -> bool:
        return bool(
            self.cloudinary_cloud_name
            and self.cloudinary_api_key
            and self.cloudinary_api_secret
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
