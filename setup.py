from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='poster',
      version=version,
      description="Streaming upload support over HTTP",
      long_description="""The modules in the Python standard library don't
provide a way to upload large files via HTTP without having to load the
entire file into memory first.  poster provides support for both streaming
POST requests as well as multipart/form-data encoding of string or file
parameters""",
      classifiers=[
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='python http post multipart/form-data file upload',
      author='Chris AtLee',
      author_email='chris@atlee.ca',
      url='http://atlee.ca/software/poster',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[],
      entry_points="",
      )
