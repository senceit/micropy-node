ip = ${IP}
password = ${PASSWORD}

IN = $(wildcard src/*.py)
IN2 = $(addsuffix .mpy,$(basename $(IN)))
OUT = $(subst src/,build/, $(IN2))

default: build-dev

install-deps:
	npm install -g html-minifier-cli
	npm install -g cssnano
	npm install -g uglify-es

setup: install-deps
	echo "Install webrepl"
	echo "Downloading MicroPython for Esp8266"
	curl http://micropython.org/resources/firmware/esp8266-20191220-v1.12.bin -o ./firmware/esp8266-20191220-v1.12.bin

clean:
	rm -rf build/*

build/%.mpy: src/%.py
	poetry run python -m mpy_cross $< -o $@

compile: $(OUT)

build-common: clean compile
	mkdir -p build/www/css
	mkdir -p build/www/js
	mkdir -p build/www/img
	cp src/main.py build/main.py
	cp src/device_mode.py build/device_mode.py
	cp src/ultrasonic.py build/ultrasonic.py
	cp src/config.json build/config.json
	cp www/img/silogo42x136.png build/www/img/silogo42x136.png
	cssnano www/css/style.css build/www/css/temp.min.css

build-prod: build-common
	gzip -c build/www/css/temp.min.css > build/www/css/style.min.css && rm build/www/css/temp.min.css
	htmlmin www/index.html | gzip -c > build/www/index.html
	uglifyjs --compress --mangle -- www/js/scripts.js | gzip -c > build/www/js/scripts.min.js


build-dev: build-common
	htmlmin www/index.html -o build/www/index.html
	uglifyjs --compress --mangle -o build/www/js/scripts.min.js -- www/js/scripts.js
	cp build/www/css/temp.min.css build/www/css/style.min.css && rm build/www/css/temp.min.css

build-web:
	cssnano www/css/style.css build/www/css/style.min.css
	htmlmin www/index.html -o build/www/index.html
	uglifyjs --compress --mangle -o build/www/js/scripts.min.js -- www/js/scripts.js

deploy:
	echo "Deploy"
	python webrepl/webrepl_cli.py -p $(password) build/main.py $(ip):/main.py
	python webrepl/webrepl_cli.py -p $(password) build/app_config.mpy $(ip):/app_config.mpy
	python webrepl/webrepl_cli.py -p $(password) build/app_run.mpy $(ip):/app_run.mpy
	python webrepl/webrepl_cli.py -p $(password) build/ultrasonic.py $(ip):/ultrasonic.py
	python webrepl/webrepl_cli.py -p $(password) build/esp_io.mpy $(ip):/esp_io.mpy
	python webrepl/webrepl_cli.py -p $(password) build/esp8266.mpy $(ip):/esp8266.mpy
	python webrepl/webrepl_cli.py -p $(password) build/webserver.mpy $(ip):/webserver.mpy
	python webrepl/webrepl_cli.py -p $(password) build/uhttp.mpy $(ip):/uhttp.mpy
	python webrepl/webrepl_cli.py -p $(password) build/util.mpy $(ip):/util.mpy
	python webrepl/webrepl_cli.py -p $(password) build/stepper.mpy $(ip):/stepper.mpy
	python webrepl/webrepl_cli.py -p $(password) build/config.mpy $(ip):/config.mpy
	python webrepl/webrepl_cli.py -p $(password) build/device_mode.py $(ip):/device_mode.py
	python webrepl/webrepl_cli.py -p $(password) build/config.json $(ip):/config.json
	python webrepl/webrepl_cli.py -p $(password) build/www/index.html $(ip):/www/index.html
	python webrepl/webrepl_cli.py -p $(password) build/www/img/silogo42x136.png $(ip):/www/img/silogo42x136.png
	python webrepl/webrepl_cli.py -p $(password) build/www/css/style.min.css $(ip):/www/css/style.min.css
	python webrepl/webrepl_cli.py -p $(password) build/www/js/scripts.min.js $(ip):/www/js/scripts.min.js

deploy-web:
	python webrepl/webrepl_cli.py -p $(password) build/www/index.html $(ip):/www/index.html
	python webrepl/webrepl_cli.py -p $(password) build/www/js/scripts.min.js $(ip):/www/js/scripts.min.js

deploy-app:
	python webrepl/webrepl_cli.py -p $(password) build/app_config.mpy $(ip):/app_config.mpy
	python webrepl/webrepl_cli.py -p $(password) build/app_run.mpy $(ip):/app_run.mpy

config-mode:
	python webrepl/webrepl_cli.py -p $(password) build/device_mode.py $(ip):/device_mode.py

test:
	poetry run pytest --ignore=micropython/

.PHONY: all clean build-dev build-prod deploy test
