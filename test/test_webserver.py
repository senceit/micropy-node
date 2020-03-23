from webserver import (
    Http,
    RequestStreamParser,
    Route,
    HttpRequest,
    StringBuilder,
    HTTP_METHOD,
    HttpResponse
)


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
    http.register_handler(HTTP_METHOD.GET, "/config", lambda http, req : HttpResponse(200, {}))

    assert len(http.handlers.items()) == 1

    req = HttpRequest(Route(HTTP_METHOD.GET, "/config"), {})
    assert http._match_route(req).method == HTTP_METHOD.GET
    assert http._match_route(req).path == "/config"

    http.handle(req)

    assert http.get_response().status == 200
    assert http.get_response().body == None
    assert "Content-type" in http.get_response().headers
    assert http.get_response().headers["Content-type"] == "application/json;charset=UTF-8"

    assert "Server" in http.get_response().headers
    assert http.get_response().headers["Server"] == Http.SERVER

    assert str(http.get_response()).startswith("HTTP/1.1 200 OK")
