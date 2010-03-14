#!/usr/bin/env python

import os
import sys
import datetime
import logging
from cStringIO import StringIO

import sqlalchemy.orm.exc
from configdict import ConfigDict
import git

import db
import utils
from  blog import Blog
from rstdoc import RSTDoc

class GitError(Exception):
    '''Base class for all exceptions raised by this module.'''
    pass

class NoConfigurationError(GitError):
    '''Raised if there is no [gitblogger] section in the config
    file.'''
    pass

class ConfigurationError(GitError):
    '''Raised in the event of an invalid configuration.'''
    pass

class GitBlogger (object):

    def __init__ (self, config_path, repo_path):
        try:
            self.config = ConfigDict(config_path)['gitblogger']
            # XXX: configdict should probaly raise KeyError for
            # unknown sections.
            if not self.config:
                raise KeyError
        except KeyError:
            raise NoConfigurationError('No [gitblogger] section in config file.')

        self.setup_logging()
        self.repo = git.repo.Repo(repo_path)
        self.log.info('Repository path is: %s' % self.repo.path)
        self.blog = Blog(self.config)
        db.init(self.config.get('database uri',
            'sqlite:///%s/gitblogger.sqlite' % self.repo.path))

    def setup_logging(self):
        self.log = logging.getLogger('gitblogger')
        loglevel = self.config.get('loglevel', '').upper()
        if loglevel:
            try:
                loglevel = getattr(logging, loglevel)
                self.log.setLevel(loglevel)
            except AttributeError:
                raise ConfigurationError('No such loglevel: %(loglevel)s' %
                        self.config)

    def post_receive(self):
        '''Called from git repository's post-receive hook.  Uses
        diff-tree to get a list of changes between current and previous
        commit.'''

        self.log.info('Resetting repository (sync to index).')
        self.repo.git.reset('--hard')
        refs = self.config.get('refs',
                'refs/heads/master').split()

        for line in sys.stdin:
            old, new, ref = line.strip().split()
            if ref not in refs:
                self.log.info('Skipping %s: not in refs.' % ref)
                continue

            self.log.debug('old commit id: %s' % old)
            self.log.debug('new commit id: %s' % new)

            for diff in utils.diff_tree(self.repo, old, new):
                if not diff.a_path.endswith('.rst'):
                    self.log.warn('Unknown extension (skipping): %(a_path)s' % diff)
                    continue

                if diff.deleted_file:
                    self.handle_delete(diff)
                elif diff.modified_file:
                    self.handle_modify(diff)
                elif diff.new_file:
                    self.handle_new(diff)
                elif diff.renamed_file:
                    self.handle_rename(diff)

            self.update_last_commit_id(new)
            db.session.commit()

    def handle_delete(self, diff):
        '''Called for deleted files (status=D). Delete post from blog,
        if it exists, and then delete post from local database.'''

        self.log.warn('DELETE %(a_path)s.' % diff)
        try:
            entry = db.File.query.filter_by(path=diff.a_path).one()
        except sqlalchemy.orm.exc.NoResultFound:
            self.log.error('File not found in database: %(a_path)s' % diff)
            return

        if entry.post_id:
            post = self.blog.get_post(entry.post_id)
            if not post:
                self.log.warn('Post id %s not found on log.' %
                        entry.post_id)
            else:
                self.blog.delete(post)
        else:
            self.log.warn('No post id recorded for %(a_path)s.' % diff)

        self.log.info('Deleting post id %s from database.' % entry.post_id)
        entry.delete()

    def handle_new(self, diff):
        '''Called for new files (status=A).  Post to blog and create
        entry in local database.'''

        try:
            entry = db.File.query.filter_by(path=diff.a_path).one()
            if entry:
                return self.handle_modify(diff)
        except sqlalchemy.orm.exc.NoResultFound:
            pass

        self.log.warn('NEW %(a_path)s.' % diff)

        doc = RSTDoc(diff.a_path)
        post = self.blog.add_post(doc)

        entry = db.File(
                path = diff.a_path,
                last_commit_id = diff.new_commit_id,
                post_id = post.get_post_id(),
                )

        self.log.info('Posted %s as post id %s (%s).' 
                % (entry.path, entry.post_id, doc.title))

    def handle_modify(self, diff):
        '''Called for modified files (status=M).  Update blog content and
        update last update time in local database.  If the file doesn't
        appear in the local database, treat this as a new file and hand
        things of to self.handle_new(...).'''

        self.log.warn('MODIFY %(a_path)s.' % diff)

        try:
            entry = db.File.query.filter_by(path=diff.a_path).one()
        except sqlalchemy.orm.exc.NoResultFound:
            self.log.warn('File %(a_path)s not found in database.' % diff)
            self.log.warn('Treating %(a_path)s as a new file.' % diff)
            return self.handle_new(diff)

        doc = RSTDoc(diff.a_path)
        post = self.blog.get_post(entry.post_id)
        self.blog.update_post(post, doc)
        entry.last_commit_id = diff.new_commit_id
        entry.updated = datetime.datetime.utcnow()

    def handle_rename(self, diff):
        '''Called for renamed files (status=R).  Update entry 
        in local database.  If no entry appears in local database, treat
        as a new file and hand off to self.handle_new(...).'''

        self.log.warn('RENAME %(a_path)s -> %(b_path)s.' % diff)

        try:
            entry = db.File.query.filter_by(path=diff.a_path).one()
            entry.path = diff.b_path
        except sqlalchemy.orm.exc.NoResultFound:
            self.log.warn('No entry in database for %(a_path)s.' % diff)
            self.log.warn('Treating %(b_path)s as a new file.' % diff)
            diff.a_path = diff.b_path
            return self.handle_new(self, diff)

    def update_last_commit_id (self, commit_id):
        '''Updates (or creates) the last_commit_id value in the
        database.'''

        try:
            entry = db.Metadata.query.filter_by(name='last_commit_id').one()
            entry.value = commit_id
        except sqlalchemy.orm.exc.NoResultFound:
            db.Metadata(
                    name='last_commit_id',
                    value=commit_id)

def post_receive_main():
    logging.basicConfig()
    del os.environ['GIT_DIR']
    os.chdir('..')
    gb = GitBlogger('.git/config', '.')
    gb.post_receive()

if __name__ == '__main__':
    post_receive_main()

