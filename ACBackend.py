import traceback
import requests
from filelock import FileLock
from flask import Flask, request, jsonify, Response, send_file
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import logging
import os
import threading
import time
import random
from datetime import datetime

app = Flask(__name__)

session = requests.Session()
retries = Retry(total=10, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

TARGET_BASE = 'https://animalcompany.us-east1.nakamacloud.io:443'

file_lock = threading.Lock()

LOG_FOLDER = 'route_logs_json_f'
os.makedirs(LOG_FOLDER, exist_ok=True)

whitelist = ["exploding_car", "skirefr", "Ladiesman217", "Kelponline", "Harrydboi", "alex_shorts", "That1pers0nn", "1._._._._._._._._._._._._._.o", "Alex_shorts2", "sl0w_y0ur_r0le", "Jesster2", "Romeo_Rios_Vr", "Alex_shorts", "mr.fressy", "areo.ac", "iKDO.19", "Xrenobys", "catbag39840", "Vstarzie", "HYP3R_ac", "TribeGreywolfVR", "COD.janitor"]

def log_route_data_json(route, method, request_body, response_body, status_code, headers):
    safe_route = route.replace('/', '_').strip('_')
    filename = os.path.join(LOG_FOLDER, f"{safe_route}.json")

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "method": method,
        "route": f"/{route}",
        "headers": json.dumps(headers, indent=4),
        "request_body": request_body,
        "response_body": response_body,
        "status_code": status_code
    }

    with open(filename, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, indent=4) + ",\n")

@app.route('/data/game-data-prod.zip')
def download():
    file_path = os.path.join("fr2", "game-data-prod.zip")
    return send_file(file_path, as_attachment=True)

@app.route("/ac/v2/rpc/clientBootstrap", methods=["POST"])
def bootsrap():
    return {"payload":"{\"updateType\":\"None\",\"attestResult\":\"Valid\",\"attestTokenExpiresAt\":1820877961,\"photonAppID\":\"902213d1-35e6-4e9d-a254-b1e3a4e4b6ed\",\"photonVoiceAppID\":\"7928ecd5-a229-4d9c-88d8-bedfdda4b6fb\",\"termsAcceptanceNeeded\":[],\"dailyMissionDateKey\":\"\",\"dailyMissions\":null,\"dailyMissionResetTime\":0,\"serverTimeUnix\":1720877961,\"gameDataURL\":\"https://backend.xmodding.org/data/game-data-prod.zip\"}"}

@app.route("/ac/v2/account/authenticate/custom", methods=["POST"])
def auth_custom():
    forward_url = f"{TARGET_BASE}/v2/account/authenticate/custom"
    method = request.method
    headers = dict(request.headers)
    data = request.get_data()
    params = request.args
    headers.pop('Host', None)

    try:
        b = json.loads(data.decode('utf-8', errors='replace'))
        if isinstance(b, dict) and 'vars' in b and isinstance(b['vars'], dict):
            b['vars']['clientUserAgent'] = "MetaQuest 1.32.0.1515_96d6b8b7"
        resp = session.request(method, forward_url, headers=headers, data=json.dumps(b), params=params)
        if resp.status_code == 200:
            username = request.args.get("username")
            new_user = {
                "username": username,
                "auth": resp.json().get("token"),
                "refresh": resp.json().get("refresh_token")
            }

            with open("USERS.json", 'r', encoding='utf-8') as f:
                users = json.loads(f.read())

            users = [u for u in users if u.get("username") != username]

            users.append(new_user)

            with open("USERS.json", 'w', encoding='utf-8') as f:
                f.write(json.dumps(users, indent=4))

        decoded_data = json.dumps(b, indent=4)
        log_route_data_json("v2/account/authenticate/custom", method, decoded_data, resp.json(), resp.status_code, headers)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        print("Error in auth_custom:", traceback.format_exc())
        return "Internal Server Error", 500
    
@app.route("/ac/v2/storage/econ_gameplay_items", methods=["POST", "GET"])
def gameplayitems():
    return {"objects": [{"collection": "econ_gameplay_items", "key": "item_anti_gravity_grenade", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_anti_gravity_grenade\", \"netID\": 152, \"name\": \"Anti Gravity Grenade\", \"description\": \"Briefly disables gravity within a small area.\", \"category\": \"Explosives\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_apple", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_apple\", \"netID\": 71, \"name\": \"Apple\", \"description\": \"An apple a day keeps the doctor away!\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_arena_pistol", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_arena_pistol\", \"netID\": 154, \"name\": \"Pistol\", \"description\": \"...\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": true}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_arena_shotgun", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_arena_shotgun\", \"netID\": 155, \"name\": \"Shotgun\", \"description\": \"...\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": true}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_arrow", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_arrow\", \"netID\": 103, \"name\": \"Arrow\", \"description\": \"Can be attached to the crossbow.\", \"category\": \"Ammo\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_arrow_bomb", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_arrow_bomb\", \"netID\": 173, \"name\": \"Bomb Arrow\", \"description\": \"An arrow with a bomb attached. Hit something with it and watch it explode.\", \"category\": \"Ammo\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_arrow_heart", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_arrow_heart\", \"netID\": 116, \"name\": \"Heart Arrow\", \"description\": \"A love-themed arrow that will have your targets seeing hearts! \", \"category\": \"Ammo\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_arrow_lightbulb", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_arrow_lightbulb\", \"netID\": 105, \"name\": \"Lightbulb Arrow\", \"description\": \"An arrow that illuminates the surrounding area.\", \"category\": \"Ammo\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_arrow_teleport", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_arrow_teleport\", \"netID\": 174, \"name\": \"Teleport Arrow\", \"description\": \"Teleport more accurately with the precision of an arrow.\", \"category\": \"Ammo\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_backpack", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_backpack\", \"netID\": 1, \"name\": \"Backpack\", \"description\": \"The perfect adventurers pack. Has a base capacity of 10 items.\", \"category\": \"Bags\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_backpack_black", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_backpack_black\", \"netID\": 2, \"name\": \"Black Backpack\", \"description\": \"The perfect adventurers pack. Has a base capacity of 10 items. Now in a stylish Black!\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_backpack_green", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_backpack_green\", \"netID\": 3, \"name\": \"Green Backpack\", \"description\": \"The perfect adventurers pack. Has a base capacity of 10 items. Now in a stylish Green!\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_backpack_large_base", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_backpack_large_base\", \"netID\": 88, \"name\": \"Large Backpack\", \"description\": \"A massive pack with an extended capacity. Has a base capacity of 20 items.\", \"category\": \"Bags\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_backpack_large_basketball", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_backpack_large_basketball\", \"netID\": 138, \"name\": \"Large Basketball Print Backpack\", \"description\": \"A massive pack with an extended capacity. Has a base capacity of 20 items.\", \"category\": \"Bags\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_backpack_large_clover", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_backpack_large_clover\", \"netID\": 137, \"name\": \"Large Clover Print Backpack\", \"description\": \"A massive pack with an extended capacity. Has a base capacity of 20 items.\", \"category\": \"Bags\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_backpack_pink", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_backpack_pink\", \"netID\": 4, \"name\": \"Pink Backpack\", \"description\": \"The perfect adventurers pack. Has a base capacity of 10 items. Now in a stylish Pink!\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_backpack_small_base", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_backpack_small_base\", \"netID\": 87, \"name\": \"Small Backpack\", \"description\": \"Has a base capacity of 5 items.\", \"category\": \"Bags\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_backpack_white", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_backpack_white\", \"netID\": 5, \"name\": \"White Backpack\", \"description\": \"The perfect adventurers pack. Has a base capacity of 10 items. Now in a stylish White!\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_backpack_with_flashlight", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_backpack_with_flashlight\", \"netID\": 6, \"name\": \"Backpack with Flashlight\", \"description\": \"The perfect combination. Lights up dark hallways and has a base capacity of 10 items.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_balloon", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_balloon\", \"netID\": 75, \"name\": \"Balloon\", \"description\": \"A tool that helps you defy gravity...but not too much.\", \"category\": \"Toys\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_balloon_heart", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_balloon_heart\", \"netID\": 115, \"name\": \"Heart Balloon\", \"description\": \"Heart shaped balloon! For when love has you floating on air!\", \"category\": \"Toys\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_banana", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_banana\", \"netID\": 23, \"name\": \"Banana\", \"description\": \"Go bananas! Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_baseball_bat", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_baseball_bat\", \"netID\": 63, \"name\": \"Baseball Bat\", \"description\": \"A weapon that's great for hitting monsters out of the park.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_big_cup", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_big_cup\", \"netID\": 38, \"name\": \"Big Cup\", \"description\": \"Much more valuable than a little cup. Turn it in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_boombox", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_boombox\", \"netID\": 7, \"name\": \"Boombox\", \"description\": \"Carry this device around for vibes on the go!\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_boombox_neon", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_boombox_neon\", \"netID\": 153, \"name\": \"Neon Boombox\", \"description\": \"Carry this device around for vibes on the go!\", \"category\": \"Toys\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_box_fan", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_box_fan\", \"netID\": 122, \"name\": \"Box Fan\", \"description\": \"It blows air.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_brain_chunk", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_brain_chunk\", \"netID\": 178, \"name\": \"Brain Matter\", \"description\": \"A chunk of hyper intelligence.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_broccoli_grenade", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_broccoli_grenade\", \"netID\": 165, \"name\": \"Mega Broccoli Bomb\", \"description\": \"A dangerous-looking vegetable...bomb.\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_broccoli_shrink_grenade", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_broccoli_shrink_grenade\", \"netID\": 166, \"name\": \"Micro Broccoli Bomb\", \"description\": \"A dangerous-looking vegetable...bomb.\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_calculator", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_calculator\", \"netID\": 126, \"name\": \"Calculator\", \"description\": \"Helpful for number crunching\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_cardboard_box", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_cardboard_box\", \"netID\": 145, \"name\": \"Cardboard Box\", \"description\": \"A box. You get this sudden urge to hide inside it.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_cash", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_cash\", \"netID\": 49, \"name\": \"Cash\", \"description\": \"\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": true}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_cash_mega_pile", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_cash_mega_pile\", \"netID\": 51, \"name\": \"Cash Mega Pile\", \"description\": \"\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": true}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_cash_pile", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_cash_pile\", \"netID\": 50, \"name\": \"Cash Pile\", \"description\": \"\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": true}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ceo_plaque", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ceo_plaque\", \"netID\": 179, \"name\": \"CEO Plaque\", \"description\": \"This belongs to the big man upstairs.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_clapper", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_clapper\", \"netID\": 78, \"name\": \"Clapper\", \"description\": \"Lights, camera, action!\", \"category\": \"Toys\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_cluster_grenade", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_cluster_grenade\", \"netID\": 80, \"name\": \"Cluster Grenade\", \"description\": \"One grenade, multiple explosions. It\\u2019s like a fireworks show but with more danger.\", \"category\": \"Explosives\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_cola", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_cola\", \"netID\": 25, \"name\": \"Cola\", \"description\": \"Bubbly sugar water. Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_cola_large", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_cola_large\", \"netID\": 26, \"name\": \"Large Cola\", \"description\": \"The regular size cola wasn't enough. Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_company_ration", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_company_ration\", \"netID\": 67, \"name\": \"Company Ration\", \"description\": \"Experimental sustenance. Eat for a boost in productivity. May have side effects.\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_company_ration_heal", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_company_ration_heal\", \"netID\": 121, \"name\": \"Company Ration\", \"description\": \"Optimized for survival. Contents undisclosed.\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_cracker", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_cracker\", \"netID\": 72, \"name\": \"Cracker\", \"description\": \"Some dry biscuits that would pair well with soup.\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_crate", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_crate\", \"netID\": 8, \"name\": \"Crate\", \"description\": \"Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_crossbow", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_crossbow\", \"netID\": 9, \"name\": \"Crossbow\", \"description\": \"Attach almost anything and launch to create improvised weapons.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_crossbow_heart", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_crossbow_heart\", \"netID\": 117, \"name\": \"Heart Crossbow\", \"description\": \"A love-themed crossbow...because nothing says romance like a high-velocity declaration of love!\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_crowbar", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_crowbar\", \"netID\": 10, \"name\": \"Crowbar\", \"description\": \"A versatile tool for smashing things and fighting monsters.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_d20", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_d20\", \"netID\": 180, \"name\": \"D20\", \"description\": \"A 20 sided die.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_disc", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_disc\", \"netID\": 127, \"name\": \"DVD\", \"description\": \"May or may not contain a ripped copy of ROTK.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_disposable_camera", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_disposable_camera\", \"netID\": 11, \"name\": \"Disposable Camera\", \"description\": \"A digital camera. Take pictures of monsters and sell the camera for profit.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_drill", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_drill\", \"netID\": 176, \"name\": \"BFD9000\", \"description\": \"When pickaxes aren't enough, you bring the BFD. \", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_dynamite", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_dynamite\", \"netID\": 83, \"name\": \"Dynamite\", \"description\": \"For when subtlety just isn't an option. Light the fuse and throw!\", \"category\": \"Explosives\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_dynamite_cube", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_dynamite_cube\", \"netID\": 143, \"name\": \"Cube Dynamite\", \"description\": \"For when subtlety just isn't an option. Light the fuse and throw!\", \"category\": \"Explosives\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_egg", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_egg\", \"netID\": 27, \"name\": \"Egg\", \"description\": \"Beware its mother. Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": true, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_electrical_tape", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_electrical_tape\", \"netID\": 181, \"name\": \"Electrical Tape\", \"description\": \"Electrically resistant tape.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_eraser", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_eraser\", \"netID\": 182, \"name\": \"Eraser\", \"description\": \"Used to erase your mistakes.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_finger_board", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_finger_board\", \"netID\": 183, \"name\": \"Finger Board\", \"description\": \"Great for impressing your friends.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_flaregun", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_flaregun\", \"netID\": 12, \"name\": \"Flaregun\", \"description\": \"Fires a single use flare that lights up the environment and stuns enemies caught in the explosion.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_flashbang", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_flashbang\", \"netID\": 13, \"name\": \"Flashbang\", \"description\": \"Blind and deafen your enemies with an explosion and flash of bright light!\", \"category\": \"Explosives\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_flashlight", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_flashlight\", \"netID\": 14, \"name\": \"Flashlight\", \"description\": \"Perfect for lighting up spooky corridors and ominous caverns.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_flashlight_mega", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_flashlight_mega\", \"netID\": 15, \"name\": \"Mega Flashlight\", \"description\": \"Flood the room with light. World brightest flashlight.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_flashlight_red", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_flashlight_red\", \"netID\": 55, \"name\": \"Red Flashlight\", \"description\": \"Perfect for lighting up spooky corridors and ominous caverns. Now in red!\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_floppy3", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_floppy3\", \"netID\": 128, \"name\": \"Floppy Disc\", \"description\": \"A relic of a bygone era.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_floppy5", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_floppy5\", \"netID\": 129, \"name\": \"Floppy Disc\", \"description\": \"A relic of a bygone era.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_football", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_football\", \"netID\": 62, \"name\": \"Football\", \"description\": \"For throwing, catching, and sometimes bonking someone on the head.\", \"category\": \"Toys\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_friend_launcher", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_friend_launcher\", \"netID\": 191, \"name\": \"Friend Launcher\", \"description\": \"Convince your friend to grab on. Then charge it up and launch them.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_frying_pan", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_frying_pan\", \"netID\": 64, \"name\": \"Frying Pan\", \"description\": \"A weapon that's good for cooking eggs and cracking skulls.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_gameboy", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_gameboy\", \"netID\": 184, \"name\": \"Game Box\", \"description\": \"Can play the latest games.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_glowstick", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_glowstick\", \"netID\": 79, \"name\": \"Glowstick\", \"description\": \"Produces a bright yellow light and is unaffected by gravity. Makes your hand feel fuzzy when held.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_goldbar", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_goldbar\", \"netID\": 28, \"name\": \"Gold Bar\", \"description\": \"Valuable metal. Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_goldcoin", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_goldcoin\", \"netID\": 185, \"name\": \"Golden Coin\", \"description\": \"A relic of a bygone era.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_grenade", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_grenade\", \"netID\": 16, \"name\": \"Impact Grenade\", \"description\": \"A grenade that explodes on contact with any surface\", \"category\": \"Explosives\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_grenade_gold", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_grenade_gold\", \"netID\": 177, \"name\": \"Golden Grenade\", \"description\": \"A grenade that is gold!\", \"category\": \"Explosives\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_grenade_launcher", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_grenade_launcher\", \"netID\": 192, \"name\": \"Grenade Launcher\", \"description\": \"Loads up to 3 grenades of different types.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_harddrive", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_harddrive\", \"netID\": 186, \"name\": \"Encrypted Data\", \"description\": \"Highly sensitive data. Worth a lot to the right buyer.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_hawaiian_drum", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_hawaiian_drum\", \"netID\": 159, \"name\": \"Hawaiian Drums\", \"description\": \"Form a drum circle and improve your wellbeing with some rhythm. Heals nearby players when played.\", \"category\": \"Toys\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_heart_chunk", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_heart_chunk\", \"netID\": 48, \"name\": \"Heart Chunk\", \"description\": \"Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_heart_gun", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_heart_gun\", \"netID\": 54, \"name\": \"Heart Gun\", \"description\": \"Experimental Technology. Can suck entities in or repel them.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_heartchocolatebox", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_heartchocolatebox\", \"netID\": 114, \"name\": \"Heart Chocolate Box\", \"description\": \"Happy Valentine's Day! Gift this to someone sweet or eat it yourself!\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_hh_key", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_hh_key\", \"netID\": 29, \"name\": \"Haunted House Key\", \"description\": \"Unlocks a spooky door. Can be turned in for nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": true}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_hookshot", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_hookshot\", \"netID\": 82, \"name\": \"Hookshot\", \"description\": \"A fancy, over-engineered grappling hook device.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_hookshot_sword", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_hookshot_sword\", \"netID\": 160, \"name\": \"Yeetblade\", \"description\": \"Fifty percent hook, fifty percent blade, hundred percent awesome.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_hoverpad", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_hoverpad\", \"netID\": 30, \"name\": \"Hoverpad\", \"description\": \"Activate to propel against the ground.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_impulse_grenade", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_impulse_grenade\", \"netID\": 89, \"name\": \"Impulse Grenade\", \"description\": \"Throw it and watch everyone around you get yeeted.\", \"category\": \"Explosives\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_jetpack", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_jetpack\", \"netID\": 17, \"name\": \"Jetpack\", \"description\": \"Activate and hold on to fly into the sky.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_keycard", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_keycard\", \"netID\": 125, \"name\": \"Keycard\", \"description\": \"An employee keycard. It can be used to activate Canopy equipment.\\n\\n\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_lance", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_lance\", \"netID\": 74, \"name\": \"Lance\", \"description\": \"A huge lance letting you attack from a distance.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_landmine", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_landmine\", \"netID\": 156, \"name\": \"Landmine\", \"description\": \"Buried surprises are the best kind. For you, not for them.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_large_banana", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_large_banana\", \"netID\": 24, \"name\": \"Large Banana\", \"description\": \"Probably grown from a larger tree. Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_mug", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_mug\", \"netID\": 130, \"name\": \"Mug\", \"description\": \"A simple mug.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_nut", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_nut\", \"netID\": 31, \"name\": \"Nut\", \"description\": \"Currency...the economy is nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_nut_drop", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_nut_drop\", \"netID\": 148, \"name\": \"Nut Drop\", \"description\": \"Currency...the economy is nuts.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ogre_hands", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ogre_hands\", \"netID\": 66, \"name\": \"Ogre Hands\", \"description\": \"Green and mean, perfect for SMASHING enemies.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ore_copper_l", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ore_copper_l\", \"netID\": 95, \"name\": \"Large Copper Chunk\", \"description\": \"A conductive metal. Turn this in for Nuts.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ore_copper_m", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ore_copper_m\", \"netID\": 94, \"name\": \"Copper Chunk\", \"description\": \"A conductive metal. Turn this in for Nuts.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ore_copper_s", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ore_copper_s\", \"netID\": 93, \"name\": \"Small Copper Chunk\", \"description\": \"A conductive metal. Turn this in for Nuts.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ore_gold_l", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ore_gold_l\", \"netID\": 101, \"name\": \"Large Gold Chunk\", \"description\": \"Valuable metal. Turn this in for Nuts.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ore_gold_m", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ore_gold_m\", \"netID\": 100, \"name\": \"Gold Chunk\", \"description\": \"Valuable metal. Turn this in for Nuts.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ore_gold_s", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ore_gold_s\", \"netID\": 99, \"name\": \"Small Gold Chunk\", \"description\": \"Valuable metal. Turn this in for Nuts.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ore_hell", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ore_hell\", \"netID\": 113, \"name\": \"Cinder\", \"description\": \"It's warm to the touch.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ore_silver_l", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ore_silver_l\", \"netID\": 98, \"name\": \"Large Silver Chunk\", \"description\": \"Shiny. Turn this in for Nuts.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ore_silver_m", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ore_silver_m\", \"netID\": 97, \"name\": \"Small Silver Chunk\", \"description\": \"Shiny. Turn this in for Nuts.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ore_silver_s", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ore_silver_s\", \"netID\": 96, \"name\": \"Silver Chunk\", \"description\": \"Shiny. Turn this in for Nuts.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_painting_canvas", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_painting_canvas\", \"netID\": 52, \"name\": \"Painting Canvas\", \"description\": \"A priceless worth of art...turn it in for some Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_paperpack", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_paperpack\", \"netID\": 131, \"name\": \"Paper\", \"description\": \"The finest paper straight from Pennsylvania\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_pelican_case", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_pelican_case\", \"netID\": 32, \"name\": \"Black Crate\", \"description\": \"Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_pickaxe", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_pickaxe\", \"netID\": 65, \"name\": \"Pickaxe\", \"description\": \"The only weapon that's equally good at both mining and maiming.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_pickaxe_cny", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_pickaxe_cny\", \"netID\": 108, \"name\": \"Gilded Pickaxe\", \"description\": \"The only weapon that's equally good at both mining and maiming, but this one is gold plated. Gold is always better, no?\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_pickaxe_cube", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_pickaxe_cube\", \"netID\": 142, \"name\": \"Cube Pickaxe\", \"description\": \"The only weapon that's equally good at both mining and maiming.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_pinata_bat", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_pinata_bat\", \"netID\": 151, \"name\": \"Pinata Bat\", \"description\": \"A festive bat, perfect for smashing monsters like candy-filled pi\\u00f1atas.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_pipe", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_pipe\", \"netID\": 33, \"name\": \"Pipe\", \"description\": \"A versatile tool for smashing things and a plumber's best friend.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_plunger", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_plunger\", \"netID\": 34, \"name\": \"Plunger\", \"description\": \"Push against a wall to activate suction. Can be used to climb almost any surface.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_pogostick", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_pogostick\", \"netID\": 35, \"name\": \"Pogostick\", \"description\": \"Boing boing boing.\", \"category\": \"Toys\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_police_baton", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_police_baton\", \"netID\": 124, \"name\": \"Police Baton (Crowbar)\", \"description\": \"A crowbar variant. A versatile tool for smashing things and catching bad animals.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_portable_teleporter", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_portable_teleporter\", \"netID\": 175, \"name\": \"Portable Teleporter\", \"description\": \"Activate it to teleport back to the lobby\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_pumpkin_pie", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_pumpkin_pie\", \"netID\": 73, \"name\": \"Pumpkin Pie\", \"description\": \"A not-so-fresh pie that expired last Thanksgiving.\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_pumpkinjack", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_pumpkinjack\", \"netID\": 56, \"name\": \"Pumpkin Jack\", \"description\": \"The perfect combo of Halloween spirit and spooky energy.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_pumpkinjack_small", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_pumpkinjack_small\", \"netID\": 57, \"name\": \"Small Pumpkin Jack\", \"description\": \"Halloween spirit and spooky energy, now fun-sized.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_quiver", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_quiver\", \"netID\": 104, \"name\": \"Quiver\", \"description\": \"Carry many arrows. Can be equipped onto your hip or back.\", \"category\": \"Bags\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_quiver_heart", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_quiver_heart\", \"netID\": 118, \"name\": \"Heart Quiver\", \"description\": \"Love makes the heart quiver, now your arrows can too!\", \"category\": \"Bags\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_radioactive_broccoli", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_radioactive_broccoli\", \"netID\": 119, \"name\": \"Mega Broccoli\", \"description\": \"A dangerous-looking vegetable. Probably shouldn't eat it, but...\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_randombox_mobloot_big", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_randombox_mobloot_big\", \"netID\": 58, \"name\": \"Big Mob Loot Box\", \"description\": \"Open it for a huge surprise!\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_randombox_mobloot_medium", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_randombox_mobloot_medium\", \"netID\": 59, \"name\": \"Mob Loot Box\", \"description\": \"Open it for a big surprise!\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_randombox_mobloot_small", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_randombox_mobloot_small\", \"netID\": 60, \"name\": \"Small Mob Loot Box\", \"description\": \"Open it for a surprise!\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_randombox_mobloot_weapons", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_randombox_mobloot_weapons\", \"netID\": 92, \"name\": \"Mob Weapons Loot Box\", \"description\": \"A weapon box.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_randombox_mobloot_zombie", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_randombox_mobloot_zombie\", \"netID\": 164, \"name\": \"Zombie Loot Box\", \"description\": \"Open it for a big surprise!\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_rare_card", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_rare_card\", \"netID\": 187, \"name\": \"Rare Trading Card\", \"description\": \"An extremely valuable trading card.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_revolver", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_revolver\", \"netID\": 68, \"name\": \"Revolver\", \"description\": \"6 shots, make them count.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_revolver_ammo", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_revolver_ammo\", \"netID\": 86, \"name\": \"Revolver Ammo\", \"description\": \"Use to reload a revolver\", \"category\": \"Ammo\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_revolver_gold", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_revolver_gold\", \"netID\": 146, \"name\": \"Gold Revolver\", \"description\": \"6 shots, make them count.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_robo_monke", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_robo_monke\", \"netID\": 190, \"name\": \"RoboMonke2000\", \"description\": \"A little monkey robot toy\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_rope", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_rope\", \"netID\": 112, \"name\": \"Rope\", \"description\": \"Use it as ammo for the zipline gun.\", \"category\": \"Ammo\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_rpg", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_rpg\", \"netID\": 84, \"name\": \"RPG\", \"description\": \"A single use tool of ultimate destruction.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_rpg_ammo", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_rpg_ammo\", \"netID\": 85, \"name\": \"RPG Rocket\", \"description\": \"Use to reload an RPG after firing\", \"category\": \"Ammo\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_rpg_ammo_egg", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_rpg_ammo_egg\", \"netID\": 150, \"name\": \"Egg RPG Ammo\", \"description\": \"An explosive egg with more explosions inside. Used to reload an RPG\", \"category\": \"Ammo\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_rpg_ammo_spear", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_rpg_ammo_spear\", \"netID\": 162, \"name\": \"Boomspear Ammo\", \"description\": \"Reload and explode! Ammo for the Boomspear!\", \"category\": \"Ammo\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_rpg_cny", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_rpg_cny\", \"netID\": 110, \"name\": \"Rocket Dragon RPG\", \"description\": \"For ultimate destruction with style\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_rpg_easter", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_rpg_easter\", \"netID\": 149, \"name\": \"Egg Launcher RPG\", \"description\": \"For ultimate destruction with style\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_rpg_spear", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_rpg_spear\", \"netID\": 161, \"name\": \"Boomspear\", \"description\": \"Explode responsibly.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_rubberducky", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_rubberducky\", \"netID\": 36, \"name\": \"Rubber Ducky\", \"description\": \"He makes bath time so much fun!\", \"category\": \"Toys\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ruby", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ruby\", \"netID\": 37, \"name\": \"Ruby\", \"description\": \"It's not Nuts, but you can turn it in for some.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_saddle", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_saddle\", \"netID\": 61, \"name\": \"Saddle\", \"description\": \"Mount your friends, joust monsters, or give that one guy who can't use his arms a lift.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_scanner", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_scanner\", \"netID\": 18, \"name\": \"Scanner\", \"description\": \"Your personal monster radar...because sometimes, it\\u2019s better to know when you\\u2019re about to be eaten.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_scissors", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_scissors\", \"netID\": 132, \"name\": \"Scissors\", \"description\": \"Perfect for arts and crafts.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_server_pad", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_server_pad\", \"netID\": 188, \"name\": \"Broken Tablet\", \"description\": \"A broken tablet.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_shield", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_shield\", \"netID\": 77, \"name\": \"Shield\", \"description\": \"It protecc.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_shield_bones", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_shield_bones\", \"netID\": 109, \"name\": \"Protective Bone Shield\", \"description\": \"A shield made from your enemies bones.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_shield_police", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_shield_police\", \"netID\": 123, \"name\": \"Police Shield\", \"description\": \"A shield for protecting you and your squad\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_shield_viking_1", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_shield_viking_1\", \"netID\": 168, \"name\": \"Viking Shield\", \"description\": \"Strong enough for a viking.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_shield_viking_2", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_shield_viking_2\", \"netID\": 169, \"name\": \"Berserker Shield\", \"description\": \"Probably used more for smashing than protecting...\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_shield_viking_3", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_shield_viking_3\", \"netID\": 170, \"name\": \"Thane Shield\", \"description\": \"A shield fit for a Thane.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_shield_viking_4", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_shield_viking_4\", \"netID\": 171, \"name\": \"Varangian Shield\", \"description\": \"If it's good enough for Varangians, it's good enough for you.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_shotgun", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_shotgun\", \"netID\": 19, \"name\": \"Shotgun\", \"description\": \"Shoot a spread of pellets dealing massive damage. \", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_shotgun_ammo", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_shotgun_ammo\", \"netID\": 20, \"name\": \"Shotgun Ammo\", \"description\": \"Use to reload a shotgun\", \"category\": \"Ammo\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_shredder", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_shredder\", \"netID\": 135, \"name\": \"Nut Shredder\", \"description\": \"Shred your loot into nuts.\", \"category\": \"Bags\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_shrinking_broccoli", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_shrinking_broccoli\", \"netID\": 120, \"name\": \"Micro Broccoli\", \"description\": \"A dangerous-looking vegetable. Probably shouldn't eat it, but...\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_snowball", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_snowball\", \"netID\": 91, \"name\": \"Snowball\", \"description\": \"A perfectly shaped snowball ready to be thrown.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_stapler", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_stapler\", \"netID\": 133, \"name\": \"Stapler\", \"description\": \"A gorgeous red stapler\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_stash_grenade", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_stash_grenade\", \"netID\": 147, \"name\": \"Stash Grenade\", \"description\": \"Harness the power of the stash for a few seconds\", \"category\": \"Explosives\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_stick_armbones", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_stick_armbones\", \"netID\": 107, \"name\": \"Arm Bones (Stick)\", \"description\": \"In case you need to defend your bones with more bones.\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_stick_bone", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_stick_bone\", \"netID\": 106, \"name\": \"Bone (Stick)\", \"description\": \"Why use a tree stick when you can use a bone?\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_sticker_dispenser", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_sticker_dispenser\", \"netID\": 144, \"name\": \"Sticker Dispenser\", \"description\": \"Drop glowing stickers to mark your path and never lose your way.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_sticky_dynamite", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_sticky_dynamite\", \"netID\": 102, \"name\": \"Sticky Dynamite\", \"description\": \"Dunno what this dynamite got into.\", \"category\": \"Explosives\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_stinky_cheese", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_stinky_cheese\", \"netID\": 140, \"name\": \"Stinky Cheese\", \"description\": \"Stinky Swiss cheese. Stay as far away as possible.\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_tablet", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_tablet\", \"netID\": 21, \"name\": \"Tablet\", \"description\": \"It\\u2019s like a treasure map, but on a tiny screen.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_tapedispenser", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_tapedispenser\", \"netID\": 134, \"name\": \"Tape Dispenser\", \"description\": \"Perfect for arts and crafts.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_tele_grenade", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_tele_grenade\", \"netID\": 76, \"name\": \"Tele Grenade\", \"description\": \"Activate and throw to spatially transpose your body after a delay.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_teleport_gun", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_teleport_gun\", \"netID\": 189, \"name\": \"Teleport Gun\", \"description\": \"A gun that can spatially transpose your body when fired.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_theremin", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_theremin\", \"netID\": 136, \"name\": \"Theremin\", \"description\": \"Make some music, or weird noises.\", \"category\": \"Toys\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_timebomb", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_timebomb\", \"netID\": 141, \"name\": \"Time Bomb\", \"description\": \"A bomb that explodes after a certain amount of time.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_toilet_paper", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_toilet_paper\", \"netID\": 39, \"name\": \"Toilet Paper\", \"description\": \"Soft and in high demand. Turn it in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_toilet_paper_mega", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_toilet_paper_mega\", \"netID\": 41, \"name\": \"Mega Toilet Paper\", \"description\": \"Extra fluffy, extra valuable. Turn it in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_toilet_paper_roll_empty", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_toilet_paper_roll_empty\", \"netID\": 40, \"name\": \"Empty Toilet Paper Roll\", \"description\": \"It has its uses. Turn it in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_treestick", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_treestick\", \"netID\": 90, \"name\": \"Tree Stick\", \"description\": \"Nature's sword. Can be used as a weapon, but it seems like it will break any second...\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_tripwire_explosive", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_tripwire_explosive\", \"netID\": 22, \"name\": \"Tripwire Explosive\", \"description\": \"Attach to any surface to create a deadly trap.\", \"category\": \"Explosives\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_trophy", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_trophy\", \"netID\": 42, \"name\": \"Trophy\", \"description\": \"Everybody deserves one. Turn it in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_turkey_leg", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_turkey_leg\", \"netID\": 70, \"name\": \"Turkey Leg\", \"description\": \"A juicy leg from a turkey.\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_turkey_whole", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_turkey_whole\", \"netID\": 69, \"name\": \"Turkey Whole\", \"description\": \"A whole turkey. Big appetite required!\", \"category\": \"Consumables\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ukulele", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ukulele\", \"netID\": 157, \"name\": \"Ukulele\", \"description\": \"Serenade your friends with a relaxing tune. Heals nearby players when played.\", \"category\": \"Toys\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_ukulele_gold", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_ukulele_gold\", \"netID\": 158, \"name\": \"Golden Ukulele\", \"description\": \"Serenade your friends even more with gold. Heals nearby players when played.\", \"category\": \"Toys\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_umbrella", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_umbrella\", \"netID\": 43, \"name\": \"Umbrella\", \"description\": \"Descend gracefully. Part parachute, part parasol, all fabulous.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_umbrella_clover", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_umbrella_clover\", \"netID\": 139, \"name\": \"Clover Umbrella\", \"description\": \"Descend gracefully. Part parachute, part parasol, all fabulous.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_unidentified", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_unidentified\", \"netID\": 0, \"name\": \"Unknown Item\", \"description\": \"???\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_upsidedown_loot", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_upsidedown_loot\", \"netID\": 53, \"name\": \"Upsidedown Loot\", \"description\": \"Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_uranium_chunk_l", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_uranium_chunk_l\", \"netID\": 46, \"name\": \"Large Uranium Chunk\", \"description\": \"Radioactive metal. Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_uranium_chunk_m", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_uranium_chunk_m\", \"netID\": 45, \"name\": \"Uranium Chunk\", \"description\": \"Radioactive metal. Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_uranium_chunk_s", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_uranium_chunk_s\", \"netID\": 44, \"name\": \"Small Uranium Chunk\", \"description\": \"Radioactive metal. Turn this in for Nuts.\", \"category\": \"Hidden\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_viking_hammer", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_viking_hammer\", \"netID\": 167, \"name\": \"Dawn Hammer\", \"description\": \"Launch your enemies into the sun!\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_viking_hammer_twilight", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_viking_hammer_twilight\", \"netID\": 172, \"name\": \"Twilight Hammer\", \"description\": \"Launch your enemies like a shooting star!\", \"category\": \"Weapons\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_whoopie", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_whoopie\", \"netID\": 47, \"name\": \"Whoopie\", \"description\": \"Pfffttt\", \"category\": \"Toys\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_zipline_gun", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_zipline_gun\", \"netID\": 111, \"name\": \"Zipline Gun\", \"description\": \"Load it with rope and fire to instantly create a zipline between two points.\", \"category\": \"Gadgets\", \"price\": 0, \"value\": 100000000, \"isLoot\": false, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}, {"collection": "econ_gameplay_items", "key": "item_zombie_meat", "user_id": "00000000-0000-0000-0000-000000000000", "value": "{\"id\": \"item_zombie_meat\", \"netID\": 163, \"name\": \"Zombie Meat\", \"description\": \"Not fresh. Not valuable. Not... safe.\", \"category\": \"Loot\", \"price\": 0, \"value\": 100000000, \"isLoot\": true, \"isPurchasable\": true, \"isUnique\": false, \"isDevOnly\": false}", "version": "64b72d358f12a50f7004e6d80cdb4a23", "permission_read": 2, "create_time": "2025-02-06T15:14:05Z", "update_time": "2025-02-11T14:51:59Z"}]}

@app.route("/ac/v2/account", methods=["POST", "GET"])
def account():
    forward_url = f"{TARGET_BASE}/v2/account"
    method = request.method
    headers = dict(request.headers)
    data = request.get_data()
    params = request.args
    headers.pop('Host', None)

    try:
        decoded_data = data.decode('utf-8', errors='replace')
        resp = session.request(method, forward_url, headers=headers, data=decoded_data, params=params)
        
        if 'application/json' in resp.headers.get('Content-Type', ''):
            body = resp.json()
            if (body["user"]["username"] in whitelist):
                wallet = json.loads(body["wallet"])
                wallet["researchPoints"] = 100000
                wallet["hardCurrency"] = 1000000
                wallet["softCurrency"] = 1000000000
                body["wallet"] = json.dumps(wallet)
                body["user"]["metadata"] = "{\"isDeveloper\": true}"
                log_route_data_json("v2/account", method, decoded_data, body, resp.status_code, headers)
                return jsonify(body), resp.status_code
            return "not whitelisted.", 403
        else:
            decoded_content = resp.content.decode('utf-8', errors='replace')
            log_route_data_json("v2/account", method, decoded_data, decoded_content, resp.status_code, headers)
            return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        print("Error in account:", traceback.format_exc())
        return "Internal Server Error", 500
    
@app.route('/ac/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route('/ac/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def catch_all(path):
    forward_url = f"{TARGET_BASE}/{path}"
    method = request.method
    headers = dict(request.headers)
    data = request.get_data()
    params = request.args
    headers.pop('Host', None)

    try:
        resp = session.request(method, forward_url, headers=headers, data=data, params=params)
        decoded_data = data.decode('utf-8', errors='replace')

        if 'application/json' in resp.headers.get('Content-Type', ''):
            log_route_data_json(path, method, decoded_data, resp.json(), resp.status_code, headers)
            return jsonify(resp.json()), resp.status_code

        decoded_content = resp.content.decode('utf-8', errors='replace')
        log_route_data_json(path, method, decoded_data, decoded_content, resp.status_code, headers)
        return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))

    except Exception as e:
        print("Error in catch_all:", traceback.format_exc())
        return "Internal Server Error", 500


############################## ANTI BAN API ##############################

@app.route("/ac/antiban/v2/storage", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def storage_antiban():
    return {
        "objects": [
            {
                "collection": "user_avatar",
                "key": "0",
                "user_id": "3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236",
                "value": "{\"butt\": \"bp_butt_cat\", \"head\": \"bp_head_cat\", \"tail\": \"bp_tail_cat\", \"torso\": \"bp_torso_cat\", \"armLeft\": \"bp_arm_l_cat\", \"eyeLeft\": \"bp_eye_polarbear\", \"armRight\": \"bp_arm_r_cat\", \"eyeRight\": \"bp_eye_polarbear\", \"accessories\": [], \"primaryColor\": \"000000\"}",
                "version": "b5d3102f94143f10d57d38959d13bb3f",
                "permission_read": 2,
                "create_time": "2024-09-20T21:26:18Z",
                "update_time": "2025-07-16T18:55:07Z"
            },
            {
                "collection": "user_inventory",
                "key": "avatar",
                "user_id": "3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236",
                "value": "{\"items\": [],\"version\": 1}",
                "version": "f9180aba79021d89b07e7ea48438d7ca",
                "permission_read": 1,
                "create_time": "2024-09-20T21:26:18Z",
                "update_time": "2025-07-16T18:53:41Z"
            },
            {
                "collection": "user_inventory",
                "key": "research",
                "user_id": "3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236",
                "value": "{\"nodes\": [\"node_dynamite\", \"node_teleport_grenade\", \"node_glowsticks\", \"node_skill_backpack_cap_1\", \"node_skill_health_1\", \"node_crowbar\", \"node_flaregun\", \"node_ogre_hands\", \"node_revolver\", \"node_skill_gundamage_1\", \"node_skill_explosive_1\", \"node_rpg\", \"node_skill_selling_1\", \"node_revolver_ammo\", \"node_rpg_ammo\", \"node_flashbang\", \"node_impact_grenade\", \"node_cluster_grenade\", \"node_jetpack\", \"node_shotgun\", \"node_tripwire_explosive\", \"node_crossbow\", \"node_tablet\", \"node_plunger\", \"node_umbrella\", \"node_backpack\", \"node_flashlight_mega\", \"node_lance\", \"node_balloon\", \"node_saddle\", \"node_skill_right_hip_attachment\", \"node_skill_left_hip_attachment\", \"node_sticky_dynamite\", \"node_rpg_cny\", \"node_zipline_gun\", \"node_zipline_rope\", \"node_company_ration\", \"node_balloon_heart\", \"node_crossbow_heart\", \"node_arrow\", \"node_arrow_heart\", \"node_hoverpad\", \"node_quiver\", \"node_backpack_large\", \"node_shield\", \"node_shield_police\", \"node_hookshot\", \"node_baseball_bat\", \"node_police_baton\", \"node_heart_gun\", \"node_pogostick\", \"node_boxfan\", \"node_mega_broccoli\", \"node_mini_broccoli\", \"node_dynamite_cube\", \"node_skill_backpack_cap_2\", \"node_whoopie\", \"node_disposable_camera\", \"node_sticker_dispenser\", \"node_impulse_grenade\", \"node_stash_grenade\", \"node_cardboardbox\", \"node_rpg_easter\", \"node_rpg_ammo_egg\", \"node_pinata_bat\", \"node_hawaiian_drum\", \"node_ukulele\", \"node_anti_gravity_grenade\", \"node_antigrav_grenade\", \"node_football\", \"node_skill_backpack_cap_3\", \"node_item_nut_shredder\", \"node_hookshot_sword\", \"node_rpg_spear\", \"node_rpg_ammo_spear\", \"node_skill_health_2\", \"node_skill_selling_2\", \"node_skill_selling_3\", \"node_frying_pan\", \"node_skill_melee_1\", \"node_skill_melee_2\", \"node_skill_melee_3\", \"node_viking_hammer\", \"node_viking_hammer_twilight\", \"node_mega_broccoli_bomb\", \"node_micro_broccoli_bomb\", \"node_teleport_gun\", \"node_arrow_bomb\", \"node_robo_monke\", \"node_friend_launcher\", \"node_grenade_launcher\"]}",
                "version": "58c1d1c4ade0e8e205939be8a07ce49b",
                "permission_read": 1,
                "create_time": "2024-11-25T17:55:33Z",
                "update_time": "2025-07-14T21:34:27Z"
            },
            {
                "collection": "user_inventory",
                "key": "stash",
                "user_id": "3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236",
                "value": "{\"items\": [],\"version\": 1}",
                "version": "1b44e9d93285fca73f03043b97532017",
                "permission_read": 1,
                "permission_write": 1,
                "create_time": "2025-02-11T22:35:00Z",
                "update_time": "2025-07-18T00:25:53Z"
            },
            {
                "collection": "user_inventory",
                "key": "gameplay_loadout",
                "user_id": "3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236",
                "value": "{\"version\": 1}",
                "version": "77efb8e3fa276d4674932392a66555e4",
                "permission_read": 1,
                "permission_write": 1,
                "create_time": "2024-10-30T01:21:34Z",
                "update_time": "2025-07-18T00:51:32Z"
            },
            {
                "collection": "user_preferences",
                "key": "gameplay_items",
                "user_id": "3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236",
                "value": "{\"recents\": []}",
                "version": "0f76108dd7e2ed6b33ae4d1b7e9a3a73",
                "permission_read": 1,
                "permission_write": 1,
                "create_time": "2024-12-10T20:44:21Z",
                "update_time": "2025-07-18T00:50:57Z"
            }
        ]
    }

@app.route("/ac/antiban/v2/account/authenticate/custom", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def auth_custom_antiban():
    return {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWQiOiI3Y2RjMWZhNy01ZDkwLTQ1NzUtYTZhMy00N2YwNzQ4ZGE4OTgiLCJ1aWQiOiIzNTYwZmUyZS0wMTVjLTRkMmItYjJhNi02ZWI5ZjhkNmEyMzYiLCJ1c24iOiJza2lyZWZyIiwidnJzIjp7ImF1dGhJRCI6IjFjYjNkYWU3NTkzMTRjMDU5MmRiODMwMGY3Y2I2OTc5IiwiY2xpZW50VXNlckFnZW50IjoiTWV0YVF1ZXN0IDEuMzEuMi4xNTExXzk2ZDZiOGI3IiwiZGV2aWNlSUQiOiI5ZGM3MmQyOTk5ZDY0MTIzYTA2Yzc5NjJiZDlhNDEyOSIsImxvZ2luVHlwZSI6Im1ldGFfcXVlc3QifSwiZXhwIjoxNzUyOTY3Mzg2LCJpYXQiOjE3NTI5NjM3ODZ9.Gfv3RYNgsb4vutev0ab0yCuIDN39zGAuVOZ7KofxsCw",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWQiOiI3Y2RjMWZhNy01ZDkwLTQ1NzUtYTZhMy00N2YwNzQ4ZGE4OTgiLCJ1aWQiOiIzNTYwZmUyZS0wMTVjLTRkMmItYjJhNi02ZWI5ZjhkNmEyMzYiLCJ1c24iOiJza2lyZWZyIiwidnJzIjp7ImF1dGhJRCI6IjFjYjNkYWU3NTkzMTRjMDU5MmRiODMwMGY3Y2I2OTc5IiwiY2xpZW50VXNlckFnZW50IjoiTWV0YVF1ZXN0IDEuMzEuMi4xNTExXzk2ZDZiOGI3IiwiZGV2aWNlSUQiOiI5ZGM3MmQyOTk5ZDY0MTIzYTA2Yzc5NjJiZDlhNDEyOSIsImxvZ2luVHlwZSI6Im1ldGFfcXVlc3QifSwiZXhwIjoxNzUzMDUwMTg2LCJpYXQiOjE3NTI5NjM3ODZ9.2VYOvTIoVukTGVJ6KOdb6YOP1dUq0QbYtnZtMzmhO2g"
    }

@app.route("/ac/antiban/v2/account/session/refresh", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def refresh_antiban():
    return {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWQiOiI3Y2RjMWZhNy01ZDkwLTQ1NzUtYTZhMy00N2YwNzQ4ZGE4OTgiLCJ1aWQiOiIzNTYwZmUyZS0wMTVjLTRkMmItYjJhNi02ZWI5ZjhkNmEyMzYiLCJ1c24iOiJza2lyZWZyIiwidnJzIjp7ImF1dGhJRCI6IjFjYjNkYWU3NTkzMTRjMDU5MmRiODMwMGY3Y2I2OTc5IiwiY2xpZW50VXNlckFnZW50IjoiTWV0YVF1ZXN0IDEuMzEuMi4xNTExXzk2ZDZiOGI3IiwiZGV2aWNlSUQiOiI5ZGM3MmQyOTk5ZDY0MTIzYTA2Yzc5NjJiZDlhNDEyOSIsImxvZ2luVHlwZSI6Im1ldGFfcXVlc3QifSwiZXhwIjoxNzUyOTY3Mzg2LCJpYXQiOjE3NTI5NjM3ODZ9.Gfv3RYNgsb4vutev0ab0yCuIDN39zGAuVOZ7KofxsCw",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWQiOiI3Y2RjMWZhNy01ZDkwLTQ1NzUtYTZhMy00N2YwNzQ4ZGE4OTgiLCJ1aWQiOiIzNTYwZmUyZS0wMTVjLTRkMmItYjJhNi02ZWI5ZjhkNmEyMzYiLCJ1c24iOiJza2lyZWZyIiwidnJzIjp7ImF1dGhJRCI6IjFjYjNkYWU3NTkzMTRjMDU5MmRiODMwMGY3Y2I2OTc5IiwiY2xpZW50VXNlckFnZW50IjoiTWV0YVF1ZXN0IDEuMzEuMi4xNTExXzk2ZDZiOGI3IiwiZGV2aWNlSUQiOiI5ZGM3MmQyOTk5ZDY0MTIzYTA2Yzc5NjJiZDlhNDEyOSIsImxvZ2luVHlwZSI6Im1ldGFfcXVlc3QifSwiZXhwIjoxNzUzMDUwMTg2LCJpYXQiOjE3NTI5NjM3ODZ9.2VYOvTIoVukTGVJ6KOdb6YOP1dUq0QbYtnZtMzmhO2g"
    }

@app.route("/ac/antiban/v2/account", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def account_antiban():
    return {
        "user": {
            "id": "3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236",
            "username": "XMOD USER",
            "display_name": "XMOD",
            "lang_tag": "en",
            "metadata": "{\"isDeveloper\": true}",
            "edge_count": 198,
            "create_time": "2024-08-24T04:20:56Z",
            "update_time": "2025-07-18T00:50:32Z",
            "isDev": True
        },
        "wallet": "{\"stashCols\": 8, \"stashRows\": 8, \"hardCurrency\": 100000, \"softCurrency\": 10000000000, \"researchPoints\": 100000}",
        "custom_id": "26412155295098886"
    }

@app.route("/ac/antiban/v2/rpc/mining.balance", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def mining_antiban():
    return {
        "payload": "{\"hardCurrency\":1000000,\"researchPoints\":1000000}"
    }

@app.route("/ac/antiban/v2/rpc/purchase.list", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def purchaselist_antiban():
    return {
        "payload": "{\"purchases\":[{\"user_id\":\"3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236\",\"product_id\":\"CHAMELEON_BUNDLE\",\"transaction_id\":\"642819158920561\",\"store\":3,\"purchase_time\":{\"seconds\":1748315321},\"create_time\":{\"seconds\":1748315350,\"nanos\":615822000},\"update_time\":{\"seconds\":1748315350,\"nanos\":615822000},\"refund_time\":{},\"provider_response\":\"{\\\"success\\\": true, \\\"grant_time\\\": 1748315321}\",\"environment\":2},{\"user_id\":\"3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236\",\"product_id\":\"SHELLLONG_BUNDLE\",\"transaction_id\":\"583001341569010\",\"store\":3,\"purchase_time\":{\"seconds\":1742932724},\"create_time\":{\"seconds\":1742932880,\"nanos\":773282000},\"update_time\":{\"seconds\":1742932880,\"nanos\":773282000},\"refund_time\":{},\"provider_response\":\"{\\\"success\\\": true}\",\"environment\":2},{\"user_id\":\"3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236\",\"product_id\":\"G.O.A.T_BUNDLE\",\"transaction_id\":\"556928314176313\",\"store\":3,\"purchase_time\":{\"seconds\":1740523561},\"create_time\":{\"seconds\":1740523626,\"nanos\":858485000},\"update_time\":{\"seconds\":1741616276,\"nanos\":636221000},\"refund_time\":{},\"provider_response\":\"{\\\"success\\\": true}\",\"environment\":2},{\"user_id\":\"3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236\",\"product_id\":\"CURRENCY_SMALL\",\"transaction_id\":\"520077871194691\",\"store\":3,\"purchase_time\":{\"seconds\":1737165591},\"create_time\":{\"seconds\":1737165616,\"nanos\":219758000},\"update_time\":{\"seconds\":1737165616,\"nanos\":219758000},\"refund_time\":{},\"provider_response\":\"{\\\"success\\\": true}\",\"environment\":2},{\"user_id\":\"3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236\",\"product_id\":\"POLAR_PAWS_BUNDLE\",\"transaction_id\":\"498846086651203\",\"store\":3,\"purchase_time\":{\"seconds\":1735139449},\"create_time\":{\"seconds\":1735155215,\"nanos\":988535000},\"update_time\":{\"seconds\":1735155215,\"nanos\":988535000},\"refund_time\":{},\"provider_response\":\"{\\\"success\\\": true}\",\"environment\":2},{\"user_id\":\"3560fe2e-015c-4d2b-b2a6-6eb9f8d6a236\",\"product_id\":\"FROG_BUNDLE\",\"transaction_id\":\"411070858762060\",\"store\":3,\"purchase_time\":{\"seconds\":1726952768},\"create_time\":{\"seconds\":1726953016,\"nanos\":937191000},\"update_time\":{\"seconds\":1726953016,\"nanos\":937191000},\"refund_time\":{},\"provider_response\":\"{\\\"success\\\": true}\",\"environment\":2}]}"
    }

@app.route("/ac/antiban/v2/rpc/attest.start", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def attest_antiban():
    return {
        "payload": "{\"serverTimeUnix\":0}"
    }

@app.route("/ac/antiban/v2/rpc/clientBootstrap", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def bootstrap_antiban():
    return {
        "payload": "{\"updateType\":\"None\",\"attestResult\":\"Valid\",\"attestTokenExpiresAt\":1820877961,\"photonAppID\":\"183b6ceb-f1ea-4c16-8303-8fc3e7eaa316\",\"photonVoiceAppID\":\"52688ea6-5ea9-41e9-86f5-f9c53d723970\",\"termsAcceptanceNeeded\":[],\"dailyMissionDateKey\":\"\",\"dailyMissions\":null,\"dailyMissionResetTime\":0,\"serverTimeUnix\":1720877961,\"gameDataURL\":\"http://ac-main.b-cdn.net/data/game-data-prod.zip/}"
    }

@app.route("/ac/antiban/v2/storage/econ_gameplay_items", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def gameplayitems_antiban():
    return {
        "objects": [
            {
                "collection": "econ_gameplay_items",
                "key": "item_anti_gravity_grenade",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_anti_gravity_grenade\", \"name\": \"Anti Gravity Grenade\", \"netID\": 152, \"price\": 299, \"value\": 23, \"isLoot\": false, \"category\": \"Explosives\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Briefly disables gravity within a small area.\", \"isPurchasable\": true}",
                "version": "f274efc1f82df99ac4870d1b06987847",
                "permission_read": 2,
                "create_time": "2025-05-13T17:42:13Z",
                "update_time": "2025-05-28T16:03:56Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_apple",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_apple\", \"name\": \"Apple\", \"netID\": 71, \"price\": 200, \"value\": 7, \"isLoot\": true, \"category\": \"Consumables\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"An apple a day keeps the doctor away!\", \"isPurchasable\": false}",
                "version": "5969a600405b8525db6c143279f493ff",
                "permission_read": 2,
                "create_time": "2024-11-18T02:55:39Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_arena_pistol",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_arena_pistol\", \"name\": \"Pistol\", \"netID\": 154, \"price\": 2147483647, \"value\": 0, \"isLoot\": false, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": true, \"description\": \"...\", \"isPurchasable\": false}",
                "version": "d46291c01d22184fad21e6bc14e288e0",
                "permission_read": 2,
                "create_time": "2025-05-13T17:42:13Z",
                "update_time": "2025-05-21T15:53:00Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_arena_shotgun",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_arena_shotgun\", \"name\": \"Shotgun\", \"netID\": 155, \"price\": 2147483647, \"value\": 0, \"isLoot\": false, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": true, \"description\": \"...\", \"isPurchasable\": false}",
                "version": "0f03a2b2eafc8e3cb69c2392c8fed9c8",
                "permission_read": 2,
                "create_time": "2025-05-13T17:42:13Z",
                "update_time": "2025-05-21T15:53:00Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_arrow",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_arrow\", \"name\": \"Arrow\", \"netID\": 103, \"price\": 199, \"value\": 8, \"isLoot\": false, \"category\": \"Ammo\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Can be attached to the crossbow.\", \"isPurchasable\": true}",
                "version": "f86a15aa34108f4853f5a7fa97aca4a1",
                "permission_read": 2,
                "create_time": "2025-01-27T19:12:49Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_arrow_bomb",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_arrow_bomb\", \"name\": \"Bomb Arrow\", \"netID\": 173, \"price\": 299, \"value\": 18, \"isLoot\": false, \"category\": \"Ammo\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"An arrow with a bomb attached. Hit something with it and watch it explode.\", \"isPurchasable\": true}",
                "version": "ea5a75a8c849e9c292333ce6c97be587",
                "permission_read": 2,
                "create_time": "2025-06-16T23:34:50Z",
                "update_time": "2025-06-24T14:14:42Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_arrow_heart",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_arrow_heart\", \"name\": \"Heart Arrow\", \"netID\": 116, \"price\": 199, \"value\": 8, \"isLoot\": false, \"category\": \"Ammo\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A love-themed arrow that will have your targets seeing hearts! \", \"isPurchasable\": true}",
                "version": "6565015437a46afad7647167004f200f",
                "permission_read": 2,
                "create_time": "2025-02-11T14:51:59Z",
                "update_time": "2025-02-12T21:54:50Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_arrow_lightbulb",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_arrow_lightbulb\", \"name\": \"Lightbulb Arrow\", \"netID\": 105, \"price\": 249, \"value\": 10, \"isLoot\": false, \"category\": \"Ammo\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"An arrow that illuminates the surrounding area.\", \"isPurchasable\": true}",
                "version": "61d87c6f2b74436d5911bf0d95d93e65",
                "permission_read": 2,
                "create_time": "2025-01-28T14:31:51Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_arrow_teleport",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_arrow_teleport\", \"name\": \"Teleport Arrow\", \"netID\": 174, \"price\": 299, \"value\": 19, \"isLoot\": false, \"category\": \"Ammo\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Teleport more accurately with the precision of an arrow.\", \"isPurchasable\": true}",
                "version": "18c38312aad2e3d764260d9322d056ba",
                "permission_read": 2,
                "create_time": "2025-06-16T23:34:50Z",
                "update_time": "2025-06-24T14:14:42Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_backpack",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_backpack\", \"name\": \"Backpack\", \"netID\": 1, \"price\": 49, \"value\": 2, \"isLoot\": false, \"category\": \"Bags\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"The perfect adventurers pack. Has a base capacity of 10 items.\", \"isPurchasable\": true}",
                "version": "c5ced1ba7b3dd2e5374c2f6e894849ac",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_backpack_black",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_backpack_black\", \"name\": \"Black Backpack\", \"netID\": 2, \"price\": 49, \"value\": 2, \"isLoot\": false, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"The perfect adventurers pack. Has a base capacity of 10 items. Now in a stylish Black!\", \"isPurchasable\": true}",
                "version": "78936d2343c619b81efad38d6c785ffa",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_backpack_green",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_backpack_green\", \"name\": \"Green Backpack\", \"netID\": 3, \"price\": 49, \"value\": 2, \"isLoot\": false, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"The perfect adventurers pack. Has a base capacity of 10 items. Now in a stylish Green!\", \"isPurchasable\": true}",
                "version": "d496d7e7c3b2f3efdd4c40fa6d2a3a12",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_backpack_large_base",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_backpack_large_base\", \"name\": \"Large Backpack\", \"netID\": 88, \"price\": 299, \"value\": 15, \"isLoot\": false, \"category\": \"Bags\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A massive pack with an extended capacity. Has a base capacity of 20 items.\", \"isPurchasable\": true}",
                "version": "e78cc2628024555d54ac46ffedf9bebc",
                "permission_read": 2,
                "create_time": "2024-12-06T03:18:20Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_backpack_large_basketball",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_backpack_large_basketball\", \"name\": \"Large Basketball Print Backpack\", \"netID\": 138, \"price\": 299, \"value\": 15, \"isLoot\": false, \"category\": \"Bags\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A massive pack with an extended capacity. Has a base capacity of 20 items.\", \"isPurchasable\": true}",
                "version": "75e4971dc9172172052252554d73fb95",
                "permission_read": 2,
                "create_time": "2025-03-12T18:37:38Z",
                "update_time": "2025-03-12T18:37:38Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_backpack_large_clover",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_backpack_large_clover\", \"name\": \"Large Clover Print Backpack\", \"netID\": 137, \"price\": 299, \"value\": 15, \"isLoot\": false, \"category\": \"Bags\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A massive pack with an extended capacity. Has a base capacity of 20 items.\", \"isPurchasable\": true}",
                "version": "5fbd60851e27f99be45278668d23623d",
                "permission_read": 2,
                "create_time": "2025-03-12T18:37:38Z",
                "update_time": "2025-03-12T18:37:38Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_backpack_pink",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_backpack_pink\", \"name\": \"Pink Backpack\", \"netID\": 4, \"price\": 49, \"value\": 2, \"isLoot\": false, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"The perfect adventurers pack. Has a base capacity of 10 items. Now in a stylish Pink!\", \"isPurchasable\": true}",
                "version": "2736fb2d35f0a431e9220455826736b8",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_backpack_small_base",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_backpack_small_base\", \"name\": \"Small Backpack\", \"netID\": 87, \"price\": 29, \"value\": 1, \"isLoot\": false, \"category\": \"Bags\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Has a base capacity of 5 items.\", \"isPurchasable\": true}",
                "version": "27303af1389eb843bb7efc55ae745a6c",
                "permission_read": 2,
                "create_time": "2024-12-06T03:18:20Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_backpack_white",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_backpack_white\", \"name\": \"White Backpack\", \"netID\": 5, \"price\": 49, \"value\": 2, \"isLoot\": false, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"The perfect adventurers pack. Has a base capacity of 10 items. Now in a stylish White!\", \"isPurchasable\": true}",
                "version": "6c509758f57935d1e79cd3543021e7f9",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_backpack_with_flashlight",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_backpack_with_flashlight\", \"name\": \"Backpack with Flashlight\", \"netID\": 6, \"price\": 499, \"value\": 35, \"isLoot\": false, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"The perfect combination. Lights up dark hallways and has a base capacity of 10 items.\", \"isPurchasable\": true}",
                "version": "afaec9f2a44ecc4a5ce37844b6331119",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-19T20:16:28Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_balloon",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_balloon\", \"name\": \"Balloon\", \"netID\": 75, \"price\": 149, \"value\": 12, \"isLoot\": false, \"category\": \"Toys\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A tool that helps you defy gravity...but not too much.\", \"isPurchasable\": true}",
                "version": "1dd876f985706923135c1011fe56e2f4",
                "permission_read": 2,
                "create_time": "2024-11-25T17:50:51Z",
                "update_time": "2025-01-14T16:26:51Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_balloon_heart",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_balloon_heart\", \"name\": \"Heart Balloon\", \"netID\": 115, \"price\": 149, \"value\": 12, \"isLoot\": false, \"category\": \"Toys\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Heart shaped balloon! For when love has you floating on air!\", \"isPurchasable\": true}",
                "version": "f1b54237807ed00de134b95327063aa0",
                "permission_read": 2,
                "create_time": "2025-02-11T14:51:59Z",
                "update_time": "2025-02-12T21:54:50Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_banana",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_banana\", \"name\": \"Banana\", \"netID\": 23, \"price\": 2147483647, \"value\": 25, \"isLoot\": true, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Go bananas! Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "015d1d7fa93c8be8597a5271e08a7087",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_baseball_bat",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_baseball_bat\", \"name\": \"Baseball Bat\", \"netID\": 63, \"price\": 349, \"value\": 19, \"isLoot\": false, \"category\": \"Weapons\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A weapon that's great for hitting monsters out of the park.\", \"isPurchasable\": true}",
                "version": "ceed8ff2eca893e111f11e78c4b183e0",
                "permission_read": 2,
                "create_time": "2024-11-11T23:46:08Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_big_cup",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_big_cup\", \"name\": \"Big Cup\", \"netID\": 38, \"price\": 2147483647, \"value\": 35, \"isLoot\": true, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Much more valuable than a little cup. Turn it in for Nuts.\", \"isPurchasable\": false}",
                "version": "5fe5ba6db242ca2fa2f5576e398f4e25",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_boombox",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_boombox\", \"name\": \"Boombox\", \"netID\": 7, \"price\": 564, \"value\": 3, \"isLoot\": false, \"category\": \"Gadgets\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Carry this device around for vibes on the go!\", \"isPurchasable\": false}",
                "version": "eb2971b6a007f90646bfc12258661bbd",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_boombox_neon",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_boombox_neon\", \"name\": \"Neon Boombox\", \"netID\": 153, \"price\": 564, \"value\": 3, \"isLoot\": false, \"category\": \"Toys\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Carry this device around for vibes on the go!\", \"isPurchasable\": false}",
                "version": "a9121f792102aa4c75f8e7e0ff6aae64",
                "permission_read": 2,
                "create_time": "2025-05-13T17:42:13Z",
                "update_time": "2025-05-13T17:42:13Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_box_fan",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_box_fan\", \"name\": \"Box Fan\", \"netID\": 122, \"price\": 999, \"value\": 36, \"isLoot\": false, \"category\": \"Gadgets\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"It blows air.\", \"isPurchasable\": true}",
                "version": "145479de9925394f55ea08b045531113",
                "permission_read": 2,
                "create_time": "2025-03-05T20:48:16Z",
                "update_time": "2025-03-11T16:02:43Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_brain_chunk",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_brain_chunk\", \"name\": \"Brain Matter\", \"netID\": 178, \"price\": 9999, \"value\": 512, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A chunk of hyper intelligence.\", \"isPurchasable\": false}",
                "version": "f3133457eefd3a3e35e5db4247091ad9",
                "permission_read": 2,
                "create_time": "2025-07-01T00:36:53Z",
                "update_time": "2025-07-01T00:36:53Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_broccoli_grenade",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_broccoli_grenade\", \"name\": \"Mega Broccoli Bomb\", \"netID\": 165, \"price\": 999, \"value\": 40, \"isLoot\": false, \"category\": \"Consumables\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A dangerous-looking vegetable...bomb.\", \"isPurchasable\": true}",
                "version": "3a74a5b8c4761478fac8444f224c5c40",
                "permission_read": 2,
                "create_time": "2025-06-10T17:11:31Z",
                "update_time": "2025-06-16T23:34:50Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_broccoli_shrink_grenade",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_broccoli_shrink_grenade\", \"name\": \"Micro Broccoli Bomb\", \"netID\": 166, \"price\": 999, \"value\": 40, \"isLoot\": false, \"category\": \"Consumables\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A dangerous-looking vegetable...bomb.\", \"isPurchasable\": true}",
                "version": "65aec1526151f07b372750a9ac4c72ba",
                "permission_read": 2,
                "create_time": "2025-06-10T17:11:31Z",
                "update_time": "2025-06-16T23:34:50Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_calculator",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_calculator\", \"name\": \"Calculator\", \"netID\": 126, \"price\": 999, \"value\": 32, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Helpful for number crunching\", \"isPurchasable\": false}",
                "version": "2e2e218e1358df32bfa3405b37256cc7",
                "permission_read": 2,
                "create_time": "2025-03-10T14:55:16Z",
                "update_time": "2025-03-10T14:55:16Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_cardboard_box",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_cardboard_box\", \"name\": \"Cardboard Box\", \"netID\": 145, \"price\": 499, \"value\": 20, \"isLoot\": false, \"category\": \"Gadgets\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A box. You get this sudden urge to hide inside it.\", \"isPurchasable\": true}",
                "version": "0ba5a6062bbaa6d2e4717cb6a4c68980",
                "permission_read": 2,
                "create_time": "2025-04-08T13:38:27Z",
                "update_time": "2025-04-24T19:22:06Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_cash",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_cash\", \"name\": \"Cash\", \"netID\": 49, \"price\": 2147483647, \"value\": 0, \"isLoot\": false, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": true, \"description\": \"\", \"isPurchasable\": false}",
                "version": "d1c47fffdc56e73f3b96f65317e42c38",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2025-07-02T21:31:45Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_cash_mega_pile",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_cash_mega_pile\", \"name\": \"Cash Mega Pile\", \"netID\": 51, \"price\": 2147483647, \"value\": 0, \"isLoot\": false, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": true, \"description\": \"\", \"isPurchasable\": false}",
                "version": "6cfd693a561aa7b16b618993e554cc62",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2025-07-02T21:31:45Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_cash_pile",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_cash_pile\", \"name\": \"Cash Pile\", \"netID\": 50, \"price\": 2147483647, \"value\": 0, \"isLoot\": false, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": true, \"description\": \"\", \"isPurchasable\": false}",
                "version": "b92ea1d03e7523ae21837116afeefe0c",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2025-07-02T21:31:45Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_ceo_plaque",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_ceo_plaque\", \"name\": \"CEO Plaque\", \"netID\": 179, \"price\": 9999, \"value\": 306, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"This belongs to the big man upstairs.\", \"isPurchasable\": false}",
                "version": "a43dd36ff8b23b5daf6b1083a6f10a48",
                "permission_read": 2,
                "create_time": "2025-07-01T00:36:53Z",
                "update_time": "2025-07-01T00:36:53Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_clapper",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_clapper\", \"name\": \"Clapper\", \"netID\": 78, \"price\": 99, \"value\": 1, \"isLoot\": false, \"category\": \"Toys\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Lights, camera, action!\", \"isPurchasable\": true}",
                "version": "e7e99e096dec4a29cc46f99fb006ebce",
                "permission_read": 2,
                "create_time": "2024-12-06T03:18:20Z",
                "update_time": "2024-12-06T03:18:20Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_cluster_grenade",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_cluster_grenade\", \"name\": \"Cluster Grenade\", \"netID\": 80, \"price\": 599, \"value\": 14, \"isLoot\": false, \"category\": \"Explosives\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"One grenade, multiple explosions. It\u2019s like a fireworks show but with more danger.\", \"isPurchasable\": true}",
                "version": "048e5491a9f5c2948daec3d871dfcf8f",
                "permission_read": 2,
                "create_time": "2024-12-06T03:18:20Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_cola",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_cola\", \"name\": \"Cola\", \"netID\": 25, \"price\": 2147483647, \"value\": 27, \"isLoot\": true, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Bubbly sugar water. Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "593debcbff60597106848ed78234607a",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_cola_large",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_cola_large\", \"name\": \"Large Cola\", \"netID\": 26, \"price\": 2147483647, \"value\": 49, \"isLoot\": true, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"The regular size cola wasn't enough. Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "ceab3458dcbae3e1af365a27867297d6",
                "permission_read": 2,
                "create_time": "2024-10-18T18:43:32Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_company_ration",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_company_ration\", \"name\": \"Company Ration\", \"netID\": 67, \"price\": 219, \"value\": 17, \"isLoot\": false, \"category\": \"Consumables\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Experimental sustenance. Eat for a boost in productivity. May have side effects.\", \"isPurchasable\": true}",
                "version": "4cd8601f873005fe5a35eb4b56ae4acc",
                "permission_read": 2,
                "create_time": "2024-11-11T23:53:22Z",
                "update_time": "2024-12-06T04:29:14Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_company_ration_heal",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_company_ration_heal\", \"name\": \"Company Ration\", \"netID\": 121, \"price\": 219, \"value\": 17, \"isLoot\": false, \"category\": \"Consumables\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Optimized for survival. Contents undisclosed.\", \"isPurchasable\": false}",
                "version": "b9ad27b34b524cd421b150ea1c8cdd11",
                "permission_read": 2,
                "create_time": "2025-03-03T16:27:52Z",
                "update_time": "2025-03-03T16:27:52Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_cracker",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_cracker\", \"name\": \"Cracker\", \"netID\": 72, \"price\": 200, \"value\": 4, \"isLoot\": true, \"category\": \"Consumables\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Some dry biscuits that would pair well with soup.\", \"isPurchasable\": false}",
                "version": "95789f06431de90f075ed260a2b710db",
                "permission_read": 2,
                "create_time": "2024-11-18T02:55:39Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_crate",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_crate\", \"name\": \"Crate\", \"netID\": 8, \"price\": 2147483647, \"value\": 500, \"isLoot\": true, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "f963215ec55bdf3b02ad11c18d21ca79",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_crossbow",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_crossbow\", \"name\": \"Crossbow\", \"netID\": 9, \"price\": 1499, \"value\": 47, \"isLoot\": false, \"category\": \"Weapons\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Attach almost anything and launch to create improvised weapons.\", \"isPurchasable\": true}",
                "version": "1e735f7ad3ecd86f9a17d3a8acd2303e",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-06T04:29:14Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_crossbow_heart",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_crossbow_heart\", \"name\": \"Heart Crossbow\", \"netID\": 117, \"price\": 1499, \"value\": 47, \"isLoot\": false, \"category\": \"Weapons\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A love-themed crossbow...because nothing says romance like a high-velocity declaration of love!\", \"isPurchasable\": true}",
                "version": "a3114ddf51d153193b39d601c37e4186",
                "permission_read": 2,
                "create_time": "2025-02-11T14:51:59Z",
                "update_time": "2025-02-12T21:54:50Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_crowbar",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_crowbar\", \"name\": \"Crowbar\", \"netID\": 10, \"price\": 399, \"value\": 23, \"isLoot\": false, \"category\": \"Weapons\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A versatile tool for smashing things and fighting monsters.\", \"isPurchasable\": true}",
                "version": "1b715ae2a91f6bbc8552c994145f576e",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-06T04:29:14Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_d20",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_d20\", \"name\": \"D20\", \"netID\": 180, \"price\": 9999, \"value\": 64, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A 20 sided die.\", \"isPurchasable\": false}",
                "version": "8caca12af8ef2c59b5aade41e9854cfe",
                "permission_read": 2,
                "create_time": "2025-07-01T00:36:53Z",
                "update_time": "2025-07-01T00:36:53Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_disc",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_disc\", \"name\": \"DVD\", \"netID\": 127, \"price\": 999, \"value\": 100, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"May or may not contain a ripped copy of ROTK.\", \"isPurchasable\": false}",
                "version": "09b41774e3b9f618e2aa7e9e7b0ee398",
                "permission_read": 2,
                "create_time": "2025-03-10T14:55:16Z",
                "update_time": "2025-03-10T14:55:16Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_disposable_camera",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_disposable_camera\", \"name\": \"Disposable Camera\", \"netID\": 11, \"price\": 199, \"value\": 3, \"isLoot\": false, \"category\": \"Gadgets\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A digital camera. Take pictures of monsters and sell the camera for profit.\", \"isPurchasable\": true}",
                "version": "eb76ffa16895f1e84a8c27556ce2fc9f",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-06T19:18:13Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_drill",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_drill\", \"name\": \"BFD9000\", \"netID\": 176, \"price\": 1999, \"value\": 122, \"isLoot\": false, \"category\": \"Weapons\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"When pickaxes aren't enough, you bring the BFD. \", \"isPurchasable\": true}",
                "version": "ac450b4d29c96dd0e208798b4ce0e3d5",
                "permission_read": 2,
                "create_time": "2025-06-24T14:14:42Z",
                "update_time": "2025-06-25T16:37:30Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_dynamite",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_dynamite\", \"name\": \"Dynamite\", \"netID\": 83, \"price\": 249, \"value\": 21, \"isLoot\": false, \"category\": \"Explosives\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"For when subtlety just isn't an option. Light the fuse and throw!\", \"isPurchasable\": true}",
                "version": "c7a65d030d9888df2c55e081f0bb6a8c",
                "permission_read": 2,
                "create_time": "2024-12-06T03:18:20Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_dynamite_cube",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_dynamite_cube\", \"name\": \"Cube Dynamite\", \"netID\": 143, \"price\": 249, \"value\": 21, \"isLoot\": false, \"category\": \"Explosives\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"For when subtlety just isn't an option. Light the fuse and throw!\", \"isPurchasable\": true}",
                "version": "c02c340f4d57c90218c9b4867f7ea99b",
                "permission_read": 2,
                "create_time": "2025-04-02T19:10:08Z",
                "update_time": "2025-04-02T19:10:08Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_egg",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_egg\", \"name\": \"Egg\", \"netID\": 27, \"price\": 2147483647, \"value\": 2626, \"isLoot\": true, \"category\": \"Hidden\", \"isUnique\": true, \"isDevOnly\": false, \"description\": \"Beware its mother. Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "e2596bf2c7ec772519d721755cc6c937",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2025-04-17T18:10:51Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_electrical_tape",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_electrical_tape\", \"name\": \"Electrical Tape\", \"netID\": 181, \"price\": 9999, \"value\": 48, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Electrically resistant tape.\", \"isPurchasable\": false}",
                "version": "cfc933438ca639e1befc7a7d28ba23bf",
                "permission_read": 2,
                "create_time": "2025-07-01T00:36:53Z",
                "update_time": "2025-07-01T00:36:53Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_eraser",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_eraser\", \"name\": \"Eraser\", \"netID\": 182, \"price\": 9999, \"value\": 100, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Used to erase your mistakes.\", \"isPurchasable\": false}",
                "version": "a9699ee1caeee63397ca837cffce3285",
                "permission_read": 2,
                "create_time": "2025-07-01T00:36:53Z",
                "update_time": "2025-07-01T00:36:53Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_finger_board",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_finger_board\", \"name\": \"Finger Board\", \"netID\": 183, \"price\": 9999, \"value\": 165, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Great for impressing your friends.\", \"isPurchasable\": false}",
                "version": "003689965052ed9a82661ff72f992cd5",
                "permission_read": 2,
                "create_time": "2025-07-01T00:36:53Z",
                "update_time": "2025-07-01T00:36:53Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_flaregun",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_flaregun\", \"name\": \"Flaregun\", \"netID\": 12, \"price\": 199, \"value\": 20, \"isLoot\": false, \"category\": \"Weapons\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Fires a single use flare that lights up the environment and stuns enemies caught in the explosion.\", \"isPurchasable\": true}",
                "version": "6ecb585a6991da29ace18305863e691a",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-17T17:45:58Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_flashbang",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_flashbang\", \"name\": \"Flashbang\", \"netID\": 13, \"price\": 99, \"value\": 10, \"isLoot\": false, \"category\": \"Explosives\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Blind and deafen your enemies with an explosion and flash of bright light!\", \"isPurchasable\": true}",
                "version": "380240e05fa1d1ad8cd3d05190b37eaf",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_flashlight",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_flashlight\", \"name\": \"Flashlight\", \"netID\": 14, \"price\": 49, \"value\": 4, \"isLoot\": false, \"category\": \"Gadgets\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Perfect for lighting up spooky corridors and ominous caverns.\", \"isPurchasable\": true}",
                "version": "8e0a57211c2fc3b6b83e1b19fc9aa3ea",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-19T20:16:28Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_flashlight_mega",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_flashlight_mega\", \"name\": \"Mega Flashlight\", \"netID\": 15, \"price\": 999, \"value\": 35, \"isLoot\": false, \"category\": \"Gadgets\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Flood the room with light. World brightest flashlight.\", \"isPurchasable\": true}",
                "version": "e5a13cfcbfcece7e4527e67141be2ecc",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-06T19:18:13Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_flashlight_red",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_flashlight_red\", \"name\": \"Red Flashlight\", \"netID\": 55, \"price\": 69, \"value\": 5, \"isLoot\": false, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Perfect for lighting up spooky corridors and ominous caverns. Now in red!\", \"isPurchasable\": true}",
                "version": "2fb248fa1e0c82ba5daf17787ec285e0",
                "permission_read": 2,
                "create_time": "2024-10-22T02:30:02Z",
                "update_time": "2024-12-19T20:16:28Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_floppy3",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_floppy3\", \"name\": \"Floppy Disc\", \"netID\": 128, \"price\": 999, \"value\": 64, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A relic of a bygone era.\", \"isPurchasable\": false}",
                "version": "b45d8de10982743e5059ffc388f6e6b4",
                "permission_read": 2,
                "create_time": "2025-03-10T14:55:16Z",
                "update_time": "2025-03-10T14:55:16Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_floppy5",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_floppy5\", \"name\": \"Floppy Disc\", \"netID\": 129, \"price\": 999, \"value\": 64, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A relic of a bygone era.\", \"isPurchasable\": false}",
                "version": "768e3c7f3d0fa2c10c865735de55f767",
                "permission_read": 2,
                "create_time": "2025-03-10T14:55:16Z",
                "update_time": "2025-03-10T14:55:16Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_football",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_football\", \"name\": \"Football\", \"netID\": 62, \"price\": 99, \"value\": 11, \"isLoot\": false, \"category\": \"Toys\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"For throwing, catching, and sometimes bonking someone on the head.\", \"isPurchasable\": true}",
                "version": "daa91919e66bc3c679c97494116da8d4",
                "permission_read": 2,
                "create_time": "2024-11-05T22:06:01Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_friend_launcher",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_friend_launcher\", \"name\": \"Friend Launcher\", \"netID\": 191, \"price\": 699, \"value\": 36, \"isLoot\": false, \"category\": \"Gadgets\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Convince your friend to grab on. Then charge it up and launch them.\", \"isPurchasable\": true}",
                "version": "720e94cbf08438196a76783fb7c4bb50",
                "permission_read": 2,
                "create_time": "2025-07-14T20:09:29Z",
                "update_time": "2025-07-15T19:56:50Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_frying_pan",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_frying_pan\", \"name\": \"Frying Pan\", \"netID\": 64, \"price\": 399, \"value\": 23, \"isLoot\": false, \"category\": \"Weapons\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A weapon that's good for cooking eggs and cracking skulls.\", \"isPurchasable\": true}",
                "version": "d6ec29f178a045f7be4cf70728b88671",
                "permission_read": 2,
                "create_time": "2024-11-11T23:46:08Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_gameboy",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_gameboy\", \"name\": \"Game Box\", \"netID\": 184, \"price\": 9999, \"value\": 999, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Can play the latest games.\", \"isPurchasable\": false}",
                "version": "62e538dcc8f8d2e93af8b2f67e26a727",
                "permission_read": 2,
                "create_time": "2025-07-01T00:36:53Z",
                "update_time": "2025-07-01T00:36:53Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_glowstick",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_glowstick\", \"name\": \"Glowstick\", \"netID\": 79, \"price\": 99, \"value\": 15, \"isLoot\": false, \"category\": \"Gadgets\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Produces a bright yellow light and is unaffected by gravity. Makes your hand feel fuzzy when held.\", \"isPurchasable\": true}",
                "version": "e5a04ae5d298bd4da386fbce4b663ad1",
                "permission_read": 2,
                "create_time": "2024-12-06T03:18:20Z",
                "update_time": "2024-12-06T19:18:13Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_goldbar",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_goldbar\", \"name\": \"Gold Bar\", \"netID\": 28, \"price\": 2147483647, \"value\": 155, \"isLoot\": true, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Valuable metal. Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "e7b94c0bb2fda5ed9088dee83b933cc6",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_goldcoin",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_goldcoin\", \"name\": \"Golden Coin\", \"netID\": 185, \"price\": 9999, \"value\": 503, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A relic of a bygone era.\", \"isPurchasable\": false}",
                "version": "07acc26a52b6830b29ea224a27df0185",
                "permission_read": 2,
                "create_time": "2025-07-01T00:36:53Z",
                "update_time": "2025-07-01T00:36:53Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_grenade",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_grenade\", \"name\": \"Impact Grenade\", \"netID\": 16, \"price\": 249, \"value\": 19, \"isLoot\": false, \"category\": \"Explosives\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A grenade that explodes on contact with any surface\", \"isPurchasable\": true}",
                "version": "23bdd9d89b3880991542346b0bf399db",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_grenade_gold",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_grenade_gold\", \"name\": \"Golden Grenade\", \"netID\": 177, \"price\": 449, \"value\": 33, \"isLoot\": false, \"category\": \"Explosives\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A grenade that is gold!\", \"isPurchasable\": true}",
                "version": "083f1b1a24c0b6bf342baf0c89e3cd48",
                "permission_read": 2,
                "create_time": "2025-06-26T19:22:35Z",
                "update_time": "2025-07-01T03:10:31Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_grenade_launcher",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_grenade_launcher\", \"name\": \"Grenade Launcher\", \"netID\": 192, \"price\": 8999, \"value\": 301, \"isLoot\": false, \"category\": \"Weapons\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Loads up to 3 grenades of different types.\", \"isPurchasable\": true}",
                "version": "4b581b1d6104503b206d14cace017d26",
                "permission_read": 2,
                "create_time": "2025-07-14T20:09:29Z",
                "update_time": "2025-07-15T19:56:50Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_harddrive",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_harddrive\", \"name\": \"Encrypted Data\", \"netID\": 186, \"price\": 9999, \"value\": 780, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Highly sensitive data. Worth a lot to the right buyer.\", \"isPurchasable\": false}",
                "version": "5915a78600314dc915feec7c66c12b83",
                "permission_read": 2,
                "create_time": "2025-07-01T00:36:53Z",
                "update_time": "2025-07-01T00:36:53Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_hawaiian_drum",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_hawaiian_drum\", \"name\": \"Hawaiian Drums\", \"netID\": 159, \"price\": 999, \"value\": 42, \"isLoot\": false, \"category\": \"Toys\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Form a drum circle and improve your wellbeing with some rhythm. Heals nearby players when played.\", \"isPurchasable\": true}",
                "version": "726500d52e93946522333c8a28e7182a",
                "permission_read": 2,
                "create_time": "2025-05-23T21:41:48Z",
                "update_time": "2025-06-04T16:58:59Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_heartchocolatebox",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_heartchocolatebox\", \"name\": \"Heart Chocolate Box\", \"netID\": 114, \"price\": 200, \"value\": 14, \"isLoot\": true, \"category\": \"Consumables\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Happy Valentine's Day! Gift this to someone sweet or eat it yourself!\", \"isPurchasable\": false}",
                "version": "00a17350e6a6239d9beb9a53a10b720a",
                "permission_read": 2,
                "create_time": "2025-02-10T16:31:15Z",
                "update_time": "2025-07-02T21:31:45Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_heart_chunk",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_heart_chunk\", \"name\": \"Heart Chunk\", \"netID\": 48, \"price\": 2147483647, \"value\": 135, \"isLoot\": true, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "eaf82cb81b649660502a64224f15e374",
                "permission_read": 2,
                "create_time": "2024-10-18T23:51:13Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_heart_gun",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_heart_gun\", \"name\": \"Heart Gun\", \"netID\": 54, \"price\": 1999, \"value\": 34, \"isLoot\": false, \"category\": \"Weapons\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Experimental Technology. Can suck entities in or repel them.\", \"isPurchasable\": true}",
                "version": "355b4a55f92e6e95cf3684ee2fb662e6",
                "permission_read": 2,
                "create_time": "2024-10-21T17:57:28Z",
                "update_time": "2024-12-06T19:18:13Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_hh_key",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_hh_key\", \"name\": \"Haunted House Key\", \"netID\": 29, \"price\": 2147483647, \"value\": 200, \"isLoot\": true, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": true, \"description\": \"Unlocks a spooky door. Can be turned in for nuts.\", \"isPurchasable\": false}",
                "version": "9712c1ca52d472f064c94f7f6d784940",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_hookshot",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_hookshot\", \"name\": \"Hookshot\", \"netID\": 82, \"price\": 1999, \"value\": 29, \"isLoot\": false, \"category\": \"Gadgets\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A fancy, over-engineered grappling hook device.\", \"isPurchasable\": true}",
                "version": "932653131592e417690d8f66e500854f",
                "permission_read": 2,
                "create_time": "2024-12-06T03:18:20Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_hookshot_sword",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_hookshot_sword\", \"name\": \"Yeetblade\", \"netID\": 160, \"price\": 2999, \"value\": 198, \"isLoot\": false, \"category\": \"Gadgets\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Fifty percent hook, fifty percent blade, hundred percent awesome.\", \"isPurchasable\": true}",
                "version": "45c7f1ef2133b3a205272b4ed14e8836",
                "permission_read": 2,
                "create_time": "2025-06-04T16:58:59Z",
                "update_time": "2025-06-04T16:58:59Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_hoverpad",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_hoverpad\", \"name\": \"Hoverpad\", \"netID\": 30, \"price\": 4000, \"value\": 230, \"isLoot\": false, \"category\": \"Gadgets\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Activate to propel against the ground.\", \"isPurchasable\": true}",
                "version": "9b416d237835903a3fcdf183a329de9b",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-06T19:18:13Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_impulse_grenade",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_impulse_grenade\", \"name\": \"Impulse Grenade\", \"netID\": 89, \"price\": 299, \"value\": 22, \"isLoot\": false, \"category\": \"Explosives\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Throw it and watch everyone around you get yeeted.\", \"isPurchasable\": true}",
                "version": "bfbd9dc11fce94f6efc1451087235a9d",
                "permission_read": 2,
                "create_time": "2024-12-06T19:18:13Z",
                "update_time": "2025-01-14T16:26:51Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_jetpack",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_jetpack\", \"name\": \"Jetpack\", \"netID\": 17, \"price\": 121, \"value\": 11, \"isLoot\": false, \"category\": \"Gadgets\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Activate and hold on to fly into the sky.\", \"isPurchasable\": true}",
                "version": "78a95e1e582dcf7a6d88d9bd814b5355",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2024-12-06T19:18:13Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_keycard",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_keycard\", \"name\": \"Keycard\", \"netID\": 125, \"price\": 999, \"value\": 99, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"An employee keycard. It can be used to activate Canopy equipment.\\n\\n\", \"isPurchasable\": false}",
                "version": "3a6a592ca68c91fcdac7f6feebcab893",
                "permission_read": 2,
                "create_time": "2025-03-10T14:55:16Z",
                "update_time": "2025-07-02T21:31:45Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_lance",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_lance\", \"name\": \"Lance\", \"netID\": 74, \"price\": 499, \"value\": 24, \"isLoot\": false, \"category\": \"Weapons\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A huge lance letting you attack from a distance.\", \"isPurchasable\": true}",
                "version": "d2422c6b758dec0532cf4e2cb68b69c3",
                "permission_read": 2,
                "create_time": "2024-11-20T12:59:18Z",
                "update_time": "2024-12-06T04:29:14Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_landmine",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_landmine\", \"name\": \"Landmine\", \"netID\": 156, \"price\": 219, \"value\": 19, \"isLoot\": false, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Buried surprises are the best kind. For you, not for them.\", \"isPurchasable\": false}",
                "version": "564cd89c463ff37e2ab1a0c87b55fa1e",
                "permission_read": 2,
                "create_time": "2025-05-23T21:41:48Z",
                "update_time": "2025-05-23T21:41:48Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_large_banana",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_large_banana\", \"name\": \"Large Banana\", \"netID\": 24, \"price\": 2147483647, \"value\": 44, \"isLoot\": true, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Probably grown from a larger tree. Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "152908fc72557bb4785c4dc6ddfcbacb",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_mug",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_mug\", \"name\": \"Mug\", \"netID\": 130, \"price\": 999, \"value\": 24, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A simple mug.\", \"isPurchasable\": false}",
                "version": "7f469b5ddb8ab8734b300d97d57a40a0",
                "permission_read": 2,
                "create_time": "2025-03-10T14:55:16Z",
                "update_time": "2025-03-10T14:55:16Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_nut",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_nut\", \"name\": \"Nut\", \"netID\": 31, \"price\": 2147483647, \"value\": 89, \"isLoot\": true, \"category\": \"Hidden\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Currency...the economy is nuts.\", \"isPurchasable\": false}",
                "version": "1f0b36b3265bd86aea30b33c3c9a20ce",
                "permission_read": 2,
                "create_time": "2024-10-18T14:51:03Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_nut_drop",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_nut_drop\", \"name\": \"Nut Drop\", \"netID\": 148, \"price\": 9999, \"value\": 1, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Currency...the economy is nuts.\", \"isPurchasable\": false}",
                "version": "fbdf1addfd23157111c79cf9c7d0551b",
                "permission_read": 2,
                "create_time": "2025-05-01T20:28:52Z",
                "update_time": "2025-05-01T20:28:52Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_ogre_hands",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_ogre_hands\", \"name\": \"Ogre Hands\", \"netID\": 66, \"price\": 349, \"value\": 21, \"isLoot\": false, \"category\": \"Weapons\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Green and mean, perfect for SMASHING enemies.\", \"isPurchasable\": true}",
                "version": "aa58f5debcbb21d8155822464361af56",
                "permission_read": 2,
                "create_time": "2024-11-11T23:46:08Z",
                "update_time": "2024-12-10T16:40:01Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_ore_copper_l",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_ore_copper_l\", \"name\": \"Large Copper Chunk\", \"netID\": 95, \"price\": 2147483647, \"value\": 45, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A conductive metal. Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "c846ea7e3a0851e4d1f6687da08f1b07",
                "permission_read": 2,
                "create_time": "2025-01-14T16:26:51Z",
                "update_time": "2025-02-16T23:04:40Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_ore_copper_m",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_ore_copper_m\", \"name\": \"Copper Chunk\", \"netID\": 94, \"price\": 2147483647, \"value\": 32, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A conductive metal. Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "40d597937febb4c66cbc5689f676a885",
                "permission_read": 2,
                "create_time": "2025-01-14T16:26:51Z",
                "update_time": "2025-02-16T23:04:40Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_ore_copper_s",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_ore_copper_s\", \"name\": \"Small Copper Chunk\", \"netID\": 93, \"price\": 2147483647, \"value\": 23, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"A conductive metal. Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "ffcf7a801be7833fd77963a33e3655f6",
                "permission_read": 2,
                "create_time": "2025-01-14T16:26:51Z",
                "update_time": "2025-02-16T23:04:40Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_ore_gold_l",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_ore_gold_l\", \"name\": \"Large Gold Chunk\", \"netID\": 101, \"price\": 2147483647, \"value\": 165, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Valuable metal. Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "64057be4053e83e9872f53a5f9fff0c4",
                "permission_read": 2,
                "create_time": "2025-01-14T16:26:51Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_ore_gold_m",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_ore_gold_m\", \"name\": \"Gold Chunk\", \"netID\": 100, \"price\": 2147483647, \"value\": 89, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Valuable metal. Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "a034a29371152da8320c1f2de73176d8",
                "permission_read": 2,
                "create_time": "2025-01-14T16:26:51Z",
                "update_time": "2025-02-16T22:55:57Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_ore_gold_s",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_ore_gold_s\", \"name\": \"Small Gold Chunk\", \"netID\": 99, \"price\": 2147483647, \"value\": 45, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"Valuable metal. Turn this in for Nuts.\", \"isPurchasable\": false}",
                "version": "59d31a660f938861cb9b2161dbe2bfc9",
                "permission_read": 2,
                "create_time": "2025-01-14T16:26:51Z",
                "update_time": "2025-02-16T23:04:40Z"
            },
            {
                "collection": "econ_gameplay_items",
                "key": "item_ore_hell",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "value": "{\"id\": \"item_ore_hell\", \"name\": \"Cinder\", \"netID\": 113, \"price\": 2147483647, \"value\": 500, \"isLoot\": true, \"category\": \"Loot\", \"isUnique\": false, \"isDevOnly\": false, \"description\": \"It's warm to the touch.\", \"isPurchasable\": false}",
                "version": "b2beddac65eac1ee428c0fa2b7eb84b4",
                "permission_read": 2,
                "create_time": "2025-02-07T17:35:04Z",
                "update_time": "2025-05-13T17:42:13Z"
            }
        ],
        "cursor": "OP-RAwEBDXN0b3JhZ2VDdXJzb3IB_5IAAQMBA0tleQEMAAEGVXNlcklEAf-KAAEEUmVhZAEEAAAAEP-JBgEBBFVVSUQB_4oAAAAU_5IBDWl0ZW1fb3JlX2hlbGwCBAA"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6957)