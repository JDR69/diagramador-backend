#!/usr/bin/env bash
set -euo pipefail

echo "[startup] Using Daphne ASGI server"
# Azure normalmente expone el puerto 8000 dentro del contenedor/app
PORT_ENV=${PORT:-8000}
exec daphne -b 0.0.0.0 -p "$PORT_ENV" diagram_backend.asgi:application
