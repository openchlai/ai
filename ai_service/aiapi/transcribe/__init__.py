#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    unicode_literals,
    print_function
    )

import os
from threading import Thread

from . import solorunscribe

from pydoc import (
    locate)
from flask import (
    request,
    jsonify,
    Blueprint,
    render_template)
from flask.helpers import (
    send_file,
    url_for)
from logs import (
    logger)


scribe = Blueprint(
    'transcribe',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='assets'
    )

edir = os.path.dirname(os.path.realpath(__file__))

epath = edir + "/__init__.py"

def init():
    pass
    thread = Thread(target=solorunscribe.scribe_timer, args=({},))
    thread.daemon = True
    thread.start()
    return


"""
curl -X POST "localhost:50001/transcribe/{create, data, action, stats, index}/item" \
-H "Content-Type: application/json" \
--data "{}"
"""
@scribe.route("/create/<itemname>", methods=['POST'])
def create(itemname):
    logger.debug("""Transcribe Create""")

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + itemname)

        if path is not None:
            """Create Data"""
            data = path.indexcreate(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Create Transcribe-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404


@scribe.route("/data/<itemname>", methods=['POST'])
def data(itemname):
    logger.debug("""Transcribe Data""")

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + itemname)

        if path is not None:
            """Gather Data"""
            data = path.indexdata(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Data Transcribe-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404


@scribe.route("/action/<itemname>", methods=['POST'])
def action(itemname):
    logger.debug("""Transcribe Action: """ + itemname)

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + itemname)

        if path is not None:
            """Update Data"""
            data = path.indexaction(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Action Transcribe-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404


@scribe.route("/stats/<itemname>", methods=['POST'])
def stats(itemname):
    logger.debug("""Transcribe Stats: """ + itemname)

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + itemname)

        if path is not None:
            """Stats Data"""
            data = path.indexstats(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Stats Transcribe-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404


@scribe.route("/reset/<itemname>", methods=['POST'])
def resets(itemname):
    logger.debug("""Transcribe Reset: """ + itemname)

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + itemname)

        if path is not None:
            """Stats Data"""
            data = path.indexreset(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Stats Transcribe-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404
