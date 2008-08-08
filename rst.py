# $Id$

"""
RST support.
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import logging
import os
import sys
import StringIO

from docutils import core, nodes, parsers
from docutils.parsers.rst import states, directives
from docutils.core import publish_parts

from pygments import lexers, util, highlight, formatters
from pygments.styles import get_style_by_name

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def code_block(name, arguments, options, content, lineno,
               content_offset, block_text, state, state_machine):
    """
    The code-block directive provides syntax highlighting for blocks
    of code.  It is used with the the following syntax::

    .. code-block:: python

        import sys
        def main():
            sys.stdout.write("Hello world")

    The resulting output is placed in a ``<div>`` block, with CSS class
    "code-block". A suitable CSS rule is something like this::

        div.code-block
        {
            margin-left: 2em ;
            margin-right: 2em ;
            background-color: #eeeeee;
            font-family: "Courier New", Courier, monospace;
            font-size: 10pt;
        }

    Adapted from http://lukeplant.me.uk/blog.php?id=1107301665
    """

    def _custom_highlighter(code):
        outfile = StringIO.StringIO()
        highlight(code, lexer, formatter, outfile)
        return outfile.getvalue()
    
    def _noop_highlighter(code):
        return code

    language = arguments[0]
    highlighter = None
    element = 'div'

    # Get the highlighter

    if language in ['xml', 'html']:
        lexer = lexers.get_lexer_by_name('text')
        highlighter = _noop_highlighter
        element = 'pre'

    else:
        try:
            lexer = lexers.get_lexer_by_name(language)
            formatter = formatters.get_formatter_by_name('html')
    
    
            highlighter = _custom_highlighter
    
        except util.ClassNotFound:
            lexer = lexers.get_lexer_by_name('text')
            highlighter = _noop_highlighter
            element = 'pre'

    if highlighter is None:
        node = nodes.literal_block(block_text, block_text)
        error = state_machine.reporter.error('The "%s" directive does not '
                                             'support language "%s".' %
                                             (name, language), node, line=lineno)
        return [error]

    if not content:
        node = nodes.literal_block(block_text, block_text)
        error = state_machine.reporter.error('The "%s" block is empty; '
                                             'content required.' %
                                             (name), node, line=lineno)
        return [error]

    include_text = highlighter("\n".join(content))
    html = '<%s class="code-block %s">\n%s\n</%s>\n' %\
           (element, language, include_text, element)
    raw = nodes.raw('', html, format='html')
    return [raw]

def rst2html(s, pygments_style='colorful', stylesheet=None):
    settings = {'style' : pygments_style, 'config' : None}

    # Necessary, because otherwise docutils attempts to read a config file
    # via the codecs module, which doesn't work with AppEngine.
    os.environ['DOCUTILSCONFIG'] = ""
    parts = publish_parts(source=s,
                          writer_name='html4css1',
                          settings_overrides=settings)
    return parts['fragment']

# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

code_block.arguments = (1, 0, 0)
code_block.options = {'languages' : parsers.rst.directives.unchanged}
code_block.content = 1

# Register with docutils

directives.register_directive('code-block', code_block)

