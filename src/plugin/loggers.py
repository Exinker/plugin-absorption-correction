import json
import logging
import logging.config
from datetime import datetime, timezone

from plugin import ROOT
from plugin.configs.logging_config import LoggingConfig


class JsonRecordFormatter(logging.Formatter):

    RECORD_KEYS = {
        'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName',
        'levelname', 'levelno', 'lineno', 'module', 'msecs', 'msg', 'name',
        'pathname', 'relativeCreated', 'process', 'processName', 'stack_info',
        'taskName', 'thread', 'threadName',
    }

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:

        data = dict(
            timestamp=datetime.fromtimestamp(
                timestamp=record.created,
                tz=timezone.utc,
            ).isoformat(),
            level=record.levelname,
            msg=record.getMessage(),
        )
        if record.exc_info:
            data['error'] = self.formatException(record.exc_info)

        extra = dict()
        for key, value in record.__dict__.items():
            if key not in self.RECORD_KEYS:
                extra[key] = value

        return json.dumps(dict(
            **data,
            **extra,
        ), ensure_ascii=False, default=str)


def setup_logging(
    config: LoggingConfig,
) -> None:

    config = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'formatter': {
                '()': JsonRecordFormatter,
            },
        },

        'handlers': {
            'stream_handler': {
                'class': 'logging.StreamHandler',
                'level': config.level.value,
                'filters': [],
                'formatter': 'formatter',
            },
            'file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': config.level.value,
                'filename': str(ROOT / '.log'),
                'mode': 'a',
                'maxBytes': config.file_bytes,
                'backupCount': config.file_backups,
                'formatter': 'formatter',
                'encoding': 'utf-8',
            },
        },

        'loggers': {
            'plugin-absorption-correction': {
                'level': logging.DEBUG,
                'handlers': ['stream_handler', 'file_handler'],
                'propagate': True,
            },
        },

    }
    logging.config.dictConfig(config)
