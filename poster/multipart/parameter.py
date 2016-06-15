from io import UnsupportedOperation

from email.header import Header
from mimetypes import guess_type

import os
import re
import uuid


class Parameter(object):
    """Represents a single parameter in a multipart/form-data request

        ``name`` is the name of this parameter.

        If ``value`` is set, it must be a string or unicode object to use as the
        data for this parameter.

        If ``filename`` is set, it is what to say that this parameter's filename
        is.  Note that this does not have to be the actual filename any local file.

        If ``filetype`` is set, it is used as the Content-Type for this parameter.
        If unset it defaults to "text/plain; charset=utf8"

        If ``filesize`` is set, it specifies the length of the file ``fileobj``

        If ``fileobj`` is set, it must be a file-like object that supports
        .read().

        Both ``value`` and ``fileobj`` must not be set, doing so will
        raise a ValueError assertion.

        If ``fileobj`` is set, and ``filesize`` is not specified, then
        the file's size will be determined first by stat'ing ``fileobj``'s
        file descriptor, and if that fails, by seeking to the end of the file,
        recording the current position as the size, and then by seeking back to the
        beginning of the file.

        ``cb`` is a callable which will be called from iter_encode with (self,
        current, total), representing the current parameter, current amount
        transferred, and the total size.
        """

    def __init__(self, name, content, filename=None, mime_type=None, cb=None):
        """
        Creates a new multipart form data object, representing a file
         or some data.

        :param name:
        :param content:
        :param filename:
        :param mime_type:
        :param file:
        :param cb:
        """

        # Check that there is content provided
        if not content:
            raise ValueError('You must provide content to encode')

        self.file = None
        self.filename = None
        self.mime_type = None

        # Set the boundary
        self.boundary = None

        # If the content is a 'file-like' object, set it as the
        # file object.
        if content and hasattr(content, 'read'):
            self.file = content

        # Encode the header
        self.name = Header(name).encode()

        # Make the content None if the content is a file object
        self.content = None if self.file else content.encode('utf-8')

        if self.file:
            # Let's encode the filename properly
            self.filename = filename.encode('ascii', 'xmlcharrefreplace') \
                .decode('utf-8').replace('"', '\\"') if filename else None

            # Use mimetypes to guess the MIME type if it's not provided
            self.mime_type = guess_type(filename)[0] if not mime_type and filename else mime_type

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
                # TODO: Remove me and replace w/ something better
                print('Couldn\'t determine file size, {},{},{}'.format(self.filename,
                                                                       self.filesize,
                                                                       self.filename))
            finally:
                if self.file:
                    boundary_match = re.compile(r'^--[\w]+$', re.MULTILINE)
                    contents = str(self.file.read())

                    if re.match(boundary_match, contents):
                        raise ValueError('Boundary was found in file contents')

        # The callback method
        self.callback = cb

    def __len__(self):
        return self.content_length

    def __cmp__(self, other):
        # The attributes to compare
        attrs = ['name', 'file', 'content', 'filename', 'filesize', 'mime_type']

        # Grab the attributes for both our and the comparison object
        my = [getattr(self, a) for a in attrs]
        other = [getattr(other, a) for a in attrs]

        # Since Python 3 does not have cmp(), we use the 'official'
        # workaround.
        # http://codegolf.stackexchange.com/a/49779
        return (my > other) - (my < other)

    def set_boundary(self, boundary):
        self.boundary = boundary

    @classmethod
    def from_file(cls, name, filename, mime_type=None):
        """Returns a new MultipartParam object constructed from the local
        file at ``filename``.

        ``filesize`` is determined by os.path.getsize(``filename``)

        ``filetype`` is determined by mimetypes.guess_type(``filename``)[0]

        ``filename`` is set to os.path.basename(``filename``)
        """

        # Check if the path exists, if it doesn't raise an exception.
        if not os.path.exists(filename):
            raise IOError('File \'{}\' does not exist'.format(filename))

        # Create a new Parameter based off of the file
        return cls(name, open(filename, 'rb'),
                   filename=os.path.basename(filename),
                   filesize=os.path.getsize(filename),
                   mime_type=mime_type),

    @property
    def headers(self):
        # Prefix with the multipart boundary '--[boundary]'
        headers = []

        if self.file and self.filename:
            disposition = 'form-data; name="{}"; filename="{}"'.format(self.name, self.filename)
        else:
            disposition = 'form-data; name="{}"'.format(self.name)

        # Append the key and filename information
        headers.append("Content-Disposition: {}".format(disposition))

        if self.mime_type:
            mime_type = self.mime_type
        else:
            mime_type = "text/plain; charset=utf-8"

        # Append the Content-Type
        headers.append("Content-Type: {}".format(mime_type))

        # Spacing
        headers.append("")
        headers.append("")

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

        content = ['--{}'.format(self.boundary)]  # The boundary beginning
        content += self.headers  # All headers

        if self.file:
            self.file.seek(0)
            block = self.file.read().decode('utf-8')

            content.append(block)
        else:
            content.append(self.content.decode('utf-8'))

        return '\r\n'.join(content) + '\r\n'
