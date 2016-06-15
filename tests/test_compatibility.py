from . import TestCase

from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers

import tempfile


class TestCompatibility(TestCase):
    def test_multipart_encode(self):
        with tempfile.NamedTemporaryFile('w+b') as file:
            file.write(b'world')
            file.flush()

            response, headers = multipart_encode({
                'foo': 'bar',
                'hello': file,
            })

            boundary = response[-34:-2]

        expected_foo = '\r\n'.join([
            '--' + boundary,
            'Content-Disposition: form-data; name="foo"',
            'Content-Type: text/plain; charset=utf-8',
            '', 'bar'
        ]).strip()

        expected_hello = '\r\n'.join([
            '--' + boundary,
            'Content-Disposition: form-data; name="hello"; filename="{}"'.format(file.name),
            'Content-Type: text/plain; charset=utf-8',
            '', 'world'
        ]).strip()

        self.assertGreater(response.find(expected_foo), -1)
        self.assertGreater(response.find(expected_hello), -1)

        self.assertIn('Content-Length', list(headers.keys()))
        self.assertIn('Content-Type', list(headers.keys()))

        self.assertEqual('multipart/form-data; boundary=--' + boundary, headers.get('Content-Type'))

    def test_multipart_encode_list(self):
        with tempfile.NamedTemporaryFile('w+b') as file:
            file.write(b'world')
            file.flush()

            param = MultipartParam.from_file('hello', file)

            self.assertIsNotNone(param)
            print(param)

    def test_register_openers(self):
        """
        This test checks that the function exists and can be called.
        """

        opener = register_openers()

        # Make sure we're using the dummy opener
        self.assertEqual('DummyOpener', type(opener).__name__)
        self.assertIsNone(opener.add_handler())
