"""Structured (JSON) logging.

Why JSON and not plain text: production logs are CONSUMED BY MACHINES
(Datadog, CloudWatch, Loki, ELK). A JSON line per event is queryable -
"show me all triage_failed events where latency_ms > 5000" - which plain
"print()" text never can be.
"""
import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    """Render each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "event": record.getMessage(),
            "logger": record.name,
        }
        # Structured fields are passed via logger.info(msg, extra={"fields": {...}})
        fields = getattr(record, "fields", None)
        if fields:
            payload.update(fields)
        # On errors, attach the full traceback so failures are debuggable.
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def get_logger(name: str = "support_router") -> logging.Logger:
    """Return a process-wide singleton logger with the JSON handler attached."""
    logger = logging.getLogger(name)
    if not logger.handlers:  # configure once
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False  # don't double-log via the root logger
    return logger
