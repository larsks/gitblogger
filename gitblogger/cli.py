#!/usr/bin/python

import os
import sys

import gitblogger
import baker
from baker import run

@baker.command
def receive (debug=False):
    pass

@baker.command
def list(unlinked=False):
    pass

@baker.command
def link(path, postid):
    pass

@baker.command
def unlink(path_or_id, path=False, postid=False):
    pass

@baker.command
def render(path, stdout=False):
    pass

if __name__ == '__main__':
    run()

