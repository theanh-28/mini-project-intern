import logging
import logging.config

from app.gateway.context import ContextStore


class CorrelationIdFilter(logging.Filter):
    """
    Bộ lọc để tự động chèn correlation_id từ ContextStore vào từng dòng log.
    """
    def filter(self, record):
        try:
            # Lấy correlation_id từ ContextStore hiện tại
            correlation_id = ContextStore.get_correlation_id()
        except Exception:
            correlation_id = None

        # Nếu không có correlation_id, mặc định hiển thị dấu gạch ngang "-"
        record.correlation_id = correlation_id or "-"
        return True


def setup_logging(debug: bool = False):
    """
    Khởi tạo và cấu hình hệ thống Logger cho API Gateway.
    """
    log_level = "DEBUG" if debug else "INFO"

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_id": {
                "()": CorrelationIdFilter,
            }
        },
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] [%(correlation_id)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "filters": ["correlation_id"],
            },
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
        "loggers": {
            "gateway": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        }
    }

    logging.config.dictConfig(LOGGING_CONFIG)
