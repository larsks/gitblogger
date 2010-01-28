import os
import sys

import gdata.blogger.client

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

    def post(self, doc, draft=False):
        post = self.client.add_post(
                self.blog_id,
                doc.title,
                doc.content,
                draft)

        return post.get_post_id()

    def update(self, post_id, doc):
        # find original post
        pass

    def delete(self, post_id):
        pass

if __name__ == '__main__':
    from ConfigParser import ConfigParser
    cf = ConfigParser()
    cf.read(sys.argv[1])

    b = Blog(cf)

