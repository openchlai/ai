#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (
    unicode_literals,
    print_function
    )

import os
import json
import pandas as pd
import phonenumbers

from time import (
    time)
from core import (
    creds)
from logs import (
    logger)
from pymongo import (
    MongoClient)
from bson.objectid import (
    ObjectId)
from phonenumbers import (
    geocoder,
    carrier,
    timezone)

client = MongoClient(creds.MONGOHOST)
db = client.helpline

edir = os.path.dirname(os.path.realpath(__file__))
epath = edir + "/phonedata.py"


def indexinit():
    """Create Synthetic Data"""

    try:
        data = []
        dat = creds.DATASETS + "/phonedata.json"

        if os.path.isfile(dat):
            with open(dat, 'r') as fp:
                data = json.load(fp)

        if len(data) and not db.helpline_phonedata.count_documents({}):
            # db.helpline_phonedata.delete_many({"demo": True})

            edit = {}
            # edit['demo'] = True
            edit['admin'] = {}
            edit['audit'] = []
            edit['created'] = int(time())

            db.helpline_phonedata.insert_many(data)
            db.helpline_phonedata.update_many({},{"$set": edit})

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

        if db.helpline_phonedata.count_documents({
            "phone": dat['phone'],
            "status": {"$nin": ['deleted']},
            }):
            logger.warn("""FIX-ME""")
            x = db.helpline_phonedata.find_one({
                "phone": dat['phone'],
                "status": {"$nin": ['deleted']},
                })

            data['data'] = True
            data['id'] = str(x.get('_id'))
            data['status'] = x.get('status')

            return data

        phone = "".join([x for x in dat['phone'] if x.isdigit()])

        pn = phonenumbers.parse("+" + phone)
        if not phonenumbers.is_valid_number(pn):
            data['error'] = "Not A Valid Phone Number"
            logger.error(data['error'] + " +" + phone)
            return data

        elif not phonenumbers.is_possible_number(pn):
            data['error'] = "Not a Possible Phone Number"
            ogger.error(data['error'] + " +" + phone)
            return data

        dat['network'] = carrier.name_for_number(pn, 'en')
        dat['timezone'] = timezone.time_zones_for_number(pn)[0]
        dat['country'] = geocoder.country_name_for_number(pn, 'en')
        dat['region'] = geocoder.description_for_number(pn,'en')

        x = db.helpline_phonedata.insert_one({
            "admin": {},
            "audit": [],
            "phone": phone,
            "status": "active",
            "created": int(time()),
            "source": dat['source'],  # manual, call, chat
            "network": carrier.name_for_number(pn, 'en'),
            "timezone": timezone.time_zones_for_number(pn)[0],
            "region": geocoder.description_for_number(pn,'en'),
            "country": geocoder.country_name_for_number(pn, 'en'),
            })

        data['id'] = str(x.inserted_id)

        if 'edit' in dat and type(dat['edit']) == dict and len(dat['edit']):
            db.helpline_phonedata.update_one({
                "_id": x.inserted_id},
                {"$set": dat['edit']})

    except Exception as e:
        data['error'] = "Error Module Helpline Call Create Helpline-Case {}".format(e)
        logger.critical(data['error'])

    if data['error'] and 'id' in data:
        db.helpline_phonedata.delete_one({"_id": ObjectId(data['id'])})
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

        df = pd.DataFrame(list(db.helpline_phonedata.find(
            query).limit(dat['docs'])))            
        data['total'] = db.helpline_phonedata.count_documents({
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
                if db.helpline_phonedata.count_documents({
                    "_id": {"$gt": ObjectId(data['meta'][-1]["id"])}}):
                    """Gather Next"""
                    x = db.helpline_phonedata.find_one({
                        "_id": {"$gt": ObjectId(data['meta'][-1]["id"])}
                        })
                    data['next'] = str(x.get('_id'))

            del df

        data['module'] = "Helpline Call Data"

        data['data'] = True
    except Exception as e:
        data['error'] = "Error Module Helpline Call Data {}".format(e)
        logger.critical(data['error'])

    return data


def indexinfo(dat):
    """Info Helpline-Case Metadata"""

    data = {}
    data['data'] = False
    data['error'] = False

    try:
        
        pass

    except Exception as e:
        data['error'] = "Error Module Helpline Call Info {}".format(e)
        logger.critical(data['error'])

    return data


def indexaction(dat):
    logger.debug("""Helpline Call Action """ + str(dat))

    data = {}
    data['data'] = False
    data['error'] = False

    try:
        
        edit = {}
        audit = {}
        info = {}

        if 'track' in dat:
            info['track'] = dat['track']
        elif 'id' in dat:
            info['_id'] = ObjectId(dat['id'])
        else:
            data['error'] = "Call Metadata Error. One-Of `track` or `id`."
            return data

        if not db.helpline_phonedata.count_documents(info):
            data['error'] = "Call Metadata Action Data not Found"
            return data

        x = db.helpline_phonedata.find_one(info)

        if dat['item'] == "pull":
            """Update and Audit"""
            db.helpline_phonedata.update_one(
                {"track": x.get('track')},
                {"$unset": {dat['pull']: ""}}
                )

        if dat['item'] == "push":
            """Update and Audit"""
            db.helpline_phonedata.update_one(
                {"track": x.get('track')},
                {"$push": {dat['push']: dat['data']}}
                )

        if dat['item'] == "edit" or len(edit):
            """Update and Audit"""
            if len(edit):
                dat['edit'] = edit
            db.helpline_phonedata.update_one(
                {"track": x.get('track')},
                {"$set": dat['edit']}
                )

        if dat['item'] == "audit" or len(audit):
            """Update and Audit"""
            if len(audit):
                dat['audit'] = audit
            dat['audit']['createdate'] = datetime.fromtimestamp(
                int(time())).strftime('%d %B %Y')
            dat['audit']['createtime'] = datetime.fromtimestamp(
                int(time())).strftime('%H:%M:%S %p')
            db.helpline_phonedata.update_one(
                {"track": x.get('track')},
                {"$push": {"audit": dat['audit']}}
                )

        data['data'] = True
    except Exception as e:
        data['error'] = "Error Module Helpline Call Action {}".format(e)
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
            logger.debug("""Reset Helpline Call Data""")

            data['entries'] = db.helpline_phonedata.count_documents(
                {dat['keys']: {"$ne": None}})
            
            if data['entries']:
                db.helpline_phonedata.update_many(
                    {dat['keys']: {"$ne": None}},
                    {"$unset": {dat['keys']: ""}}
                    )

        if dat['item'] == "dummy":
            data['dummy'] = {}


        data['data'] = True
    except Exception as e:
        data['error'] = "Error Module Helpline Call Stats {}".format(e)
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
        data['error'] = "Error Module Helpline Call APIs {}".format(e)
        logger.critical(data['error'])

    return data


def indexreset(dat=False):
    """Helpline-Case Reset"""
    data = {}
    data['data'] = False
    data['error'] = False

    try:
        data['source'] = "Helpline Call Data"

        if dat and 'stats' in dat:
            """App-Stats"""
            data['stats'] = db.helpline_phonedata.count_documents({})

        elif dat and 'track' in dat:
            """Delete Specific Item"""
            data['meta'] = db.helpline_phonedata.count_documents({
                "track": dat['track']
                })
            if data['meta']:
                x = db.helpline_phonedata.find_one({
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
                db.helpline_phonedata.update_one(
                    {"track": dat['track']},
                    {"$set": edit})

        elif dat and 'demo' in dat:
            """Delete Demo Metadatas"""
            data['demo'] =  db.helpline_phonedata.count_documents({
                "demo": {"$ne": False}
                })
            if data['demo']:
                db.helpline_phonedata.delete_many({
                    "demo": {"$ne": False},
                    })

        elif dat and 'backup' in dat:
            """Delete Demo Metadatas"""
            core = []
            if db.helpline_phonedata.count_documents({}):
                df = pd.DataFrame(list(db.helpline_phonedata.find({})))
                df = df.drop(columns=['_id'])
                df = df.to_json(orient='records')
                core = json.loads(df)

            backup = os.getcwd() + "/datasets/backup"
            if not os.path.isdir(backup):
                cmd = "mkdir -p " + backup

            if len(core):
                with open(backup + "/helpline_phonedata.json", 'w') as fp:
                    fp.write(json.dumps(core, indent=2))

            data['meta'] = len(core)

        elif not dat and credentials.RUNSTATUS == 'production':
            """Production Reset All"""
            data['meta'] = db.helpline_phonedata.count_documents({})
            if data['meta']:
                edit = {}
                edit['status'] = "deleted"
                edit['admin.deleted'] = int(time())
                db.helpline_phonedata.update_many(
                    {"status": {"$ne": "deleted"}},
                    {"$set": edit}
                    )

        elif not dat:
            """Dev Reset All"""
            data['meta'] = db.helpline_phonedata.count_documents({})
            if data['meta']:
                db.helpline_phonedata.delete_many({})
                
        data['data'] = True
    except Exception as e:
        data['error'] = "Error Module Helpline Call Reset {}".format(e)
        logger.critical(data['error'])

    return data
    