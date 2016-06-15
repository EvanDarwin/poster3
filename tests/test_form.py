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
        form = Form()

        self.assertRaises(ValueError, form.add_data, None, '')
        self.assertRaises(ValueError, form.add_data, False, '')
        self.assertRaises(ValueError, form.add_data, True, '')
        self.assertRaises(ValueError, form.add_data, 123, '')

    def test_add_data_invalid_content(self):
        form = Form()

        self.assertRaises(ValueError, form.add_data, 'abc1', None)
        self.assertRaises(ValueError, form.add_data, 'abc2', False)
        self.assertRaises(ValueError, form.add_data, 'abc3', True)
        self.assertRaises(ValueError, form.add_data, 'abc4', 123)
        self.assertRaises(ValueError, form.add_data, 'abc4', dict())

    def test_add_form_data(self):
        form = Form()
        data = FormData('foo', 'bar')

        form.add_form_data(data)

        self.assertEqual('foo', form.data[0].name)
        self.assertEqual([data], form.data)

    def test_add_form_data_invalid_type(self):
        form = Form()

        self.assertRaises(ValueError, form.add_form_data, None)
        self.assertRaises(ValueError, form.add_form_data, False)
        self.assertRaises(ValueError, form.add_form_data, '')
        self.assertRaises(ValueError, form.add_form_data, {})
        self.assertRaises(ValueError, form.add_form_data, 123)

    def test_add_parameter(self):
        pass

    def test_add_parameter_invalid_type(self):
        pass

    def test_encode(self):
        with NamedTemporaryFile() as f:
            f.write(b'hello_world')
            f.flush()

            form = Form()
            form.add_data('foo', 'bar')
            form.add_data('a space', 'hello')
            form.add_data('arr[]', 'hello2')
            form.add_file('hello', f)

            contents, headers = form.encode()

            expected = '\r\n'.join("""--{0}
Content-Disposition: form-data; name="foo"
Content-Type: text/plain; charset=utf-8

bar
--{0}
Content-Disposition: form-data; name="a space"
Content-Type: text/plain; charset=utf-8

hello
--{0}
Content-Disposition: form-data; name="arr[]"
Content-Type: text/plain; charset=utf-8

hello2
--{0}
Content-Disposition: form-data; name="hello"; filename="{1}"
Content-Type: text/plain; charset=utf-8

hello_world
--{0}--""".split('\n')).format(form.boundary, f.name)

            self.assertEqual(expected, contents)

    def test_boundary_space(self):
        form = Form()
