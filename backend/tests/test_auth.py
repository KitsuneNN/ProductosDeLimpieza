# -*- coding: utf-8 -*-
"""Tests de autenticación (B-T2)."""
import pytest


@pytest.mark.asyncio
async def test_registro_y_login_flujo_completo(client):
    # Registro
    r = await client.post(
        "/api/auth/registro",
        json={
            "nombre": "María González",
            "telefono": "2615559999",
            "email": "maria@example.com",
            "password": "clave1234",
        },
    )
    assert r.status_code == 201, r.text
    cuerpo = r.json()
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["access_token"]
    assert cuerpo["usuario"]["rol"] == "cliente"
    assert "password" not in str(cuerpo)

    # Login con la misma cuenta
    r2 = await client.post(
        "/api/auth/login", json={"email": "maria@example.com", "password": "clave1234"}
    )
    assert r2.status_code == 200, r2.text

    # /me con el token
    r3 = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {cuerpo['access_token']}"}
    )
    assert r3.status_code == 200
    assert r3.json()["email"] == "maria@example.com"


@pytest.mark.asyncio
async def test_registro_email_duplicado(client):
    r1 = await client.post(
        "/api/auth/registro",
        json={
            "nombre": "Ana",
            "telefono": "2611111111",
            "email": "dup@example.com",
            "password": "clave1234",
        },
    )
    assert r1.status_code == 201
    r2 = await client.post(
        "/api/auth/registro",
        json={
            "nombre": "Bea",
            "telefono": "2612222222",
            "email": "dup@example.com",
            "password": "otraclave99",
        },
    )
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_login_password_incorrecta(client):
    r = await client.post(
        "/api/auth/login",
        json={"email": "cliente@example.com", "password": "incorrecta"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_sin_token_o_token_invalido(client):
    assert (await client.get("/api/auth/me")).status_code == 401
    assert (
        await client.get(
            "/api/auth/me", headers={"Authorization": "Bearer token-falso"}
        )
    ).status_code == 401


@pytest.mark.asyncio
async def test_password_corta_rechazada(client):
    r = await client.post(
        "/api/auth/registro",
        json={
            "nombre": "C",
            "telefono": "2613333333",
            "email": "corta@example.com",
            "password": "123",
        },
    )
    assert r.status_code == 422
