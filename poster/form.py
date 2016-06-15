from .form_data import FormData

import uuid

try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus


class Form(object):
    def __init__(self, data=None):
        self.data = data or []
        self.boundary = quote_plus(uuid.uuid4().hex)

        # Check that the parameters given is a dictionary
        if not isinstance(self.data, list):
            raise ValueError('data list must be of type list, is type {}'.format(type(self.data).__name__))

        if not all([isinstance(x, FormData) for x in self.data]):
            raise TypeError('All objects in list must be of type FormData')

        # Update the list
        for parameter in self.data:
            parameter.set_boundary(self.boundary)

    def add_file(self, name, fh, filename=None, mime_type=None):
        if not name or not isinstance(name, str):
            raise ValueError('You must provide a valid name')

        if not fh or not hasattr(fh, 'read'):
            raise ValueError('You must provide a valid file handler')

        data = FormData(name, fh, filename=filename, mime_type=mime_type)
        self.add_form_data(data)

        return data

    def add_data(self, name, content):
        if not name:
            raise ValueError('You must provide a valid name')

        if not content:
            raise ValueError('You must provide valid content')

        data = FormData(name, content)
        self.add_form_data(data)

        return data

    def add_form_data(self, form_data):
        if not isinstance(form_data, FormData):
            raise ValueError(
                'Multipart requires form_data to be of type FormData, is \'{}\''.format(type(form_data).__name__))

        self.data.append(form_data)

    def encode(self, cb=None):
        """
        Encode ``params`` as multipart/form-data.

        ``params`` should be a sequence of (name, value) pairs or MultipartParam
        objects, or a mapping of names to values.
        Values are either strings parameter values, or file-like objects to use as
        the parameter value.  The file-like objects must support .read() and either
        .fileno() or both .seek() and .tell().

        If ``boundary`` is set, then it as used as the MIME boundary.  Otherwise
        a randomly generated boundary will be used.  In either case, if the
        boundary string appears in the parameter values a ValueError will be
        raised.

        If ``cb`` is set, it should be a callback which will get called as blocks
        of data are encoded.  It will be called with (param, current, total),
        indicating the current parameter being encoded, the current amount encoded,
        and the total amount to encode.

        Returns a tuple of `datagen`, `headers`, where `datagen` is a
        generator that will yield blocks of data that make up the encoded
        parameters, and `headers` is a dictionary with the assoicated
        Content-Type and Content-Length headers.

        """

        content = ''
        position = 0

        # [parameters] * [param. length] + '--' + [boundary] + '--' + \r\n
        #                              |||   2  +     32     +  2   +   2   =   38 bytes
        total = sum(len(p) for p in self.data) + 38

        for field in self.data:
            field.set_boundary(self.boundary)

            block = field.encode()
            position += len(block)

            content += block

            if cb:
                cb(field, position, total)

        content += '--{}--'.format(self.boundary)

        headers = {
            'Content-Type': 'multipart/form-data; boundary=--{}'.format(self.boundary),
            'Content-Length': str(len(content)),
        }

        return content, headers
