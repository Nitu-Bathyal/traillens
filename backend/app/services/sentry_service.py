from typing import Dict, Any, Optional
import sentry_sdk
from app.config import settings


def sanitize_sentry_event(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Ensure user privacy by stripping any raw images, base64 data,
    or GPS coordinates before sending events to Sentry.
    """
    if "request" in event:
        req = event["request"]
        # Remove multipart files / body if present
        if "data" in req and isinstance(req["data"], dict):
            for k in list(req["data"].keys()):
                if "image" in k.lower() or "base64" in k.lower() or "file" in k.lower():
                    req["data"][k] = "[REDACTED_IMAGE_DATA]"
                if "lat" in k.lower() or "lon" in k.lower():
                    req["data"][k] = "[REDACTED_GPS_DATA]"

    # Scrub extra tags
    if "extra" in event and isinstance(event["extra"], dict):
        for k in list(event["extra"].keys()):
            if "image" in k.lower() or "base64" in k.lower():
                event["extra"][k] = "[REDACTED]"

    return event


def init_sentry():
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            before_send=sanitize_sentry_event,
            environment=settings.APP_ENV,
            send_default_pii=False,
            attach_stacktrace=True
        )


def capture_inference_metric(latency_ms: float, model: str, success: bool):
    """Record custom inference telemetry span/metric."""
    if settings.SENTRY_DSN:
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("ai.model", model)
            scope.set_tag("ai.success", str(success))
            scope.set_extra("ai.latency_ms", latency_ms)
