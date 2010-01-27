import os
import sys
import lxml.etree

from docutils.core import publish_parts, publish_doctree

class RSTDoc (object):

    def __init__ (self, path):
        text = open(path).read()

        self.path = path
        self.raw = text
        self.parts = publish_parts(text, writer_name='html')
        self.tree = publish_doctree(text)

        self.title = self.parts.get('title') or os.path.basename(path)
        self.content  = self.parts.get('body', '')

        self.parse_docinfo()

    def parse_docinfo(self):
        self.etree = lxml.etree.XML(self.tree.asdom().toxml())
        fields = self.etree.xpath('/document/docinfo//field')
        self.docinfo = {}
        for field in fields:
            self.docinfo[field.find('field_name').text] \
                    = '\n'.join([x.text for x in
                        field.find('field_body').findall('paragraph')])

if __name__ == '__main__':

    doc = RSTDoc(sys.argv[1])

