# Despliegue ASGI (Daphne + Channels + WebSockets)

Este proyecto usa Django Channels y necesita que el proceso se inicie con **Daphne** (ASGI) y no con Gunicorn (WSGI).

## Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `backend/Procfile` | Procfile local dentro del subdirectorio backend. |
| `Procfile` (raíz)  | Procfile raíz para que Oryx / Azure lo detecte. |
| `backend/diagram_backend/asgi.py` | Punto de entrada ASGI (HTTP + WebSocket). |
| `backend/apps/diagrams/consumers.py` | Consumer de colaboración. |

## Comando de arranque

```
web: daphne -b 0.0.0.0 -p 8000 backend.diagram_backend.asgi:application
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
Quitar `gunicorn` de `backend/requirements.txt` o agregar un `startup command` manual (si el plan / portal lo permite).

---
Documento auxiliar generado automáticamente.