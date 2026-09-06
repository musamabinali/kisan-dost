"""Tracing setup for OpenAI Agents SDK."""

from specialists import set_tracing_disabled, set_tracing_export
from config import settings
import logging

logger = logging.getLogger(__name__)

def setup_tracing():
    """Configure SDK tracing based on settings."""
    if not settings.agents_sdk_tracing_enabled:
        set_tracing_disabled(True)
        logger.info("Tracing disabled")
        return
    
    # Configure export
    if settings.agents_sdk_trace_export == "console":
        set_tracing_export("console")
        logger.info("Tracing enabled: console export")
    elif settings.agents_sdk_trace_export == "file":
        # File export - SDK handles this
        logger.info(f"Tracing enabled: file export to {settings.agents_sdk_trace_file}")
    elif settings.agents_sdk_trace_export == "otlp":
        logger.info("Tracing enabled: OTLP export")
    
    # In production, you might configure:
    # - Custom exporters (Jaeger, Zipkin, OTLP)
    # - Sampling rates
    # - Span processors

def get_trace_url(trace_id: str) -> str:
    """Generate trace URL for viewing."""
    # If using OpenAI platform
    return f"https://platform.openai.com/traces/{trace_id}"