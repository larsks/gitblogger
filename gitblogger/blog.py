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
    '''This is a simple class for interacting with a Blogger blog.
    It uses the Google gdata.blogger.client API to create, remove,
    and update Blogger posts.'''

    def __init__ (self, config):
        '''``config`` is a configuration dictionary that must provide
        values for:
        
        - *username* -- your Blogger username
        - *password* -- the corresponding password
        - *blog* -- the name of your blog
        '''

        self.config = config
        self.log = logging.getLogger('gitblogger.blog')
        self.blog_name = config['blog']

        self.connect()
        self.find_blog()

    def connect(self):
        '''Authenticate to Blogger.'''

        self.log.info('Connecting to %(blog)s as %(username)s.' %
                self.config)
        self.client = gdata.blogger.client.BloggerClient()
        self.client.client_login(
                self.config['username'],
                self.config['password'],
                'com.oddbit.gitblogger',
                service='blogger')

    def find_blog(self):
        '''Iterate through blogs looking for one with the title
        selected in our configuration.'''

        feed = self.client.get_blogs()
        for entry in feed.entry:
            if entry.title.text == self.blog_name:
                self.blog = entry
                self.blog_id = self.blog.get_blog_id()

        if not self.blog:
            raise NoSuchBlogError(self.blog_name)

        self.log.info('Found blog id %s' % self.blog_id)

    def add_post(self, doc, draft=None):
        '''Add a post to the blog.  ``doc`` is a document object that
        provides the following attributes:

        - *title* -- document title
        - *content* -- document content (HTML)
        - *docinfo* -- document metadata dictionary
        '''

        if draft is None:
            draft = doc.docinfo.get('draft', 'false').lower() == 'true'

        return self.client.add_post(
                self.blog_id,
                doc.title,
                doc.content,
                labels=doc.docinfo.get('tags', '').split(),
                draft=draft)

    def get_post(self, post_id):
        '''Retrieve a post by post id.  Returns a
        ``gdata.blogger.data.BlogPost`` object.'''

        return self.client.get_feed(
                self.blog.get_post_link().href + '/%s' % post_id,
                auth_token=self.client.auth_token,
                desired_class=gdata.blogger.data.BlogPost)

    def get_posts(self, *args, **kwargs):
        '''Like gdata.blogger.client.BloggerClient.get_posts(), but
        blog_id is provided automatically.'''

        return self.client.get_posts(self.blog_id, *args, **kwargs)
        
    def update_post(self, post, doc):
        '''Update title, content, and tags of the given document.  Note 
        that tag changes are only additive.'''

        post.title = atom.data.Title(type='text', text=doc.title)
        post.content = atom.data.Content(type='html', text=doc.content)

        if post.control \
                and post.control.draft \
                and post.control.draft.text == 'yes' \
                and doc.docinfo.get('draft', 'False') == 'False':
            post.control.draft.text = 'no'

        for tag in doc.docinfo.get('tags', '').split():
            post.add_label(tag)
        return self.client.update(post)

    def delete(self, post):
        '''Delete a post.'''
        return self.client.delete(post)

if __name__ == '__main__':
    import rstdoc
    import configdict
    logging.basicConfig(level=logging.DEBUG)

    cf = configdict.ConfigDict(sys.argv[1])
    b = Blog(cf['gitblogger'])

