from .form_data import FormData

import uuid

try:  # pragma: no cover
    from urllib import quote_plus
except ImportError:  # pragma: no cover
    from urllib.parse import quote_plus


class Form(object):
    def __init__(self, data=None, boundary=None):
        """
        Creates a new Form object, which is used to generate the
        multipart http form response.

        :param data:    The data parameter should be left blank, or if you
                        have pre-existing FormData objects, you can pass them
                        in as a list.

                        Example:
                        >>> form = Form([FormData('a', 'b')])

        :type data:     list
        """

        # See if the user provided data, otherwise fallback
        self.data = data or []

        if boundary and isinstance(boundary, str):
            # Use the user provided boundary
            self.boundary = quote_plus(boundary.replace(' ', '+'))
        else:
            # Generate a new unique random string for the boundary
            self.boundary = quote_plus(uuid.uuid4().hex)

        # Check that the parameters given is a list
        if not isinstance(self.data, list):
            raise ValueError('data list must be of type list, is type {}'.format(type(self.data).__name__))

        # Check that all of the items are the FormData type
        if not all([isinstance(x, FormData) for x in self.data]):
            raise TypeError('All objects in list must be of type FormData')

    def add_file(self, name, fh, filename=None, mime_type=None):
        """
        Adds a new FormData object that uses a file handler for the content,
        allowing for buffered input.

        :param name:        A name used by multipart to identify the content
        :param fh:          The file(-like) handler that allows for buffered reading
        :param filename:    If not provided, will attempt to determine it automatically
        :param mime_type:   The MIME type of the document, with also automatically detect
                            based on the file extension of the ``filename``

        :returns:   The new FormData obejct
        :rtype:     FormData
        """

        # Validate that the name is valid
        if not name or not isinstance(name, str):
            raise ValueError('You must provide a valid name')

        # Validate that the file buffer is valid
        if not fh or not hasattr(fh, 'read'):
            raise ValueError('You must provide a valid file handler')

        # Create a new FormData object
        data = FormData(name, fh, filename=filename, mime_type=mime_type)

        # Add to this form
        self.add_form_data(data)

        return data

    def add_data(self, name, content):
        """
        Adds a new FormData object to the Form, and accepts the value to
        be any arbitrary string.

        This data has no Content-Type applied to it.

        :param name:    The name to identify the content
        :param content: The content to encode

        :returns: The FormData object
        :rtype: FormData
        """

        # Validate that the name is valid
        if not name or not isinstance(name, str):
            raise ValueError('You must provide a valid name')

        # Validate that the file buffer is valid
        if not content or not isinstance(content, str):
            raise ValueError('You must provide a valid content as a string')

        # Create a new FormData object
        data = FormData(name, content)

        # Add to this form
        self.add_form_data(data)

        return data

    def add_form_data(self, form_data):
        """
        Adds a FormData object directly to our list of data.

        :param form_data:   The FormData object to add
        :type form_data:    FormData
        """

        # Check that it's the correct instance type
        if not isinstance(form_data, FormData):
            raise ValueError(
                'Multipart requires form_data to be of type FormData, is \'{}\''.format(type(form_data).__name__))

        # Add the FormData to our data
        self.data.append(form_data)

    def encode(self, cb=None):
        """
        Encodes the FormData object into something that can be joined together to
        make a valid, encoded multipart form.

        The resulting output should be something similar to:

            >>> --EXAMPLE
            >>> Content-Disposition: form-data; name="foo"
            >>>
            >>> bar
            >>> --EXAMPLE
            >>> Content-Disposition: form-data; name="profile"; filename="profile.jpg"
            >>> Content-Type: image/jpg
            >>>
            >>> IMAGE_DATA_HERE
            >>> --EXAMPLE--

        :param cb:  The callback function, can be used to track the process
                    of reading the buffered content, especially for larger
                    files.
        """

        content = ''
        position = 0

        # The sum of all of our data + 38
        # -- (2) + [uuid boundary] (32) + -- (2) + \r\n (2) = 38 bytes
        total = sum(len(p) for p in self.data) + 38

        # Iterate through the data
        for field in self.data:
            # Set the boundary for this Form on the FormData
            field.set_boundary(self.boundary)

            # Get the encoded output of the data
            block = field.encode()

            # Track the size of our output
            position += len(block)

            # Add the content to our result
            content += block

            # If we have a callback, call it
            if cb:
                cb(field, position, total)

        # Print a --[boundary]-- at the end to terminate the sequence
        content += '--{}--'.format(self.boundary)

        headers = {
            'Content-Type': 'multipart/form-data; boundary=--{}'.format(self.boundary),
            'Content-Length': str(len(content)),
        }

        return content, headers
