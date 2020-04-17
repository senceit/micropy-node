##
#
# Copyright 2020 - Intersect Technologies CC
# Author: Niel Swart <niel@nielswart.com>
#
##

import time
import gc
from machine import Timer

from util import Logger

from webserver import Webserver
from uhttp import Http, HTTP_METHOD, HttpResponse, HttpRequest
from esp8266 import ESP8266

log = Logger.getLogger()
device = ESP8266()


def get_config(request: HttpRequest):
    """
    TODO: single API call for device config
    - Wifi Networks
    - Device ID
    - Supported sensors
    - Default SenceIt Ctrl IP

    What do we do about security?
    """
    global device

    from config import config

    resp = config
    resp["networks"] = device.wifi_networks

    return HttpResponse.ok(200, Http.MIME_TYPE["JSON"], body=resp)


def save_config(req: HttpRequest):
    """
    Save config
    """
    global device
    resp = {}
    resp["success"] = True
    with open("config.json", "w") as config:
        for l in req.body:
            config.write(l)

    # set device in run mode
    device.enable_run_mode()

    # start timer to reboot device in 5 s
    timer = Timer(-1)
    cb = lambda _: device.reboot()
    timer.init(period=5000, mode=Timer.ONE_SHOT, callback=cb)

    return HttpResponse.ok(200, Http.MIME_TYPE["JSON"], body=resp)


def main():
    http = Http()

    # Register handler for each path
    http.register_handler(HTTP_METHOD.GET, "/config", get_config)
    http.register_handler(HTTP_METHOD.POST, "/config", save_config)

    # Start the server @ port 80
    log.info("IP: {}".format(device.get_ip()))
    log.info("Device ID: {}".format(device.id))
    web = Webserver(http)
    web.start(80)
    gc.collect()

    try:
        while True:
            # Let server process requests
            web.handle_client()

            time.sleep_ms(50)
    except Exception as err:
        log.severe("Unhandled exception: " + str(err))
    finally:
        web.close()
