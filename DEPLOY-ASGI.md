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
CHANNELS_ENABLE_REDIS=false  # dejar en false hasta permitir IPs en Redis
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

## Errores comunes

### `Client IP address is not in the allowlist.`
Proviene de tu instancia de Redis administrada (por ejemplo Azure Cache for Redis) que tiene un firewall / allowlist. El contenedor de App Service se conecta desde IPs internas dinámicas y si no están permitidas, Redis rechaza el handshake y Channels no puede unir el grupo; el WebSocket se cierra.

El ajuste en `settings.py` ahora:
1. Intenta `PING` a Redis al inicio.
2. Si falla (timeout / allowlist / auth), imprime:
   ```
   [settings] Redis no disponible, usando InMemoryChannelLayer. Motivo: ...
   ```
3. Hace fallback automático a capa en memoria (funciona, pero sin coordinación entre múltiples instancias / escalado horizontal).

Soluciones definitivas:
* Agregar las IP de salida de tu App Service al firewall del Redis (en Azure Portal: Redis > Networking > Firewall & VNet).
* O usar una VNet integrada.
* O (para desarrollo) crear un Redis sin firewall restrictivo.

Mientras no tengas Redis accesible, la colaboración multi‑usuario simultánea entre instancias distintas no será consistente (en un solo contenedor sí funciona). Para pruebas locales o un único plan básico es suficiente.

### `Invalid HTTP_HOST header: '169.254.130.x:8000'`
Se agregaron automáticamente esas IPs internas (health probes) a `ALLOWED_HOSTS`. Si vuelve a aparecer, revisa `DJANGO_ALLOWED_HOSTS` o sobrescrituras en variables de entorno.
