from setuptools import setup
import io

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


setup(name='dayonetools',
      version='1.1.0',
      description='Tools to import multiple services into Day One Journal',
      long_description=read('README.md'),
      package_data={'': ['README.md']},
      license='MIT',
      author='Luke Lee',
      author_email='durdenmisc@gmail.com',
      url='https://github.com/durden/dayonetools',
      packages=['dayonetools', 'dayonetools.services'],
      install_requires=['python-dateutil>=2.2', 'pytz==2014.4'],
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
