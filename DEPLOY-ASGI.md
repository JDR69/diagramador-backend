# Despliegue ASGI (Daphne + Channels + WebSockets)

Este proyecto usa Django Channels y necesita que el proceso se inicie con **Daphne** (ASGI) y no con Gunicorn (WSGI).

## Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `Procfile` | Indica a Azure que debe iniciar Daphne (ASGI). |
| `runtime.txt` | Fija versión de Python (3.13.0). |
| `startup.sh` | Fallback manual si Procfile es ignorado (configurar STARTUP_COMMAND). |
| `diagram_backend/asgi.py` | Punto de entrada ASGI (HTTP + WebSocket). |
| `apps/diagrams/consumers.py` | Consumer de colaboración (Channels). |

## Comando de arranque

```
web: daphne -b 0.0.0.0 -p 8000 diagram_backend.asgi:application
```

## Variables requeridas

```
REDIS_URL=rediss://default:<password>@<host>:6379/0
DJANGO_ALLOWED_HOSTS=diagram-class-backend-xxxxx.azurewebsites.net,localhost,127.0.0.1
FRONTEND_ORIGINS=http://localhost:3000,https://<frontend>.azurewebsites.net
```

## Pasos en Azure App Service (Linux)
1. Subir código a main.
2. Confirmar en logs de build que se detecta el **Procfile**.
3. En Configuración > Variables agregar las variables de arriba.
4. Reiniciar.
5. Ver en logs de arranque: `Daphne running` y `Loaded clean UTF-8 settings file | Redis: ON`.
6. Probar WebSocket con:
   ```
   wscat -c wss://<backend>/ws/collaboration/test/
   ```

## Si aún se levanta Gunicorn
1. Verifica que en el deployment realmente se sube este `Procfile`.
2. Asegura variables (opcional): `ENABLE_ORYX_BUILD=true`, `WEBSITES_PORT=8000`.
3. Configura en Azure App Service > Configuración > General un **Startup Command**:
   ```
   bash startup.sh
   ```
4. Revisa logs de arranque: debe aparecer `[startup] Using Daphne ASGI server` y luego logs de Daphne.

---
Documento auxiliar generado automáticamente.