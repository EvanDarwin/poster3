from setuptools import setup, find_packages
import poster

version = ".".join(str(x) for x in poster.version)

setup(name='poster',
      version=version,
      description="Streaming HTTP uploads and multipart/form-data encoding",
      long_description="""\
The modules in the Python standard library don't provide a way to upload large
files via HTTP without having to load the entire file into memory first.

poster provides support for both streaming POST requests as well as
multipart/form-data encoding of string or file parameters""",
      classifiers=[
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='python http post multipart/form-data file upload',
      author='Evan Darwin',
      author_email='evan@relta.net',
      url='https://github.com/EvanDarwin/poster3',
      license='MIT',
      packages=find_packages(exclude=['tests', 'tests.*']),
      include_package_data=True,
      zip_safe=True,
      extras_require={'poster': ["buildutils", "sphinx"]},
      tests_require=["nose", "webob", "paste"],
      test_suite='nose.collector',
      )
