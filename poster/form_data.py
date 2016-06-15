from io import UnsupportedOperation

from email.header import Header
from mimetypes import guess_type
from collections import OrderedDict

import os
import re


class FormData(object):
    def __init__(self, name, content, filename=None, mime_type=None, cb=None):
        """
        Creates a new FormData object, which will take a content that is either
        a `str` or a file-like object, and will read the contents into a buffer.

        If you provide the `filename` parameter, you can override the filename
        that is returned in the list of headers and the final encoded result.

        If you specify the `mime_type` parameter, it will override the MIME type
        declaration with any string you provide.

        If you specify the callback method, you must provide a callable function with
        these three parameters:

            - data      (A ``FormData`` object)
            - current   (The current byte position of the buffer)
            - total     (The total number of bytes to read)


        :param name:        The key to identify the data with

        :param content:     The content to include, can be either a string or a file-like
                            object that will read the contents

        :param filename:    The filename to include in the request, default of None will
                            automatically determine the filename. If a value is provided, it will
                            use that file name in the encoded result.

        :param mime_type:   The MIME type to declare, if left blank (None), we will
                            automatically try and determine the type based off of the file
                            extension.

        :param cb:          The callback, used for progress functions and tracking.
        """

        # Validate that some form of content was provided
        if not content and not (isinstance(content, str) or hasattr(content, 'read')):
            raise ValueError('You must provide a content of type str or a file-like object')

        self.file = None
        """ File: If the content is a buffer, this is where the file-like object is """

        self.filename = None
        """ str: The filename of the file, if not provided, will be automatically found """

        self.mime_type = None
        """ str: The MIME type of the content, if not provided, will attempt to detect based
                 on the filename """

        # Set the boundary
        self.boundary = None
        """ str: A random string that is used to separate the elements of the form """

        # Detect if the content provided is a buffer object, that has
        # a .read() method.
        if content and hasattr(content, 'read'):
            self.file = content

        self.name = Header(name).encode()
        """ str: The name of this value, the identifier for this data. The value is automatically encoded. """

        # Make the content None if the content is a file object
        self.content = None if self.file else content
        """ object: The content object, only set if the content is not a buffer """

        # If we're dealing with a buffer object
        if self.file:
            # Validate the user input
            if filename and not isinstance(filename, str):
                filename = None

            # If our file-like object has a name attribute and we've got nothing
            # yet, let's try that.
            if not filename and hasattr(self.file, 'name'):
                filename = self.file.name

            # Encode whatever we've got.
            if filename:
                self.filename = filename.encode('ascii', 'xmlcharrefreplace') \
                    .decode('utf-8').replace('"', '\\"')

            # Validate the mime_type parameter
            if mime_type and not isinstance(mime_type, str):
                mime_type = None

                # Use mimetypes package to guess the MIME type based off of the file name
            if not mime_type and self.filename:
                mime_type = guess_type(filename)[0]

            self.mime_type = mime_type

            try:
                # Use fstat to find the length of the file
                self.filesize = os.fstat(self.file.fileno()).st_size
            except (OSError, AttributeError, UnsupportedOperation):
                if self.file:
                    # Go to the last byte in the file
                    self.file.seek(0, 2)

                    # .tell() us the position of that byte
                    self.filesize = self.file.tell()

                    # Seek back to the beginning of the file
                    self.file.seek(0)
            except AttributeError:
                # FIXME: Throw a real error here
                self.filesize = -1
            finally:
                if self.file:
                    boundary_match = re.compile(r'^--[\w]+$', re.MULTILINE)
                    contents = str(self.file.read())

                    if re.match(boundary_match, contents):
                        raise ValueError('Boundary was found in file contents')

        # The callback method
        self.callback = cb

    def __len__(self):
        """
        The __len__ magic method, which returns the length of the content.

        In this case, we have a specific function that determines the length of
        our encoded response, so let's use that.

        :returns: The length of the encoded response
        :rtype: int
        """

        return self.content_length

    def __cmp__(self, other):
        """
        The __cmp__ magic method, which compares two FormData objects.

        :param other: The object to compare it to

        :return: -1 and 1 specify that the objects are not equal, while 0 is equal.
        """

        # The attributes to compare
        attrs = ['name', 'content', 'filename', 'filesize', 'mime_type']

        # Grab the attributes for both our and the comparison object
        my = [getattr(self, a) for a in attrs]
        other = [getattr(other, a) for a in attrs]

        # Since Python 3 does not have cmp(), we use the 'official' workaround.
        # http://codegolf.stackexchange.com/a/49779
        return (my > other) - (my < other)

    def set_boundary(self, boundary):
        """
        Sets the boundary in the context of a Form, this is usually called
        by the `Form` class because all Form objects should have the same
        boundary key.

        :param boundary: A unique string that is the boundary
        :type boundary: str
        """

        self.boundary = boundary

    @property
    def headers(self):
        """
        A dictionary of the data's HTTP headers and their values.

        Example:
            >>> {
            >>>     'Content-Type': 'text/plain'
            >>> }

        :return: A dictionary of HTTP headers to apply for this object
        :rtype: dict
        """

        # Prefix with the multipart boundary '--[boundary]'
        headers = {}

        disposition = 'form-data; name="{}"'.format(self.name)

        if self.file and self.filename:
            disposition += '; filename="{}"'.format(self.filename)

        headers = OrderedDict([
            ('Content-Disposition', disposition),
            ('Content-Type', self.mime_type or 'text/plain; charset=utf-8')
        ])

        return headers

    @property
    def content_length(self):
        content_length = self.filesize if self.file else len(self.content)

        return len('\r\n'.join(self.headers)) + 2 + content_length

    def encode(self):
        """
        Returns the string encoding of this parameter

        Example result:

        >>> --6e5519580cb741e49982addb5b6bbb63
        >>> Content-Disposition: form-data; name="hello"; filename="hello.txt"
        >>> Content-Type: text/plain
        >>>
        >>> world
        """

        content = '--{}\r\n'.format(self.boundary)
        content += '\r\n'.join(['{}: {}'.format(k, v) for k, v in self.headers.items()])
        content += '\r\n\r\n'

        if self.file:
            self.file.seek(0)
            block = self.file.read().decode('utf-8')

            content += block
        else:
            content += self.content

        return content + '\r\n'
