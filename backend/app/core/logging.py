import logging
import json
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "trace_id": getattr(record, "trace_id", None),
            "dispute_id": getattr(record, "dispute_id", None),
            "event": getattr(record, "event", None),
        }
        return json.dumps({k: v for k, v in log_record.items() if v is not None})

def setup_logging(level: str = "INFO"):
    logger = logging.getLogger("dispute_sentinel")
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    return logger
