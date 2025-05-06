#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    unicode_literals,
    print_function
    )

import os

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


xlate = Blueprint(
    'translate',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='assets'
    )

edir = os.path.dirname(os.path.realpath(__file__))

epath = edir + "/__init__.py"


"""
curl -X POST "localhost:50001/translate/{create, data, action, stats, index}/item" \
-H "Content-Type: application/json" \
--data "{}"
"""
@xlate.route("/create/<filepath>/<filename>", methods=['POST'])
def create(filepath, filename):
    logger.debug("""Translate Create""")

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + filepath + '.' + filename)

        if path is not None:
            """Create Data"""
            data = path.indexcreate(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Create Translate-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404


@xlate.route("/data/<filepath>/<filename>", methods=['POST'])
def data(filepath, filename):
    logger.debug("""Translate Data""")

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + filepath + '.' + filename)

        if path is not None:
            """Gather Data"""
            data = path.indexdata(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Data Translate-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404


@xlate.route("/action/<filepath>/<filename>", methods=['POST'])
def action(filepath, filename):
    logger.debug("""Translate Action: """ + filepath)

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + filepath + '.' + filename)

        if path is not None:
            """Update Data"""
            data = path.indexaction(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Action Translate-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404


@xlate.route("/stats/<filepath>/<filename>", methods=['POST'])
def stats(filepath, filename):
    logger.debug("""Translate Stats: """ + filepath)

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + filepath + '.' + filename)

        if path is not None:
            """Stats Data"""
            data = path.indexstats(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Stats Translate-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404


@xlate.route("/reset/<filepath>/<filename>", methods=['POST'])
def resets(filepath, filename):
    logger.debug("""Translate Reset: """ + filepath)

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + filepath + '.' + filename)

        if path is not None:
            """Stats Data"""
            data = path.indexreset(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Stats Translate-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404
