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
        self.string.append(text)
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
    def __init__(self, method: HTTP_METHOD, route: str):
        self.path = route
        self.method = method

    def __eq__(self, other):
        if not isinstance(other, Route):
            return False
        return self.method == other.method and self.path == other.path

    def __hash__(self):
        return hash((self.method, self.path))


class HttpRequest:
    def __init__(self, route, headers, query=None, body=None):
        self.route = route
        self.headers = headers
        self.query = query if query else {}
        self.body = body if body else {}

class HttpResponse:
    '''
    *Immutable* data object
    '''

    def __init__(self, status, headers: dict, body=None):
        self.headers = headers
        self.body = body
        self.status = status
        self._response = StringBuilder()

        self._add_protocol_header()
        self._add_headers()
        self._add_body()

    def __str__(self):
        return self._response.build()

    def _add_protocol_header(self):
        self._response.add(Http.VERSION).space().add(Http.STATUS_CODE[self.status]).newline()

    def _add_headers(self):
        if ("Server" not in self.headers):
            self.headers["Server"] = Http.SERVER

        for k, v in self.headers.items():
            self._response.add(k).add(":").space().add(v).newline()

    def _add_body(self):
        """
        Mapping
        ----
        dict - json
        """

        if ("Content-type" not in self.headers):
            self.headers["Content-type"] = Http.MIME_TYPE["JSON"] + ";" + Http.CHARSET

        self._response.add(json.dumps(self.body)).newline()

    @staticmethod
    def err(self, code, message=None):
        """
        Response error message to client
        """
        response = HttpResponse(code, [], { "error": message })
        return response

    # Response succesful message to client
    @staticmethod
    def ok(code, msg: dict):
        resp = HttpResponse()
        resp._add_protocol_header(code)._add_body(msg)
        return resp

class RequestStreamParser:
    def __init__(self):
        self._first_line = None
        self.request = None

    def update(self, line):
        request = line.split(" ")
        if "?" in route:  # Check if there's query string?
            (path, query) = route.split("?", 2)
        else:
            (path, query) = (route, "")
        args = {}
        if query:  # Parsing the querying string
            argPairs = query.split("&")
            for argPair in argPairs:
                arg = argPair.split("=")
                args[arg[0]] = arg[1]
        while True:
            # Read until blank line after header
            # TODO: should also read body of request
            header = self.socket.readline()
            if header == b"":
                return
            if header == b"\r\n":
                break

    def validate(self, request) -> Union[int, bool]:
        if self._first_line:
            request = raw.split(" ")
            if len(request) != 3:  # Discarded if it's a bad header
                return False

        # Check for supported HTTP version
        if self.request.version != "HTTP/1.0" and self.request.version != "HTTP/1.1":
            return 505


class Http:
    """
    Http class handles HTTP
    """
    SERVER = "SenceIt MicroWebServer/1.0"
    VERSION = "HTTP/1.1"
    CHARSET = "charset=UTF-8"

    MIME_TYPE = {
        "HTML": "text/html",
        "TEXT": "text/plain",
        "CSS": "text/css",
        "JS": "text/javascript",
        "JSON": "application/json",
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
                self._static(request)

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
        try:
            if (request.route.path == "/"):
                request.route.path = "/index.html"
            file = self.www_root + request.route.route
            print(file)

            # Check for file existence
            os.stat(self.www_root)

            # Response header first
            self._add_protocol_header(200)

            # Respond with the file content
            with open(file, "rb") as f:
                while True:
                    data = f.read(64)
                    if data == b"":
                        break
                    self.response.append(data)
            return
        except Exception as ex:
            print(str(ex))
            # Can't find the file specified in path
            self._err(404)

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


class Webserver:
    """
    Very basic webserver that supports the following HTTP methods:
    GET, POST, PUT, DELETE

    Custom route handlers can be registered, but they only support json response types
    The body of all requests also only support json

    If no route is matched it will look for static files with the same route in the www_root directory of the file system

    It does not support Transfer-Encoding: Chunked and many other HTTP features
    It requires a Content-Length header to be present
    If no Content-Length is given, the server responds with 400 Bad request
    """

    def __init__(self, http_handler):

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
        first_line = parser.update(str(self.socket.readline(), "utf-8"))
        if not HttpRequest.validate_line_1(first_line):
            return self.err(400)

        request = []
        request.append(first_line)

        while True:
            ## read until we get the Content-Length header and then continue until the end specified by length
            line = self.socket.readline()
            request.append(line)

        return HttpRequest.parse(request)
