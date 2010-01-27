from setuptools import setup, find_packages

setup(name='gitblogger',
        version='20100127.1',
        description='Publish reStructuredText documents to Blogger from a Git repository.',
        author='Lars Kellogg-Stedman',
        author_email='lars@oddbit.com',
        packages=['gitblogger'],
        scripts=['scripts/gitblogger',],
        )
