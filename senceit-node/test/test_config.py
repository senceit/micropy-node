import sys
from unittest.mock import Mock
import os

sys.modules["network"] = Mock()
sys.modules["esp"] = Mock()
sys.modules["machine"] = Mock()

from esp8266 import ESP8266
from esp_io import DataLoggerFactory, DataLogger


def test_id():
    from config import config

    assert config["id"] == "FB20GY"


def test_config_override():
    device = ESP8266(os.path.join(os.getcwd(), "test"))

    config = device.get_config()

    assert config["wifi"]["ssid"] == "Swart"
    assert config["mqtt"]["ip"] == "10.0.0.117"
    assert config["location"][0] == 25.55
    assert config["location"][1] == -23.55
    assert "peripherals" in config
    assert "0" in config["peripherals"]


def test_config_mode():
    import device_mode

    assert device_mode.CONFIG_MODE is True

    device = ESP8266(os.path.join(os.getcwd(), "test"))
    device.hard_reset(0)

    import test.device_mode

    assert test.device_mode.CONFIG_MODE is True


def test_get_config_match():
    from config import config

    device = ESP8266(os.path.join(os.getcwd(), "test"))
    device.get_config()

    sensors = device.get_sensors()

    assert len(sensors.keys()) == 1
    assert "LevelSensor" in sensors.values()

    for k, s in sensors.items():
        p_id = device._get_peripheral_id(k)
        assert p_id == "USLS01"

        pin_mapping = device._get_pin_mapping(k)
        assert "trigger_pin" in pin_mapping

        parms = device._get_parameters(k)
        assert "dam_height" in parms

        topic = device._get_topic(k)
        assert topic == "dam/level/level1"

        interval = device._get_interval(k)
        assert interval == "15m"

        loc = device._get_location()
        assert loc is not None

        #  def create(id, topic, interval, trigger=None, *args):
        tx = lambda top, msg: print("Topic: {}, Message: ".format(top, msg))
        logger = DataLoggerFactory.create(
            p_id, device.id, loc, tx, topic, interval, None, pin_mapping, parms,
        )
        assert isinstance(logger, DataLogger)
