import setuptools

VERSION = '0.1'

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dict-tiny",
    version=VERSION,
    author="louie",
    author_email="louiehan1015@gmail.com",
    description="A tiny command-line dictionary that scrapes youdao.com.",
    long_description=long_description,
    url="https://github.com/louieh/dict-tiny",
    keywords='youdao dictionary command-line',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'lxml',
        'plumbum'
    ],
    entry_points={
      'console_scripts':[
          'dict-tiny = dict_tiny.main:main'
      ]
    },
    classifiers=(
        "Environment :: Console",
        "Intenden Audience :: Developers",
        "Opersting System :: OS Independent",
        "Programming Language :: Python :: 3",
    )

)