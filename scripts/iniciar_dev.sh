#!/usr/bin/env bash
# Arranque del entorno de desarrollo completo (PostgreSQL + API + Frontend)
# Uso: bash scripts/iniciar_dev.sh
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_URL="postgresql+asyncpg://limpieza:limpieza_dev@127.0.0.1:5432/limpieza"
DB_SYNC="postgresql+psycopg://limpieza:limpieza_dev@127.0.0.1:5432/limpieza"

echo "1/5 · PostgreSQL"
if ! pg_isready -h 127.0.0.1 -q 2>/dev/null; then
  sudo pg_ctlcluster 17 main start 2>/dev/null || sudo service postgresql start
fi
pg_isready -h 127.0.0.1

echo "2/5 · Migraciones + seed"
cd "$RAIZ/backend"
.venv/bin/pip install -q -r requirements.txt 2>/dev/null || true
DATABASE_URL="$DB_URL" .venv/bin/python -m alembic upgrade head
.venv/bin/python - << EOF
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.seed import seed
seed(sessionmaker(bind=create_engine("$DB_SYNC"))())
EOF

echo "3/5 · Admin de desarrollo"
ADMIN_EMAIL=admin@limpieza.com ADMIN_PASSWORD="${ADMIN_PASSWORD:-Admin#Limpieza2026}" \
  DATABASE_URL="$DB_URL" .venv/bin/python -m app.db.seed_admin || true

echo "4/5 · Verificadores de contrato"
.venv/bin/python scripts/verify_contract.py || true
.venv/bin/python scripts/verify_migration_parity.py || true

echo "5/5 · Arrancar servidores:"
echo "  API:      cd backend && DATABASE_URL='$DB_URL' .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "  Frontend: cd frontend && npm install && npm run dev -- --hostname 0.0.0.0 --port 3000"
echo ""
echo "Previews: abrir los puertos 8000 (API) y 3000 (Frontend) en el panel de previews."
echo "Admin dev: admin@limpieza.com / Admin#Limpieza2026"
