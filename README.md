# poster3
##### A fork from Chris AtLee's poster package, available [on Bitbucket](https://bitbucket.org/chrisatlee/poster).  

**poster provides a set of classes and functions to faciliate making HTTP POST (or PUT) requests using the standard multipart/form-data encoding.**

### Version 0.9 Notice

The `poster3` package publishes the same APIs as used in the `poster` package, however the internal workings have changed completely. Until version 0.9, we will provide compatibility APIs that facade the new backend API.

---

## Examples

### Using the 0.9+ API

In the **0.9** release, many of the scattered functions in `poster` are now managed by objects, many of which are handled for you.

```python
from poster.multipart import Multipart
import requests  # For demonstration

# Create a new multipart form
form = Multipart()

# Add an image object
form.add_file('image', open('upload.jpg', 'rb'))

# Add a simple object
form.add_data('foo', 'bar')

content, headers = form.encode()
res = requests.post('http://site.com/form', data=content, headers=headers)
```

The **`headers`** result is a dictionary containing the key and value pairs of headers that should be passed and applied to your request.

Here's what the resulting headers look like:
```json
{
    "Content-Type": "multipart/form-data; boundary=--efaa3fef19fd4826b3e7c6fc37967291",
    "Content-Length": "318"
}
```

And for a look at what the ``content`` (the encoded output) looks like,

```
--efaa3fef19fd4826b3e7c6fc37967291
Content-Disposition: form-data; name="foo"
Content-Type: text/plain

bar
--efaa3fef19fd4826b3e7c6fc37967291
Content-Disposition: form-data; name="image"; filename="upload.jpg"
Content-Type: image/jpg

[... image data here ...]
--efaa3fef19fd4826b3e7c6fc37967291--
```
### Using the Old API

This section is for reference to the backwords-compatible API we provide. ***This API will be removed in version 1.0***, so you should convert to the new syntax immediately.


Here's an example client using the old poster API:

**test_client.py**:
```python
# THESE FUNCTIONS ARE DEPRECATED AND
#         _WILL_ BE REMOVED
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

# The register_openers() function does absolutely nothing.
# So we won't even call it.

# Start encoding the file "DSC0001.jpg", naming it "image1" in
# the request.
content, headers = multipart_encode({
    "image1": open("DSC0001.jpg", "rb")
})

# Create the Request object
request = urllib2.Request("http://localhost:5000/upload", content, headers)

# Actually do the request, and get the response
print urllib2.urlopen(request).read()
```

**test_server.py**:

```python
from paste import httpserver
import webob

def app(environ, start_response):
    request = webob.Request(environ)
    start_response("200 OK", [("Content-Type", "text/plain")])

    for name,value in request.POST.items():
        yield "%s: %s\n" % (name, value)

httpserver.serve(app, port=5000)
```

After starting up the server, you should be able to connect to it with the client and get the following output:

```
image1: FieldStorage('image1', 'DSC0001.jpg')
```

## Parameters

One of the core classes in the `poster` API is the concept of a parameter, a key value pair that has a value, whether it be a `File`-like object or a `str`.

For every element you want to send in your multipart HTTP form, you will need to add a new parameter. However, in most cases when you use `poster`, you won't need to create these `Parameter` objects on your own.

Here's a quick guide:
```python
from poster.multipart imort Multipart, Parameter

# The boundary is a random string used to separate data
boundary = 'mycustomboundary'

# If you want to track progress, you can pass a
# callback function.
def cb(parameter, current, total):
    print('CB: {}/{} bytes!'.format(current, total))

form = Multipart()

# Create it automatically (provides the same parameters)
form.add_file('photo', open('profile.jpg', 'rb'),
             filename='new_profile.jpg',
             mime_type='image/jpg',  # If you want to override it
             cb=cb)                  # Add a progress callback
                 
# Add the 'description' parameter to the form
form.add_parameter(param)
```

## Multipart Form

The `Multipart` class collects attributes and encodes the data into a HTTP multipart format.

```python
from poster.multipart import Multipart, Parameter

form = Multipart()
form.add_file('profile', open('profile.jpg', 'rb'))
form.add_data('foo', 'bar')
form.add_parameter(Parameter('hello', 'world'))

# Encode it into a multipart string
content, headers = form.encode()

# Use the requests lib for example purposes, works with urllib and
# http/httplib too.
import requests
resp = requests.post('http://localhost/upload', content=content,
                                                headers=headers)
```

## Changelog

### 0.9.0 (June 14, 2016)
- Added support for ***both Python 2.7+ and 3.2+***.
- Cleaned out a lot of code, removed old imports and weird conditions.
- Refactored a lot of `MultipartParam` into the `poster.multipart.Parameter` class *(the APIs have changed)*
- The following functions and attributes will be **deprecated and *removed*** in *version 1.0.0*:
    - Using the `poster.encode.MultipartParam` class
    - `poster.streaminghttp.register_openers()`
    - `poster.encode.multipart_encode()`
    - Accessing the `poster.version` tuple
- Encoding is now handled by the `Multipart` object, allowing you to add attributes easily
- Added more thorough tests for both Python 2/3
- Travis CI now builds on all Python versions
- Removed streaming HTTP helpers, if needed, can be reimplemented.

For more information about migrating to the new API in 0.9.0, read the [migration guide](https://github.com/EvanDarwin/poster3/wiki/Migration-from-0.8.1-to-0.9-)

### 0.8.1 (April 16, 2011)
- Factor out handler creation into get_handlers() method. Thanks to Flavio Percoco Premoli

### 0.8.0 (Febuary 13, 2011)

- Fixed parameter name encoding so that it follows RFC 2388,2047. Thanks to Emilien Klein for pointing this out.
- Don’t include Content-Length header for each part of the multipart message. Fixes issues with some ruby web servers. Thanks to Anders Pearson.

### 0.7.0 (October 23, 2010)

- Added callback parameters to `MultipartParam` and `multipart_encode` so you can add progress indicators to your applications. Thanks to Ludvig Ericson for the suggestion.
- Fixed a bug where posting to a url that returned a 401 code would hang. Thanks to Patrick Guido and Andreas Loupasakis for the bug reports.
- `MultipartParam.from_params` will now accept `MultipartParam` instances as the values of a dict object passed in. The parameter name must match the key corresponding to the parameter in the dict. Thanks to Matthew King for the suggestion.
- *poster* now works on Python 2.7

### 0.6 (May 10, 2010)

- Update docs to clarify how to use multiple parameters with the same key
- Fix for unicode filenames. Thanks to Zed Shaw.
- Added poster.version attribute. Thanks to Chritophe Combelles.

### 0.5 (October 7, 2009)

- Fix `MultipartParam` to open files in binary mode
- Update docs to open files in binary mode
- Updated `register_openers()` to return the `OpenerDirector` object

### 0.4 (April 5, 2009)

- Added `__all__` attributes to modules
- Bug fixes from 0.3:
    - Fix connections to HTTPS. Thanks to Kenji Noguchi and Marat Khayrullin

### 0.3 (January 2, 2009)

- Bug fixes from 0.2
- Use quoted-string encoding for filename parameter
- Terminate encoded document with MIME boundary

### 0.2 (December 1, 2008)

- Bug fixes from version 0.1

### 0.1 (August 2, 2008)

- First release, used for internal projects

## License
##### poster3 (and poster) are licensed under the MIT license, available in the `LICENSE.txt` file.


```
Copyright (c) 2011 Chris AtLee, 2016 Evan Darwin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```