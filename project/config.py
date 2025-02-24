from email.policy import default
import logging
import os
import pathlib
from functools import lru_cache
from kombu import Queue


def route_task(name, args, kwargs, options, task=None, **kw):
    if ":" in name:
        queue, _ = name.split(":")
        return {"queue": queue}
    return {"queue": "default"}


class BaseConfig:
    db_url = "postgresql://fastapi_celery:fastapi_celery@localhost/fastapi_celery"  # don't commit
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent

    DATABASE_URL: str = os.environ.get("DATABASE_URL", db_url)
    DATABASE_CONNECT_DICT: dict = {}
    CELERY_BROKER_URL: str = os.environ.get(
        "CELERY_BROKER_URL", "redis://127.0.0.1:6379/0"
    )  # NEW
    CELERY_RESULT_BACKEND: str = os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0"
    )  #
    WS_MESSAGE_QUEUE: str = os.environ.get("WS_MESSAGE_QUEUE")
    CELERY_BEAT_SCHEDULE: dict = {
        # "task-schedule-work": {"task": "task_schedule_work", "schedule": 5.0}
    }
    CELERY_TASK_DEFAULT_QUEUE: str = "default"
    CELERY_TASK_CREATE_MISSING_QUEUES: bool = False
    CELERY_TASK_QUEUES = (
        # need to define default queue here or exception would be raised
        Queue("default"),
        Queue("high_priority"),
        Queue("low_priority"),
    )

    CELERY_TASK_ROUTES = {"project.users.tasks.*": {"queue": "high_priority"}}

    CELERY_TASK_ROUTES = (route_task,)
    UPLOADS_DEFAULT_DEST: str = str(BASE_DIR / "upload")


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_CONNECT_DICT: dict = {"check_same_thread": False}


@lru_cache()
def get_settings():
    # logging.basicConfig(
    #     filename="log.txt",
    #     filemode="a",
    #     format="%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s",
    #     datefmt="%Y-%m-%d %H:%M:%S",
    #     level=logging.DEBUG,
    # )

    config_cls_dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    config_name = os.environ.get("FASTAPI_CONFIG", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
