import logging
import sys
import structlog
from structlog.processors import JSONRenderer

class PrettyJSONRenderer(JSONRenderer):
    def __init__(self, **kwargs):
        kwargs["ensure_ascii"] = False  #  păstrăm diacriticele ca atare
        super().__init__(**kwargs)


def configure_logging():
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            PrettyJSONRenderer()  # în loc de JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Logger global disponibil în restul aplicației
logger = structlog.get_logger()
