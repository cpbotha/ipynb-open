import os
from setuptools import setup
from ipython_notebook_open import ipno

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="ipython_notebook_open",
    version=ipno.VERSION,
    author="Charl P. Botha",
    author_email="cpbotha@vxlabs.com",
    description="Script for attaching to local IPython Notebook servers.",
    license="BSD",
    keywords="ipython ipython-notebook",
    url="https://github.com/cpbotha/ipython_notebook_open",
    packages=['ipython_notebook_open'],
    long_description=read('README.rst'),
    install_requires=['requests'],
    entry_points={
        'console_scripts': ['ipno = ipython_notebook_open.ipno:main']
    },
    # use MANIFEST.in file
    # because package_data is ignored during sdist
    #include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ]
)
