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
    datagen, headers = multipart_encode({"image1": open("DSC0001.jpg")})

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
poster can be downloaded from http://atlee.ca/software/poster/dist/0.3

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

