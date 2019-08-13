from collections.abc import Mapping
from datetime import datetime
import logging

from typing import Optional

from stackdriver_log_formatter.serializer import DefaultFunc, dumps

class StackdriverLogFormatter(logging.Formatter):
    """Log formatter suitable for Stackdriver Logging.

    This formatter print log as a single-line json with appropriate fields.
    For detailed information about each fields, refer to Stackdriver's API document [1]_
    and fluent-plugin-google-cloud source [2]_.

    References
    ----------
    .. [1]: https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
    .. [2]: https://github.com/GoogleCloudPlatform/fluent-plugin-google-cloud

    Example
    -------
    >>> # setup
    >>> logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    >>> logging.root.handlers[0].setFormatter(StackdriverLogFormatter())

    >>> # logging
    >>> logger = logging.getLogger(__name__)
    >>> logger.info('Hello world')

    >>> # With custom fields (shown in 'jsonPayload' in Stackdriver)
    >>> logger.info('bla bla bla', {'customFiled': 123})
    >>> logger.info('bla bla bla: %(customeField)s', {'customFiled': 123})

    >>> # With exception
    >>> try:
    ...     1 / 0
    ... except Exception:
    ...     logger.exception('Oops, an error occured!')
    """
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self, *, default: DefaultFunc=None):
        """Initialize formatter.

        Keyword Arguments
        -----------------
        default: function or None, optional
            A function called to serialize non-standard objects.
            It should return a json serializable version of the object or raise a TypeError.
        """
        self.default = default

    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str]=None) -> str:
        """Return the creation time of the specified LogRecord as formatted text.

        The format is always ISO8601 in UTC ('Z'-suffixed), so `datefmt` argument is ignored.
        We use `datetime.datetime` rather than `time.time` to print subseconds.
        """
        return datetime.utcfromtimestamp(record.created).strftime(self.DATE_FORMAT)

    def usesTime(self) -> bool:
        """Check if the format uses the creation time of the record.

        This is always true.
        """
        return True

    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record as text.

        This will be a single-line json with appropriate fields.
        """

        record.message = record.getMessage()
        record.asctime = self.formatTime(record)
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

        log_obj = {
            'severity': record.levelname,
            'time': record.asctime,
            'message': record.message,
            'logger': record.name,
            'module': record.module,
            'logging.googleapis.com/sourceLocation': {
                'file': record.pathname,
                'line': record.lineno,
                'function': record.funcName,
            },
            'process': {
                'name': record.processName,
                'id': record.process,
            },
            'thread': {
                'name': record.threadName,
                'id': record.thread,
            },
        }
        if record.exc_info:
            log_obj['exceptionType'] = type(record.exc_info[1]).__name__
        if record.exc_text:
            log_obj['stackTrace'] = record.exc_text
        if record.stack_info:
            log_obj['stackInfo'] = self.formatStack(record.stack_info)

        if isinstance(record.args, Mapping):
            for k, v in record.args.items():
                if k in log_obj or k in ('exceptionType', 'stackTrace', 'stackInfo'):
                    continue
                log_obj.setdefault(k, v)

        return dumps(log_obj, default=self.default)
