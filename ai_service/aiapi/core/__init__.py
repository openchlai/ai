#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    unicode_literals,
    print_function
    )

import os
import random

from . import (
    creds)
from logs import (
    logger)
from config import (
    app_config)
from flask import (
    Flask,
    request,
    jsonify,
    redirect,
    Blueprint
    )
"""
from pydoc import (
    locate)
from flask_socketio import (
    SocketIO,
    emit
    )
from flask_restplus import (
    Api,
    Resource,
    fields,
    apidoc
    )
"""


def create_app(config_name):
    """Create App"""
    app = Flask(
        __name__,
        instance_relative_config=True
        )

    """
    socketio = SocketIO(
        app,
        debug=True,
        cors_allowed_origins="*",
         # async_mode="eventlet"
        )
    """

    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SECRET_KEY'] = creds.FLASKSECRET

    # api = Api(app)
    # apibp = Blueprint('api', __name__, url_prefix='/api')
    # app.register_blueprint(apibp)
    # app.register_blueprint(apidoc)

    # logger.debug("Register Main Dashboard Blueprint")
    from visuals import dash as dashbp
    app.register_blueprint(dashbp, url_prefix="/dashboard")

    # logger.debug("Register Transcription Blueprint")
    from transcribe import scribe as scribebp
    app.register_blueprint(scribebp, url_prefix="/transcribe")

    import transcribe
    transcribe.init()

    from models import casedata

    # logger.debug("Register Translation Blueprint")
    from translate import xlate as xlatebp
    app.register_blueprint(xlatebp, url_prefix="/translate")

    # Create Thread to Manage Keywords
    # from models import keywords
    # keywords.indexstats({"item": "runcreate"})

    casedata.indexinit()

    # Handle View Errors
    urls = ["https://pornhub.com", "https://sex.com", "https://piratesbay.se"]
    urls += ["https://google.com", "https://microsoft.com", "https://kremlin.ru"]

    @app.errorhandler(403)
    def forbidden(error):
        """Forbidden"""

        data = {}
        data['code'] = 403
        data['method'] = request.method
        data['remote'] = request.remote_addr
        data['realip'] = request.headers.get('X-Real-IP')
        data['forward'] = request.headers.get('X-Forwarded-For')

        # system.indexcreate(data)

        if request.method == "POST":
            return jsonify({}), 403
        return redirect(random.choice(urls))

    @app.errorhandler(404)
    def page_not_found(error):
        """Log Handle Hits"""

        data = {}
        data['code'] = 404
        data['method'] = request.method
        data['remote'] = request.remote_addr
        data['realip'] = request.headers.get('X-Real-IP')
        data['forward'] = request.headers.get('X-Forwarded-For')

        # system.indexcreate(data)

        if request.method == "POST":
            return jsonify({}), 404
        return redirect(random.choice(urls))

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Not Allowed"""

        data = {}
        data['code'] = 405
        data['method'] = request.method
        data['remote'] = request.remote_addr
        data['realip'] = request.headers.get('X-Real-IP')
        data['forward'] = request.headers.get('X-Forwarded-For')

        # system.indexcreate(data)

        if request.method == "POST":
            return jsonify({}), 405
        return redirect(random.choice(urls))

    @app.errorhandler(500)
    def internal_server_error(error):
        """Server Error"""

        data = {}
        data['code'] = 405
        data['method'] = request.method
        data['remote'] = request.remote_addr
        data['realip'] = request.headers.get('X-Real-IP')
        data['forward'] = request.headers.get('X-Forwarded-For')

        # system.indexcreate(data)

        if request.method == "POST":
            return jsonify({}), 500
        return redirect(random.choice(urls))

    return app
