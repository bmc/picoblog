# $Id$
#
# Constants used by this application

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import os

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

BLOG_NAME = 'PicoBlog'
CANONICAL_BLOG_URL = 'http://picoblog.appspot.com/'
BLOG_OWNER = 'Joe Example'

TEMPLATE_SUBDIR = 'templates'

TAG_URL_PATH = 'tag'
DATE_URL_PATH = 'date'
ARTICLE_URL_PATH = 'id'
MEDIA_URL_PATH = 'static'
ATOM_URL_PATH = 'atom'
RSS2_URL_PATH = 'rss2'
ARCHIVE_URL_PATH = 'archive'

MAX_ARTICLES_PER_PAGE = 5
TOTAL_RECENT = 10

_server_software = os.environ.get('SERVER_SOFTWARE','').lower()
if _server_software.startswith('goog'):
    ON_GAE = True
else:
    ON_GAE = False
del _server_software
