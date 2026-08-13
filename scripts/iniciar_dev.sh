#!/usr/bin/env bash
# Arranque del entorno de desarrollo completo (PostgreSQL + API + Frontend)
# Uso: bash scripts/iniciar_dev.sh
# Idempotente y resiliente: reinstala PostgreSQL si el sandbox lo perdió.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_URL="postgresql+asyncpg://limpieza:limpieza_dev@127.0.0.1:5432/limpieza"
DB_SYNC="postgresql+psycopg://limpieza:limpieza_dev@127.0.0.1:5432/limpieza"

echo "1/6 · PostgreSQL"
if ! command -v psql >/dev/null 2>&1 || [ ! -d /usr/lib/postgresql ]; then
  echo "  → instalando PostgreSQL…"
  export DEBIAN_FRONTEND=noninteractive
  sudo apt-get update -qq
  sudo apt-get install -y -qq postgresql postgresql-contrib
fi
if ! pg_isready -h 127.0.0.1 -q 2>/dev/null; then
  sudo pg_ctlcluster 17 main start 2>/dev/null || sudo service postgresql start
fi
pg_isready -h 127.0.0.1
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='limpieza'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE ROLE limpieza LOGIN PASSWORD 'limpieza_dev';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='limpieza'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE DATABASE limpieza OWNER limpieza;"

echo "1b/6 · Claves y git (el snapshot puede restaurar permisos abiertos)"
chmod 600 "$HOME/.ssh/github_deploy_key" "$HOME/.ssh/config" 2>/dev/null || true
cd "$RAIZ"
git config user.name "Chef Master (Arena Agent)" 2>/dev/null || true
git config user.email "chef-master@arena.workspace" 2>/dev/null || true
git remote get-url origin >/dev/null 2>&1 || \
  git remote add origin git@github.com:KitsuneNN/ProductosDeLimpieza.git

echo "2/6 · Dependencias + migraciones + seed"
cd "$RAIZ/backend"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt 2>/dev/null || true
DATABASE_URL="$DB_URL" .venv/bin/python -m alembic upgrade head
.venv/bin/python - << EOF
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.seed import seed
seed(sessionmaker(bind=create_engine("$DB_SYNC"))())
EOF

echo "3/6 · Admin de desarrollo"
ADMIN_EMAIL=admin@limpieza.com ADMIN_PASSWORD="${ADMIN_PASSWORD:-Admin#Limpieza2026}" \
  DATABASE_URL="$DB_URL" .venv/bin/python -m app.db.seed_admin || true

echo "4/6 · Verificadores de contrato"
.venv/bin/python scripts/verify_contract.py || true
.venv/bin/python scripts/verify_migration_parity.py || true

echo "5/6 · Dependencias del frontend"
cd "$RAIZ/frontend"
[ -d node_modules ] || npm install --no-audit --no-fund

echo "6/6 · Arrancar servidores (con las herramientas de proceso del asistente):"
echo "  API:      cd $RAIZ/backend && DATABASE_URL='$DB_URL' .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "  Frontend: cd $RAIZ/frontend && npm run dev -- --hostname 0.0.0.0 --port 3000"
echo ""
echo "Previews: abrir los puertos 8000 (API) y 3000 (Frontend) en el panel de previews."
echo "Admin dev: admin@limpieza.com / Admin#Limpieza2026"
