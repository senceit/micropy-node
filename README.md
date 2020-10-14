# SenceIt

SenceIt Ndoes use [Micropython](https://micropython.org/) firmware.

NOTE:  This is not Arduino compatible.

## Project Structure

* senceit-node - contains the micropython code that can be deployed to an ESP8266 device
* senceit-ctrl - A NodeRED server and MQTT broker running as docker containers

## SensorNode

A MicroPython sensor node device.

Tested with the ESP8266 NodeMCU device

This section applies to the `./senceit-node` project in the repository:


### Environment setup

You need to have python installed with pip. 
You also need to install Node.js and npm to run the web build scripts

**Windows**: 

- Download: https://www.python.org/downloads/windows/ and follow the instructions to install python and pip
- Download: https://nodejs.org/en/download/ and follow the insturction to install Node and npm

Open a command prompt or powershell and change your directory to:

```pwsh
cd ./senceit-node
```

```cmd
pip install esptool
```

This will install the esptool that is used to flash firmware to the device.

**Linux**:

- You should have a default python environment installed

Full instructions can be found at https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html#intro

```bash
pip install esptool
```

Getting the latest firmware

```bash
curl http://micropython.org/resources/firmware/esp8266-20191220-v1.12.bin -o ./firmware/esp8266-20191220-v1.12.bin
```

or download version `1.12` from https://micropython.org/download/esp8266/ and save it

WSL NOTE: USB and serial devices are currently not supported in WSL 2 and you need to do this part in Windows

#### Erasing the device flash with esptool

To enable ESP8266 firmware flashing GPIO0 pin must be pulled low before the device is reset.
Put the NodeMCU board in flash mode by

```pwsh
esptool.py --port COM3 erase_flash
```

**Windows**:

Use the correct COM port on your computer

**Linux**:

### Flashing the device with MicroPython Firmware

```pwsh
esptool.py --port COM3 --baud 460800 write_flash --flash_size=detect 0 .\firmware\esp8266-20191220-v1.12.bin
```

Replace the path to the firmware you downloaded in the command above.

The device should now be available as a Wifi access point with ESSID in the form MicroPython-xxxxxx

#### Enable Webrepl with password

TODO

### Build

Install poetry

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

#### Install the necessary build tooling

**ALL**

```
make install-deps
```

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

## SenceIt-Ctrl

This section applies to the `./senceit-ctrl` project

### Run

```bash
cd ./senceit-ctrl/gateway
docker-compose up -d
```
