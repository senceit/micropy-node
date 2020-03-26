import ultrasonic


class Output:
    def __init__(self, pin):
        self.p = pin

    def toggle(self):
        self.p.value(not self.p.value())


class Led(Output):
    """
    """

    def on(self):
        """
        """

    def off(self):
        """
        """


class Logger:
    def __init__(self, tx: Transmitter, interval: int, sensor: Sensor):
        self.tx = tx
        self.interval = interval

    def start(self):
        """
        """

    def stop(self):
        """
        """


class Sensor:
    def measure(self):
        return 0


class LevelSensor(Sensor):
    def __init__(self, trigger_pin, echo_pin):
        self.sensor = ultrasonic.HCSR04(trigger_pin, echo_pin)

    def calc_volume(self, dam_height, sensor_height, distance, diameter=None):
        """
        Given the diameter of a dam/tank
        the height palcement of the range sensor
        and the distance from the liquid surface

        We calculate the volume of liquid in the tank/dam
        """
        level = sensor_height - distance
        pct = (level / dam_height) * 100
        if diameter:
            volume = math.pi * ((diameter / 2000) ** 2) * (level / 1000)
        else:
            volume = None

        return level, pct, volume

    def measure(self):
        """
        """
        dist = sensor.distance_mm()
        level, pct, vol = calc_volume(1500, 1800, dist, 3000)


class Transmitter:
    def send(self):
        """
        """
