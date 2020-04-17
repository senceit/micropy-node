config = {
    "id": "FB20GY",
    "version": "0.1.0",
    "arch": "esp8266",
    "wifi": {"ssid": "SenceIt"},
    "mqtt": {"ip": "senceit-ctrl"},
    "location": (25.59877, -23.54654),
    "peripherals": {
        "LevelSensor": {
            "id": "USLS01",
            "type": "sensor",
            "interval": "15m",
            "trigger": None,
            "topic": "dam/level",
            "parameters": {
                "dam_height": {"value": 1500, "unit": "mm"},
                "sensor_height": {"value": 1700, "unit": "mm"},
                "dam_diameter": {"value": 6, "unit": "m"},
            },
        },
    },
    "topic_prefix": {"sensor": "stat", "actuator": "cmnd"},
    "pin_mapping": {"USLS01": {"trigger_pin": 14, "echo_pin": 15},},
}
