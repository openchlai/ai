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


dash = Blueprint(
    'dashboard',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='assets'
    )

edir = os.path.dirname(os.path.realpath(__file__))

epath = edir + "/__init__.py"


"""
curl -X POST "localhost:50001/dashboard/{create, data, action, stats, index}/item" \
-H "Content-Type: application/json" \
--data "{}"
"""
@dash.route("/create/<filepath>/<filename>", methods=['POST'])
def create(filepath, filename):
    logger.debug("""Dashboard Create""")

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + filepath + '.' + filename)

        if path is not None:
            """Create Data"""
            data = path.indexcreate(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Create Dashboard-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404


@dash.route("/data/<filepath>/<filename>", methods=['POST'])
def data(filepath, filename):
    logger.debug("""Dashboard Data""")

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + filepath + '.' + filename)

        if path is not None:
            """Gather Data"""
            data = path.indexdata(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Data Dashboard-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404


@dash.route("/action/<filepath>/<filename>", methods=['POST'])
def action(filepath, filename):
    logger.debug("""Dashboard Action: """ + itemname)

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + filepath + '.' + filename)

        if path is not None:
            """Update Data"""
            data = path.indexaction(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Action Dashboard-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404


@dash.route("/stats/<filepath>/<filename>", methods=['POST'])
def stats(filepath, filename):
    logger.debug("""Dashboard Stats: """ + itemname)

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + filepath + '.' + filename)

        if path is not None:
            """Stats Data"""
            data = path.indexstats(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Stats Dashboard-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404


@dash.route("/reset/<filepath>/<filename>", methods=['POST'])
def resets(filepath, filename):
    logger.debug("""Dashboard Reset: """ + itemname)

    try:

        data = {}
        x = request.get_json()

        path = locate('models.' + filepath + '.' + filename)

        if path is not None:
            """Stats Data"""
            data = path.indexreset(x)

        return jsonify(data)

    except Exception as e:
        data['error'] = "Error Index-Stats Dashboard-Core {}".format(e)
        logger.critical(data['error'])

    return jsonify(data), 404
