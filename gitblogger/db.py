from elixir import *

class File (Entity):

    path            = Field(UnicodeText, unique=True)
    post_id         = Field(UnicodeText)
    last_commit_id  = Field(Unicode(40))
    updated         = Field(DateTime())

    def __repr__ (self):
        return '<File "%s">' % self.path

class Metadata (Entity):

    name        = Field(Unicode(80), unique=True)
    value       = Field(UnicodeText)

