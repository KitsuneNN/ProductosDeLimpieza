#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verificador de REGLA 5: schemas Pydantic ↔ types TypeScript (espejo exacto).

Uso:
    cd backend && .venv/bin/python scripts/verify_contract.py

Valida:
1. Que cada schema Pydantic listado tenga su interfaz TS con los MISMOS campos
   (nombres exactos, snake_case) y la misma opcionalidad (`?` en TS ⇔ default en Pydantic).
2. Que las uniones Literal de Pydantic coincidan con los type alias de TS.
3. Que los montos Decimal se serialicen como NÚMERO en JSON (wire-format).

Exit code 0 = contrato consistente. Cualquier discrepancia → exit 1.
"""
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

# ---------------------------------------------------------------- configuración
RAIZ = Path(__file__).resolve().parents[1]  # backend/
sys.path.insert(0, str(RAIZ))  # permite `from app.schemas import ...` desde cualquier cwd
TYPES_DIR = RAIZ.parent / "frontend" / "src" / "types"

PARES = {
    # schema Pydantic → interfaz TS
    "RegistroRequest": "RegistroRequest",
    "LoginRequest": "LoginRequest",
    "UsuarioPublic": "UsuarioPublic",
    "TokenResponse": "TokenResponse",
    "CategoriaPublic": "CategoriaPublic",
    "CategoriaCreate": "CategoriaCreate",
    "CategoriaUpdate": "CategoriaUpdate",
    "ProductoAdminPublic": "ProductoAdminPublic",
    "ProductoCreate": "ProductoCreate",
    "ProductoUpdate": "ProductoUpdate",
    "ProductoEstadoUpdate": "ProductoEstadoUpdate",
    "ProductoClientePublic": "ProductoClientePublic",
    "ItemSolicitudCreate": "ItemSolicitudCreate",
    "SolicitudCreate": "SolicitudCreate",
    "DetalleSolicitudPublic": "DetalleSolicitudPublic",
    "SolicitudPublic": "SolicitudPublic",
    "SolicitudAdminPublic": "SolicitudAdminPublic",
    "SolicitudesResponse": "SolicitudesResponse",
    "SolicitudesAdminResponse": "SolicitudesAdminResponse",
    "PagoResponse": "PagoResponse",
    "FaltanteInfo": "FaltanteInfo",
    "FaltantesResponse": "FaltantesResponse",
    "ConfiguracionPublic": "ConfiguracionPublic",
    "ConfiguracionUpdate": "ConfiguracionUpdate",
    "UmbralResponse": "UmbralResponse",
    "CategoriasResponse": "CategoriasResponse",
    "CatalogoResponse": "CatalogoResponse",
}

ALIAS = {
    # type alias TS → Literal Pydantic
    "Disponibilidad": "DISPONIBILIDAD",
    "EstadoProducto": "ESTADO_PRODUCTO",
    "EstadoSolicitud": "ESTADO_SOLICITUD",
    "RolUsuario": "ROL_USUARIO",
}

# ---------------------------------------------------------------- parsers TS
IFACE_RE = re.compile(
    r"export interface (\w+)(?:\s+extends\s+([\w, ]+?))?\s*\{(.*?)\}",
    re.DOTALL,
)
FIELD_RE = re.compile(r"^\s*(\w+)(\?)?\s*:", re.MULTILINE)
ALIAS_RE = re.compile(r"export type (\w+) = ([^;]+);", re.DOTALL)


def parse_ts() -> dict:
    interfaces: dict[str, dict] = {}
    aliases: dict[str, set[str]] = {}
    for archivo in TYPES_DIR.glob("*.ts"):
        texto = archivo.read_text(encoding="utf-8")
        for nombre, extends, cuerpo in IFACE_RE.findall(texto):
            campos: dict[str, bool] = {}
            for campo, opt in FIELD_RE.findall(cuerpo):
                campos[campo] = bool(opt)
            interfaces[nombre] = {
                "campos": campos,
                "extends": [e.strip() for e in extends.split(",") if e.strip()],
            }
        for nombre, cuerpo in ALIAS_RE.findall(texto):
            aliases[nombre] = set(re.findall(r'"([^"]+)"', cuerpo))
    return interfaces, aliases


def campos_ts(interfaces: dict, nombre: str, visitados: set | None = None) -> dict[str, bool]:
    visitados = visitados or set()
    if nombre in visitados:
        raise SystemExit(f"Ciclo de extends detectado en TS: {nombre}")
    visitados.add(nombre)
    info = interfaces[nombre]
    campos: dict[str, bool] = {}
    for padre in info["extends"]:
        campos.update(campos_ts(interfaces, padre, set(visitados)))
    campos.update(info["campos"])
    return campos


# ---------------------------------------------------------------- validaciones
def main() -> int:
    from app.schemas import (  # import dentro de main (requiere cwd=backend)
        CatalogoResponse,
        CategoriasResponse,
        CategoriaCreate,
        CategoriaPublic,
        CategoriaUpdate,
        ConfiguracionPublic,
        ConfiguracionUpdate,
        DetalleSolicitudPublic,
        DISPONIBILIDAD,
        ESTADO_PRODUCTO,
        ESTADO_SOLICITUD,
        FaltanteInfo,
        FaltantesResponse,
        ItemSolicitudCreate,
        LoginRequest,
        PagoResponse,
        ProductoAdminPublic,
        ProductoClientePublic,
        ProductoCreate,
        ProductoEstadoUpdate,
        ProductoUpdate,
        RegistroRequest,
        ROL_USUARIO,
        SolicitudAdminPublic,
        SolicitudCreate,
        SolicitudPublic,
        SolicitudesAdminResponse,
        SolicitudesResponse,
        TokenResponse,
        UmbralResponse,
        UsuarioPublic,
    )
    esquemas = {
        "RegistroRequest": RegistroRequest,
        "LoginRequest": LoginRequest,
        "UsuarioPublic": UsuarioPublic,
        "TokenResponse": TokenResponse,
        "CategoriaPublic": CategoriaPublic,
        "CategoriaCreate": CategoriaCreate,
        "CategoriaUpdate": CategoriaUpdate,
        "ProductoAdminPublic": ProductoAdminPublic,
        "ProductoCreate": ProductoCreate,
        "ProductoUpdate": ProductoUpdate,
        "ProductoEstadoUpdate": ProductoEstadoUpdate,
        "ProductoClientePublic": ProductoClientePublic,
        "ItemSolicitudCreate": ItemSolicitudCreate,
        "SolicitudCreate": SolicitudCreate,
        "DetalleSolicitudPublic": DetalleSolicitudPublic,
        "SolicitudPublic": SolicitudPublic,
        "SolicitudAdminPublic": SolicitudAdminPublic,
        "SolicitudesResponse": SolicitudesResponse,
        "SolicitudesAdminResponse": SolicitudesAdminResponse,
        "PagoResponse": PagoResponse,
        "FaltanteInfo": FaltanteInfo,
        "FaltantesResponse": FaltantesResponse,
        "ConfiguracionPublic": ConfiguracionPublic,
        "ConfiguracionUpdate": ConfiguracionUpdate,
        "UmbralResponse": UmbralResponse,
        "CategoriasResponse": CategoriasResponse,
        "CatalogoResponse": CatalogoResponse,
    }
    literales = {
        "DISPONIBILIDAD": DISPONIBILIDAD,
        "ESTADO_PRODUCTO": ESTADO_PRODUCTO,
        "ESTADO_SOLICITUD": ESTADO_SOLICITUD,
        "ROL_USUARIO": ROL_USUARIO,
    }

    interfaces, aliases = parse_ts()
    errores: list[str] = []

    # 1) campos espejo
    for py_name, ts_name in PARES.items():
        if ts_name not in interfaces:
            errores.append(f"Interfaz TS faltante: {ts_name}")
            continue
        py_fields = esquemas[py_name].model_fields
        ts_fields = campos_ts(interfaces, ts_name)
        solo_py = set(py_fields) - set(ts_fields)
        solo_ts = set(ts_fields) - set(py_fields)
        if solo_py:
            errores.append(f"{py_name}↔{ts_name}: faltan en TS → {sorted(solo_py)}")
        if solo_ts:
            errores.append(f"{py_name}↔{ts_name}: sobran en TS → {sorted(solo_ts)}")
        for campo in set(py_fields) & set(ts_fields):
            py_req = py_fields[campo].is_required()
            ts_opt = ts_fields[campo]  # True si tiene '?'
            if py_req == ts_opt:
                lado = "requerido" if py_req else "opcional"
                errores.append(
                    f"{py_name}↔{ts_name}.{campo}: en Pydantic es {lado} y en TS no coincide"
                )

    # 2) literales
    for ts_alias, py_lit in ALIAS.items():
        if ts_alias not in aliases:
            errores.append(f"Type alias TS faltante: {ts_alias}")
            continue
        valores_py = set(literales[py_lit].__args__)
        if aliases[ts_alias] != valores_py:
            errores.append(
                f"{ts_alias}: TS={sorted(aliases[ts_alias])} vs Pydantic={sorted(valores_py)}"
            )

    # 3) wire-format de montos (número, no string)
    muestra = ProductoAdminPublic(
        id=1,
        categoria_id=1,
        nombre="Lavandina 1L",
        descripcion=None,
        precio=Decimal("1250.50"),
        stock_actual=7,
        imagen_url=None,
        estado="activo",
        creado_en="2026-08-13T18:00:00Z",
        actualizado_en="2026-08-13T18:00:00Z",
    )
    json_str = muestra.model_dump_json()
    if '"precio":"1250.50"' in json_str or '"precio":1250.5' not in json_str:
        errores.append("Wire-format de montos: Decimal se serializa como string, debe ser número")
    else:
        print(f"Wire-format montos OK → {json_str}")

    if errores:
        print("❌ INCONSISTENCIAS DE CONTRATO:")
        for e in errores:
            print("  -", e)
        return 1

    print(f"✅ Regla 5 verificada: {len(PARES)} pares Pydantic↔TS idénticos")
    print(f"✅ Literales coincidentes: {len(ALIAS)} aliases TS ↔ Pydantic")
    return 0


if __name__ == "__main__":
    sys.exit(main())
