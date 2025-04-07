#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    unicode_literals,
    print_function
    )

import os
import locale
from time import (strftime)
from urllib.parse import quote_plus

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


# Datasets
DATASETS = os.path.dirname(os.getcwd()) + "/datasets"

# MongoDB Host
MONGOUSER = "bitzdb"
MONGOPASS = "OpenAI@2025#!"
MONGOURLS = "localhost"

MONGOHOST = "mongodb://%s:%s@%s" % (quote_plus(MONGOUSER), quote_plus(MONGOPASS), MONGOURLS)

# if no password
MONGOHOST = MONGOURLS

# Flask Secret
FLASKSECRET = "\xfb\x12\xdf\xa1@i\xd6>V\xc0\xbb\x8fp\x16#Z\x0b\x81\xeb\x16"

# Run Status
RUNSTATUS = "development"
