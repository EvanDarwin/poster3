from tests import TestCase

from poster import FormData
from tempfile import NamedTemporaryFile


class TestFormData(TestCase):
    def test_basic_construct(self):
        data = FormData('foo', 'bar')

        self.assertEqual('foo', data.name)
        self.assertEqual('bar', data.content)
        self.assertEqual(38, data.content_length)

    def test_file_construct(self):
        with NamedTemporaryFile() as tmp_file:
            tmp_file.write(b'profile example here')
            tmp_file.flush()

            data = FormData('profile', tmp_file)
            data.set_boundary('testing')

            encode = data.encode()

            print('*' * 50)
            print(encode.encode('utf-8'))
            print('*' * 50)

            self.assertEqual("""--{0}
Content-Disposition: form-data; name="profile"; filename="{1}"
Content-Type: text/plain; charset=utf-8

profile example here
""".format('testing', tmp_file.name).replace('\n', '\r\n'), encode)

    def test_name_php_array(self):
        data = FormData('array[]', 'value')
        data.set_boundary('xxxxx')

        content = data.encode()

        self.assertEqual('array[]', data.name)
        self.assertEqual('value', data.content)

        self.assertEqual("""--{0}
Content-Disposition: form-data; name="array[]"
Content-Type: text/plain; charset=utf-8

value
""".format('xxxxx').replace('\n', '\r\n'), content)

    def test_boundary_space(self):
        data = FormData('hello', 'value')
        data.set_boundary('i am spaced')

        content = data.encode()

        self.assertEqual('hello', data.name)
        self.assertEqual('value', data.content)

        self.assertEqual("""--i+am+spaced
Content-Disposition: form-data; name="hello"
Content-Type: text/plain; charset=utf-8

value
""".replace('\n', '\r\n'), content)

    def test_construct_options(self):
        pass

    def file_construct_invalid_content(self):
        pass
