import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='gitblogger',
        version='20100130.3',
        install_requires=[
            'gitpython',
            'elixir',
            'sqlalchemy',
            'configdict',
            ],
        description='Publish reStructuredText documents to Blogger from a Git repository.',
        long_description=read('README.rst'),
        author='Lars Kellogg-Stedman',
        author_email='lars@oddbit.com',
        packages=['gitblogger'],
        scripts=['scripts/gitblogger-post-receive',],
        )

