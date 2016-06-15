from poster import Form, FormData


def multipart_encode(parameters):
    # TODO: REWRITE CODE

    form = Form()

    if isinstance(parameters, list):
        if not all([isinstance(x, FormData) for x in parameters]):
            raise ValueError('All instances must be of type Parameter when providing a list')

        form.parameters += parameters
    elif isinstance(parameters, dict):
        for name, content in parameters.items():
            try:
                content.seek(0)

                form.add_file(name, content)
            except AttributeError:
                form.add_data(name, content)

    return form.encode()


class MultipartParam(object):
    @classmethod
    def from_file(cls, name, path):
        import os

        if isinstance(path, str):
            if not os.path.exists(path):
                raise IOError('\'{}\' could not be located'.format(path))

            return FormData(name, open(path, 'rb'))
        else:
            return FormData(name, path)
