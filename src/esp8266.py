##
#
# Copyright 2020 - Intersect Technologies CC
# Author: Niel Swart <niel@nielswart.com>
#
##

import network
import esp
import machine
import gc
import json
import os
import time

from util import Logger

from esp_io import DataLoggerFactory, DataLogger

log = Logger.getLogger()


class ESP8266:
    def __init__(self, config_path=""):
        self.config_path = config_path

    @property
    def wifi_networks(self):
        """
        Get available Wifi networks
        """

        nic = network.WLAN(network.STA_IF)
        return [x[0] for x in nic.scan() if x[5] == 0]

    @property
    def id(self):
        """
        """

        self.get_config()

        return self.config["id"]

    @property
    def mac_addr(self):
        return machine.unique_id()

    def enable_run_mode(self):
        log.info("Enabling configuration mode on restart")
        with open(os.path.join(self.config_path, "device_mode.py"), "w") as mode:
            mode.write("CONFIG_MODE = False")

    def hard_reset(self):
        """
        Enable config mode
        """

        log.info("Enabling configuration mode on restart")
        with open(os.path.join(self.config_path, "device_mode.py"), "w") as mode:
            mode.write("CONFIG_MODE = True")

        for i in range(5):
            log.info("Restarting in {}s".format(5 - i))
            time.sleep(1)

        self.reboot()

    def reboot(self):
        """
        """
        log.info("Rebooting SenceIt Node {}".format(self.id))
        machine.reset()

    def sta_config(self, ap_if, ssid, pwd):
        """
        activate station config
        """
        # Connect to Wi-Fi if not connected
        sta_if = network.WLAN(network.STA_IF)
        if not ap_if.active():
            sta_if.active(True)
        if not sta_if.isconnected():
            sta_if.connect(ssid, pwd)
            # Wait for connecting to Wi-Fi
            while not sta_if.isconnected():
                pass

        return sta_if

    def connect_to_wifi(self, ssid, pwd):
        # Disable AP interface
        ap_if = network.WLAN(network.AP_IF)
        if ap_if.active():
            ap_if.active(False)

        sta_if = self.sta_config(ap_if, ssid, pwd)
        # Show IP address
        ip = sta_if.ifconfig()[0]
        log.info("Connected to " + ssid + " with IP: " + ip)

    def init_peripherals(self, sender):
        """
        """
        self.loggers = {}
        for k, p in self.get_peripherals().items():
            #  def create(id, topic, interval, trigger=None, *args):
            self.loggers[k] = DataLoggerFactory.create(
                self._get_peripheral_id(k),
                self.id,
                self._get_location(),
                sender,
                self._get_topic(k),
                self._get_interval(k),
                None,
                self._get_pin_mapping(k),
                self._get_parameters(k),
            )

    def start(self):
        for k, l in self.loggers.items():
            l.start()

        machine.idle()

    def get_stats(self):
        freq = machine.freq()
        free_mem = gc.mem_free()

        return (freq, free_mem)

    def get_ip(self):
        sta_if = network.WLAN(network.STA_IF)
        return sta_if.ifconfig()[0]

    def get_mqtt_broker(self):
        return self.config["mqtt"]["ip"]

    def get_config(self) -> dict:
        from config import config

        self.config = config.copy()
        peripherals = self.config["peripherals"]
        with open(self.config_path + "/config.json") as fp:
            conf = json.load(fp)
        for k in self.config.keys():
            if k in conf:
                self.config[k] = conf[k]

        for k, v in self.config["peripherals"].items():
            self.config["peripherals"][k]["id"] = peripherals[v["name"]]["id"]

        return self.config

    def get_sensors(self):
        return dict(
            [
                (key, value["name"])
                for key, value in self.config["peripherals"].items()
                if value["type"] == "sensor"
            ]
        )

    def get_peripherals(self):
        return dict(
            [(key, value["name"]) for key, value in self.config["peripherals"].items()]
        )

    def _get_location(self) -> (float, float):
        return self.config["location"]

    def _get_topic(self, key):
        """
        Add topic prefix and sensor specific topic to form full topic
        """

        return self.config["peripherals"][key]["config"]["topic"]

    def _get_interval(self, key):
        """
        """

        return self.config["peripherals"][key]["config"]["interval"]

    def _get_parameters(self, key):
        """
        """

        return self.config["peripherals"][key]["config"]["parameters"]

    def _get_pin_mapping(self, key):
        """
        """

        return self.config["pin_mapping"][key]

    def _get_peripheral_id(self, key):
        """
        """

        if key in self.config["peripherals"]:
            return self.config["peripherals"][key]["id"]

        return False

    @staticmethod
    def time_sync():
        """
        Sync time with NTP if available
        """


class Wifi:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password


class Mqtt:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
