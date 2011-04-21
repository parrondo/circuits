# Module:   server
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Web Servers

This module implements the several Web Server components.
"""

import time
import sys

from socket import gethostname as _gethostname

from circuits.core import handler, BaseComponent

from circuits import io

from circuits.net.sockets import TCPServer, UNIXServer
from circuits.net.sockets import TCPClient, Read, Write

from .http import HTTP
from .events import WebEvent
from .wrappers import Request, Host
from .constants import SERVER_VERSION
from .dispatchers import Dispatcher

class BaseServer(BaseComponent):
    """Create a Base Web Server

    Create a Base Web Server (HTTP) bound to the IP Address / Port or
    UNIX Socket specified by the 'bind' parameter.

    :ivar server: Reference to underlying Server Component

    :param bind: IP Address / Port or UNIX Socket to bind to.
    :type bind: Instance of int, list, tuple or str

    The 'bind' parameter is quite flexible with what valid values it accepts.

    If an int is passed, a TCPServer will be created. The Server will be
    bound to the Port given by the 'bind' argument and the bound interface
    will default (normally to  "0.0.0.0").

    If a list or tuple is passed, a TCPServer will be created. The
    Server will be bound to the Port given by the 2nd item in the 'bind'
    argument and the bound interface will be the 1st item.

    If a str is passed and it contains the ':' character, this is
    assumed to be a request to bind to an IP Address / Port. A TCpServer
    will thus be created and the IP Address and Port will be determined
    by splitting the string given by the 'bind' argument.

    Otherwise if a str is passed and it does not contain the ':'
    character, a file path is assumed and a UNIXServer is created and
    bound to the file given by the 'bind' argument.
    """

    channel = "web"

    def __init__(self, bind, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        kwargs.setdefault("channel", self.channel)
        super(BaseServer, self).__init__(**kwargs)

        WebEvent._target = kwargs["channel"]

        if type(bind) in set(int, list, tuple):
            SocketType = TCPServer
        else:
            if ":" in bind:
                SocketType = TCPServer
            else:
                SocketType = UNIXServer

        self.server = SocketType(bind, **kwargs).register(self)
        HTTP(encoding=self.server._encoding,
                channel=self.server.channel).register(self)

        Request.server = self
        if isinstance(self.server._bind, tuple):
            Request.local = Host(self.server._bind[0],
                    self.server._bind[1])
        else:
            Request.local = Host(self.server._bind, None)
        Request.host = self.host
        Request.scheme = "https" if self.server.secure else "http"

    @property
    def version(self):
        return SERVER_VERSION

    @property
    def host(self):
        if hasattr(self, "server"):
            return self.server.host

    @property
    def port(self):
        if hasattr(self, "server"):
            return self.server.port

    @property
    def secure(self):
        if hasattr(self, "server"):
            return self.server.secure

    @property
    def scheme(self):
        return "https" if self.secure else "http"

    @property
    def base(self):
        host = self.host or "0.0.0.0"
        port = self.port or 80
        scheme = self.scheme
        secure = self.secure

        tpl = "%s://%s%s"

        if (port == 80 and not secure) or (port == 443 and secure):
            port = ""
        else:
            port = ":%d" % port

        return tpl % (scheme, host, port)

class Server(BaseServer):
    """Create a Web Server

    Create a Web Server (HTTP) complete with the default Dispatcher to
    parse requests and posted form data dispatching to appropriate
    Controller(s).

    See: circuits.web.servers.BaseServer
    """

    def __init__(self, bind, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Server, self).__init__(bind, **kwargs)

        Dispatcher(channel=self.channel).register(self)

class FakeSock():
    def getpeername(self):
        return (None, None)

class StdinServer(BaseComponent):
    channel = "web"

    def __init__(self, **kwargs):
        kwargs.setdefault("channel", self.channel)
        super(StdinServer, self).__init__(**kwargs)
        WebEvent._target = kwargs["channel"]

        self.server = io.stdin + io.stdout + HTTP(**kwargs)
        self += self.server

        Request.server = self
        Dispatcher(channel=self.channel).register(self)

    @handler("read", target="stdin")
    def read(self, data):
        self.push(Read(FakeSock(), data), "read", self.channel)

    @handler("write")
    def write(self, sock, data):
        self.push(Write(data), "write", "stdout")

