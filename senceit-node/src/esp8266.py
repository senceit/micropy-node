##
#
# Copyright 2020 - Intersect Technologies CC
# Author: Niel Swart <niel@nielswart.com>
#
##

import network
import machine

from util import Logger

log = Logger.getLogger()


class ESP8266:
    def __init__(self, config_path=""):
        self.config_path = config_path

    @property
    def wifi_networks(self):
        """
        Get available Wifi networks
        """
        import time

        nic = network.WLAN(network.STA_IF)
        nic.active(True)
        time.sleep_ms(10)
        nets = [x[0] for x in nic.scan() if x[5] == 0]
        time.sleep_ms(10)
        nic.active(False)
        return nets

    @property
    def id(self):
        """
        """

        self.get_config()

        return self.config["id"]

    @property
    def mac_addr(self):
        return machine.unique_id()

    def _get_config_path(self):
        return (
            self.config_path + "/device_mode.py"
            if self.config_path != ""
            else "device_mode.py"
        )

    def enable_run_mode(self):
        log.info("Enabling configuration mode on restart")
        with open(self._get_config_path(), "w",) as mode:
            mode.write("CONFIG_MODE = False")

    def hard_reset(self):
        """
        Enable config mode
        """
        import time

        log.info("Enabling configuration mode on restart")
        with open(self._get_config_path(), "w") as mode:
            mode.write("CONFIG_MODE = True")

        # set to AP mode

        for i in range(5):
            log.info("Restarting in {}s".format(5 - i))
            time.sleep(1)

        self.reboot()

    def reboot(self):
        """
        """
        log.info("Rebooting SenceIt Node {}".format(self.id))
        machine.reset()

    def activate_ap(self):
        """
        """
        log.info("Changing Wifi to AP mode")
        sta = network.WLAN(network.STA_IF)  # create station interface
        if sta.active() or sta.isconnected():
            sta.active(False)

        ap = network.WLAN(network.AP_IF)
        if not ap.active():
            ap.active(True)

        ssid = "SENCEIT-{}".format(self.id)
        pwd = "PWD-{}".format(self.id)
        log.info("Creating AP {} with password: {}".format(ssid, pwd))
        ap.config(
            essid=ssid, password=pwd, authmode=network.AUTH_WPA_WPA2_PSK
        )  # set the ESSID of the access point

    def sta_config(self, ap_if, ssid, pwd):
        """
        activate station config
        """
        # Connect to Wi-Fi if not connected
        sta_if = network.WLAN(network.STA_IF)
        if not ap_if.active():
            sta_if.active(True)
        if not sta_if.isconnected():
            log.info("Connecting to {}...".format(ssid))
            sta_if.connect(ssid, pwd)
            # Wait for connecting to Wi-Fi
            while not sta_if.isconnected():
                pass

        return sta_if

    def connect_to_wifi(self):
        # Disable AP interface
        ap_if = network.WLAN(network.AP_IF)
        if ap_if.active():
            ap_if.active(False)

        sta_if = self.sta_config(
            ap_if, self.config["wifi"]["ssid"], self.config["wifi"]["password"]
        )
        # Show IP address
        ip = sta_if.ifconfig()[0]
        log.info("Connected to " + self.config["wifi"]["ssid"] + " with IP: " + ip)

    def init_peripherals(self, sender):
        """
        """
        from esp_io import DataLoggerFactory, DataLogger

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
        import gc

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
        import json

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
        """
        Returns the key and name of the peripherals
        """

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
        id = self.config["peripherals"][key]["id"]
        return self.config["pin_mapping"][id]

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
