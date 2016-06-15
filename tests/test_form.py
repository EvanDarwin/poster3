from tests import TestCase

from poster import Form, FormData
from tempfile import NamedTemporaryFile


class TestForm(TestCase):
    def test_construct(self):
        form = Form()

        self.assertEqual([], form.data)
        self.assertIsNotNone(form.boundary)

        # Extra construct check (should default to [])
        self.assertEqual([], Form(False).data)

        form_data = FormData('a', 'b')
        form_filled = Form([form_data])

        self.assertEqual([form_data], form_filled.data)

    def test_construct_not_list(self):
        self.assertRaises(ValueError, Form, {'a': 'b'})

    def test_construct_not_all_formdata(self):
        self.assertRaises(TypeError, Form, [1, 2, 3])

    def test_add_file(self):
        with NamedTemporaryFile() as f:
            f.write(b'hello, world')
            f.flush()

            form = Form()
            form.add_file('test', f, filename='test.html')

            content, headers = form.encode()
            boundary = form.boundary

            expected = '\r\n'.join([
                '--' + boundary,
                'Content-Disposition: form-data; name="test"; filename="test.html"',
                'Content-Type: text/html\r\n',
                'hello, world',
                '--{}--'.format(boundary)
            ])

            self.assertEqual(expected, content)

            self.assertEqual('180', headers.get('Content-Length'))
            self.assertEqual('multipart/form-data; boundary=--' + boundary,
                             headers.get('Content-Type'))

    def test_add_file_invalid_name(self):
        form = Form()

        self.assertRaises(ValueError, form.add_file, None, None)
        self.assertRaises(ValueError, form.add_file, False, None)
        self.assertRaises(ValueError, form.add_file, True, None)
        self.assertRaises(ValueError, form.add_file, 123, None)

    def test_add_file_invalid_content(self):
        form = Form()

        self.assertRaises(ValueError, form.add_file, 'abc1', None)
        self.assertRaises(ValueError, form.add_file, 'abc2', False)
        self.assertRaises(ValueError, form.add_file, 'abc3', True)
        self.assertRaises(ValueError, form.add_file, 'abc4', 123)
        self.assertRaises(ValueError, form.add_file, 'abc4', '')

    def test_add_data_invalid_name(self):
        pass

    def test_add_data_invalid_content(self):
        pass

    def test_add_parameter(self):
        pass

    def test_add_parameter_invalid_type(self):
        pass

    def test_encode(self):
        pass
