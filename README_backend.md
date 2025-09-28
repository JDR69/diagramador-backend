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

## Despliegue en Azure App Service

### 1. Requisitos
- App Service Linux (recomendado para websockets) o Windows (con `web.config` ya incluido).
- Configurar en Azure las variables de entorno (Configuration > Application settings):
	- `SECRET_KEY`
	- `DJANGO_ALLOWED_HOSTS` (incluir tu dominio *.azurewebsites.net y el custom si existe)
	- `DATABASE_URL` (añadir `?sslmode=require` si tu proveedor lo exige)
	- `REDIS_URL` (si usas Channels con Redis gestionado)
	- `FRONTEND_ORIGINS`
	- `LOG_LEVEL`, `LOG_SQL`

### 2. Instalación de dependencias
Azure ejecutará `pip install -r backend/requirements.txt`. Asegúrate que la versión de Python del plan soporta Django 5.

### 3. Servidor ASGI
Usamos `daphne` para soportar HTTP + WebSockets. Archivo `Procfile`:
```
web: daphne -b 0.0.0.0 -p $PORT diagram_backend.asgi:application
```
En Windows App Service `web.config` ya lanza daphne.

### 4. Migraciones automáticas (opcional)
Puedes agregar un comando de inicio (Startup Command) en Azure:
```
python backend/manage.py migrate && daphne -b 0.0.0.0 -p $PORT diagram_backend.asgi:application
```
o ejecutar manualmente via SSH / consola de Azure después del deploy.

### 5. Archivos estáticos
Ejecuta una vez:
```
python backend/manage.py collectstatic --noinput
```
Puedes automatizarlo añadiéndolo al Startup Command antes de `migrate`.

### 6. Salud / verificación
- Ver logs en Log Stream.
- Probar `ws://<app>.azurewebsites.net/ws/collaboration/test/` (usar wss:// si tu front está en HTTPS).

### 7. Escalabilidad
- Configura Redis real (no InMemory) para múltiples instancias.
- Ajusta número de workers daphne usando variable `DAPHNE_WORKERS` (puedes crear un script de arranque si quieres tuning avanzado).

### 8. Seguridad
- Nunca subir `.env` real.
- Rotar `SECRET_KEY` sólo si aceptas invalidar sesiones.
- Limitar CORS a dominios productivos.


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