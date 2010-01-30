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

