import time
import logging
import os
from typing import Callable
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

SLOW_THRESHOLD_MS = float(os.environ.get("PERF_SLOW_MS", "800"))  # Ajustable vía env PERF_SLOW_MS

class PerformanceMiddleware:
    """Middleware simple para loguear duración de requests.
    Registra toda request y destaca las lentas (>SLOW_THRESHOLD_MS).
    Ajusta el umbral exportando PERF_SLOW_MS (en ms)."""
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()
        try:
            response = self.get_response(request)
            return response
        finally:
            dt_ms = (time.perf_counter() - start) * 1000
            path = request.path
            if dt_ms > SLOW_THRESHOLD_MS:
                logger.warning(f"[perf][slow] {request.method} {path} {dt_ms:.1f}ms status={getattr(response,'status_code', '?')}")
            else:
                logger.debug(f"[perf] {request.method} {path} {dt_ms:.1f}ms")
