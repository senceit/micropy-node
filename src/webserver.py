##
#
# A simple HTTP server
#
# Copyright 2020 - Intersect Technologies CC
# Author: Niel Swart <niel@nielswart.com>
#
##

import socket
import select
import gc

from uhttp import Http, RequestStreamParser, HttpRequest, HttpError, HttpResponse
from util import Logger

log = Logger.getLogger()


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

        self.connection = None
        self.http_handler = http_handler

    # Function to start http server
    def start(self, port):
        self.intro()
        self.server.bind(("0.0.0.0", port))
        self.server.listen(3)
        # Register for checking new client connection
        self.poller.register(self.server, select.POLLIN)

    def close(self):
        self.poller.unregister(self.server)
        self.server.close()

    # Check for new client connection and process the request
    def handle_client(self):
        # Note: don't call poll() with 0, that would randomly cause
        # reset with "Fatal exception 28(LoadProhibitedCause)" message
        if self.poller.poll(1):
            # There's a new client connection
            (conn, sockaddr) = self.server.accept()
            try:
                self.connection = conn
                request = self.get_request()
                self.http_handler.handle(request)
                resp = self.http_handler.get_response()
                if resp.has_stream():
                    self.connection.write(str(resp))
                    resp.body.pipe(self.connection)
                else:
                    self.connection.write(str(resp))
            except OSError as oserr:
                log.severe(str(oserr))
            except MemoryError as memerr:
                gc.collect()
                log.severe(str(memerr))
            except HttpError as err:
                log.severe(err.message)
                self.connection.write(str(HttpResponse.err(err.code, err.message)))
            finally:
                self.connection.close()

    def get_request(self) -> HttpRequest:
        parser = RequestStreamParser()
        line = self.read()
        status = parser.update(line)

        while status:
            line = self.read()
            status = parser.update(line)

        return parser.get_request()

    def read(self):
        return str(self.connection.readline(), "utf-8")

    def intro(self):
        print("   ____                 ______ ")
        print("  / __/__ ___  _______ /  _/ /_")
        print(" _\ \/ -_) _ \/ __/ -_)/ // __/")
        print("/___/\__/_//_/\__/\__/___/\__/ ")
        print("")
        print("-------------------------------")
        print("Starting web server on port 80")
