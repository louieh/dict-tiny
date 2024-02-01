import setuptools
from dict_tiny import version

VERSION = version.__version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=version.name,
    version=VERSION,
    author="louie",
    author_email="louiehan1015@gmail.com",
    description=version.DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/louieh/dict-tiny",
    keywords='python youdao dictionary command-line plumbum translator translate google-translation-api gemini openai',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'lxml',
        'plumbum',
        'pyperclip',
        'prompt-toolkit',
        'google-generativeai',
        'rich',
        'openai'
    ],
    entry_points={
        'console_scripts': [
            'dict-tiny = dict_tiny.main:run'
        ]
    },
    classifiers=(
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ),
    python_requires='>=3.9',

)
