import os
import sys
import logging

import gdata.blogger.client
import gdata.blogger.data
import atom

class BlogError (Exception):
    pass

class NoSuchBlogError (BlogError):
    pass

class Blog (object):

    def __init__ (self, config):
        self.config = config
        self.log = logging.getLogger('gitblogger.blog')
        self.blog_name = config['blog']

        self.log.info('Connecting to %(blog)s as %(username)s.' %
                config)
        self.client = gdata.blogger.client.BloggerClient()
        self.client.client_login(
                config['username'],
                config['password'],
                'com.oddbit.gitblogger',
                service='blogger')

        # Iterate through blogs looking for one with the appropate 
        # title.
        feed = self.client.get_blogs()
        for entry in feed.entry:
            if entry.title.text == self.blog_name:
                self.blog = entry
                self.blog_id = self.blog.get_blog_id()

        if not self.blog:
            raise NoSuchBlogError(self.blog_name)

    def add_post(self, doc, draft=None):
        if draft is None:
            draft = doc.docinfo.get('draft', 'False') == 'True'

        return self.client.add_post(
                self.blog_id,
                doc.title,
                doc.content,
                labels=doc.docinfo.get('tags', '').split(),
                draft=draft)

    def get_post(self, post_id):
        return self.client.get_feed(
                self.blog.get_post_link().href + '/%s' % post_id,
                auth_token=self.client.auth_token,
                desired_class=gdata.blogger.data.BlogPost)
        
    def update_post(self, post, doc):
        '''Update title, content, and tags of the given document.  Note 
        that tag changes are only additive.'''

        post.title = atom.data.Title(type='text', text=doc.title)
        post.content = atom.data.Content(type='html', text=doc.content)
        for tag in doc.docinfo.get('tags', '').split():
            post.add_label(tag)
        return self.client.update(post)

    def delete(self, post):
        return self.client.delete(post)

if __name__ == '__main__':
    import rstdoc
    from ConfigParser import ConfigParser
    cf = ConfigParser()
    cf.read(sys.argv[1])

    b = Blog(cf)

