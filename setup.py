from distutils.core import setup

setup(name='dayonetools',
      version='0.1',
      description='Tools to import multiple services into Day One Journal',
      author='Luke Lee',
      author_email='durdenmisc@gmail.com',
      url='http://www.lukelee.me',
      packages=['dayonetools', 'dayonetools.services'],
      entry_points={
        "console_scripts": [
            "dayonetools = dayonetools.main:main",
        ]
    },
)
