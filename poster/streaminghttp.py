"""Streaming HTTP uploads module.

This module extends the standard httplib and urllib2 objects so that
iterable objects can be used in the body of HTTP requests.

In most cases all one should have to do is call :func:`register_openers()`
to register the new streaming http handlers which will take priority over
the default handlers, and then you can use iterable objects in the body
of HTTP requests.

**N.B.** You must specify a Content-Length header if using an iterable object
since there is no way to determine in advance the total size that will be
yielded, and there is no way to reset an interator.

Example usage:

>>> from StringIO import StringIO
>>> import urllib2, poster.streaminghttp

>>> poster.streaminghttp.register_openers()

>>> s = "Test file data"
>>> f = StringIO(s)

>>> req = urllib2.Request("http://localhost:5000", f, {'Content-Length': s})
"""

import httplib, urllib2, socket
from httplib import NotConnected

class StreamingHTTPConnection(httplib.HTTPConnection):
    """Subclass of `httplib.HTTPConnection` that overrides the `send()` method
    to support iterable body objects"""

    def send(self, value):
        """Send ``value`` to the server.
        
        ``value`` can be a string object, a file-like object that supports
        a .read() method, or an iterable object that supports a .next()
        method.
        """
        # Based on python 2.6's httplib.HTTPConnection.send()
        if self.sock is None:
            if self.auto_open:
                self.connect()
            else:
                raise NotConnected()

        # send the data to the server. if we get a broken pipe, then close
        # the socket. we want to reconnect when somebody tries to send again.
        #
        # NOTE: we DO propagate the error, though, because we cannot simply
        #       ignore the error... the caller will know if they can retry.
        if self.debuglevel > 0:
            print "send:", repr(value)
        try:
            blocksize=8192
            if hasattr(value,'read') :
                if self.debuglevel > 0: print "sendIng a read()able"
                data=value.read(blocksize)
                while data:
                    self.sock.sendall(data)
                    data=value.read(blocksize)
            elif hasattr(value,'next'):
                if self.debuglevel > 0: print "sendIng an iterable"
                for data in value:
                    self.sock.sendall(data)
            else:
                self.sock.sendall(value)
        except socket.error, v:
            if v[0] == 32:      # Broken pipe
                self.close()
            raise

class StreamingHTTPSConnection(httplib.HTTPSConnection):
    """Subclass of `httplib.HTTSConnection` that overrides the `send()` method
    to support iterable body objects"""

    send = StreamingHTTPConnection.send

class StreamingHTTPHandler(urllib2.AbstractHTTPHandler):
    """Subclass of `urllib2.AbstractHTTPHandler` that uses
    StreamingHTTPConnection as its http connection class."""

    handler_order = urllib2.AbstractHTTPHandler.handler_order - 1

    def http_open(self, req):
        return self.do_open(StreamingHTTPConnection, req)

    def http_request(self, req):
        # Make sure that if we're using an iterable object as the request
        # body, that we've also specified Content-Length
        if req.has_data():
            data = req.get_data()
            if not hasattr(data, 'read') and hasattr(data, 'next'):
                if not req.has_header('Content-length'):
                    raise ValueError(
                            "No Content-Length specified for iterable body")
        return urllib2.AbstractHTTPHandler.do_request_(self, req)

if hasattr(httplib, 'HTTPS'):
    class StreamingHTTPSHandler(urllib2.AbstractHTTPHandler):
        """Subclass of `urllib2.AbstractHTTPHandler` that uses
        StreamingHTTPSConnection as its http connection class."""

        handler_order = urllib2.AbstractHTTPHandler.handler_order - 1

        def https_open(self, req):
            return self.do_open(StreamingHTTPSConnection, req)

        https_request = StreamingHTTPHandler.http_request

def register_openers():
    """Register the streaming http handlers in the global urllib2 default
    opener object."""
    handlers = [StreamingHTTPHandler]
    if hasattr(httplib, "HTTPS"):
        handlers.append(StreamingHTTPSHandler)

    urllib2.install_opener(urllib2.build_opener(*handlers))
