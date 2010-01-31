#!/usr/bin/env python

import os
import sys
import optparse
import datetime
import logging
from cStringIO import StringIO

from configdict import ConfigDict
import git

import db
import blog
import utils
import rstdoc
from lock import Lock

class GitError(Exception):
    pass

def parse_args():
    p = optparse.OptionParser()
    return p.parse_args()

def read_config(path):
    config = ConfigDict(path)
    if not 'gitblogger' in config:
        raise GitError('No [gitblogger] section in config file.')

    return config

def post_receive_main():
    config = read_config('config')

    del os.environ['GIT_DIR']
    os.chdir('..')
    myrepo = git.repo.Repo('.')
    print >>sys.stderr, 'Repo path:', myrepo.path
    myblog = blog.Blog(config)

    db.metadata.bind = 'sqlite:///.git/gitblogger.sqlite'
    db.setup_all()
    db.create_all()

    print >>sys.stderr, 'Resetting HEAD...'
    myrepo.git.reset('--hard')

    refs = config['gitblogger'].get('refs', '').split()
    for line in sys.stdin:
        old, new, ref = line.strip().split()
        if ref not in refs:
            print >>sys.stderr, 'Skipping %s: not in refs.' % ref
            continue

        print >>sys.stderr, 'old:', old
        print >>sys.stderr, 'new:', new

        diffs = utils.diff_tree(myrepo, old, new)
        for diff in diffs:
            if not diff.a_path.endswith('.rst'):
                print >>sys.stderr, 'Unknown extension: %s' % diff.a_path
                continue

            if diff.deleted_file:
                # file was deleted; delete from blog (maybe)
                # and remove from database.
                print 'DELETE:', diff.a_path

                entry = db.File.query.filter_by(path=diff.a_path).one()
                if not entry:
                    print >>sys.stderr, 'File not found in database:', diff.a_path
                    continue

                if entry.post_id:
                    post = myblog.get_post(entry.post_id)
                    if not post:
                        print >>sys.stderr, 'Post not found on log.'
                    else:
                        myblog.delete(post)

                entry.delete()
            elif diff.new_file:
                # file is new; add to database, post to blog,
                # update database with post id.
                print 'NEW:', diff.a_path

                doc = rstdoc.RSTDoc(diff.a_path)
                post = myblog.add_post(doc)
                entry = db.File(
                        path = diff.a_path,
                        last_commit_id = new,
                        post_id = post.get_post_id(),
                        )
            elif diff.renamed_file:
                # file was renamed; update database.
                print 'RENAME:', diff.a_path, diff.b_path

                entry = db.File.query.filter_by(path=diff.a_path).one()
                entry.path = diff.b_path
            elif diff.modified_file:
                # file was modified; re-post to blog.
                print 'MODIFY:', diff.a_path
                entry = db.File.query.filter_by(path=diff.a_path).one()
                if not entry:
                    print >>sys.stderr, 'File not found in database:', diff.a_path
                    continue
                doc = rstdoc.RSTDoc(diff.a_path)
                post = myblog.get_post(entry.post_id)
                myblog.update_post(post, doc)
                entry.last_commit_id = new
                entry.updated = datetime.datetime.utcnow()
            else:
                print 'UNKNOWN'

        db.Metadata(
                name='last_commit_id',
                value=new)
        db.session.commit()

if __name__ == '__main__':
    post_receive_main()

