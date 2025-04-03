#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    unicode_literals,
    print_function
    )

import logging
from core import (create_app)
from flask_twisted import (Twisted)
from flask_cors import (CORS)


app = create_app('development')

logging.getLogger('flask_cors').level = logging.DEBUG

CORS(
    app,
    resources=r'/*',
    allow_headers='Content-Type'
    )

twisted = Twisted(app)


if __name__ == "__main__":
    app.run(
        host='localhost',
        port=50001,
        threaded=True
        )
