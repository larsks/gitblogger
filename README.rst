==========
Gitblogger
==========

What it is, yo?
===============

Gitblogger lets you write blog entries in reStructuredText_ (RST) and posts
(or updates) them automatically to a Blogger blog when you push them to a
repository.

And why would you want to do that?
==================================

Maybe you don't?  I don't know.

I don't think that anyone should have to write HTML, and RST is my
preferred lightweight markup language.  I'm also a fan of version control
in general and git_ in particular.  I like being able to track my changes
over time, I like using a `real editor`_ on my posts, and I like having
things happen with the smallest amount of manual intervention possibe.

Requirements
============

Requirements that should be installed automatically if you use easy_install
---------------------------------------------------------------------------

- SQLAlchemy_
- Elixir_
- configdict_

Requirements that you will need to provide manually
---------------------------------------------------

- `Google gdata API`_

.. _sqlalchemy: http://www.sqlalchemy.org/
.. _elixir: http://elixir.ematia.de/trac/wiki
.. _configdict: http://github.com/larsks/configdict
.. _google gdata api: http://code.google.com/p/gdata-python-client/

Installation
============

#. Install gdata library.

#. Install gitblogger::

     python setup.py install

#. Add `gitblogger-post-receive` as the `post-receive` hook
   to a git repository that receives
   pushes from your working tree,

Configuration
=============

You need to provide credentials for authenticating to Google, the name of
your blog, and the refs gitblogger should be watching.  Add a 
``[gitblogger]]`` to your ``.git/config`` configuration file.

For example::

  [gitblogger]

  username  = you@gmail.com
  password  = secret
  blog      = Your Blog Title

  refs      = refs/head/master

.. _restructuredtext: http://docutils.sourceforge.net/rst.html
.. _real editor: http://www.vim.org/
.. _git: http://git-scm.org/

