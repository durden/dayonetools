from setuptools import setup

import io

import dayonetools

# Take from Jeff Knupp's excellent article:
# http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []

    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())

    return sep.join(buf)

long_description = read('README.md')

setup(name='dayonetools',
      version='0.2.0',
      description='Tools to import multiple services into Day One Journal',
      author='Luke Lee',
      author_email='durdenmisc@gmail.com',
      url='http://www.lukelee.me',
      packages=['dayonetools', 'dayonetools.services'],
      platforms='any',
      classifiers= [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: System :: Archiving'],
      entry_points={
        "console_scripts": [
            "dayonetools = dayonetools.main:main",
        ]
    },
)
