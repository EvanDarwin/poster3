Welcome to poster's documentation!
==================================

:Author: Chris AtLee <chris@atlee.ca>
:Date: |today|

poster provides a set of classes and functions to faciliate making HTTP POST
(or PUT) requests using the standard multipart/form-data encoding.

Example
-------

A short example may help::

    # test_client.py
    from poster.encode import multipart_encode
    from poster.streaminghttp import register_openers
    import urllib2

    # Register the streaming http handlers with urllib2
    register_openers()

    # Start the multipart/form-data encoding of the file "DSC0001.jpg"
    # "image1" is the name of the parameter, which is normally set
    # via the "name" parameter of the HTML <input> tag.
    
    # headers contains the necessary Content-Type and Content-Length
    # datagen is a generator object that yields the encoded parameters
    datagen, headers = multipart_encode({"image1": open("DSC0001.jpg", "rb")})

    # Create the Request object
    request = urllib2.Request("http://localhost:5000/upload_image", datagen, headers)
    # Actually do the request, and get the response
    print urllib2.urlopen(request).read()

And we can check that it's working with Paste and WebOb::

    # test_server.py
    import webob
    from paste import httpserver

    def app(environ, start_response):
        request = webob.Request(environ)
        start_response("200 OK", [("Content-Type", "text/plain")])

        for name,value in request.POST.items():
            yield "%s: %s\n" % (name, value)

    httpserver.serve(app, port=5000)

After starting up the server, you should be able to connect to it with
the client and get the following output::

    image1: FieldStorage('image1', 'DSC0001.jpg')

For more control over how individiual parameters are handled, you should use
the :class:`poster.encode.MultipartParam` class::

    image_param = MultipartParam.from_file("image1", "DSC0001.jpg")

    datagen, headers = multipart_encode([image_param])

You can also combine poster with other urllib2 handlers, e.g. for sending cookies::

    opener = poster.streaminghttp.register_openers()
    opener.add_handler(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))

    params = {'file': open("test.txt", "rb"), 'name': 'upload test'}
    datagen, headers = poster.encode.multipart_encode(params)
    request = urllib2.Request(upload_url, datagen, headers)
    result = urllib2.urlopen(request)


Roadmap
-------

0.1 (2008-07-02):
    - First release, used on internal projects

0.2 (2008-12-01):
    - Bug fixes from 0.1

0.3 (2009-01-02):
    - Bug fixes from 0.2:
       - Use quoted-string encoding for filename parameter
       - Terminate encoded document with MIME boundary (Thanks to Stephen Waterbury)

0.4 (2009-04-05):
    - Added __all__ attributes to modules
    - Bug fixes from 0.3:
        - Fix connections to HTTPS.  Thanks to Kenji Noguchi and Marat Khayrullin

0.5 (2009-10-07):
    - Fix MultipartParam to open files in binary mode
    - Update docs to open files in binary mode
    - Updated register_openers() to return the OpenerDirector object

0.6 (2010-05-10):
    - Update docs to clarify how to use multiple parameters with the same key
    - Fix for unicode filenames.  Thanks to Zed Shaw.
    - Added poster.version attribute.  Thanks to JP Calderone.
    - Handle StringIO file objects.  Thanks to Christophe Combelles.

0.7 (2010-10-23):
    - Added callback parameters to MutipartParam and multipart_encode so you
      can add progress indicators to your applications.  Thanks to Ludvig
      Ericson for the suggestion.
    - Fixed a bug where posting to a url that returned a 401 code would hang.
      Thanks to Patrick Guido and Andreas Loupasakis for the bug reports.
    - MultipartParam.from_params will now accept MultipartParam instances as
      the values of a dict object passed in.  The parameter name must match the
      key corresponding to the parameter in the dict.  Thanks to Matthew King
      for the suggestion.
    - poster now works under python2.7

0.9 (future):
    - Finalize API

1.0 (future):
    - Bug fixes from 0.9
    - No new features

Module reference
----------------

.. toctree::
   :maxdepth: 2

   poster

Download
--------
poster can be downloaded from http://atlee.ca/software/poster/dist/0.7.0


License
-------
poster is licensed under the MIT license:

Copyright (c) 2010 Chris AtLee

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

