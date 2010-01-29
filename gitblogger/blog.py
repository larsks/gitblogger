import os
import sys

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
        self.blog_name = config.get('gitblogger', 'blog')

        self.client = gdata.blogger.client.BloggerClient()
        self.client.client_login(
                config.get('gitblogger', 'username'),
                config.get('gitblogger', 'password'),
                'com.oddbit.gitblogger', service='blogger')

        feed = self.client.get_blogs()
        for entry in feed.entry:
            if entry.title.text == self.blog_name:
                self.blog = entry
                self.blog_id = self.blog.get_blog_id()

        if not self.blog:
            raise NoSuchBlogError(self.blog_name)

    def add_post(self, doc, draft=False):
        post = self.client.add_post(
                self.blog_id,
                doc.title,
                doc.content,
                draft)

        return post.get_post_id()

    def get_post(self, post_id):
        return self.client.get_feed(
                self.blog.get_post_link().href + '/%s' % post_id,
                auth_token=self.client.auth_token,
                desired_class=gdata.blogger.data.BlogPost)
        
    def update(self, post, doc):
        post.title = atom.data.Title(type='xhtml', text=doc.title)
        post.content = atom.data.Content(type='xhtml', text=doc.content)

        return self.client.update(post)

    def delete(self, post_id):
        pass

if __name__ == '__main__':
    from ConfigParser import ConfigParser
    cf = ConfigParser()
    cf.read(sys.argv[1])

    b = Blog(cf)

