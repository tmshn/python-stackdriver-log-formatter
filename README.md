# python-stackdriver-log-formatter

[![Build Status](https://travis-ci.com/tmshn/python-stackdriver-log-formatter.svg?branch=master)](https://travis-ci.com/tmshn/python-stackdriver-log-formatter)

[![PyPI version](https://img.shields.io/pypi/v/stackdriver-log-formatter.svg)](https://pypi.python.org/pypi/stackdriver-log-formatter/)

Python log formatter for Google Stackdriver Logging.

## Usage

```python
>>> # setup
>>> import logging, sys
>>> from stackdriver_log_formatter import StackdriverLogFormatter
>>> logging.basicConfig(level=logging.INFO, stream=sys.stdout)
>>> logging.root.handlers[0].setFormatter(StackdriverLogFormatter())
>>> # logging
>>> logger = logging.getLogger(__name__)
>>> logger.info('Hello world')
```
