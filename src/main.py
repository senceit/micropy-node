import machine
import time

import network
import math

from webserver import Webserver
from esp8266 import ESP8266
from io import LevelSensor

__version__ = "0.1.0"

TRIGGER_PIN = 5
ECHO_PIN = 4
LED_PIN = 2

# Wi-Fi configuration
STA_SSID = "Swart"
STA_PASS = "870622eta"

led_pin = machine.Pin(LED_PIN, machine.Pin.OUT)

# # Handler for path "/"
# def handle_root(web: Webserver, args):
#     global rootPage
#     # Replacing title text and display text color according
#     # to the status of LED
#     response = rootPage.format(
#         "Remote LED",
#         "red" if led_pin.value() else "green",
#         "Off" if led_pin.value() else "On",
#         "on" if led_pin.value() else "off",
#         "Turn on" if led_pin.value() else "Turn off",
#     )
#     # Return the HTML page
#     web.ok("200", response)


# Handler for path "/switch?led=[on|off]"
def handle_switch(web: Webserver, args):
    if "led" in args:
        if args["led"] == "on":
            led_pin.off()
        elif args["led"] == "off":
            led_pin.on()
        # handle_root(web, args)
    else:
        web.err("400", "Bad Request")


# handler for path "/switch"
def handle_toggle(web: Webserver, args):
    toggle(led_pin)
    # Switch back and forth
    web.ok("200", "On" if led_pin.value() == 0 else "Off")


if __name__ == "__main__":

    device = ESP8266()

    # Start the server @ port 80
    print("Starting web server on port 80")
    web = Webserver()
    web.start(80)
    # Setting the path to documents
    web.set_www_root("www")

    # Register handler for each path
    web.register_handler("/switch", handle_switch)
    web.register_handler("/toggle", handle_toggle)

    try:
        while True:
            # dist = sensor.distance_mm()
            # level, pct, vol = calc_volume(1500, 1800, dist, 3000)
            # Let server process requests
            web.handle_client()

            # print(
            #     "Level (m), '%', Volume (l): "
            #     + str(level / 1000)
            #     + ", "
            #     + str(pct)
            #     + ", "
            #     + str(vol)
            # )
            # time.sleep(1)
    except NameError as err:
        print("Unhandled exception: " + str(err))
        web.close()
