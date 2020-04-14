##
#
# Copyright 2020 - Intersect Technologies CC
# Author: Niel Swart <niel@nielswart.com>
#
##

import ultrasonic
import json
import re
import math
from machine import Timer
import time

from util import Logger, signal_filter


log = Logger.getLogger()


class Peripheral:
    def __init__(self, id, _type):
        self.id = id
        self._type = _type


class Actuator(Peripheral):
    def __init__(self, pin):
        self.p = pin

    def toggle(self):
        self.p.value(not self.p.value())

    def value(self):
        return self.p.value()


class Led(Actuator):
    """
    """

    def on(self):
        """
        """

    def off(self):
        """
        """


class Sensor(Peripheral):
    def __init__(self, id, _type):
        super().__init__(id, _type)

    def _create_payload(self, id, loc):
        return json.dumps(
            {
                "timestamp": time.time(),
                "device_id": id,
                "peripheral_id": self.id,
                "type": self._type,
                "location": {"lon": loc[0], "lat": loc[1]},
                "measurement": self.stat(),
            }
        )

    def stat(self):
        pass


class LevelSensor(Sensor):
    def __init__(self, id, pin_mapping, config):
        super().__init__(id, "LevelSensor")
        trigger = pin_mapping["trigger_pin"]
        echo = pin_mapping["echo_pin"]
        log.info("Configured trigger @ pin {} and echo @ pin {}".format(trigger, echo))
        self.sensor = ultrasonic.HCSR04(trigger, echo)
        self.config = config
        self.dh, self.sh, self.dd = self.parse_parameters()

    def calc_volume(self, distance, dam_height, sensor_height, diameter=None):
        """
        Given the diameter of a dam/tank
        the height palcement of the range sensor
        and the distance from the liquid surface

        We calculate the volume of liquid in the tank/dam
        """

        level = int(sensor_height) - int(distance)
        level = level if level > 0 else 0
        pct = math.trunc((level / dam_height) * 100)
        if diameter:
            volume = math.trunc(math.pi * ((diameter / 2000) ** 2) * (level))
        else:
            volume = None

        return level, pct, volume

    def parse_parameters(self):
        dh = self.config["dam_height"]
        sh = self.config["sensor_height"]
        dd = self.config.get("dam_diameter", None)

        # convert everything to mm
        out = []
        for p in [dh, sh, dd]:
            if type(p) == dict:
                out.append(self.convert(p))
            else:
                out.append(None)

        return tuple(out)

    def convert(self, m):
        if m["unit"] == "mm":
            mult = 1
        elif m["unit"] == "cm":
            mult = 10
        elif m["unit"] == "m":
            mult = 1000
        else:
            raise AttributeError("Unsupported measurement unit")

        return mult * int(m["measure"])

    def stat(self):
        """
        """

        min = self.sh - self.dh
        d = []
        for i in range(8):
            t = self.sensor.distance_mm()
            if t > min:
                d.append(t)
            time.sleep_ms(1)
        dist = signal_filter(d)
        log.info("Measured distance: {} mm".format(dist))
        level, pct, vol = self.calc_volume(dist, self.dh, self.sh, self.dd)
        return [
            {"type": "Level", "unit": "mm", "value": level},
            {"type": "Level", "unit": "%", "value": pct},
            {"type": "Level", "unit": "liter", "value": vol},
        ]


class DataLogger:
    def __init__(self, device_id, loc, tx, interval: int, topic: str, sensor: Sensor):
        self.timer = None
        self.topic = topic
        self.interval = 1  # defualt interval is 1000ms
        if interval.rstrip().endswith("m"):
            self.interval = int(interval[:-1]) * 60
        elif interval.rstrip().endswith("h"):
            self.interval = int(interval[:-1]) * 3600
        elif interval.rstrip().endswith("s"):
            self.interval = int(interval[:-1])
        self.interval *= 1000
        self.is_running = False
        self.sender = tx
        self.sensor = sensor
        self.device_id = device_id
        self.loc = loc

    def run(self):
        self.sender(self.topic, self.sensor._create_payload(self.device_id, self.loc))
        log.info("Transmitting data...")

    def start(self):
        if not self.is_running:
            self.timer = Timer(-1)
            cb = lambda _: self.run()
            self.timer.init(period=self.interval, mode=Timer.PERIODIC, callback=cb)
            self.is_running = True
            log.info(
                "Started Data Logger for {} at an interval of {} ms, sending data to {}".format(
                    self.sensor.id, self.interval, self.topic
                )
            )

    def stop(self):
        self.timer.deinit()
        self.is_running = False

    @staticmethod
    def validate_topic(_type):
        if _type == "cmnd":
            #
            p = re.compile("(?=[^/].*)(\\S*)")
        return True if (p.match(topic) != None) else False


class DataLoggerFactory:
    peripherals = {"USLS01": LevelSensor}

    @staticmethod
    def create(
        id, device_id, loc, sender, topic, interval, trigger=None, *args
    ) -> DataLogger:
        sensor = DataLoggerFactory.peripherals[id](id, *args)
        logger = DataLogger(device_id, loc, sender, interval, topic, sensor)
        return logger
