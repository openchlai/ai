#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    unicode_literals,
    print_function
    )

import logging
from time import (
    strftime)
from logging.handlers import (
    RotatingFileHandler)


class ContextFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """

    def filter(self, record):
        record.user_id = 'anonymous'
        # Imagine a function that retrieves the user ID from the current session
        # record.user_id = get_current_user_id()
        return True

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler that logs even debug messages
# fh = logging.FileHandler('klinik/runtime.log')
fh = RotatingFileHandler(
    'logs/runtime.log',
    maxBytes=16384000,
    backupCount=20
    )
fh.setLevel(logging.DEBUG)

# Create a console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# Create a formatter and set it for both handlers
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(user_id)s - %(message)s')
formatter = logging.Formatter(
    '[%(asctime)s] -- "%(filename)s" : "%(lineno)d" [-] "%(levelname)s" -- "%(message)s"'
    )
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add a filter to inject user ID
# filter = ContextFilter()
# logger.addFilter(filter)

# Add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
