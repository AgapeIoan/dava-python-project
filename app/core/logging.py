import logging
import sys
import structlog
from structlog.processors import JSONRenderer

class PrettyJSONRenderer(JSONRenderer): # UTF-8 encoding with diacritics support
    def __init__(self, **kwargs):
        kwargs["ensure_ascii"] = False  
        super().__init__(**kwargs)


def configure_logging(): #
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout, # Redirect logs to stdout, useful for Docker
        level=logging.INFO, # Set level to INFO by default
    )

    structlog.configure( #useful for JSON logging
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


# This logger can be used in modern tools like Logstash, Kibana, or Grafana
# It outputs structured logs in JSON format, which is suitable for log aggregation and analysis.