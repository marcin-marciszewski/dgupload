import logging
import logging.config


def configure_logging():
    logging_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[%(asctime)s: %(levelname)s] [%(pathname)s:%(lineno)d] %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "loggers": {
            "project": {
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(logging_dict)
    from celery.app.log import TaskFormatter

    celery_logger = logging.getLogger("celery")
    for handler in celery_logger.handlers:
        handler.setFormatter(
            TaskFormatter(
                "[%(asctime)s: %(levelname)s/%(processName)s/%(thread)d] [%(task_name)s(%(task_id)s)] %(message)s"
            )
        )
