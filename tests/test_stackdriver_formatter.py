from datetime import datetime
import json
import logging
from typing import List, Tuple

import freezegun
import pytest

import stackdriver_formatter


class OnmemoryHandler(logging.Handler):
    def __init__(self, level: int=logging.NOTSET):
        super().__init__(level)
        self.data: List[str] = []

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.data.append(msg)


LoggerAndData = Tuple[logging.Logger, List[str]]

@pytest.fixture
def logger_and_data() -> LoggerAndData:
    hdr = OnmemoryHandler()
    hdr.setFormatter(stackdriver_formatter.StackdriverLogFormatter())

    lgr = logging.getLogger('test_logger_for_stackdriver_formatter')
    lgr.setLevel(logging.DEBUG)
    lgr.propagate = False
    for h in lgr.handlers:
        lgr.removeHandler(h)
    lgr.addHandler(hdr)

    return lgr, hdr.data


@pytest.fixture(autouse=True)
def freezed_time():
    with freezegun.freeze_time(datetime(2020, 12, 31, 18, 55, 56, 123456)):
        yield


def test_info(logger_and_data: LoggerAndData):
    logger, data = logger_and_data
    logger.info('hello world')
    assert len(data) == 1

    # Make sure it is single line
    assert '\n' not in data[0]
    # Check content
    payload = json.loads(data[0])
    assert payload['severity'] == 'INFO'
    assert payload['time'] == '2020-12-31T18:55:56.123456Z'
    assert payload['message'] == 'hello world'
    assert payload['logger'] == 'test_logger_for_stackdriver_formatter'
    assert payload['module'] == 'test_stackdriver_formatter'
    assert payload['logging.googleapis.com/sourceLocation']['file'] == __file__
    assert payload['logging.googleapis.com/sourceLocation']['line'] == 47
    assert payload['logging.googleapis.com/sourceLocation']['function'] == 'test_info'
    assert payload['process']['name'] == 'MainProcess'
    assert isinstance(payload['process']['id'], int)
    assert payload['thread']['name'] == 'MainThread'
    assert isinstance(payload['thread']['id'], int)
    assert 'exceptionType' not in payload
    assert 'stackTrace' not in payload
    assert 'stackInfo' not in payload


def test_info_with_custom_data(logger_and_data: LoggerAndData):
    logger, data = logger_and_data
    logger.info('I have a data: %(value)d',
                {'value': 99, 'module': 'You cannot override!', 'stackInfo': 'Cannot override too'})
    assert len(data) == 1

    # Make sure it is single line
    assert '\n' not in data[0]
    # Check content
    payload = json.loads(data[0])
    assert payload['severity'] == 'INFO'
    assert payload['time'] == '2020-12-31T18:55:56.123456Z'
    assert payload['message'] == 'I have a data: 99'
    assert payload['logger'] == 'test_logger_for_stackdriver_formatter'
    assert payload['module'] == 'test_stackdriver_formatter'  # This is not overriden
    assert payload['logging.googleapis.com/sourceLocation']['file'] == __file__
    assert payload['logging.googleapis.com/sourceLocation']['line'] == 74
    assert payload['logging.googleapis.com/sourceLocation']['function'] == 'test_info_with_custom_data'
    assert payload['process']['name'] == 'MainProcess'
    assert isinstance(payload['process']['id'], int)
    assert payload['thread']['name'] == 'MainThread'
    assert isinstance(payload['thread']['id'], int)
    assert 'exceptionType' not in payload
    assert 'stackTrace' not in payload
    assert 'stackInfo' not in payload  # This is not overriden
    # Check custom fields
    assert payload['value'] == 99


def test_exception(logger_and_data: LoggerAndData):
    logger, data = logger_and_data
    try:
        raise RuntimeError('this is exception for the test')
    except RuntimeError:
        logger.exception('An error occured!')
    assert len(data) == 1

    # Make sure it is single line
    assert '\n' not in data[0]
    # Check content
    payload = json.loads(data[0])
    assert payload['severity'] == 'ERROR'
    assert payload['time'] == '2020-12-31T18:55:56.123456Z'
    assert payload['message'] == 'An error occured!'
    assert payload['logger'] == 'test_logger_for_stackdriver_formatter'
    assert payload['module'] == 'test_stackdriver_formatter'
    assert payload['logging.googleapis.com/sourceLocation']['file'] == __file__
    assert payload['logging.googleapis.com/sourceLocation']['line'] == 105
    assert payload['logging.googleapis.com/sourceLocation']['function'] == 'test_exception'
    assert payload['process']['name'] == 'MainProcess'
    assert isinstance(payload['process']['id'], int)
    assert payload['thread']['name'] == 'MainThread'
    assert isinstance(payload['thread']['id'], int)
    assert payload['exceptionType'] == 'RuntimeError'
    assert 'this is exception for the test' in payload['stackTrace'].splitlines()[-1]
    assert 'stackInfo' not in payload


def test_custom_exception(logger_and_data: LoggerAndData):
    logger, data = logger_and_data
    e = ValueError('this is custom exception for the test')
    logger.critical('I have a custom exception', exc_info=e)
    assert len(data) == 1

    # Make sure it is single line
    assert '\n' not in data[0]
    # Check content
    payload = json.loads(data[0])
    assert payload['severity'] == 'CRITICAL'
    assert payload['time'] == '2020-12-31T18:55:56.123456Z'
    assert payload['message'] == 'I have a custom exception'
    assert payload['logger'] == 'test_logger_for_stackdriver_formatter'
    assert payload['module'] == 'test_stackdriver_formatter'
    assert payload['logging.googleapis.com/sourceLocation']['file'] == __file__
    assert payload['logging.googleapis.com/sourceLocation']['line'] == 132
    assert payload['logging.googleapis.com/sourceLocation']['function'] == 'test_custom_exception'
    assert payload['process']['name'] == 'MainProcess'
    assert isinstance(payload['process']['id'], int)
    assert payload['thread']['name'] == 'MainThread'
    assert isinstance(payload['thread']['id'], int)
    assert payload['exceptionType'] == 'ValueError'
    assert 'this is custom exception for the test' in payload['stackTrace'].splitlines()[-1]
    assert 'stackInfo' not in payload


def test_stackinfo(logger_and_data: LoggerAndData):
    logger, data = logger_and_data
    logger.debug('show stack info', stack_info=True)
    assert len(data) == 1

    # Make sure it is single line
    assert '\n' not in data[0]
    # Check content
    payload = json.loads(data[0])
    assert payload['severity'] == 'DEBUG'
    assert payload['time'] == '2020-12-31T18:55:56.123456Z'
    assert payload['message'] == 'show stack info'
    assert payload['logger'] == 'test_logger_for_stackdriver_formatter'
    assert payload['module'] == 'test_stackdriver_formatter'
    assert payload['logging.googleapis.com/sourceLocation']['file'] == __file__
    assert payload['logging.googleapis.com/sourceLocation']['line'] == 158
    assert payload['logging.googleapis.com/sourceLocation']['function'] == 'test_stackinfo'
    assert payload['process']['name'] == 'MainProcess'
    assert isinstance(payload['process']['id'], int)
    assert payload['thread']['name'] == 'MainThread'
    assert isinstance(payload['thread']['id'], int)
    assert 'exceptionType' not in payload
    assert 'stackTrace' not in payload
    assert isinstance('stackInfo', str)
