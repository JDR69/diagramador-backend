Backend Django - Diagramador
============================

Este backend usa Django + DRF + Channels, con soporte para PostgreSQL y (opcional) Redis.

## Variables de Entorno Principales (.env)

Copiar este ejemplo (no subas credenciales reales al repositorio público):

```
SECRET_KEY=pon-una-key-segura
DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require

# Orígenes frontend permitidos (separados por coma). Si vacío y DEBUG=True => permite todo
FRONTEND_ORIGINS=http://localhost:3000

# Redis (opcional para Channels). Si no se define, usa memoria.
# Ejemplo: redis://:password@host:6379/0
REDIS_URL=

# Logging
LOG_LEVEL=INFO
LOG_SQL=False
```

## Instalación local

```
python -m venv .venv
./.venv/Scripts/activate  # Windows
pip install -r backend/requirements.txt
pip install psycopg[binary] channels_redis  # si usarás redis
```

## Migraciones
```
python backend/manage.py makemigrations
python backend/manage.py migrate
```

## Crear superusuario
```
python backend/manage.py createsuperuser
```

## Ejecutar servidor
```
python backend/manage.py runserver 0.0.0.0:8000
```

## Canales / WebSockets
Si defines `REDIS_URL`, Channels usará Redis. Si no, usará InMemory (solo para desarrollo). Para producción usa Redis siempre.

## Ajustar CORS
- Define `FRONTEND_ORIGINS` para restringir.
- Si está vacío y `DEBUG=True`, se permite todo.

## Logging
- `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR)
- `LOG_SQL=True` para ver queries (recomendado solo en desarrollo)

## Errores Comunes
1. psycopg2/psycopg no instalado: instalar `psycopg[binary]`.
2. Null bytes en settings: asegurarse de guardar en UTF-8 sin BOM.
3. Timeout a Postgres remoto: revisar firewall/sslmode y credenciales.

---
Documentación generada automáticamente.