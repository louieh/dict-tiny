import setuptools

VERSION = '0.0.2'

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dict-tiny",
    version=VERSION,
    author="louie",
    author_email="louiehan1015@gmail.com",
    description="A tiny dictionary.",
    long_description=long_description,
    url="https://github.com/louieh/dict-tiny",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'lxml'
    ],
    entry_points={
      'console_scripts':[
          'dict-tiny = dict_tiny.main:main'
      ]
    },
    classifiers=(
      "Programming Language :: Python :: 3",
    )

)
