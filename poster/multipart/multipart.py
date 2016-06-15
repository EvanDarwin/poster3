from . import Parameter

import uuid

try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus


class Multipart(object):
    def __init__(self, parameters=None):
        self.parameters = parameters or []
        self.boundary = quote_plus(uuid.uuid4().hex)

        # Check that the parameters given is a dictionary
        if not isinstance(self.parameters, list):
            raise ValueError('Parameters list must be of type list, is type {}'.format(type(self.parameters).__name__))

        if not all([isinstance(x, Parameter) for x in self.parameters]):
            raise TypeError('All objects in list must be of type Parameter')

        # Update the list
        for parameter in self.parameters:
            parameter.set_boundary(self.boundary)

    def add_file(self, name, fh, filename=None, mime_type=None):
        if not name or not isinstance(name, str):
            raise ValueError('You must provide a valid name')

        if not fh:
            raise ValueError('You must provide a valid file handler')

        filename = fh.name if fh and not filename else filename

        parameter = Parameter(name, fh, filename=filename, mime_type=mime_type)
        self.add_parameter(parameter)

        return parameter

    def add_data(self, name, content):
        if not name:
            raise ValueError('You must provide a valid name')

        if not content:
            raise ValueError('You must provide valid content')

        parameter = Parameter(name, content)
        self.add_parameter(parameter)

        return parameter

    def add_parameter(self, parameter):
        if not isinstance(parameter, Parameter):
            raise ValueError(
                'Multipart requires parameters to be of type Parameter, is \'{}\''.format(type(parameter).__name__))

        self.parameters.append(parameter)

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
        total = sum(p.content_length for p in self.parameters) + 38

        for parameter in self.parameters:
            parameter.set_boundary(self.boundary)

            block = parameter.encode()
            position += len(block)

            content += block

            if cb:
                cb(parameter, position, total)

        content += '--{}--'.format(self.boundary)
        headers = {
            'Content-Type': 'multipart/form-data; boundary=--{}'.format(self.boundary),
            'Content-Length': str(len(content)),
        }

        return content.encode('utf-8'), headers
