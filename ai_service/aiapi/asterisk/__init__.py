#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    unicode_literals,
    print_function)

import os
import functools

from logs import (
    logger)
from flask import (
    request)
from flask_socketio import (
    emit,
    disconnect,
    ConnectionRefusedError)
from asterisk.astsocket import (
    IOBlueprint)


calls = IOBlueprint('asterisk', __name__)

edir = os.path.dirname(os.path.realpath(__file__))

epath = edir + "/__init__.py"


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not is_logged_in():
            disconnect()
        else:
            return f(*args, **kwargs)

    return wrapped


@calls.on('connect')
def connect():
    if not is_logged_in():
        raise ConnectionRefusedError('unauthorized!')
    emit('flash', 'Welcome ' + request.remote_user)  # context aware emit


@calls.on('echo')
# @authenticated_only
def on_alive(data):
    logger.debug(data)
    emit('echo', data)  # context aware emit


@calls.on('broadcast')
# @authenticated_only
def on_broadcast(data):
    logger.debug(data)
    bp.emit('broadcast', data)  # bp.emit same as socketio.emit
