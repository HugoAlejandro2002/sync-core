# Caja Inteligente Bolivia — Backend

Backend (FastAPI) para estructurar evidencia financiera de comerciantes informales:
crea solicitudes de crédito, sube imágenes de evidencia, extrae transacciones con IA
(Gemini Flash, con proveedor *fake* por defecto) y devuelve un resumen financiero.

La especificación está en [`AGENTS.md`](./AGENTS.md) (`CLAUDE.md` es un symlink a ese archivo).

## Requisitos

- Python 3.12+ y [uv](https://docs.astral.sh/uv/)
- MySQL 8 (se incluye `docker-compose.yml`)
- Docker (opcional, para levantar MySQL)

## Puesta en marcha

```bash
# 1. Base de datos (MySQL 8). Si el puerto 3306 está ocupado:
#    MYSQL_HOST_PORT=3307 docker compose up -d   (y ajustá DATABASE_URL a :3307)
docker compose up -d

# 2. Variables de entorno
cp .env.example .env        # dejá GEMINI_API_KEY="replace-me" para usar IA simulada

# 3. Dependencias
uv sync

# 4. Migraciones
uv run alembic upgrade head

# 5. Servidor de desarrollo  ->  http://localhost:8000
uv run fastapi dev src/app/main.py
```

Verificá el estado en `GET http://localhost:8000/api/v1/health`.
Documentación interactiva en `http://localhost:8000/docs`.

## IA (extracción de evidencia)

- Sin `GEMINI_API_KEY` (o con `"replace-me"`) se usa un proveedor **fake** determinista,
  por lo que todo el flujo funciona sin gastar llamadas a Gemini.
- Con una `GEMINI_API_KEY` válida se usa **Gemini Flash** (modelo configurable con `GEMINI_MODEL`).

## Endpoints (`/api/v1`)

```
GET    /health
POST   /managements                       (multipart: datos + files[] opcional)
GET    /managements?status=all|pending|in_review|observed|ready_for_analysis
GET    /managements/{id}
POST   /managements/{id}/evidence         (multipart: files[])
POST   /managements/{id}/transactions     (transacción manual)
PATCH  /transactions/{id}
POST   /transactions/{id}/reject
PATCH  /managements/{id}/advisor-notes
PATCH  /managements/{id}/status
```

## Calidad

```bash
uv run ruff format .
uv run ruff check .
uv run mypy src
```
