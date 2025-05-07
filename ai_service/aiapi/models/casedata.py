#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    unicode_literals,
    print_function
    )

from datetime import datetime
import hashlib
import os
import json
import random
import string
import pandas as pd

from time import (
    mktime,
    strftime,
    time)
from core import (
    creds)
from logs import (
    logger)
from bson.objectid import (
    ObjectId)
from pymongo import MongoClient

client = MongoClient(creds.MONGOHOST)
db = client.helpline


def indexinit():
    """Create Synthetic Data"""

    try:
        data = creds.DATASETS + "/casesdata.json"

        with open(data, 'r') as fp:
            data = json.load(fp)

        if not db.helpline_casedata.count_documents({}):
            # db.helpline_casedata.delete_many({"demo": True})

            edit = {}
            # edit['demo'] = True
            edit['admin'] = {}
            edit['audit'] = []
            edit['created'] = int(time())

            db.helpline_casedata.insert_many(data)
            db.helpline_casedata.update_many({},{"$set": edit})

    except Exception as e:
        print("Error Init {}".format(e))

    return


def indexcreate(dat):
    # print("""Create Helpline-Case Entry""",dat)

    data = {}
    data['data'] = False
    data['error'] = False
    data['status'] = "pending"

    try:

        if db.helpline_casedata.count_documents({
            "meta": dat['meta'],
            "status": {"$ne": ['deleted', 'expired']},
            }):
            logger.warn("""FIX-ME""")
            x = db.helpline_casedata.find_one({
                "meta": dat['meta'],
                "init": {"$gte": dat['init']},
                "exit": {"$lte": dat['exit']},
                "status": {"$ne": ['completed', 'expired']},
                })

            data['data'] = True
            data['track'] = x.get('track')
            data['status'] = x.get('status')

            return data

        data['track'] = False

        tracks = list(set(string.digits))
        tracks += list(set(string.ascii_uppercase))

        while True:
            random.shuffle(tracks)
            track = "".join(tracks[0:12])
            if not db.helpline_casedata.count_documents({
                "track": track}):
                data['track'] = track
                break

        if 'fees' not in dat:
            dat['fees'] = 0

        x = db.helpline_casedata.insert_one(dat)

        data['id'] = str(x.inserted_id)

        if 'edit' in dat and type(dat['edit']) == dict and len(dat['edit']):
            db.helpline_casedata.update_one({
                "track": data['track']},{"$set": dat['edit']})

    except Exception as e:
        data['error'] = "Error Module Helpline Case Create Helpline-Case {}".format(e)
        logger.critical(data['error'])

    if data['error'] and 'id' in data:
        db.helpline_casedata.delete_one({"_id": ObjectId(data['id'])})
        del data['id']

    data['data'] = True

    return data


def indexdata(dat):
    # print("""Data Helpline-Case""", dat)
    data = {}
    data['data'] = False
    data['error'] = False
    data['prev'] = False
    data['next'] = False
    data['meta'] = []

    try:

        query = {}
        multi = False

        if 'id' in dat:
            """Track"""
            query['_id'] = ObjectId(dat['id'])
        else:
            """Data"""
            multi = True
            query['status'] = {"$ne": "deleted"}

            if 'today' in dat:
                pass

            if 'week' in dat:
                pass

            if 'month' in dat:
                pass

            if 'status' in dat:
                query['status'] = dat['status']

            if 'next' in dat and dat['next']:
                query['_id'] = {"$gte": ObjectId(dat['next'])}

            elif 'prev' in dat and dat['prev']:
                query['_id'] = {"$lte": ObjectId(dat['prev'])}

        if 'docs' not in dat:
            """Limit Docs"""
            dat['docs'] = 25

        df = pd.DataFrame(list(db.helpline_casedata.find(
            query).limit(dat['docs'])))            
        data['total'] = db.helpline_casedata.count_documents({
            "status": {"$ne": "deleted"}})

        if len(df):
            df['_id'] =  df._id.apply(str)
            df = df.rename(columns={"_id": "id"})
            # df = (df.pipe(utils.df_pipe_created))
            # df = df.drop(columns=['created'])
            df = df.where(df.notna(), lambda x: [{}])
            df = df.to_json(orient='records')
            data['meta'] = json.loads(df)
            if not multi:
                data = data['meta'][0]
                data['error'] = False
            else:
                if 'next' in dat and dat['next']:
                    data['prev'] = dat['next']
                if db.helpline_casedata.count_documents({
                    "_id": {"$gt": ObjectId(data['meta'][-1]["id"])}}):
                    """Gather Next"""
                    x = db.helpline_casedata.find_one({
                        "_id": {"$gt": ObjectId(data['meta'][-1]["id"])}
                        })
                    data['next'] = str(x.get('_id'))

            del df

        data['module'] = "Helpline Case Data"

        data['data'] = True
    except Exception as e:
        data['error'] = "Error Module Helpline Case Data {}".format(e)
        logger.critical(data['error'])

    return data


def indexinfo(dat):
    """Info Helpline-Case Metadata"""
    data = {}
    data['data'] = False
    data['error'] = False
    try:
        edit = {}
        info = {}
        if 'track' in dat:
            info['track'] = dat['track']
        elif 'id' in dat:
            info['_id'] = ObjectId(dat['id'])
        else:
            data['error'] = "Helpline-Case Metadata Error. "
            data['error'] += "One-Of `track` or `id`."
            data['data'] = True
            return data

        if not db.helpline_casedata.count_documents(info):
            data['error'] = "Helpline-Case Metadata Info "
            data['error'] += "Data not Found"
            data['data'] = True
            return data

        x = db.helpline_casedata.find_one(info)

        if 'item' in dat:
            data[dat['item']] = x.get(dat['item'])
            data['data'] = True

    except Exception as e:
        data['error'] = "Error Module Helpline Case Info {}".format(e)
        logger.critical(data['error'])

    return data


def indexaction(dat):
    """Action Book"""
    data = {}
    data['data'] = False
    data['error'] = False
    try:
        edit = {}
        audit = {}

        demo = False
        if 'demo' in dat and dat['demo']:
            demo = dat['demo']

        created = int(time())
        if 'created' in dat and dat['created']:
            created = int(dat['created'])

        info = {}
        if 'track' in dat:
            info['track'] = dat['track']
        elif 'id' in dat:
            info['_id'] = ObjectId(dat['id'])
        else:
            data['error'] = "Helpline-Case Metadata Error. "
            data['error'] += "One-Of `track` or `id`."
            data['data'] = True
            return data

        if not db.helpline_casedata.count_documents(info):
            data['error'] = "Helpline-Case Metadata Action "
            data['error'] += "Data not Found"
            data['data'] = True
            return data

        x = db.helpline_casedata.find_one(info)

        if dat['item'] in ["multipull", "pull"]:
            """Update and Audit"""
            db.helpline_casedata.update_one(
                {"track": x.get('track')},
                {"$unset": {dat['pull']: ""}}
                )

        if dat['item'] in ["multiedit", "edit"] or len(edit):
            """Update and Audit"""
            if len(edit):
                dat['edit'] = edit
            db.helpline_casedata.update_one(
                {"track": x.get('track')},
                {"$set": dat['edit']}
                )

        if dat['item'] in ["multiaudit", "audit"] or len(audit):
            """Update and Audit"""
            if len(audit):
                dat['audit'] = audit
            dat['audit']['createdate'] = datetime.fromtimestamp(
                int(time())).strftime('%d %B %Y')
            dat['audit']['createtime'] = datetime.fromtimestamp(
                int(time())).strftime('%H:%M:%S %p')
            db.helpline_casedata.update_one(
                {"track": x.get('track')},
                {"$push": {"audit": dat['audit']}}
                )

        data['data'] = True
    except Exception as e:
        data['error'] = "Error Module Helpline Case Action {}".format(e)
        logger.critical(data['error'])

    return data


def indexstats(dat):
    """Stats Helpline-Case """

    data = {}
    data['data'] = False
    data['error'] = False

    try:
        tdy = int(mktime(datetime(
            int(strftime('%Y')),
            int(strftime('%m')),
            int(strftime('%d'))
            ).timetuple()))

        if dat['item'] == "unsetdata":
            logger.debug("""Reset Helpline Case Data""")

            data['entries'] = db.helpline_casedata.count_documents(
                {dat['keys']: {"$ne": None}})
            
            if data['entries']:
                db.helpline_casedata.update_many(
                    {dat['keys']: {"$ne": None}},
                    {"$unset": {dat['keys']: ""}}
                    )

        if dat['item'] == "diarized":
            # logger.debug("Helpline-Case Info")

            data['stats'] = {}
            data['diary'] = {}

        if dat['item'] == "dummy":

            data['diary'] = {}


        data['data'] = True
    except Exception as e:
        data['error'] = "Error Module Helpline Case Stats {}".format(e)
        logger.critical(data['error'])

    return data


def indexapis(dat):
    # print("""API-Access""",dat)
    data = {}
    data['data'] = False
    data['error'] = False
    
    try:
        data['data'] = True
    except Exception as e:
        data['error'] = "Error Module Helpline Case APIs {}".format(e)
        logger.critical(data['error'])

    return data


def indexreset(dat=False):
    """Helpline-Case Reset"""
    data = {}
    data['data'] = False
    data['error'] = False

    try:
        data['source'] = "Helpline Case Data"

        if dat and 'stats' in dat:
            """App-Stats"""
            data['stats'] = db.helpline_casedata.count_documents({})

        elif dat and 'track' in dat:
            """Delete Specific Item"""
            data['meta'] = db.helpline_casedata.count_documents({
                "track": dat['track']
                })
            if data['meta']:
                x = db.helpline_casedata.find_one({
                    "track": dat['track']
                    })
                edit = {}
                edit['track'] = hashlib.sha256(
                    dat['track'].encode()
                    ).hexdigest()
                edit['phone'] = hashlib.sha256(
                    x.get('phone').encode()
                    ).hexdigest()
                edit['status'] = "deleted"
                edit['admin.deleted'] = int(time())
                db.helpline_casedata.update_one(
                    {"track": dat['track']},
                    {"$set": edit})

        elif dat and 'demo' in dat:
            """Delete Demo Metadatas"""
            data['demo'] =  db.helpline_casedata.count_documents({
                "demo": {"$ne": False}
                })
            if data['demo']:
                db.helpline_casedata.delete_many({
                    "demo": {"$ne": False},
                    })

        elif dat and 'backup' in dat:
            """Delete Demo Metadatas"""
            core = []
            if db.helpline_casedata.count_documents({}):
                df = pd.DataFrame(list(db.helpline_casedata.find({})))
                df = df.drop(columns=['_id'])
                df = df.to_json(orient='records')
                core = json.loads(df)

            backup = os.getcwd() + "/datasets/backup"
            if not os.path.isdir(backup):
                cmd = "mkdir -p " + backup

            if len(core):
                with open(backup + "/helpline_casedata.json", 'w') as fp:
                    fp.write(json.dumps(core, indent=2))

            data['meta'] = len(core)

        elif not dat and creds.RUNSTATUS == 'production':
            """Production Reset All"""
            data['meta'] = db.helpline_casedata.count_documents({})
            if data['meta']:
                edit = {}
                edit['status'] = "deleted"
                edit['admin.deleted'] = int(time())
                db.helpline_casedata.update_many(
                    {"status": {"$ne": "deleted"}},
                    {"$set": edit}
                    )

        elif not dat:
            """Dev Reset All"""
            data['meta'] = db.helpline_casedata.count_documents({})
            if data['meta']:
                db.helpline_casedata.delete_many({})
                
        data['data'] = True
    except Exception as e:
        data['error'] = "Error Module Helpline Case Reset {}".format(e)
        logger.critical(data['error'])

    return data
    