"""
Logging configuration module.
Provides structured logging using `structlog` for JSON-based log aggregation.
"""

import logging
import sys
import structlog
from structlog.processors import JSONRenderer

class PrettyJSONRenderer(JSONRenderer):
    """
    Custom JSON renderer with UTF-8 encoding and diacritics support.

    Args:
        kwargs: Additional arguments for JSON rendering.
    """
    def __init__(self, **kwargs):
        kwargs["ensure_ascii"] = False  
        super().__init__(**kwargs)

def configure_logging():
    """
    Configures logging for the application.

    Sets up `structlog` for structured JSON logging and redirects logs to stdout.
    Useful for Docker environments and log aggregation tools like Logstash, Kibana, or Grafana.
    """
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,  # Redirect logs to stdout
        level=logging.INFO,  # Set default log level to INFO
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            PrettyJSONRenderer()  
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Global logger instance available throughout the application
logger = structlog.get_logger()

# This logger outputs structured logs in JSON format, suitable for log aggregation and analysis.
# It can be integrated with modern tools like Logstash, Kibana, or Grafana.