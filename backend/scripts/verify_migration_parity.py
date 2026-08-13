#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verificador de paridad: migración Alembic == modelos SQLAlchemy (Regla 5 análoga).

Uso:
    cd backend && .venv/bin/python scripts/verify_migration_parity.py

Estrategia: crea el esquema en SQLite por DOS vías independientes:
  1) `alembic upgrade head` (la migración real con DDL congelado)
  2) `Base.metadata.create_all` (lo que los modelos generan)
y compara columna por columna (tipo, nulabilidad, defaults), PKs, FKs,
constraints UNIQUE e índices únicos.

Exit 0 = espejo exacto. Cualquier divergencia → exit 1 (un cambio de modelo
SIN migración, o una migración SIN modelo, queda en evidencia).
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]  # backend/
sys.path.insert(0, str(RAIZ))

from sqlalchemy import create_engine, inspect  # noqa: E402


def dump_esquema(db_path: str) -> dict:
    engine = create_engine(f"sqlite:///{db_path}")
    insp = inspect(engine)
    out = {}
    for tabla in sorted(insp.get_table_names()):
        if tabla == "alembic_version":
            continue
        columnas = insp.get_columns(tabla)
        out[tabla] = {
            "cols": sorted(
                (c["name"], str(c["type"]), bool(c["nullable"]), str(c.get("default")))
                for c in columnas
            ),
            "pks": sorted(c["name"] for c in columnas if c.get("primary_key")),
            "fks": sorted(
                (tuple(fk["constrained_columns"]), fk["referred_table"])
                for fk in insp.get_foreign_keys(tabla)
            ),
            "unq": sorted(tuple(sorted(u["column_names"])) for u in insp.get_unique_constraints(tabla))
            + sorted(
                tuple(sorted(ix["column_names"]))
                for ix in insp.get_indexes(tabla)
                if ix.get("unique") and not ix["name"].startswith("sqlite_")
            ),
        }
    engine.dispose()
    return out


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="parity_"))
    mig_db = tmp / "migracion.db"
    mod_db = tmp / "modelos.db"
    try:
        env = dict(os.environ, DATABASE_URL=f"sqlite:///{mig_db}")
        r = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=RAIZ, env=env, capture_output=True, text=True,
        )
        if r.returncode != 0:
            print("❌ alembic upgrade falló:", r.stderr[-600:])
            return 1

        from app.models import Base  # noqa: E402

        engine = create_engine(f"sqlite:///{mod_db}")
        Base.metadata.create_all(engine)
        engine.dispose()

        d_mig, d_mod = dump_esquema(mig_db), dump_esquema(mod_db)
        if d_mig != d_mod:
            print("❌ DIVERGENCIA migración ↔ modelos:")
            for t in sorted(set(d_mig) | set(d_mod)):
                if d_mig.get(t) != d_mod.get(t):
                    print(f"  tabla {t}:")
                    print(f"    migración = {d_mig.get(t)}")
                    print(f"    modelos   = {d_mod.get(t)}")
            return 1

        n_cols = sum(len(v["cols"]) for v in d_mig.values())
        print(f"✅ Migración == modelos (espejo exacto): {len(d_mig)} tablas, {n_cols} columnas")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
