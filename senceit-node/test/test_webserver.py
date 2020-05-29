
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
        HTTP_METHOD.POST,
        "/config",
        lambda req: HttpResponse.ok(200, Http.MIME_TYPE["JSON"]),
    )

    assert len(http.handlers.items()) == 1

    req = HttpRequest(Route(HTTP_METHOD.POST, "/config"), {})
    assert http._match_route(req).method == HTTP_METHOD.POST
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
    fs = File(os.getcwd())
    path = "/www/img/silogo42x136.png"
    (m, s, p) = fs.get_file_stat(path)

    assert m == Http.MIME_TYPE["PNG"]
    assert s == 4127


def test_static_image():
    http = Http()
    http.set_www_root(os.path.join(os.getcwd(), "www"))
    # GET image
    req = HttpRequest(Route(HTTP_METHOD.GET, "/img/silogo42x136.png"), {})
    http.handle(req)

    resp = http.get_response()
    assert resp.status == 200
    assert resp.mime_type == Http.MIME_TYPE["PNG"]
    assert resp.headers["Content-Length"] == 4127
    assert resp.headers["Content-Type"] == Http.MIME_TYPE["PNG"]
    assert resp.headers["Server"] == Http.SERVER
    assert resp.has_stream() is True
    assert resp.body is not None

    with open(os.path.join(os.getcwd(), "test/image.png"), "wb") as dest:
        resp.body.pipe(dest)

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
    assert resp.headers["Content-Length"] == 4098
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
    assert resp.headers["Content-Length"] == 11720
    assert resp.headers["Server"] == Http.SERVER
    assert resp.body is not None
    assert str(resp).startswith("HTTP/1.1 200 OK\r\n")


def test_error_resp():
    resp = HttpResponse.err(404, "File does not exist")

    assert resp.has_stream() is False
    assert resp.body is not None
