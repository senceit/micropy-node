from webserver import (
    Http,
    RequestStreamParser,
    Route,
    HttpRequest,
    StringBuilder,
    HTTP_METHOD,
    HttpResponse,
    FileServer,
)

import os
import json


def test_string_builder():
    sb = StringBuilder()
    string = sb.add("hello").space().add("world").newline().build()

    assert string == "hello world\r\n"

    sb = StringBuilder()
    string = sb.add("hello").space().add("world").newline().newline().build()

    assert string == "hello world\r\n\r\n"


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


def test_http_static_routes():
    http = Http()

    req = HttpRequest(Route(HTTP_METHOD.GET, "/"), [])
    assert http._match_static_route(req)

    req = HttpRequest(Route(HTTP_METHOD.GET, "/index.html"), [])
    assert http._match_static_route(req)

    req = HttpRequest(Route(HTTP_METHOD.GET, "/css/styles.css"), [])
    assert http._match_static_route(req)

    req = HttpRequest(Route(HTTP_METHOD.GET, "/js/scripts.js"), [])
    assert http._match_static_route(req)

    req = HttpRequest(Route(HTTP_METHOD.GET, "/favicon.ico"), [])
    assert http._match_static_route(req)

    req = HttpRequest(Route(HTTP_METHOD.GET, "/img/image.png"), [])
    assert http._match_static_route(req)

    req = HttpRequest(Route(HTTP_METHOD.POST, "/img/image.png"), [])
    assert not http._match_static_route(req)


def test_http_handlers():

    http = Http()
    http.register_handler(
        HTTP_METHOD.GET,
        "/config",
        lambda http, req: HttpResponse.ok(200, Http.MIME_TYPE["JSON"]),
    )

    assert len(http.handlers.items()) == 1

    req = HttpRequest(Route(HTTP_METHOD.GET, "/config"), {})
    assert http._match_route(req).method == HTTP_METHOD.GET
    assert http._match_route(req).path == "/config"

    http.handle(req)

    assert http.get_response().status == 200
    assert http.get_response().body == None
    assert "Content-Type" in http.get_response().headers
    assert (
        http.get_response().headers["Content-Type"] == "application/json; charset=UTF-8"
    )

    assert "Server" in http.get_response().headers
    assert http.get_response().headers["Server"] == Http.SERVER

    assert str(http.get_response()).startswith("HTTP/1.1 200 OK")


def test_fs():
    fs = FileServer(os.getcwd())
    path = "/www/img/SenceItLogo.png"
    (m, d, s) = fs.read(path)

    assert m == Http.MIME_TYPE["PNG"]
    assert s == 8849


def test_static_image():
    http = Http()
    http.set_www_root(os.path.join(os.getcwd(), "www"))
    # GET image
    req = HttpRequest(Route(HTTP_METHOD.GET, "/img/SenceItLogo.png"), {})
    http.handle(req)

    resp = http.get_response()
    assert resp.status == 200
    assert resp.mime_type == Http.MIME_TYPE["PNG"]
    assert resp.headers["Content-Length"] == 8849
    assert resp.headers["Content-Type"] == Http.MIME_TYPE["PNG"]
    assert resp.headers["Server"] == Http.SERVER
    assert resp.body is not None
    assert str(resp).startswith("HTTP/1.1 200 OK\r\n")


def test_static_html():
    http = Http()
    http.set_www_root(os.path.join(os.getcwd(), "www"))
    # GET HTML
    req = HttpRequest(Route(HTTP_METHOD.GET, "/"), {})
    http.handle(req)

    resp = http.get_response()
    assert resp.status == 200
    assert resp.mime_type == Http.MIME_TYPE["HTML"]
    assert resp.headers["Content-Type"] == Http.MIME_TYPE["HTML"]
    assert resp.headers["Content-Length"] == 5234
    assert resp.headers["Server"] == Http.SERVER
    assert resp.body is not None
    assert str(resp).startswith("HTTP/1.1 200 OK\r\n")


def test_static_js():
    http = Http()
    http.set_www_root(os.path.join(os.getcwd(), "www"))
    # GET HTML
    req = HttpRequest(Route(HTTP_METHOD.GET, "/js/scripts.js"), {})
    http.handle(req)

    resp = http.get_response()
    assert resp.status == 200
    assert resp.mime_type == Http.MIME_TYPE["JS"]
    assert resp.headers["Content-Type"] == Http.MIME_TYPE["JS"]
    assert resp.headers["Content-Length"] == 6880
    assert resp.headers["Server"] == Http.SERVER
    assert resp.body is not None
    assert str(resp).startswith("HTTP/1.1 200 OK\r\n")


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
    parser = RequestStreamParser()
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "request1.txt"), "r"
    ) as f:
        for line in f:
            parser.update(line)

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
    parser = RequestStreamParser()
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "request2.txt"), "r"
    ) as f:
        for line in f:
            parser.update(line)

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
    parser = RequestStreamParser()
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "request3.txt"), "r"
    ) as f:
        for line in f:
            print(line.rstrip())
            resp = parser.update(line)

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

    assert json.loads(req.body) == json.loads('{ "key": "value" }')
    assert len(req.body) == 18
