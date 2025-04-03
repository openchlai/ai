#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    unicode_literals,
    print_function
    )

import os
import json
import pandas as pd

from time import (
    time)
from core import (
    creds)
from bson.objectid import (
    ObjectId)

client = MongoClient(creds.MONGOHOST)
db = client.helpline


def indexinit():
    """Create Synthetic Data"""

    try:
        data = creds.DATASET + "/casedata.json"

        with open(dat, 'r') as fp:
            data = json.load(fp)

        if db.helpline_casedata.count_documents({"demo": True}):
            db.helpline_casedata.delete_many({"demo": True})

        edit = {}
        edit['admin'] = {}
        edit['audit'] = []
        edit['created'] = int(time())

        db.helpline_casedata.insert_many(data)
        db.helpline_casedata.update_many({},{"$set": edit})

    except Exception as e:
        print("Error Init {}".format(e))

    return


def indexdata(dat):
    pass