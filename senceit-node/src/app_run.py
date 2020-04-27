##
#
# Copyright 2020 - Intersect Technologies CC
# Author: Niel Swart <niel@nielswart.com>
#
##

import time
import machine
from umqtt.robust import MQTTClient

from esp8266 import ESP8266
from util import Logger
import gc

log = Logger.getLogger()

device = ESP8266()


def setup():
    """
    """
    global device

    device.get_config()
    device.connect_to_wifi()

    id = device.id
    ip = device.get_mqtt_broker()

    log.info("Connecting to MQTT broker @ {}".format(ip))
    log.info("Device ID: {}".format(id))
    log.info("Free memory: {}".format(gc.mem_free()))

    mqtt = MQTTClient(id, ip)
    time.sleep_ms(50)
    try:
        status = mqtt.connect()
        log.info("Connected successfully - status: {}".format(status))
    except:
        log.severe("Could not connect to MQTT broker")
        mqtt.reconnect()

    # Create sender
    sender = lambda topic, message: mqtt.publish(topic, message)
    device.init_peripherals(sender)

    return mqtt


def main():
    mqtt = setup()
    gc.collect()
    device.start()

    while True:
        log.info("Awaiting action...")
        mqtt.wait_msg()
