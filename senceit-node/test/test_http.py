from util import StringBuilder

from uhttp import (
    Http,
    RequestStreamParser,
    Route,
    HttpRequest,
    HTTP_METHOD,
    HttpResponse,
    File,
)

import os
import json


def test_route():
    rt1 = Route(HTTP_METHOD.GET, "/root")
    rt2 = Route(HTTP_METHOD.GET, "/path")

    assert rt1 != rt2

    rt1 = Route(HTTP_METHOD.GET, "/root")
    rt2 = Route(HTTP_METHOD.PUT, "/root")

    assert rt1 != rt2

    rt1 = Route(HTTP_METHOD.POST, "/root")
    rt2 = Route(HTTP_METHOD.POST, "/root")

    assert rt1 == rt2


def test_http():
    http = Http()

    assert http.www_root == "/www"
    assert http.VERSION == "HTTP/1.1"

    http.set_www_root("/docs")
    assert http.www_root == "/docs"


def test_request_parser():
    parser = RequestStreamParser()
    parser.update("GET http://192.168.2.4/config?id=1 HTTP/1.1\r\n")
    req = parser.get_request()

    assert req.route.method == HTTP_METHOD.GET
    assert req.protocol == "http"
    assert req.domain == "192.168.2.4"
    assert req.route.path == "/config"
    assert req.body is None
    assert req.query["id"] == "1"


def test_full_request_parsing_1():
    parser = RequestStreamParser("\n")
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "request1.txt"), "r"
    ) as f:
        for line in f:
            resp = parser.update(line)

    assert resp is False
    req = parser.get_request()
    assert req.route.method == HTTP_METHOD.GET
    assert req.protocol == "https"
    assert req.domain == "www.google.com"
    assert req.header["Host"] == "www.google.com"
    assert req.header["Connection"] == "keep-alive"
    assert (
        req.header["User-Agent"]
        == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    )
    assert (
        req.header["Accept"]
        == "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    )
    assert req.header["Accept-Encoding"] == "gzip, deflate, br"


def test_full_request_parsing_2():
    parser = RequestStreamParser("\n")
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "request2.txt"), "r"
    ) as f:
        for line in f:
            resp = parser.update(line)

    assert resp is False
    req = parser.get_request()
    assert req.route.method == HTTP_METHOD.GET
    assert req.protocol == "https"
    assert req.domain == "git.homeppl.com"
    assert req.header["Host"] == "git.homeppl.com"
    assert req.header["Connection"] == "keep-alive"
    assert (
        req.header["User-Agent"]
        == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    )
    assert (
        req.header["Accept"]
        == "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    )
    assert req.header["Accept-Encoding"] == "gzip, deflate, br"


def test_full_request_parsing_3():
    parser = RequestStreamParser("\n")
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "request3.txt"), "r"
    ) as f:
        for line in f:
            print(line.rstrip())
            resp = parser.update(line)

    assert resp is False
    req = parser.get_request()
    assert req.route.method == HTTP_METHOD.POST
    assert req.route.path == "/test"
    assert req.protocol == None
    assert req.domain is None
    assert req.header["Host"] == "www.example.com"
    assert req.header["Connection"] == "keep-alive"
    assert req.header["User-Agent"] == "Dummy-Agent"
    assert req.header["Content-Type"] == "application/json"
    assert req.header["Content-Length"] == "18"
    assert req.header["Accept-Encoding"] == "gzip, deflate, br"

    assert req.body == json.loads('{ "key": "value" }')


def test_full_request_parsing_4():
    parser = RequestStreamParser("\n")
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "request4.txt"), "rb"
    ) as f:
        line = str(f.readline(), "utf-8")
        status = parser.update(line)
        while status:
            line = str(f.readline(), "utf-8")
            status = parser.update(line)

    req = parser.get_request()
    assert req.route.method == HTTP_METHOD.POST
    assert req.route.path == "/config"
    assert req.protocol == "http"
    assert req.domain == "192.168.4.1"
    assert req.header["Host"] == "192.168.4.1"
    assert req.header["Connection"] == "keep-alive"
    assert req.header["User-Agent"] == "PostmanRuntime/7.24.1"
    assert req.header["Content-Type"] == "application/json"
    assert req.header["Content-Length"] == "378"
    assert req.header["Accept-Encoding"] == "gzip, deflate, br"

    assert req.body == json.loads(
        '{"wifi":{"ssid":"Swart","password":"870622eta"},"mqtt":{"ip":"10.0.0.114"},"location":["25","-23"],"peripherals":{"0":{"type":"sensor","name":"LevelSensor","id":"USLS01","config":{"interval":"1m","trigger":null,"topic":"dam/level/1","parameters":{"dam_height":{"value":"1500","unit":"mm"},"sensor_height":{"value":"1700","unit":"mm"},"dam_diameter":{"value":"5","unit":"m"}}}}}}'
    )
