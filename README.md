# SenceIt

## SensorNode

A MicroPython sensor node device.

Tested with the ESP8266 NodeMCU device

## Environment setup

You should have python installed with pip. Full instructions can be found at https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html#intro

```bash
pip install esptool
```

Getting the latest firmware

```bash
curl http://micropython.org/resources/firmware/esp8266-20191220-v1.12.bin -o ./firmware/esp8266-20191220-v1.12.bin
```

NOTE: USB and serial devices are currently not supported on WSL 2 and you need to do this part in windows

In order to minify the static content on the webserver install

### Erasing the device flash with esptool

To enable ESP8266 firmware flashing GPIO0 pin must be pulled low before the device is reset.
Put the NodeMCU board in flash mode by

```bash
esptool.py --port COM3 erase_flash
```

### Flashing the device with MicroPython Firmware

```powershell
esptool.py --port COM3 --baud 460800 write_flash --flash_size=detect 0 .\firmware\esp8266-20191220-v1.12.bin
```

The device should now be available as a Wifi access point with ESSID in the form MicroPython-xxxxxx

### Enable Webrepl with password

## Build

Install poetry

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

### Install the necessary build tooling

**HTML**

```bash
npm install html-minifier-cli -g
```

**CSS**

```bash
npm install -g cssnano
```

**JS**

```bash
npm install -g uglify-es
```

```bash
make build
```

### Deploy

```bash
make deploy
```

### Run SenceIt Ctrl software

```bash
cd ./gateway
docker-compose up -d
```
