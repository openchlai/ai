
# import ari
import os
import websocket
import requests
import json
from time import time

cdr = {}



def asterisk_ari(dat):
     
    ws = websocket.WebSocket()
    ws.connect(f"ws://127.0.0.1:8088/ari/events?api_key={dat}&app=bitzai&subscribeAll=true")
 
    while True:
        print("Loop ARI Events")
        data = ws.recv()        
        if not data:
            # if data is not received break
            ws.close()
            break
 
        dat = json.loads(data)
        if dat.get('type') == "StasisStart":
            print("We are starting the call")
            cdr[dat['channel']['id']] = dat['channel']['name']
            cmd = "curl -u 'bitzitc:ai@2025' -X POST http://localhost:8088/ari/channels/"
            cmd += dat.get('channel')['id'] + "/play?media=sound:hello-world"
            os.system(cmd)

        elif dat.get('type') == "StasisEnd":
            print("We are ending the call")

        elif dat.get('type') == "PlaybackStarted":
            print("We are starting the playback")
            cmd = "curl -u 'bitzitc:ai@2025' -X GET http://localhost:8088/ari/bridges"
            # os.system(cmd)

        elif dat.get('type') == "PlaybackFinished":
            print("We are ending the playback")
            channel = dat.get('playback')['target_uri'].split(':')[-1]

            cmd = "curl -u 'bitzitc:ai@2025' -X GET http://localhost:8088/ari/bridges"
            os.system(cmd)
            
            if channel in cdr:
                print("We are Terminating Call", channel)
                cmd = "curl -u 'bitzitc:ai@2025' -X DELETE http://localhost:8088/ari/channels/"
                cmd += channel
                # os.system(cmd)
        else:
            print(dat)
        # ws.send(json.dumps( str(data) ))

    #conn.close()  # close the connection


devEUI = "bitzitc:ai@2025"
asterisk_ari(devEUI)
# getDataLogsConnection(devEUI)
