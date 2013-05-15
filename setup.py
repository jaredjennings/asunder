#!/usr/bin/env python

from setuptools import setup

# http://www.scotttorborg.com/python-packaging/metadata.html
def readme():
    with open('README.rst') as f:
            return f.read()

setup(name='asunder',
    version='0.1',
    description='Automatically rips audio CDs upon insertion',
    long_description=readme(),
    author='Jared Jennings',
    author_email='jjenning@fastmail.fm',
    license='GPLv3+',
    packages=['asunder', 'asunder.detect', 'asunder.notify'],
    url='http://github.com/jaredjennings/asunder',
    install_requires=[
        'pyxdg',
        'sleekxmpp',
        'morituri',
        'PyGObject',
        'dbus-python',
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Topic :: Multimedia :: Sound/Audio :: CD Audio :: CD Ripping',
    ],
    entry_points={
        'console_scripts': [
            'asunder=asunder.main:main',
        ],
    },
)

