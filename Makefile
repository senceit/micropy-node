ip = 10.0.0.125
password = linda

all: clean build

setup:
	echo "Install webrepl"
	echo "Download latest MicroPython firmware"

clean:
	rm -rf build/*

build: clean
	mkdir -p build/www/css
	mkdir -p build/www/js
	cp src/main.py build/main.py
	cp src/io.py build/io.py
	cp src/esp8266.py build/esp8266.py
	cp src/ultrasonic.py build/ultrasonic.py
	cp src/webserver.py build/webserver.py
	cp www/index.html build/www/index.html
	cp www/404.html build/www/404.html
	cp www/css/404.css build/www/css/404.css
	cp www/css/style.css build/www/css/style.css
	cp www/js/scripts.js build/www/js/scripts.js

deploy:
	echo "Deploy"
	python webrepl/webrepl_cli.py -p $(password) build/main.py $(ip):/main.py
	python webrepl/webrepl_cli.py -p $(password) build/ultrasonic.py $(ip):/ultrasonic.py
	python webrepl/webrepl_cli.py -p $(password) build/webserver.py $(ip):/webserver.py
	python webrepl/webrepl_cli.py -p $(password) build/www/index.html $(ip):/www/index.html
	# python webrepl/webrepl_cli.py -p $(password) build/www/404.html $(ip):/www/404.html
	python webrepl/webrepl_cli.py -p $(password) build/www/css/404.css $(ip):/www/css/404.css
	python webrepl/webrepl_cli.py -p $(password) build/www/css/style.css $(ip):/www/css/style.css
	python webrepl/webrepl_cli.py -p $(password) build/www/js/scripts.js $(ip):/www/js/scripts.js

test:
	pytest

.PHONY: all clean build deploy
