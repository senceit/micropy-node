import network


class ESP8266:
    def __init__(self, web: Webserver, SSID: str, PWD: str):
        self.web = web
        self.SSID = SSID
        self.passwd = PWD

    @property
    def wifi_networks(self):
        """
        """

    @property
    def device_id(self):
        """
        """

    def reset(self):
        """
        activate SenceIt AP
        """

    def sta_config(self, ap_if):
        """
        activate station config
        """
        # Connect to Wi-Fi if not connected
        sta_if = network.WLAN(network.STA_IF)
        if not ap_if.active():
            sta_if.active(True)
        if not sta_if.isconnected():
            sta_if.connect(self.SSID, self.passwd)
            # Wait for connecting to Wi-Fi
            while not sta_if.isconnected():
                pass

        return sta_if

    def connect_to_wifi(self):
        # Disable AP interface
        ap_if = network.WLAN(network.AP_IF)
        if ap_if.active():
            ap_if.active(False)

        sta_if = sta_config(ap_if)
        # Show IP address
        print("Server started @ ", sta_if.ifconfig()[0])

