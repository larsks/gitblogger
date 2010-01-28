#!/usr/bin/env python

import os
import sys
import optparse
import git
import subprocess

import db
from lock import Lock

from ConfigParser import ConfigParser

class GitError(Exception):
    pass

def parse_args():
    p = optparse.OptionParser()
    return p.parse_args()

def read_config():
    config = ConfigParser()
    config.read('gitblogger.conf')
    if not config.has_section('gitblogger'):
        raise GitError('No [gitblogger] section in config file.')

    return config

class Repo(git.repo.Repo):
    
    def __init__ (self, config, path='.'):
        self.config = config
        self.path = os.path.abspath(path)

        git.repo.Repo.__init__(self, self.path)

    def reset(self):
        self.git.reset('--hard')

class Blog(object):
    
    def __init__ (self, config):
        self.config = config

def post_receive_main():
    config = read_config()

    repo = Repo(config)
    blog = Blog(config)

    db.metadata.bind = 'sqlite:///gitblogger.sqlite'
    db.setup_all()
    db.create_all()

#    # bring repository up-to-date
#    print >>sys.stderr, 'Resetting HEAD...'
#    x = os.environ['GIT_DIR']
#    del os.environ['GIT_DIR']
#    repo.reset()
#    os.environ['GIT_DIR'] = x

    for line in sys.stdin:
        old, new, ref = line.strip().split()
        if ref not in config.get('gitblogger', 'refs').split():
            print >>sys.stderr, 'Skipping %s: not in refs.' % ref
            continue

        print >>sys.stderr, 'old:', old
        print >>sys.stderr, 'new:', new

        diffs = git.commit.Commit.diff(repo, old, new)
        for diff in diffs:
            print diff.a_path, diff.b_path, diff.new_file, diff.deleted_file, diff.renamed

            if diff.deleted_file:
                # file was deleted; delete from blog (maybe)
                # and remove from database.
                entry = db.File.query.filter_by(path=diff.a_path).one()
                print 'DELETE:', entry
            elif diff.new_file:
                # file is new; add to database, post to blog,
                # update database with post id.
                entry = db.File(
                        path = diff.a_path,
                        last_commit_id = new,
                        )
                print 'NEW:', entry
            elif diff.renamed:
                # file was renamed; update database.
                entry = db.File.query.filter_by(path=diff.a_path).one()
                entry.path = diff.b_path
                print 'RENAME:', entry
            else:
                # file was modified; re-post to blog.
                entry = db.File.query.filter_by(path=diff.a_path).one()
                print 'MODIFY:', entry

        db.session.commit()

if __name__ == '__main__':
    post_receive_main()

