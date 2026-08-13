# -*- coding: utf-8 -*-
"""Tests de integración de la API (flujos completos por HTTP)."""
import pytest

from app.core.security import create_access_token


def _token_admin() -> str:
    return create_access_token(1, "admin")


def _token_cliente() -> str:
    return create_access_token(2, "cliente")


@pytest.mark.asyncio
async def test_catalogo_cliente_sin_stock_numerico(client):
    r = await client.get(
        "/api/catalogo", headers={"Authorization": f"Bearer {_token_cliente()}"}
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == 2  # solo activos (el pausado no aparece)
    for item in cuerpo["items"]:
        assert "stock_actual" not in item
        assert item["disponibilidad"] in {"disponible", "pocas", "sin_stock"}
    # stock 10 con umbral 5 → disponible; stock 3 → pocas
    etiquetas = {i["nombre"]: i["disponibilidad"] for i in cuerpo["items"]}
    assert etiquetas["Lavandina 1L"] == "disponible"
    assert etiquetas["Detergente Limón"] == "pocas"


@pytest.mark.asyncio
async def test_cliente_no_puede_ver_productos_admin_403(client):
    r = await client.get(
        "/api/admin/productos",
        headers={"Authorization": f"Bearer {_token_cliente()}"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_admin_crud_producto(client):
    headers = {"Authorization": f"Bearer {_token_admin()}"}
    r = await client.post(
        "/api/admin/productos",
        headers=headers,
        json={
            "categoria_id": 1,
            "nombre": "Esponja Doble",
            "precio": 350,
            "stock_actual": 12,
        },
    )
    assert r.status_code == 201, r.text
    nuevo = r.json()
    assert nuevo["stock_actual"] == 12  # admin SÍ ve números

    r2 = await client.patch(
        f"/api/admin/productos/{nuevo['id']}/estado",
        headers=headers,
        json={"estado": "pausado"},
    )
    assert r2.status_code == 200
    assert r2.json()["estado"] == "pausado"

    r3 = await client.put(
        f"/api/admin/productos/{nuevo['id']}",
        headers=headers,
        json={"stock_actual": 20, "precio": 330},
    )
    assert r3.status_code == 200
    assert r3.json()["stock_actual"] == 20

    r4 = await client.delete(f"/api/admin/productos/{nuevo['id']}", headers=headers)
    assert r4.status_code == 204


@pytest.mark.asyncio
async def test_flujo_de_oro_api(client):
    """Cliente crea solicitud → admin la ve → paga → stock baja y 409 al repetir."""
    cliente = {"Authorization": f"Bearer {_token_cliente()}"}
    admin = {"Authorization": f"Bearer {_token_admin()}"}

    r = await client.post(
        "/api/solicitudes",
        headers=cliente,
        json={"items": [{"producto_id": 1, "cantidad": 2}]},
    )
    assert r.status_code == 201, r.text
    solicitud_id = r.json()["id"]
    assert r.json()["estado"] == "pendiente"

    # Admin lista pendientes
    r2 = await client.get("/api/admin/solicitudes?estado=pendiente", headers=admin)
    assert r2.status_code == 200
    ids = [s["id"] for s in r2.json()["items"]]
    assert solicitud_id in ids

    # Pagar
    r3 = await client.post(f"/api/admin/solicitudes/{solicitud_id}/pagar", headers=admin)
    assert r3.status_code == 200, r3.text
    assert r3.json()["unidades_descontadas"] == 2

    # Stock bajó (admin lo ve; el catálogo de cliente solo etiqueta)
    r4 = await client.get("/api/admin/productos/1", headers=admin)
    assert r4.json()["stock_actual"] == 8

    # Pagar de nuevo → 409
    r5 = await client.post(f"/api/admin/solicitudes/{solicitud_id}/pagar", headers=admin)
    assert r5.status_code == 409


@pytest.mark.asyncio
async def test_pago_con_faltantes_409_con_detalle(client):
    cliente = {"Authorization": f"Bearer {_token_cliente()}"}
    admin = {"Authorization": f"Bearer {_token_admin()}"}
    r = await client.post(
        "/api/solicitudes",
        headers=cliente,
        json={"items": [{"producto_id": 2, "cantidad": 50}]},  # stock 3
    )
    solicitud_id = r.json()["id"]
    r2 = await client.post(f"/api/admin/solicitudes/{solicitud_id}/pagar", headers=admin)
    assert r2.status_code == 409
    cuerpo = r2.json()
    assert cuerpo["faltantes"][0]["producto_id"] == 2
    assert cuerpo["faltantes"][0]["disponible"] == 3
    # Stock intacto
    r3 = await client.get("/api/admin/productos/2", headers=admin)
    assert r3.json()["stock_actual"] == 3


@pytest.mark.asyncio
async def test_umbral_configurable(client):
    admin = {"Authorization": f"Bearer {_token_admin()}"}
    r = await client.get("/api/admin/config/umbral-pocas-unidades", headers=admin)
    assert r.json()["umbral_pocas_unidades"] == 5
    r2 = await client.put(
        "/api/admin/config/umbral-pocas-unidades", headers=admin, json={"valor": "2"}
    )
    assert r2.status_code == 200
    assert r2.json()["umbral_pocas_unidades"] == 2
    # Umbral inválido rechazado
    r3 = await client.put(
        "/api/admin/config/umbral-pocas-unidades", headers=admin, json={"valor": "cero"}
    )
    assert r3.status_code == 400
