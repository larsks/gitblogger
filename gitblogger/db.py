import logging
from elixir import *

class File (Entity):

    path            = Field(String, unique=True)
    post_id         = Field(String)
    last_commit_id  = Field(String(40))
    updated         = Field(DateTime())

    def __repr__ (self):
        return '<File "%s">' % self.path

class Metadata (Entity):

    name        = Field(String(80), unique=True)
    value       = Field(String)

def init(uri, echo=False):
    global metadata
    log = logging.getLogger('gitblogger.db')
    log.info('Connecting to %s.' % uri)
    metadata.bind = uri
    metadata.bind.echo = echo
    setup_all()
    create_all()

