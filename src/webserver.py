##
#
# A simple HTTP server that only accepts GET requests (for now)
#
# Copyright 2020 - Niel Swart
#
# based on work from https://github.com/codemee/ESP8266WebServer
##
from typing import Union
from enum import Enum

import socket
import select
import os
import json


class HTTP_METHOD(Enum):
    GET = 1
    PUT = 2
    POST = 3
    DELETE = 4


class StringBuilder:
    def __init__(self):
        self.string = []

    def add(self, text):
        if text is None or text == "":
            return self
        self.string.append(str(text))
        return self

    def space(self):
        self.string.append(" ")
        return self

    def newline(self):
        self.string.append("\r\n")
        return self

    def semicolon(self):
        self.string.append("; ")
        return self

    def build(self):
        return "".join(self.string)


class Route:
    def __init__(self, method: HTTP_METHOD, path: str):
        self.path = path
        self.method = method

    def __eq__(self, other):
        if not isinstance(other, Route):
            return False
        return self.method == other.method and self.path == other.path

    def __hash__(self):
        return hash((self.method, self.path))


class HttpRequest:
    def __init__(
        self, route: Route, headers, query=None, body=None, protocol="http", domain=None
    ):
        self.route = route
        self.header = headers
        self.query = query if query else {}
        self.body = body
        self.protocol = protocol
        self.domain = domain


class HttpResponse:
    """
    *Immutable* data class
    """

    def __init__(self, status, mime, headers: dict, body=None):
        self.headers = headers
        self.body = body
        self.status = status
        self.mime_type = mime
        self._response = StringBuilder()

        self._add_protocol_header()
        self._add_headers()
        self._add_body()

    def __str__(self):
        return self._response.build()

    def _add_protocol_header(self):
        self._response.add(Http.VERSION).space().add(
            Http.STATUS_CODE[self.status]
        ).newline()

    def _add_headers(self):
        if not self.headers:
            self.headers = {}
        if "Server" not in self.headers:
            self.headers["Server"] = Http.SERVER
        if "Content-Type" not in self.headers:
            self.headers["Content-Type"] = self.mime_type

        for k, v in self.headers.items():
            self._response.add(k).add(":").space().add(v).newline()

    def _add_body(self):
        """
        Mapping
        ----
        dict - json
        """

        if type(self.body) != dict:
            self._response.add(self.body).newline()
        else:
            self._response.add(json.dumps(self.body)).newline()

    @staticmethod
    def err(self, code, message=None):
        """
        Response error message to client
        """
        return HttpResponse(code, Http.MIME_TYPE["JSON"], {}, {"error": message})

    # Response succesful message to client
    @staticmethod
    def ok(
        code, mime_type, headers=None, body=None,
    ):
        return HttpResponse(code, mime_type, headers, body)


class RequestStreamParser:

    SUPPORTED_HEADERS = [
        "Accept",
        "Accept-Encoding",
        "Host",
        "Connection",
        "User-Agent",
        "Content-Length",
        "Content-Type",
    ]

    def __init__(self):
        self._line = None
        self._lines = 0
        self._path = None
        self._method = HTTP_METHOD.GET
        self._protocol = None
        self._domain = None
        self._queries = {}
        self._header = {}
        self._version = None
        self._break = False
        self._content_length = None
        self._body = None

    def update(self, line) -> bool:
        if line == "\n":
            self._break = True

        raw = line.rstrip()
        self._lines += 1
        self._line = raw

        if self._lines == 1:
            # first line
            self.validate()
            req = raw.split(" ", 2)
            self._parse_method(req[0])
            _path = req[1]
            self._version = req[2]
            self.validate()

            if "http" in _path:
                (self._protocol, _path) = _path.split("://", 1)
            if not _path.startswith("/"):
                (self._domain, _path) = _path.split("/", 1)
                _path = "/" + _path
            if "?" in _path:  # Check if there's query string?
                (path, query) = _path.split("?", 1)
                self._queries = self._parse_query(query)
            else:
                (path, query) = (_path, "")

            self._path = path
            return True

        print(self._break)
        if self._lines > 1 and not self._break:
            self._parse_header(raw)
            return True

        if self._break and self._content_length and self._lines > 1:
            return self._parse_body(raw)

        return False

    def _parse_body(self, line):
        """
        Parses the body line by line until the Content-Length
        It accept only application/json as mime type for the body of requests

        returns True when accepting more and False when the full body has been received
        """
        if not self._body:
            self._body = ""
        self._body += line

        return len(self._body) != self._content_length

    def _parse_header(self, line: str) -> dict:
        """
        Parses the following Request headers

        - Accept
        - Accept-Encoding
        - Host
        - Connection
        - User-Agent
        - Content-Length
        - Content-Type

        Ignores all others
        """
        for h in filter(lambda h: line.startswith(h + ":"), self.SUPPORTED_HEADERS):
            (_, value) = line.split(": ", 2)
            self._header[h] = value.strip()
            if h == "Content-Length":
                self._content_length = int(self._header[h])

    def _parse_method(self, method) -> HTTP_METHOD:
        if method == "GET":
            self._method = HTTP_METHOD.GET
        elif method == "PUT":
            self._method = HTTP_METHOD.PUT
        elif method == "POST":
            self._method = HTTP_METHOD.POST
        elif method == "DELETE":
            self._method = HTTP_METHOD.DELETE
        else:
            raise HttpError("Unsupported HTTP Method", 405)

    def _parse_query(self, query):
        args = {}
        if query:
            # Parsing the query string
            argPairs = query.split("&")
            for argPair in argPairs:
                arg = argPair.split("=")
                args[arg[0]] = arg[1]

        return args

    def validate(self):
        if self._lines == 1:
            req = self._line.split(" ")
            if len(req) != 3:  # Discarded if it's a bad header
                raise HttpError("Bad Request", 400)
            # Check for supported HTTP version
            if (
                self._version
                and self._version != "HTTP/1.0"
                and self._version != "HTTP/1.1"
            ):
                raise HttpError("Version Not Supported", 505)

    def get_request(self) -> HttpRequest:
        route = Route(self._method, self._path)
        return HttpRequest(
            route,
            self._header,
            self._queries,
            self._body,
            self._protocol,
            self._domain,
        )


class HttpError(Exception):
    def __init__(self, msg, code):
        super().__init__()
        self.message = msg
        self.code = code

    def __str__(self):
        return Http.STATUS_CODE[self.code]


class Http:
    """
    Http class handles HTTP
    """

    SERVER = "SenceIt muWebServer/1.0"
    VERSION = "HTTP/1.1"
    CHARSET = "charset=UTF-8"

    MIME_TYPE = {
        "HTML": "text/html; " + CHARSET,
        "TEXT": "text/plain; " + CHARSET,
        "CSS": "text/css; " + CHARSET,
        "JS": "text/javascript; " + CHARSET,
        "JSON": "application/json; " + CHARSET,
        "PNG": "image/png",
        "SVG": "image/svg+xml",
        "JPG": "image/jpeg",
        "BINARY": "application/octet-stream",
    }

    STATUS_CODE = {
        200: "200 OK",
        201: "201 Created",
        301: "301 Moved Permanently",
        302: "302 Moved Remporarily",
        400: "400 Bad Request",
        401: "401 Unauthorized",
        403: "403 Forbidden",
        404: "404 Not Found",
        405: "405 Method not Allowed",
        500: "500 Internal Server Error",
        501: "501 Not Implemented",
        505: "505 HTTP Version Not Supported",
    }

    def __init__(self):
        self.response = None

        # The path to the web documents on MicroPython filesystem
        self.www_root = "/www"

        # Dict for registed handlers of all paths
        self.handlers = {}

    def set_www_root(self, path):
        """
        Set the path to documents' directory
        """
        self.www_root = path

    def handle(self, request: HttpRequest):
        # Handle all registered paths first, if none found, try serve static content
        match = self._match_route(request)
        if type(match) is bool and not match:
            if request.route.method == HTTP_METHOD.GET and self._match_static_route(
                request
            ):
                self.response = self._static(request)

            else:
                self.response = HttpResponse.err(400)
        else:
            try:
                self.response = self.handlers[match](self, request)
            except Exception as ex:
                self.response = HttpResponse.err(500, str(ex))

    def register_handler(self, method: HTTP_METHOD, path, handler):
        """
        Register handler for processing request for specified path
        """
        route = Route(method, path)
        self.handlers[route] = handler

    def get_response(self) -> HttpResponse:
        return self.response

    def _static(self, request: HttpRequest):
        # Check for path to any document
        fs = FileServer(self.www_root)
        try:
            if request.route.path == "/":
                request.route.path = "/index.html"
            file = request.route.path
            mime_type, data, size = fs.read(file)

            # Respond with the file content
            return HttpResponse.ok(
                200, mime_type, body=data, headers={"Content-Length": size},
            )
        except Exception as ex:
            # Can't find the file specified in path
            return HttpResponse.err(404, str(ex))

    def _match_route(self, request: HttpRequest) -> Union[Route, bool]:
        """
        Returns the first matched route or False if no route is matched
        """
        matched = [route for route in self.handlers.keys() if route == request.route]

        if len(matched) > 0:
            return matched[0]
        else:
            return False

    def _match_static_route(self, request: HttpRequest):
        return request.route.method == HTTP_METHOD.GET and (
            request.route.path == "/"
            or request.route.path == "/index.html"
            or request.route.path.startswith("/css")
            or request.route.path.startswith("/js")
            or request.route.path.startswith("/favicon")
            or request.route.path.startswith("/img")
        )


class FileServer:
    """
    """

    def __init__(self, root):
        """
        """
        self.root = root

    def resolve_type(self, path: str) -> str:
        if path.lower().endswith("css"):
            return Http.MIME_TYPE["CSS"]

        if path.lower().endswith("html"):
            return Http.MIME_TYPE["HTML"]

        if path.lower().endswith("png"):
            return Http.MIME_TYPE["PNG"]

        if path.lower().endswith("jpg"):
            return Http.MIME_TYPE["JPG"]

        if path.lower().endswith("svg"):
            return Http.MIME_TYPE["SVG"]

        if path.lower().endswith("js"):
            return Http.MIME_TYPE["JS"]

        if path.lower().endswith("json"):
            return Http.MIME_TYPE["JSON"]

        if path.lower().endswith(("txt")):
            return Http.MIME_TYPE["TEXT"]
        else:
            return Http.MIME_TYPE["BINARY"]

    def read(self, path):
        """
        """

        # Check if file exists
        p = self.root + path
        fstat = os.stat(p)
        mime_type = self.resolve_type(path)

        with open(p, "rb") as reader:
            data = reader.read()

        return (mime_type, data, fstat.st_size)


class Webserver:
    """
    Very basic webserver that supports the following HTTP methods:
    GET, POST, PUT, DELETE

    Custom route handlers can be registered, but they only support application/json response types
    The body of all requests also only supports application/json

    If no route is matched it will look for static files with the same route in the www_root directory of the file system

    It does not support Transfer-Encoding: Chunked and many other HTTP features
    It requires a Content-Length header to be present
    If no Content-Length is given, the server responds with 400 Bad request
    """

    def __init__(self, http_handler: Http):

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Use for checking a new client connection
        self.poller = select.poll()

        self.socket = None
        self.http_handler = http_handler

    # Function to start http server
    def start(self, port):
        self.server.bind(("0.0.0.0", port))
        self.server.listen(1)
        # Register for checking new client connection
        self.poller.register(self.server, select.POLLIN)

    def close(self):
        self.poller.unregister(self.server)
        self.server.close()

    # Check for new client connection and process the request
    def handle_client(self):
        # Note: don't call poll() with 0, that would randomly cause
        # reset with "Fatal exception 28(LoadProhibitedCause)" message
        res = self.poller.poll(1)
        if res:
            # There's a new client connection
            (socket, sockaddr) = self.server.accept()
            try:
                self.socket = socket
                request = self.get_request()
                self.http_handler.handle(request)
                self.socket.write(self.http_handler.get_response())
                self.socket.close()
                self.socket = None
            except OSError as oserr:
                print(str(oserr))

    def get_request(self, request) -> HttpRequest:
        parser = RequestStreamParser()
        status = parser.update(str(self.socket.readline(), "utf-8"))

        while status:
            status = parser.update(str(self.socket.readline(), "utf-8"))

        return parser.get_request()
